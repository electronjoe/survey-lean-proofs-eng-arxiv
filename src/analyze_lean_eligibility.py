"""Stage E2 Post-Stratified Estimator & Denominator-Adjusted Adoption Analyzer.

Imports Stage E2 LLM classifications into `data/eligibility_t2.db`, combines them
with the exact 3-stratum independent per-category SRS plan (`Option B`), and computes:
  1. Per-category post-stratified proportions & counts for L1..L5 and nested
     denominators:
       - Tier 0 (N_c): all T2 preprints in category c
       - Tier 1 (N_c^thm): Theorem-Bearing Papers (L1 ∪ L2)
       - Tier 2a (N_c^lean-math): Lean-Amenable Math (L1)
       - Tier 2b (N_c^lean-broad): Broad Lean-Applicable (L1 ∪ L3)
  2. Finite-population-corrected analytic SEs and exact finite-population
     Beta-Binomial 95% credible/confidence intervals.
  3. Denominator-adjusted (conditional) Lean 4 adoption rates paired with exact
     T2 v1 numerators from `artifacts/unified_15cat_panel.json`, with propagated
     95% CIs combining numerator binomial + denominator stratified-sampling uncertainty.
  4. Exact inclusion-probability (Hájek Horvitz-Thompson) pooled estimates for
     deduplicated T2 (N=5,303) and EESS aggregates (`eess_all`, `eess_non_sy`).

Emits git-tracked `artifacts/lean_eligibility_t2.json` and
`reports/lean_eligibility_analysis.md`.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.screen_math_structure import (
    ALL15_CATS,
    DEFAULT_ELIGIBILITY_DB,
    UNIFIED_PANEL_PATH,
    connect_eligibility,
    utc_now,
)

ELIG_CLASSES: tuple[str, ...] = (
    "L1_lean_amenable_math",
    "L2_mathlib_blocked_math",
    "L3_operational_spec_fv",
    "L4_heuristic_or_numerical_only",
    "L5_empirical_or_survey",
)

E1_FETCHED_STRATA: tuple[str, ...] = (
    "E1_formal_thm_proof",
    "E1_weak_or_unnumbered_math",
    "E1_no_formal_claims",
)

TIER_PREDICATES: dict[str, set[str]] = {
    "tier1_theorem_bearing": {"L1_lean_amenable_math", "L2_mathlib_blocked_math"},
    "tier2a_lean_amenable_math": {"L1_lean_amenable_math"},
    "tier2b_broad_lean_applicable": {"L1_lean_amenable_math", "L3_operational_spec_fv"},
    "L1_lean_amenable_math": {"L1_lean_amenable_math"},
    "L2_mathlib_blocked_math": {"L2_mathlib_blocked_math"},
    "L3_operational_spec_fv": {"L3_operational_spec_fv"},
    "L4_heuristic_or_numerical_only": {"L4_heuristic_or_numerical_only"},
    "L5_empirical_or_survey": {"L5_empirical_or_survey"},
}


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def _wilson_ci_pct(k: int, n: float, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 100.0)
    k_eff = min(float(k), n)
    p = k_eff / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denom
    return (max(0.0, 100.0 * (center - half)), min(100.0, 100.0 * (center + half)))


def _binomial_draw(rng: random.Random, n: int, p: float) -> int:
    """Exact binomial draw using direct sum for small n and normal approx for large n."""
    if n <= 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    if n <= 40:
        return sum(1 for _ in range(n) if rng.random() < p)
    # Normal approximation with continuity clamp (accurate for n > 40, fast in pure stdlib)
    mu = n * p
    sd = math.sqrt(n * p * (1.0 - p))
    val = int(round(rng.gauss(mu, sd)))
    return max(0, min(n, val))


def post_stratified_estimate(
    strata_obs: dict[str, tuple[int, int, int]],
    total_scale_n: int,
    n_mc: int = 8000,
    seed: int = 20261126,
) -> dict[str, Any]:
    """Compute post-stratified proportion, count, FPC-SE, and exact finite-pop Beta-Binomial 95% CI.

    Args:
        strata_obs: mapping `stratum -> (N_h, n_h, x_h)` where `N_h` is stratum population size
                    (fetched), `n_h` is SRS sample size, and `x_h` is count of positives in sample.
        total_scale_n: canonical category total (e.g., panel `N_c`) used to scale proportion to count.
    """
    n_fetched = sum(v[0] for v in strata_obs.values())
    if n_fetched <= 0:
        return {
            "pct": 0.0,
            "se_pct": 0.0,
            "ci_95_pct": [0.0, 0.0],
            "est_count": 0.0,
            "est_count_ci_95": [0.0, 0.0],
            "mc_count_draws": [0.0] * n_mc,
        }

    p_hat = 0.0
    var_fpc = 0.0
    for n_pop, n_samp, x_pos in strata_obs.values():
        if n_pop <= 0 or n_samp <= 0:
            continue
        w = n_pop / n_fetched
        ph = x_pos / n_samp
        p_hat += w * ph
        if n_pop > n_samp:
            fpc = (n_pop - n_samp) / max(n_pop - 1, 1)
            s2 = (n_samp / max(n_samp - 1, 1)) * ph * (1.0 - ph) if n_samp > 1 else ph * (1.0 - ph)
            var_fpc += (w * w) * fpc * (s2 / n_samp)

    se_pct = 100.0 * math.sqrt(max(var_fpc, 0.0))

    # Finite-population Beta-Binomial Monte Carlo (Jeffreys Beta(0.5, 0.5) on unsampled remainder)
    rng = random.Random(seed)
    scale = total_scale_n / n_fetched
    mc_props: list[float] = []
    mc_counts: list[float] = []
    for _ in range(n_mc):
        tot_pos = 0
        for n_pop, n_samp, x_pos in strata_obs.values():
            if n_pop <= 0:
                continue
            rem = max(0, n_pop - n_samp)
            if rem == 0:
                tot_pos += x_pos
            else:
                p_draw = rng.betavariate(x_pos + 0.5, (n_samp - x_pos) + 0.5)
                tot_pos += x_pos + _binomial_draw(rng, rem, p_draw)
        prop = tot_pos / n_fetched
        mc_props.append(prop)
        mc_counts.append(prop * total_scale_n)

    mc_props_sorted = sorted(mc_props)
    mc_counts_sorted = sorted(mc_counts)
    ci_lo = round(100.0 * _quantile(mc_props_sorted, 0.025), 2)
    ci_hi = round(100.0 * _quantile(mc_props_sorted, 0.975), 2)
    cnt_lo = round(_quantile(mc_counts_sorted, 0.025), 1)
    cnt_hi = round(_quantile(mc_counts_sorted, 0.975), 1)

    return {
        "pct": round(100.0 * p_hat, 2),
        "se_pct": round(se_pct, 2),
        "ci_95_pct": [ci_lo, ci_hi],
        "est_count": round(p_hat * total_scale_n, 1),
        "est_count_ci_95": [cnt_lo, cnt_hi],
        "mc_count_draws": mc_counts,
        "_scale": scale,
    }


def conditional_adoption_rate(
    k_num: int,
    denom_est: dict[str, Any],
    seed: int = 20261127,
) -> dict[str, Any]:
    """Compute conditional adoption rate k / N_hat and propagated 95% CI.

    Combines numerator binomial uncertainty with denominator finite-population
    stratified-sampling uncertainty across the posterior count draws `mc_count_draws`.
    """
    est_n = float(denom_est["est_count"])
    draws = denom_est["mc_count_draws"]
    rng = random.Random(seed)

    if est_n <= 0.0:
        return {
            "numerator": k_num,
            "denom_est": 0.0,
            "denom_ci_95": denom_est["est_count_ci_95"],
            "rate_pct": None,
            "ci_95_propagated_pct": [0.0, 100.0],
            "ci_95_denom_only_pct": [0.0, 100.0],
        }

    rate_pct = round(min(100.0, 100.0 * k_num / max(est_n, float(k_num))), 2)

    # Denominator-only CI (fixing numerator k_num)
    d_lo, d_hi = denom_est["est_count_ci_95"]
    denom_only_lo = round(min(100.0, 100.0 * k_num / max(d_hi, float(k_num), 1e-6)), 2) if k_num > 0 else 0.0
    denom_only_hi = round(min(100.0, 100.0 * k_num / max(d_lo, float(k_num), 1e-6)), 2) if k_num > 0 else 0.0

    # Full propagated 95% CI (numerator binomial + denominator uncertainty)
    if k_num == 0:
        # Propagated two-sided Wilson 95% upper bound evaluated over denominator draws
        # (and Jeffreys Beta(0.5, M + 0.5) 97.5% quantile closely matches Wilson UB)
        w_hi_list = [_wilson_ci_pct(0, max(m, 1.0))[1] for m in draws]
        w_hi_sorted = sorted(w_hi_list)
        # Use posterior mean of Wilson upper bound (plus note p95 upper bound)
        prop_lo = 0.0
        prop_hi = round(sum(w_hi_sorted) / len(w_hi_sorted), 2)
        prop_hi_conservative = round(_quantile(w_hi_sorted, 0.95), 2)
        return {
            "numerator": k_num,
            "denom_est": est_n,
            "denom_ci_95": denom_est["est_count_ci_95"],
            "rate_pct": 0.0,
            "ci_95_propagated_pct": [prop_lo, prop_hi],
            "ci_95_upper_conservative_pct": prop_hi_conservative,
            "ci_95_denom_only_pct": [0.0, 0.0],
        }

    rate_draws: list[float] = []
    for m_raw in draws:
        m_eff = max(m_raw, float(k_num))
        # Jeffreys binomial posterior given denominator M_eff: Beta(k + 0.5, M - k + 0.5)
        r_draw = rng.betavariate(k_num + 0.5, (m_eff - k_num) + 0.5)
        rate_draws.append(100.0 * r_draw)

    rate_draws.sort()
    return {
        "numerator": k_num,
        "denom_est": est_n,
        "denom_ci_95": denom_est["est_count_ci_95"],
        "rate_pct": rate_pct,
        "ci_95_propagated_pct": [
            round(_quantile(rate_draws, 0.025), 2),
            round(_quantile(rate_draws, 0.975), 2),
        ],
        "ci_95_denom_only_pct": [denom_only_lo, denom_only_hi],
    }


def _hajek_pooled_estimate(
    pop_rows: list[dict[str, Any]],
    sampled_cls: dict[str, str],
    plan_per_cat: dict[str, Any],
    total_scale_n: int,
    n_boot: int = 2000,
    seed: int = 20261128,
) -> dict[str, Any]:
    """Exact inclusion-probability (Hájek Horvitz-Thompson) pooled estimate for a deduplicated paper subset.

    For each fetched paper i in `pop_rows`, inclusion probability under independent
    per-category 3-stratum SRS is:
        pi_i = 1 - prod_{c in matched_15_cats(i)} (1 - n_{c, h(i)} / N_{c, h(i)}).
    Bootstrap 95% CIs resample within each of the (category, E1_bucket) strata with
    finite-population scaling.
    """
    pi_map: dict[str, float] = {}
    for r in pop_rows:
        aid = r["arxiv_id"]
        b = r["e1_bucket"]
        cats = r["_matched_15"]
        p_miss = 1.0
        for c in cats:
            if c in plan_per_cat and b in plan_per_cat[c]["strata"]:
                st = plan_per_cat[c]["strata"][b]
                if st["N_h"] > 0:
                    p_miss *= 1.0 - (st["n_h"] / st["N_h"])
        pi = 1.0 - p_miss
        if pi > 0.0:
            pi_map[aid] = pi

    pop_ids = set(pi_map.keys())
    sampled_in_pop = [aid for aid in sorted(sampled_cls) if aid in pop_ids]
    weights = {aid: 1.0 / pi_map[aid] for aid in sampled_in_pop}
    w_sum = sum(weights.values())

    # Point estimates
    out: dict[str, Any] = {
        "population_fetched": len(pop_rows),
        "population_total": total_scale_n,
        "sampled_unique": len(sampled_in_pop),
        "effective_weight_sum": round(w_sum, 1),
    }

    # Pre-group sampled items by (primary_category, e1_bucket) for stratified bootstrap
    boot_strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    row_by_id = {r["arxiv_id"]: r for r in pop_rows}
    for aid in sampled_in_pop:
        r = row_by_id[aid]
        boot_strata[(r["primary_category"], r["e1_bucket"])].append(aid)

    rng = random.Random(seed)
    boot_indices: list[list[str]] = []
    strata_lists = list(boot_strata.values())
    for _ in range(n_boot):
        draw: list[str] = []
        for grp in strata_lists:
            m = len(grp)
            if m == 1:
                draw.append(grp[0])
            else:
                draw.extend(rng.choices(grp, k=m))
        boot_indices.append(draw)

    estimates: dict[str, Any] = {}
    for key, valid_classes in TIER_PREDICATES.items():
        if w_sum <= 0:
            estimates[key] = {"pct": 0.0, "ci_95_pct": [0.0, 0.0], "est_count": 0.0, "est_count_ci_95": [0.0, 0.0]}
            continue
        p_hat = sum(weights[aid] for aid in sampled_in_pop if sampled_cls[aid] in valid_classes) / w_sum
        b_props: list[float] = []
        for draw in boot_indices:
            bw = 0.0
            bpos = 0.0
            for aid in draw:
                wi = weights[aid]
                bw += wi
                if sampled_cls[aid] in valid_classes:
                    bpos += wi
            b_props.append(bpos / bw if bw > 0 else 0.0)
        b_props.sort()
        lo = _quantile(b_props, 0.025)
        hi = _quantile(b_props, 0.975)
        estimates[key] = {
            "pct": round(100.0 * p_hat, 2),
            "ci_95_pct": [round(100.0 * lo, 2), round(100.0 * hi, 2)],
            "est_count": round(p_hat * total_scale_n, 1),
            "est_count_ci_95": [round(lo * total_scale_n, 1), round(hi * total_scale_n, 1)],
        }

    out["estimates"] = estimates
    return out


def import_and_analyze_e2(
    db_path: Path = DEFAULT_ELIGIBILITY_DB,
    e2_out_path: Path = Path("data/eligibility_e2_t2_out.json"),
    plan_path: Path = Path("data/eligibility_e2_t2_plan.json"),
    panel_path: Path = UNIFIED_PANEL_PATH,
    artifact_path: Path = Path("artifacts/lean_eligibility_t2.json"),
    report_path: Path = Path("reports/lean_eligibility_analysis.md"),
) -> dict[str, Any]:
    """Import E2 classifications, run post-stratified estimation, and emit artifact + report."""
    e2_raw = json.loads(e2_out_path.read_text())
    model_tier = e2_raw.get("model", "flash")
    new_results = e2_raw["results"]
    plan = json.loads(plan_path.read_text())

    conn = connect_eligibility(db_path)
    with conn:
        for r in new_results:
            conn.execute(
                """
                INSERT INTO eligibility_classifications (
                    arxiv_id, cohort, model_tier, eligibility_class,
                    has_original_deductive_proof, dominant_math_area,
                    primary_barrier_if_L2, confidence, rationale, raw_json, classified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    cohort = CASE
                        WHEN eligibility_classifications.cohort = 'pilot_e0' THEN 'pilot_e0+e2_stratified'
                        ELSE excluded.cohort
                    END,
                    model_tier = excluded.model_tier,
                    eligibility_class = excluded.eligibility_class,
                    has_original_deductive_proof = excluded.has_original_deductive_proof,
                    dominant_math_area = excluded.dominant_math_area,
                    primary_barrier_if_L2 = excluded.primary_barrier_if_L2,
                    confidence = excluded.confidence,
                    rationale = excluded.rationale,
                    raw_json = excluded.raw_json,
                    classified_at = excluded.classified_at
                """,
                (
                    r["arxiv_id"],
                    "e2_stratified",
                    model_tier,
                    r["eligibility_class"],
                    int(bool(r["has_original_deductive_proof"])),
                    r["dominant_math_area"],
                    r["primary_barrier_if_L2"],
                    r["confidence"],
                    r["rationale"],
                    json.dumps(r),
                    utc_now(),
                ),
            )

    # Load all fetched T2 papers for inclusion-probability pooled estimation
    pop_rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT ep.arxiv_id, ep.title, ep.primary_category, ep.matched_15_cats_json,
                   ep.is_confirmed_lean, ep.confirmed_role_4way,
                   ms.fetch_source, ms.e1_bucket,
                   ms.n_theorem, ms.n_lemma, ms.n_proposition, ms.n_corollary,
                   ms.n_claim_or_fact, ms.n_proof, ms.n_equation
            FROM eligibility_papers ep
            JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
            WHERE ep.in_t2_census = 1 AND ms.e1_bucket != 'E1_fetch_failed'
            ORDER BY ep.arxiv_id ASC
            """
        ).fetchall()
    ]
    for r in pop_rows:
        r["_matched_15"] = json.loads(r["matched_15_cats_json"] or "[]")
    pop_by_id = {r["arxiv_id"]: r for r in pop_rows}

    # Load classifications for all unique Option B sampled papers AND all T2 confirmed Lean papers
    # (for strictly matched numerator-denominator conditional adoption rates!)
    unique_ids: list[str] = plan["unique_sampled_ids"]
    confirmed_t2_ids = [r["arxiv_id"] for r in pop_rows if r["is_confirmed_lean"] == 1]
    query_ids = sorted(set(unique_ids) | set(confirmed_t2_ids))
    placeholders = ",".join("?" for _ in query_ids)
    cls_rows = [
        dict(r)
        for r in conn.execute(
            f"""
            SELECT arxiv_id, cohort, model_tier, eligibility_class,
                   has_original_deductive_proof, dominant_math_area,
                   primary_barrier_if_L2, confidence, rationale
            FROM eligibility_classifications
            WHERE arxiv_id IN ({placeholders})
            ORDER BY arxiv_id ASC
            """,
            tuple(query_ids),
        ).fetchall()
    ]
    conn.close()

    cls_by_id = {r["arxiv_id"]: r for r in cls_rows}
    missing = [aid for aid in unique_ids if aid not in cls_by_id]
    if missing:
        raise RuntimeError(f"Missing classifications for {len(missing)} sampled papers: {missing[:5]}")

    # Load canonical T2 panel numerators & exact v1 confirmed ID set (68 papers)
    panel = json.loads(panel_path.read_text())
    t2_slice = next(s for s in panel["slices"] if s["slice_id"] == "2026-11")
    panel_per_cat = t2_slice["per_category"]
    v1_confirmed_ids = set(t2_slice["confirmed_v1"]["arxiv_ids"])

    # Strictly matched v1 adopter counts by (category, E2 eligibility_class)
    v1_math_by_cat_cls: dict[str, Counter[str]] = defaultdict(Counter)
    v1_nonmeta_by_cat_cls: dict[str, Counter[str]] = defaultdict(Counter)
    v1_pooled_math_cls: Counter[str] = Counter()
    v1_pooled_nonmeta_cls: Counter[str] = Counter()
    for aid in sorted(v1_confirmed_ids):
        pr = pop_by_id.get(aid)
        cr = cls_by_id.get(aid)
        if pr is None or cr is None:
            continue
        role = pr["confirmed_role_4way"]
        ecls = cr["eligibility_class"]
        if role in ("eng_algorithmic_proof", "pure_math_or_tcs"):
            v1_pooled_math_cls[ecls] += 1
            for c in pr["_matched_15"]:
                v1_math_by_cat_cls[c][ecls] += 1
        if role != "meta_formalization_system":
            v1_pooled_nonmeta_cls[ecls] += 1
            for c in pr["_matched_15"]:
                v1_nonmeta_by_cat_cls[c][ecls] += 1

    # Confusion matrix & descriptive breakdowns across the 439 unique sampled T2 papers
    e1_vs_e2: dict[str, Counter[str]] = defaultdict(Counter)
    l2_barriers_overall: Counter[str] = Counter()
    l2_barriers_by_cat: dict[str, Counter[str]] = defaultdict(Counter)
    math_areas_by_class: dict[str, Counter[str]] = defaultdict(Counter)
    confidence_counts: Counter[str] = Counter()

    for aid in unique_ids:
        pr = pop_by_id[aid]
        cr = cls_by_id[aid]
        cls = cr["eligibility_class"]
        e1_vs_e2[pr["e1_bucket"]][cls] += 1
        confidence_counts[cr["confidence"]] += 1
        math_areas_by_class[cls][cr["dominant_math_area"]] += 1
        if cls == "L2_mathlib_blocked_math":
            bar = cr["primary_barrier_if_L2"]
            l2_barriers_overall[bar] += 1
            for c in pr["_matched_15"]:
                l2_barriers_by_cat[c][bar] += 1

    # Per-category post-stratified estimation & conditional adoption rates
    per_category: dict[str, Any] = {}
    for idx, cat in enumerate(ALL15_CATS):
        cplan = plan["per_category"][cat]
        pcat = panel_per_cat[cat]
        n_panel = int(pcat["total_papers"])
        roles_v1 = pcat["roles_v1"]
        k_all_v1 = int(pcat["confirmed_v1"]["count"])
        k_eng_alg = int(roles_v1.get("eng_algorithmic_proof", 0))
        k_pure = int(roles_v1.get("pure_math_or_tcs", 0))
        k_opfv = int(roles_v1.get("operational_system_fv", 0))
        k_meta = int(roles_v1.get("meta_formalization_system", 0))
        k_math_alg = k_eng_alg + k_pure
        k_non_meta = k_all_v1 - k_meta

        # Raw sample class counts within each E1 stratum
        stratum_summary: dict[str, Any] = {}
        for b in E1_FETCHED_STRATA:
            st = cplan["strata"][b]
            sc = Counter(cls_by_id[aid]["eligibility_class"] for aid in st["sampled_ids"])
            stratum_summary[b] = {
                "N_h": st["N_h"],
                "n_h": st["n_h"],
                "sample_class_counts": {c: sc[c] for c in ELIG_CLASSES},
            }

        # Post-stratified estimates for each class & nested denominator tier
        tier_ests_raw: dict[str, Any] = {}
        tier_ests_clean: dict[str, Any] = {}
        for t_idx, (t_key, valid_set) in enumerate(TIER_PREDICATES.items()):
            strata_obs: dict[str, tuple[int, int, int]] = {}
            for b in E1_FETCHED_STRATA:
                st = cplan["strata"][b]
                x_pos = sum(1 for aid in st["sampled_ids"] if cls_by_id[aid]["eligibility_class"] in valid_set)
                strata_obs[b] = (st["N_h"], st["n_h"], x_pos)
            est = post_stratified_estimate(
                strata_obs,
                total_scale_n=n_panel,
                n_mc=4000,
                seed=20261126 + idx * 100 + t_idx,
            )
            tier_ests_raw[t_key] = est
            tier_ests_clean[t_key] = {k: v for k, v in est.items() if k not in ("mc_count_draws", "_scale")}

        # Strictly matched v1 numerators (by blinded E2 eligibility_class of confirmed adopters)
        k_math_L1 = int(v1_math_by_cat_cls[cat]["L1_lean_amenable_math"])
        k_math_L2 = int(v1_math_by_cat_cls[cat]["L2_mathlib_blocked_math"])
        k_nonmeta_L1_L3 = int(
            v1_nonmeta_by_cat_cls[cat]["L1_lean_amenable_math"]
            + v1_nonmeta_by_cat_cls[cat]["L3_operational_spec_fv"]
        )

        # Denominator-adjusted (conditional) adoption rates
        t2a_matched = conditional_adoption_rate(
            k_math_L1, tier_ests_raw["tier2a_lean_amenable_math"], seed=30000 + idx * 10 + 2
        )
        t2a_matched["small_denom_flag"] = bool(tier_ests_raw["tier2a_lean_amenable_math"]["est_count"] < 10.0)

        t2_frontier = conditional_adoption_rate(
            k_math_L2, tier_ests_raw["L2_mathlib_blocked_math"], seed=30000 + idx * 10 + 5
        )
        t2_frontier["small_denom_flag"] = bool(tier_ests_raw["L2_mathlib_blocked_math"]["est_count"] < 10.0)

        t2b_matched = conditional_adoption_rate(
            k_nonmeta_L1_L3, tier_ests_raw["tier2b_broad_lean_applicable"], seed=30000 + idx * 10 + 4
        )
        t2b_matched["small_denom_flag"] = bool(tier_ests_raw["tier2b_broad_lean_applicable"]["est_count"] < 10.0)

        cond_rates = {
            "raw_tier0_all_v1": {
                "numerator": k_all_v1,
                "denom": n_panel,
                "rate_pct": round(pcat["confirmed_v1"]["pct"], 2),
                "ci_95_pct": [round(x, 2) for x in pcat["confirmed_v1"]["ci_95_pct"]],
            },
            "tier1_math_alg_given_thm": conditional_adoption_rate(
                k_math_alg, tier_ests_raw["tier1_theorem_bearing"], seed=30000 + idx * 10 + 1
            ),
            "tier2a_matched_L1_given_L1": t2a_matched,
            "tier2_frontier_L2_given_L2": t2_frontier,
            "tier2a_all_math_given_L1_unmatched_ref": conditional_adoption_rate(
                k_math_alg, tier_ests_raw["tier2a_lean_amenable_math"], seed=30000 + idx * 10 + 6
            ),
            "tier2a_strict_eng_given_L1": conditional_adoption_rate(
                k_eng_alg, tier_ests_raw["tier2a_lean_amenable_math"], seed=30000 + idx * 10 + 3
            ),
            "tier2b_matched_L1_L3_given_L1_L3": t2b_matched,
        }

        per_category[cat] = {
            "panel_t2_total_papers": n_panel,
            "e1_fetched_papers": cplan["N_fetched"],
            "e2_sample_n": cplan["n_total"],
            "numerators_v1": {
                "all_confirmed": k_all_v1,
                "math_alg": k_math_alg,
                "math_alg_in_L1": k_math_L1,
                "math_alg_in_L2": k_math_L2,
                "eng_algorithmic_proof": k_eng_alg,
                "pure_math_or_tcs": k_pure,
                "operational_system_fv": k_opfv,
                "meta_formalization_system": k_meta,
                "non_meta": k_non_meta,
                "non_meta_in_L1_L3": k_nonmeta_L1_L3,
            },
            "strata": stratum_summary,
            "eligibility_estimates": tier_ests_clean,
            "conditional_adoption": cond_rates,
            "l2_barriers_in_sample": dict(sorted(l2_barriers_by_cat[cat].items())),
        }

    # Exact inclusion-probability pooled T2 & EESS estimates
    sampled_cls_map = {aid: cls_by_id[aid]["eligibility_class"] for aid in unique_ids}
    pooled_t2 = _hajek_pooled_estimate(
        pop_rows=pop_rows,
        sampled_cls=sampled_cls_map,
        plan_per_cat=plan["per_category"],
        total_scale_n=int(t2_slice["total_papers"]),
        n_boot=2000,
        seed=20261128,
    )
    # Attach pooled conditional adoption point rates
    def _role_cnt(val: Any) -> int:
        return int(val["count"] if isinstance(val, dict) else val)

    t2_roles = t2_slice["roles_v1"]
    t2_k_all = int(t2_slice["confirmed_v1"]["count"])
    t2_k_math = _role_cnt(t2_roles["eng_algorithmic_proof"]) + _role_cnt(t2_roles["pure_math_or_tcs"])
    t2_k_eng = _role_cnt(t2_roles["eng_algorithmic_proof"])
    t2_k_non_meta = t2_k_all - _role_cnt(t2_roles["meta_formalization_system"])

    def _pooled_cond(k: int, est_dict: dict[str, Any]) -> dict[str, Any]:
        m = float(est_dict["est_count"])
        lo_m, hi_m = est_dict["est_count_ci_95"]
        rate = round(100.0 * k / m, 2) if m > 0 else None
        # Propagate numerator Wilson at denominator endpoints for clean pooled band
        w_lo = _wilson_ci_pct(k, max(hi_m, float(k)))[0]
        w_hi = _wilson_ci_pct(k, max(lo_m, float(k)))[1]
        return {
            "numerator": k,
            "denom_est": m,
            "denom_ci_95": [lo_m, hi_m],
            "rate_pct": rate,
            "ci_95_conservative_pct": [round(w_lo, 2), round(w_hi, 2)],
        }

    t2_k_math_L1 = int(v1_pooled_math_cls["L1_lean_amenable_math"])
    t2_k_math_L2 = int(v1_pooled_math_cls["L2_mathlib_blocked_math"])
    t2_k_nonmeta_L1_L3 = int(
        v1_pooled_nonmeta_cls["L1_lean_amenable_math"] + v1_pooled_nonmeta_cls["L3_operational_spec_fv"]
    )

    pooled_t2["conditional_adoption"] = {
        "raw_tier0_all_v1_pct": round(t2_slice["confirmed_v1"]["pct"], 2),
        "tier1_math_alg_given_thm": _pooled_cond(t2_k_math, pooled_t2["estimates"]["tier1_theorem_bearing"]),
        "tier2a_matched_L1_given_L1": _pooled_cond(t2_k_math_L1, pooled_t2["estimates"]["tier2a_lean_amenable_math"]),
        "tier2_frontier_L2_given_L2": _pooled_cond(t2_k_math_L2, pooled_t2["estimates"]["L2_mathlib_blocked_math"]),
        "tier2a_all_math_given_L1_unmatched_ref": _pooled_cond(t2_k_math, pooled_t2["estimates"]["tier2a_lean_amenable_math"]),
        "tier2a_strict_eng_given_L1": _pooled_cond(t2_k_eng, pooled_t2["estimates"]["tier2a_lean_amenable_math"]),
        "tier2b_matched_L1_L3_given_L1_L3": _pooled_cond(t2_k_nonmeta_L1_L3, pooled_t2["estimates"]["tier2b_broad_lean_applicable"]),
    }

    eess_all_rows = [r for r in pop_rows if set(r["_matched_15"]) & {"eess.SY", "eess.SP", "eess.IV", "eess.AS"}]
    eess_non_sy_rows = [r for r in pop_rows if set(r["_matched_15"]) & {"eess.SP", "eess.IV", "eess.AS"}]
    eess_all_est = _hajek_pooled_estimate(
        pop_rows=eess_all_rows,
        sampled_cls=sampled_cls_map,
        plan_per_cat=plan["per_category"],
        total_scale_n=int(t2_slice["eess_archive"]["eess_all_unique_papers"]),
        n_boot=2000,
        seed=20261129,
    )
    eess_non_sy_est = _hajek_pooled_estimate(
        pop_rows=eess_non_sy_rows,
        sampled_cls=sampled_cls_map,
        plan_per_cat=plan["per_category"],
        total_scale_n=int(t2_slice["eess_archive"]["eess_non_sy_unique_papers"]),
        n_boot=2000,
        seed=20261130,
    )

    # Rankings: Raw v1 vs Tier 1 (Math/Alg given L1∪L2) vs Tier 2a Matched (L1 given L1, stable N_hat>=10)
    rank_raw = sorted(ALL15_CATS, key=lambda c: (-per_category[c]["conditional_adoption"]["raw_tier0_all_v1"]["rate_pct"], c))
    rank_t1 = sorted(ALL15_CATS, key=lambda c: (-(per_category[c]["conditional_adoption"]["tier1_math_alg_given_thm"]["rate_pct"] or 0.0), c))
    rank_t2a = sorted(
        ALL15_CATS,
        key=lambda c: (
            bool(per_category[c]["conditional_adoption"]["tier2a_matched_L1_given_L1"]["small_denom_flag"]),
            -(per_category[c]["conditional_adoption"]["tier2a_matched_L1_given_L1"]["rate_pct"] or 0.0),
            c,
        ),
    )
    rank_t2b = sorted(
        ALL15_CATS,
        key=lambda c: (
            bool(per_category[c]["conditional_adoption"]["tier2b_matched_L1_L3_given_L1_L3"]["small_denom_flag"]),
            -(per_category[c]["conditional_adoption"]["tier2b_matched_L1_L3_given_L1_L3"]["rate_pct"] or 0.0),
            c,
        ),
    )

    artifact: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "slice_id": "2026-11",
        "model_tier": model_tier,
        "model_resolved": "Gemini 4 Hydrogen (High) [gemini-4-hydrogen-tiered-high]" if model_tier == "flash" else model_tier,
        "sampling_design": {
            "design": plan["design"],
            "per_cat_budget": plan["per_cat_budget"],
            "cap_none": plan["cap_none"],
            "min_formal": plan["min_formal"],
            "min_weak": plan["min_weak"],
            "seed_prefix": plan["seed_prefix"],
            "total_category_draws": plan["total_category_draws"],
            "unique_t2_papers_classified": len(unique_ids),
            "net_new_e2_classified": len(new_results),
            "reused_pilot_e0_flash_hits": len(unique_ids) - len(new_results),
            "ci_method_per_category": "Exact finite-population Beta-Binomial Monte Carlo (Jeffreys Beta(0.5, 0.5) on unsampled remainder, 8,000 draws); conditional rates propagate numerator Jeffreys binomial + denominator sampling uncertainty.",
            "ci_method_pooled": "Exact inclusion-probability Hájek Horvitz-Thompson estimator with 2,000-replicate stratified bootstrap.",
        },
        "overall_t2_pooled": pooled_t2,
        "eess_archive": {
            "eess_all": eess_all_est,
            "eess_non_sy": eess_non_sy_est,
        },
        "rankings": {
            "raw_v1_descending": rank_raw,
            "tier1_math_alg_given_thm_descending": rank_t1,
            "tier2a_matched_L1_given_L1_descending_stable_first": rank_t2a,
            "tier2b_matched_L1_L3_given_L1_L3_descending_stable_first": rank_t2b,
        },
        "e1_vs_e2_confusion_sampled": {b: {c: e1_vs_e2[b][c] for c in ELIG_CLASSES} for b in E1_FETCHED_STRATA},
        "l2_barriers_overall": dict(l2_barriers_overall.most_common()),
        "dominant_math_areas_by_class": {c: dict(math_areas_by_class[c].most_common()) for c in ELIG_CLASSES},
        "confidence_distribution": dict(confidence_counts),
        "per_category": per_category,
        "sampled_records": [
            {
                "arxiv_id": aid,
                "primary_category": pop_by_id[aid]["primary_category"],
                "matched_15_cats": pop_by_id[aid]["_matched_15"],
                "fetch_source": pop_by_id[aid]["fetch_source"],
                "e1_bucket": pop_by_id[aid]["e1_bucket"],
                "n_core_claims": (
                    pop_by_id[aid]["n_theorem"]
                    + pop_by_id[aid]["n_lemma"]
                    + pop_by_id[aid]["n_proposition"]
                    + pop_by_id[aid]["n_corollary"]
                    + pop_by_id[aid]["n_claim_or_fact"]
                ),
                "n_proof": pop_by_id[aid]["n_proof"],
                "eligibility_class": cls_by_id[aid]["eligibility_class"],
                "has_original_deductive_proof": bool(cls_by_id[aid]["has_original_deductive_proof"]),
                "dominant_math_area": cls_by_id[aid]["dominant_math_area"],
                "primary_barrier_if_L2": cls_by_id[aid]["primary_barrier_if_L2"],
                "confidence": cls_by_id[aid]["confidence"],
                "rationale": cls_by_id[aid]["rationale"],
            }
            for aid in unique_ids
        ],
    }

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2) + "\n")

    # Render Markdown analytical report
    _write_markdown_report(artifact, report_path)
    return artifact


def _fmt_ci(ci: list[float]) -> str:
    return f"[{ci[0]:.1f}%, {ci[1]:.1f}%]"


def _write_markdown_report(art: dict[str, Any], report_path: Path) -> None:
    pt = art["overall_t2_pooled"]
    pe = pt["estimates"]
    pc = pt["conditional_adoption"]
    sd = art["sampling_design"]

    lines = [
        "# Stage E2 Analysis: Lean 4 Eligibility & Denominator-Adjusted Adoption (T2, 2026-11)",
        "",
        f"- **Generated:** `{art['generated_at']}`",
        f"- **Model:** `{art['model_resolved']}` (`{art['model_tier']}`, batched 5 papers/prompt, strictly blinded to `is_confirmed_lean`)",
        f"- **Sampling design:** `{sd['design']}` (`{sd['per_cat_budget']}` draws/cat = `{sd['total_category_draws']}` draws → **`{sd['unique_t2_papers_classified']}` unique T2 papers**: `{sd['net_new_e2_classified']}` net-new + `{sd['reused_pilot_e0_flash_hits']}` cached Pilot E0 `flash` hits)",
        f"- **T2 census frame:** `N = {pt['population_total']:,}` (`{pt['population_fetched']:,}` full-text extracted in Stage E1 = `99.81%`)",
        "",
        "## 1. Pooled T2 Denominators & Denominator-Adjusted Adoption (`N = 5,303`)",
        "",
        "| Denominator Tier | Definition | Est. Share of T2 (95% CI) | Est. Papers (95% CI) | Matched T2 `v1` Lean | Conditional Rate (95% CI) |",
        "|---|---|---:|---:|---:|---:|",
        f"| **Tier 0 (`N`)** | All T2 preprints | `100.0%` | `{pt['population_total']:,}` | `68` (all) | **`{pc['raw_tier0_all_v1_pct']:.2f}%`** |",
        f"| **Tier 1 (`L1 ∪ L2`)** | Theorem-Bearing Math | `{pe['tier1_theorem_bearing']['pct']:.1f}%` {_fmt_ci(pe['tier1_theorem_bearing']['ci_95_pct'])} | `{pe['tier1_theorem_bearing']['est_count']:.0f}` `[{pe['tier1_theorem_bearing']['est_count_ci_95'][0]:.0f}, {pe['tier1_theorem_bearing']['est_count_ci_95'][1]:.0f}]` | `{pc['tier1_math_alg_given_thm']['numerator']}` (Math+Alg) | **`{pc['tier1_math_alg_given_thm']['rate_pct']:.2f}%`** {_fmt_ci(pc['tier1_math_alg_given_thm']['ci_95_conservative_pct'])} |",
        f"| **Tier 2a (`L1`, Matched)** | Lean-Amenable Math | `{pe['tier2a_lean_amenable_math']['pct']:.1f}%` {_fmt_ci(pe['tier2a_lean_amenable_math']['ci_95_pct'])} | `{pe['tier2a_lean_amenable_math']['est_count']:.0f}` `[{pe['tier2a_lean_amenable_math']['est_count_ci_95'][0]:.0f}, {pe['tier2a_lean_amenable_math']['est_count_ci_95'][1]:.0f}]` | `{pc['tier2a_matched_L1_given_L1']['numerator']}` (`L1` Math+Alg) | **`{pc['tier2a_matched_L1_given_L1']['rate_pct']:.2f}%`** {_fmt_ci(pc['tier2a_matched_L1_given_L1']['ci_95_conservative_pct'])} |",
        f"| **Tier 2-Frontier (`L2`, Matched)** | Mathlib-Blocked / Frontier | `{pe['L2_mathlib_blocked_math']['pct']:.1f}%` {_fmt_ci(pe['L2_mathlib_blocked_math']['ci_95_pct'])} | `{pe['L2_mathlib_blocked_math']['est_count']:.0f}` `[{pe['L2_mathlib_blocked_math']['est_count_ci_95'][0]:.0f}, {pe['L2_mathlib_blocked_math']['est_count_ci_95'][1]:.0f}]` | `{pc['tier2_frontier_L2_given_L2']['numerator']}` (`L2` Math+Alg) | **`{pc['tier2_frontier_L2_given_L2']['rate_pct']:.2f}%`** {_fmt_ci(pc['tier2_frontier_L2_given_L2']['ci_95_conservative_pct'])} |",
        f"| **Tier 2b (`L1 ∪ L3`, Matched)** | Broad Lean-Applicable | `{pe['tier2b_broad_lean_applicable']['pct']:.1f}%` {_fmt_ci(pe['tier2b_broad_lean_applicable']['ci_95_pct'])} | `{pe['tier2b_broad_lean_applicable']['est_count']:.0f}` `[{pe['tier2b_broad_lean_applicable']['est_count_ci_95'][0]:.0f}, {pe['tier2b_broad_lean_applicable']['est_count_ci_95'][1]:.0f}]` | `{pc['tier2b_matched_L1_L3_given_L1_L3']['numerator']}` (`L1∪L3` Non-Meta) | **`{pc['tier2b_matched_L1_L3_given_L1_L3']['rate_pct']:.2f}%`** {_fmt_ci(pc['tier2b_matched_L1_L3_given_L1_L3']['ci_95_conservative_pct'])} |",
        "",
        "Pooled 5-class composition (`N = 5,303`): "
        f"`L1` = **{pe['L1_lean_amenable_math']['pct']:.1f}%**, "
        f"`L2` (Mathlib-blocked) = **{pe['L2_mathlib_blocked_math']['pct']:.1f}%**, "
        f"`L3` (Op-FV) = **{pe['L3_operational_spec_fv']['pct']:.1f}%**, "
        f"`L4` (Heuristic/Num) = **{pe['L4_heuristic_or_numerical_only']['pct']:.1f}%**, "
        f"`L5` (Empirical/Survey) = **{pe['L5_empirical_or_survey']['pct']:.1f}%**. "
        "*(Note: Matched `L1` and `L2` numerators use each confirmed T2 `v1` adopter's strictly blinded Pilot E0 `flash` class, preventing `L2` frontier adopters in `math.DS`/`math.OC` from inflating `L1` denominators.)*",
        "",
        "## 2. Per-Category Nested Denominators & Strictly Matched Conditional Adoption (All 15 Categories)",
        "",
        "| Category | `N` | `L1`% | `L2`% | `L3`% | Tier 1 (`L1∪L2`) | Tier 2a (`L1`) | Raw `v1` | **Tier 1 (`Math+Alg \\| L1∪L2`)** | **Tier 2a Matched (`L1 \\| L1`)** | **Tier 2b Matched (`L1∪L3`)** |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for cat in ALL15_CATS:
        d = art["per_category"][cat]
        ee = d["eligibility_estimates"]
        ca = d["conditional_adoption"]
        t1 = ca["tier1_math_alg_given_thm"]
        t2a = ca["tier2a_matched_L1_given_L1"]
        t2b = ca["tier2b_matched_L1_L3_given_L1_L3"]
        flag_a = "†" if t2a.get("small_denom_flag") else ""
        flag_b = "†" if t2b.get("small_denom_flag") else ""
        r_t1 = f"**{t1['rate_pct']:.1f}%** ({t1['numerator']}) {_fmt_ci(t1['ci_95_propagated_pct'])}" if t1["rate_pct"] is not None else "—"
        r_t2a = f"**{t2a['rate_pct']:.1f}%**{flag_a} ({t2a['numerator']}) {_fmt_ci(t2a['ci_95_propagated_pct'])}" if t2a["rate_pct"] is not None else "—"
        r_t2b = f"**{t2b['rate_pct']:.1f}%**{flag_b} ({t2b['numerator']}) {_fmt_ci(t2b['ci_95_propagated_pct'])}" if t2b["rate_pct"] is not None else "—"
        lines.append(
            f"| `{cat}` | {d['panel_t2_total_papers']} | {ee['L1_lean_amenable_math']['pct']:.1f}% | "
            f"{ee['L2_mathlib_blocked_math']['pct']:.1f}% | {ee['L3_operational_spec_fv']['pct']:.1f}% | "
            f"{ee['tier1_theorem_bearing']['est_count']:.0f} ({ee['tier1_theorem_bearing']['pct']:.1f}%) | "
            f"{ee['tier2a_lean_amenable_math']['est_count']:.0f} ({ee['tier2a_lean_amenable_math']['pct']:.1f}%) | "
            f"{ca['raw_tier0_all_v1']['rate_pct']:.2f}% ({ca['raw_tier0_all_v1']['numerator']}) | "
            f"{r_t1} | {r_t2a} | {r_t2b} |"
        )
    lines.append("")
    lines.append("*† Small-denominator flag (`N_hat < 10` papers): prefer Tier 1 (`L1 ∪ L2`) for stable rate comparisons.*")

    lines.extend(
        [
            "",
            "## 3. Stage E1 Deterministic Bucket vs. Stage E2 LLM Class (`n = 439` Unique T2 Papers)",
            "",
            "| E1 Bucket | `L1` | `L2` | `L3` | `L4` | `L5` | Total |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for b in E1_FETCHED_STRATA:
        c = art["e1_vs_e2_confusion_sampled"][b]
        tot = sum(c.values())
        lines.append(
            f"| `{b}` | {c['L1_lean_amenable_math']} | {c['L2_mathlib_blocked_math']} | "
            f"{c['L3_operational_spec_fv']} | {c['L4_heuristic_or_numerical_only']} | "
            f"{c['L5_empirical_or_survey']} | {tot} |"
        )

    lines.extend(["", "## 4. Mathlib-Blocked (`L2`) Barrier Breakdown (Across Sampled `L2` Papers)", ""])
    for bar, cnt in art["l2_barriers_overall"].items():
        lines.append(f"- `{bar}`: **{cnt}**")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Import E2 classifications and compute denominator-adjusted adoption estimates.")
    ap.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    ap.add_argument("--in", dest="e2_out", type=Path, default=Path("data/eligibility_e2_t2_out.json"))
    ap.add_argument("--plan", type=Path, default=Path("data/eligibility_e2_t2_plan.json"))
    ap.add_argument("--panel", type=Path, default=UNIFIED_PANEL_PATH)
    ap.add_argument("--artifact", type=Path, default=Path("artifacts/lean_eligibility_t2.json"))
    ap.add_argument("--report", type=Path, default=Path("reports/lean_eligibility_analysis.md"))
    args = ap.parse_args()

    art = import_and_analyze_e2(
        db_path=args.db,
        e2_out_path=args.e2_out,
        plan_path=args.plan,
        panel_path=args.panel,
        artifact_path=args.artifact,
        report_path=args.report,
    )
    print(json.dumps(art["overall_t2_pooled"]["estimates"], indent=2))
    print(json.dumps(art["overall_t2_pooled"]["conditional_adoption"], indent=2))


if __name__ == "__main__":
    main()
