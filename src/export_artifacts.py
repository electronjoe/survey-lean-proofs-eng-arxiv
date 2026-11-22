"""Export canonical, deduplicated, license-safe JSON artifacts from slice SQLite DBs.

Reads `artifacts/slices/manifest.json` (with `--all` or `--slice <id>`) or explicit
`--db` / `--out-dir` arguments, and writes:
  - `classifications.json`: deduplicated Stage-4 LLM classifications (lean_candidate & beyond_lean)
  - `layer_a_audits.json`: deduplicated Stage-5 Layer-A semantic fidelity audits (when present)
  - `figure_inputs.json`: compact aggregate/per-paper records enabling zero-DB figure generation

Never exports copyrighted full-text bodies, paper abstracts, or third-party `.lean` code.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.db import connect

DEFAULT_MANIFEST = Path("artifacts/slices/manifest.json")

TARGET_CATEGORIES = [
    "math.OC",
    "cs.DC",
    "cs.IT",
    "cs.CR",
    "eess.SY",
    "eess.SP",
    "cs.NI",
    "cs.RO",
]


def build_figure_inputs(db_path: Path, slice_id: str) -> dict[str, Any]:
    """Extract the compact, license-safe data required by `src/generate_figures.py`."""
    conn = connect(db_path)

    date_min, date_max = conn.execute(
        "SELECT MIN(submitted_date), MAX(submitted_date) FROM papers"
    ).fetchone()
    total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    screened = conn.execute(
        "SELECT COUNT(*) FROM screen_results WHERE fetch_source != 'failed'"
    ).fetchone()[0]
    candidates = conn.execute(
        "SELECT COUNT(*) FROM screen_results WHERE has_lean_strong = 1 OR has_lean_contextual = 1"
    ).fetchone()[0]
    negatives = screened - candidates
    confirmed = conn.execute(
        "SELECT COUNT(*) FROM classifications WHERE track='lean_candidate' AND lean_usage_status='lean_contributed'"
    ).fetchone()[0]
    eng_math = sum(
        1
        for r in conn.execute(
            "SELECT raw_json FROM classifications WHERE track='lean_candidate' AND lean_usage_status='lean_contributed'"
        )
        if json.loads(r[0]).get("paper_domain_role") == "engineering_math_proof"
    )
    audited = conn.execute("SELECT COUNT(*) FROM layer_a_audits").fetchone()[0]

    # Category bifurcation aggregates
    cat_total: Counter[str] = Counter()
    cat_role: dict[str, Counter[str]] = {c: Counter() for c in TARGET_CATEGORIES}
    for r in conn.execute(
        """
        SELECT p.matched_target_cats_json, c.lean_usage_status, c.raw_json
        FROM papers p
        LEFT JOIN classifications c ON p.arxiv_id = c.arxiv_id AND c.track = 'lean_candidate'
        """
    ):
        cats = json.loads(r[0])
        is_lean = r[1] == "lean_contributed"
        role = json.loads(r[2]).get("paper_domain_role") if is_lean and r[2] else None
        for c in cats:
            if c in cat_role:
                cat_total[c] += 1
                if role:
                    cat_role[c][role] += 1

    # Confirmed Lean papers (paradigm, tier, role, and compact lean-repo LoC list)
    confirmed_papers: list[dict[str, Any]] = []
    for r in conn.execute(
        """
        SELECT p.arxiv_id, p.primary_category, c.authoring_paradigm, c.verification_tier,
               c.raw_json, a.repos_json
        FROM papers p
        JOIN classifications c ON p.arxiv_id = c.arxiv_id
        LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
        WHERE c.track='lean_candidate' AND c.lean_usage_status='lean_contributed'
        ORDER BY p.arxiv_id ASC
        """
    ).fetchall():
        cls = json.loads(r["raw_json"])
        raw_repos = json.loads(r["repos_json"]) if r["repos_json"] else []
        lean_repos = [
            {
                "repo": rp["repo"],
                "host": rp.get("host", "github"),
                "lean_file_count": rp.get("lean_file_count", 0),
                "loc_nonempty": rp.get("lean_static_counts", {}).get("loc_nonempty", 0),
            }
            for rp in raw_repos
            if rp.get("lean_file_count", 0) > 0
        ]
        confirmed_papers.append(
            {
                "arxiv_id": r["arxiv_id"],
                "primary_category": r["primary_category"],
                "authoring_paradigm": r["authoring_paradigm"],
                "verification_tier": r["verification_tier"],
                "paper_domain_role": cls.get("paper_domain_role"),
                "lean_repos": lean_repos,
            }
        )

    # Layer-A audit rows for heatmap
    audit_rows: list[dict[str, Any]] = []
    for r in conn.execute(
        """
        SELECT l.arxiv_id, l.raw_json, p.primary_category, c.authoring_paradigm
        FROM layer_a_audits l
        JOIN papers p ON l.arxiv_id = p.arxiv_id
        LEFT JOIN classifications c ON l.arxiv_id = c.arxiv_id
        ORDER BY l.arxiv_id ASC
        """
    ).fetchall():
        a = json.loads(r["raw_json"])
        audit_rows.append(
            {
                "arxiv_id": r["arxiv_id"],
                "primary_category": r["primary_category"],
                "authoring_paradigm": r["authoring_paradigm"],
                "overall_fidelity": a["overall_fidelity"],
                "mode1_statement_drift": {"severity": a["mode1_statement_drift"]["severity"]},
                "mode2_scope_downgrade": {"severity": a["mode2_scope_downgrade"]["severity"]},
                "mode3_definition_smuggling": {"severity": a["mode3_definition_smuggling"]["severity"]},
                "mode4_junk_or_vacuity": {"severity": a["mode4_junk_or_vacuity"]["severity"]},
                "has_non_vacuity_witnesses": bool(a.get("has_non_vacuity_witnesses")),
                "mathlib_anchoring_quality": a["mathlib_anchoring_quality"],
            }
        )

    conn.close()
    return {
        "schema_version": "1.0",
        "slice_id": slice_id,
        "window": {
            "date_min": date_min[:10] if date_min else "",
            "date_max": date_max[:10] if date_max else "",
        },
        "funnel": {
            "total_papers": total,
            "screened": screened,
            "candidates": candidates,
            "negatives": negatives,
            "confirmed": confirmed,
            "eng_math": eng_math,
            "audited": audited,
        },
        "category_bifurcation": {
            "cat_total": {c: cat_total[c] for c in TARGET_CATEGORIES},
            "cat_role": {c: dict(sorted(cat_role[c].items())) for c in TARGET_CATEGORIES},
        },
        "confirmed_lean_papers": confirmed_papers,
        "layer_a_audits": audit_rows,
    }


def export_slice(
    db_path: Path,
    out_dir: Path,
    slice_id: str,
    export_figure_inputs: bool = True,
) -> dict[str, Path]:
    """Export canonical deduplicated JSON artifacts for a single slice DB."""
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB not found: {db_path}")

    conn = connect(db_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    # 1. Deduplicated classifications (lean_candidate and beyond_lean)
    cls_rows = conn.execute(
        """
        SELECT c.arxiv_id, c.track, c.model_tier, c.raw_json,
               p.primary_category, p.matched_target_cats_json,
               p.submitted_date, p.updated_date, p.version
        FROM classifications c
        JOIN papers p ON c.arxiv_id = p.arxiv_id
        ORDER BY c.track ASC, c.arxiv_id ASC
        """
    ).fetchall()

    lean_results: list[dict[str, Any]] = []
    beyond_results: list[dict[str, Any]] = []
    lean_models: set[str] = set()
    beyond_models: set[str] = set()

    for r in cls_rows:
        raw = json.loads(r["raw_json"])
        entry = {
            "arxiv_id": r["arxiv_id"],
            "primary_category": r["primary_category"],
            "matched_target_cats": json.loads(r["matched_target_cats_json"]),
            "submitted_date": r["submitted_date"][:10],
            "updated_date": r["updated_date"][:10],
            "version": r["version"],
            "model_tier": r["model_tier"],
            **raw,
        }
        if r["track"] == "lean_candidate":
            lean_results.append(entry)
            lean_models.add(r["model_tier"])
        else:
            beyond_results.append(entry)
            beyond_models.add(r["model_tier"])

    cls_payload = {
        "schema_version": "1.0",
        "slice_id": slice_id,
        "lean_models": sorted(lean_models),
        "beyond_lean_models": sorted(beyond_models),
        "lean_candidate_count": len(lean_results),
        "beyond_lean_count": len(beyond_results),
        "lean_results": lean_results,
        "beyond_lean_results": beyond_results,
    }
    cls_path = out_dir / "classifications.json"
    cls_path.write_text(json.dumps(cls_payload, indent=2) + "\n")
    written["classifications"] = cls_path

    # 2. Deduplicated Layer-A audits (only written when audits exist for this slice)
    audit_rows = conn.execute(
        """
        SELECT l.arxiv_id, l.model_tier, l.raw_json,
               p.primary_category, p.matched_target_cats_json,
               c.authoring_paradigm, c.verification_tier
        FROM layer_a_audits l
        JOIN papers p ON l.arxiv_id = p.arxiv_id
        LEFT JOIN classifications c ON l.arxiv_id = c.arxiv_id
        ORDER BY l.arxiv_id ASC
        """
    ).fetchall()
    conn.close()

    if audit_rows:
        audit_models = sorted({r["model_tier"] for r in audit_rows})
        audits_list = []
        for r in audit_rows:
            raw = json.loads(r["raw_json"])
            audits_list.append(
                {
                    "arxiv_id": r["arxiv_id"],
                    "primary_category": r["primary_category"],
                    "matched_target_cats": json.loads(r["matched_target_cats_json"]),
                    "authoring_paradigm": r["authoring_paradigm"],
                    "verification_tier": r["verification_tier"],
                    "model_tier": r["model_tier"],
                    **raw,
                }
            )
        audit_payload = {
            "schema_version": "1.0",
            "slice_id": slice_id,
            "audit_models": audit_models,
            "audit_count": len(audits_list),
            "audits": audits_list,
        }
        audit_path = out_dir / "layer_a_audits.json"
        audit_path.write_text(json.dumps(audit_payload, indent=2) + "\n")
        written["layer_a_audits"] = audit_path

    # 3. Compact figure_inputs.json for zero-DB figure generation
    if export_figure_inputs:
        fig_payload = build_figure_inputs(db_path, slice_id)
        fig_path = out_dir / "figure_inputs.json"
        fig_path.write_text(json.dumps(fig_payload, indent=2) + "\n")
        written["figure_inputs"] = fig_path

    print(
        f"[{slice_id}] Exported {len(lean_results)} lean + {len(beyond_results)} beyond-lean classifications, "
        f"{len(audit_rows)} Layer-A audits"
        + (", + figure_inputs.json" if export_figure_inputs else "")
        + f" -> {out_dir}"
    )
    return written


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export canonical license-safe JSON artifacts from slice SQLite databases."
    )
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--all", action="store_true", help="Export all slices registered in manifest.json.")
    ap.add_argument("--slice", dest="slice_id", help="Export a single slice_id from manifest.json.")
    ap.add_argument("--db", type=Path, help="Explicit SQLite DB path (overrides manifest).")
    ap.add_argument("--out-dir", type=Path, help="Explicit output directory (requires --db).")
    ap.add_argument(
        "--with-figure-inputs",
        action="store_true",
        help="Also export figure_inputs.json when using --db/--out-dir.",
    )
    args = ap.parse_args()

    if args.db is not None:
        if args.out_dir is None:
            ap.error("--out-dir is required when --db is specified.")
        export_slice(
            db_path=args.db,
            out_dir=args.out_dir,
            slice_id=args.slice_id or args.out_dir.name,
            export_figure_inputs=args.with_figure_inputs,
        )
        return

    manifest = json.loads(args.manifest.read_text())
    slices = manifest["slices"]
    if args.slice_id:
        slices = [s for s in slices if s["slice_id"] == args.slice_id]
        if not slices:
            ap.error(f"Unknown slice_id {args.slice_id!r} in {args.manifest}")
    elif not args.all:
        ap.error("Specify --all, --slice <slice_id>, or --db <path> --out-dir <dir>.")

    for s in slices:
        export_slice(
            db_path=Path(s["db_path"]),
            out_dir=Path(s["artifacts_dir"]),
            slice_id=s["slice_id"],
            export_figure_inputs=bool(s.get("export_figure_inputs", False)),
        )


if __name__ == "__main__":
    main()
