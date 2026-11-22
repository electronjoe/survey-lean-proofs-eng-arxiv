"""Generate a Phase 0 markdown summary report from SQLite."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect


def generate_report(db_path: Path = DEFAULT_DB_PATH, out_path: Path = Path("reports/slices/2026-11/phase0.md")) -> None:
    conn = connect(db_path)
    total_papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    screened = conn.execute("SELECT COUNT(*) FROM screen_results").fetchone()[0]

    by_source = dict(
        conn.execute("SELECT fetch_source, COUNT(*) FROM screen_results GROUP BY fetch_source").fetchall()
    )
    date_bounds = conn.execute("SELECT MIN(submitted_date), MAX(submitted_date) FROM papers").fetchone()

    # Category breakdown
    cat_total: Counter[str] = Counter()
    cat_lean_strong: Counter[str] = Counter()
    cat_lean_ctx: Counter[str] = Counter()
    cat_itp: Counter[str] = Counter()
    cat_mc: Counter[str] = Counter()
    cat_proto: Counter[str] = Counter()
    cat_smt: Counter[str] = Counter()

    tool_counts: Counter[str] = Counter()

    rows = conn.execute(
        """
        SELECT p.*, s.fetch_source, s.text_chars,
               s.has_lean_strong, s.has_lean_contextual,
               s.has_other_itp, s.has_model_checker, s.has_protocol_verifier, s.has_smt_sat,
               s.lean_hits_json, s.other_hits_json, s.urls_json, s.meta_hits_json,
               a.latex_signals_json, a.repos_json
        FROM papers p
        LEFT JOIN screen_results s ON p.arxiv_id = s.arxiv_id
        LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
        ORDER BY p.submitted_date DESC
        """
    ).fetchall()

    lean_strong_rows = []
    lean_ctx_only_rows = []
    lean_repo_rows = []
    meta_only_lean_strong = 0

    for r in rows:
        matched_cats = json.loads(r["matched_target_cats_json"])
        for c in matched_cats:
            cat_total[c] += 1
            if r["has_lean_strong"]:
                cat_lean_strong[c] += 1
            if r["has_lean_contextual"]:
                cat_lean_ctx[c] += 1
            if r["has_other_itp"]:
                cat_itp[c] += 1
            if r["has_model_checker"]:
                cat_mc[c] += 1
            if r["has_protocol_verifier"]:
                cat_proto[c] += 1
            if r["has_smt_sat"]:
                cat_smt[c] += 1

        if r["meta_hits_json"]:
            mh = json.loads(r["meta_hits_json"])
            if mh.get("has_lean_strong"):
                meta_only_lean_strong += 1

        if r["other_hits_json"]:
            oh = json.loads(r["other_hits_json"])
            for group, tools in oh.items():
                for tname in tools.keys():
                    tool_counts[f"{group}:{tname}"] += 1

        if r["has_lean_strong"]:
            lean_strong_rows.append(r)
        elif r["has_lean_contextual"]:
            lean_ctx_only_rows.append(r)

        if r["repos_json"]:
            repos = json.loads(r["repos_json"])
            if any(rp.get("lean_file_count", 0) > 0 for rp in repos):
                lean_repo_rows.append((r, repos))

    lines: list[str] = []
    lines.append("# Phase 0 Deterministic Probe Summary")
    lines.append("")
    lines.append(f"- **Date window (submitted):** `{date_bounds[0]}` to `{date_bounds[1]}`")
    lines.append(f"- **Total unique papers ingested:** {total_papers}")
    lines.append(f"- **Total papers screened:** {screened} (`html`: {by_source.get('html', 0)}, `pdf`: {by_source.get('pdf', 0)}, `failed`: {by_source.get('failed', 0)})")
    lines.append(f"- **Lean strong hits (full text):** {len(lean_strong_rows)} *(vs. metadata-only: {meta_only_lean_strong})*")
    lines.append(f"- **Lean contextual-only hits:** {len(lean_ctx_only_rows)}")
    lines.append(f"- **Confirmed public Lean GitHub repos found:** {len(lean_repo_rows)}")
    lines.append("")

    lines.append("## Breakdown by Target arXiv Category")
    lines.append("")
    lines.append("| Category | Papers | Lean Strong | Lean Ctx | Other ITP | Model Checker | Protocol Verifier | SMT/SAT |")
    lines.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for c in sorted(cat_total.keys()):
        lines.append(
            f"| `{c}` | {cat_total[c]} | {cat_lean_strong[c]} | {cat_lean_ctx[c]} | "
            f"{cat_itp[c]} | {cat_mc[c]} | {cat_proto[c]} | {cat_smt[c]} |"
        )
    lines.append("")

    lines.append("## Beyond-Lean Tool Counts (Deterministic Full-Text Hits)")
    lines.append("")
    lines.append("| Group : Tool | Papers |")
    lines.append("| :--- | ---: |")
    for k, v in tool_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")

    lines.append(f"## Lean Strong Hits ({len(lean_strong_rows)} papers)")
    lines.append("")
    for r in lean_strong_rows:
        lh = json.loads(r["lean_hits_json"] or "{}")
        urls = [
            u for u in json.loads(r["urls_json"] or "[]")
            if "arXiv/html_feedback" not in u and "brucemiller/LaTeXML" not in u
        ]
        repos = json.loads(r["repos_json"] or "[]") if r["repos_json"] else []
        latex_sig = json.loads(r["latex_signals_json"] or "{}") if r["latex_signals_json"] else {}
        strong_keys = sorted((lh.get("strong") or {}).keys())
        lines.append(f"### [{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) — {r['title']}")
        lines.append(f"- **Primary / Target Cats:** `{r['primary_category']}` / {json.loads(r['matched_target_cats_json'])} | **Submitted:** `{r['submitted_date'][:10]}` | **Source:** `{r['fetch_source']}`")
        if r["comment"]:
            lines.append(f"- **Comment:** {r['comment']}")
        lines.append(f"- **Matched Lean Signals:** `{strong_keys}`")
        if latex_sig:
            lines.append(f"- **LaTeX Signals:** `{latex_sig}`")
        if urls:
            lines.append(f"- **Artifact URLs:** {', '.join(urls[:5])}")
        for rp in repos:
            if rp.get("lean_file_count", 0) > 0 or rp.get("has_lean_toolchain"):
                sc = rp.get("lean_static_counts", {})
                lines.append(
                    f"- **Lean Repo `{rp['repo']}`:** `.lean` files={rp.get('lean_file_count')}, "
                    f"LoC={sc.get('loc_nonempty', 0)}, theorems={sc.get('theorem_decl', 0)}, "
                    f"defs={sc.get('def_decl', 0)}, sorry={sc.get('sorry', 0)}, "
                    f"axiom={sc.get('custom_axiom', 0)}, native_decide={sc.get('native_decide', 0)}, "
                    f"unsafe={sc.get('unsafe_or_impl_by', 0)}, blueprint_attr={sc.get('blueprint_attr', 0)}, "
                    f"toolchain=`{rp.get('lean_toolchain', 'none')}`, ci=`{rp.get('ci_signals', [])}`"
                )
        # First 2 strong snippets
        shown = 0
        for k, info in (lh.get("strong") or {}).items():
            for sn in info.get("snippets", [])[:1]:
                lines.append(f"  - *{k}:* `{sn[:320]}`")
                shown += 1
                if shown >= 3:
                    break
            if shown >= 3:
                break
        lines.append("")

    if lean_ctx_only_rows:
        lines.append(f"## Lean Contextual-Only Hits ({len(lean_ctx_only_rows)} papers — review for recall)")
        lines.append("")
        for r in lean_ctx_only_rows[:40]:
            lh = json.loads(r["lean_hits_json"] or "{}")
            sn = (lh.get("contextual", {}).get("snippets") or [""])[0][:240]
            lines.append(f"- **[{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']})** (`{r['primary_category']}`) {r['title']} — `{sn}`")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    conn.close()
    print(f"Wrote report to {out_path} ({len(lean_strong_rows)} lean_strong, {len(lean_ctx_only_rows)} lean_ctx_only, {len(lean_repo_rows)} lean_repos).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Phase 0 summary markdown report.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--out", type=Path, default=Path("reports/slices/2026-11/phase0.md"))
    args = ap.parse_args()
    generate_report(db_path=args.db, out_path=args.out)


if __name__ == "__main__":
    main()
