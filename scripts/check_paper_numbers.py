#!/usr/bin/env python3
"""Programmatic numeric consistency gate for `papers/arxiv-empirical/main.tex`.

Verifies every bolded count, percentage, confidence interval, LoC aggregate,
table cell, and per-paper inventory row in `papers/arxiv-empirical/main.tex`
against the version-controlled JSON artifacts:
  - `artifacts/longitudinal_summary.json`
  - `artifacts/slices/*/figure_inputs.json`
  - `artifacts/slices/2026-11/recall_calibration.json`
  - `artifacts/phase2_provenance.json`

Exit code 0 if every check passes; non-zero with exact expected-vs-found diffs
if any number drifts across edits.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEX = REPO_ROOT / "papers" / "arxiv-empirical" / "main.tex"
DEFAULT_LONGITUDINAL = REPO_ROOT / "artifacts" / "longitudinal_summary.json"
DEFAULT_SLICES_DIR = REPO_ROOT / "artifacts" / "slices"
DEFAULT_PROVENANCE = REPO_ROOT / "artifacts" / "phase2_provenance.json"

# Multi-paper monorepos whose inventory LoC reports paper-specific subpackage LoC (*).
SUBPACKAGE_IDS = {"2611.09050", "2611.13584", "2611.15128"}

# Cited third-party/sibling/mirror repos excluded from raw primary repo LoC sum.
SKIP_CITED_REPOS = {
    "anthropics/fermats-last-theorem",
    "cameronfreer/lean4-skills",
    "oOo0oOo/lean-lsp-mcp",
    "leanprover/comparator",
    "optsuite/optlib",
    "MColbrook/AIM",
    "forgi86/control-theory-in-lean",
    "TauCetiProject/TauCeti",
    "ywatanabex/bp-degree-syzygies-lean",
    "zenodo/22643866",
    "zenodo/24118844",
}

ROLE_SHORT = {
    "engineering_math_proof": "Eng",
    "software_or_system_fv": "Sys",
    "pure_tcs_or_math": "TCS",
}
TIER_SHORT = {
    "Tier3_Gold": "T3",
    "Tier2_Silver": "T2",
    "Tier1_Bronze": "T1",
}
AI_SHORT = {
    "explicitly_yes": "Yes",
    "unclear": "Unc",
    "explicitly_no": "No",
}
RISK_SHORT = {
    "Mode2_ScopeDowngrade": "M2",
    "Mode3_CustomDefs": "M3",
    "Mode6_SorryOrAxiomOrNativeDecide": "M6",
    "Mode10_ProofBloat": "M10",
    "Mode12_ProcessOpacity": "M12",
}


def strip_tex_comments(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in tex.splitlines())


def clean_tex_cell(cell: str) -> str:
    s = cell.strip()
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    s = s.replace(r"\%", "%").replace("~", " ").replace(r"\,", "")
    s = s.replace("{,}", ",")
    return re.sub(r"\s+", " ", s).strip()


def parse_int(text: str) -> int:
    m = re.search(r"[\d,]+", text)
    if not m:
        raise ValueError(f"No integer in {text!r}")
    return int(m.group(0).replace(",", ""))


def clopper_pearson_upper_pct(n: int, alpha: float = 0.05) -> float:
    return 100.0 * (1.0 - alpha ** (1.0 / n))


def extract_table_by_label(tex: str, label: str) -> str:
    """Return the tabular/tabularx body of the table containing \\label{<label>}."""
    for m in re.finditer(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", tex, flags=re.DOTALL):
        block = m.group(0)
        if f"\\label{{{label}}}" in block:
            tm = re.search(r"\\begin\{tabularx?\}.*?\\end\{tabularx?\}", block, flags=re.DOTALL)
            if tm:
                return tm.group(0)
    raise ValueError(f"Table with \\label{{{label}}} not found in LaTeX source")


def split_tabular_rows(tabular_block: str) -> list[list[str]]:
    """Split a LaTeX tabular body into rows of cells (skipping rules/headers)."""
    # Strip \begin{tabular...}{...} and \end{tabular...}
    body = re.sub(r"^\\begin\{tabularx?\}(?:\{[^}]*\})?\{.*?\}\n", "", tabular_block, count=1, flags=re.DOTALL)
    body = re.sub(r"\\end\{tabularx?\}\s*$", "", body, flags=re.DOTALL)
    rows: list[list[str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("\\toprule", "\\midrule", "\\bottomrule", "\\multicolumn")):
            continue
        if r"\\" not in line:
            continue
        line = line.split(r"\\")[0].strip()
        if not line:
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)&", line)]
        rows.append(cells)
    return rows


def compute_raw_primary_repo_stats(fig_inputs: dict[str, Any]) -> tuple[int, int, int]:
    """Return (unique_primary_repos, papers_with_primary_repo, total_raw_primary_loc) from figure_inputs."""
    unique_repos: dict[str, int] = {}
    papers_scanned = 0
    for p in fig_inputs.get("confirmed_lean_papers", []):
        owned = [
            rp
            for rp in p.get("lean_repos", [])
            if rp.get("lean_file_count", 0) > 0
            and rp.get("repo") not in SKIP_CITED_REPOS
            and rp.get("loc_nonempty", 0) > 0
        ]
        if not owned:
            continue
        best = max(owned, key=lambda rp: rp.get("loc_nonempty", 0))
        papers_scanned += 1
        unique_repos[best["repo"]] = max(unique_repos.get(best["repo"], 0), int(best["loc_nonempty"]))
    return len(unique_repos), papers_scanned, sum(unique_repos.values())


def check_cross_artifact_consistency(
    longit: dict[str, Any],
    fig_inputs_by_slice: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    slices_by_id = {s["short_id"]: s for s in longit["slices"]}
    t2 = slices_by_id["T2"]
    fig = fig_inputs_by_slice.get("2026-11")
    if fig is None:
        return ["Missing artifacts/slices/2026-11/figure_inputs.json"]

    funnel = fig["funnel"]
    pairs = [
        ("funnel.total_papers", funnel["total_papers"], t2["total_papers"]),
        ("funnel.screened", funnel["screened"], t2["screened_ok"]),
        ("funnel.candidates", funnel["candidates"], t2["stage2_lean_candidates"]),
        ("funnel.negatives", funnel["negatives"], t2["screened_ok"] - t2["stage2_lean_candidates"]),
        ("funnel.confirmed", funnel["confirmed"], t2["v1"]["count"]),
        ("funnel.eng_math", funnel["eng_math"], t2["v1"]["eng_math_count"]),
        ("funnel.audited", funnel["audited"], len(t2["audits"])),
    ]
    for name, a, b in pairs:
        if a != b:
            errors.append(f"Cross-artifact mismatch ({name}): figure_inputs={a} vs longitudinal_summary={b}")

    bif = fig["category_bifurcation"]
    for cat, total in t2["cat_total"].items():
        if bif["cat_total"].get(cat) != total:
            errors.append(
                f"Cross-artifact mismatch (cat_total[{cat}]): figure_inputs={bif['cat_total'].get(cat)} vs longitudinal={total}"
            )
        fig_lean = sum(bif["cat_role"].get(cat, {}).values())
        long_lean = t2["v1"]["cat_lean"].get(cat, 0)
        if fig_lean != long_lean:
            errors.append(f"Cross-artifact mismatch (cat_lean[{cat}]): figure_inputs={fig_lean} vs longitudinal={long_lean}")
        fig_eng = bif["cat_role"].get(cat, {}).get("engineering_math_proof", 0)
        long_eng = t2["v1"]["cat_eng"].get(cat, 0)
        if fig_eng != long_eng:
            errors.append(f"Cross-artifact mismatch (cat_eng[{cat}]): figure_inputs={fig_eng} vs longitudinal={long_eng}")

    _, fig_papers_scanned, fig_raw_loc = compute_raw_primary_repo_stats(fig)
    if fig_papers_scanned != t2["v1"]["scanned_owned_repos"]:
        errors.append(
            f"Cross-artifact mismatch (T2 scanned_owned_repos): figure_inputs={fig_papers_scanned} "
            f"vs longitudinal_summary={t2['v1']['scanned_owned_repos']}"
        )
    if "raw_primary_total_loc" in t2["v1"] and fig_raw_loc != t2["v1"]["raw_primary_total_loc"]:
        errors.append(
            f"Cross-artifact mismatch (T2 raw_primary_total_loc): figure_inputs={fig_raw_loc} "
            f"vs longitudinal_summary={t2['v1']['raw_primary_total_loc']}"
        )

    return errors


def check_table_categories(tex: str, t2: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:categories")
    rows = split_tabular_rows(tab)
    seen_cats: set[str] = set()

    for cells in rows:
        if len(cells) < 5:
            continue
        col0 = clean_tex_cell(cells[0])
        if col0.startswith("Category"):
            continue
        if col0.startswith("Deduplicated Union"):
            exp_n = t2["total_papers"]
            exp_k = t2["v1"]["count"]
            exp_pct = f"{t2['v1']['pct']:.2f}%"
            exp_eng = t2["v1"]["eng_math_count"]
            got_n, got_k, got_pct, got_eng = (
                parse_int(clean_tex_cell(cells[1])),
                parse_int(clean_tex_cell(cells[2])),
                clean_tex_cell(cells[3]),
                parse_int(clean_tex_cell(cells[4])),
            )
            if (got_n, got_k, got_pct, got_eng) != (exp_n, exp_k, exp_pct, exp_eng):
                errors.append(
                    f"tab:categories [Union]: got ({got_n}, {got_k}, {got_pct}, {got_eng}) "
                    f"!= expected ({exp_n}, {exp_k}, {exp_pct}, {exp_eng})"
                )
            continue
        if col0.startswith("Excl."):
            exp_n = t2["non_tcs_total"]
            exp_k = t2["v1"]["non_tcs_count"]
            exp_pct = f"{t2['v1']['non_tcs_pct']:.2f}%"
            got_n, got_k, got_pct = (
                parse_int(clean_tex_cell(cells[1])),
                parse_int(clean_tex_cell(cells[2])),
                clean_tex_cell(cells[3]),
            )
            if (got_n, got_k, got_pct) != (exp_n, exp_k, exp_pct):
                errors.append(
                    f"tab:categories [Non-TCS]: got ({got_n}, {got_k}, {got_pct}) "
                    f"!= expected ({exp_n}, {exp_k}, {exp_pct})"
                )
            continue

        m = re.match(r"([a-z]+\.[A-Z]{2})\b", col0)
        if not m:
            continue
        cat = m.group(1)
        seen_cats.add(cat)
        exp_n = t2["cat_total"][cat]
        exp_k = t2["v1"]["cat_lean"].get(cat, 0)
        exp_pct = f"{100.0 * exp_k / exp_n:.2f}%"
        exp_eng = t2["v1"]["cat_eng"].get(cat, 0)
        got_n, got_k, got_pct, got_eng = (
            parse_int(clean_tex_cell(cells[1])),
            parse_int(clean_tex_cell(cells[2])),
            clean_tex_cell(cells[3]),
            parse_int(clean_tex_cell(cells[4])),
        )
        if (got_n, got_k, got_pct, got_eng) != (exp_n, exp_k, exp_pct, exp_eng):
            errors.append(
                f"tab:categories [{cat}]: got ({got_n}, {got_k}, {got_pct}, {got_eng}) "
                f"!= expected ({exp_n}, {exp_k}, {exp_pct}, {exp_eng})"
            )

    missing_cats = set(t2["cat_total"]) - seen_cats
    if missing_cats:
        errors.append(f"tab:categories missing categories: {sorted(missing_cats)}")
    return errors


def check_table_distributions(tex: str, t2: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:distributions")
    rows = split_tabular_rows(tab)
    v1 = t2["v1"]
    n_conf = v1["count"]

    def _expect_count_pct(label_name: str, cell_text: str, expected_cnt: int) -> None:
        exp = f"{expected_cnt} ({100.0 * expected_cnt / n_conf:.1f}%)"
        got = clean_tex_cell(cell_text)
        if got != exp:
            errors.append(f"tab:distributions [{label_name}]: got {got!r} != expected {exp!r}")

    key_map = {
        "P1_paper_first_posthoc": ("paradigms", "P1_paper_first_posthoc"),
        "P0_opaque_or_unspecified": ("paradigms", "P0_opaque_or_unspecified"),
        "P4_speclock_solve_distill": ("paradigms", "P4_speclock_solve_distill"),
        "engineering_math_proof": ("roles", "engineering_math_proof"),
        "pure_tcs_or_math": ("roles", "pure_tcs_or_math"),
        "software_or_system_fv": ("roles", "software_or_system_fv"),
        "Tier3_Gold": ("tiers", "Tier3_Gold"),
        "Tier2_Silver": ("tiers", "Tier2_Silver"),
        "Tier1_Bronze": ("tiers", "Tier1_Bronze"),
        "Mode12_ProcessOpacity": ("risks", "Mode12_ProcessOpacity"),
        "Mode10_ProofBloat": ("risks", "Mode10_ProofBloat"),
        "Mode2_ScopeDowngrade": ("risks", "Mode2_ScopeDowngrade"),
        "Mode6_SorryOrAxiomOrNativeDecide": ("risks", "Mode6_SorryOrAxiomOrNativeDecide"),
        "Mode3_CustomDefs": ("risks", "Mode3_CustomDefs"),
    }

    for cells in rows:
        if len(cells) < 3:
            continue
        dim = clean_tex_cell(cells[0])
        cat_col = clean_tex_cell(cells[1]).replace(r"\_", "_")
        val_col = clean_tex_cell(cells[2])

        if "P2_lean_first" in cat_col and "P3_blueprint_sync" in cat_col:
            exp_p23 = v1["paradigms"].get("P2_lean_first", 0) + v1["paradigms"].get("P3_blueprint_sync", 0)
            _expect_count_pct("P2/P3", val_col, exp_p23)
            continue

        matched_key = False
        for tok, (bucket, field) in key_map.items():
            if tok in cat_col:
                _expect_count_pct(tok, val_col, v1[bucket].get(field, 0))
                matched_key = True
                break
        if matched_key:
            continue

        if "AI Assistance" in dim:
            exp_ai = (
                f"{v1['ai'].get('explicitly_yes', 0)} / "
                f"{v1['ai'].get('unclear', 0)} / "
                f"{v1['ai'].get('explicitly_no', 0)}"
            )
            if val_col != exp_ai:
                errors.append(f"tab:distributions [AI Assistance]: got {val_col!r} != expected {exp_ai!r}")
        elif "Artifact Status" in dim:
            art = v1["artifacts"]
            exp_art = (
                f"{art.get('public_lean_repo', 0)} / "
                f"{art.get('appendix_only', 0)} / "
                f"{art.get('broken_or_missing_repo', 0)} / "
                f"{art.get('none', 0)}"
            )
            if val_col != exp_art:
                errors.append(f"tab:distributions [Artifact Status]: got {val_col!r} != expected {exp_art!r}")
            # Also check parenthetical breakdown of scanned vs ext/zip if present
            m_sc = re.search(r"(\d+)\s+scanned,\s+(\d+)\s+ext", cat_col)
            if m_sc:
                got_sc, got_ext = int(m_sc.group(1)), int(m_sc.group(2))
                # Count how many public_lean_repo papers have scanned primary_owned_loc vs unprofiled
                pub_scanned = sum(
                    1
                    for p in t2["confirmed_papers"]
                    if p["artifact_availability"] == "public_lean_repo" and p["primary_owned_loc"]
                )
                pub_unscanned = art.get("public_lean_repo", 0) - pub_scanned
                if (got_sc, got_ext) != (pub_scanned, pub_unscanned):
                    errors.append(
                        f"tab:distributions [Artifact Status public_lean_repo breakdown]: "
                        f"got ({got_sc} scanned, {got_ext} ext) != expected ({pub_scanned} scanned, {pub_unscanned} ext)"
                    )

    return errors


def check_table_inventory(tex: str, t2: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:inventory")
    rows = split_tabular_rows(tab)
    by_id = {p["arxiv_id"]: p for p in t2["confirmed_papers"]}
    seen_ids: set[str] = set()

    for cells in rows:
        if len(cells) < 8:
            continue
        aid = clean_tex_cell(cells[0])
        if not re.match(r"^\d{4}\.\d{5}$", aid):
            continue
        seen_ids.add(aid)
        if aid not in by_id:
            errors.append(f"tab:inventory: unknown arXiv ID {aid} not in longitudinal_summary T2 confirmed_papers")
            continue
        p = by_id[aid]

        got_role = clean_tex_cell(cells[2])
        exp_role = ROLE_SHORT[p["paper_domain_role"]]
        if got_role != exp_role:
            errors.append(f"tab:inventory [{aid}] Role: got {got_role!r} != expected {exp_role!r}")

        got_par = clean_tex_cell(cells[3])
        exp_par = p["authoring_paradigm"].split("_")[0]
        if got_par != exp_par:
            errors.append(f"tab:inventory [{aid}] Paradigm: got {got_par!r} != expected {exp_par!r}")

        got_tier = clean_tex_cell(cells[4])
        exp_tier = TIER_SHORT[p["verification_tier"]]
        if got_tier != exp_tier:
            errors.append(f"tab:inventory [{aid}] Tier: got {got_tier!r} != expected {exp_tier!r}")

        got_ai = clean_tex_cell(cells[5])
        exp_ai = AI_SHORT[p["ai_agent_assisted"]]
        if got_ai != exp_ai:
            errors.append(f"tab:inventory [{aid}] AI: got {got_ai!r} != expected {exp_ai!r}")

        raw_loc_cell = cells[6].strip()
        exp_loc = p["primary_owned_loc"]
        if exp_loc is not None:
            exp_loc_str = f"{exp_loc:,}" + ("*" if aid in SUBPACKAGE_IDS else "")
            got_loc_str = clean_tex_cell(raw_loc_cell)
            if got_loc_str != exp_loc_str:
                errors.append(f"tab:inventory [{aid}] LoC: got {got_loc_str!r} != expected {exp_loc_str!r}")
        else:
            if not (r"\textemdash" in raw_loc_cell or "ext" in clean_tex_cell(raw_loc_cell)):
                errors.append(
                    f"tab:inventory [{aid}] LoC: got {raw_loc_cell!r} but primary_owned_loc is null in artifacts"
                )

        got_risks_txt = clean_tex_cell(cells[7])
        got_risks = set() if got_risks_txt == "none" else {x.strip() for x in got_risks_txt.split(",") if x.strip()}
        exp_risks = {RISK_SHORT[r] for r in p.get("static_risk_flags", [])}
        if got_risks != exp_risks:
            errors.append(f"tab:inventory [{aid}] Risks: got {sorted(got_risks)} != expected {sorted(exp_risks)}")

    missing = sorted(set(by_id) - seen_ids)
    if missing:
        errors.append(f"tab:inventory missing confirmed T2 papers: {missing}")
    if len(seen_ids) != len(by_id):
        errors.append(f"tab:inventory row count={len(seen_ids)} != expected {len(by_id)}")
    return errors


def check_table_longitudinal(tex: str, slices: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:longitudinal")
    rows = split_tabular_rows(tab)
    t0, t1, t2 = slices["T0"], slices["T1"], slices["T2"]

    def _row_by_prefix(prefix: str) -> list[str] | None:
        for r in rows:
            if clean_tex_cell(r[0]).startswith(prefix):
                return [clean_tex_cell(c) for c in r]
        return None

    def _chk(row_name: str, idx: int, expected: str) -> None:
        row = _row_by_prefix(row_name)
        if row is None:
            errors.append(f"tab:longitudinal missing row starting with {row_name!r}")
            return
        if row[idx] != expected:
            errors.append(f"tab:longitudinal [{row_name}][col {idx}]: got {row[idx]!r} != expected {expected!r}")

    _chk("Corpus size", 1, f"{t0['total_papers']:,}")
    _chk("Corpus size", 2, f"{t1['total_papers']:,}")
    _chk("Corpus size", 3, f"{t2['total_papers']:,}")
    growth_6m = 100.0 * (t2["total_papers"] - t1["total_papers"]) / t1["total_papers"]
    growth_12m = 100.0 * (t2["total_papers"] - t0["total_papers"]) / t0["total_papers"]
    row_corp = _row_by_prefix("Corpus size")
    if row_corp:
        for tok in (f"+{growth_6m:.1f}%", f"+{growth_12m:.1f}%"):
            if tok not in row_corp[4]:
                errors.append(f"tab:longitudinal [Corpus size][Shift]: missing {tok!r} in {row_corp[4]!r}")

    _chk("Full-text coverage", 1, f"{t0['coverage_pct']:.2f}%")
    _chk("Full-text coverage", 2, f"{t1['coverage_pct']:.2f}%")
    _chk("Full-text coverage", 3, f"{t2['coverage_pct']:.2f}%")

    _chk("Later-revised preprints", 1, f"{t0['revised_v_gt_1']:,} ({t0['revised_pct']:.1f}%)")
    _chk("Later-revised preprints", 2, f"{t1['revised_v_gt_1']:,} ({t1['revised_pct']:.1f}%)")
    _chk("Later-revised preprints", 3, f"{t2['revised_v_gt_1']:,} ({t2['revised_pct']:.1f}%)")

    _chk("Stage-2 Beyond-Lean", 1, f"{t0['stage2_beyond_any']} ({t0['stage2_beyond_any_pct']:.2f}%)")
    _chk("Stage-2 Beyond-Lean", 2, f"{t1['stage2_beyond_any']} ({t1['stage2_beyond_any_pct']:.2f}%)")
    _chk("Stage-2 Beyond-Lean", 3, f"{t2['stage2_beyond_any']} ({t2['stage2_beyond_any_pct']:.2f}%)")

    _chk("Stage-2 Lean candidates", 1, f"{t0['stage2_lean_candidates']} ({t0['stage2_lean_cand_pct']:.2f}%)")
    _chk("Stage-2 Lean candidates", 2, f"{t1['stage2_lean_candidates']} ({t1['stage2_lean_cand_pct']:.2f}%)")
    _chk("Stage-2 Lean candidates", 3, f"{t2['stage2_lean_candidates']} ({t2['stage2_lean_cand_pct']:.2f}%)")

    _chk("Confirmed Lean (v1 contemp.)", 1, f"{t0['v1']['count']} ({t0['v1']['pct']:.2f}%)")
    _chk("Confirmed Lean (v1 contemp.)", 2, f"{t1['v1']['count']} ({t1['v1']['pct']:.2f}%)")
    _chk("Confirmed Lean (v1 contemp.)", 3, f"{t2['v1']['count']} ({t2['v1']['pct']:.2f}%)")
    v1_mult = t2["v1"]["pct"] / t1["v1"]["pct"]
    row_v1 = _row_by_prefix("Confirmed Lean (v1 contemp.)")
    if row_v1 and f"{v1_mult:.1f}" not in row_v1[4]:
        errors.append(f"tab:longitudinal [Confirmed Lean v1][Shift]: expected {v1_mult:.1f}x in {row_v1[4]!r}")

    _chk("Confirmed Lean (v\\_latest)", 1, f"{t0['v_latest']['count']} ({t0['v_latest']['pct']:.2f}%)")
    _chk("Confirmed Lean (v\\_latest)", 2, f"{t1['v_latest']['count']} ({t1['v_latest']['pct']:.2f}%)")
    _chk("Confirmed Lean (v\\_latest)", 3, f"{t2['v_latest']['count']} ({t2['v_latest']['pct']:.2f}%)")

    _chk("engineering\\_math\\_proof", 1, f"{t0['v1']['eng_math_count']} / {t0['v_latest']['eng_math_count']}")
    _chk("engineering\\_math\\_proof", 2, f"{t1['v1']['eng_math_count']} / {t1['v_latest']['eng_math_count']}")
    _chk("engineering\\_math\\_proof", 3, f"{t2['v1']['eng_math_count']}")

    t2_oc_cnt = t2["v1"]["cat_lean"].get("math.OC", 0)
    t2_oc_pct = 100.0 * t2_oc_cnt / t2["cat_total"]["math.OC"]
    t1_oc_vlat_pct = 100.0 * t1["v_latest"]["cat_lean"].get("math.OC", 0) / t1["cat_total"]["math.OC"]
    _chk("math.OC Lean", 1, "0.00%")
    _chk("math.OC Lean", 2, f"0.00% / {t1_oc_vlat_pct:.2f}%")
    _chk("math.OC Lean", 3, f"{t2_oc_pct:.2f}% ({t2_oc_cnt})")

    # AI disclosure
    t1_ai = t1["v1"]["ai"]
    t2_ai = t2["v1"]["ai"]
    t1_ai_pct = 100.0 * t1_ai.get("explicitly_yes", 0) / t1["v1"]["count"]
    t2_ai_pct = 100.0 * t2_ai.get("explicitly_yes", 0) / t2["v1"]["count"]
    _chk(
        "Explicit AI disclosure",
        2,
        f"{t1_ai.get('explicitly_yes',0)} / {t1_ai.get('unclear',0)} / {t1_ai.get('explicitly_no',0)} ({t1_ai_pct:.0f}%)",
    )
    _chk(
        "Explicit AI disclosure",
        3,
        f"{t2_ai.get('explicitly_yes',0)} / {t2_ai.get('unclear',0)} / {t2_ai.get('explicitly_no',0)} ({t2_ai_pct:.1f}%)",
    )

    # Paradigms P1/P2/P3/P4/P0
    for col_idx, sl in ((2, t1), (3, t2)):
        pm = sl["v1"]["paradigms"]
        exp_p = (
            f"{pm.get('P1_paper_first_posthoc',0)}/{pm.get('P2_lean_first',0)}/"
            f"{pm.get('P3_blueprint_sync',0)}/{pm.get('P4_speclock_solve_distill',0)}/"
            f"{pm.get('P0_opaque_or_unspecified',0)}"
        )
        _chk("Paradigms v1", col_idx, exp_p)

    # Tiers Gold/Silver/Bronze
    for col_idx, sl in ((2, t1), (3, t2)):
        tm = sl["v1"]["tiers"]
        exp_t = f"{tm.get('Tier3_Gold',0)} / {tm.get('Tier2_Silver',0)} / {tm.get('Tier1_Bronze',0)}"
        _chk("Tiers v1", col_idx, exp_t)
    gold_pct_t2 = 100.0 * t2["v1"]["tiers"].get("Tier3_Gold", 0) / t2["v1"]["count"]
    row_tiers = _row_by_prefix("Tiers v1")
    if row_tiers and f"{gold_pct_t2:.1f}%" not in row_tiers[4]:
        errors.append(f"tab:longitudinal [Tiers v1][Shift]: expected Gold {gold_pct_t2:.1f}% in {row_tiers[4]!r}")

    # Median & total paper-owned LoC
    _chk("Median paper-owned LoC", 2, f"{t1['v1']['median_owned_loc']:,} ($n={t1['v1']['scanned_owned_repos']}$)")
    _chk("Median paper-owned LoC", 3, f"{t2['v1']['median_owned_loc']:,} ($n={t2['v1']['scanned_owned_repos']}$)")
    loc_mult = t2["v1"]["median_owned_loc"] / t1["v1"]["median_owned_loc"]
    row_med = _row_by_prefix("Median paper-owned LoC")
    if row_med and f"{loc_mult:.1f}" not in row_med[4]:
        errors.append(f"tab:longitudinal [Median paper-owned LoC][Shift]: expected {loc_mult:.1f}x in {row_med[4]!r}")

    _chk("Total paper-owned LoC", 2, f"{t1['v1']['total_owned_loc']:,}")
    _chk("Total paper-owned LoC", 3, f"{t2['v1']['total_owned_loc']:,}")
    row_tot = _row_by_prefix("Total paper-owned LoC")
    exp_tot_m = f"{t2['v1']['total_owned_loc'] / 1e6:.2f}M"
    if row_tot and exp_tot_m not in row_tot[4]:
        errors.append(f"tab:longitudinal [Total paper-owned LoC][Shift]: expected {exp_tot_m!r} in {row_tot[4]!r}")

    return errors


def check_prose_and_bolded_claims(
    tex: str,
    slices: dict[str, dict[str, Any]],
    fig_inputs: dict[str, Any],
    recall_cal: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    t0, t1, t2 = slices["T0"], slices["T1"], slices["T2"]

    tot_papers = t0["total_papers"] + t1["total_papers"] + t2["total_papers"]
    tot_screened = t0["screened_ok"] + t1["screened_ok"] + t2["screened_ok"]
    tot_cov = 100.0 * tot_screened / tot_papers

    t0_ub = clopper_pearson_upper_pct(t0["total_papers"])
    t1_lo, t1_hi = t1["v1"]["wilson_95"]
    t2_lo, t2_hi = t2["v1"]["wilson_95"]

    v1_jump = t2["v1"]["pct"] / t1["v1"]["pct"]
    med_jump = t2["v1"]["median_owned_loc"] / t1["v1"]["median_owned_loc"]
    ai_t1_pct = 100.0 * t1["v1"]["ai"].get("explicitly_yes", 0) / t1["v1"]["count"]
    ai_t2_pct = 100.0 * t2["v1"]["ai"].get("explicitly_yes", 0) / t2["v1"]["count"]
    gold_t2_pct = 100.0 * t2["v1"]["tiers"].get("Tier3_Gold", 0) / t2["v1"]["count"]
    opacity_t2 = t2["v1"]["risks"].get("Mode12_ProcessOpacity", 0)
    opacity_t2_pct = 100.0 * opacity_t2 / t2["v1"]["count"]

    n_uniq_repos, n_papers_scanned, raw_loc = compute_raw_primary_repo_stats(fig_inputs)
    raw_loc_m = raw_loc / 1e6
    owned_loc_m = t2["v1"]["total_owned_loc"] / 1e6

    # Retroactive v2 LoC across T1
    retro_loc = t1["v_latest"]["total_owned_loc"] - t1["v1"]["total_owned_loc"]
    retro_infl = t1["v_latest"]["total_owned_loc"] / t1["v1"]["total_owned_loc"]

    # Zero-adoption totals
    t2_zero_sum = t2["cat_total"]["eess.SP"] + t2["cat_total"]["cs.NI"] + t2["cat_total"]["cs.RO"]
    ni_3slice = sum(s["cat_total"]["cs.NI"] for s in (t0, t1, t2))
    ro_3slice = sum(s["cat_total"]["cs.RO"] for s in (t0, t1, t2))

    # T2 pruned % and recall ratio
    pruned_pct = 100.0 * (1.0 - t2["stage2_lean_candidates"] / t2["total_papers"])
    meta_recall_x = t2["stage2_lean_candidates"] / t2["meta_lean_strong"]

    # Phase 2 Layer-A audit counts
    t2_audits = t2["audits"]
    t1_audits = t1["audits"]
    n_aud_t2 = len(t2_audits)
    n_aud_t1 = len(t1_audits)
    n_aud_tot = n_aud_t2 + n_aud_t1
    n_indep_t2 = sum(1 for a in t2_audits if a["arxiv_id"] != "2611.26272")
    n_high_t2 = sum(1 for a in t2_audits if a["overall_fidelity"] == "high_faithful")
    n_m2_t2 = sum(1 for a in t2_audits if a["m2"] != "none")
    n_nonvac_t2 = sum(1 for a in t2_audits if a["non_vacuity"])
    nonvac_pct_t2 = 100.0 * n_nonvac_t2 / n_aud_t2
    n_mathlib_strong_t2 = sum(1 for a in t2_audits if a["mathlib"] == "strong_mathlib")
    n_mathlib_mixed_t2 = sum(1 for a in t2_audits if a["mathlib"] == "mixed_custom_and_mathlib")

    # Helper: verify substring or regex presence in a specific text scope
    def _must_match(desc: str, pattern: str, scope: str = tex) -> None:
        if not re.search(pattern, scope):
            errors.append(f"Prose/bolded mismatch ({desc}): expected pattern {pattern!r} in main.tex")

    abs_m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, flags=re.DOTALL)
    abstract_tex = abs_m.group(1) if abs_m else ""
    if not abstract_tex:
        errors.append("Missing \\begin{abstract}...\\end{abstract} block in main.tex")

    # 1. Corpus & coverage (checked in Abstract AND body where repeated)
    _must_match("Abstract total corpus 9,837", rf"\\textbf\{{{tot_papers:,}\}}", scope=abstract_tex)
    _must_match("Section 6 total corpus 9,837", rf"\\textbf\{{{tot_papers:,}\}}.*\\textbf\{{{tot_screened:,}\}}.*\\textbf\{{{tot_cov:.2f}\\%\}}")
    _must_match("T0 corpus", rf"n={t0['total_papers']:,}".replace(",", r"\{,\}"))
    _must_match("T1 corpus", rf"n={t1['total_papers']:,}".replace(",", r"\{,\}"))
    _must_match("T2 corpus", rf"n={t2['total_papers']:,}".replace(",", r"\{,\}"))
    _must_match("T2 non-TCS corpus", rf"\\textbf\{{{t2['non_tcs_total']:,}\}}")
    _must_match("T2 coverage", rf"\\textbf\{{{t2['coverage_pct']:.2f}\\% full-text coverage\}}")
    _must_match(
        "T2 fetch breakdown",
        rf"{t2['fetch_counts']['html']:,} HTML5,\s*{t2['fetch_counts']['pdf']:,} PDF,\s*{t2['fetch_counts']['failed']} genuine HTTP 404s",
    )
    _must_match("pruned %", rf"{pruned_pct:.1f}\\%")
    _must_match("metadata recall multiplier", rf"{meta_recall_x:.1f}\\times")
    _must_match("T2 metadata strong hits", rf"\\textbf\{{{t2['meta_lean_strong']}\}}")
    _must_match(
        "T2 Stage-2 candidates",
        rf"\\textbf\{{{t2['stage2_lean_candidates']} Lean candidates\}}\s*\({t2['stage2_lean_strong']} strong,\s*{t2['stage2_lean_candidates'] - t2['stage2_lean_strong']} contextual-only",
    )

    # 2. Longitudinal adoption curve, CIs, Beyond-Lean control
    _must_match(
        "Abstract T0 v1 0/N + 95% UB",
        rf"\\textbf\{{0/{t0['total_papers']:,}\s*\(0\.00\\%,\s*95\\% UB {t0_ub:.2f}\\%\)\}}",
        scope=abstract_tex,
    )
    _must_match(
        "Abstract T1 v1 count & pct",
        rf"\\textbf\{{{t1['v1']['count']}/{t1['total_papers']:,}\s*\({t1['v1']['pct']:.2f}\\%\)\}}",
        scope=abstract_tex,
    )
    _must_match(
        "Abstract T2 v1 count & pct",
        rf"\\textbf\{{{t2['v1']['count']}/{t2['total_papers']:,}\s*\({t2['v1']['pct']:.2f}\\%\)\}}",
        scope=abstract_tex,
    )
    _must_match("Abstract median LoC jump", rf"\\textbf\{{{med_jump:.1f}\$\\times\$\}}\s*\({t1['v1']['median_owned_loc']:,}\s*\$\\rightarrow\$\s*{t2['v1']['median_owned_loc']:,}~LoC\)", scope=abstract_tex)
    _must_match("T1 Wilson CI", rf"\[{t1_lo:.2f}\\%,\s*{t1_hi:.2f}\\%\]")
    _must_match("T2 Wilson CI", rf"\[{t2_lo:.2f}\\%,\s*{t2_hi:.2f}\\%\]")
    _must_match("6-month jump multiplier", rf"{v1_jump:.1f}\\times")
    _must_match(
        "Beyond-Lean control series",
        rf"\\textbf\{{{t0['stage2_beyond_any_pct']:.2f}\\%\s*\$\\rightarrow\$\s*{t1['stage2_beyond_any_pct']:.2f}\\%\s*\$\\rightarrow\$\s*{t2['stage2_beyond_any_pct']:.2f}\\%\}}",
    )
    _must_match(
        "Lean overtaking Beyond-Lean",
        rf"{t2['stage2_lean_candidates']}\s+vs\.\\\s+{t2['stage2_beyond_any']}",
    )
    _must_match("rescued revised range", rf"{t1['revised_pct']:.1f}--{t0['revised_pct']:.1f}\\%")
    _must_match("retroactive v2 LoC", rf"{retro_loc / 1e3:.1f}k~LoC")
    _must_match("retroactive inflation", rf"{round(retro_infl)}\\times")

    # 3. Scale (LoC), AI disclosure, Tier3_Gold, Opacity
    _must_match("median LoC jump ratio", rf"\\textbf\{{{med_jump:.1f}\$\\times\$\}}")
    _must_match("median LoC scale headline", rf"\\textbf\{{{med_jump:.1f}\$\\times\$ scale explosion")
    _must_match("median LoC Section 6 bold", rf"\\textbf\{{{t2['v1']['median_owned_loc']:,}~LoC\}}")
    _must_match(
        "median LoC T1->T2",
        rf"{t1['v1']['median_owned_loc']:,}\s*\$\\rightarrow\$\s*{t2['v1']['median_owned_loc']:,}~LoC",
    )
    _must_match("T1 total owned LoC", rf"total {t1['v1']['total_owned_loc']:,}~LoC")
    _must_match("T2 total owned LoC (M)", rf"\\textbf\{{{owned_loc_m:.2f}M\}}")
    _must_match("T2 raw primary repo LoC (M) in prose", rf"{raw_loc_m:.2f}M raw repo LoC")
    _must_match("T2 raw primary repo LoC (M)", rf"\\textbf\{{{raw_loc_m:.2f}~million non-empty lines of code\}}")
    _must_match(
        "T2 scanned repo & paper count",
        rf"Across {n_uniq_repos} unique locally scanned primary (?:repositories|artifacts)\s*\(covering {n_papers_scanned} papers",
    )
    _must_match("explicit AI disclosure T1->T2", rf"\\textbf\{{{ai_t1_pct:.0f}\\%\}}\s+to\s+\\textbf\{{{ai_t2_pct:.1f}\\%\}}")
    _must_match("Tier3_Gold T1->T2", rf"\\textbf\{{0\\%\}}\s+to\s+\\textbf\{{{gold_t2_pct:.1f}\\%\}}")
    _must_match(
        "Mode12_ProcessOpacity in prose",
        rf"Mode12\\_ProcessOpacity\}}\s+at\s+{opacity_t2_pct:.1f}\\%\s*\({opacity_t2}/{t2['v1']['count']}\)",
    )

    # 4. Category highlights & zero-adoption totals
    oc_cnt = t2["v1"]["cat_lean"]["math.OC"]
    oc_tot = t2["cat_total"]["math.OC"]
    oc_pct = 100.0 * oc_cnt / oc_tot
    oc_eng = t2["v1"]["cat_eng"]["math.OC"]
    _must_match("math.OC headline", rf"{oc_pct:.2f}\\%\s*\({oc_cnt}/{oc_tot},\s*{oc_eng}")
    _must_match("zero-adoption trio sum", rf"0 / {t2_zero_sum:,}")
    _must_match("cs.NI 3-slice zero", rf"cs\.NI\}}\s*\(0/{ni_3slice:,}")
    _must_match("cs.RO 3-slice zero", rf"cs\.RO\}}\s*\(0/{ro_3slice:,}")

    # 5. Recall calibration
    if recall_cal is not None:
        gh_ub = 100.0 * recall_cal["gh_fn_95pct_upper_bound"]
        gh_acc_ub = 100.0 * recall_cal["gh_acc_fn_95pct_upper_bound"]
        gh_share = 100.0 * recall_cal["total_github_linked_negatives"] / recall_cal["total_stage2_negatives"]
        _must_match("recall total negatives", rf"\\textbf\{{{recall_cal['total_stage2_negatives']:,}\}}")
        _must_match(
            "recall GH-linked negatives",
            rf"{recall_cal['total_github_linked_negatives']:,}\s+papers containing non-boilerplate GitHub links\s*\({gh_share:.1f}\\%\)",
        )
        _must_match("recall non-GH negatives", rf"{recall_cal['total_non_github_negatives']:,}\s+without")
        _must_match("recall GH sample", rf"\\textbf\{{{recall_cal['gh_sample_size']}\}}")
        _must_match("recall 333 unique repos", rf"\\textbf\{{{recall_cal['gh_unique_repos_checked']} unique GitHub repositories\}}")
        _must_match("recall accessible papers", rf"{recall_cal['gh_accessible_papers']} papers had")
        _must_match("recall 0/200", rf"\\textbf\{{{recall_cal['gh_lean_hits_count']}/{recall_cal['gh_sample_size']}\}}")
        _must_match("recall 95% UB", rf"\\textbf\{{{gh_ub:.2f}\\%\}}")
        _must_match("recall accessible 95% UB", rf"\\textbf\{{{gh_acc_ub:.2f}\\%\}}")
        _must_match("recall 0/100 non-GH", rf"\\textbf\{{{len(recall_cal['non_gh_broad_meta_flags'])} / {recall_cal['non_gh_sample_size']}\}}")

    # 6. Phase 2 Layer-A Audit counts
    _must_match("Phase 2 total cohort", rf"\\textbf\{{{n_aud_tot}\}}")
    _must_match("Phase 2 T2 + T1 split", rf"\({n_aud_t2} in T2 \+ {n_aud_t1} in T1\)")
    _must_match("Phase 2 independent author-owned", rf"{n_indep_t2}/{n_indep_t2}")
    _must_match("Phase 2 high_faithful", rf"\\textbf\{{{n_high_t2}/{n_indep_t2}\}}")
    _must_match("Phase 2 Mode #2", rf"{n_m2_t2}/{n_aud_t2} Mode")
    _must_match("Phase 2 Mathlib anchoring", rf"{n_mathlib_strong_t2} strong,\s*{n_mathlib_mixed_t2} mixed")
    _must_match("Phase 2 non-vacuity", rf"\\textbf\{{{n_nonvac_t2}/{n_aud_t2}\s*=\s*{nonvac_pct_t2:.1f}\\%\}}")

    # 7. Also verify no stale pre-hygiene figure/caption LoC or scanned-repo count remains
    fig_loc_caption = re.search(
        r"\\label\{fig:loc\}",
        tex,
    )
    if fig_loc_caption:
        # Check caption immediately preceding \label{fig:loc}
        cap_m = re.search(r"\\caption\{(.*?)\}\s*\\label\{fig:loc\}", tex, flags=re.DOTALL)
        if cap_m and f"all {n_papers_scanned} confirmed papers" not in cap_m.group(1):
            errors.append(
                f"fig:loc caption: expected 'all {n_papers_scanned} confirmed papers' in caption"
            )

    return errors


def check_all_bolded_numbers(
    tex: str,
    slices: dict[str, dict[str, Any]],
    fig_inputs: dict[str, Any],
    recall_cal: dict[str, Any] | None,
) -> list[str]:
    """Audit EVERY numeric token inside any \\textbf{...} span in main.tex against artifact-derived values."""
    t0, t1, t2 = slices["T0"], slices["T1"], slices["T2"]
    allowed: set[str] = set()

    def _add_int(v: int) -> None:
        allowed.add(str(v))
        allowed.add(f"{v:,}")

    def _add_pct(v: float) -> None:
        allowed.add(f"{v:.0f}%")
        allowed.add(f"{v:.1f}%")
        allowed.add(f"{v:.2f}%")

    def _add_mult(v: float) -> None:
        allowed.add(f"{v:.1f}x")
        allowed.add(f"{v:.0f}x")

    # Corpus, screening, revisions, candidates, Beyond-Lean
    tot_papers = t0["total_papers"] + t1["total_papers"] + t2["total_papers"]
    tot_screened = t0["screened_ok"] + t1["screened_ok"] + t2["screened_ok"]
    _add_int(tot_papers)
    _add_int(tot_screened)
    _add_pct(100.0 * tot_screened / tot_papers)

    for s in (t0, t1, t2):
        _add_int(s["total_papers"])
        _add_int(s["non_tcs_total"])
        _add_int(s["screened_ok"])
        _add_pct(s["coverage_pct"])
        _add_int(s["revised_v_gt_1"])
        _add_pct(s["revised_pct"])
        _add_int(s["meta_lean_strong"])
        _add_int(s["stage2_lean_strong"])
        _add_int(s["stage2_lean_candidates"])
        _add_pct(s["stage2_lean_cand_pct"])
        _add_int(s["stage2_beyond_any"])
        _add_pct(s["stage2_beyond_any_pct"])
        for mode in ("v1", "v_latest"):
            m = s[mode]
            _add_int(m["count"])
            _add_pct(m["pct"])
            _add_int(m["non_tcs_count"])
            _add_pct(m["non_tcs_pct"])
            _add_int(m["eng_math_count"])
            _add_pct(m["eng_math_share_pct"])
            for c_val in m["cat_lean"].values():
                _add_int(c_val)
            for c_val in m["cat_eng"].values():
                _add_int(c_val)
            for bucket in ("roles", "paradigms", "tiers", "ai", "artifacts", "risks"):
                for v in m[bucket].values():
                    _add_int(v)
                    if m["count"] > 0:
                        _add_pct(100.0 * v / m["count"])
            _add_int(m["scanned_owned_repos"])
            _add_int(m["total_owned_loc"])
            _add_int(m["median_owned_loc"])
        for cat, tot in s["cat_total"].items():
            _add_int(tot)
            for mode in ("v1", "v_latest"):
                k = s[mode]["cat_lean"].get(cat, 0)
                _add_pct(100.0 * k / tot)
                ek = s[mode]["cat_eng"].get(cat, 0)
                if k > 0:
                    _add_pct(100.0 * ek / k)

    # Derived longitudinal ratios, CIs, LoC aggregates, zero-adoption totals
    _add_pct(0.0)
    _add_pct(95.0)
    _add_pct(clopper_pearson_upper_pct(t0["total_papers"]))
    _add_pct(100.0 * (1.0 - t2["stage2_lean_candidates"] / t2["total_papers"]))
    _add_mult(t2["v1"]["pct"] / t1["v1"]["pct"])
    _add_mult(t2["stage2_lean_cand_pct"] / t1["stage2_lean_cand_pct"])
    _add_mult(t2["stage2_lean_cand_pct"] / t0["stage2_lean_cand_pct"])
    _add_mult(t2["v1"]["eng_math_corpus_pct"] / t1["v1"]["eng_math_corpus_pct"])
    _add_mult(t2["v1"]["median_owned_loc"] / t1["v1"]["median_owned_loc"])

    _add_int(t2["cat_total"]["eess.SP"] + t2["cat_total"]["cs.NI"] + t2["cat_total"]["cs.RO"])
    _add_int(sum(s["cat_total"]["cs.NI"] for s in (t0, t1, t2)))
    _add_int(sum(s["cat_total"]["cs.RO"] for s in (t0, t1, t2)))

    retro_loc = t1["v_latest"]["total_owned_loc"] - t1["v1"]["total_owned_loc"]
    allowed.add(f"{retro_loc / 1e3:.1f}k")
    allowed.add(f"{t2['v1']['total_owned_loc'] / 1e6:.2f}M")
    _, _, raw_loc = compute_raw_primary_repo_stats(fig_inputs)
    allowed.add(f"{raw_loc / 1e6:.2f}")
    allowed.add(f"{raw_loc / 1e6:.2f}M")
    _add_int(12)  # Pilot v1 Beyond-Lean confirmed baseline in tab:categories

    # Phase 2 Layer-A audit metrics
    n_t2_aud = len(t2["audits"])
    n_t1_aud = len(t1["audits"])
    n_indep_t2 = sum(1 for a in t2["audits"] if a["arxiv_id"] != "2611.26272")
    n_oct_nov_indep = n_indep_t2 + sum(1 for a in t1["audits"] if a["is_retroactive_v2"])
    n_high = sum(1 for a in t2["audits"] if a["overall_fidelity"] == "high_faithful")
    n_m2 = sum(1 for a in t2["audits"] if a["m2"] != "none")
    n_nonvac = sum(1 for a in t2["audits"] if a["non_vacuity"])
    n_strong_m = sum(1 for a in t2["audits"] if a["mathlib"] == "strong_mathlib")
    n_mixed_m = sum(1 for a in t2["audits"] if a["mathlib"] == "mixed_custom_and_mathlib")
    for v in (n_t2_aud, n_t1_aud, n_t2_aud + n_t1_aud, n_indep_t2, n_oct_nov_indep, n_high, n_m2, n_nonvac, n_strong_m, n_mixed_m, 0):
        _add_int(v)
    _add_pct(100.0 * n_nonvac / n_t2_aud)

    # Recall calibration metrics
    if recall_cal is not None:
        for k in (
            "total_stage2_negatives",
            "total_github_linked_negatives",
            "total_non_github_negatives",
            "gh_sample_size",
            "gh_accessible_papers",
            "gh_unique_repos_checked",
            "gh_lean_hits_count",
            "non_gh_sample_size",
        ):
            _add_int(int(recall_cal[k]))
        _add_pct(100.0 * recall_cal["gh_fn_95pct_upper_bound"])
        _add_pct(100.0 * recall_cal["gh_acc_fn_95pct_upper_bound"])

    # Structural / non-metric tokens that appear inside \textbf{...} headings/labels
    structural_re = re.compile(
        r"(?:"
        r"\b(?:Nov|May)\s+1--19\b|"
        r"\b(?:T[0-3]|P[0-4]|M(?:2|3|6|10|12)|v1|v2)\b|"
        r"\b(?:Stage|Stages|Phase|Tier|Layer|Gemini|Lean|Mode)\s*[~-]?\s*(?:\\#)?\d+(?:[.-]\d+)?|"
        r"\\#\d+|"
        r"\b\d{4}\.\d{5}\b|"
        r"\bOptPaper-20\b|"
        r"\bTTony2019/OptPaper\b|"
        r"\b1bde49b\b|"
        r"\b(?:2025|2026)\b|"
        r"\b8 cats\b"
        r")"
    )

    errors: list[str] = []
    for line_no, raw_line in enumerate(tex.splitlines(), 1):
        for m in re.finditer(r"\\textbf\{((?:[^{}]|\{[^{}]*\})*)\}", raw_line):
            span = m.group(1)
            cleaned = clean_tex_cell(span).replace(r"$\times$", "x").replace(r"\times", "x")
            cleaned = re.sub(r"\\texttt\{([^}]*)\}", r"\1", cleaned)
            cleaned = structural_re.sub(" ", cleaned)
            # Extract numeric tokens (percentages, multipliers, k/M LoC, comma-grouped ints, decimals)
            for nm in re.finditer(r"\d+(?:,\d{3})*(?:\.\d+)?(?:%|[kMx])?", cleaned):
                tok = nm.group(0)
                if tok not in allowed:
                    errors.append(
                        f"Bolded numeric audit (line {line_no}): unverified token {tok!r} inside \\textbf{{{span}}}"
                    )
    return errors


def check_provenance_integrity(prov: dict[str, Any], slices: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    expected_total = len(slices["T1"]["audits"]) + len(slices["T2"]["audits"])
    if prov.get("total_audited_repos") != expected_total:
        errors.append(
            f"phase2_provenance.json: total_audited_repos={prov.get('total_audited_repos')} != expected {expected_total}"
        )
    summary = prov.get("theorems_compared_file_line_summary", {})
    if summary.get("resolved_in_bounds") != summary.get("total_refs"):
        errors.append(
            f"phase2_provenance.json: file:line check incomplete "
            f"({summary.get('resolved_in_bounds')}/{summary.get('total_refs')})"
        )
    for rec in prov.get("records", []):
        chk = rec.get("theorems_compared_file_line_check", {})
        if chk.get("unresolved"):
            errors.append(f"phase2_provenance.json [{rec['arxiv_id']}]: unresolved refs {chk['unresolved']}")
        if chk.get("out_of_bounds"):
            errors.append(f"phase2_provenance.json [{rec['arxiv_id']}]: out_of_bounds refs {chk['out_of_bounds']}")
    return errors


def run_all_checks(
    tex_path: Path = DEFAULT_TEX,
    longitudinal_path: Path = DEFAULT_LONGITUDINAL,
    slices_dir: Path = DEFAULT_SLICES_DIR,
    provenance_path: Path = DEFAULT_PROVENANCE,
) -> tuple[list[str], dict[str, Any]]:
    tex = strip_tex_comments(tex_path.read_text(encoding="utf-8"))
    longit = json.loads(longitudinal_path.read_text(encoding="utf-8"))
    slices = {s["short_id"]: s for s in longit["slices"]}

    fig_inputs_by_slice: dict[str, dict[str, Any]] = {}
    for fp in sorted(slices_dir.glob("*/figure_inputs.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        fig_inputs_by_slice[data.get("slice_id", fp.parent.name)] = data

    recall_path = slices_dir / "2026-11" / "recall_calibration.json"
    recall_cal = json.loads(recall_path.read_text(encoding="utf-8")) if recall_path.is_file() else None

    errors: list[str] = []
    errors.extend(check_cross_artifact_consistency(longit, fig_inputs_by_slice))
    errors.extend(check_table_categories(tex, slices["T2"]))
    errors.extend(check_table_distributions(tex, slices["T2"]))
    errors.extend(check_table_inventory(tex, slices["T2"]))
    errors.extend(check_table_longitudinal(tex, slices))
    if "2026-11" in fig_inputs_by_slice:
        errors.extend(check_prose_and_bolded_claims(tex, slices, fig_inputs_by_slice["2026-11"], recall_cal))
        errors.extend(check_all_bolded_numbers(tex, slices, fig_inputs_by_slice["2026-11"], recall_cal))
    if provenance_path.is_file():
        prov = json.loads(provenance_path.read_text(encoding="utf-8"))
        errors.extend(check_provenance_integrity(prov, slices))

    t2 = slices["T2"]
    stats = {
        "slices_checked": sorted(slices.keys()),
        "figure_inputs_checked": sorted(fig_inputs_by_slice.keys()),
        "t2_confirmed": t2["v1"]["count"],
        "t2_scanned_owned_repos": t2["v1"]["scanned_owned_repos"],
        "t2_median_owned_loc": t2["v1"]["median_owned_loc"],
        "t2_total_owned_loc": t2["v1"]["total_owned_loc"],
    }
    return errors, stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify numeric consistency between main.tex and JSON artifacts.")
    ap.add_argument("--tex", type=Path, default=DEFAULT_TEX)
    ap.add_argument("--longitudinal", type=Path, default=DEFAULT_LONGITUDINAL)
    ap.add_argument("--slices-dir", type=Path, default=DEFAULT_SLICES_DIR)
    ap.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    args = ap.parse_args()

    errors, stats = run_all_checks(
        tex_path=args.tex,
        longitudinal_path=args.longitudinal,
        slices_dir=args.slices_dir,
        provenance_path=args.provenance,
    )
    if errors:
        print(f"Paper numeric consistency gate FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(
        "Paper numeric consistency gate PASSED: "
        f"slices={stats['slices_checked']}, figure_inputs={stats['figure_inputs_checked']}, "
        f"T2 confirmed={stats['t2_confirmed']}, scanned={stats['t2_scanned_owned_repos']}, "
        f"median_owned_loc={stats['t2_median_owned_loc']:,}, "
        f"total_owned_loc={stats['t2_total_owned_loc']:,} (0 mismatches)."
    )


if __name__ == "__main__":
    main()
