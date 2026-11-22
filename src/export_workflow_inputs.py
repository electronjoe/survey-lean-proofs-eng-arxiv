"""Export compact candidate bundles from SQLite for run_workflow classification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect

BOILERPLATE_SUBSTRINGS = ("arXiv/html_feedback", "brucemiller/LaTeXML")
PURE_TCS_PRIMARY_CATS = {"cs.CC", "cs.DS", "cs.LO", "cs.DM", "cs.FL", "cs.CG"}


def _clean_urls(urls: list[str]) -> list[str]:
    return [u for u in urls if not any(b in u for b in BOILERPLATE_SUBSTRINGS)]


def _resolve_local_dirs(repos: list[dict], clone_root: Path) -> list[str]:
    dirs: list[str] = []
    for rp in repos:
        if rp.get("lean_file_count", 0) > 0 and not rp.get("clone_skipped"):
            if rp.get("local_dir") and Path(rp["local_dir"]).exists():
                dirs.append(str(Path(rp["local_dir"]).resolve()))
            else:
                slug = rp["repo"].replace("/", "__")
                d = (clone_root / slug).resolve()
                if d.exists():
                    dirs.append(str(d))
    return dirs


def export_inputs(
    db_path: Path = DEFAULT_DB_PATH,
    out_path: Path = Path("data/workflow_inputs.json"),
    clone_root: Path = Path("data/repos"),
    unclassified_only: bool = False,
    lean_only: bool = False,
    exclude_tcs_primary: bool = False,
    only_ids: list[str] | None = None,
) -> None:
    conn = connect(db_path)

    classified_ids = {
        r["arxiv_id"] for r in conn.execute("SELECT arxiv_id FROM classifications").fetchall()
    }

    rows = conn.execute(
        """
        SELECT p.*, s.fetch_source, s.text_chars,
               s.has_lean_strong, s.has_lean_contextual,
               s.has_other_itp, s.has_model_checker, s.has_protocol_verifier, s.has_smt_sat,
               s.lean_hits_json, s.other_hits_json, s.urls_json,
               a.latex_signals_json, a.repos_json
        FROM papers p
        JOIN screen_results s ON p.arxiv_id = s.arxiv_id
        LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
        WHERE s.has_lean_strong = 1
           OR s.has_lean_contextual = 1
           OR s.has_other_itp = 1
           OR s.has_model_checker = 1
           OR s.has_protocol_verifier = 1
           OR s.has_smt_sat = 1
        ORDER BY s.has_lean_strong DESC, s.has_lean_contextual DESC, p.submitted_date DESC
        """
    ).fetchall()

    lean_candidates = []
    beyond_lean_candidates = []
    only_id_set = set(only_ids) if only_ids else None

    for r in rows:
        aid = r["arxiv_id"]
        if only_id_set is not None and aid not in only_id_set:
            continue
        if unclassified_only and aid in classified_ids and (only_id_set is None):
            continue
        if exclude_tcs_primary and r["primary_category"] in PURE_TCS_PRIMARY_CATS and (only_id_set is None):
            continue

        repos = json.loads(r["repos_json"]) if r["repos_json"] else []
        local_repo_dirs = _resolve_local_dirs(repos, clone_root)

        item = {
            "arxiv_id": aid,
            "title": r["title"],
            "primary_category": r["primary_category"],
            "matched_target_cats": json.loads(r["matched_target_cats_json"]),
            "submitted_date": r["submitted_date"][:10],
            "comment": r["comment"],
            "journal_ref": r["journal_ref"],
            "abstract": r["abstract"],
            "urls": _clean_urls(json.loads(r["urls_json"] or "[]")),
            "lean_hits": json.loads(r["lean_hits_json"] or "{}"),
            "other_hits": json.loads(r["other_hits_json"] or "{}"),
            "latex_signals": json.loads(r["latex_signals_json"] or "{}") if r["latex_signals_json"] else {},
            "repos": repos,
            "local_repo_dirs": local_repo_dirs,
        }
        if r["has_lean_strong"] or r["has_lean_contextual"]:
            lean_candidates.append(item)
        elif not lean_only:
            beyond_lean_candidates.append(item)

    payload = {
        "lean_candidates": lean_candidates,
        "beyond_lean_candidates": beyond_lean_candidates,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    conn.close()
    print(
        f"Exported {len(lean_candidates)} lean_candidates and "
        f"{len(beyond_lean_candidates)} beyond_lean_candidates to {out_path}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Export candidate bundles for run_workflow classification.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--out", type=Path, default=Path("data/workflow_inputs.json"))
    ap.add_argument("--clone-root", type=Path, default=Path("data/repos"))
    ap.add_argument("--unclassified-only", action="store_true")
    ap.add_argument("--lean-only", action="store_true")
    ap.add_argument("--exclude-tcs-primary", action="store_true")
    ap.add_argument("--only-ids", nargs="+", default=None)
    args = ap.parse_args()
    export_inputs(
        db_path=args.db,
        out_path=args.out,
        clone_root=args.clone_root,
        unclassified_only=args.unclassified_only,
        lean_only=args.lean_only,
        exclude_tcs_primary=args.exclude_tcs_primary,
        only_ids=args.only_ids,
    )


if __name__ == "__main__":
    main()
