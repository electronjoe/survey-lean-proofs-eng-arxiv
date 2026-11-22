"""Step 3: Static LaTeX source & GitHub/GitLab/Zenodo artifact profiler for Lean candidate papers.

STRICTLY STATIC: never executes `lake build`, `#eval`, or any repo code.
Supports:
- GitHub repos via authenticated `gh api` (5,000 req/hr) + shallow git clone
- GitLab repos (gitlab.com and self-hosted gitlab.* instances) via shallow git clone
- Zenodo records (zenodo.org/records/<id> and doi.org/10.5281/zenodo.<id>) via Zenodo REST API + static archive scan
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import time
import zipfile
from pathlib import Path
from typing import Any

import httpx

from src.db import DEFAULT_DB_PATH, connect, upsert_artifact_profile
from src.patterns import REPO_URL_RE, scan_latex_source, scan_lean_source

USER_AGENT = "survey-lean-proofs-eng-arxiv/0.2 (academic research survey; static profiler)"
GITHUB_REPO_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.IGNORECASE)
GITLAB_REPO_RE = re.compile(
    r"https?://(gitlab\.[A-Za-z0-9.\-]+)/([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+)",
    re.IGNORECASE,
)
ZENODO_ID_RE = re.compile(
    r"(?:zenodo\.org/(?:records?|deposit)/|doi\.org/10\.5281/zenodo\.)(\d+)",
    re.IGNORECASE,
)
SKIP_REPOS = {
    ("arxiv", "html_feedback"),
    ("brucemiller", "latexml"),
    ("leanprover", "lean4"),
    ("leanprover-community", "mathlib4"),
    ("leanprover-community", "mathlib"),
    ("leanprover", "lean"),
    ("openai", "math"),
}
MAX_CLONE_KB = 600_000  # Allow up to ~600 MB repos (e.g. leanVM ~420 MB); still skip multi-GB monorepos
MAX_ZENODO_MB = 500.0


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


def _scan_local_dir(target_dir: Path, profile: dict[str, Any]) -> None:
    """Strictly static scan of a cloned repo or extracted archive directory."""
    all_files = [p for p in target_dir.rglob("*") if p.is_file() and ".git" not in p.parts and ".lake" not in p.parts]
    rel_paths = [str(p.relative_to(target_dir)) for p in all_files]

    lean_files = [p for p in all_files if p.suffix == ".lean"]
    tex_files = [p for p in all_files if p.suffix == ".tex"]

    profile.setdefault("total_files", len(rel_paths))
    profile["lean_file_count"] = max(profile.get("lean_file_count", 0), len(lean_files))
    profile["tex_file_count"] = max(profile.get("tex_file_count", 0), len(tex_files))
    profile["has_lean_toolchain"] = profile.get("has_lean_toolchain", False) or any(
        Path(rp).name == "lean-toolchain" for rp in rel_paths
    )
    profile["has_lakefile"] = profile.get("has_lakefile", False) or any(
        Path(rp).name in ("lakefile.lean", "lakefile.toml") for rp in rel_paths
    )
    profile["has_challenge_file"] = profile.get("has_challenge_file", False) or any(
        "challenge" in rp.lower() and rp.endswith(".lean") for rp in rel_paths
    )
    profile["has_solution_file"] = profile.get("has_solution_file", False) or any(
        "solution" in rp.lower() and rp.endswith(".lean") for rp in rel_paths
    )
    profile["has_blueprint_dir"] = profile.get("has_blueprint_dir", False) or any(
        "blueprint" in rp.lower() for rp in rel_paths
    )
    profile["local_dir"] = str(target_dir.resolve())

    # Read lean-toolchain if present
    tc_files = [p for p in all_files if p.name == "lean-toolchain"]
    if tc_files:
        profile["lean_toolchain"] = tc_files[0].read_text(errors="ignore").strip()[:120]

    # Read CI workflows (.github/workflows or .gitlab-ci.yml)
    ci_signals: list[str] = []
    ci_files = [
        p
        for p in all_files
        if ".github/workflows/" in str(p.relative_to(target_dir)) or p.name == ".gitlab-ci.yml"
    ]
    for wf in ci_files:
        wf_txt = wf.read_text(errors="ignore")
        for kw in [
            "lake build",
            "comparator",
            "--paranoid",
            "leanchecker",
            "nanoda",
            "print axioms",
            "axle",
            "SafeVerify",
            "leanblueprint",
        ]:
            if kw.lower() in wf_txt.lower():
                ci_signals.append(kw)
    profile["ci_signals"] = sorted(set(ci_signals))

    # Scan all .lean files statically
    agg: dict[str, int] = {}
    scanned_files = 0
    for lf in lean_files:
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
    for rname in ("README.md", "readme.md", "README.rst", "README", "README.txt"):
        candidates = sorted(target_dir.rglob(rname), key=lambda p: len(p.parts))
        if candidates and candidates[0].is_file():
            profile["readme_preview"] = candidates[0].read_text(errors="ignore")[:1500]
            break


def _archive_contains_lean_tar(raw: bytes) -> bool:
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                name = m.name.lower()
                base = Path(m.name).name.lower()
                if name.endswith(".lean") or base in ("lean-toolchain", "lakefile.lean", "lakefile.toml"):
                    return True
    except tarfile.TarError:
        return False
    return False


def _archive_contains_lean_zip(raw: bytes) -> bool:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = info.filename.lower()
                base = Path(info.filename).name.lower()
                if name.endswith(".lean") or base in ("lean-toolchain", "lakefile.lean", "lakefile.toml"):
                    return True
    except zipfile.BadZipFile:
        return False
    return False


def _extract_arxiv_ancillary_lean(raw: bytes, arxiv_id: str, clone_root: Path) -> dict[str, Any] | None:
    """Strictly static extraction & scan of Lean files or nested Lean archives inside an arXiv /src tarball."""
    try:
        tf_check = tarfile.open(fileobj=io.BytesIO(raw), mode="r:*")
    except tarfile.TarError:
        return None

    direct_lean_members: list[tarfile.TarInfo] = []
    nested_lean_archives: list[tuple[str, bytes, str]] = []
    readme_members: list[tarfile.TarInfo] = []

    with tf_check as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            low = member.name.lower()
            base = Path(member.name).name.lower()
            if low.endswith(".lean") or base in ("lean-toolchain", "lakefile.lean", "lakefile.toml"):
                direct_lean_members.append(member)
            elif base in ("readme.md", "readme.txt", "readme", "manifest.txt") and "anc" in low:
                readme_members.append(member)
            elif low.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
                f = tf.extractfile(member)
                if f is not None:
                    data = f.read()
                    if _archive_contains_lean_tar(data):
                        nested_lean_archives.append((member.name, data, "tar"))
            elif low.endswith(".zip"):
                f = tf.extractfile(member)
                if f is not None:
                    data = f.read()
                    if _archive_contains_lean_zip(data):
                        nested_lean_archives.append((member.name, data, "zip"))

        if not direct_lean_members and not nested_lean_archives:
            return None

        target_dir = clone_root / f"arxiv_anc__{arxiv_id}"
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_resolved = target_dir.resolve()

        extracted_bytes = 0
        for member in direct_lean_members + readme_members:
            out_path = (target_dir / member.name).resolve()
            if not str(out_path).startswith(str(dest_resolved)):
                continue
            f = tf.extractfile(member)
            if f is not None:
                data = f.read()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(data)
                extracted_bytes += len(data)

        extracted_archives: list[str] = []
        seen_hashes: set[str] = set()
        for arc_name, arc_bytes, arc_kind in nested_lean_archives:
            digest = hashlib.sha256(arc_bytes).hexdigest()
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            stem = Path(arc_name).name
            for suf in (".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".tar", ".zip"):
                if stem.lower().endswith(suf):
                    stem = stem[: -len(suf)]
                    break
            arc_dest = target_dir / stem
            if arc_kind == "tar":
                with tarfile.open(fileobj=io.BytesIO(arc_bytes), mode="r:*") as ntf:
                    _safe_extract_tar(ntf, arc_dest)
            else:
                with zipfile.ZipFile(io.BytesIO(arc_bytes)) as nzf:
                    _safe_extract_zip(nzf, arc_dest)
            extracted_bytes += len(arc_bytes)
            extracted_archives.append(arc_name)

    profile: dict[str, Any] = {
        "host": "arxiv_ancillary",
        "repo": f"arxiv-anc/{arxiv_id}",
        "accessible": True,
        "size_kb": extracted_bytes // 1024,
    }
    if extracted_archives:
        profile["extracted_archives"] = extracted_archives
    _scan_local_dir(target_dir, profile)
    return profile


def fetch_and_scan_latex(
    client: httpx.Client,
    arxiv_id: str,
    version: int,
    clone_root: Path | None = None,
) -> tuple[bool, dict[str, Any], list[str], dict[str, Any] | None]:
    url = f"https://arxiv.org/src/{arxiv_id}v{version}"
    try:
        r = client.get(url, follow_redirects=True)
        if r.status_code != 200 or not r.content:
            return False, {"error": f"status={r.status_code}"}, [], None
        raw = r.content
        tex_parts: list[str] = []
        try:
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as tf:
                for member in tf.getmembers():
                    if member.isfile() and member.name.lower().endswith((".tex", ".sty", ".bbl", ".lean")):
                        f = tf.extractfile(member)
                        if f is not None:
                            data = f.read().decode("utf-8", errors="ignore")
                            if member.name.lower().endswith((".tex", ".bbl")):
                                tex_parts.append(data)
        except tarfile.TarError:
            try:
                tex_parts.append(gzip.decompress(raw).decode("utf-8", errors="ignore"))
            except Exception:
                tex_parts.append(raw.decode("utf-8", errors="ignore"))

        combined_tex = "\n".join(tex_parts)
        signals = scan_latex_source(combined_tex)
        signals["tex_files_chars"] = len(combined_tex)
        found_urls = sorted({u.rstrip(".,;:)]}\"'\\}") for u in REPO_URL_RE.findall(combined_tex)})
        anc_profile = (
            _extract_arxiv_ancillary_lean(raw, arxiv_id, clone_root)
            if clone_root is not None
            else None
        )
        return True, signals, found_urls, anc_profile
    except Exception as exc:
        return False, {"error": str(exc)}, [], None


def profile_github_repo(owner: str, repo: str, clone_root: Path) -> dict[str, Any]:
    repo = repo.removesuffix(".git")
    full_name = f"{owner}/{repo}"
    meta = _gh_api_json(f"repos/{full_name}")
    if not meta or "full_name" not in meta:
        return {"host": "github", "repo": full_name, "accessible": False}

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
        "host": "github",
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

    commits = _gh_api_json(f"repos/{full_name}/commits?per_page=30")
    if isinstance(commits, list):
        profile["recent_commit_count"] = len(commits)
        if commits:
            profile["latest_commit_date"] = commits[0].get("commit", {}).get("author", {}).get("date")
            profile["earliest_sampled_commit_date"] = commits[-1].get("commit", {}).get("author", {}).get("date")

    repo_size_kb = meta.get("size", 0) or 0
    profile["size_kb"] = repo_size_kb
    lean_archives = [
        p
        for p in paths
        if p.lower().endswith((".zip", ".tar.gz", ".tgz")) and "lean" in Path(p).name.lower()
    ]
    if lean_files or has_lean_toolchain or has_lakefile or lean_archives:
        target_dir = clone_root / f"{owner}__{repo}"
        if repo_size_kb > MAX_CLONE_KB:
            profile["clone_skipped"] = f"size_kb={repo_size_kb}>{MAX_CLONE_KB}"
        elif not target_dir.exists():
            clone_root.mkdir(parents=True, exist_ok=True)
            env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
            try:
                proc = subprocess.run(
                    ["git", "clone", "--depth", "1", f"https://github.com/{full_name}.git", str(target_dir)],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    env=env,
                )
                if proc.returncode != 0:
                    profile["clone_skipped"] = f"git_rc={proc.returncode}"
            except subprocess.TimeoutExpired:
                profile["clone_skipped"] = "timeout_180s"
        if target_dir.exists() and not profile.get("clone_skipped"):
            if lean_archives and not lean_files:
                extracted_root = target_dir / "_extracted_archives"
                extracted_archives: list[str] = []
                seen_hashes: set[str] = set()
                for rel_arc in sorted(lean_archives, key=lambda x: (len(Path(x).parts), x)):
                    arc_path = target_dir / rel_arc
                    if not arc_path.is_file():
                        continue
                    arc_bytes = arc_path.read_bytes()
                    digest = hashlib.sha256(arc_bytes).hexdigest()
                    if digest in seen_hashes:
                        continue
                    seen_hashes.add(digest)
                    low = rel_arc.lower()
                    if low.endswith(".zip") and _archive_contains_lean_zip(arc_bytes):
                        dest = extracted_root / arc_path.stem
                        if dest.exists():
                            continue
                        with zipfile.ZipFile(io.BytesIO(arc_bytes)) as zf:
                            _safe_extract_zip(zf, dest)
                        extracted_archives.append(rel_arc)
                    elif low.endswith((".tar.gz", ".tgz")) and _archive_contains_lean_tar(arc_bytes):
                        stem = arc_path.name[:-7] if low.endswith(".tar.gz") else arc_path.stem
                        dest = extracted_root / stem
                        if dest.exists():
                            continue
                        with tarfile.open(fileobj=io.BytesIO(arc_bytes), mode="r:*") as tf:
                            _safe_extract_tar(tf, dest)
                        extracted_archives.append(rel_arc)
                if extracted_archives:
                    profile["extracted_archives"] = extracted_archives
            _scan_local_dir(target_dir, profile)

    return profile


def _normalize_gitlab_repo_path(raw_path: str) -> str:
    # Strip GitLab UI path segments like /-/tree/main/... or /-/blob/...
    path = raw_path.split("/-/")[0].strip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) > 3:
        parts = parts[:3]
    return "/".join(parts).removesuffix(".git")


def profile_gitlab_repo(host: str, raw_path: str, clone_root: Path) -> dict[str, Any]:
    repo_path = _normalize_gitlab_repo_path(raw_path)
    full_name = f"{host}/{repo_path}"
    slug = f"gitlab__{host}__{repo_path.replace('/', '__')}"
    target_dir = clone_root / slug
    profile: dict[str, Any] = {
        "host": "gitlab",
        "repo": full_name,
        "accessible": False,
    }
    clone_url = f"https://{host}/{repo_path}.git"
    if not target_dir.exists():
        clone_root.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        try:
            proc = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=45,
                env=env,
            )
            if proc.returncode != 0:
                profile["clone_error"] = (proc.stderr or proc.stdout).strip()[:300]
                return profile
        except subprocess.TimeoutExpired:
            profile["clone_skipped"] = "timeout_45s"
            return profile

    if target_dir.exists():
        profile["accessible"] = True
        _scan_local_dir(target_dir, profile)
    return profile


def _safe_extract_zip(zf: zipfile.ZipFile, dest: Path) -> None:
    dest_resolved = dest.resolve()
    for info in zf.infolist():
        target = (dest / info.filename).resolve()
        if not str(target).startswith(str(dest_resolved)):
            continue
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                dst.write(src.read())


def _safe_extract_tar(tf: tarfile.TarFile, dest: Path) -> None:
    dest_resolved = dest.resolve()
    for member in tf.getmembers():
        if not (member.isfile() or member.isdir()):
            continue
        target = (dest / member.name).resolve()
        if not str(target).startswith(str(dest_resolved)):
            continue
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            src = tf.extractfile(member)
            if src is not None:
                with open(target, "wb") as dst:
                    dst.write(src.read())


def profile_zenodo_record(client: httpx.Client, record_id: str, clone_root: Path) -> dict[str, Any]:
    full_name = f"zenodo/{record_id}"
    target_dir = clone_root / f"zenodo__{record_id}"
    profile: dict[str, Any] = {
        "host": "zenodo",
        "repo": full_name,
        "accessible": False,
    }
    api_url = f"https://zenodo.org/api/records/{record_id}"
    try:
        r = client.get(api_url, follow_redirects=True, timeout=30.0)
        if r.status_code != 200:
            profile["error"] = f"api_status={r.status_code}"
            return profile
        meta = r.json()
    except Exception as exc:
        profile["error"] = str(exc)[:200]
        return profile

    profile["accessible"] = True
    profile["created_at"] = meta.get("created")
    profile["pushed_at"] = meta.get("updated")
    profile["description"] = (meta.get("metadata") or {}).get("title")
    files = meta.get("files") or []
    total_bytes = sum(int(f.get("size", 0) or 0) for f in files)
    profile["size_kb"] = total_bytes // 1024
    profile["zenodo_files"] = [f.get("key") for f in files]

    if total_bytes / (1024 * 1024) > MAX_ZENODO_MB:
        profile["clone_skipped"] = f"size_mb={total_bytes/(1024*1024):.1f}>{MAX_ZENODO_MB}"
        return profile

    if not target_dir.exists() or not any(target_dir.iterdir()):
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            key = f.get("key") or "file"
            dl_url = (f.get("links") or {}).get("self")
            if not dl_url:
                continue
            try:
                dl = client.get(dl_url, follow_redirects=True, timeout=180.0)
                if dl.status_code != 200:
                    continue
                content = dl.content
                lower_key = key.lower()
                if lower_key.endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(content)) as zf:
                        _safe_extract_zip(zf, target_dir / Path(key).stem)
                elif lower_key.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
                    with tarfile.open(fileobj=io.BytesIO(content), mode="r:*") as tf:
                        _safe_extract_tar(tf, target_dir / Path(key).stem)
                else:
                    out_file = target_dir / Path(key).name
                    out_file.write_bytes(content)
            except Exception as exc:
                profile.setdefault("extract_warnings", []).append(f"{key}:{str(exc)[:120]}")

    _scan_local_dir(target_dir, profile)
    return profile


def run_profile(
    db_path: Path = DEFAULT_DB_PATH,
    clone_root: Path = Path("data/repos"),
    include_contextual: bool = True,
    reprofile_ids: list[str] | None = None,
) -> None:
    conn = connect(db_path)
    if reprofile_ids:
        placeholders = ",".join("?" for _ in reprofile_ids)
        rows = conn.execute(
            f"""
            SELECT p.arxiv_id, p.version, p.title, p.comment, p.doi,
                   s.has_lean_strong, s.has_lean_contextual, s.urls_json
            FROM papers p
            JOIN screen_results s ON p.arxiv_id = s.arxiv_id
            WHERE p.arxiv_id IN ({placeholders})
            ORDER BY p.submitted_date DESC
            """,
            reprofile_ids,
        ).fetchall()
    else:
        where = "(s.has_lean_strong = 1 OR s.has_lean_contextual = 1)" if include_contextual else "s.has_lean_strong = 1"
        rows = conn.execute(
            f"""
            SELECT p.arxiv_id, p.version, p.title, p.comment, p.doi,
                   s.has_lean_strong, s.has_lean_contextual, s.urls_json
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
            urls_set = set(json.loads(row["urls_json"] or "[]"))
            if row["comment"]:
                urls_set.update(u.rstrip(".,;:)]}\"'") for u in REPO_URL_RE.findall(row["comment"]))
            if row["doi"]:
                urls_set.update(u.rstrip(".,;:)]}\"'") for u in REPO_URL_RE.findall(row["doi"]))

            latex_ok, latex_signals, tex_urls, anc_profile = fetch_and_scan_latex(
                client, arxiv_id, version, clone_root=clone_root
            )
            urls_set.update(tex_urls)
            urls = sorted(urls_set)
            print(
                f"[{i}/{len(rows)}] {arxiv_id} (strong={row['has_lean_strong']}, ctx={row['has_lean_contextual']}) urls={len(urls)}",
                flush=True,
            )
            time.sleep(1.0)

            seen_gh: set[tuple[str, str]] = set()
            seen_gl: set[tuple[str, str]] = set()
            seen_zen: set[str] = set()
            repo_profiles: list[dict[str, Any]] = []
            if anc_profile is not None:
                repo_profiles.append(anc_profile)
                print(
                    f"    -> ARXIV ANCILLARY LEAN {anc_profile['repo']}: {anc_profile['lean_file_count']} .lean files, "
                    f"LoC={anc_profile.get('lean_static_counts', {}).get('loc_nonempty', 0)}, "
                    f"sorry={anc_profile.get('lean_static_counts', {}).get('sorry', 0)}, "
                    f"axiom={anc_profile.get('lean_static_counts', {}).get('custom_axiom', 0)}",
                    flush=True,
                )

            for u in urls:
                m_gh = GITHUB_REPO_RE.match(u)
                if m_gh:
                    owner, repo = m_gh.group(1), m_gh.group(2).removesuffix(".git")
                    key = (owner.lower(), repo.lower())
                    if key in SKIP_REPOS or key in seen_gh:
                        continue
                    seen_gh.add(key)
                    prof = profile_github_repo(owner, repo, clone_root)
                    repo_profiles.append(prof)
                    if prof.get("lean_file_count", 0) > 0:
                        print(
                            f"    -> GITHUB LEAN REPO {prof['repo']}: {prof['lean_file_count']} .lean files, "
                            f"LoC={prof.get('lean_static_counts', {}).get('loc_nonempty', 0)}, "
                            f"sorry={prof.get('lean_static_counts', {}).get('sorry', 0)}, "
                            f"axiom={prof.get('lean_static_counts', {}).get('custom_axiom', 0)}",
                            flush=True,
                        )
                    continue

                m_gl = GITLAB_REPO_RE.match(u)
                if m_gl:
                    host = m_gl.group(1).lower()
                    repo_path = _normalize_gitlab_repo_path(m_gl.group(2))
                    key = (host, repo_path.lower())
                    if key in seen_gl or "/" not in repo_path:
                        continue
                    seen_gl.add(key)
                    prof = profile_gitlab_repo(host, repo_path, clone_root)
                    repo_profiles.append(prof)
                    if prof.get("lean_file_count", 0) > 0:
                        print(
                            f"    -> GITLAB LEAN REPO {prof['repo']}: {prof['lean_file_count']} .lean files, "
                            f"LoC={prof.get('lean_static_counts', {}).get('loc_nonempty', 0)}, "
                            f"sorry={prof.get('lean_static_counts', {}).get('sorry', 0)}, "
                            f"axiom={prof.get('lean_static_counts', {}).get('custom_axiom', 0)}",
                            flush=True,
                        )
                    continue

                m_zen = ZENODO_ID_RE.search(u)
                if m_zen:
                    rec_id = m_zen.group(1)
                    if rec_id in seen_zen:
                        continue
                    seen_zen.add(rec_id)
                    prof = profile_zenodo_record(client, rec_id, clone_root)
                    repo_profiles.append(prof)
                    if prof.get("lean_file_count", 0) > 0:
                        print(
                            f"    -> ZENODO LEAN ARTIFACT {prof['repo']}: {prof['lean_file_count']} .lean files, "
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
    ap = argparse.ArgumentParser(description="Static LaTeX + GitHub/GitLab/Zenodo profiler for Lean candidate papers.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--clone-root", type=Path, default=Path("data/repos"))
    ap.add_argument("--strong-only", action="store_true")
    ap.add_argument("--reprofile-ids", nargs="+", default=None, help="Re-profile specific arXiv IDs")
    args = ap.parse_args()
    run_profile(
        db_path=args.db,
        clone_root=args.clone_root,
        include_contextual=not args.strong_only,
        reprofile_ids=args.reprofile_ids,
    )


if __name__ == "__main__":
    main()
