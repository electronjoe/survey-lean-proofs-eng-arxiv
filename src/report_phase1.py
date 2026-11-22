"""Import run_workflow classification outputs into SQLite and generate reports/phase1_survey.md from SQLite."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect, upsert_classification

PURE_TCS_PRIMARY_CATS = {"cs.CC", "cs.DS", "cs.LO", "cs.DM", "cs.FL", "cs.CG"}


def import_and_report(
    db_path: Path = DEFAULT_DB_PATH,
    outputs_path: Path | None = Path("data/workflow_outputs.json"),
    report_path: Path = Path("reports/slices/2026-11/phase1_survey.md"),
) -> None:
    conn = connect(db_path)

    if outputs_path is not None and outputs_path.exists():
        data = json.loads(outputs_path.read_text())
        lean_model = data.get("lean_model", "flash")
        other_model = data.get("other_model", "flash_lite")
        with conn:
            for r in data.get("lean_results", []):
                upsert_classification(conn, r["arxiv_id"], "lean_candidate", lean_model, r)
            for r in data.get("beyond_lean_results", []):
                adapted = {
                    "lean_usage_status": r["formal_usage_status"],
                    "authoring_paradigm": "N/A",
                    "paradigm_confidence": "N/A",
                    "verification_tier_observed": "N/A",
                    "ai_agent_assisted": "N/A",
                    "artifact_availability": "N/A",
                    "other_formal_tools_contributed": r.get("tools_contributed", []),
                    "static_risk_flags": [],
                    **r,
                }
                upsert_classification(conn, r["arxiv_id"], "beyond_lean", other_model, adapted)

    total_papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    screened_ok = conn.execute("SELECT COUNT(*) FROM screen_results WHERE fetch_source != 'failed'").fetchone()[0]
    date_bounds = conn.execute("SELECT MIN(submitted_date), MAX(submitted_date) FROM papers").fetchone()

    papers_by_id = {
        r["arxiv_id"]: dict(r)
        for r in conn.execute(
            """
            SELECT p.*, a.repos_json, a.latex_signals_json
            FROM papers p
            LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
            """
        ).fetchall()
    }

    # All unique target categories present in DB
    all_target_cats = sorted(
        {c for p in papers_by_id.values() for c in json.loads(p["matched_target_cats_json"])}
    )

    # Read ALL classifications from SQLite (ordered by paper submitted_date DESC)
    lean_results = [
        json.loads(r["raw_json"])
        for r in conn.execute(
            """
            SELECT c.raw_json
            FROM classifications c
            JOIN papers p ON c.arxiv_id = p.arxiv_id
            WHERE c.track = 'lean_candidate'
            ORDER BY p.submitted_date DESC, p.arxiv_id DESC
            """
        ).fetchall()
    ]
    beyond_results = [
        json.loads(r["raw_json"])
        for r in conn.execute(
            """
            SELECT c.raw_json
            FROM classifications c
            JOIN papers p ON c.arxiv_id = p.arxiv_id
            WHERE c.track = 'beyond_lean'
            ORDER BY p.submitted_date DESC, p.arxiv_id DESC
            """
        ).fetchall()
    ]

    lean_status_counts = Counter(r["lean_usage_status"] for r in lean_results)
    lean_contrib = [r for r in lean_results if r["lean_usage_status"] == "lean_contributed"]
    lean_contrib_non_tcs_prim = [
        r
        for r in lean_contrib
        if papers_by_id.get(r["arxiv_id"], {}).get("primary_category") not in PURE_TCS_PRIMARY_CATS
    ]
    eng_math_contrib = [r for r in lean_contrib if r.get("paper_domain_role") == "engineering_math_proof"]

    paradigm_counts = Counter(r["authoring_paradigm"] for r in lean_contrib)
    domain_counts = Counter(r.get("paper_domain_role", "N/A") for r in lean_contrib)
    tier_counts = Counter(r["verification_tier_observed"] for r in lean_contrib)
    ai_counts = Counter(r["ai_agent_assisted"] for r in lean_contrib)
    artifact_counts = Counter(r["artifact_availability"] for r in lean_contrib)
    risk_counts = Counter(f for r in lean_contrib for f in r.get("static_risk_flags", []))

    cat_papers = Counter()
    cat_non_tcs_papers = Counter()
    cat_lean = Counter()
    cat_eng_math = Counter()
    for p in papers_by_id.values():
        for c in json.loads(p["matched_target_cats_json"]):
            cat_papers[c] += 1
            if p["primary_category"] not in PURE_TCS_PRIMARY_CATS:
                cat_non_tcs_papers[c] += 1
    for r in lean_contrib:
        p = papers_by_id.get(r["arxiv_id"])
        if p:
            for c in json.loads(p["matched_target_cats_json"]):
                cat_lean[c] += 1
                if r.get("paper_domain_role") == "engineering_math_proof":
                    cat_eng_math[c] += 1

    beyond_status_counts = Counter(r.get("formal_usage_status", r.get("lean_usage_status")) for r in beyond_results)
    beyond_contrib = [
        r for r in beyond_results if r.get("formal_usage_status", r.get("lean_usage_status")) == "formal_contributed"
    ]
    tool_counts = Counter()
    tool_cat_counts = Counter()
    for r in beyond_contrib:
        tool_cat_counts[r["tool_category"]] += 1
        for t in r.get("tools_contributed", []):
            tool_counts[t] += 1
    for r in lean_results:
        for t in r.get("other_formal_tools_contributed", []):
            tool_counts[t] += 1

    non_tcs_total = sum(1 for p in papers_by_id.values() if p["primary_category"] not in PURE_TCS_PRIMARY_CATS)

    lines = [
        "# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers",
        "",
        f"- **Date window (submitted):** `{date_bounds[0][:10]}` to `{date_bounds[1][:10]}` (3 weeks)",
        f"- **Target categories ({len(all_target_cats)}):** " + ", ".join(f"`{c}`" for c in all_target_cats),
        f"- **Corpus size:** {total_papers} unique papers ({screened_ok} full-text screened, {100.0*screened_ok/max(total_papers,1):.2f}% coverage)",
        f"- **Non-TCS-primary engineering corpus (excluding primary {sorted(PURE_TCS_PRIMARY_CATS)}):** {non_tcs_total} unique papers",
        f"- **Confirmed papers contributing Lean proofs (all):** **{len(lean_contrib)}** ({100.0*len(lean_contrib)/max(total_papers,1):.2f}% of corpus)",
        f"- **Confirmed Lean papers (non-TCS primary):** **{len(lean_contrib_non_tcs_prim)}** ({100.0*len(lean_contrib_non_tcs_prim)/max(non_tcs_total,1):.2f}% of non-TCS corpus)",
        f"- **Confirmed `engineering_math_proof` Lean papers:** **{len(eng_math_contrib)}** ({100.0*len(eng_math_contrib)/max(total_papers,1):.2f}% of corpus)",
        f"- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **{len(beyond_contrib)}**",
        "",
        "## 1. Category Breakdown & Lean Candidate Triage",
        "",
        "| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |",
        "| :--- | ---: | ---: | ---: | ---: |",
    ]
    for c in all_target_cats:
        n = cat_papers[c]
        lc = cat_lean[c]
        em = cat_eng_math[c]
        lines.append(f"| `{c}` | {n} | {lc} | {100.0*lc/max(n,1):.2f}% | {em} |")
    lines.append(f"| **Deduplicated Union** | **{total_papers}** | **{len(lean_contrib)}** | **{100.0*len(lean_contrib)/max(total_papers,1):.2f}%** | **{len(eng_math_contrib)}** |")

    lines += [
        "",
        "| Lean Triage Status | Count |",
        "| :--- | ---: |",
    ]
    for k, v in lean_status_counts.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        "## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)",
        "",
        "| Paradigm | Count |",
        "| :--- | ---: |",
    ]
    for k in [
        "P1_paper_first_posthoc",
        "P2_lean_first",
        "P3_blueprint_sync",
        "P4_speclock_solve_distill",
        "P0_opaque_or_unspecified",
    ]:
        lines.append(f"| `{k}` | {paradigm_counts[k]} |")

    lines += [
        "",
        "## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags",
        "",
        f"- **Domain Role (Bhaskar's lens):** {dict(domain_counts)}",
        f"- **Observed Verification Tiers:** {dict(tier_counts)}",
        f"- **Artifact Availability:** {dict(artifact_counts)}",
        f"- **AI/Agent Assistance Disclosed:** {dict(ai_counts)}",
        f"- **Target Categories (Lean Contributed):** {dict(cat_lean)}",
        f"- **Static Risk Flags (`proof-methods.md`):** {dict(risk_counts.most_common())}",
        "",
        f"## 4. Detailed Inventory of Confirmed Lean Papers ({len(lean_contrib)})",
        "",
        "| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in lean_contrib:
        p = papers_by_id.get(r["arxiv_id"], {})
        cat = p.get("primary_category", "?")
        tcats = ",".join(json.loads(p.get("matched_target_cats_json", "[]")))
        flags = ", ".join(r.get("static_risk_flags", [])) or "none"
        summary = r.get("one_line_summary", "").replace("|", "/")
        lines.append(
            f"| [{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) | `{cat}` | `{tcats}` | "
            f"`{r.get('paper_domain_role', 'N/A')}` | "
            f"`{r['authoring_paradigm']}` ({r['paradigm_confidence']}) | `{r['verification_tier_observed']}` | "
            f"`{r['artifact_availability']}` | `{r['ai_agent_assisted']}` | {flags} | "
            f"**{p.get('title', '')[:70]}** — {summary} |"
        )

    lines += ["", "### Evidence Notes per Confirmed Lean Paper", ""]
    for r in lean_contrib:
        p = papers_by_id.get(r["arxiv_id"], {})
        repos = json.loads(p["repos_json"]) if p.get("repos_json") else []
        lean_repos = [rp for rp in repos if rp.get("lean_file_count", 0) > 0]
        lines.append(f"#### [{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) — {p.get('title', '')}")
        lines.append(
            f"- **Primary / Target Cats:** `{p.get('primary_category', '?')}` / {json.loads(p.get('matched_target_cats_json', '[]'))} | "
            f"**Role:** `{r.get('paper_domain_role')}`"
        )
        lines.append(
            f"- **Paradigm:** `{r['authoring_paradigm']}` (`{r['paradigm_confidence']}`) | "
            f"**Tier:** `{r['verification_tier_observed']}` | **AI:** `{r['ai_agent_assisted']}` ({r.get('ai_tools_mentioned', [])})"
        )
        lines.append(f"- **Evidence:** {r['paradigm_evidence']}")
        lines.append(f"- **Risk flags:** {r.get('static_risk_flags', [])}")
        for rp in lean_repos:
            sc = rp.get("lean_static_counts", {})
            lines.append(
                f"- **Repo `{rp['repo']}` ({rp.get('host', 'github')}):** `.lean` files={rp.get('lean_file_count')}, "
                f"LoC={sc.get('loc_nonempty', 0)}, theorems={sc.get('theorem_decl', 0)}, "
                f"defs={sc.get('def_decl', 0)}, sorry={sc.get('sorry', 0)}, "
                f"axiom={sc.get('custom_axiom', 0)}, native_decide={sc.get('native_decide', 0)}, "
                f"unsafe={sc.get('unsafe_or_impl_by', 0)}, blueprint_attr={sc.get('blueprint_attr', 0)}, "
                f"toolchain=`{rp.get('lean_toolchain', 'none')}`, ci=`{rp.get('ci_signals', [])}`"
            )
        lines.append("")

    lines += [
        "## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)",
        "",
        f"- **Candidate triage:** {dict(beyond_status_counts)}",
        f"- **Tool categories (contributed):** {dict(tool_cat_counts.most_common())}",
        "",
        "| Formal Tool | Papers Contributing |",
        "| :--- | ---: |",
    ]
    for t, c in tool_counts.most_common():
        lines.append(f"| `{t}` | {c} |")

    lines += ["", "### Confirmed Beyond-Lean Papers", ""]
    for r in beyond_contrib:
        p = papers_by_id.get(r["arxiv_id"], {})
        lines.append(
            f"- **[{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']})** (`{p.get('primary_category', '?')}`, "
            f"`{r['tool_category']}`, tools={r['tools_contributed']}): {p.get('title', '')} — {r['one_line_summary']}"
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    conn.close()
    print(f"Wrote {report_path}: {len(lean_contrib)} Lean ({len(eng_math_contrib)} eng_math_proof), {len(beyond_contrib)} Beyond-Lean.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Import classification outputs and generate Phase 1 report from SQLite.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--outputs", type=Path, default=Path("data/workflow_outputs.json"))
    ap.add_argument("--no-import", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("reports/slices/2026-11/phase1_survey.md"))
    args = ap.parse_args()
    import_and_report(
        db_path=args.db,
        outputs_path=None if args.no_import else args.outputs,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
