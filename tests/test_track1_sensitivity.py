"""Unit and consistency tests for Track 1 (Phase A1) 4-way sensitivity analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.analyze_track1_sensitivity import (
    DEFAULT_ADJUDICATION,
    DEFAULT_BLANK_CSV_OUT,
    DEFAULT_JSON_OUT,
    DEFAULT_LONGITUDINAL,
    DEFAULT_MD_OUT,
    ROLES_4WAY,
    compute_sensitivity,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_GATES = {"G1_meta", "G2_operational_fv", "G3_eng_algorithmic", "G4_pure_math_tcs"}
ALLOWED_VER_OBJS = {
    "algorithm_convergence_or_bound",
    "physical_or_control_model",
    "numerical_or_stat_method",
    "operational_sw_hw_db_protocol",
    "abstract_math_or_tcs_theorem",
    "meta_proving_pipeline",
}


def test_adjudication_covers_all_47_confirmed_papers_exactly() -> None:
    long_data = json.loads(DEFAULT_LONGITUDINAL.read_text(encoding="utf-8"))
    adj_data = json.loads(DEFAULT_ADJUDICATION.read_text(encoding="utf-8"))

    expected_ids = {
        p["arxiv_id"]
        for sl in long_data["slices"]
        for p in sl["confirmed_papers"]
    }
    records = adj_data["records"]
    actual_ids = {r["arxiv_id"] for r in records}

    assert len(records) == 47
    assert actual_ids == expected_ids

    for r in records:
        assert r["role_4way"] in ROLES_4WAY
        assert r["verification_object"] in ALLOWED_VER_OBJS
        assert r["decision_gate"] in ALLOWED_GATES
        assert isinstance(r["is_borderline"], bool)
        if r["is_borderline"]:
            assert r["borderline_alt_role"] in ROLES_4WAY
            assert r["borderline_alt_role"] != r["role_4way"]
        else:
            assert r["borderline_alt_role"] is None
        assert len(r["rationale"].strip()) >= 20


def test_sensitivity_partition_invariants_hold() -> None:
    summary = compute_sensitivity()
    assert summary["total_confirmed_papers_v_latest"] == 47

    for sl in summary["slices"]:
        for mode in ("v1", "v_latest"):
            m = sl["modes"][mode]
            pooled = m["pooled"]
            by_role = m["by_role"]

            assert sum(by_role[r]["count"] for r in ROLES_4WAY) == pooled["count"]
            assert sum(by_role[r]["scanned_owned_repos"] for r in ROLES_4WAY) == pooled["scanned_owned_repos"]
            assert sum(by_role[r]["total_owned_loc"] for r in ROLES_4WAY) == pooled["total_owned_loc"]
            assert sum(by_role[r]["tier3_gold_count"] for r in ROLES_4WAY) == pooled["tier3_gold_count"]
            assert sum(by_role[r]["p4_count"] for r in ROLES_4WAY) == pooled["p4_count"]
            assert sum(by_role[r]["ai_explicit_yes_count"] for r in ROLES_4WAY) == pooled["ai_explicit_yes_count"]

            sc = m["eng_strict_core_non_borderline"]
            eng = by_role["eng_algorithmic_proof"]
            assert sc["count"] <= eng["count"]
            assert sc["total_owned_loc"] <= eng["total_owned_loc"]

    # Phase 2 Layer-A audits (n = 23 total: 20 T2 + 3 T1)
    p2 = summary["phase2_audits_by_role"]
    assert sum(p2[r]["count"] for r in ROLES_4WAY) == 23
    assert p2["eng_algorithmic_proof"]["material_undisclosed_count"] == 0
    assert p2["meta_formalization_system"]["material_undisclosed_count"] == 1

    # Sandboxed Docker builds (n = 14 total)
    sb = summary["sandbox_builds_by_role"]
    assert sum(sb[r]["attempted"] for r in ROLES_4WAY) == 14
    assert sum(sb[r]["pass_ootb"] for r in ROLES_4WAY) == 11
    assert sum(sb[r]["theorems_ootb"] for r in ROLES_4WAY) == 3190
    assert sum(sb[r]["theorems_incl_synthetic"] for r in ROLES_4WAY) == 3254

    # All 9 v0.6 Stage-4 IRR paper_domain_role disagreements accounted for
    assert len(summary["v06_irr_disagreements_reconciled"]) == 9


def test_generated_artifacts_match_recomputation() -> None:
    assert DEFAULT_JSON_OUT.is_file()
    if DEFAULT_MD_OUT.parent.is_dir():
        assert DEFAULT_MD_OUT.is_file()
    assert DEFAULT_BLANK_CSV_OUT.is_file()

    disk_summary = json.loads(DEFAULT_JSON_OUT.read_text(encoding="utf-8"))
    fresh_summary = compute_sensitivity()
    assert disk_summary == fresh_summary

    with DEFAULT_BLANK_CSV_OUT.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 47
    for row in rows:
        # Blinded template must not pre-fill answers
        assert row["annotator_id"] == ""
        assert row["role_4way"] == ""
        assert row["verification_object"] == ""
        assert row["borderline_flag"] == ""
