"""Unit tests for canonical `artifacts/unified_15cat_panel.json` integrity and schema."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIFIED_PATH = REPO_ROOT / "artifacts" / "unified_15cat_panel.json"


def _load() -> dict:
    assert UNIFIED_PATH.is_file(), f"Missing {UNIFIED_PATH}"
    return json.loads(UNIFIED_PATH.read_text(encoding="utf-8"))


def test_unified_panel_size_and_grand_totals() -> None:
    size_kb = UNIFIED_PATH.stat().st_size / 1024.0
    assert size_kb < 350.0, f"unified_15cat_panel.json too large: {size_kb:.1f} KB"

    d = _load()
    gt = d["grand_totals"]
    assert gt["total_papers"] == 12613
    assert gt["fulltext_screened"] == 12564
    assert gt["confirmed_v1_total"] == 75
    assert gt["confirmed_v_latest_total"] == 82
    assert gt["retroactive_v2_total"] == 7
    assert gt["complete_eess_3slice_unique_papers"] == 3558
    assert gt["eess_non_sy_3slice_unique_papers"] == 1958
    assert gt["eess_non_sy_3slice_confirmed_v1"]["count"] == 1


def test_unified_panel_slices_and_4way_partition() -> None:
    d = _load()
    slices = {s["short_id"]: s for s in d["slices"]}
    assert set(slices.keys()) == {"T0", "T1", "T2"}
    assert [slices[k]["total_papers"] for k in ("T0", "T1", "T2")] == [3164, 4146, 5303]
    assert [slices[k]["confirmed_v1"]["count"] for k in ("T0", "T1", "T2")] == [0, 7, 68]
    assert [slices[k]["confirmed_v_latest"]["count"] for k in ("T0", "T1", "T2")] == [2, 11, 69]

    for sl in slices.values():
        role_v1_sum = sum(v["count"] for v in sl["roles_v1"].values())
        role_lat_sum = sum(v["count"] for v in sl["roles_v_latest"].values())
        assert role_v1_sum == sl["confirmed_v1"]["count"]
        assert role_lat_sum == sl["confirmed_v_latest"]["count"]


def test_unified_panel_harmonized_flags_and_82_ledger() -> None:
    d = _load()
    papers = d["confirmed_papers"]
    assert len(papers) == 82
    ids = {p["arxiv_id"] for p in papers}
    assert len(ids) == 82

    by_id = {p["arxiv_id"]: p for p in papers}
    # Zero-dep operational_system_fv repos must NOT retain legacy Mode3_CustomDefs
    for aid in ("2611.10810", "2605.19531"):
        assert by_id[aid]["role_4way"] == "operational_system_fv"
        assert "Mode3_CustomDefs" not in by_id[aid]["static_risk_flags"]

    # Every confirmed paper must have a valid 4-way role and non-negative owned LoC
    allowed = {"eng_algorithmic_proof", "operational_system_fv", "pure_math_or_tcs", "meta_formalization_system"}
    for p in papers:
        assert p["role_4way"] in allowed
        assert p["primary_owned_loc"] >= 0
        assert p["primary_raw_loc"] >= p["primary_owned_loc"]


def test_unified_panel_layer_a_opfv_and_recall() -> None:
    d = _load()
    la = d["layer_a_audits"]
    assert la["total_audited"] == 27
    assert la["total_file_line_refs"] == 274
    assert la["resolved_file_line_refs"] == 274
    assert la["summary"]["eng_algorithmic_proof_all"]["count"] == 22
    assert la["summary"]["eng_algorithmic_proof_all"]["material_undisclosed_count"] == 0
    assert la["summary"]["meta_formalization_system_all"]["count"] == 2
    assert la["summary"]["pure_math_or_tcs_contrast"]["count"] == 3

    opfv = d["operational_fv_audit"]["summary_counts"]
    assert opfv["total_operational_fv_papers"] == 8
    assert opfv["opfv1_refinement_gap_present"] == 8
    assert opfv["opfv2_unproved_env_or_oracle_assumptions_present"] == 8

    rc = d["recall_calibration"]
    assert rc["gh_sample_size"] == 250
    assert rc["confirmed_missed_lean_contributions"] == 0
    assert rc["non_gh_sample_size"] == 125

    sb = d["sandbox_builds"]["overall"]
    assert sb["total_attempted"] == 23
    assert sb["pass_out_of_box"] == 18
    assert sb["pass_and_standard_axioms_only"] == 14
    assert sb["tier3_gold_attempted"] == 12
    assert sb["tier3_gold_pass_out_of_box"] == 11
    assert sb["tier3_gold_clean_axioms"] == 11
    assert sb["native_decide_repos_ootb"] == ["2611.15711"]
    assert d["sandbox_builds"]["by_role"]["eng_algorithmic_proof"]["total_attempted"] == 11
    assert d["sandbox_builds"]["by_role"]["eng_algorithmic_proof"]["native_decide_repos_ootb"] == []
