#!/usr/bin/env python3
"""Programmatic numeric consistency & scholarly-register gate for `papers/arxiv-empirical/main.tex`.

Verifies every empirical table cell (Tables 4–10 + Appendix A 82-paper master ledger),
headline prose statistic, confidence interval, multiplier, and scholarly-style invariant
in `papers/arxiv-empirical/main.tex` directly against the canonical git-tracked artifact:
  - `artifacts/unified_15cat_panel.json`

Exit code 0 if every check passes; non-zero with exact expected-vs-found diffs on drift.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEX = REPO_ROOT / "papers" / "arxiv-empirical" / "main.tex"
DEFAULT_PANEL = REPO_ROOT / "artifacts" / "unified_15cat_panel.json"

ROLE_SHORT = {
    "eng_algorithmic_proof": "Eng. Alg.",
    "operational_system_fv": "System FV",
    "pure_math_or_tcs": "Math/TCS",
    "meta_formalization_system": "Meta-Sys.",
}
TIER_SHORT = {
    "Tier3_Gold": "Gold",
    "Tier2_Silver": "Silver",
    "Tier1_Bronze": "Bronze",
}
AI_SHORT = {
    "explicitly_yes": "Disclosed",
    "explicitly_no": "Human",
    "unclear": "Unstated",
}
RISK_SHORT = {
    "Mode2_ScopeDowngrade": "Scope",
    "Mode3_CustomDefs": "Defs",
    "Mode6_SorryOrAxiomOrNativeDecide": "Axiom",
    "Mode7_MetaprogOrUnsafe": "Meta",
    "Mode10_ProofBloat": "Bloat",
    "Mode12_ProcessOpacity": "Opac.",
    "OpFV_RefinementGap": "Refin.",
}

FORBIDDEN_SCHEMA_TOKENS = (
    "eng_algorithmic_proof",
    "operational_system_fv",
    "pure_math_or_tcs",
    "meta_formalization_system",
    "lean_usage_status",
    "lean_contributed",
    "Tier3_Gold",
    "Tier2_Silver",
    "Tier1_Bronze",
    "P1_paper_first_posthoc",
    "P2_lean_first",
    "P3_blueprint_sync",
    "P4_speclock_solve_distill",
    "P0_opaque_or_unspecified",
    "material_undisclosed_drift_or_risk",
    "high_faithful",
    "mostly_faithful_with_disclosed_gaps",
    "partial_or_weakened_formalization",
    "explicitly_yes",
    "explicitly_no",
    "Mode12_ProcessOpacity",
    "Mode10_ProofBloat",
    "Mode2_ScopeDowngrade",
    "Mode3_CustomDefs",
    "Mode6_SorryOrAxiomOrNativeDecide",
    "Mode7_MetaprogOrUnsafe",
    "paper_domain_role",
    "public_lean_repo",
    "broken_or_missing_repo",
    "v_latest",
)

FORBIDDEN_INTERNAL_PATHS = (
    "src/",
    "scripts/",
    "workflows/",
    "artifacts/",
    "reports/",
    "data/survey.db",
    "data/slice_",
    "docs/",
)


def strip_tex_comments(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in tex.splitlines())


def clean_tex_cell(cell: str) -> str:
    s = cell.strip()
    s = re.sub(r"\\quad\s*", " ", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    s = s.replace(r"\ ", " ")
    s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_")
    s = s.replace("~", " ").replace(r"\,", "").replace("{,}", ",")
    s = s.replace(r"\textemdash{}", "—").replace(r"\textemdash", "—")
    s = s.replace(r"$\times$", "x").replace(r"\times", "x")
    s = s.replace(r"$\to$", "->").replace(r"$\rightarrow$", "->")
    return re.sub(r"\s+", " ", s).strip()


def extract_table_by_label(tex: str, label: str) -> str:
    """Return the tabular/tabularx/longtable body containing \\label{<label>}."""
    # First search standard table / table* floats
    for m in re.finditer(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", tex, flags=re.DOTALL):
        block = m.group(0)
        if f"\\label{{{label}}}" in block:
            tm = re.search(r"\\begin\{tabularx?\}.*?\\end\{tabularx?\}", block, flags=re.DOTALL)
            if tm:
                return tm.group(0)
    # Next search longtable environments
    for m in re.finditer(r"\\begin\{longtable\}.*?\\end\{longtable\}", tex, flags=re.DOTALL):
        block = m.group(0)
        if f"\\label{{{label}}}" in block:
            return block
    raise ValueError(f"Table with \\label{{{label}}} not found in LaTeX source")


def split_tabular_rows(tabular_block: str) -> list[list[str]]:
    """Split a LaTeX tabular/tabularx/longtable body into data rows of cells."""
    if tabular_block.startswith(r"\begin{longtable}"):
        # Data rows start immediately after \endlastfoot
        m = re.search(r"\\endlastfoot\s*(.*?)\\end\{longtable\}", tabular_block, flags=re.DOTALL)
        body = m.group(1) if m else tabular_block
    else:
        body = re.sub(r"^\\begin\{tabularx?\}(?:\{[^}]*\})?\{.*?\}\n", "", tabular_block, count=1, flags=re.DOTALL)
        body = re.sub(r"\\end\{tabularx?\}\s*$", "", body, flags=re.DOTALL)

    rows: list[list[str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(
            ("\\toprule", "\\midrule", "\\bottomrule", "\\multicolumn", "\\caption", "\\label")
        ):
            continue
        if r"\\" not in line:
            continue
        line = line.split(r"\\")[0].strip()
        if not line:
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)&", line)]
        rows.append(cells)
    return rows


def check_table_longitudinal_15cat(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:longitudinal_15cat")
    rows = split_tabular_rows(tab)
    t0, t1, t2 = panel["slices"]
    gt = panel["grand_totals"]
    mult = panel["multipliers"]

    def _row_by_prefix(prefix: str) -> list[str] | None:
        for r in rows:
            if clean_tex_cell(r[0]).startswith(prefix):
                return [clean_tex_cell(c) for c in r]
        return None

    def _chk(prefix: str, idx: int, expected: str) -> None:
        row = _row_by_prefix(prefix)
        if row is None:
            errors.append(f"tab:longitudinal_15cat missing row starting with {prefix!r}")
            return
        if row[idx] != expected:
            errors.append(
                f"tab:longitudinal_15cat [{prefix}][col {idx}]: got {row[idx]!r} != expected {expected!r}"
            )

    def _chk_contains(prefix: str, idx: int, token: str) -> None:
        row = _row_by_prefix(prefix)
        if row is None:
            errors.append(f"tab:longitudinal_15cat missing row starting with {prefix!r}")
            return
        if token not in row[idx]:
            errors.append(
                f"tab:longitudinal_15cat [{prefix}][col {idx}]: missing {token!r} in {row[idx]!r}"
            )

    # Corpus & revisions
    for ci, sl in ((1, t0), (2, t1), (3, t2)):
        _chk("Unique preprints", ci, f"{sl['total_papers']:,} ({sl['fulltext_coverage_pct']:.2f}%)")
        _chk("Later-revised preprints", ci, f"{sl['revised_v_gt_1']:,} ({sl['revised_v_gt_1_pct']:.1f}%)")
        _chk("Traditional FV tools", ci, f"{sl['beyond_lean_stage2']['count']} ({sl['beyond_lean_stage2']['pct']:.2f}%)")
        _chk("Stage-2 Lean 4", ci, f"{sl['stage2_lean_candidates']} ({sl['stage2_lean_cand_pct']:.2f}%)")
        _chk("Confirmed Lean (initial v1)", ci, f"{sl['confirmed_v1']['count']} ({sl['confirmed_v1']['pct']:.2f}%)")
        _chk("Confirmed Lean (incl. revisions)", ci, f"{sl['confirmed_v_latest']['count']} ({sl['confirmed_v_latest']['pct']:.2f}%)")
    _chk_contains("Unique preprints", 4, f"{gt['total_papers']:,}")
    _chk_contains("Unique preprints", 4, f"{gt['fulltext_coverage_pct']:.2f}%")
    _chk_contains("Confirmed Lean (initial v1)", 4, f"{mult['pooled_v1_t2_over_t1']:.1f}x")
    _chk_contains("Confirmed Lean (incl. revisions)", 4, f"{mult['pooled_v_latest_t2_over_t1']:.1f}x")
    _chk_contains("Confirmed Lean (incl. revisions)", 4, f"{mult['pooled_v_latest_t2_over_t0']:.2f}x")

    # 4-way strata
    role_prefixes = [
        ("1. Engineering algorithmic proofs", "eng_algorithmic_proof"),
        ("2. Operational system verification", "operational_system_fv"),
        ("3. Pure math & TCS cross-lists", "pure_math_or_tcs"),
        ("4. Autoformalization pipelines", "meta_formalization_system"),
    ]
    for pref, rk in role_prefixes:
        for ci, sl in ((1, t0), (2, t1), (3, t2)):
            v1_b = sl["roles_v1"][rk]
            lat_b = sl["roles_v_latest"][rk]
            exp = f"{v1_b['count']} ({lat_b['count']}) [{v1_b['pct']:.2f}%]"
            _chk(pref, ci, exp)
    _chk_contains("1. Engineering algorithmic proofs", 4, f"{mult['eng_alg_v1_t2_over_t1']:.2f}x")
    _chk_contains("3. Pure math & TCS cross-lists", 4, f"{mult['pure_math_tcs_v1_t2_over_t1']:.2f}x")

    # Strict core eng_alg
    for ci, sl in ((1, t0), (2, t1), (3, t2)):
        eb = sl["roles_v1"]["eng_algorithmic_proof"]
        _chk("Strict core", ci, f"{eb['strict_core_count']} [{eb['strict_core_pct']:.2f}%]")

    # AI disclosure, tiers, median & total LoC
    for ci, sl in ((2, t1), (3, t2)):
        ai = sl["confirmed_v1"]["ai_assistance"]
        n_v1 = sl["confirmed_v1"]["count"]
        ai_pct = 100.0 * ai.get("explicitly_yes", 0) / n_v1
        _chk(
            "Explicit AI disclosure",
            ci,
            f"{ai.get('explicitly_yes', 0)} / {ai.get('unclear', 0)} / {ai.get('explicitly_no', 0)} ({ai_pct:.1f}%)",
        )
        tr = sl["confirmed_v1"]["tiers"]
        _chk(
            "Verification tiers",
            ci,
            f"{tr.get('Tier3_Gold', 0)} / {tr.get('Tier2_Silver', 0)} / {tr.get('Tier1_Bronze', 0)}",
        )
        _chk(
            "Median paper-owned LoC (v1, pooled)",
            ci,
            f"{sl['confirmed_v1']['median_owned_loc']:,} ($n={sl['confirmed_v1']['scanned_owned_repos']}$)",
        )
        eb = sl["roles_v1"]["eng_algorithmic_proof"]
        _chk(
            "Median paper-owned LoC (v1, Eng. Alg.)",
            ci,
            f"{eb['median_owned_loc']:,} ($n={eb['scanned_owned_repos']}$)",
        )
        _chk("Total paper-owned LoC", ci, f"{sl['confirmed_v1']['total_owned_loc']:,}")

    gold_t2_pct = 100.0 * t2["confirmed_v1"]["tiers"]["Tier3_Gold"] / t2["confirmed_v1"]["count"]
    _chk_contains("Verification tiers", 4, f"{gold_t2_pct:.1f}%")
    _chk_contains("Median paper-owned LoC (v1, pooled)", 4, f"{mult['pooled_median_loc_t2_over_t1']:.1f}x")
    _chk_contains("Median paper-owned LoC (v1, Eng. Alg.)", 4, f"{mult['eng_alg_median_loc_t2_over_t1']:.1f}x")
    _chk_contains("Total paper-owned LoC", 4, f"{t2['confirmed_v1']['total_owned_loc'] / 1e6:.2f}M")

    # Complete eess.* and non-control eess.*
    for ci, sl in ((1, t0), (2, t1), (3, t2)):
        ea = sl["eess_archive"]
        _chk(
            "Complete eess.* archive",
            ci,
            f"{ea['eess_all_confirmed_v1']['count']}/{ea['eess_all_unique_papers']:,} ({ea['eess_all_confirmed_v1']['pct']:.2f}%)",
        )
        _chk(
            "Non-control eess.*",
            ci,
            f"{ea['eess_non_sy_confirmed_v1']['count']}/{ea['eess_non_sy_unique_papers']:,} ({ea['eess_non_sy_confirmed_v1']['pct']:.2f}%)",
        )
    _chk_contains("Complete eess.* archive", 4, f"{gt['complete_eess_3slice_unique_papers']:,}")
    nc3 = gt["eess_non_sy_3slice_confirmed_v1"]
    _chk_contains("Non-control eess.*", 4, f"{nc3['count']}/{nc3['total']:,} ({nc3['pct']:.2f}%)")

    return errors


def check_table_categories_15cat(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:categories_15cat")
    rows = split_tabular_rows(tab)
    t0, t1, t2 = panel["slices"]
    gt = panel["grand_totals"]
    seen_cats: set[str] = set()

    for raw_cells in rows:
        cells = [clean_tex_cell(c) for c in raw_cells]
        if len(cells) < 12 or cells[0].startswith("Category"):
            continue
        col0 = cells[0]

        if col0.startswith("Deduplicated 15-Cat Union"):
            exp_row = [
                f"{t0['total_papers']:,} ({t0['confirmed_v1']['count']}/{t0['confirmed_v_latest']['count']})",
                f"{t1['total_papers']:,} ({t1['confirmed_v1']['count']}/{t1['confirmed_v_latest']['count']})",
                f"{t2['total_papers']:,}",
                f"{t2['stage2_lean_candidates']}",
                f"{t2['confirmed_v1']['count']} ({t2['confirmed_v_latest']['count']})",
                f"{t2['confirmed_v1']['pct']:.2f}%",
                f"{t2['roles_v1']['eng_algorithmic_proof']['count']} ({t2['roles_v1']['eng_algorithmic_proof']['pct']:.2f}%)",
                f"{t2['roles_v1']['pure_math_or_tcs']['count']}",
                f"{t2['roles_v1']['operational_system_fv']['count']}",
                f"{t2['roles_v1']['meta_formalization_system']['count']}",
                f"{gt['total_papers']:,} ({gt['confirmed_v1_total']}/{gt['confirmed_v_latest_total']})",
            ]
            if cells[1:12] != exp_row:
                errors.append(f"tab:categories_15cat [Union]: got {cells[1:12]} != expected {exp_row}")
            continue

        if col0.startswith("Complete eess.*"):
            e0, e1, e2 = t0["eess_archive"], t1["eess_archive"], t2["eess_archive"]
            if cells[3] != f"{e2['eess_all_unique_papers']:,}" or cells[6] != f"{e2['eess_all_confirmed_v1']['pct']:.2f}%":
                errors.append(f"tab:categories_15cat [Complete eess.*]: unexpected T2 values {cells[1:12]}")
            if not cells[11].startswith(f"{gt['complete_eess_3slice_unique_papers']:,}"):
                errors.append(f"tab:categories_15cat [Complete eess.*]: unexpected 3-slice {cells[11]!r}")
            continue

        if col0.startswith("Non-control eess.*"):
            nc3 = gt["eess_non_sy_3slice_confirmed_v1"]
            if cells[3] != f"{t2['eess_archive']['eess_non_sy_unique_papers']:,}" or cells[6] != "0.00%":
                errors.append(f"tab:categories_15cat [Non-control eess.*]: unexpected T2 values {cells[1:12]}")
            exp_3s = f"{nc3['total']:,} ({nc3['count']}/{nc3['count']})"
            if cells[11] != exp_3s:
                errors.append(f"tab:categories_15cat [Non-control eess.*]: got {cells[11]!r} != expected {exp_3s!r}")
            continue

        m = re.match(r"([a-z]+\.[A-Za-z-]+)\b", col0)
        if not m:
            continue
        cat = m.group(1)
        if cat not in t2["per_category"]:
            continue
        seen_cats.add(cat)
        c0, c1, c2 = t0["per_category"][cat], t1["per_category"][cat], t2["per_category"][cat]
        c3 = panel["per_category_3slice_totals"][cat]
        r2 = c2["roles_v1"]
        t2_v1 = c2["confirmed_v1"]["count"]
        t2_lat = c2["confirmed_v_latest"]["count"]
        t2_v1_str = f"{t2_v1}" if t2_v1 == t2_lat else f"{t2_v1} ({t2_lat})"
        eng_k = r2["eng_algorithmic_proof"]
        eng_pct = 100.0 * eng_k / c2["total_papers"]
        eng_s = f"{eng_k} ({eng_pct:.2f}%)" if eng_k > 0 else "0"
        exp_row = [
            f"{c0['total_papers']:,} ({c0['confirmed_v1']['count']}/{c0['confirmed_v_latest']['count']})",
            f"{c1['total_papers']:,} ({c1['confirmed_v1']['count']}/{c1['confirmed_v_latest']['count']})",
            f"{c2['total_papers']:,}",
            f"{c2['stage2_lean_candidates']}",
            t2_v1_str,
            f"{c2['confirmed_v1']['pct']:.2f}%",
            eng_s,
            f"{r2['pure_math_or_tcs']}",
            f"{r2['operational_system_fv']}",
            f"{r2['meta_formalization_system']}",
            f"{c3['total_papers_3slice']:,} ({c3['confirmed_v1_3slice']['count']}/{c3['confirmed_v_latest_3slice']['count']})",
        ]
        if cells[1:12] != exp_row:
            errors.append(f"tab:categories_15cat [{cat}]: got {cells[1:12]} != expected {exp_row}")

    missing = set(panel["categories"]["all15"]) - seen_cats
    if missing:
        errors.append(f"tab:categories_15cat missing categories: {sorted(missing)}")
    return errors


def check_table_off_arxiv(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:off_arxiv")
    rows = [[clean_tex_cell(c) for c in r] for r in split_tabular_rows(tab)]
    oa = panel["off_arxiv_probe"]
    ps = oa["preprint_servers"]
    oal = oa["openalex"]

    def _find(prefix: str) -> list[str] | None:
        for r in rows:
            if r[0].startswith(prefix):
                return r
        return None

    for pref, blk in (
        ("TechRxiv (IEEE", ps["techrxiv"]),
        ("engrXiv", ps["engrxiv"]),
        ("TechRxiv + engrXiv", ps["combined"]),
    ):
        r = _find(pref)
        if not r:
            errors.append(f"tab:off_arxiv missing row {pref!r}")
            continue
        exp_tot = f"{blk['total_records_2025_2026']:,}"
        exp_ub = f"{blk['confirmed_95pct_ub_pct']:.3f}%"
        if r[1] != exp_tot or exp_ub not in r[2] or not r[2].startswith(f"{blk['confirmed_lean_tp_unique']} "):
            errors.append(f"tab:off_arxiv [{pref}]: got ({r[1]}, {r[2]}) != expected ({exp_tot}, {blk['confirmed_lean_tp_unique']} / UB {exp_ub})")

    r_gl = _find("OpenAlex Global")
    all_f = oal["mathlib_all_fields"]
    if not r_gl:
        errors.append("tab:off_arxiv missing OpenAlex Global row")
    else:
        for tok in (f"{all_f['count_2025_2026']:,}", f"{all_f['yoy_multiplier_2026_over_2025']:.1f}x"):
            if tok not in r_gl[2]:
                errors.append(f"tab:off_arxiv [OpenAlex Global]: missing {tok!r} in {r_gl[2]!r}")
        for tok in (f"{all_f['count_2025']}", f"{all_f['count_2026']:,}"):
            if tok not in r_gl[3]:
                errors.append(f"tab:off_arxiv [OpenAlex Global]: missing {tok!r} in {r_gl[3]!r}")

    r_eng = _find("OpenAlex Engineering")
    eng = oal["engineering_field_22"]
    if not r_eng:
        errors.append("tab:off_arxiv missing OpenAlex Engineering row")
    else:
        if r_eng[1] != f"{eng['total_works_2025_2026']:,}":
            errors.append(f"tab:off_arxiv [OpenAlex Eng total]: got {r_eng[1]!r} != {eng['total_works_2025_2026']:,}")
        for tok in (f"{eng['mathlib_count_2025_2026']}", f"{eng['mathlib_share_of_all_mathlib_pct']:.2f}%"):
            if tok not in r_eng[2]:
                errors.append(f"tab:off_arxiv [OpenAlex Eng]: missing {tok!r} in {r_eng[2]!r}")
    return errors


def check_table_distributions_15cat(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:distributions_15cat")
    rows = [[clean_tex_cell(c) for c in r] for r in split_tabular_rows(tab)]
    dist = panel["t2_distributions_by_role_v1"]
    col_keys = [
        "eng_algorithmic_proof",
        "pure_math_or_tcs",
        "operational_system_fv",
        "meta_formalization_system",
        "pooled",
    ]
    pooled_loc = dist["pooled"]["total_owned_loc"]

    def _row_by_col1(prefix: str) -> list[str] | None:
        for r in rows:
            if len(r) >= 7 and r[1].startswith(prefix):
                return r
        return None

    def _chk_cnt_pct(label_prefix: str, bucket: str, field: str) -> None:
        r = _row_by_col1(label_prefix)
        if not r:
            errors.append(f"tab:distributions_15cat missing row {label_prefix!r}")
            return
        for idx, rk in enumerate(col_keys, start=2):
            n_tot = dist[rk]["count"]
            k = dist[rk][bucket].get(field, 0)
            exp = f"{k} ({100.0 * k / n_tot:.1f}%)"
            if r[idx] != exp:
                errors.append(f"tab:distributions_15cat [{label_prefix}][{rk}]: got {r[idx]!r} != expected {exp!r}")

    for pref, bucket, field in [
        ("P1: Post-hoc", "paradigms", "P1_paper_first_posthoc"),
        ("P0: Unspecified", "paradigms", "P0_opaque_or_unspecified"),
        ("P4: Pinned", "paradigms", "P4_speclock_solve_distill"),
        ("P3: Synchronized", "paradigms", "P3_blueprint_sync"),
        ("P2: Lean-first", "paradigms", "P2_lean_first"),
        ("Gold", "tiers", "Tier3_Gold"),
        ("Silver", "tiers", "Tier2_Silver"),
        ("Bronze", "tiers", "Tier1_Bronze"),
        ("Explicitly disclosed", "ai_assistance", "explicitly_yes"),
        ("Unstated", "ai_assistance", "unclear"),
        ("Explicitly human-only", "ai_assistance", "explicitly_no"),
        ("Proof bloat", "static_risk_flags", "Mode10_ProofBloat"),
        ("Process opacity", "static_risk_flags", "Mode12_ProcessOpacity"),
        ("Scope downgrading", "static_risk_flags", "Mode2_ScopeDowngrade"),
        ("Unproved axioms", "static_risk_flags", "Mode6_SorryOrAxiomOrNativeDecide"),
        ("Metaprogramming", "static_risk_flags", "Mode7_MetaprogOrUnsafe"),
    ]:
        _chk_cnt_pct(pref, bucket, field)

    # Scale rows
    for pref, fn in [
        ("Scanned repositories", lambda rk: f"{dist[rk]['scanned_owned_repos']}"),
        ("Median paper-owned LoC", lambda rk: f"{dist[rk]['median_owned_loc']:,}"),
        ("Total paper-owned LoC", lambda rk: f"{dist[rk]['total_owned_loc']:,}"),
        ("Share of T2 owned LoC", lambda rk: f"{100.0 * dist[rk]['total_owned_loc'] / pooled_loc:.1f}%"),
    ]:
        r = _row_by_col1(pref)
        if not r:
            errors.append(f"tab:distributions_15cat missing row {pref!r}")
            continue
        for idx, rk in enumerate(col_keys, start=2):
            exp = fn(rk)
            if r[idx] != exp:
                errors.append(f"tab:distributions_15cat [{pref}][{rk}]: got {r[idx]!r} != expected {exp!r}")

    # Artifact status rows
    r_art2 = _row_by_col1("Ancillary / Broken / None")
    if not r_art2:
        errors.append("tab:distributions_15cat missing 'Ancillary / Broken / None' row")
    else:
        for idx, rk in enumerate(col_keys, start=2):
            a = dist[rk]["artifact_availability"]
            exp = f"{a.get('appendix_only', 0)} / {a.get('broken_or_missing_repo', 0)} / {a.get('none', 0)}"
            if r_art2[idx] != exp:
                errors.append(f"tab:distributions_15cat [Artifact Status][{rk}]: got {r_art2[idx]!r} != expected {exp!r}")

    return errors


def _check_paper_ledger_table(
    tex: str,
    label: str,
    expected_papers: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, label)
    rows = split_tabular_rows(tab)
    by_id = {p["arxiv_id"]: p for p in expected_papers}
    seen_ids: set[str] = set()

    for raw_cells in rows:
        if len(raw_cells) < 10:
            continue
        aid = clean_tex_cell(raw_cells[0])
        if not re.match(r"^\d{4}\.\d{5}$", aid):
            continue
        seen_ids.add(aid)
        if aid not in by_id:
            errors.append(f"{label}: unexpected arXiv ID {aid}")
            continue
        p = by_id[aid]

        # Slice + retro dagger
        got_sl = raw_cells[1].strip()
        exp_sl_base = p["short_id"]
        if not got_sl.startswith(exp_sl_base):
            errors.append(f"{label} [{aid}] Slice: got {got_sl!r} != expected {exp_sl_base!r}")
        has_dagger = r"\dagger" in got_sl
        if p["lean_in_v1"] and has_dagger:
            errors.append(f"{label} [{aid}]: unexpected retroactive dagger on v1 paper")
        if (not p["lean_in_v1"]) and (not has_dagger):
            errors.append(f"{label} [{aid}]: missing retroactive dagger on v_latest-only paper")

        # Role, Paradigm, Tier, AI
        for col_i, col_name, exp_val in [
            (3, "Role", ROLE_SHORT[p["role_4way"]]),
            (4, "Paradigm", p["authoring_paradigm"].split("_")[0]),
            (5, "Tier", TIER_SHORT[p["verification_tier"]]),
            (6, "AI", AI_SHORT[p["ai_agent_assisted"]]),
        ]:
            got = clean_tex_cell(raw_cells[col_i])
            if got != exp_val:
                errors.append(f"{label} [{aid}] {col_name}: got {got!r} != expected {exp_val!r}")

        # Owned LoC
        got_loc = clean_tex_cell(raw_cells[7])
        loc = p.get("primary_owned_loc") or 0
        if loc > 0:
            exp_loc = f"{loc:,}" + ("*" if p.get("vendor_exclusion_note") else "")
            if got_loc != exp_loc:
                errors.append(f"{label} [{aid}] LoC: got {got_loc!r} != expected {exp_loc!r}")
        else:
            art = p["artifact_availability"]
            if art == "public_lean_repo" and "unreach" not in got_loc:
                errors.append(f"{label} [{aid}] LoC: expected 'unreach.' for unreachable repo, got {got_loc!r}")
            elif art == "appendix_only" and "anc" not in got_loc:
                errors.append(f"{label} [{aid}] LoC: expected 'anc.' for ancillary paper, got {got_loc!r}")
            elif art in ("none", "broken_or_missing_repo") and got_loc != "—":
                errors.append(f"{label} [{aid}] LoC: expected em-dash, got {got_loc!r}")

        # Risks
        got_risks_txt = clean_tex_cell(raw_cells[8])
        got_risks = set() if got_risks_txt == "None" else {x.strip() for x in got_risks_txt.split(",") if x.strip()}
        exp_risks = {RISK_SHORT[f] for f in p.get("static_risk_flags", []) if f in RISK_SHORT}
        if got_risks != exp_risks:
            errors.append(f"{label} [{aid}] Risks: got {sorted(got_risks)} != expected {sorted(exp_risks)}")

        # Citation key present in title cell
        exp_cite = f"\\cite{{arxiv{aid.replace('.', '_')}}}"
        if exp_cite not in raw_cells[9]:
            errors.append(f"{label} [{aid}]: missing {exp_cite} in title column")

    missing = sorted(set(by_id) - seen_ids)
    if missing:
        errors.append(f"{label} missing papers: {missing}")
    if len(seen_ids) != len(by_id):
        errors.append(f"{label} row count={len(seen_ids)} != expected {len(by_id)}")
    return errors


def check_table_sandbox_unified(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:sandbox_unified")
    rows = split_tabular_rows(tab)
    sb = panel["sandbox_builds"]
    ov = sb["overall"]
    by_id = {r["arxiv_id"]: r for r in sb["records"]}
    seen_ids: set[str] = set()
    saw_pooled = False

    for raw_cells in rows:
        cells = [clean_tex_cell(c) for c in raw_cells]
        if len(cells) < 9:
            continue
        if cells[0].startswith("Pooled All-Role"):
            saw_pooled = True
            if cells[1] != str(ov["total_attempted"]):
                errors.append(f"tab:sandbox_unified [Pooled n]: got {cells[1]!r} != {ov['total_attempted']}")
            if f"{ov['distinct_pinned_toolchains_count']} distinct" not in cells[4]:
                errors.append(f"tab:sandbox_unified [Pooled toolchains]: got {cells[4]!r}")
            if f"{ov['median_pass_wall_time_sec']:.1f}" not in cells[6]:
                errors.append(f"tab:sandbox_unified [Pooled median time]: got {cells[6]!r}")
            if cells[7] != f"{ov['total_theorems_checked_ootb']:,}":
                errors.append(f"tab:sandbox_unified [Pooled OOTB thms]: got {cells[7]!r} != {ov['total_theorems_checked_ootb']:,}")
            for tok in (
                f"{ov['pass_out_of_box']}/{ov['total_attempted']} ({ov['pass_out_of_box_pct']:.1f}%)",
                f"{ov['pass_and_standard_axioms_only']}/{ov['pass_out_of_box']} clean",
                f"{ov['tier3_gold_clean_axioms']}/{ov['tier3_gold_pass_out_of_box']} Gold clean",
                f"{ov['total_theorems_checked_incl_synthetic']:,}",
            ):
                if tok not in cells[8]:
                    errors.append(f"tab:sandbox_unified [Pooled summary]: missing {tok!r} in {cells[8]!r}")
            continue

        aid = cells[0]
        if not re.match(r"^\d{4}\.\d{5}$", aid):
            continue
        seen_ids.add(aid)
        if aid not in by_id:
            errors.append(f"tab:sandbox_unified: unknown arXiv ID {aid}")
            continue
        r = by_id[aid]

        if cells[1] != r["short_id"]:
            errors.append(f"tab:sandbox_unified [{aid}] Slice: got {cells[1]!r} != {r['short_id']!r}")
        if cells[2] != TIER_SHORT[r["static_verification_tier"]]:
            errors.append(f"tab:sandbox_unified [{aid}] Tier: got {cells[2]!r} != {TIER_SHORT[r['static_verification_tier']]!r}")
        if cells[3] != f"{r['owned_loc']:,}":
            errors.append(f"tab:sandbox_unified [{aid}] LoC: got {cells[3]!r} != {r['owned_loc']:,}")

        exp_tc = (r.get("lean_toolchain") or "").replace("leanprover/lean4:", "") or "none"
        if cells[4] != exp_tc:
            errors.append(f"tab:sandbox_unified [{aid}] Toolchain: got {cells[4]!r} != {exp_tc!r}")

        if r["build_status"] == "pass":
            exp_t = f"{r['wall_time_sec']:,.1f}"
            if cells[6] != exp_t:
                errors.append(f"tab:sandbox_unified [{aid}] Time: got {cells[6]!r} != {exp_t!r}")
            if cells[7] != f"{r['total_theorems_checked']:,}":
                errors.append(f"tab:sandbox_unified [{aid}] Thms: got {cells[7]!r} != {r['total_theorems_checked']:,}")
            if not cells[8].startswith("Pass"):
                errors.append(f"tab:sandbox_unified [{aid}] Outcome: expected Pass, got {cells[8]!r}")
        elif r["build_status"] == "fail_packaging":
            syn = r.get("synthetic_env_check") or {}
            exp_thms = f"0 ({syn.get('total_theorems_checked', 0)}*)"
            if cells[7] != exp_thms:
                errors.append(f"tab:sandbox_unified [{aid}] Synth thms: got {cells[7]!r} != {exp_thms!r}")
            if "Fail (packaging)" not in cells[8]:
                errors.append(f"tab:sandbox_unified [{aid}] Outcome: expected Fail (packaging), got {cells[8]!r}")
        else:
            if cells[6] != f"{r['wall_time_sec']:.1f}" or cells[7] != "0":
                errors.append(f"tab:sandbox_unified [{aid}] Local-dep fail mismatch: ({cells[6]}, {cells[7]})")

    if not saw_pooled:
        errors.append("tab:sandbox_unified missing Pooled All-Role summary row")
    missing = sorted(set(by_id) - seen_ids)
    if missing:
        errors.append(f"tab:sandbox_unified missing repos: {missing}")
    return errors


def check_table_stage4_irr(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:stage4_irr")
    rows = [[clean_tex_cell(c) for c in r] for r in split_tabular_rows(tab)]
    irr_metrics = panel["human_validation"]["stage4_irr"]["human_vs_llm"]["annotator_1"]["metrics"]
    by_key = {(m["field"], m["scope"]): m for m in irr_metrics}

    row_map = [
        ("Lean proof contribution", "All sampled", ("is_lean_contributed", "all")),
        ("Lean usage status", "All sampled", ("lean_usage_status", "all")),
        ("Static verification tier", "All sampled", ("verification_tier", "all")),
        ("Authoring paradigm", "All sampled", ("authoring_paradigm", "all")),
        ("AI assistance disclosure", "All sampled", ("ai_agent_assisted", "all")),
        ("Initial 3-way domain role", "All sampled", ("paper_domain_role", "all")),
        ("Static verification tier", "Agreed contributors", ("verification_tier", "agreed_contributed")),
        ("Authoring paradigm", "Agreed contributors", ("authoring_paradigm", "agreed_contributed")),
        ("AI assistance disclosure", "Agreed contributors", ("ai_agent_assisted", "agreed_contributed")),
        ("Initial 3-way domain role", "Agreed contributors", ("paper_domain_role", "agreed_contributed")),
    ]

    for col0_pref, col1_pref, key in row_map:
        m = by_key[key]
        matched = [r for r in rows if len(r) >= 6 and r[0].startswith(col0_pref) and r[1].startswith(col1_pref)]
        if not matched:
            errors.append(f"tab:stage4_irr missing row ({col0_pref!r}, {col1_pref!r})")
            continue
        r = matched[0]
        exp = [
            str(m["n"]),
            f"{m['exact_agreement']:.3f}",
            f"{m['cohens_kappa']:.3f}",
            f"{m['krippendorff_alpha']:.3f}",
        ]
        if r[2:6] != exp:
            errors.append(f"tab:stage4_irr [{key}]: got {r[2:6]} != expected {exp}")
    return errors


def check_prose_and_style(tex: str, panel: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    t0, t1, t2 = panel["slices"]
    gt = panel["grand_totals"]
    mult = panel["multipliers"]
    rc = panel["recall_calibration"]
    la = panel["layer_a_audits"]
    sb = panel["sandbox_builds"]
    ov = sb["overall"]
    opfv = panel["operational_fv_audit"]["summary_counts"]
    oa = panel["off_arxiv_probe"]
    hv = panel["human_validation"]

    # Normalize TeX formatting slightly for clean numeric prose checks without requiring \textbf
    plain_tex = re.sub(r"\\textbf\{([^}]*)\}", r"\1", tex)
    plain_tex = plain_tex.replace(r"\%", "%").replace("~", " ").replace("{,}", ",")

    def _must_match(desc: str, pattern: str, scope: str = plain_tex) -> None:
        if not re.search(pattern, scope):
            errors.append(f"Prose mismatch ({desc}): expected pattern {pattern!r} in main.tex")

    abs_m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, flags=re.DOTALL)
    abstract_raw = abs_m.group(1) if abs_m else ""
    if not abstract_raw:
        errors.append("Missing \\begin{abstract}...\\end{abstract} block")
    else:
        if r"\textbf{" in abstract_raw:
            errors.append("Style violation: Abstract must contain ZERO \\textbf{...} spans")
        # Count standard whitespace-delimited words (excluding LaTeX commands)
        clean_abs = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", abstract_raw)
        clean_abs = re.sub(r"\\[a-zA-Z]+", " ", clean_abs)
        abs_words = len([w for w in clean_abs.split() if re.search(r"[A-Za-z0-9]", w)])
        if abs_words > 300:
            errors.append(f"Style violation: Abstract is too long ({abs_words} words > 300 max)")

    # 1. Zero raw JSON schema enum leakage & zero internal repo paths & zero Markdown **
    tex_unescaped = tex.replace(r"\_", "_")
    for tok in FORBIDDEN_SCHEMA_TOKENS:
        if re.search(rf"\b{re.escape(tok)}\b", tex_unescaped):
            errors.append(f"Schema leakage: raw JSON enum token {tok!r} appears in main.tex")

    for path_tok in FORBIDDEN_INTERNAL_PATHS:
        if path_tok in tex_unescaped:
            errors.append(f"Style violation: internal repository path {path_tok!r} appears in main.tex")

    if "**" in tex:
        errors.append("Formatting error: raw Markdown '**' found in main.tex")

    # 2. Headline corpus, recall, and longitudinal claims
    _must_match("Total 15-cat corpus", rf"\b{gt['total_papers']:,}\b")
    _must_match("Full-text screened", rf"\b{gt['fulltext_screened']:,}\b")
    _must_match("Full-text coverage %", rf"\b{gt['fulltext_coverage_pct']:.2f}%")
    _must_match("Stage-2 pruned %", rf"\b{gt['stage2_pruned_pct']:.1f}%")
    _must_match("Metadata recall ratio", rf"{gt['fulltext_vs_meta_recall_ratio']:.1f}\$\\times\$")
    _must_match("T0 v1 0/N", rf"0/{t0['total_papers']:,}\s*\(0\.00%")
    _must_match("T0 95% UB", rf"{t0['confirmed_v1']['ci_95_pct'][1]:.2f}%")
    _must_match("T1 v1 k/N", rf"{t1['confirmed_v1']['count']}/{t1['total_papers']:,}\s*\({t1['confirmed_v1']['pct']:.2f}%")
    _must_match("T2 v1 k/N", rf"{t2['confirmed_v1']['count']}/{t2['total_papers']:,}\s*\({t2['confirmed_v1']['pct']:.2f}%")
    _must_match("T1 Wilson CI", rf"\[{t1['confirmed_v1']['ci_95_pct'][0]:.2f}%,\s*{t1['confirmed_v1']['ci_95_pct'][1]:.2f}%\]")
    _must_match("T2 Wilson CI", rf"\[{t2['confirmed_v1']['ci_95_pct'][0]:.2f}%,\s*{t2['confirmed_v1']['ci_95_pct'][1]:.2f}%\]")
    _must_match("Pooled 6-mo multiplier", rf"{mult['pooled_v1_t2_over_t1']:.1f}\$\\times\$")
    _must_match("Pooled YoY v_latest multiplier", rf"{mult['pooled_v_latest_t2_over_t0']:.2f}\$\\times\$")
    _must_match("Eng. Alg. 6-mo multiplier", rf"{mult['eng_alg_v1_t2_over_t1']:.2f}\$\\times\$")
    _must_match("Eng. Alg. T2 Wilson CI", rf"\[{t2['roles_v1']['eng_algorithmic_proof']['ci_95_pct'][0]:.2f}%,\s*{t2['roles_v1']['eng_algorithmic_proof']['ci_95_pct'][1]:.2f}%\]")
    _must_match("Pure math/TCS 6-mo multiplier", rf"{mult['pure_math_tcs_v1_t2_over_t1']:.2f}\$\\times\$")

    # 3. Recall calibration
    _must_match("Recall T2 negatives", rf"\b{rc['total_t2_stage2_negatives']:,}\b")
    _must_match("Recall 0/250", rf"{rc['confirmed_missed_lean_contributions']}/{rc['gh_sample_size']}\b")
    _must_match("Recall 410 repos", rf"\b{rc['gh_unique_repos_checked']}\b")
    _must_match("Recall 95% UB", rf"\b{rc['confirmed_fn_95pct_upper_bound_pct']:.2f}%")
    _must_match("Recall acc 95% UB", rf"\b{rc['confirmed_acc_fn_95pct_upper_bound_pct']:.2f}%")
    _must_match("Recall non-GH 0/125", rf"{rc['non_gh_broad_meta_flags']}/{rc['non_gh_sample_size']}\b")

    # 4. Complete eess.* & Off-arXiv
    _must_match("Complete eess.* 3-slice", rf"\b{gt['complete_eess_3slice_unique_papers']:,}\b")
    nc3 = gt["eess_non_sy_3slice_confirmed_v1"]
    _must_match("Non-control eess.* 3-slice", rf"{nc3['count']}/{nc3['total']:,}\s*\({nc3['pct']:.2f}%")
    _must_match("TechRxiv+engrXiv 0/10,511", rf"0/{oa['preprint_servers']['combined']['total_records_2025_2026']:,}")
    _must_match("Off-arXiv 95% UB", rf"{oa['preprint_servers']['combined']['confirmed_95pct_ub_pct']:.3f}%")
    _must_match("OpenAlex Engineering share", rf"{oa['openalex']['engineering_field_22']['mathlib_share_of_all_mathlib_pct']:.2f}%")

    # 5. Scale, AI, Gold
    _must_match("Pooled owned LoC 8.14M", rf"{t2['confirmed_v1']['total_owned_loc'] / 1e6:.2f}\s*million")
    _must_match("Pooled median LoC jump", rf"{mult['pooled_median_loc_t2_over_t1']:.1f}\$\\times\$")
    _must_match("Eng. Alg. median LoC jump", rf"{mult['eng_alg_median_loc_t2_over_t1']:.1f}\$\\times\$")
    ai_t2_pct = 100.0 * t2["confirmed_v1"]["ai_assistance"]["explicitly_yes"] / t2["confirmed_v1"]["count"]
    gold_t2_pct = 100.0 * t2["confirmed_v1"]["tiers"]["Tier3_Gold"] / t2["confirmed_v1"]["count"]
    _must_match("T2 AI disclosure %", rf"{ai_t2_pct:.1f}%")
    _must_match("T2 Gold tier %", rf"{gold_t2_pct:.1f}%")

    # 6. Dynamic sandbox
    _must_match("Sandbox 18/23 (78.3%)", rf"{ov['pass_out_of_box']}/{ov['total_attempted']}\s*\({ov['pass_out_of_box_pct']:.1f}%")
    _must_match("Sandbox OOTB theorems", rf"\b{ov['total_theorems_checked_ootb']:,}\b")
    _must_match("Sandbox total incl synth theorems", rf"\b{ov['total_theorems_checked_incl_synthetic']:,}\b")
    _must_match("Sandbox Gold axiom-clean", rf"{ov['tier3_gold_clean_axioms']}/{ov['tier3_gold_pass_out_of_box']}")
    _must_match("Sandbox distinct toolchains", rf"\b{ov['distinct_pinned_toolchains_count']} distinct Lean 4 toolchains")
    _must_match("Sandbox 0/23 compile fails", rf"0/{ov['total_attempted']} suffer genuine Lean proof")

    # 7. Layer-A, OpFV & Human Validation
    eng_la = la["summary"]["eng_algorithmic_proof_all"]
    _must_match("Layer-A 0/22 eng drift", rf"0/{eng_la['count']}\b")
    _must_match("Layer-A 274/274 refs", rf"{la['resolved_file_line_refs']}/{la['total_file_line_refs']}")
    _must_match("OpFV 8/8 refinement", rf"{opfv['opfv1_refinement_gap_present']}/{opfv['total_operational_fv_papers']}")
    _must_match("OpFV 4/8 liveness", rf"{opfv['opfv3_no_mechanized_lean_liveness']}/{opfv['total_operational_fv_papers']}")
    _must_match("OpFV 5/8 TCB", rf"{opfv['opfv4_extraction_monitor_or_cross_kernel_tcb_gap']}/{opfv['total_operational_fv_papers']}")
    hc = hv["layer_a_human_co_review"]
    _must_match(
        f"Human co-review {hc['named_critiques_reviewed']}/{hc['named_critiques_reviewed']} critiques",
        rf"{hc['named_critiques_reviewed']}/{hc['named_critiques_reviewed']}",
    )
    _must_match(
        f"Human co-review {hc['clean_spot_checks_reviewed']}/{hc['clean_spot_checks_reviewed']} spot-checks",
        rf"{hc['clean_spot_checks_reviewed']}/{hc['clean_spot_checks_reviewed']}",
    )
    _must_match(
        f"Human co-review {hc['total_reviewed']} total Stage-5 repos",
        rf"\b{hc['total_reviewed']}\s+Stage-5",
    )

    return errors


def run_all_checks(
    tex_path: Path = DEFAULT_TEX,
    panel_path: Path = DEFAULT_PANEL,
) -> tuple[list[str], dict[str, Any]]:
    tex = strip_tex_comments(tex_path.read_text(encoding="utf-8"))
    panel = json.loads(panel_path.read_text(encoding="utf-8"))

    errors: list[str] = []
    errors.extend(check_table_longitudinal_15cat(tex, panel))
    errors.extend(check_table_categories_15cat(tex, panel))
    errors.extend(check_table_off_arxiv(tex, panel))
    errors.extend(check_table_distributions_15cat(tex, panel))

    eng_meta = [
        p for p in panel["confirmed_papers"]
        if p["role_4way"] in ("eng_algorithmic_proof", "meta_formalization_system")
    ]
    errors.extend(_check_paper_ledger_table(tex, "tab:inventory_eng", eng_meta))
    errors.extend(_check_paper_ledger_table(tex, "tab:master_ledger", panel["confirmed_papers"]))
    errors.extend(check_table_sandbox_unified(tex, panel))
    errors.extend(check_table_stage4_irr(tex, panel))
    errors.extend(check_prose_and_style(tex, panel))

    t2 = next(s for s in panel["slices"] if s["short_id"] == "T2")
    stats = {
        "total_papers": panel["grand_totals"]["total_papers"],
        "t2_confirmed_v1": t2["confirmed_v1"]["count"],
        "t2_scanned_owned_repos": t2["confirmed_v1"]["scanned_owned_repos"],
        "inventory_eng_rows": len(eng_meta),
        "master_ledger_rows": len(panel["confirmed_papers"]),
        "sandbox_repos": panel["sandbox_builds"]["overall"]["total_attempted"],
        "layer_a_audited": panel["layer_a_audits"]["total_audited"],
    }
    return errors, stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify paper numeric & scholarly-style consistency against unified_15cat_panel.json.")
    ap.add_argument("--tex", type=Path, default=DEFAULT_TEX)
    ap.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    args = ap.parse_args()

    errors, stats = run_all_checks(tex_path=args.tex, panel_path=args.panel)
    if errors:
        print(f"Paper numeric consistency FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(
        "Paper numeric consistency PASSED (0 issues): "
        f"N={stats['total_papers']:,} (15 cats), T2 v1={stats['t2_confirmed_v1']} "
        f"({stats['t2_scanned_owned_repos']} scanned), Eng+Meta table={stats['inventory_eng_rows']}, "
        f"Master ledger={stats['master_ledger_rows']}, Sandbox={stats['sandbox_repos']}, "
        f"Layer-A={stats['layer_a_audited']}."
    )


if __name__ == "__main__":
    main()
