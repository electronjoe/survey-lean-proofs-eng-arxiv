"""Import Phase 2 Layer-A audit outputs into SQLite and generate reports/phase2_layer_a_audit.md from SQLite."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect, upsert_layer_a_audit


def import_and_report(
    db_path: Path = DEFAULT_DB_PATH,
    outputs_path: Path | None = Path("data/phase2_outputs.json"),
    report_path: Path = Path("reports/slices/2026-11/phase2_layer_a_audit.md"),
) -> None:
    conn = connect(db_path)

    if outputs_path is not None and outputs_path.exists():
        data = json.loads(outputs_path.read_text())
        model_tier = data.get("audit_model", "pro")
        with conn:
            for r in data.get("audits", []):
                upsert_layer_a_audit(conn, r["arxiv_id"], model_tier, r)

    rows = conn.execute(
        """
        SELECT l.raw_json, l.model_tier, p.title, p.primary_category, p.matched_target_cats_json,
               c.authoring_paradigm, c.verification_tier
        FROM layer_a_audits l
        JOIN papers p ON l.arxiv_id = p.arxiv_id
        LEFT JOIN classifications c ON l.arxiv_id = c.arxiv_id
        ORDER BY p.submitted_date DESC, p.arxiv_id DESC
        """
    ).fetchall()

    audits = [json.loads(r["raw_json"]) for r in rows]
    meta_by_id = {json.loads(r["raw_json"])["arxiv_id"]: dict(r) for r in rows}
    model_tiers = sorted({r["model_tier"] for r in rows})

    overall_counts = Counter(r["overall_fidelity"] for r in audits)
    m1_counts = Counter(r["mode1_statement_drift"]["severity"] for r in audits)
    m2_counts = Counter(r["mode2_scope_downgrade"]["severity"] for r in audits)
    m3_counts = Counter(r["mode3_definition_smuggling"]["severity"] for r in audits)
    m4_counts = Counter(r["mode4_junk_or_vacuity"]["severity"] for r in audits)
    non_vac = sum(1 for r in audits if r.get("has_non_vacuity_witnesses"))
    mathlib_counts = Counter(r.get("mathlib_anchoring_quality") for r in audits)

    lines = [
        "# Phase 2 Report: Layer-A Semantic Fidelity Audit (`engineering_math_proof` Papers)",
        "",
        f"- **Audited cohort:** {len(audits)} confirmed `engineering_math_proof` papers with locally inspected Lean 4 repos",
        f"- **Auditor model tier(s):** `{', '.join(model_tiers)}` (read-only adversarial LaTeX ↔ Lean comparison)",
        f"- **Overall Fidelity:** {dict(overall_counts)}",
        f"- **Mode #1 (Statement/Hypothesis Drift):** {dict(m1_counts)}",
        f"- **Mode #2 (Scope Downgrade):** {dict(m2_counts)}",
        f"- **Mode #3 (Definition Smuggling):** {dict(m3_counts)}",
        f"- **Mode #4 (Junk Values / Vacuity):** {dict(m4_counts)}",
        f"- **Explicit Non-Vacuity Witnesses Present:** {non_vac} / {len(audits)}",
        f"- **Mathlib Anchoring Quality:** {dict(mathlib_counts)}",
        "",
        "## Summary Matrix",
        "",
        "| arXiv ID | Cat | Par | Overall Fidelity | M1 Drift | M2 Scope | M3 Defs | M4 Junk/Vac | Non-Vac? | Mathlib |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |",
    ]

    for r in audits:
        p = meta_by_id.get(r["arxiv_id"], {})
        par = (p.get("authoring_paradigm") or "?").split("_")[0]
        lines.append(
            f"| [{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) | `{p.get('primary_category', '?')}` | `{par}` | "
            f"`{r['overall_fidelity']}` | `{r['mode1_statement_drift']['severity']}` | "
            f"`{r['mode2_scope_downgrade']['severity']}` | `{r['mode3_definition_smuggling']['severity']}` | "
            f"`{r['mode4_junk_or_vacuity']['severity']}` | {'Yes' if r.get('has_non_vacuity_witnesses') else 'No'} | "
            f"`{r.get('mathlib_anchoring_quality')}` |"
        )

    lines += ["", "## Detailed Per-Paper Audit Findings", ""]
    for r in audits:
        p = meta_by_id.get(r["arxiv_id"], {})
        lines.append(f"### [{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) — {p.get('title', '')}")
        lines.append(
            f"- **Repo audited:** `{r['primary_repo_audited']}` | **Overall:** `{r['overall_fidelity']}` | "
            f"**Non-vacuity witnesses:** `{r['has_non_vacuity_witnesses']}` | **Mathlib anchoring:** `{r['mathlib_anchoring_quality']}`"
        )
        lines.append(f"- **Executive Verdict:** {r['executive_verdict']}")
        if r.get("notable_good_practices"):
            lines.append(f"- **Good Practices:** {'; '.join(r['notable_good_practices'])}")
        lines.append("")
        lines.append("| Paper Claim | Lean Declaration | Location | Verdict | Delta Notes |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for tc in r.get("theorems_compared", []):
            pc = tc["paper_claim"].replace("|", "/")
            ld = tc["lean_declaration"].replace("|", "/")
            loc = tc["lean_file_and_line"].replace("|", "/")
            dn = tc["delta_notes"].replace("|", "/")
            lines.append(f"| {pc} | `{ld}` | `{loc}` | `{tc['alignment_verdict']}` | {dn} |")
        lines.append("")
        for label, key in [
            ("Mode #1 — Statement & Hypothesis Drift", "mode1_statement_drift"),
            ("Mode #2 — Scope Downgrade", "mode2_scope_downgrade"),
            ("Mode #3 — Definition Smuggling", "mode3_definition_smuggling"),
            ("Mode #4 — Junk Values & Vacuity", "mode4_junk_or_vacuity"),
        ]:
            m = r[key]
            lines.append(f"- **{label} (`{m['severity']}`):** {m['summary']}")
            for ex in m.get("concrete_examples", []):
                lines.append(f"  - {ex}")
        lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    conn.close()
    print(f"Wrote {report_path} with {len(audits)} Layer-A audits.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Import Layer-A audit outputs and generate Phase 2 report from SQLite.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--outputs", type=Path, default=Path("data/phase2_outputs.json"))
    ap.add_argument("--no-import", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("reports/slices/2026-11/phase2_layer_a_audit.md"))
    args = ap.parse_args()
    import_and_report(
        db_path=args.db,
        outputs_path=None if args.no_import else args.outputs,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
