#!/usr/bin/env python3
"""In-container execution entrypoint for isolated Lean 4 builds and axiom auditing.

Runs ONLY inside the unprivileged `--network=none` container with:
  - /src/repo      (read-only mount of the untrusted repository)
  - /src/packages  (optional read-only mount of pre-fetched .lake/packages)
  - /opt/elan      (read-only mount of pre-installed Lean 4 toolchains)
  - /work          (ephemeral writable scratch directory, destroyed on --rm)

Emits a single structured JSON summary line prefixed with `SANDBOX_RESULT_JSON:`
to stdout so the host orchestrator never has to parse untrusted files on disk.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


CHECK_AXIOMS_LIB = Path("/opt/sandbox/check_axioms.lean")


def _tail(text: str, max_chars: int = 2500) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return "...[truncated]...\n" + text[-max_chars:]


def _parse_axioms_json(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith("SANDBOX_AXIOMS_JSON:"):
            return json.loads(line[len("SANDBOX_AXIOMS_JSON:") :])
    return None


def _discover_built_modules(project_dir: Path, root_prefixes: list[str]) -> list[str]:
    """Find built .olean modules under .lake/build/lib/lean (or .lake/build/lib)."""
    mods: list[str] = []
    for base in (project_dir / ".lake" / "build" / "lib" / "lean", project_dir / ".lake" / "build" / "lib"):
        if not base.is_dir():
            continue
        for olean in sorted(base.rglob("*.olean")):
            rel = olean.relative_to(base).with_suffix("")
            mod = ".".join(rel.parts)
            if not root_prefixes or any(mod == p or mod.startswith(p + ".") for p in root_prefixes):
                mods.append(mod)
        if mods:
            break
    # Deduplicate preserving order
    seen: set[str] = set()
    uniq: list[str] = []
    for m in mods:
        if m not in seen:
            seen.add(m)
            uniq.append(m)
    return uniq


def _select_import_roots(built_mods: list[str], preferred_roots: list[str]) -> list[str]:
    """Prefer top-level umbrella modules if built; otherwise import all leaf modules."""
    if not built_mods:
        return preferred_roots
    built_set = set(built_mods)
    # Check if preferred roots cover everything, else include every built module so nothing is missed!
    # Importing every built module directly guarantees 100% theorem coverage even if an umbrella
    # module forgets to import a submodule.
    return built_mods


def _make_axiom_driver(imports: list[str], prefixes: list[str]) -> str:
    body = CHECK_AXIOMS_LIB.read_text(encoding="utf-8").replace("import Lean\n", "", 1)
    imp_lines = "\n".join(["import Lean"] + [f"import {m}" for m in imports])
    pref_lit = "[" + ", ".join(f'"{p}"' for p in prefixes) + "]"
    return (
        f"{imp_lines}\n"
        f"{body}\n\n"
        f"#eval SandboxAxiomAudit.runAudit {pref_lit} 60\n"
    )


def _run_cmd(
    cmd: list[str],
    cwd: Path,
    timeout: int,
    env: dict[str, str],
) -> tuple[int, str, str, float, bool]:
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr, time.monotonic() - t0, False
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return 124, out, err + f"\nTIMEOUT after {timeout}s", time.monotonic() - t0, True


def _mirror_tree(src_dir: Path, dst_dir: Path) -> None:
    """Create real dirs, symlink .git and immutable files, and copy mutable .hash/.trace files."""
    copy_suffixes = (".hash", ".trace", ".log.json")
    for root, dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        dst_root = dst_dir if rel == "." else dst_dir / rel
        dst_root.mkdir(parents=True, exist_ok=True)
        # Symlink .git directory directly without walking inside it
        if ".git" in dirs:
            dirs.remove(".git")
            os.symlink(os.path.join(root, ".git"), os.path.join(str(dst_root), ".git"))
        for fn in files:
            s = os.path.join(root, fn)
            d = os.path.join(str(dst_root), fn)
            if fn.endswith(copy_suffixes):
                shutil.copyfile(s, d)
            else:
                os.symlink(s, d)


def _stage_packages(src_pkgs: Path, dst_pkgs: Path) -> None:
    """Stage pre-fetched packages into writable .lake/packages without mutating read-only /src/packages."""
    dst_pkgs.mkdir(parents=True, exist_ok=True)
    for item in sorted(src_pkgs.iterdir()):
        target = dst_pkgs / item.name
        if target.exists() or target.is_symlink():
            continue
        if not item.is_dir():
            shutil.copy2(item, target)
            continue
        src_lake_build = item / ".lake" / "build"
        if src_lake_build.is_dir():
            _mirror_tree(item, target)
        else:
            # Unbuilt dependency (e.g., extra git package) -> copy so Lake can compile it inside /work
            shutil.copytree(item, target, symlinks=True)


def _resolve_toolchain_bin(proj_dir: Path, override_tc: str = "") -> Path | None:
    tc = override_tc.strip()
    if not tc:
        tc_file = proj_dir / "lean-toolchain"
        if tc_file.is_file():
            tc = tc_file.read_text(encoding="utf-8").strip()
    if not tc:
        return None
    tc_dir_name = tc.replace("/", "--").replace(":", "---")
    bin_dir = Path("/opt/elan/toolchains") / tc_dir_name / "bin"
    return bin_dir if bin_dir.is_dir() else None


def _env_with_toolchain(base_env: dict[str, str], proj_dir: Path, override_tc: str = "") -> dict[str, str]:
    env = base_env.copy()
    tc_bin = _resolve_toolchain_bin(proj_dir, override_tc)
    if tc_bin is not None:
        env["PATH"] = f"{tc_bin}:{env.get('PATH', '')}"
        env["LEAN_SYSROOT"] = str(tc_bin.parent)
    # Also give elan a writable local settings dir in /tmp pointing at read-only toolchains
    tmp_elan = Path("/tmp/elan_ro_shim")
    tmp_elan.mkdir(parents=True, exist_ok=True)
    tc_link = tmp_elan / "toolchains"
    if not tc_link.exists() and not tc_link.is_symlink():
        os.symlink("/opt/elan/toolchains", str(tc_link))
    settings = tmp_elan / "settings.toml"
    if not settings.exists():
        settings.write_text('version = "12"\n', encoding="utf-8")
    env["ELAN_HOME"] = str(tmp_elan)
    # Allow git inside Lake to read read-only mounted /src/packages owned by host UID
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "safe.directory"
    env["GIT_CONFIG_VALUE_0"] = "*"
    return env


def run_lake_mode(args: argparse.Namespace, work_repo: Path, env: dict[str, str]) -> dict[str, Any]:
    proj_dir = work_repo / args.project_subdir if args.project_subdir else work_repo
    if not proj_dir.is_dir():
        return {
            "exit_code": 2,
            "build_status": "fail_packaging",
            "wall_time_sec": 0.0,
            "error_summary": f"Project subdir not found: {args.project_subdir}",
        }

    src_pkgs = Path("/src/packages")
    if src_pkgs.is_dir() and any(src_pkgs.iterdir()):
        _stage_packages(src_pkgs, proj_dir / ".lake" / "packages")

    # Determine toolchain override if synthetic
    if args.synthetic_toolchain:
        (proj_dir / "lean-toolchain").write_text(args.synthetic_toolchain + "\n", encoding="utf-8")

    env = _env_with_toolchain(env, proj_dir, args.synthetic_toolchain)

    # Build command
    lake_cmd = ["lake", "build"]
    if args.lake_targets:
        lake_cmd.extend(args.lake_targets)

    rc, out, err, elapsed, timed_out = _run_cmd(lake_cmd, proj_dir, args.timeout, env)

    result: dict[str, Any] = {
        "exit_code": rc,
        "build_status": "timeout" if timed_out else ("pass" if rc == 0 else "fail_build"),
        "wall_time_sec": round(elapsed, 2),
        "build_stdout_tail": _tail(out, 1500),
        "build_stderr_tail": _tail(err, 2000),
        "error_summary": "" if rc == 0 else _tail((err + "\n" + out).strip(), 1200),
        "axioms_audit": None,
    }

    if rc != 0:
        # Classify failure reason cleanly
        combined = (err + "\n" + out).lower()
        if timed_out:
            result["build_status"] = "timeout"
        elif "package directory not found" in combined or (
            "no such file or directory" in combined and ("../" in combined or "qanary" in combined)
        ):
            result["build_status"] = "fail_missing_local_dep"
        elif "could not resolve host" in combined or "unable to access" in combined or "failed to fetch" in combined:
            result["build_status"] = "fail_network_dep"
        return result

    # Run programmatic #print axioms across ALL built project modules!
    prefixes = args.module_prefixes or args.lake_targets or []
    built_mods = _discover_built_modules(proj_dir, prefixes)
    if not built_mods and prefixes:
        built_mods = list(prefixes)

    if built_mods:
        driver_src = _make_axiom_driver(built_mods, prefixes if prefixes else [m.split(".")[0] for m in built_mods])
        driver_path = proj_dir / "_SandboxAxiomAudit.lean"
        driver_path.write_text(driver_src, encoding="utf-8")
        arc, aout, aerr, aelapsed, atimed_out = _run_cmd(
            ["lake", "env", "lean", str(driver_path.name)],
            proj_dir,
            min(300, max(60, args.timeout // 3)),
            env,
        )
        parsed = _parse_axioms_json(aout)
        result["axiom_check_wall_time_sec"] = round(aelapsed, 2)
        result["axiom_check_exit_code"] = arc
        if parsed is not None:
            result["axioms_audit"] = parsed
        else:
            result["axiom_check_error"] = _tail((aerr + "\n" + aout).strip(), 1200)
    return result


def run_lean_files_mode(args: argparse.Namespace, work_repo: Path, env: dict[str, str]) -> dict[str, Any]:
    """Run direct `lean` compilation + axiom check on standalone files (e.g. Std-only TrustBound)."""
    proj_dir = work_repo / args.project_subdir if args.project_subdir else work_repo
    env = _env_with_toolchain(env, proj_dir, args.synthetic_toolchain)
    existing_lp = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{proj_dir}:{existing_lp}" if existing_lp else str(proj_dir)
    files = args.lean_files or []
    if not files:
        files = sorted(str(p.relative_to(proj_dir)) for p in proj_dir.glob("*.lean"))

    t_start = time.monotonic()
    total_theorems = 0
    std_axioms: list[str] = []
    nonstd_axioms: list[str] = []
    sorry_det = False
    of_reduce_det = False
    trust_comp_det = False
    axioms_by_thm: dict[str, list[str]] = {}
    file_results: list[dict[str, Any]] = []
    overall_rc = 0
    errors: list[str] = []

    check_lib = CHECK_AXIOMS_LIB.read_text(encoding="utf-8")
    for rel_f in files:
        fpath = proj_dir / rel_f
        if not fpath.is_file():
            overall_rc = 2
            errors.append(f"Missing file: {rel_f}")
            continue
        olean_path = fpath.with_suffix(".olean")
        rc, out, err, dt, timed_out = _run_cmd(
            ["lean", "-o", str(olean_path), str(fpath)], proj_dir, args.timeout, env
        )
        file_results.append({"file": rel_f, "exit_code": rc, "wall_time_sec": round(dt, 2)})
        if rc != 0:
            overall_rc = rc
            errors.append(f"{rel_f}: {_tail(err + ' ' + out, 500)}")
            continue

        # Axiom audit: prepend `import Lean` (only if not already imported) and append runAudit ["__LOCAL__"]
        orig_src = fpath.read_text(encoding="utf-8")
        # Place `import Lean` right after existing import lines
        lines = orig_src.splitlines()
        imp_idx = 0
        for idx, line in enumerate(lines):
            s = line.strip()
            if s.startswith("import "):
                imp_idx = idx + 1
            elif s and not s.startswith("--") and not s.startswith("/-"):
                break
        has_import_lean = any(l.strip() == "import Lean" for l in lines[: imp_idx + 1])
        body_without_import_lean = check_lib.replace("import Lean\n", "")
        augmented = (
            "\n".join(lines[:imp_idx])
            + ("\n" if imp_idx > 0 else "")
            + ("" if has_import_lean else "import Lean\n")
            + "\n".join(lines[imp_idx:])
            + "\n\n"
            + body_without_import_lean
            + '\n#eval SandboxAxiomAudit.runAudit ["__LOCAL__"] 60\n'
        )
        tmp_f = proj_dir / f"_audit_{fpath.name}"
        tmp_f.write_text(augmented, encoding="utf-8")
        arc, aout, aerr, _, _ = _run_cmd(["lean", str(tmp_f)], proj_dir, 180, env)
        tmp_f.unlink(missing_ok=True)
        parsed = _parse_axioms_json(aout)
        if parsed:
            total_theorems += int(parsed.get("total_theorems_checked", 0))
            for a in parsed.get("standard_axioms_used", []):
                if a not in std_axioms:
                    std_axioms.append(a)
            for a in parsed.get("nonstandard_axioms_detected", []):
                if a not in nonstd_axioms:
                    nonstd_axioms.append(a)
            sorry_det = sorry_det or bool(parsed.get("sorry_ax_detected"))
            of_reduce_det = of_reduce_det or bool(parsed.get("of_reduce_bool_detected"))
            trust_comp_det = trust_comp_det or bool(parsed.get("trust_compiler_detected"))
            for k, v in parsed.get("axioms_by_theorem", {}).items():
                if len(axioms_by_thm) < 80 or any(a not in ("propext", "Classical.choice", "Quot.sound") for a in v):
                    axioms_by_thm[f"{fpath.stem}.{k}"] = v
        else:
            errors.append(f"axiom audit parse failed for {rel_f}: {_tail(aerr + ' ' + aout, 400)}")

    total_dt = time.monotonic() - t_start
    return {
        "exit_code": overall_rc,
        "build_status": "pass" if overall_rc == 0 else "fail_build",
        "wall_time_sec": round(total_dt, 2),
        "files_checked": file_results,
        "error_summary": "\n".join(errors)[:1200],
        "axioms_audit": {
            "target_modules_count": len(file_results),
            "total_theorems_checked": total_theorems,
            "standard_axioms_used": std_axioms,
            "nonstandard_axioms_detected": nonstd_axioms,
            "sorry_ax_detected": sorry_det,
            "of_reduce_bool_detected": of_reduce_det,
            "trust_compiler_detected": trust_comp_det,
            "axioms_by_theorem": axioms_by_thm,
        }
        if overall_rc == 0
        else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["lake", "lean_files", "synthetic_mathlib"], required=True)
    ap.add_argument("--project-subdir", default="")
    ap.add_argument("--lake-targets", nargs="*", default=[])
    ap.add_argument("--module-prefixes", nargs="*", default=[])
    ap.add_argument("--lean-files", nargs="*", default=[])
    ap.add_argument("--synthetic-toolchain", default="")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    work_repo = Path("/work/repo")
    if work_repo.exists():
        shutil.rmtree(work_repo)

    # Copy read-only source repo into ephemeral writable /work/repo (skipping .git/.lake)
    def _ignore(dirpath: str, names: list[str]) -> set[str]:
        return {n for n in names if n in (".git", ".lake")}

    shutil.copytree(Path("/src/repo"), work_repo, symlinks=True, ignore=_ignore)

    env = os.environ.copy()
    env["ELAN_HOME"] = "/opt/elan"
    env["HOME"] = "/tmp"
    env["TMPDIR"] = "/tmp"

    if args.mode == "lake":
        res = run_lake_mode(args, work_repo, env)
    elif args.mode == "lean_files":
        res = run_lean_files_mode(args, work_repo, env)
    elif args.mode == "synthetic_mathlib":
        # Copy standalone .lean files into a synthetic Lake project backed by /src/packages (Mathlib)
        syn_dir = Path("/work/synthetic_proj")
        syn_dir.mkdir(parents=True, exist_ok=True)
        (syn_dir / "lean-toolchain").write_text(args.synthetic_toolchain + "\n", encoding="utf-8")
        env = _env_with_toolchain(env, syn_dir, args.synthetic_toolchain)
        src_pkgs = Path("/src/packages")
        if src_pkgs.is_dir():
            _stage_packages(src_pkgs, syn_dir / ".lake" / "packages")
        # Copy synthetic lakefile/manifest if provided in /src/synthetic_meta
        syn_meta = Path("/src/synthetic_meta")
        if syn_meta.is_dir():
            for f in ("lakefile.toml", "lake-manifest.json"):
                if (syn_meta / f).is_file():
                    shutil.copy2(syn_meta / f, syn_dir / f)

        # Copy target .lean files and run `lake env lean <file>` on each!
        src_base = work_repo / args.project_subdir if args.project_subdir else work_repo
        t_start = time.monotonic()
        total_theorems = 0
        std_axioms: list[str] = []
        nonstd_axioms: list[str] = []
        sorry_det = False
        of_reduce_det = False
        trust_comp_det = False
        axioms_by_thm: dict[str, list[str]] = {}
        file_results: list[dict[str, Any]] = []
        overall_rc = 0
        errors: list[str] = []
        check_lib = CHECK_AXIOMS_LIB.read_text(encoding="utf-8").replace("import Lean\n", "")

        for rel_f in args.lean_files:
            fpath = src_base / rel_f
            if not fpath.is_file():
                overall_rc = 2
                errors.append(f"Missing file: {rel_f}")
                continue
            rc, out, err, dt, timed_out = _run_cmd(["lake", "env", "lean", str(fpath)], syn_dir, args.timeout, env)
            file_results.append({"file": rel_f, "exit_code": rc, "wall_time_sec": round(dt, 2)})
            if rc != 0:
                overall_rc = rc
                errors.append(f"{rel_f}: {_tail(err + ' ' + out, 500)}")
                continue
            orig_src = fpath.read_text(encoding="utf-8")
            lines = orig_src.splitlines()
            imp_idx = 0
            for idx, line in enumerate(lines):
                s = line.strip()
                if s.startswith("import "):
                    imp_idx = idx + 1
                elif s and not s.startswith("--") and not s.startswith("/-"):
                    break
            augmented = (
                "\n".join(lines[:imp_idx])
                + ("\n" if imp_idx > 0 else "")
                + "import Lean\n"
                + "\n".join(lines[imp_idx:])
                + "\n\n"
                + check_lib
                + '\n#eval SandboxAxiomAudit.runAudit ["__LOCAL__"] 60\n'
            )
            tmp_f = syn_dir / f"_audit_{fpath.name}"
            tmp_f.write_text(augmented, encoding="utf-8")
            arc, aout, aerr, _, _ = _run_cmd(["lake", "env", "lean", str(tmp_f)], syn_dir, 240, env)
            tmp_f.unlink(missing_ok=True)
            parsed = _parse_axioms_json(aout)
            if parsed:
                total_theorems += int(parsed.get("total_theorems_checked", 0))
                for a in parsed.get("standard_axioms_used", []):
                    if a not in std_axioms:
                        std_axioms.append(a)
                for a in parsed.get("nonstandard_axioms_detected", []):
                    if a not in nonstd_axioms:
                        nonstd_axioms.append(a)
                sorry_det = sorry_det or bool(parsed.get("sorry_ax_detected"))
                of_reduce_det = of_reduce_det or bool(parsed.get("of_reduce_bool_detected"))
                trust_comp_det = trust_comp_det or bool(parsed.get("trust_compiler_detected"))
                for k, v in parsed.get("axioms_by_theorem", {}).items():
                    if len(axioms_by_thm) < 80 or any(a not in ("propext", "Classical.choice", "Quot.sound") for a in v):
                        axioms_by_thm[f"{fpath.stem}.{k}"] = v
            else:
                errors.append(f"axiom audit parse failed for {rel_f}: {_tail(aerr + ' ' + aout, 400)}")

        res = {
            "exit_code": overall_rc,
            "build_status": "pass" if overall_rc == 0 else "fail_build",
            "wall_time_sec": round(time.monotonic() - t_start, 2),
            "files_checked": file_results,
            "error_summary": "\n".join(errors)[:1200],
            "axioms_audit": {
                "target_modules_count": len(file_results),
                "total_theorems_checked": total_theorems,
                "standard_axioms_used": std_axioms,
                "nonstandard_axioms_detected": nonstd_axioms,
                "sorry_ax_detected": sorry_det,
                "of_reduce_bool_detected": of_reduce_det,
                "trust_compiler_detected": trust_comp_det,
                "axioms_by_theorem": axioms_by_thm,
            }
            if overall_rc == 0
            else None,
        }
    else:
        raise SystemExit(f"Unsupported mode: {args.mode}")

    print("SANDBOX_RESULT_JSON:" + json.dumps(res, sort_keys=True))


if __name__ == "__main__":
    main()
