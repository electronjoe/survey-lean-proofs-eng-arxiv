#!/usr/bin/env python3
"""Pin immutable provenance (arXiv version, Git commit SHA / Zenodo fingerprint,
Lean toolchain, and automated file:line existence checks) for all Phase-2 Layer-A
audited repositories into `artifacts/phase2_provenance.json`.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = REPO_ROOT / "data" / "repos"
OUT_PATH = REPO_ROOT / "artifacts" / "phase2_provenance.json"

SLICES = (
    ("2026-11", REPO_ROOT / "data" / "survey.db", REPO_ROOT / "artifacts" / "slices" / "2026-11" / "layer_a_audits.json"),
    ("2026-05", REPO_ROOT / "data" / "slice_2026_05.db", REPO_ROOT / "artifacts" / "slices" / "2026-05" / "layer_a_audits.json"),
)

# Explicit canonical repo mapping for each audited paper (primary + companion repos when applicable)
REPO_DIR_MAP: dict[str, tuple[str, str, str]] = {
    # arxiv_id: (local_dir_name, host, canonical_url)
    "2611.04876": ("sdziembowski__MatrixRefresh", "github", "https://github.com/sdziembowski/MatrixRefresh"),
    "2611.05136": ("qianchen92__aft-lean-theorem99", "github", "https://github.com/qianchen92/aft-lean-theorem99"),
    "2611.05243": ("CoffeeAndConvexity__AltOMD-Lean", "github", "https://github.com/CoffeeAndConvexity/AltOMD-Lean"),
    "2611.08172": ("dcass-121__d3-lean-verification", "github", "https://github.com/dcass-121/d3-lean-verification"),
    "2611.09050": ("dmivilensky__PolynomialRealizationsProgram", "github", "https://github.com/dmivilensky/PolynomialRealizationsProgram"),
    "2611.10902": ("canberksaner__bic-public", "github", "https://github.com/canberksaner/bic-public"),
    "2611.11713": ("ywatanabex__bp-response-geometry-lean", "github", "https://github.com/ywatanabex/bp-response-geometry-lean"),
    "2611.12680": ("zenodo__24136107", "zenodo", "https://zenodo.org/records/24136107"),
    "2611.13584": ("dmivilensky__PolynomialRealizationsProgram", "github", "https://github.com/dmivilensky/PolynomialRealizationsProgram"),
    "2611.13872": ("k3nfalt__longtails", "github", "https://github.com/k3nfalt/longtails"),
    "2611.14475": ("ckuemmerle__ExplicitRIPTwoThirds", "github", "https://github.com/ckuemmerle/ExplicitRIPTwoThirds"),
    "2611.14756": ("magbenji__discrete-modified-gradient-lean", "github", "https://github.com/magbenji/discrete-modified-gradient-lean"),
    "2611.15128": ("leanEthereum__leanVM", "github", "https://github.com/leanEthereum/leanVM"),
    "2611.18220": ("manasdm__Lean-SysID", "github", "https://github.com/manasdm/Lean-SysID"),
    "2611.18455": ("inody__wmfki_lean", "github", "https://github.com/inody/wmfki_lean"),
    "2611.23762": ("guanyuzhu2014__Uniform-product-expansion---theory-and-Lean-certification", "github", "https://github.com/guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification"),
    "2611.26272": ("TTony2019__OptPaper", "github", "https://github.com/TTony2019/OptPaper"),
    "2605.02856": ("rayiskander2406__qanary-k-stage-composition-arXiv-2605.02856", "github", "https://github.com/rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856"),
    "2605.09552": ("mlexpos__phases-of-muon", "github", "https://github.com/mlexpos/phases-of-muon"),
    "2605.14610": ("SZabolotnii__Ku-PATP-code-supplement", "github", "https://github.com/SZabolotnii/Ku-PATP-code-supplement"),
}

COMPANION_REPOS: dict[str, list[tuple[str, str]]] = {
    "2605.09552": [("mlexpos__alea-foundations", "https://github.com/mlexpos/alea-foundations")],
}

FILE_LINE_RE = re.compile(r"((?:Lean code/)?[A-Za-z0-9_./-]+\.lean):(\d+)(?:[-–](\d+))?")


def _git_info(repo_path: Path) -> tuple[str | None, str | None]:
    if not (repo_path / ".git").exists():
        return None, None
    sha = subprocess.check_output(["git", "-C", str(repo_path), "rev-parse", "HEAD"], text=True).strip()
    dt = subprocess.check_output(["git", "-C", str(repo_path), "show", "-s", "--format=%cI", "HEAD"], text=True).strip()
    return sha, dt


def _lean_tree_sha256(repo_path: Path) -> tuple[str, int]:
    """Deterministic SHA-256 over all relative paths + contents of *.lean files."""
    h = hashlib.sha256()
    lean_files = sorted(repo_path.rglob("*.lean"))
    for lf in lean_files:
        rel = lf.relative_to(repo_path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(lf.read_bytes())
        h.update(b"\0")
    return h.hexdigest(), len(lean_files)


def _find_toolchain(repo_path: Path) -> str | None:
    tcs = sorted(repo_path.rglob("lean-toolchain"))
    for tc in tcs:
        if ".lake" in tc.parts:
            continue
        val = tc.read_text(encoding="utf-8", errors="replace").strip()
        if val:
            return val
    return None


def _resolve_lean_file(repo_paths: list[Path], cited_path: str) -> Path | None:
    """Resolve an auditor-cited relative Lean path (exact or suffix match) in repo_paths."""
    cited_clean = cited_path.lstrip("./")
    for rp in repo_paths:
        direct = rp / cited_clean
        if direct.is_file():
            return direct
    # Fallback: suffix match across *.lean files
    parts = Path(cited_clean).parts
    for rp in repo_paths:
        for lf in rp.rglob(Path(cited_clean).name):
            if ".lake" in lf.parts:
                continue
            rel_parts = lf.relative_to(rp).parts
            if len(rel_parts) >= len(parts) and rel_parts[-len(parts) :] == parts:
                return lf
    return None


def _verify_cited_file_lines(audit_item: dict, repo_paths: list[Path]) -> dict:
    """Check every `path/to/File.lean:line[-end]` reference in `theorems_compared`."""
    total_refs = 0
    resolved_in_bounds = 0
    unresolved: list[str] = []
    out_of_bounds: list[str] = []

    for thm in audit_item.get("theorems_compared", []):
        loc_str = thm.get("lean_file_and_line", "") or ""
        for m in FILE_LINE_RE.finditer(loc_str):
            total_refs += 1
            fpath, s_str, e_str = m.group(1), m.group(2), m.group(3)
            start_ln = int(s_str)
            end_ln = int(e_str) if e_str else start_ln
            resolved = _resolve_lean_file(repo_paths, fpath)
            if resolved is None:
                unresolved.append(m.group(0))
                continue
            nlines = len(resolved.read_text(encoding="utf-8", errors="replace").splitlines())
            if 1 <= start_ln <= nlines and end_ln <= nlines:
                resolved_in_bounds += 1
            else:
                out_of_bounds.append(f"{m.group(0)} (file has {nlines} lines)")

    return {
        "total_file_line_refs": total_refs,
        "resolved_in_bounds": resolved_in_bounds,
        "unresolved": unresolved,
        "out_of_bounds": out_of_bounds,
    }


def build_provenance() -> dict:
    records: list[dict] = []
    for slice_id, db_path, audit_path in SLICES:
        audits = json.loads(audit_path.read_text(encoding="utf-8"))
        items = audits if isinstance(audits, list) else audits.get("audits", [])
        conn = sqlite3.connect(str(db_path))

        for it in sorted(items, key=lambda x: x["arxiv_id"]):
            aid = it["arxiv_id"]
            prow = conn.execute(
                "SELECT version, submitted_date, updated_date FROM papers WHERE arxiv_id = ?",
                (aid,),
            ).fetchone()
            local_name, host, url = REPO_DIR_MAP[aid]
            repo_path = REPOS_DIR / local_name
            if not repo_path.is_dir():
                raise FileNotFoundError(f"Missing local repo for {aid}: {repo_path}")

            sha, cdate = _git_info(repo_path)
            tree_sha256, lean_file_count = _lean_tree_sha256(repo_path)
            toolchain = _find_toolchain(repo_path)

            search_paths = [repo_path]
            companions: list[dict] = []
            for comp_dir, comp_url in COMPANION_REPOS.get(aid, []):
                cpath = REPOS_DIR / comp_dir
                if cpath.is_dir():
                    search_paths.append(cpath)
                    csha, ccdate = _git_info(cpath)
                    companions.append(
                        {
                            "repo_url": comp_url,
                            "commit_sha": csha,
                            "commit_date": ccdate,
                        }
                    )

            fl_check = _verify_cited_file_lines(it, search_paths)

            rec = {
                "slice_id": slice_id,
                "arxiv_id": aid,
                "arxiv_version_audited": f"v{prow[0]}" if prow and prow[0] else None,
                "arxiv_submitted_date": prow[1] if prow else None,
                "arxiv_updated_date": prow[2] if prow else None,
                "repo_host": host,
                "repo_url": url,
                "commit_sha": sha,
                "commit_short_sha": sha[:7] if sha else None,
                "commit_date": cdate,
                "zenodo_record_id": local_name.split("__", 1)[1] if host == "zenodo" else None,
                "lean_files_count": lean_file_count,
                "lean_tree_sha256": tree_sha256,
                "lean_toolchain": toolchain,
                "companion_repos": companions,
                "overall_fidelity": it.get("overall_fidelity"),
                "mode1_severity": (it.get("mode1_statement_drift") or {}).get("severity"),
                "mode2_severity": (it.get("mode2_scope_downgrade") or {}).get("severity"),
                "mode3_severity": (it.get("mode3_definition_smuggling") or {}).get("severity"),
                "mode4_severity": (it.get("mode4_junk_or_vacuity") or {}).get("severity"),
                "theorems_compared_file_line_check": fl_check,
            }
            records.append(rec)

        conn.close()

    total_refs = sum(r["theorems_compared_file_line_check"]["total_file_line_refs"] for r in records)
    total_ok = sum(r["theorems_compared_file_line_check"]["resolved_in_bounds"] for r in records)
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_audited_repos": len(records),
        "git_pinned_count": sum(1 for r in records if r["commit_sha"]),
        "zenodo_pinned_count": sum(1 for r in records if r["zenodo_record_id"]),
        "theorems_compared_file_line_summary": {
            "total_refs": total_refs,
            "resolved_in_bounds": total_ok,
        },
        "records": records,
    }


def main() -> None:
    payload = build_provenance()
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    s = payload["theorems_compared_file_line_summary"]
    print(
        f"Wrote {OUT_PATH} ({payload['total_audited_repos']} repos: "
        f"{payload['git_pinned_count']} Git SHAs, {payload['zenodo_pinned_count']} Zenodo; "
        f"file:line checks {s['resolved_in_bounds']}/{s['total_refs']} resolved & in-bounds)"
    )
    for r in payload["records"]:
        chk = r["theorems_compared_file_line_check"]
        if chk["unresolved"] or chk["out_of_bounds"]:
            print(
                f"  [NOTE] {r['arxiv_id']}: unresolved={chk['unresolved']} out_of_bounds={chk['out_of_bounds']}"
            )


if __name__ == "__main__":
    main()
