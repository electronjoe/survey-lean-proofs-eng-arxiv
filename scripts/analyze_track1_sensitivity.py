#!/usr/bin/env python3
"""Track 1 (Phase A1) Zero-Token Sensitivity Analysis Across the 4-Way Role Split.

Reads ONLY version-controlled canonical artifacts (zero SQLite dependency, zero LLM tokens):
  - artifacts/longitudinal_summary.json
  - artifacts/human_annotations/track1_4way_adjudication.json
  - artifacts/sandbox_builds/results_2026-05.json
  - artifacts/sandbox_builds/results_2026-11.json
  - artifacts/human_annotations/stage4_irr.csv

Produces:
  - artifacts/track1_sensitivity_summary.json
  - reports/track1_sensitivity_analysis.md
  - artifacts/human_annotations/track1_4way_coding_blank.csv (blinded Phase B2 template)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LONGITUDINAL = REPO_ROOT / "artifacts" / "longitudinal_summary.json"
DEFAULT_ADJUDICATION = REPO_ROOT / "artifacts" / "human_annotations" / "track1_4way_adjudication.json"
DEFAULT_SANDBOX_DIR = REPO_ROOT / "artifacts" / "sandbox_builds"
DEFAULT_IRR_CSV = REPO_ROOT / "artifacts" / "human_annotations" / "stage4_irr.csv"
DEFAULT_JSON_OUT = REPO_ROOT / "artifacts" / "track1_sensitivity_summary.json"
DEFAULT_MD_OUT = REPO_ROOT / "reports" / "track1_sensitivity_analysis.md"
DEFAULT_BLANK_CSV_OUT = REPO_ROOT / "artifacts" / "human_annotations" / "track1_4way_coding_blank.csv"

ROLES_4WAY = (
    "eng_algorithmic_proof",
    "operational_system_fv",
    "pure_math_or_tcs",
    "meta_formalization_system",
)

ROLE_LABELS = {
    "eng_algorithmic_proof": "Eng. Algorithmic Proof",
    "operational_system_fv": "Operational System FV",
    "pure_math_or_tcs": "Pure Math / TCS",
    "meta_formalization_system": "Meta-Formalization System",
}

TARGET_CATEGORIES = ["math.OC", "cs.DC", "cs.IT", "cs.CR", "eess.SY", "eess.SP", "cs.NI", "cs.RO"]
PURE_TCS_PRIMARY_CATS = {"cs.CC", "cs.DS", "cs.LO", "cs.DM", "cs.FL", "cs.CG"}


def wilson_ci_pct(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Two-sided 95% Wilson score confidence interval (percent)."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n)) / denom
    return (max(0.0, 100.0 * (center - half)), min(100.0, 100.0 * (center + half)))


def clopper_pearson_upper_pct(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided 95% Clopper-Pearson upper bound (percent) when k == 0."""
    if n <= 0 or k != 0:
        return wilson_ci_pct(k, n)[1]
    return 100.0 * (1.0 - alpha ** (1.0 / n))


def ci_pct(k: int, n: int) -> tuple[float, float]:
    if k == 0:
        return (0.0, clopper_pearson_upper_pct(0, n))
    return wilson_ci_pct(k, n)


def aggregate_cohort(papers: list[dict[str, Any]], total_corpus: int) -> dict[str, Any]:
    n = len(papers)
    pct = 100.0 * n / max(total_corpus, 1)
    lo, hi = ci_pct(n, total_corpus)

    locs = [int(p["primary_owned_loc"]) for p in papers if p.get("primary_owned_loc")]
    tiers = Counter(p["verification_tier"] for p in papers)
    paradigms = Counter(p["authoring_paradigm"] for p in papers)
    ai = Counter(p["ai_agent_assisted"] for p in papers)
    artifacts = Counter(p["artifact_availability"] for p in papers)
    risks = Counter(flag for p in papers for flag in p.get("static_risk_flags", []))
    ver_objs = Counter(p["verification_object"] for p in papers)

    gold = tiers.get("Tier3_Gold", 0)
    p4 = paradigms.get("P4_speclock_solve_distill", 0)
    ai_yes = ai.get("explicitly_yes", 0)
    non_tcs_prim = sum(1 for p in papers if p["primary_category"] not in PURE_TCS_PRIMARY_CATS)

    cat_counts: dict[str, int] = {c: 0 for c in TARGET_CATEGORIES}
    for p in papers:
        for c in p.get("matched_target_cats", []):
            if c in cat_counts:
                cat_counts[c] += 1

    return {
        "count": n,
        "corpus_pct": round(pct, 4),
        "ci_95_pct": [round(lo, 4), round(hi, 4)],
        "ci_type": "clopper_pearson_one_sided_95" if n == 0 else "wilson_two_sided_95",
        "non_tcs_primary_count": non_tcs_prim,
        "scanned_owned_repos": len(locs),
        "total_owned_loc": sum(locs),
        "median_owned_loc": int(statistics.median(locs)) if locs else 0,
        "mean_owned_loc": round(statistics.mean(locs), 1) if locs else 0.0,
        "min_owned_loc": min(locs) if locs else 0,
        "max_owned_loc": max(locs) if locs else 0,
        "tier3_gold_count": gold,
        "tier3_gold_pct_of_bucket": round(100.0 * gold / n, 2) if n else 0.0,
        "tier3_gold_pct_of_scanned": round(100.0 * gold / len(locs), 2) if locs else 0.0,
        "p4_count": p4,
        "p4_pct_of_bucket": round(100.0 * p4 / n, 2) if n else 0.0,
        "ai_explicit_yes_count": ai_yes,
        "ai_explicit_yes_pct": round(100.0 * ai_yes / n, 2) if n else 0.0,
        "tiers": dict(tiers),
        "paradigms": dict(paradigms),
        "ai": dict(ai),
        "artifacts": dict(artifacts),
        "risks": dict(risks),
        "verification_objects": dict(ver_objs),
        "cat_counts": cat_counts,
        "arxiv_ids": [p["arxiv_id"] for p in papers],
    }


def compute_sensitivity(
    longitudinal_path: Path = DEFAULT_LONGITUDINAL,
    adjudication_path: Path = DEFAULT_ADJUDICATION,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    irr_csv_path: Path = DEFAULT_IRR_CSV,
) -> dict[str, Any]:
    long_data = json.loads(longitudinal_path.read_text(encoding="utf-8"))
    adj_data = json.loads(adjudication_path.read_text(encoding="utf-8"))

    adj_by_id: dict[str, dict[str, Any]] = {}
    for rec in adj_data["records"]:
        aid = rec["arxiv_id"]
        if aid in adj_by_id:
            raise ValueError(f"Duplicate arxiv_id in adjudication: {aid}")
        adj_by_id[aid] = rec

    all_confirmed_ids: set[str] = set()
    enriched_slices: list[dict[str, Any]] = []
    migration_all: dict[str, dict[str, int]] = {}
    migration_t2: dict[str, dict[str, int]] = {}
    all_enriched_papers: list[dict[str, Any]] = []

    for sl in long_data["slices"]:
        short_id = sl["short_id"]
        total_papers = sl["total_papers"]
        enriched_papers: list[dict[str, Any]] = []
        for p in sl["confirmed_papers"]:
            aid = p["arxiv_id"]
            all_confirmed_ids.add(aid)
            if aid not in adj_by_id:
                raise ValueError(f"Missing adjudication record for {short_id} {aid}")
            adj = adj_by_id[aid]
            if adj["old_paper_domain_role"] != p["paper_domain_role"]:
                raise ValueError(
                    f"Old role mismatch for {aid}: adj={adj['old_paper_domain_role']} vs long={p['paper_domain_role']}"
                )
            merged = {
                **p,
                "slice_id": adj["slice_id"],
                "short_id": short_id,
                "old_paper_domain_role": adj["old_paper_domain_role"],
                "role_4way": adj["role_4way"],
                "verification_object": adj["verification_object"],
                "decision_gate": adj["decision_gate"],
                "is_borderline": bool(adj["is_borderline"]),
                "borderline_alt_role": adj.get("borderline_alt_role"),
                "rationale": adj["rationale"],
            }
            enriched_papers.append(merged)
            all_enriched_papers.append(merged)

            old_r = p["paper_domain_role"]
            new_r = adj["role_4way"]
            migration_all.setdefault(old_r, {r: 0 for r in ROLES_4WAY})[new_r] += 1
            if short_id == "T2":
                migration_t2.setdefault(old_r, {r: 0 for r in ROLES_4WAY})[new_r] += 1

        # Enrich Phase 2 audits with 4-way role
        audits_enriched = []
        for a in sl.get("audits", []):
            adj = adj_by_id[a["arxiv_id"]]
            audits_enriched.append({**a, "role_4way": adj["role_4way"], "is_borderline": bool(adj["is_borderline"])})

        slice_out: dict[str, Any] = {
            "short_id": short_id,
            "label": sl["label"],
            "total_papers": total_papers,
            "cat_total": sl["cat_total"],
            "modes": {},
            "audits_by_role": {},
        }

        for mode in ("v1", "v_latest"):
            subset = [p for p in enriched_papers if (not p["is_retroactive_v2"] if mode == "v1" else True)]
            pooled_agg = aggregate_cohort(subset, total_papers)
            by_role = {
                role: aggregate_cohort([p for p in subset if p["role_4way"] == role], total_papers)
                for role in ROLES_4WAY
            }
            # Share of confirmed papers & share of owned LoC per role
            tot_conf = pooled_agg["count"]
            tot_loc = pooled_agg["total_owned_loc"]
            for role, stats in by_role.items():
                stats["share_of_confirmed_pct"] = round(100.0 * stats["count"] / tot_conf, 4) if tot_conf else 0.0
                stats["share_of_owned_loc_pct"] = round(100.0 * stats["total_owned_loc"] / tot_loc, 4) if tot_loc else 0.0

            # Strict-core sensitivity band: eng_algorithmic_proof excluding borderline items
            strict_core_papers = [
                p for p in subset if p["role_4way"] == "eng_algorithmic_proof" and not p["is_borderline"]
            ]
            strict_core_agg = aggregate_cohort(strict_core_papers, total_papers)
            strict_core_agg["share_of_confirmed_pct"] = (
                round(100.0 * strict_core_agg["count"] / tot_conf, 4) if tot_conf else 0.0
            )
            strict_core_agg["share_of_owned_loc_pct"] = (
                round(100.0 * strict_core_agg["total_owned_loc"] / tot_loc, 4) if tot_loc else 0.0
            )

            slice_out["modes"][mode] = {
                "pooled": pooled_agg,
                "by_role": by_role,
                "eng_strict_core_non_borderline": strict_core_agg,
            }

        # Phase 2 audit summary by 4-way role
        for role in ROLES_4WAY:
            ra = [a for a in audits_enriched if a["role_4way"] == role]
            if ra:
                slice_out["audits_by_role"][role] = {
                    "count": len(ra),
                    "fidelity_counts": dict(Counter(a["overall_fidelity"] for a in ra)),
                    "non_vacuity_count": sum(1 for a in ra if a["non_vacuity"]),
                    "material_undisclosed_count": sum(
                        1 for a in ra if a["overall_fidelity"] == "material_undisclosed_drift_or_risk"
                    ),
                    "arxiv_ids": [a["arxiv_id"] for a in ra],
                }
        enriched_slices.append(slice_out)

    extra_adj = sorted(set(adj_by_id.keys()) - all_confirmed_ids)
    if extra_adj:
        raise ValueError(f"Adjudication contains unknown arxiv_ids not in longitudinal_summary: {extra_adj}")

    # Combined Phase 2 audits across T1 + T2 (n=23)
    all_audits = [
        {**a, "short_id": sl["short_id"], "role_4way": adj_by_id[a["arxiv_id"]]["role_4way"]}
        for sl in long_data["slices"]
        for a in sl.get("audits", [])
    ]
    phase2_overall_by_role: dict[str, Any] = {}
    for role in ROLES_4WAY:
        ra = [a for a in all_audits if a["role_4way"] == role]
        phase2_overall_by_role[role] = {
            "count": len(ra),
            "t1_v1_count": sum(1 for a in ra if a["short_id"] == "T1" and not a["is_retroactive_v2"]),
            "t1_retro_v2_count": sum(1 for a in ra if a["short_id"] == "T1" and a["is_retroactive_v2"]),
            "t2_count": sum(1 for a in ra if a["short_id"] == "T2"),
            "fidelity_counts": dict(Counter(a["overall_fidelity"] for a in ra)),
            "non_vacuity_count": sum(1 for a in ra if a["non_vacuity"]),
            "material_undisclosed_count": sum(
                1 for a in ra if a["overall_fidelity"] == "material_undisclosed_drift_or_risk"
            ),
            "arxiv_ids": [a["arxiv_id"] for a in ra],
        }

    # Sandboxed Docker dynamic builds (n=14) by 4-way role
    sandbox_records = []
    for sb_file in sorted(sandbox_dir.glob("results_*.json")):
        sb_payload = json.loads(sb_file.read_text(encoding="utf-8"))
        for rec in sb_payload.get("records", []):
            aid = rec["arxiv_id"]
            sandbox_records.append({**rec, "role_4way": adj_by_id[aid]["role_4way"]})

    sandbox_by_role: dict[str, Any] = {}
    for role in ROLES_4WAY:
        rs = [r for r in sandbox_records if r["role_4way"] == role]
        ootb_pass = [r for r in rs if r["build_status"] == "pass"]
        ootb_clean = [r for r in ootb_pass if not r["nonstandard_axioms_detected"] and not r["sorry_ax_detected"]]
        synth_pass = [
            r for r in rs if (r.get("synthetic_env_check") or {}).get("build_status") == "pass"
        ]
        sandbox_by_role[role] = {
            "attempted": len(rs),
            "pass_ootb": len(ootb_pass),
            "pass_ootb_clean_axioms": len(ootb_clean),
            "pass_ootb_nonstandard_axioms": len(ootb_pass) - len(ootb_clean),
            "fail_packaging_or_local_dep": len(rs) - len(ootb_pass),
            "synthetic_pass": len(synth_pass),
            "theorems_ootb": sum(int(r.get("total_theorems_checked", 0)) for r in ootb_pass),
            "theorems_incl_synthetic": sum(int(r.get("total_theorems_checked", 0)) for r in ootb_pass)
            + sum(int((r.get("synthetic_env_check") or {}).get("total_theorems_checked", 0)) for r in synth_pass),
            "arxiv_ids": [r["arxiv_id"] for r in rs],
        }

    # Stage-4 IRR diagnostic (how 4-way rubric resolves v0.6 annotator_1 vs LLM disagreements)
    irr_diagnostic: list[dict[str, Any]] = []
    if irr_csv_path.is_file():
        with irr_csv_path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("lean_usage_status") != "lean_contributed":
                    continue
                aid = row["arxiv_id"].strip()
                if aid not in adj_by_id:
                    continue
                adj = adj_by_id[aid]
                h_old = row["paper_domain_role"].strip()
                llm_old = adj["old_paper_domain_role"]
                if h_old != llm_old:
                    irr_diagnostic.append(
                        {
                            "slice_id": row["slice_id"].strip(),
                            "arxiv_id": aid,
                            "annotator_1_old_3way": h_old,
                            "llm_old_3way": llm_old,
                            "adjudicated_role_4way": adj["role_4way"],
                            "decision_gate": adj["decision_gate"],
                            "is_borderline": bool(adj["is_borderline"]),
                            "resolution_type": (
                                "resolved_by_new_meta_bucket"
                                if adj["role_4way"] == "meta_formalization_system"
                                else (
                                    "aligned_with_human_rater"
                                    if (h_old == "pure_tcs_or_math" and adj["role_4way"] == "pure_math_or_tcs")
                                    else "clarified_by_explicit_boundary_rule"
                                )
                            ),
                            "rationale": adj["rationale"],
                        }
                    )

    # Compute 6-month (T1 -> T2) growth multipliers for v1
    t1_v1 = enriched_slices[1]["modes"]["v1"]
    t2_v1 = enriched_slices[2]["modes"]["v1"]

    def _rate_mult(t2_pct: float, t1_pct: float) -> float | None:
        return round(t2_pct / t1_pct, 2) if t1_pct > 0 else None

    growth_t1_to_t2_v1 = {
        "pooled_rate_multiplier": _rate_mult(t2_v1["pooled"]["corpus_pct"], t1_v1["pooled"]["corpus_pct"]),
        "eng_algorithmic_proof_rate_multiplier": _rate_mult(
            t2_v1["by_role"]["eng_algorithmic_proof"]["corpus_pct"],
            t1_v1["by_role"]["eng_algorithmic_proof"]["corpus_pct"],
        ),
        "eng_algorithmic_proof_loc_median_multiplier": _rate_mult(
            t2_v1["by_role"]["eng_algorithmic_proof"]["median_owned_loc"],
            t1_v1["by_role"]["eng_algorithmic_proof"]["median_owned_loc"],
        ),
        "eng_strict_core_rate_multiplier": _rate_mult(
            t2_v1["eng_strict_core_non_borderline"]["corpus_pct"],
            t1_v1["eng_strict_core_non_borderline"]["corpus_pct"],
        ),
        "operational_system_fv_rate_multiplier": _rate_mult(
            t2_v1["by_role"]["operational_system_fv"]["corpus_pct"],
            t1_v1["by_role"]["operational_system_fv"]["corpus_pct"],
        ),
        "pure_math_or_tcs_rate_multiplier": _rate_mult(
            t2_v1["by_role"]["pure_math_or_tcs"]["corpus_pct"],
            t1_v1["by_role"]["pure_math_or_tcs"]["corpus_pct"],
        ),
    }

    return {
        "schema_version": "1.0",
        "rubric_version": adj_data["rubric_version"],
        "total_confirmed_papers_v_latest": len(all_enriched_papers),
        "borderline_count_total": sum(1 for p in all_enriched_papers if p["is_borderline"]),
        "borderline_arxiv_ids": sorted(p["arxiv_id"] for p in all_enriched_papers if p["is_borderline"]),
        "slices": enriched_slices,
        "growth_t1_to_t2_v1": growth_t1_to_t2_v1,
        "migration_old_3way_to_4way_all_47": migration_all,
        "migration_old_3way_to_4way_t2_39": migration_t2,
        "phase2_audits_by_role": phase2_overall_by_role,
        "sandbox_builds_by_role": sandbox_by_role,
        "v06_irr_disagreements_reconciled": irr_diagnostic,
        "papers_47": all_enriched_papers,
    }


def write_blank_coding_csv(summary: dict[str, Any], out_csv: Path) -> None:
    """Write blinded 47-paper CSV template for Phase B2 dual-rater (annotator_1 + annotator_2) IRR."""
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "slice_id",
        "short_id",
        "arxiv_id",
        "primary_category",
        "matched_target_cats",
        "title",
        "annotator_id",
        "role_4way",
        "verification_object",
        "borderline_flag",
        "notes",
    ]
    rows = sorted(summary["papers_47"], key=lambda p: (p["slice_id"], p["arxiv_id"]))
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in rows:
            writer.writerow(
                {
                    "slice_id": p["slice_id"],
                    "short_id": p["short_id"],
                    "arxiv_id": p["arxiv_id"],
                    "primary_category": p["primary_category"],
                    "matched_target_cats": ";".join(p["matched_target_cats"]),
                    "title": p["title"],
                    "annotator_id": "",
                    "role_4way": "",
                    "verification_object": "",
                    "borderline_flag": "",
                    "notes": "",
                }
            )


def _fmt_rate(stats: dict[str, Any]) -> str:
    lo, hi = stats["ci_95_pct"]
    if stats["count"] == 0:
        return f"0 (0.00%, UB {hi:.2f}%)"
    return f"{stats['count']} ({stats['corpus_pct']:.2f}%, [{lo:.2f}%, {hi:.2f}%])"


def write_markdown_report(summary: dict[str, Any], out_md: Path) -> None:
    t0, t1, t2 = summary["slices"]
    g = summary["growth_t1_to_t2_v1"]

    t1_eng_v1 = t1["modes"]["v1"]["by_role"]["eng_algorithmic_proof"]
    t2_eng_v1 = t2["modes"]["v1"]["by_role"]["eng_algorithmic_proof"]
    t2_pool_v1 = t2["modes"]["v1"]["pooled"]
    t2_pure_v1 = t2["modes"]["v1"]["by_role"]["pure_math_or_tcs"]
    t2_meta_v1 = t2["modes"]["v1"]["by_role"]["meta_formalization_system"]
    t2_sys_v1 = t2["modes"]["v1"]["by_role"]["operational_system_fv"]
    t1_sc_v1 = t1["modes"]["v1"]["eng_strict_core_non_borderline"]
    t2_sc_v1 = t2["modes"]["v1"]["eng_strict_core_non_borderline"]

    lines: list[str] = [
        "# Track 1 Sensitivity Analysis: 4-Way Role Decomposition of Confirmed Lean 4 Preprints (T0–T2, n = 47)",
        "",
        "> **Zero-Token Phase A1 Deliverable** · Rubric: [`docs/track1_4way_coding_rubric.md`](../docs/track1_4way_coding_rubric.md) · Adjudication: [`artifacts/human_annotations/track1_4way_adjudication.json`](../artifacts/human_annotations/track1_4way_adjudication.json) · Machine-readable output: [`artifacts/track1_sensitivity_summary.json`](../artifacts/track1_sensitivity_summary.json) · Phase B2 Dual-Rater Template: [`artifacts/human_annotations/track1_4way_coding_blank.csv`](../artifacts/human_annotations/track1_4way_coding_blank.csv)",
        "",
        "## 1. Executive Summary — What Holds vs. What Shifts Under Strict `eng_algorithmic_proof`",
        "",
        "Re-tabulating all **47** confirmed Lean 4 preprints (`T0`: 1 `v_latest` / 0 `v1`; `T1`: 7 `v_latest` / 5 `v1`; `T2`: 39 `v1` = `v_latest`) across the sharpened 4-way taxonomy (`eng_algorithmic_proof`, `operational_system_fv`, `pure_math_or_tcs`, `meta_formalization_system`) yields **five decisive empirical conclusions**:",
        "",
        f"1. **The 2026 Adoption Inflection Is Statistically Robust Even Under Strict Engineering-Only Filtering:** Restricting strictly to `eng_algorithmic_proof` moves the contemporaneous `v1` curve from **`0/2,435` (0.00%, 95% UB 0.12%) → `3/3,298` (0.09%, 95% CI [0.03%, 0.27%]) → `21/4,104` (0.51%, 95% CI [0.33%, 0.78%])** — a **{g['eng_algorithmic_proof_rate_multiplier']}×** rate jump in 6 months with **strictly non-overlapping 95% Wilson CIs**. Even under an ultra-strict *non-borderline core* stress test (excluding all {summary['borderline_count_total']} borderline papers across T1–T2, leaving `16` T2 vs. `1` T1), the 6-month rate still jumps **{g['eng_strict_core_rate_multiplier']}×** (`0.03% [0.01%, 0.17%] → 0.39% [0.24%, 0.63%]`, still non-overlapping!).",
        f"2. **Total Owned LoC Was Heavily Dominated by Pure-TCS & Meta-Systems (86.2%), While the *Median* Engineering Scale Jump (`39.2×`) Is Untouched:** Across the 28 scanned T2 repos (`{t2_pool_v1['total_owned_loc']:,}` owned LoC), **`pure_math_or_tcs`** (`{t2_pure_v1['total_owned_loc']:,}` LoC, **{t2_pure_v1['share_of_owned_loc_pct']:.1f}%**, median `{t2_pure_v1['median_owned_loc']:,}`) and **`meta_formalization_system`** (`{t2_meta_v1['total_owned_loc']:,}` LoC, **{t2_meta_v1['share_of_owned_loc_pct']:.1f}%**, median `{t2_meta_v1['median_owned_loc']:,}`) account for **86.2%** of all lines of code. Strict **`eng_algorithmic_proof`** contributes **`{t2_eng_v1['total_owned_loc']:,}` LoC ({t2_eng_v1['share_of_owned_loc_pct']:.1f}%)** across 15 scanned repos, yet its median codebase scale still leaps from **`{t1_eng_v1['median_owned_loc']:,}` → `{t2_eng_v1['median_owned_loc']:,}` LoC ({g['eng_algorithmic_proof_loc_median_multiplier']}×)** — virtually identical to the pooled `38.7×` shift (`749 → 29,005`), with no single contemporaneous T2 engineering paper exceeding `81.5k` LoC.",
        f"3. **`Tier3_Gold` Quality Share Actually *Increases* Under Strict Engineering Filtering:** `Tier3_Gold` rises from **48.7%** (`19/39`) pooled to **`{t2_eng_v1['tier3_gold_pct_of_bucket']:.1f}%` ({t2_eng_v1['tier3_gold_count']}/{t2_eng_v1['count']})** among T2 `eng_algorithmic_proof` papers (**{t2_eng_v1['tier3_gold_pct_of_scanned']:.1f}%** of scanned engineering repos!), outperforming `pure_math_or_tcs` (`{t2_pure_v1['tier3_gold_pct_of_bucket']:.1f}%`), `operational_system_fv` (`{t2_sys_v1['tier3_gold_pct_of_bucket']:.1f}%`), and `meta_formalization_system` (`{t2_meta_v1['tier3_gold_pct_of_bucket']:.1f}%`). Meanwhile, `P4` spec-lock splits cleanly: **1/3** (`2611.13872` *LongTails*) is a meta-system, leaving **2/21 (9.5%)** in `eng_algorithmic_proof` (`2611.04876`, `2611.14475`).",
        f"4. **Disciplinary Concentration Sharpens Dramatically (`cs.DC` Drops to 0 Pure-Engineering Papers):** Under the 4-way split, **100% of T2 `cs.DC` Lean papers (6/6)** are either `pure_math_or_tcs` (5) or `operational_system_fv` (1 — `cs.DB` DBLog), leaving **0** `eng_algorithmic_proof` papers in `cs.DC`. Strict engineering adoption is overwhelmingly concentrated in **`math.OC` (`13/724 = 1.80%`)**, **`cs.IT` (`4/338 = 1.18%`)**, **`cs.CR` (`3/629 = 0.48%`)**, and **`eess.SY` (`2/738 = 0.27%`)**.",
        f"5. **Phase 2 Layer-A Semantic Fidelity Has `0/15` Severe Failures Among Author-Owned T2 `eng_algorithmic_proof` Repos:** The sole `material_undisclosed_drift_or_risk` finding across all 23 Phase-2 audits (`2611.26272` *Paper2Lean*) belongs to **`meta_formalization_system`**, not `eng_algorithmic_proof`. Explicit AI disclosure in T2 is **`{t2_eng_v1['ai_explicit_yes_pct']:.1f}%`** (`14/21`) for `eng_algorithmic_proof`, vs. **`{t2_pure_v1['ai_explicit_yes_pct']:.1f}%`** (`10/11`) for `pure_math_or_tcs` and **`100.0%`** (`3/3`) for `meta_formalization_system`.",
        "",
        "---",
        "",
        "## 2. Stratified Longitudinal Adoption Curves (T0 → T1 → T2)",
        "",
        "### 2.1 Contemporaneous (`v1`-at-Submission) Adoption Rates & 95% CIs",
        "",
        "| Population / 4-Way Bucket | T0: Nov 2025 (N=2,435) | T1: May 2026 (N=3,298) | T2: Nov 2026 (N=4,104) | T2 Share of Confirmed | 6-Mo Rate Shift (`T1→T2`) |",
        "| :--- | :--- | :--- | :--- | ---: | :--- |",
    ]

    for label, getter in [
        ("**Pooled (All 4 Buckets)**", lambda sl: sl["modes"]["v1"]["pooled"]),
        ("**1. `eng_algorithmic_proof` (Core Target)**", lambda sl: sl["modes"]["v1"]["by_role"]["eng_algorithmic_proof"]),
        ("↳ *Strict Core (excl. borderline items)*", lambda sl: sl["modes"]["v1"]["eng_strict_core_non_borderline"]),
        ("2. `operational_system_fv`", lambda sl: sl["modes"]["v1"]["by_role"]["operational_system_fv"]),
        ("3. `pure_math_or_tcs`", lambda sl: sl["modes"]["v1"]["by_role"]["pure_math_or_tcs"]),
        ("4. `meta_formalization_system`", lambda sl: sl["modes"]["v1"]["by_role"]["meta_formalization_system"]),
    ]:
        s0, s1, s2 = getter(t0), getter(t1), getter(t2)
        share_str = "100.0%" if "Pooled" in label else f"{s2['share_of_confirmed_pct']:.1f}%"
        mult = f"**{s2['corpus_pct']/s1['corpus_pct']:.2f}×**" if s1["corpus_pct"] > 0 else "0 → active"
        lines.append(
            f"| {label} | {_fmt_rate(s0)} | {_fmt_rate(s1)} | {_fmt_rate(s2)} | {share_str} | {mult} |"
        )

    lines += [
        "",
        "### 2.2 Latest-Revision (`v_latest`, Including 3 Retroactive `v2` Formalizations)",
        "",
        "| Population / 4-Way Bucket | T0 `v_latest` (N=2,435) | T1 `v_latest` (N=3,298) | T2 `v_latest` (N=4,104) | Retroactive `v2` Additions |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    retro_notes = {
        "pooled": "`2511.15517` (T0), `2605.09552` & `2605.19531` (T1)",
        "eng_algorithmic_proof": "`2605.09552` (*Phases of Muon*, T1, 340.3k LoC)",
        "eng_strict_core_non_borderline": "`2605.09552` (T1)",
        "operational_system_fv": "`2511.15517` (T0 Beluga), `2605.19531` (T1 PODC, 34.3k LoC)",
        "pure_math_or_tcs": "None",
        "meta_formalization_system": "None",
    }
    for key, label, getter in [
        ("pooled", "**Pooled (All 4 Buckets)**", lambda sl: sl["modes"]["v_latest"]["pooled"]),
        ("eng_algorithmic_proof", "**1. `eng_algorithmic_proof`**", lambda sl: sl["modes"]["v_latest"]["by_role"]["eng_algorithmic_proof"]),
        ("eng_strict_core_non_borderline", "↳ *Strict Core (excl. borderline)*", lambda sl: sl["modes"]["v_latest"]["eng_strict_core_non_borderline"]),
        ("operational_system_fv", "2. `operational_system_fv`", lambda sl: sl["modes"]["v_latest"]["by_role"]["operational_system_fv"]),
        ("pure_math_or_tcs", "3. `pure_math_or_tcs`", lambda sl: sl["modes"]["v_latest"]["by_role"]["pure_math_or_tcs"]),
        ("meta_formalization_system", "4. `meta_formalization_system`", lambda sl: sl["modes"]["v_latest"]["by_role"]["meta_formalization_system"]),
    ]:
        s0, s1, s2 = getter(t0), getter(t1), getter(t2)
        lines.append(f"| {label} | {_fmt_rate(s0)} | {_fmt_rate(s1)} | {_fmt_rate(s2)} | {retro_notes[key]} |")

    lines += [
        "",
        "---",
        "",
        "## 3. T2 Codebase Scale, LoC Concentration, Paradigms, Tiers & AI Disclosure by 4-Way Bucket",
        "",
        "| 4-Way Bucket (T2 Nov 2026) | Papers | Scanned Repos | Total Owned LoC (% of 3.10M) | Median Owned LoC (Range) | `Tier3_Gold` (of Bucket / Scanned) | Paradigms (`P1/P2/P3/P4/P0`) | Explicit AI (`yes/unc/no`) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |",
    ]
    for label, s in [
        ("**1. `eng_algorithmic_proof`**", t2_eng_v1),
        ("↳ *Strict Core (non-borderline)*", t2_sc_v1),
        ("2. `operational_system_fv`", t2_sys_v1),
        ("3. `pure_math_or_tcs`", t2_pure_v1),
        ("4. `meta_formalization_system`", t2_meta_v1),
        ("**Pooled T2 Total**", t2_pool_v1),
    ]:
        loc_share = "100.0%" if "Pooled" in label else f"{s['share_of_owned_loc_pct']:.1f}%"
        loc_range = f"{s['min_owned_loc']:,}–{s['max_owned_loc']:,}" if s["scanned_owned_repos"] else "—"
        par_str = "/".join(
            str(s["paradigms"].get(p, 0))
            for p in (
                "P1_paper_first_posthoc",
                "P2_lean_first",
                "P3_blueprint_sync",
                "P4_speclock_solve_distill",
                "P0_opaque_or_unspecified",
            )
        )
        ai_str = f"{s['ai'].get('explicitly_yes',0)}/{s['ai'].get('unclear',0)}/{s['ai'].get('explicitly_no',0)} ({s['ai_explicit_yes_pct']:.1f}%)"
        gold_str = f"{s['tier3_gold_count']} ({s['tier3_gold_pct_of_bucket']:.1f}% / {s['tier3_gold_pct_of_scanned']:.1f}%)"
        lines.append(
            f"| {label} | {s['count']} | {s['scanned_owned_repos']} | {s['total_owned_loc']:,} ({loc_share}) | "
            f"**{s['median_owned_loc']:,}** ({loc_range}) | {gold_str} | `{par_str}` | {ai_str} |"
        )

    lines += [
        "",
        "### Scale Shift Comparison (`T1 v1 → T2 v1`)",
        f"- **Pooled:** median `{t1['modes']['v1']['pooled']['median_owned_loc']:,}` (3 repos) → `{t2_pool_v1['median_owned_loc']:,}` (28 repos) = **38.7×**.",
        f"- **Strict `eng_algorithmic_proof`:** median `{t1_eng_v1['median_owned_loc']:,}` (2 repos: `473` & `749`) → `{t2_eng_v1['median_owned_loc']:,}` (15 repos) = **{g['eng_algorithmic_proof_loc_median_multiplier']}×**.",
        f"- **Strict Core (non-borderline `eng_algorithmic_proof`):** median `{t1_sc_v1['median_owned_loc']:,}` (0 scanned T1 repos — `2605.03034` has no public repo) → `{t2_sc_v1['median_owned_loc']:,}` (12 repos, total `{t2_sc_v1['total_owned_loc']:,}` LoC, range `{t2_sc_v1['min_owned_loc']:,}`–`{t2_sc_v1['max_owned_loc']:,}`).",
        "",
        "---",
        "",
        "## 4. T2 Per-Category Breakdown Across the 8 Target Categories",
        "",
        "| Category | T2 Total | Pooled Lean (%) | `eng_algorithmic_proof` (%) | `operational_system_fv` | `pure_math_or_tcs` | `meta_formalization_system` |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cat in TARGET_CATEGORIES:
        tot_c = t2["cat_total"].get(cat, 0)
        p_c = t2_pool_v1["cat_counts"].get(cat, 0)
        e_c = t2_eng_v1["cat_counts"].get(cat, 0)
        s_c = t2_sys_v1["cat_counts"].get(cat, 0)
        m_c = t2_pure_v1["cat_counts"].get(cat, 0)
        meta_c = t2_meta_v1["cat_counts"].get(cat, 0)
        lines.append(
            f"| `{cat}` | {tot_c} | {p_c} ({100*p_c/max(tot_c,1):.2f}%) | **{e_c} ({100*e_c/max(tot_c,1):.2f}%)** | {s_c} | {m_c} | {meta_c} |"
        )
    lines.append("")
    lines.append("*(Category counts sum to >39 because papers cross-listed across multiple target categories are counted in each matched category, consistent with `report_longitudinal.py`.)*")

    lines += [
        "",
        "---",
        "",
        "## 5. Phase 2 Layer-A Audits (n = 23) & Sandboxed Docker Builds (n = 14) by 4-Way Bucket",
        "",
        "### 5.1 Phase 2 Adversarial Layer-A Semantic Fidelity Audits (`n = 23` Total: 20 T2 + 3 T1)",
        "",
        "| 4-Way Bucket | Audited Repos (`T2` / `T1 v1` / `T1 retro`) | `high_faithful` | `mostly_faithful` | `partial_or_weakened` | `material_undisclosed_drift` | Non-Vacuity Witnesses |",
        "| :--- | :---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for role in ROLES_4WAY:
        a = summary["phase2_audits_by_role"][role]
        fc = a["fidelity_counts"]
        lines.append(
            f"| `{role}` | **{a['count']}** (`{a['t2_count']}` / `{a['t1_v1_count']}` / `{a['t1_retro_v2_count']}`) | "
            f"{fc.get('high_faithful', 0)} | {fc.get('mostly_faithful_with_disclosed_gaps', 0)} | "
            f"{fc.get('partial_or_weakened_formalization', 0)} | **{a['material_undisclosed_count']}** | "
            f"{a['non_vacuity_count']}/{a['count']} |"
        )

    lines += [
        "",
        "### 5.2 Sandboxed Docker Dynamic Kernel Verification (`n = 14` Compact Repos `<15k` LoC)",
        "",
        "| 4-Way Bucket | Attempted | OOTB Pass | OOTB Axiom-Clean | Non-Std Axioms / `sorryAx` | Packaging / Local-Dep Fail (Synth. Pass) | Theorems Checked (OOTB / Incl. Synth.) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for role in ROLES_4WAY:
        sb = summary["sandbox_builds_by_role"][role]
        lines.append(
            f"| `{role}` | {sb['attempted']} | {sb['pass_ootb']} | {sb['pass_ootb_clean_axioms']} | "
            f"{sb['pass_ootb_nonstandard_axioms']} | {sb['fail_packaging_or_local_dep']} ({sb['synthetic_pass']}) | "
            f"{sb['theorems_ootb']:,} / {sb['theorems_incl_synthetic']:,} |"
        )
    lines.append("")
    lines.append(
        "*(All 5 OOTB-passing compact `eng_algorithmic_proof` repos — plus both packaging-only synthetic passes `2611.18220` and `2611.23762` — are 100% axiom-clean; both non-standard-axiom/sorryAx hits occurred outside `eng_algorithmic_proof`: `2605.16407` in `operational_system_fv` and `2611.16690` in `pure_math_or_tcs`.)*"
    )

    lines += [
        "",
        "---",
        "",
        "## 6. Old 3-Way → New 4-Way Migration Matrix & Stage-4 IRR Reconciliation Diagnostic",
        "",
        "### 6.1 Migration Matrix (All 47 Confirmed Papers `v_latest`; T2 `n = 39` in Parentheses)",
        "",
        "| Old v0.6 `paper_domain_role` | `eng_algorithmic_proof` | `operational_system_fv` | `pure_math_or_tcs` | `meta_formalization_system` | Total |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for old_r in ("engineering_math_proof", "software_or_system_fv", "pure_tcs_or_math"):
        row_all = summary["migration_old_3way_to_4way_all_47"].get(old_r, {})
        row_t2 = summary["migration_old_3way_to_4way_t2_39"].get(old_r, {})
        cells = [f"{row_all.get(nr, 0)} ({row_t2.get(nr, 0)})" for nr in ROLES_4WAY]
        tot_a = sum(row_all.values())
        tot_2 = sum(row_t2.values())
        lines.append(f"| `{old_r}` | {' | '.join(cells)} | **{tot_a} ({tot_2})** |")

    lines += [
        "",
        f"### 6.2 How the 4-Way Rubric Resolves the 9 v0.6 Blinded IRR Disagreements (`annotator_1` vs. LLM)",
        "",
        "| arXiv ID | `annotator_1` (Old 3-Way) | LLM (Old 3-Way) | Adjudicated `role_4way` | Resolution Mechanism |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for d in summary["v06_irr_disagreements_reconciled"]:
        b_tag = " *(borderline)*" if d["is_borderline"] else ""
        lines.append(
            f"| `{d['arxiv_id']}` | `{d['annotator_1_old_3way']}` | `{d['llm_old_3way']}` | "
            f"`{d['adjudicated_role_4way']}`{b_tag} | `{d['resolution_type']}` (`{d['decision_gate']}`) |"
        )

    res_counts = Counter(d["resolution_type"] for d in summary["v06_irr_disagreements_reconciled"])
    lines += [
        "",
        f"- **Immediate structural fixes (4/9):** `{res_counts['resolved_by_new_meta_bucket']}` meta-systems (`2611.13872`, `2611.23080`) move to the new `meta_formalization_system` bucket that `annotator_1` explicitly requested, and `{res_counts['aligned_with_human_rater']}` pure-math cross-lists (`2611.08172`, `2611.09050`) align directly with `annotator_1` as `pure_math_or_tcs`.",
        f"- **Explicit boundary-rule clarifications (5/9):** `{res_counts['clarified_by_explicit_boundary_rule']}` remaining items (`2605.02856`, `2605.14610`, `2605.19531`, `2611.01384`, `2611.01761`) map 1-to-1 to Rules B2–B4 in [`docs/track1_4way_coding_rubric.md`](../docs/track1_4way_coding_rubric.md) and will be independently re-coded by `annotator_1` and `annotator_2` in Phase B2.",
        "",
        "---",
        "",
        "## 7. Complete 47-Paper 4-Way Adjudication Inventory (`T0 + T1 + T2`, `v_latest`)",
        "",
        "| Slice | arXiv ID | Timing | Prim. (`Targets`) | Old 3-Way | New `role_4way` | `verification_object` | Borderline? | Owned LoC | Tier / Par. |",
        "| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | ---: | :--- |",
    ]
    for p in sorted(summary["papers_47"], key=lambda x: (x["slice_id"], x["arxiv_id"])):
        timing = "Retro `v2`" if p["is_retroactive_v2"] else "`v1`"
        tcats = ",".join(p["matched_target_cats"])
        loc_s = f"{p['primary_owned_loc']:,}" if p["primary_owned_loc"] else "—"
        b_s = f"Yes (`{p['borderline_alt_role']}`)" if p["is_borderline"] else "No"
        par_short = p["authoring_paradigm"].split("_")[0]
        tier_short = p["verification_tier"].split("_")[1]
        lines.append(
            f"| {p['short_id']} | [{p['arxiv_id']}](https://arxiv.org/abs/{p['arxiv_id']}) | {timing} | "
            f"`{p['primary_category']}` (`{tcats}`) | `{p['old_paper_domain_role']}` | **`{p['role_4way']}`** | "
            f"`{p['verification_object']}` | {b_s} | {loc_s} | {tier_short} / `{par_short}` |"
        )

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute Track 1 4-way sensitivity breakdown over existing 47 Lean papers.")
    ap.add_argument("--longitudinal", type=Path, default=DEFAULT_LONGITUDINAL)
    ap.add_argument("--adjudication", type=Path, default=DEFAULT_ADJUDICATION)
    ap.add_argument("--sandbox-dir", type=Path, default=DEFAULT_SANDBOX_DIR)
    ap.add_argument("--irr-csv", type=Path, default=DEFAULT_IRR_CSV)
    ap.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    ap.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    ap.add_argument("--blank-csv-out", type=Path, default=DEFAULT_BLANK_CSV_OUT)
    args = ap.parse_args()

    summary = compute_sensitivity(
        longitudinal_path=args.longitudinal,
        adjudication_path=args.adjudication,
        sandbox_dir=args.sandbox_dir,
        irr_csv_path=args.irr_csv,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(summary, args.md_out)
    write_blank_coding_csv(summary, args.blank_csv_out)
    print(f"Wrote {args.json_out}, {args.md_out}, and {args.blank_csv_out}")


if __name__ == "__main__":
    main()
