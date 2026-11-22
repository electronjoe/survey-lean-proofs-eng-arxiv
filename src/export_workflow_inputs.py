"""Export compact candidate bundles from SQLite for run_workflow classification."""

from __future__ import annotations

import json
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect

BOILERPLATE_SUBSTRINGS = ("arXiv/html_feedback", "brucemiller/LaTeXML")


def _clean_urls(urls: list[str]) -> list[str]:
    return [u for u in urls if not any(b in u for b in BOILERPLATE_SUBSTRINGS)]


def export_inputs(
    db_path: Path = DEFAULT_DB_PATH,
    out_path: Path = Path("data/workflow_inputs.json"),
    clone_root: Path = Path("data/repos"),
) -> None:
    conn = connect(db_path)
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

    for r in rows:
        repos = json.loads(r["repos_json"]) if r["repos_json"] else []
        local_repo_dirs = []
        for rp in repos:
            if rp.get("lean_file_count", 0) > 0 and not rp.get("clone_skipped"):
                slug = rp["repo"].replace("/", "__")
                d = (clone_root / slug).resolve()
                if d.exists():
                    local_repo_dirs.append(str(d))

        item = {
            "arxiv_id": r["arxiv_id"],
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
        else:
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


if __name__ == "__main__":
    export_inputs()
