"""Stage-2 Recall Calibration: audit a stratified sample of Stage-2 negatives via lightweight GitHub API tree queries.

Checks whether papers that passed Stage-2 full-text screening as Lean negatives nevertheless link to a
GitHub repository containing `lean-toolchain`, `lakefile.lean`/`lakefile.toml`, or `*.lean` files.
Also inspects a random sample of Stage-2 negatives without GitHub links for subtle metadata/URL Lean clues.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from src.db import DEFAULT_DB_PATH, connect

GITHUB_REPO_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.IGNORECASE)
BOILERPLATE_REPOS = {
    ("arxiv", "html_feedback"),
    ("brucemiller", "latexml"),
}
BROAD_LEAN_META_RE = re.compile(r"\b(?:lean|mathlib|lakefile|formaliz\w*|theorem\s+prover|proof\s+assistant)\b", re.IGNORECASE)


def _gh_api_json(endpoint: str) -> Any | None:
    try:
        proc = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _check_repo_for_lean(owner: str, repo: str) -> dict[str, Any]:
    repo = repo.removesuffix(".git")
    full = f"{owner}/{repo}"
    meta = _gh_api_json(f"repos/{full}")
    if not meta or "full_name" not in meta:
        return {"repo": full, "accessible": False, "has_lean": False}
    branch = meta.get("default_branch", "main")
    tree = _gh_api_json(f"repos/{full}/git/trees/{branch}?recursive=1")
    paths = [item["path"] for item in (tree or {}).get("tree", []) if item.get("type") == "blob"]
    lean_files = [p for p in paths if p.endswith(".lean")]
    has_tc = any(Path(p).name == "lean-toolchain" for p in paths)
    has_lake = any(Path(p).name in ("lakefile.lean", "lakefile.toml") for p in paths)
    return {
        "repo": full,
        "accessible": True,
        "default_branch": branch,
        "total_files": len(paths),
        "lean_file_count": len(lean_files),
        "sample_lean_files": lean_files[:5],
        "has_lean_toolchain": has_tc,
        "has_lakefile": has_lake,
        "has_lean": bool(lean_files or has_tc or has_lake),
    }


def _clopper_pearson_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided (1 - alpha) Clopper-Pearson upper bound on binomial proportion p."""
    if n <= 0:
        return 1.0
    if k >= n:
        return 1.0
    if k == 0:
        return 1.0 - (alpha ** (1.0 / n))
    # Binary search for p such that P(Bin(n, p) <= k) = alpha
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        # CDF P(X <= k)
        cdf = 0.0
        for i in range(k + 1):
            cdf += math.comb(n, i) * (mid**i) * ((1.0 - mid) ** (n - i))
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def calibrate(
    db_path: Path = DEFAULT_DB_PATH,
    gh_sample_size: int = 100,
    non_gh_sample_size: int = 50,
    seed: int = 20261122,
    workers: int = 8,
    out_json: Path = Path("data/recall_calibration.json"),
    out_md: Path = Path("reports/recall_calibration.md"),
) -> None:
    conn = connect(db_path)
    neg_rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT p.arxiv_id, p.title, p.primary_category, p.matched_target_cats_json,
                   p.abstract, p.comment, s.fetch_source, s.urls_json
            FROM papers p
            JOIN screen_results s ON p.arxiv_id = s.arxiv_id
            WHERE s.has_lean_strong = 0
              AND s.has_lean_contextual = 0
              AND s.fetch_source != 'failed'
            ORDER BY p.arxiv_id ASC
            """
        ).fetchall()
    ]
    conn.close()

    gh_negatives: list[tuple[dict[str, Any], list[tuple[str, str]]]] = []
    non_gh_negatives: list[dict[str, Any]] = []

    for r in neg_rows:
        urls = json.loads(r["urls_json"] or "[]")
        repos: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for u in urls:
            m = GITHUB_REPO_RE.match(u)
            if not m:
                continue
            owner, repo = m.group(1), m.group(2).removesuffix(".git")
            key = (owner.lower(), repo.lower())
            if key in BOILERPLATE_REPOS or key in seen:
                continue
            seen.add(key)
            repos.append((owner, repo))
        if repos:
            gh_negatives.append((r, repos))
        else:
            non_gh_negatives.append(r)

    rng = random.Random(seed)
    gh_sample = rng.sample(gh_negatives, min(gh_sample_size, len(gh_negatives)))
    non_gh_sample = rng.sample(non_gh_negatives, min(non_gh_sample_size, len(non_gh_negatives)))

    print(
        f"Stage-2 negatives: total={len(neg_rows)}, with_github={len(gh_negatives)}, without_github={len(non_gh_negatives)}.\n"
        f"Auditing {len(gh_sample)} GitHub-linked negatives + {len(non_gh_sample)} non-GitHub negatives...",
        flush=True,
    )

    # Deduplicate unique GitHub repos across sample
    unique_repos: dict[tuple[str, str], tuple[str, str]] = {}
    for _, repos in gh_sample:
        for owner, repo in repos[:4]:  # cap at 4 repos per paper to avoid survey lists
            unique_repos[(owner.lower(), repo.lower())] = (owner, repo)

    repo_results: dict[tuple[str, str], dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_check_repo_for_lean, o, r): k for k, (o, r) in unique_repos.items()}
        done = 0
        for fut in as_completed(futs):
            k = futs[fut]
            repo_results[k] = fut.result()
            done += 1
            if done % 25 == 0 or done == len(futs):
                print(f"  Checked {done}/{len(futs)} unique GitHub repos...", flush=True)

    gh_audited: list[dict[str, Any]] = []
    gh_lean_hits: list[dict[str, Any]] = []
    accessible_paper_count = 0

    for row, repos in gh_sample:
        checked = [repo_results[(o.lower(), r.lower())] for o, r in repos[:4]]
        any_acc = any(c["accessible"] for c in checked)
        if any_acc:
            accessible_paper_count += 1
        any_lean = any(c["has_lean"] for c in checked)
        rec = {
            "arxiv_id": row["arxiv_id"],
            "title": row["title"],
            "primary_category": row["primary_category"],
            "matched_target_cats": json.loads(row["matched_target_cats_json"]),
            "repos_checked": checked,
            "any_accessible": any_acc,
            "has_lean_repo": any_lean,
        }
        gh_audited.append(rec)
        if any_lean:
            gh_lean_hits.append(rec)

    non_gh_flagged: list[dict[str, Any]] = []
    for row in non_gh_sample:
        blob = f"{row['title']}\n{row['abstract']}\n{row['comment'] or ''}"
        matches = sorted(set(BROAD_LEAN_META_RE.findall(blob)))
        if matches:
            non_gh_flagged.append(
                {
                    "arxiv_id": row["arxiv_id"],
                    "title": row["title"],
                    "primary_category": row["primary_category"],
                    "broad_matches": matches,
                    "comment": row["comment"],
                }
            )

    n_gh = len(gh_sample)
    k_gh = len(gh_lean_hits)
    fn_rate_gh = k_gh / max(n_gh, 1)
    fn_upper_95_gh = _clopper_pearson_upper(k_gh, n_gh, alpha=0.05)

    n_acc = accessible_paper_count
    fn_upper_95_acc = _clopper_pearson_upper(k_gh, n_acc, alpha=0.05)

    payload = {
        "seed": seed,
        "total_stage2_negatives": len(neg_rows),
        "total_github_linked_negatives": len(gh_negatives),
        "total_non_github_negatives": len(non_gh_negatives),
        "gh_sample_size": n_gh,
        "gh_accessible_papers": n_acc,
        "gh_unique_repos_checked": len(unique_repos),
        "gh_lean_hits_count": k_gh,
        "gh_fn_rate": fn_rate_gh,
        "gh_fn_95pct_upper_bound": fn_upper_95_gh,
        "gh_acc_fn_95pct_upper_bound": fn_upper_95_acc,
        "gh_lean_hits": gh_lean_hits,
        "non_gh_sample_size": len(non_gh_sample),
        "non_gh_broad_meta_flags": non_gh_flagged,
        "gh_audited_sample": gh_audited,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2))

    lines = [
        "# Stage-2 Recall Calibration Report",
        "",
        f"- **Random seed:** `{seed}`",
        f"- **Total Stage-2 negatives (full-text screened):** {len(neg_rows)}",
        f"- **Stage-2 negatives with non-boilerplate GitHub links:** {len(gh_negatives)} ({100.0*len(gh_negatives)/max(len(neg_rows),1):.1f}%)",
        f"- **GitHub-linked negative sample audited:** **{n_gh}** papers ({len(unique_repos)} unique GitHub repos queried via `gh api` recursive trees; **{n_acc}** papers had ≥1 accessible public repo)",
        f"- **Missed Lean repositories found in GitHub-linked negative sample:** **{k_gh} / {n_gh}** ({100.0*fn_rate_gh:.2f}%)",
        f"- **95% Clopper–Pearson upper bound on hidden-Lean rate among GitHub-linked negatives:** **{100.0*fn_upper_95_gh:.2f}%** (or **{100.0*fn_upper_95_acc:.2f}%** conditioning on accessible repos)",
        f"- **Non-GitHub negative sample checked for broad metadata/comment keywords:** **{len(non_gh_sample)}** papers ({len(non_gh_flagged)} broad keyword matches for manual review)",
        "",
    ]
    if gh_lean_hits:
        lines += ["## Missed Lean Repos Discovered in GitHub-Linked Negatives", ""]
        for h in gh_lean_hits:
            lean_rs = [r for r in h["repos_checked"] if r["has_lean"]]
            lines.append(
                f"- **[{h['arxiv_id']}](https://arxiv.org/abs/{h['arxiv_id']})** (`{h['primary_category']}`) "
                f"{h['title']} — repos: `{[(r['repo'], r['lean_file_count'], r['sample_lean_files']) for r in lean_rs]}`"
            )
        lines.append("")
    else:
        lines += [
            "## Result",
            "",
            "Zero missed Lean repositories (`*.lean`, `lean-toolchain`, or `lakefile.*`) were detected across the entire audited GitHub-linked Stage-2 negative sample.",
            "",
        ]

    if non_gh_flagged:
        lines += ["## Non-GitHub Negative Sample — Broad Metadata Keyword Spot-Check", ""]
        for f in non_gh_flagged:
            lines.append(
                f"- **[{f['arxiv_id']}](https://arxiv.org/abs/{f['arxiv_id']})** (`{f['primary_category']}`) "
                f"{f['title']} — matched: `{f['broad_matches']}`"
            )
        lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines))
    print(f"Wrote {out_md} and {out_json} (gh_lean_hits={k_gh}/{n_gh}, 95% upper bound={100*fn_upper_95_gh:.2f}%).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Calibrate Stage-2 recall on random Stage-2 negatives.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--gh-sample", type=int, default=100)
    ap.add_argument("--non-gh-sample", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261122)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    calibrate(
        db_path=args.db,
        gh_sample_size=args.gh_sample,
        non_gh_sample_size=args.non_gh_sample,
        seed=args.seed,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
