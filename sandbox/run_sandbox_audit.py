#!/usr/bin/env python3
"""Isolated Docker `lake build` + `#print axioms` verification orchestrator.

Enforces the strict two-phase security boundary defined in `sandbox/README.md`:

  Phase A (Trusted Dependency Pre-Fetch — ZERO untrusted repo code mounted/executed):
    - Reads ONLY `lean-toolchain` (strict regex validated) and `lake-manifest.json`
      (pure JSON parsed in Python; never executes `lakefile.lean`).
    - Inside a prep container with NO mount of the untrusted repository, installs
      the requested Lean 4 toolchain into `data/sandbox_cache/elan` and pre-fetches
      pinned Mathlib `.olean` caches (`lake exe cache get` on a synthetic minimal
      project) plus plain `git -c core.hooksPath=/dev/null` checkouts of any
      additional manifest git dependencies.

  Phase B (Isolated Untrusted Build & `#print axioms` Audit):
    - Runs an ephemeral container (`docker run --rm`) with:
        --network=none
        --user 65534:65534
        --cap-drop=ALL
        --security-opt=no-new-privileges:true
        --cpus=4 --memory=10g --pids-limit=512
        --tmpfs /tmp:rw,size=2g
        -v <elan_cache>:/opt/elan:ro
        -v <repo_dir>:/src/repo:ro
        -v <pkg_cache>:/src/packages:ro
    - Copies the read-only source into ephemeral `/work`, runs `lake build` (or
      `lean` for Std-only repos with `lean-toolchain`), and if compilation succeeds,
      runs `sandbox/check_axioms.lean` (`Lean.collectAxioms`) across 100% of
      theorems defined in the project's own modules.

Outputs compact, license-safe JSON logs under `artifacts/sandbox_builds/`:
  - `results_2026-11.json`
  - `results_2026-05.json`
  - `summary.json`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = REPO_ROOT / "data" / "repos"
CACHE_ROOT = REPO_ROOT / "data" / "sandbox_cache"
ELAN_CACHE = CACHE_ROOT / "elan"
PKGS_CACHE = CACHE_ROOT / "pkgs"
OUT_DIR = REPO_ROOT / "artifacts" / "sandbox_builds"
LONGITUDINAL_PATH = REPO_ROOT / "artifacts" / "longitudinal_summary.json"
IMAGE_NAME = "lean-survey-sandbox:v1"

TOOLCHAIN_RE = re.compile(r"^leanprover/lean4:v4\.\d+\.\d+(?:-rc\d+)?$")
TRUSTED_MATHLIB_HOSTS = (
    "https://github.com/leanprover-community/",
    "https://github.com/leanprover/",
)
SECURITY_FLAGS = [
    "--network=none",
    "--user=65534:65534",
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges:true",
    "--cpus=4",
    "--memory=10g",
    "--pids-limit=512",
]


@dataclass(frozen=True)
class TargetRepo:
    slice_id: str
    arxiv_id: str
    repo: str
    local_dir: str
    project_subdir: str = ""
    mode: str = "lake"  # "lake" | "lean_files" | "packaging_only"
    lake_targets: tuple[str, ...] = ()
    module_prefixes: tuple[str, ...] = ()
    lean_files: tuple[str, ...] = ()
    # Optional secondary check when a repo omits lakefile + lean-toolchain (Mode #12 packaging gap)
    synthetic_toolchain: str = ""
    synthetic_mathlib_rev: str = ""
    synthetic_subdir: str = ""
    synthetic_files: tuple[str, ...] = ()
    timeout_sec: int = 1800
    notes: str = ""


# Exhaustive cohort: ALL standalone primary Lean 4 repos with < 15,000 non-empty LoC
# across T1 (May 2026, n=3) and T2 (Nov 2026, n=11) — 14 repositories total.
COMPACT_COHORT: list[TargetRepo] = [
    # --- T2 (2026-11), n = 11 ---
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.18220",
        repo="manasdm/Lean-SysID",
        local_dir="manasdm__Lean-SysID",
        mode="packaging_only",
        synthetic_toolchain="leanprover/lean4:v4.35.0",
        synthetic_mathlib_rev="v4.35.0",
        synthetic_subdir="Lean code",
        synthetic_files=("Tutorial.lean", "Identification.lean", "Lemma_3_1_Ljung.lean", "Template.lean"),
        notes="No lakefile or lean-toolchain in repository; README states Lean v4.35.0 + Mathlib.",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.23762",
        repo="guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification",
        local_dir="guanyuzhu2014__Uniform-product-expansion---theory-and-Lean-certification",
        mode="packaging_only",
        synthetic_toolchain="leanprover/lean4:v4.36.0-rc2",
        synthetic_mathlib_rev="v4.36.0-rc2",
        synthetic_subdir="",
        synthetic_files=("CoprimeFrobenius.lean",),
        notes="Single standalone .lean file with no lakefile or lean-toolchain; header cites Lean v4.36.0-rc2 + Mathlib.",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.14756",
        repo="magbenji/discrete-modified-gradient-lean",
        local_dir="magbenji__discrete-modified-gradient-lean",
        project_subdir="",
        mode="lake",
        lake_targets=("DiscreteStability",),
        module_prefixes=("DiscreteStability",),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.19551",
        repo="tokencraftdata/trustbound",
        local_dir="tokencraftdata__trustbound",
        project_subdir="formal",
        mode="lean_files",
        lean_files=(
            "Admission.lean",
            "StripeGate.lean",
            "Closure.lean",
            "Observers.lean",
            "Dispatch.lean",
            "StaggeredClosure.lean",
            "ExposureOptimality.lean",
        ),
        notes="Std-only Lean v4.19.0 files with pinned formal/lean-toolchain; verified via direct `lean` invocation per formal/README.md.",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.10902",
        repo="canberksaner/bic-public",
        local_dir="canberksaner__bic-public",
        project_subdir="lean",
        mode="lake",
        lake_targets=("BicLean",),
        module_prefixes=("BicLean",),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.02256",
        repo="ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs",
        local_dir="ssenge__ExactShortestPathsAndFlowsOnPlanarGraphs",
        project_subdir="lean",
        mode="lake",
        lake_targets=("SsspFlow",),
        module_prefixes=("SsspFlow",),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.15201",
        repo="zenodo/24127514",
        local_dir="zenodo__24127514",
        project_subdir="lean-sparse-mm-v1.0.1/HnVahidi-lean-sparse-mm-136a0bb",
        mode="lake",
        lake_targets=("SparseMM", "Challenge", "Solution"),
        module_prefixes=("SparseMM", "Solution"),
        notes="Comparator Challenge/Solution layout: builds all targets and audits axioms on proved SparseMM + Solution modules (excluding Challenge spec stubs).",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.16690",
        repo="RobinSchabert/positive-sym-func-h17-undecidability-lean",
        local_dir="RobinSchabert__positive-sym-func-h17-undecidability-lean",
        project_subdir="",
        mode="lake",
        lake_targets=("AnyDim",),
        module_prefixes=("AnyDim",),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.10810",
        repo="zenodo/24035424",
        local_dir="zenodo__24035424",
        project_subdir="DBLog_Orphan_Absence_artifact-1.0/DBLog_Orphan_Absence_artifact-1.0/lean",
        mode="lake",
        lake_targets=("DBLogContract", "OrphanAbsence"),
        module_prefixes=("DBLogContract", "OrphanAbsence"),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.05243",
        repo="CoffeeAndConvexity/AltOMD-Lean",
        local_dir="CoffeeAndConvexity__AltOMD-Lean",
        project_subdir="",
        mode="lake",
        lake_targets=("AltOMD",),
        module_prefixes=("AltOMD",),
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.18455",
        repo="inody/wmfki_lean",
        local_dir="inody__wmfki_lean",
        project_subdir="",
        mode="lake",
        lake_targets=("Lean_Code", "Showcase", "WMFKI_Stochastic"),
        module_prefixes=("Lean_Code", "Showcase", "WMFKI_Stochastic"),
    ),
    # --- T1 (2026-05), n = 3 (100% of contemporaneous T1 scanned repos) ---
    TargetRepo(
        slice_id="2026-05",
        arxiv_id="2605.14610",
        repo="SZabolotnii/Ku-PATP-code-supplement",
        local_dir="SZabolotnii__Ku-PATP-code-supplement",
        project_subdir="",
        mode="lake",
        lake_targets=("PATP",),
        module_prefixes=("PATP",),
    ),
    TargetRepo(
        slice_id="2026-05",
        arxiv_id="2605.02856",
        repo="rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856",
        local_dir="rayiskander2406__qanary-k-stage-composition-arXiv-2605.02856",
        project_subdir="",
        mode="lake",
        lake_targets=("QanaryPaper7",),
        module_prefixes=("QanaryPaper7",),
        notes="lakefile.lean hardcodes 4 relative sibling paths (../qanary-*) absent from this repository.",
    ),
    TargetRepo(
        slice_id="2026-05",
        arxiv_id="2605.16407",
        repo="gkoomullil/proof-carrying-certificates",
        local_dir="gkoomullil__proof-carrying-certificates",
        project_subdir="lean_artifact",
        mode="lake",
        lake_targets=("EmbeddingSensitivity",),
        module_prefixes=("EmbeddingSensitivity",),
    ),
]

# Phase C2 cohort: ALL newly discovered `<15k` LoC `eng_algorithmic_proof` public repos
# from the +7 engineering categories in T2 (2026-11) — 3 compact repositories total.
PLUS7_COMPACT_COHORT: list[TargetRepo] = [
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.14586",
        repo="zenodo/23768172",
        local_dir="zenodo__23768172",
        project_subdir="spar_zenodo/spar/theory/lean",
        mode="lake",
        lake_targets=("SparTheorems",),
        module_prefixes=("SparTheorems",),
        notes="Zenodo SPAR Lean 4 formalization (v4.35.0-rc4 + Mathlib) of deterministic algebraic core, refresh chain, and OGD/Hedge regret bounds.",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.09615",
        repo="renatoppl/trace-square-root",
        local_dir="renatoppl__trace-square-root",
        project_subdir="",
        mode="lake",
        lake_targets=("TraceSqrt",),
        module_prefixes=("TraceSqrt",),
        notes="TraceSqrt Lean 4 formalization (v4.27.0 + Mathlib) of all 22 numbered statements and 4 online algorithms.",
    ),
    TargetRepo(
        slice_id="2026-11",
        arxiv_id="2611.07395",
        repo="michalshavitNYU/Rigorously-certified-water-waves",
        local_dir="michalshavitNYU__Rigorously-certified-water-waves",
        project_subdir="Lean",
        mode="lake",
        lake_targets=("WaveCAP", "WaveCAP.PaperTheorems", "WaveCAP.PaperAudit"),
        module_prefixes=("WaveCAP",),
        notes="WaveCAP Lean 4 formalization (v4.29.0-rc6 + Mathlib); builds default WaveCAP library plus dedicated PaperTheorems and PaperAudit targets per README.",
    ),
]

PLUS7_CLS_PATH = REPO_ROOT / "artifacts" / "slices" / "2026-11" / "plus7_classifications.json"
PHASE_C1_PATH = REPO_ROOT / "artifacts" / "phase_c1_15cat_longitudinal.json"


def _get_git_sha(repo_dir: Path) -> str | None:
    if not (repo_dir / ".git").exists():
        return None
    proc = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def _hash_lean_tree(repo_dir: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(repo_dir.rglob("*.lean")):
        if ".git" in p.parts or ".lake" in p.parts:
            continue
        rel = p.relative_to(repo_dir).as_posix()
        h.update(rel.encode("utf-8") + b"\0")
        h.update(p.read_bytes() + b"\0")
    return h.hexdigest()


def _load_paper_metadata(cohort: str = "orig8") -> dict[str, dict[str, Any]]:
    if cohort == "plus7":
        out: dict[str, dict[str, Any]] = {}
        if PLUS7_CLS_PATH.is_file():
            cls_doc = json.loads(PLUS7_CLS_PATH.read_text(encoding="utf-8"))
            for r in cls_doc.get("lean_results", []):
                out[r["arxiv_id"]] = {
                    "verification_tier": r.get("verification_tier_observed"),
                    "paper_domain_role": r.get("paper_domain_role"),
                    "role_4way": r.get("role_4way"),
                    "primary_owned_loc": None,
                }
        if PHASE_C1_PATH.is_file():
            c1 = json.loads(PHASE_C1_PATH.read_text(encoding="utf-8"))
            for item in c1.get("phase_c2_eng_alg_audit_queue", []):
                aid = item["arxiv_id"]
                out.setdefault(aid, {})
                out[aid]["primary_owned_loc"] = item.get("primary_owned_loc")
                if not out[aid].get("verification_tier"):
                    out[aid]["verification_tier"] = item.get("verification_tier")
                out[aid]["role_4way"] = item.get("role_4way", "eng_algorithmic_proof")
        return out

    data = json.loads(LONGITUDINAL_PATH.read_text(encoding="utf-8"))
    out = {}
    for s in data["slices"]:
        for p in s.get("confirmed_papers", []):
            out[p["arxiv_id"]] = p
    return out


def _read_validated_toolchain(proj_dir: Path) -> str | None:
    tc_path = proj_dir / "lean-toolchain"
    if not tc_path.is_file():
        return None
    tc = tc_path.read_text(encoding="utf-8").strip()
    if not TOOLCHAIN_RE.match(tc):
        raise ValueError(f"Unsafe or unrecognized lean-toolchain {tc!r} in {tc_path}")
    return tc


def _ensure_toolchain(toolchain: str) -> None:
    """Phase A: Install Lean 4 toolchain into ELAN_CACHE inside a clean container (no repo mounted)."""
    ELAN_CACHE.mkdir(parents=True, exist_ok=True)
    tc_dir_name = toolchain.replace("/", "--").replace(":", "---")
    if (ELAN_CACHE / "toolchains" / tc_dir_name / "bin" / "lean").is_file():
        print(f"  [Phase A] Toolchain cached: {toolchain}")
        return
    print(f"  [Phase A] Installing toolchain {toolchain} into {ELAN_CACHE} ...")
    cmd = [
        "docker", "run", "--rm",
        "--entrypoint", "bash",
        "-v", f"{ELAN_CACHE}:/opt/elan:rw",
        IMAGE_NAME,
        "-c",
        f"set -euo pipefail; elan toolchain install '{toolchain}'; chmod -R a+rX /opt/elan",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to install toolchain {toolchain}:\n{proc.stderr}\n{proc.stdout}")
    print(f"  [Phase A] Installed toolchain: {toolchain}")


def _prepare_mathlib_and_deps(
    toolchain: str,
    manifest_pkgs: list[dict[str, Any]],
) -> tuple[Path | None, Path | None]:
    """Phase A: Pre-fetch Mathlib `.olean` cache + plain git clones of extra deps (ZERO untrusted repo mounted).

    Returns (packages_cache_dir, synthetic_meta_dir).
    """
    git_pkgs = [p for p in manifest_pkgs if p.get("type") == "git"]
    if not git_pkgs:
        return None, None

    # Build deterministic cache key from toolchain + sorted (name, url, rev)
    key_material = json.dumps(
        {"tc": toolchain, "pkgs": sorted((p["name"], p.get("url", ""), p.get("rev", "")) for p in git_pkgs)},
        sort_keys=True,
    )
    cache_key = hashlib.sha256(key_material.encode("utf-8")).hexdigest()[:16]
    pkg_dir = PKGS_CACHE / cache_key / "packages"
    meta_dir = PKGS_CACHE / cache_key / "meta"
    done_marker = PKGS_CACHE / cache_key / ".ready"

    if done_marker.is_file() and pkg_dir.is_dir():
        print(f"  [Phase A] Dependency cache hit: {cache_key} ({len(git_pkgs)} pkgs)")
        return pkg_dir, meta_dir

    pkg_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    # Separate trusted mathlib package (if any) from other git packages
    mathlib_pkg = next(
        (
            p
            for p in git_pkgs
            if p.get("name") == "mathlib"
            and any((p.get("url") or "").startswith(h) for h in TRUSTED_MATHLIB_HOSTS)
        ),
        None,
    )

    # Extra git packages NOT covered by mathlib's standard dep set
    mathlib_std_names = {
        "mathlib", "batteries", "Qq", "aesop", "proofwidgets",
        "Cli", "importGraph", "LeanSearchClient", "plausible",
    }
    extra_git_pkgs = [p for p in git_pkgs if p.get("name") not in mathlib_std_names]

    # Write trusted synthetic lakefile.toml + sanitized lake-manifest.json for Phase-A cache fetch
    if mathlib_pkg is not None:
        m_url = mathlib_pkg["url"]
        m_rev = mathlib_pkg["rev"]
        synth_lakefile = (
            'name = "sandbox_synth"\n'
            'version = "0.1.0"\n\n'
            '[[require]]\n'
            'name = "mathlib"\n'
            f'git = "{m_url}"\n'
            f'rev = "{m_rev}"\n'
        )
        (meta_dir / "lakefile.toml").write_text(synth_lakefile, encoding="utf-8")
        # Include ONLY trusted mathlib-ecosystem git packages in synthetic manifest (if full manifest entries)
        trusted_pkgs = [
            p
            for p in git_pkgs
            if p.get("name") in mathlib_std_names
            and "inherited" in p
            and any((p.get("url") or "").startswith(h) for h in TRUSTED_MATHLIB_HOSTS)
        ]
        if trusted_pkgs:
            synth_manifest = {
                "version": "1.1.0",
                "packagesDir": ".lake/packages",
                "packages": trusted_pkgs,
                "name": "sandbox_synth",
                "lakeDir": ".lake",
            }
            (meta_dir / "lake-manifest.json").write_text(json.dumps(synth_manifest, indent=2) + "\n", encoding="utf-8")
        else:
            (meta_dir / "lake-manifest.json").unlink(missing_ok=True)

    # Build Phase-A bash script (runs ONLY trusted elan / mathlib cache / git clone with hooks disabled)
    tc_dir_name = toolchain.replace("/", "--").replace(":", "---")
    lines = [
        "set -euo pipefail",
        "export ELAN_HOME=/opt/elan",
        f"export PATH=/opt/elan/toolchains/{tc_dir_name}/bin:$PATH",
        "export HOME=/tmp",
    ]
    if mathlib_pkg is not None:
        lines.extend([
            "mkdir -p /tmp/synth/.lake",
            f"echo '{toolchain}' > /tmp/synth/lean-toolchain",
            "cp /meta/lakefile.toml /tmp/synth/lakefile.toml",
            "if [ -f /meta/lake-manifest.json ]; then cp /meta/lake-manifest.json /tmp/synth/lake-manifest.json; fi",
            "cd /tmp/synth",
            # Materialize mathlib + transitive deps at exact manifest commits, then download Mathlib .olean cache!
            "lake update --keep-toolchain",
            "lake exe cache get",
            # Copy materialized packages into /out_pkgs
            "rm -rf /out_pkgs/*",
            "cp -a /tmp/synth/.lake/packages/. /out_pkgs/",
            # Save the lake-resolved manifest back to /meta for synthetic_mathlib mode
            "cp /tmp/synth/lake-manifest.json /meta/lake-manifest.json",
        ])

    # Clone any additional third-party git deps with hooks strictly disabled (never executed in Phase A!)
    for ep in extra_git_pkgs:
        name = ep["name"]
        url = ep["url"]
        rev = ep["rev"]
        if not re.match(r"^[A-Za-z0-9._-]+$", name) or not re.match(r"^[0-9a-f]{7,40}$", rev):
            raise ValueError(f"Unsafe extra git package spec: {ep}")
        if not url.startswith("https://github.com/"):
            raise ValueError(f"Untrusted extra git package URL: {url}")
        lines.extend([
            f"echo '[Phase A] Cloning extra dep {name} @ {rev[:12]} (hooks disabled)...'",
            f"rm -rf '/out_pkgs/{name}'",
            f"git -c core.hooksPath=/dev/null clone --filter=blob:none --no-checkout '{url}' '/out_pkgs/{name}'",
            f"git -c core.hooksPath=/dev/null -C '/out_pkgs/{name}' checkout --detach '{rev}'",
        ])

    lines.append("chmod -R a+rX /out_pkgs /meta")
    script = "\n".join(lines)

    print(f"  [Phase A] Fetching Mathlib cache + deps ({cache_key}, tc={toolchain}, extra={[p['name'] for p in extra_git_pkgs]}) ...")
    t0 = time.monotonic()
    cmd = [
        "docker", "run", "--rm",
        "--entrypoint", "bash",
        "-v", f"{ELAN_CACHE}:/opt/elan:rw",
        "-v", f"{pkg_dir}:/out_pkgs:rw",
        "-v", f"{meta_dir}:/meta:rw",
        IMAGE_NAME,
        "-c", script,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.monotonic() - t0
    if proc.returncode != 0:
        print(f"  [Phase A] ERROR ({dt:.1f}s):\n{proc.stderr[-1500:]}\n{proc.stdout[-1500:]}")
        raise RuntimeError(f"Phase A dependency prep failed for {cache_key}")
    done_marker.write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")
    print(f"  [Phase A] Dependency cache ready in {dt:.1f}s: {cache_key}")
    return pkg_dir, meta_dir


def _run_phase_b_container(
    repo_dir: Path,
    pkg_dir: Path | None,
    meta_dir: Path | None,
    entry_args: list[str],
    timeout_sec: int,
) -> dict[str, Any]:
    """Phase B: Execute untrusted repo inside strictly isolated `--network=none` container."""
    cmd = [
        "docker", "run", "--rm",
        "--network=none",
        "--user", "65534:65534",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges:true",
        "--cpus=4",
        "--memory=10g",
        "--pids-limit=512",
        "--tmpfs", "/tmp:rw,size=2g",
        "-v", f"{ELAN_CACHE}:/opt/elan:ro",
        "-v", f"{repo_dir}:/src/repo:ro",
    ]
    if pkg_dir is not None and pkg_dir.is_dir():
        cmd.extend(["-v", f"{pkg_dir}:/src/packages:ro"])
    if meta_dir is not None and meta_dir.is_dir():
        cmd.extend(["-v", f"{meta_dir}:/src/synthetic_meta:ro"])

    cmd.append(IMAGE_NAME)
    cmd.extend(entry_args)

    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec + 60)
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "build_status": "timeout",
            "wall_time_sec": round(time.monotonic() - t0, 2),
            "error_summary": f"Outer container timeout after {timeout_sec + 60}s",
            "axioms_audit": None,
        }

    for line in reversed(proc.stdout.splitlines()):
        if line.startswith("SANDBOX_RESULT_JSON:"):
            return json.loads(line[len("SANDBOX_RESULT_JSON:") :])

    return {
        "exit_code": proc.returncode if proc.returncode != 0 else 1,
        "build_status": "fail_runner",
        "wall_time_sec": round(time.monotonic() - t0, 2),
        "error_summary": (proc.stderr + "\n" + proc.stdout)[-1500:],
        "axioms_audit": None,
    }


def audit_target(target: TargetRepo, meta_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    repo_dir = REPOS_DIR / target.local_dir
    if not repo_dir.is_dir():
        raise FileNotFoundError(f"Cloned repo missing: {repo_dir}")

    paper_meta = meta_by_id.get(target.arxiv_id, {})
    commit_sha = _get_git_sha(repo_dir)
    zenodo_id = target.repo.split("/", 1)[1] if target.repo.startswith("zenodo/") else None
    lean_tree_sha = _hash_lean_tree(repo_dir)
    proj_dir = repo_dir / target.project_subdir if target.project_subdir else repo_dir

    print(f"\n=== [{target.slice_id}] {target.arxiv_id} | {target.repo} (mode={target.mode}) ===")

    executed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lean_toolchain = _read_validated_toolchain(proj_dir)

    record: dict[str, Any] = {
        "slice_id": target.slice_id,
        "arxiv_id": target.arxiv_id,
        "repo": target.repo,
        "commit_sha": commit_sha,
        "zenodo_record_id": zenodo_id,
        "lean_tree_sha256": lean_tree_sha,
        "static_verification_tier": paper_meta.get("verification_tier"),
        "paper_domain_role": paper_meta.get("paper_domain_role"),
        **({"role_4way": paper_meta["role_4way"]} if paper_meta.get("role_4way") else {}),
        "owned_loc": paper_meta.get("primary_owned_loc"),
        "lean_toolchain": lean_toolchain,
        "project_subdir": target.project_subdir or ".",
        "build_mode": target.mode,
        "executed_at": executed_at,
        "network_mode": "none",
        "security_flags": SECURITY_FLAGS,
        "timeout_sec": target.timeout_sec,
        "notes": target.notes,
    }

    if target.mode == "packaging_only":
        # Strict out-of-the-box clean-room check fails packaging (no lakefile / lean-toolchain).
        record.update({
            "exit_code": 2,
            "build_status": "fail_packaging",
            "wall_time_sec": 0.0,
            "total_theorems_checked": 0,
            "standard_axioms_used": [],
            "nonstandard_axioms_detected": [],
            "sorry_ax_detected": False,
            "of_reduce_bool_detected": False,
            "trust_compiler_detected": False,
            "axioms_by_theorem": {},
            "error_summary": "Repository omits both lakefile.{toml,lean} and lean-toolchain; clean-room `lake build` cannot execute out of the box.",
        })
        # Secondary check: test whether the standalone .lean files actually type-check in the
        # README/header-documented Lean + Mathlib environment inside the same `--network=none` container.
        if target.synthetic_toolchain and target.synthetic_mathlib_rev:
            print(f"  [Secondary] Running synthetic Mathlib check ({target.synthetic_toolchain}) ...")
            _ensure_toolchain(target.synthetic_toolchain)
            synth_pkgs = [
                {
                    "name": "mathlib",
                    "type": "git",
                    "url": "https://github.com/leanprover-community/mathlib4",
                    "rev": target.synthetic_mathlib_rev,
                }
            ]
            pkg_dir, meta_dir = _prepare_mathlib_and_deps(target.synthetic_toolchain, synth_pkgs)
            entry_args = [
                "--mode", "synthetic_mathlib",
                "--project-subdir", target.synthetic_subdir,
                "--synthetic-toolchain", target.synthetic_toolchain,
                "--timeout", str(target.timeout_sec),
                "--lean-files", *target.synthetic_files,
            ]
            syn_res = _run_phase_b_container(repo_dir, pkg_dir, meta_dir, entry_args, target.timeout_sec)
            syn_ax = syn_res.get("axioms_audit") or {}
            record["synthetic_env_check"] = {
                "toolchain_used": target.synthetic_toolchain,
                "mathlib_rev_used": target.synthetic_mathlib_rev,
                "exit_code": syn_res.get("exit_code"),
                "build_status": syn_res.get("build_status"),
                "wall_time_sec": syn_res.get("wall_time_sec"),
                "files_checked": syn_res.get("files_checked", []),
                "total_theorems_checked": syn_ax.get("total_theorems_checked", 0),
                "standard_axioms_used": syn_ax.get("standard_axioms_used", []),
                "nonstandard_axioms_detected": syn_ax.get("nonstandard_axioms_detected", []),
                "sorry_ax_detected": bool(syn_ax.get("sorry_ax_detected", False)),
                "of_reduce_bool_detected": bool(syn_ax.get("of_reduce_bool_detected", False)),
                "trust_compiler_detected": bool(syn_ax.get("trust_compiler_detected", False)),
                "axioms_by_theorem": syn_ax.get("axioms_by_theorem", {}),
                "error_summary": syn_res.get("error_summary", ""),
            }
            print(
                f"  [Secondary] status={syn_res.get('build_status')} "
                f"time={syn_res.get('wall_time_sec')}s "
                f"thms={syn_ax.get('total_theorems_checked', 0)} "
                f"nonstd={syn_ax.get('nonstandard_axioms_detected', [])}"
            )
        return record

    if not lean_toolchain:
        raise RuntimeError(f"Missing lean-toolchain in {proj_dir}")

    # Phase A: Toolchain + dependencies (zero untrusted repo mounted)
    _ensure_toolchain(lean_toolchain)

    pkg_dir: Path | None = None
    meta_dir: Path | None = None
    manifest_path = proj_dir / "lake-manifest.json"
    if target.mode == "lake" and manifest_path.is_file():
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_pkgs = manifest_data.get("packages", [])
        # Record whether manifest has unbundled local path dependencies
        path_deps = [p for p in manifest_pkgs if p.get("type") == "path"]
        if path_deps:
            record["unbundled_path_deps"] = [p.get("dir") for p in path_deps]
        pkg_dir, meta_dir = _prepare_mathlib_and_deps(lean_toolchain, manifest_pkgs)

    # Phase B: Strictly isolated `--network=none` container execution
    if target.mode == "lake":
        entry_args = [
            "--mode", "lake",
            "--project-subdir", target.project_subdir,
            "--timeout", str(target.timeout_sec),
        ]
        if target.lake_targets:
            entry_args.extend(["--lake-targets", *target.lake_targets])
        if target.module_prefixes:
            entry_args.extend(["--module-prefixes", *target.module_prefixes])
    elif target.mode == "lean_files":
        entry_args = [
            "--mode", "lean_files",
            "--project-subdir", target.project_subdir,
            "--timeout", str(target.timeout_sec),
            "--lean-files", *target.lean_files,
        ]
    else:
        raise ValueError(f"Unknown mode: {target.mode}")

    print(f"  [Phase B] Launching --network=none isolated container ({target.mode}) ...")
    res = _run_phase_b_container(repo_dir, pkg_dir, None, entry_args, target.timeout_sec)
    ax = res.get("axioms_audit") or {}

    record.update({
        "exit_code": res.get("exit_code"),
        "build_status": res.get("build_status"),
        "wall_time_sec": res.get("wall_time_sec"),
        "axiom_check_wall_time_sec": res.get("axiom_check_wall_time_sec"),
        "target_modules_count": ax.get("target_modules_count", 0),
        "total_theorems_checked": ax.get("total_theorems_checked", 0),
        "standard_axioms_used": ax.get("standard_axioms_used", []),
        "nonstandard_axioms_detected": ax.get("nonstandard_axioms_detected", []),
        "sorry_ax_detected": bool(ax.get("sorry_ax_detected", False)),
        "of_reduce_bool_detected": bool(ax.get("of_reduce_bool_detected", False)),
        "trust_compiler_detected": bool(ax.get("trust_compiler_detected", False)),
        "axioms_by_theorem": ax.get("axioms_by_theorem", {}),
        "error_summary": res.get("error_summary", ""),
    })
    if res.get("axiom_check_error"):
        record["axiom_check_error"] = res["axiom_check_error"]

    print(
        f"  [Phase B] status={record['build_status']} rc={record['exit_code']} "
        f"time={record['wall_time_sec']}s thms={record['total_theorems_checked']} "
        f"sorry={record['sorry_ax_detected']} reduceBool={record['of_reduce_bool_detected']} "
        f"nonstd={record['nonstandard_axioms_detected']}"
    )
    if record["build_status"] != "pass":
        print(f"  [Phase B] err: {record['error_summary'][:350]}")
    return record


def _summarize_records(recs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(recs)
    passed = [r for r in recs if r["build_status"] == "pass"]
    clean_axioms = [
        r
        for r in passed
        if not r.get("sorry_ax_detected")
        and not r.get("of_reduce_bool_detected")
        and not r.get("trust_compiler_detected")
        and not r.get("nonstandard_axioms_detected")
    ]
    failed_packaging = [r for r in recs if r["build_status"] == "fail_packaging"]
    failed_local_dep = [r for r in recs if r["build_status"] == "fail_missing_local_dep"]
    failed_build = [r for r in recs if r["build_status"] in ("fail_build", "fail_network_dep", "timeout", "fail_runner")]
    synth_passed = [
        r
        for r in failed_packaging
        if (r.get("synthetic_env_check") or {}).get("build_status") == "pass"
    ]
    synth_clean = [
        r
        for r in synth_passed
        if not (r.get("synthetic_env_check") or {}).get("sorry_ax_detected")
        and not (r.get("synthetic_env_check") or {}).get("of_reduce_bool_detected")
        and not (r.get("synthetic_env_check") or {}).get("nonstandard_axioms_detected")
    ]
    t3_all = [r for r in recs if r.get("static_verification_tier") == "Tier3_Gold"]
    t3_pass = [r for r in t3_all if r["build_status"] == "pass"]
    t3_clean = [r for r in t3_all if r in clean_axioms]
    total_thms_ootb = sum(int(r.get("total_theorems_checked") or 0) for r in passed)
    total_thms_synth = sum(
        int((r.get("synthetic_env_check") or {}).get("total_theorems_checked") or 0)
        for r in synth_passed
    )
    return {
        "total_attempted": n,
        "pass_out_of_box": len(passed),
        "pass_and_standard_axioms_only": len(clean_axioms),
        "pass_with_nonstandard_axioms": len(passed) - len(clean_axioms),
        "fail_packaging_no_lakefile": len(failed_packaging),
        "fail_missing_local_dep": len(failed_local_dep),
        "fail_build_or_other": len(failed_build),
        "synthetic_env_pass_among_packaging_fails": len(synth_passed),
        "synthetic_env_clean_among_packaging_fails": len(synth_clean),
        "tier3_gold_attempted": len(t3_all),
        "tier3_gold_pass_out_of_box": len(t3_pass),
        "tier3_gold_clean_axioms": len(t3_clean),
        "total_theorems_checked_ootb": total_thms_ootb,
        "total_theorems_checked_incl_synthetic": total_thms_ootb + total_thms_synth,
        "sorry_ax_repos_ootb": [r["arxiv_id"] for r in passed if r.get("sorry_ax_detected")],
        "of_reduce_bool_repos_ootb": [r["arxiv_id"] for r in passed if r.get("of_reduce_bool_detected")],
        "nonstandard_axiom_repos_ootb": [
            {"arxiv_id": r["arxiv_id"], "axioms": r.get("nonstandard_axioms_detected", [])}
            for r in passed
            if r.get("nonstandard_axioms_detected")
        ],
    }


def _merge_and_write_plus7_outputs(new_records: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res_path = OUT_DIR / "results_plus7_2026-11.json"
    rec_map: dict[str, dict[str, Any]] = {}
    if res_path.is_file():
        existing = json.loads(res_path.read_text(encoding="utf-8"))
        for r in existing.get("records", []):
            rec_map[r["arxiv_id"]] = r
    for r in new_records:
        rec_map[r["arxiv_id"]] = r

    cohort_order = {t.arxiv_id: idx for idx, t in enumerate(PLUS7_COMPACT_COHORT)}
    ordered = sorted(rec_map.values(), key=lambda x: cohort_order.get(x["arxiv_id"], 999))
    payload = {
        "schema_version": "1.0",
        "cohort": "plus7_eng_algorithmic_proof_compact",
        "slice_id": "2026-11",
        "runner_image": IMAGE_NAME,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "security_invariants": {
            "network_mode": "none",
            "user": "65534:65534",
            "cap_drop": "ALL",
            "no_new_privileges": True,
            "readonly_source_mount": True,
            "cpus": 4,
            "memory": "10g",
            "pids_limit": 512,
        },
        "selection_criterion": "All newly discovered standalone primary Lean 4 eng_algorithmic_proof repositories with < 15,000 non-empty LoC from the +7 engineering categories in T2 (Nov 2026).",
        "summary": _summarize_records(ordered),
        "records": ordered,
    }
    res_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote +7 sandbox build results to {res_path}")


def _merge_and_write_outputs(new_records: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_slice: dict[str, dict[str, dict[str, Any]]] = {"2026-11": {}, "2026-05": {}}

    # Load existing records so partial --only runs update incrementally without clobbering other repos
    for sl in by_slice:
        p = OUT_DIR / f"results_{sl}.json"
        if p.is_file():
            existing = json.loads(p.read_text(encoding="utf-8"))
            for r in existing.get("records", []):
                by_slice[sl][r["arxiv_id"]] = r

    for r in new_records:
        by_slice[r["slice_id"]][r["arxiv_id"]] = r

    cohort_order = {t.arxiv_id: idx for idx, t in enumerate(COMPACT_COHORT)}
    all_records: list[dict[str, Any]] = []

    for sl, rec_map in by_slice.items():
        ordered = sorted(rec_map.values(), key=lambda x: cohort_order.get(x["arxiv_id"], 999))
        all_records.extend(ordered)
        payload = {
            "schema_version": "1.0",
            "slice_id": sl,
            "runner_image": IMAGE_NAME,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "security_invariants": {
                "network_mode": "none",
                "user": "65534:65534",
                "cap_drop": "ALL",
                "no_new_privileges": True,
                "readonly_source_mount": True,
                "cpus": 4,
                "memory": "10g",
                "pids_limit": 512,
            },
            "records": ordered,
        }
        (OUT_DIR / f"results_{sl}.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    t2_recs = [r for r in all_records if r["slice_id"] == "2026-11"]
    t1_recs = [r for r in all_records if r["slice_id"] == "2026-05"]
    summary = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runner_image": IMAGE_NAME,
        "selection_criterion": "All standalone primary Lean 4 repositories with < 15,000 non-empty LoC across T1 (May 2026) and T2 (Nov 2026).",
        "overall": _summarize_records(all_records),
        "by_slice": {
            "2026-11": _summarize_records(t2_recs),
            "2026-05": _summarize_records(t1_recs),
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote sandbox build results and summary to {OUT_DIR}/")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run isolated Docker lake build + #print axioms benchmark.")
    ap.add_argument("--cohort", choices=["orig8", "plus7"], default="orig8", help="Target cohort (default: orig8).")
    ap.add_argument("--only", nargs="*", default=None, help="Subset of arXiv IDs to run.")
    args = ap.parse_args()

    meta_by_id = _load_paper_metadata(args.cohort)
    cohort_list = PLUS7_COMPACT_COHORT if args.cohort == "plus7" else COMPACT_COHORT
    targets = cohort_list
    if args.only:
        want = set(args.only)
        targets = [t for t in cohort_list if t.arxiv_id in want]
        if not targets:
            raise SystemExit(f"No matching targets for {args.only} in cohort {args.cohort}")

    results: list[dict[str, Any]] = []
    for t in targets:
        rec = audit_target(t, meta_by_id)
        results.append(rec)
        # Checkpoint after every repo so no progress is ever lost!
        if args.cohort == "plus7":
            _merge_and_write_plus7_outputs(results)
        else:
            _merge_and_write_outputs(results)


if __name__ == "__main__":
    main()
