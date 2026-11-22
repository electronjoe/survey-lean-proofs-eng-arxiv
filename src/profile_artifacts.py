"""Step 3: Static LaTeX source & GitHub repo profiler for Lean candidate papers.

STRICTLY STATIC: never executes `lake build`, `#eval`, or any repo code.
Uses authenticated `gh api` (5,000 req/hr) + shallow git clone for static file scanning.
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import subprocess
import tarfile
import time
from pathlib import Path
from typing import Any

import httpx

from src.db import DEFAULT_DB_PATH, connect, upsert_artifact_profile
from src.patterns import scan_latex_source, scan_lean_source

USER_AGENT = "survey-lean-proofs-eng-arxiv/0.1 (academic research survey; static profiler)"
GITHUB_REPO_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)")
SKIP_REPOS = {
    ("arxiv", "html_feedback"),
    ("brucemiller", "latexml"),
    ("leanprover", "lean4"),
    ("leanprover-community", "mathlib4"),
    ("leanprover-community", "mathlib"),
    ("leanprover", "lean"),
    ("openai", "math"),
}
MAX_CLONE_KB = 200_000  # Skip cloning multi-hundred-MB monorepos; still record metadata/tree


def _gh_api_json(endpoint: str) -> Any | None:
    proc = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def fetch_and_scan_latex(client: httpx.Client, arxiv_id: str, version: int) -> tuple[bool, dict[str, Any]]:
    url = f"https://arxiv.org/src/{arxiv_id}v{version}"
    try:
        r = client.get(url, follow_redirects=True)
        if r.status_code != 200 or not r.content:
            return False, {"error": f"status={r.status_code}"}
        raw = r.content
        tex_parts: list[str] = []
        # Try tar.gz / tar
        try:
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as tf:
                for member in tf.getmembers():
                    if member.isfile() and member.name.lower().endswith((".tex", ".sty", ".lean")):
                        f = tf.extractfile(member)
                        if f is not None:
                            data = f.read().decode("utf-8", errors="ignore")
                            if member.name.lower().endswith(".tex"):
                                tex_parts.append(data)
        except tarfile.TarError:
            # Maybe single gzipped .tex or plain .tex
            try:
                tex_parts.append(gzip.decompress(raw).decode("utf-8", errors="ignore"))
            except Exception:
                tex_parts.append(raw.decode("utf-8", errors="ignore"))

        combined_tex = "\n".join(tex_parts)
        signals = scan_latex_source(combined_tex)
        signals["tex_files_chars"] = len(combined_tex)
        return True, signals
    except Exception as exc:
        return False, {"error": str(exc)}


def profile_github_repo(owner: str, repo: str, clone_root: Path) -> dict[str, Any]:
    repo = repo.removesuffix(".git")
    full_name = f"{owner}/{repo}"
    meta = _gh_api_json(f"repos/{full_name}")
    if not meta or "full_name" not in meta:
        return {"repo": full_name, "accessible": False}

    default_branch = meta.get("default_branch", "main")
    tree_data = _gh_api_json(f"repos/{full_name}/git/trees/{default_branch}?recursive=1")
    paths = [item["path"] for item in (tree_data or {}).get("tree", []) if item.get("type") == "blob"]

    lean_files = [p for p in paths if p.endswith(".lean")]
    tex_files = [p for p in paths if p.endswith(".tex")]
    workflow_files = [p for p in paths if p.startswith(".github/workflows/")]
    has_lean_toolchain = any(p.endswith("lean-toolchain") for p in paths)
    has_lakefile = any(p.endswith(("lakefile.lean", "lakefile.toml")) for p in paths)
    has_challenge_file = any("challenge" in p.lower() and p.endswith(".lean") for p in paths)
    has_solution_file = any("solution" in p.lower() and p.endswith(".lean") for p in paths)
    has_blueprint_dir = any("blueprint" in p.lower() for p in paths)

    profile: dict[str, Any] = {
        "repo": full_name,
        "accessible": True,
        "created_at": meta.get("created_at"),
        "pushed_at": meta.get("pushed_at"),
        "default_branch": default_branch,
        "stars": meta.get("stargazers_count", 0),
        "description": meta.get("description"),
        "total_files": len(paths),
        "lean_file_count": len(lean_files),
        "tex_file_count": len(tex_files),
        "has_lean_toolchain": has_lean_toolchain,
        "has_lakefile": has_lakefile,
        "has_challenge_file": has_challenge_file,
        "has_solution_file": has_solution_file,
        "has_blueprint_dir": has_blueprint_dir,
        "workflow_files": workflow_files,
    }

    # Commit timeline summary (first/last commits touching .lean vs .tex via GitHub API)
    commits = _gh_api_json(f"repos/{full_name}/commits?per_page=30")
    if isinstance(commits, list):
        profile["recent_commit_count"] = len(commits)
        if commits:
            profile["latest_commit_date"] = commits[0].get("commit", {}).get("author", {}).get("date")
            profile["earliest_sampled_commit_date"] = commits[-1].get("commit", {}).get("author", {}).get("date")

    # Only shallow-clone if repo actually contains Lean files and is reasonable size (strictly static inspection)
    repo_size_kb = meta.get("size", 0) or 0
    profile["size_kb"] = repo_size_kb
    if lean_files or has_lean_toolchain or has_lakefile:
        target_dir = clone_root / f"{owner}__{repo}"
        if repo_size_kb > MAX_CLONE_KB:
            profile["clone_skipped"] = f"size_kb={repo_size_kb}>{MAX_CLONE_KB}"
        elif not target_dir.exists():
            clone_root.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", f"https://github.com/{full_name}.git", str(target_dir)],
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
            except subprocess.TimeoutExpired:
                profile["clone_skipped"] = "timeout_90s"
        if target_dir.exists() and not profile.get("clone_skipped"):
            # Read lean-toolchain if present
            tc_files = list(target_dir.rglob("lean-toolchain"))
            if tc_files:
                profile["lean_toolchain"] = tc_files[0].read_text(errors="ignore").strip()[:120]

            # Read CI workflows for comparator / paranoid / print axioms / axle / safeverify
            ci_signals: list[str] = []
            for wf in target_dir.glob(".github/workflows/*"):
                if wf.is_file():
                    wf_txt = wf.read_text(errors="ignore")
                    for kw in ["lake build", "comparator", "--paranoid", "leanchecker", "nanoda", "print axioms", "axle", "SafeVerify", "leanblueprint"]:
                        if kw.lower() in wf_txt.lower():
                            ci_signals.append(kw)
            profile["ci_signals"] = sorted(set(ci_signals))

            # Scan all .lean files statically (skip .lake if any)
            agg: dict[str, int] = {}
            scanned_files = 0
            for lf in target_dir.rglob("*.lean"):
                if ".lake" in lf.parts:
                    continue
                try:
                    code = lf.read_text(errors="ignore")
                except Exception:
                    continue
                counts = scan_lean_source(code)
                for k, v in counts.items():
                    agg[k] = agg.get(k, 0) + v
                scanned_files += 1
            profile["lean_files_scanned"] = scanned_files
            profile["lean_static_counts"] = agg

            # Read README preview (first 1500 chars)
            for rname in ("README.md", "readme.md", "README.rst", "README"):
                rp = target_dir / rname
                if rp.is_file():
                    profile["readme_preview"] = rp.read_text(errors="ignore")[:1500]
                    break

    return profile


def run_profile(
    db_path: Path = DEFAULT_DB_PATH,
    clone_root: Path = Path("data/repos"),
    include_contextual: bool = True,
) -> None:
    conn = connect(db_path)
    where = "(s.has_lean_strong = 1 OR s.has_lean_contextual = 1)" if include_contextual else "s.has_lean_strong = 1"
    rows = conn.execute(
        f"""
        SELECT p.arxiv_id, p.version, p.title, s.has_lean_strong, s.has_lean_contextual, s.urls_json
        FROM papers p
        JOIN screen_results s ON p.arxiv_id = s.arxiv_id
        LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
        WHERE {where} AND a.arxiv_id IS NULL
        ORDER BY s.has_lean_strong DESC, p.submitted_date DESC
        """
    ).fetchall()

    print(f"Profiling {len(rows)} Lean candidate papers...", flush=True)
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
        for i, row in enumerate(rows, 1):
            arxiv_id = row["arxiv_id"]
            version = row["version"]
            urls = json.loads(row["urls_json"])
            print(f"[{i}/{len(rows)}] {arxiv_id} (strong={row['has_lean_strong']}, ctx={row['has_lean_contextual']}) urls={len(urls)}", flush=True)

            latex_ok, latex_signals = fetch_and_scan_latex(client, arxiv_id, version)
            time.sleep(1.0)

            seen_repos: set[tuple[str, str]] = set()
            repo_profiles: list[dict[str, Any]] = []
            for u in urls:
                m = GITHUB_REPO_RE.match(u)
                if not m:
                    continue
                owner, repo = m.group(1), m.group(2).removesuffix(".git")
                key = (owner.lower(), repo.lower())
                if key in SKIP_REPOS:
                    continue
                if key in seen_repos:
                    continue
                seen_repos.add(key)
                prof = profile_github_repo(owner, repo, clone_root)
                repo_profiles.append(prof)
                if prof.get("lean_file_count", 0) > 0:
                    print(
                        f"    -> LEAN REPO {prof['repo']}: {prof['lean_file_count']} .lean files, "
                        f"LoC={prof.get('lean_static_counts', {}).get('loc_nonempty', 0)}, "
                        f"sorry={prof.get('lean_static_counts', {}).get('sorry', 0)}, "
                        f"axiom={prof.get('lean_static_counts', {}).get('custom_axiom', 0)}",
                        flush=True,
                    )

            with conn:
                upsert_artifact_profile(conn, arxiv_id, latex_ok, latex_signals, repo_profiles)

    conn.close()
    print("Done profiling Lean candidates.", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Static LaTeX + GitHub profiler for Lean candidate papers.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--clone-root", type=Path, default=Path("data/repos"))
    ap.add_argument("--strong-only", action="store_true")
    args = ap.parse_args()
    run_profile(db_path=args.db, clone_root=args.clone_root, include_contextual=not args.strong_only)


if __name__ == "__main__":
    main()
