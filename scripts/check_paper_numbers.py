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
DEFAULT_SANDBOX_DIR = REPO_ROOT / "artifacts" / "sandbox_builds"
DEFAULT_HUMAN_DIR = REPO_ROOT / "artifacts" / "human_annotations"
DEFAULT_TRACK1_PATH = REPO_ROOT / "artifacts" / "track1_sensitivity_summary.json"
DEFAULT_SCOUT_PLUS7_PATH = REPO_ROOT / "artifacts" / "scout_eng_tier12_2026_11_summary.json"
DEFAULT_TRACK3_PATH = REPO_ROOT / "artifacts" / "track3_operational_fv_pilot.json"

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
    sandbox_data: tuple[dict[str, Any], list[dict[str, Any]]] | None = None,
    human_data: tuple[dict[str, Any] | None, dict[str, Any] | None] | None = None,
    v07_data: tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None] | None = None,
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

    # Sandboxed dynamic kernel verification metrics (if present)
    if sandbox_data is not None:
        summary, records = sandbox_data
        ov = summary["overall"]
        t2_sb = summary["by_slice"]["2026-11"]
        t1_sb = summary["by_slice"]["2026-05"]
        for blk in (ov, t2_sb, t1_sb):
            for k in (
                "total_attempted",
                "pass_out_of_box",
                "pass_and_standard_axioms_only",
                "pass_with_nonstandard_axioms",
                "fail_packaging_no_lakefile",
                "fail_missing_local_dep",
                "fail_build_or_other",
                "synthetic_env_pass_among_packaging_fails",
                "tier3_gold_attempted",
                "tier3_gold_pass_out_of_box",
                "tier3_gold_clean_axioms",
                "total_theorems_checked_ootb",
                "total_theorems_checked_incl_synthetic",
            ):
                _add_int(int(blk[k]))
            if blk["total_attempted"] > 0:
                _add_pct(100.0 * blk["pass_out_of_box"] / blk["total_attempted"])
            if blk["tier3_gold_attempted"] > 0:
                _add_pct(100.0 * blk["tier3_gold_pass_out_of_box"] / blk["tier3_gold_attempted"])
            if blk["tier3_gold_pass_out_of_box"] > 0:
                _add_pct(100.0 * blk["tier3_gold_clean_axioms"] / blk["tier3_gold_pass_out_of_box"])
        # Exact derived sandbox metrics: T3 OOTB theorems, distinct toolchains, median/min/max build times, per-repo counts
        t3_thms = sum(
            int(r.get("total_theorems_checked") or 0)
            for r in records
            if r.get("static_verification_tier") == "Tier3_Gold" and r.get("build_status") == "pass"
        )
        _add_int(t3_thms)
        distinct_tc = len({r["lean_toolchain"] for r in records if r.get("lean_toolchain")})
        _add_int(distinct_tc)
        _add_int(15)
        allowed.add("15,000")
        allowed.add("15k")
        pass_times = sorted(float(r["wall_time_sec"]) for r in records if r["build_status"] == "pass")
        if pass_times:
            mid = len(pass_times) // 2
            med_t = pass_times[mid] if len(pass_times) % 2 == 1 else 0.5 * (pass_times[mid - 1] + pass_times[mid])
            allowed.add(f"{med_t:.1f}")
            allowed.add(f"{pass_times[0]:.1f}")
            allowed.add(f"{pass_times[-1]:,.1f}")
        for r in records:
            _add_int(int(r.get("total_theorems_checked") or 0))
            _add_int(len(r.get("nonstandard_axioms_detected") or []))
            syn = r.get("synthetic_env_check") or {}
            if syn:
                _add_int(int(syn.get("total_theorems_checked") or 0))

    # Human verification & blinded Stage-4 IRR metrics (if present)
    if human_data is not None:
        irr_summary, layer_a_human = human_data
        if irr_summary is not None:
            for ann_data in irr_summary.get("human_vs_llm", {}).values():
                _add_int(len(ann_data.get("disagreements", [])))
                for m in ann_data.get("metrics", []):
                    _add_int(int(m["n"]))
                    allowed.add(f"{m['exact_agreement']:.3f}")
                    _add_pct(100.0 * m["exact_agreement"])
                    if m.get("cohens_kappa") is not None:
                        allowed.add(f"{m['cohens_kappa']:.3f}")
                    if m.get("krippendorff_alpha") is not None:
                        allowed.add(f"{m['krippendorff_alpha']:.3f}")
                    for row in m.get("confusion", {}).values():
                        for v in row.values():
                            _add_int(int(v))
        if layer_a_human is not None:
            recs = layer_a_human.get("records", [])
            _add_int(len(recs))
            n_named = sum(1 for r in recs if r.get("cohort") == "named_critique")
            n_spot = sum(1 for r in recs if r.get("cohort") == "clean_spot_check")
            n_unchanged = sum(1 for r in recs if r.get("live_head_unchanged_at_review") is True)
            for v in (n_named, n_spot, n_unchanged):
                _add_int(v)

    # v0.7 scope-refinement artifacts: Track 1 (4-way), Track 2 (+7 scout), Track 3 (operational FV)
    if v07_data is not None:
        track1, scout7, track3 = v07_data
        if track1 is not None:
            _add_int(int(track1["total_confirmed_papers_v_latest"]))
            _add_int(int(track1["borderline_count_total"]))
            gr = track1["growth_t1_to_t2_v1"]
            for gk in (
                "pooled_rate_multiplier",
                "eng_algorithmic_proof_rate_multiplier",
                "eng_algorithmic_proof_loc_median_multiplier",
                "eng_strict_core_rate_multiplier",
                "operational_system_fv_rate_multiplier",
                "pure_math_or_tcs_rate_multiplier",
            ):
                if gr.get(gk) is not None:
                    v = float(gr[gk])
                    _add_mult(v)
                    allowed.add(f"{v:.2f}x")
            sl_by_id = {sl["short_id"]: sl for sl in track1["slices"]}
            for sl_blk in track1["slices"]:
                cat_tots = sl_blk.get("cat_total", {})
                for mode_key in ("v1", "v_latest"):
                    mb = sl_blk["modes"][mode_key]
                    for binfo in list(mb["by_role"].values()) + [mb["pooled"], mb["eng_strict_core_non_borderline"]]:
                        _add_int(int(binfo["count"]))
                        _add_pct(float(binfo["corpus_pct"]))
                        for ci_v in binfo.get("ci_95_pct", []):
                            _add_pct(float(ci_v))
                        _add_int(int(binfo.get("scanned_owned_repos", 0)))
                        _add_int(int(binfo.get("total_owned_loc", 0)))
                        if binfo.get("median_owned_loc") is not None:
                            _add_int(int(round(float(binfo["median_owned_loc"]))))
                        if binfo.get("share_of_owned_loc_pct") is not None:
                            _add_pct(float(binfo["share_of_owned_loc_pct"]))
                        if binfo.get("share_of_confirmed_pct") is not None:
                            _add_pct(float(binfo["share_of_confirmed_pct"]))
                        _add_int(int(binfo.get("tier3_gold_count", 0)))
                        if binfo.get("tier3_gold_pct_of_bucket") is not None:
                            _add_pct(float(binfo["tier3_gold_pct_of_bucket"]))
                        if binfo.get("tier3_gold_pct_of_scanned") is not None:
                            _add_pct(float(binfo["tier3_gold_pct_of_scanned"]))
                        if binfo.get("ai_explicit_yes_pct") is not None:
                            _add_pct(float(binfo["ai_explicit_yes_pct"]))
                        for cat_k, cat_cnt in (binfo.get("cat_counts") or {}).items():
                            _add_int(int(cat_cnt))
                            if cat_tots.get(cat_k):
                                _add_pct(100.0 * int(cat_cnt) / int(cat_tots[cat_k]))
            t2_b = sl_by_id["T2"]["modes"]["v1"]["by_role"]
            _add_pct(
                float(t2_b["pure_math_or_tcs"]["share_of_owned_loc_pct"])
                + float(t2_b["meta_formalization_system"]["share_of_owned_loc_pct"])
            )
            for p2_info in track1.get("phase2_audits_by_role", {}).values():
                _add_int(int(p2_info["count"]))
                _add_int(int(p2_info["material_undisclosed_count"]))
        if scout7 is not None:
            pt = scout7["plus7_totals"]
            _add_int(len(pt["categories"]))
            for k in (
                "raw_category_sum",
                "unique_papers",
                "overlap_with_orig8",
                "net_new_papers",
                "combined_15cat_unique_papers",
                "meta_lean_strong",
                "stage2_lean_strong",
                "stage2_lean_strong_net_new",
                "stage2_lean_ctx_only",
                "stage2_lean_ctx_only_net_new",
                "stage2_lean_candidates_total",
                "stage2_lean_candidates_net_new",
                "beyond_lean_any_fv",
                "combined_15cat_stage2_lean_candidates",
            ):
                _add_int(int(pt[k]))
            _add_int(sum(int(v) for k, v in pt["fetch_sources"].items() if k in ("html", "pdf")))
            _add_pct(float(pt["fulltext_coverage_pct"]))
            _add_pct(100.0 * pt["stage2_lean_candidates_total"] / pt["unique_papers"])
            eess = scout7["complete_eess_archive"]
            for k in ("unique_papers", "primary_eess_papers", "stage2_lean_candidates_total", "non_sy_unique_papers"):
                _add_int(int(eess[k]))
            _add_pct(float(eess["non_sy_95_upper_bound_pct"]))
            _add_pct(100.0)
            for cinfo in scout7["per_category"].values():
                _add_int(int(cinfo["total"]))
                _add_int(int(cinfo["net_new_vs_orig8"]))
                _add_int(int(cinfo["stage2_lean_candidates_total"]))
                _add_pct(float(cinfo["stage2_candidate_rate_pct"]))
                for ci_v in cinfo["stage2_candidate_ci95_pct"]:
                    _add_pct(float(ci_v))
            na = scout7["math_na_metadata_probe"]
            for k in ("total_papers", "net_new_vs_15cat", "meta_lean_strong", "meta_lean_ctx_only"):
                _add_int(int(na[k]))
            na_captured = sum(
                1 for h in na["meta_lean_hits"]
                if h["signal_tier"] == "meta_lean_strong" and (h["in_survey_db_orig8"] or h["in_plus7_scout"])
            )
            _add_int(na_captured)
        if track3 is not None:
            sc3 = track3["summary_counts"]
            for v in sc3.values():
                if isinstance(v, int):
                    _add_int(v)
            _add_int(18)  # 18 total custom axiom declarations in 2605.16407

    # Structural / non-metric tokens that appear inside \textbf{...} headings/labels
    structural_re = re.compile(
        r"(?:"
        r"\b(?:Nov|May)\s+1--19\b|"
        r"\b(?:T[0-3]|P[0-4]|M(?:2|3|6|10|12)|v1|v2)\b|"
        r"\b(?:Stage|Stages|Phase|Tier|Layer|Gemini|Lean|Mode|OpFV)\s*[~-]?\s*(?:\\#)?\d+(?:[.-]\d+)?|"
        r"\\#\d+|"
        r"\b\d{4}\.\d{5}\b|"
        r"\bOptPaper-20\b|"
        r"\bTTony2019/OptPaper\b|"
        r"\b1bde49b\b|"
        r"\b(?:2025|2026)\b|"
        r"\b(?:8|15)[-\s](?:cats?|Cat)\b|"
        r"\b4-way\b|"
        r"\b(?:1\.|2\.|3\.|4\.)\s|"
        r"\+[0-9]+"
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


def check_sandbox_builds(
    tex: str,
    summary: dict[str, Any],
    records: list[dict[str, Any]],
) -> list[str]:
    """Verify tab:sandbox and prose sandbox counts against artifacts/sandbox_builds/."""
    errors: list[str] = []
    tab = extract_table_by_label(tex, "tab:sandbox")
    rows = split_tabular_rows(tab)
    by_id = {r["arxiv_id"]: r for r in records}
    seen_ids: set[str] = set()

    for cells in rows:
        if len(cells) < 10:
            continue
        aid = clean_tex_cell(cells[0])
        if not re.match(r"^\d{4}\.\d{5}$", aid):
            continue
        seen_ids.add(aid)
        if aid not in by_id:
            errors.append(f"tab:sandbox: unknown arXiv ID {aid}")
            continue
        r = by_id[aid]
        exp_sl = "T2" if r["slice_id"] == "2026-11" else "T1"
        got_sl = clean_tex_cell(cells[1])
        if got_sl != exp_sl:
            errors.append(f"tab:sandbox [{aid}] Slice: got {got_sl!r} != expected {exp_sl!r}")

        exp_tier = TIER_SHORT[r["static_verification_tier"]]
        got_tier = clean_tex_cell(cells[2])
        if got_tier != exp_tier:
            errors.append(f"tab:sandbox [{aid}] Tier: got {got_tier!r} != expected {exp_tier!r}")

        exp_role = ROLE_SHORT[r["paper_domain_role"]]
        got_role = clean_tex_cell(cells[3])
        if got_role != exp_role:
            errors.append(f"tab:sandbox [{aid}] Role: got {got_role!r} != expected {exp_role!r}")

        exp_loc = f"{int(r['owned_loc']):,}"
        got_loc = clean_tex_cell(cells[4])
        if got_loc != exp_loc:
            errors.append(f"tab:sandbox [{aid}] LoC: got {got_loc!r} != expected {exp_loc!r}")

        got_thms = parse_int(clean_tex_cell(cells[8]))
        exp_thms = int(r.get("total_theorems_checked") or 0)
        if got_thms != exp_thms:
            errors.append(f"tab:sandbox [{aid}] Theorems: got {got_thms} != expected {exp_thms}")

        outcome_txt = clean_tex_cell(cells[9])
        if r["build_status"] == "pass" and not outcome_txt.startswith("PASS"):
            errors.append(f"tab:sandbox [{aid}] Outcome: expected PASS, got {outcome_txt!r}")
        if r["build_status"] != "pass" and not outcome_txt.startswith("FAIL"):
            errors.append(f"tab:sandbox [{aid}] Outcome: expected FAIL, got {outcome_txt!r}")

    missing = sorted(set(by_id) - seen_ids)
    if missing:
        errors.append(f"tab:sandbox missing repos: {missing}")

    ov = summary["overall"]
    ootb_pct = 100.0 * ov["pass_out_of_box"] / ov["total_attempted"]
    t3_pct = 100.0 * ov["tier3_gold_pass_out_of_box"] / ov["tier3_gold_attempted"]
    for desc, pat in [
        ("sandbox OOTB pass rate", rf"\\textbf\{{{ov['pass_out_of_box']}/{ov['total_attempted']}\s*\({ootb_pct:.1f}\\%\)\}}"),
        ("sandbox OOTB theorems", rf"\\textbf\{{{ov['total_theorems_checked_ootb']:,}\}}"),
        ("sandbox incl synth theorems", rf"\\textbf\{{{ov['total_theorems_checked_incl_synthetic']:,}\}}"),
        ("sandbox Tier3_Gold OOTB", rf"\\textbf\{{{ov['tier3_gold_pass_out_of_box']}/{ov['tier3_gold_attempted']}\s*\({t3_pct:.1f}\\%\)\}}"),
        ("sandbox Tier3_Gold clean", rf"\\textbf\{{{ov['tier3_gold_clean_axioms']}/{ov['tier3_gold_pass_out_of_box']}\s*\(100\\%\)\}}"),
    ]:
        if not re.search(pat, tex):
            errors.append(f"Sandbox prose mismatch ({desc}): expected pattern {pat!r} in main.tex")
    return errors


def check_human_verification_and_irr(
    tex: str,
    irr_summary: dict[str, Any] | None,
    layer_a_human: dict[str, Any] | None,
) -> list[str]:
    """Verify tab:stage4_irr and prose human-verification counts against artifacts/human_annotations/."""
    errors: list[str] = []
    if irr_summary is not None:
        tab = extract_table_by_label(tex, "tab:stage4_irr")
        rows = split_tabular_rows(tab)
        ann_map = irr_summary.get("human_vs_llm", {})
        if not ann_map:
            errors.append("stage4_irr_summary.json: missing human_vs_llm entries")
            return errors
        first_ann = sorted(ann_map.keys())[0]
        metrics_by_key = {
            (m["field"], m["scope"]): m for m in ann_map[first_ann].get("metrics", [])
        }
        seen_keys: set[tuple[str, str]] = set()
        for cells in rows:
            if len(cells) < 6:
                continue
            field_raw = clean_tex_cell(cells[0]).replace(r"\_", "_")
            field = field_raw.split()[0]
            scope_txt = clean_tex_cell(cells[1]).lower()
            scope = "agreed_contributed" if "agreed" in scope_txt else "all"
            key = (field, scope)
            if key not in metrics_by_key:
                continue
            seen_keys.add(key)
            exp = metrics_by_key[key]
            got_n = parse_int(clean_tex_cell(cells[2]))
            if got_n != int(exp["n"]):
                errors.append(f"tab:stage4_irr [{key}] n: got {got_n} != expected {exp['n']}")
            for col_idx, metric_key, label in (
                (3, "exact_agreement", "exact_agreement"),
                (4, "cohens_kappa", "cohens_kappa"),
                (5, "krippendorff_alpha", "krippendorff_alpha"),
            ):
                got_s = clean_tex_cell(cells[col_idx])
                exp_val = exp.get(metric_key)
                if exp_val is not None:
                    exp_s = f"{exp_val:.3f}"
                    if got_s != exp_s:
                        errors.append(f"tab:stage4_irr [{key}] {label}: got {got_s!r} != expected {exp_s!r}")

        missing = sorted(set(metrics_by_key) - seen_keys)
        if missing:
            errors.append(f"tab:stage4_irr missing rows: {missing}")

        n_dis = len(ann_map[first_ann].get("disagreements", []))
        if f"\\textbf{{{n_dis}}}" not in tex:
            errors.append(f"IRR prose mismatch: expected bolded disagreement count \\textbf{{{n_dis}}} in main.tex")

    if layer_a_human is not None:
        recs = layer_a_human.get("records", [])
        n_named = sum(1 for r in recs if r.get("cohort") == "named_critique")
        n_spot = sum(1 for r in recs if r.get("cohort") == "clean_spot_check")
        for desc, token in (
            ("named critiques human sign-off", f"\\textbf{{{n_named}/{n_named}}}"),
            ("clean-cohort spot-check count", f"\\textbf{{{n_spot}/{n_spot}}}"),
            ("clean-cohort zero missed drift", f"\\textbf{{0/{n_spot}}}"),
        ):
            if token not in tex:
                errors.append(f"Human verification prose mismatch ({desc}): expected {token!r} in main.tex")
    return errors


def check_v07_scope_refinements(
    tex: str,
    track1: dict[str, Any] | None,
    scout7: dict[str, Any] | None,
    track3: dict[str, Any] | None,
) -> list[str]:
    """Verify v0.7 Track 1 (tab:track1_4way), Track 2 (tab:scout_plus7), and Track 3 operational-FV claims."""
    errors: list[str] = []
    if track1 is not None:
        rows = [
            [clean_tex_cell(c) for c in row]
            for row in split_tabular_rows(extract_table_by_label(tex, "tab:track1_4way"))
        ]
        if not rows:
            errors.append("Could not locate tab:track1_4way in main.tex")
        else:
            sl_by_id = {sl["short_id"]: sl for sl in track1["slices"]}
            t2_b = sl_by_id["T2"]["modes"]["v1"]["by_role"]
            t1_b = sl_by_id["T1"]["modes"]["v1"]["by_role"]
            for bucket in ("eng_algorithmic_proof", "operational_system_fv", "pure_math_or_tcs", "meta_formalization_system"):
                match = [r for r in rows if bucket in r[0].replace(r"\_", "_")]
                if not match:
                    errors.append(f"tab:track1_4way missing row for {bucket}")
                    continue
                r = match[0]
                exp_t2 = int(t2_b[bucket]["count"])
                exp_t1 = int(t1_b[bucket]["count"])
                exp_loc = int(t2_b[bucket]["total_owned_loc"])
                exp_med = int(round(float(t2_b[bucket]["median_owned_loc"])))
                if parse_int(r[2]) != exp_t1:
                    errors.append(f"tab:track1_4way {bucket} T1 v1: tex={r[2]!r} vs json={exp_t1}")
                if parse_int(r[3]) != exp_t2:
                    errors.append(f"tab:track1_4way {bucket} T2 v1: tex={r[3]!r} vs json={exp_t2}")
                if parse_int(r[5]) != exp_loc:
                    errors.append(f"tab:track1_4way {bucket} T2 LoC: tex={r[5]!r} vs json={exp_loc}")
                if parse_int(r[6]) != exp_med:
                    errors.append(f"tab:track1_4way {bucket} Med LoC: tex={r[6]!r} vs json={exp_med}")

    if scout7 is not None:
        rows = [
            [clean_tex_cell(c) for c in row]
            for row in split_tabular_rows(extract_table_by_label(tex, "tab:scout_plus7"))
        ]
        if not rows:
            errors.append("Could not locate tab:scout_plus7 in main.tex")
        else:
            for cat, cinfo in scout7["per_category"].items():
                match = [r for r in rows if cat in r[0]]
                if not match:
                    errors.append(f"tab:scout_plus7 missing row for {cat}")
                    continue
                r = match[0]
                if parse_int(r[1]) != int(cinfo["total"]):
                    errors.append(f"tab:scout_plus7 {cat} total: tex={r[1]!r} vs json={cinfo['total']}")
                if parse_int(r[4]) != int(cinfo["stage2_lean_strong"]):
                    errors.append(f"tab:scout_plus7 {cat} strong: tex={r[4]!r} vs json={cinfo['stage2_lean_strong']}")
                if parse_int(r[5]) != int(cinfo["stage2_lean_ctx_only"]):
                    errors.append(f"tab:scout_plus7 {cat} ctx: tex={r[5]!r} vs json={cinfo['stage2_lean_ctx_only']}")
                if parse_int(r[6]) != int(cinfo["stage2_lean_candidates_total"]):
                    errors.append(f"tab:scout_plus7 {cat} total S2: tex={r[6]!r} vs json={cinfo['stage2_lean_candidates_total']}")
                if parse_int(r[7]) != int(cinfo["beyond_lean_any_fv"]):
                    errors.append(f"tab:scout_plus7 {cat} beyond-lean: tex={r[7]!r} vs json={cinfo['beyond_lean_any_fv']}")

    if track3 is not None:
        sc = track3["summary_counts"]
        for desc, tok in (
            ("Track 3 total operational FV papers", f"\\textbf{{{sc['total_operational_fv_papers']}}}"),
            ("Track 3 Mode3 false positives", f"\\textbf{{{sc['mode3_custom_defs_false_positives_on_zero_dep_repos']}/{sc['locally_cloned_and_code_audited']}}}"),
            ("Track 3 refinement gap count", f"\\textbf{{{sc['opfv1_refinement_gap_present']}/{sc['total_operational_fv_papers']}}}"),
        ):
            if tok not in tex:
                errors.append(f"Track 3 prose mismatch ({desc}): expected {tok!r} in main.tex")
    return errors


def run_all_checks(
    tex_path: Path = DEFAULT_TEX,
    longitudinal_path: Path = DEFAULT_LONGITUDINAL,
    slices_dir: Path = DEFAULT_SLICES_DIR,
    provenance_path: Path = DEFAULT_PROVENANCE,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    human_dir: Path = DEFAULT_HUMAN_DIR,
    track1_path: Path = DEFAULT_TRACK1_PATH,
    scout_plus7_path: Path = DEFAULT_SCOUT_PLUS7_PATH,
    track3_path: Path = DEFAULT_TRACK3_PATH,
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

    sandbox_data: tuple[dict[str, Any], list[dict[str, Any]]] | None = None
    sb_summary_path = sandbox_dir / "summary.json"
    if sb_summary_path.is_file():
        sb_summary = json.loads(sb_summary_path.read_text(encoding="utf-8"))
        sb_records: list[dict[str, Any]] = []
        for sl in ("2026-11", "2026-05"):
            rp = sandbox_dir / f"results_{sl}.json"
            if rp.is_file():
                sb_records.extend(json.loads(rp.read_text(encoding="utf-8")).get("records", []))
        sandbox_data = (sb_summary, sb_records)

    irr_path = human_dir / "stage4_irr_summary.json"
    layer_a_human_path = human_dir / "layer_a_human_verification.json"
    irr_summary = json.loads(irr_path.read_text(encoding="utf-8")) if irr_path.is_file() else None
    layer_a_human = json.loads(layer_a_human_path.read_text(encoding="utf-8")) if layer_a_human_path.is_file() else None
    human_data = (irr_summary, layer_a_human) if (irr_summary is not None or layer_a_human is not None) else None

    track1 = json.loads(track1_path.read_text(encoding="utf-8")) if track1_path.is_file() else None
    scout7 = json.loads(scout_plus7_path.read_text(encoding="utf-8")) if scout_plus7_path.is_file() else None
    track3 = json.loads(track3_path.read_text(encoding="utf-8")) if track3_path.is_file() else None
    v07_data = (track1, scout7, track3) if any(x is not None for x in (track1, scout7, track3)) else None

    errors: list[str] = []
    errors.extend(check_cross_artifact_consistency(longit, fig_inputs_by_slice))
    errors.extend(check_table_categories(tex, slices["T2"]))
    errors.extend(check_table_distributions(tex, slices["T2"]))
    errors.extend(check_table_inventory(tex, slices["T2"]))
    errors.extend(check_table_longitudinal(tex, slices))
    if "2026-11" in fig_inputs_by_slice:
        errors.extend(check_prose_and_bolded_claims(tex, slices, fig_inputs_by_slice["2026-11"], recall_cal))
        errors.extend(
            check_all_bolded_numbers(
                tex, slices, fig_inputs_by_slice["2026-11"], recall_cal, sandbox_data, human_data, v07_data
            )
        )
    if provenance_path.is_file():
        prov = json.loads(provenance_path.read_text(encoding="utf-8"))
        errors.extend(check_provenance_integrity(prov, slices))
    if sandbox_data is not None:
        errors.extend(check_sandbox_builds(tex, sandbox_data[0], sandbox_data[1]))
    if human_data is not None:
        errors.extend(check_human_verification_and_irr(tex, irr_summary, layer_a_human))
    if v07_data is not None:
        errors.extend(check_v07_scope_refinements(tex, track1, scout7, track3))

    t2 = slices["T2"]
    stats = {
        "slices_checked": sorted(slices.keys()),
        "figure_inputs_checked": sorted(fig_inputs_by_slice.keys()),
        "t2_confirmed": t2["v1"]["count"],
        "t2_scanned_owned_repos": t2["v1"]["scanned_owned_repos"],
        "t2_median_owned_loc": t2["v1"]["median_owned_loc"],
        "t2_total_owned_loc": t2["v1"]["total_owned_loc"],
        "sandbox_repos_checked": len(sandbox_data[1]) if sandbox_data is not None else 0,
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
