"""Unit tests for Stage E2 post-stratified estimator & Neyman 3-stratum sampler."""

from __future__ import annotations

import json

from src.analyze_lean_eligibility import (
    conditional_adoption_rate,
    post_stratified_estimate,
)
from src.screen_math_structure import ALL15_CATS, compute_neyman_3stratum_plan


def test_post_stratified_exhaustive_strata_has_zero_variance() -> None:
    # Exhaustive sample (n_h == N_h in every stratum) => exact proportion and zero variance
    est = post_stratified_estimate(
        {
            "E1_formal_thm_proof": (10, 10, 8),
            "E1_weak_or_unnumbered_math": (20, 20, 2),
            "E1_no_formal_claims": (10, 10, 0),
        },
        total_scale_n=40,
        n_mc=1000,
        seed=42,
    )
    assert est["pct"] == 25.0
    assert est["se_pct"] == 0.0
    assert est["ci_95_pct"] == [25.0, 25.0]
    assert est["est_count"] == 10.0
    assert est["est_count_ci_95"] == [10.0, 10.0]


def test_post_stratified_zero_positive_stratum_produces_nonzero_upper_bound() -> None:
    # Unsampled remainder with 0/4 positives must still yield a strictly positive CI upper bound
    est = post_stratified_estimate(
        {
            "E1_formal_thm_proof": (10, 10, 0),
            "E1_weak_or_unnumbered_math": (10, 10, 0),
            "E1_no_formal_claims": (100, 4, 0),
        },
        total_scale_n=120,
        n_mc=2000,
        seed=42,
    )
    assert est["pct"] == 0.0
    assert est["ci_95_pct"][0] == 0.0
    assert est["ci_95_pct"][1] > 10.0


def test_conditional_adoption_rate_positive_and_zero_numerator() -> None:
    denom = post_stratified_estimate(
        {
            "E1_formal_thm_proof": (100, 20, 16),
            "E1_weak_or_unnumbered_math": (100, 10, 2),
            "E1_no_formal_claims": (100, 4, 0),
        },
        total_scale_n=300,
        n_mc=2000,
        seed=99,
    )
    # est_count = 300 * (100*0.8 + 100*0.2 + 0)/300 = 100.0
    assert abs(denom["est_count"] - 100.0) < 0.2

    r_pos = conditional_adoption_rate(10, denom, seed=101)
    assert r_pos["rate_pct"] == 10.0
    assert r_pos["ci_95_propagated_pct"][0] < 10.0 < r_pos["ci_95_propagated_pct"][1]

    r_zero = conditional_adoption_rate(0, denom, seed=102)
    assert r_zero["rate_pct"] == 0.0
    assert r_zero["ci_95_propagated_pct"][0] == 0.0
    assert 2.0 < r_zero["ci_95_propagated_pct"][1] < 10.0


def test_compute_neyman_3stratum_plan_respects_floors_and_independence() -> None:
    rows = []
    idx = 0
    for cat in ALL15_CATS:
        for b, cnt in [
            ("E1_formal_thm_proof", 40),
            ("E1_weak_or_unnumbered_math", 40),
            ("E1_no_formal_claims", 20),
        ]:
            for _ in range(cnt):
                idx += 1
                rows.append(
                    {
                        "arxiv_id": f"2611.{idx:05d}",
                        "matched_15_cats_json": json.dumps([cat]),
                        "e1_bucket": b,
                    }
                )
    plan = compute_neyman_3stratum_plan(rows, per_cat_budget=30, cap_none=4, min_formal=10, min_weak=6)
    assert plan["total_category_draws"] == 15 * 30
    assert len(plan["unique_sampled_ids"]) == 15 * 30
    for cat in ALL15_CATS:
        st = plan["per_category"][cat]["strata"]
        assert st["E1_no_formal_claims"]["n_h"] == 4
        assert st["E1_formal_thm_proof"]["n_h"] >= 10
        assert st["E1_weak_or_unnumbered_math"]["n_h"] >= 6
        assert plan["per_category"][cat]["n_total"] == 30
