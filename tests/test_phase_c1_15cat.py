"""Unit tests verifying Phase C1 15-category longitudinal panel artifacts and invariants."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
C1_SUMMARY = REPO_ROOT / "artifacts" / "phase_c1_15cat_longitudinal.json"
SLICE_CLS_PATHS = [
    REPO_ROOT / "artifacts" / "slices" / "2025-11" / "plus7_classifications.json",
    REPO_ROOT / "artifacts" / "slices" / "2026-05" / "plus7_classifications.json",
    REPO_ROOT / "artifacts" / "slices" / "2026-11" / "plus7_classifications.json",
]


def test_phase_c1_artifacts_exist_and_schema() -> None:
    assert C1_SUMMARY.exists(), "Missing artifacts/phase_c1_15cat_longitudinal.json"
    data = json.loads(C1_SUMMARY.read_text(encoding="utf-8"))
    assert len(data["categories"]["orig8"]) == 8
    assert len(data["categories"]["plus7"]) == 7
    assert len(data["categories"]["all15"]) == 15
    assert set(data["categories"]["eess_all"]) == {"eess.SY", "eess.SP", "eess.IV", "eess.AS"}
    assert len(data["slices"]) == 3


def test_phase_c1_deduplication_and_role_sums() -> None:
    data = json.loads(C1_SUMMARY.read_text(encoding="utf-8"))
    for sl in data["slices"]:
        o8_n = sl["orig8"]["total_papers"]
        p7_n = sl["plus7"]["total_papers"]
        ov = sl["overlap_orig8_plus7"]
        net_new = sl["net_new_plus7_papers"]
        u15 = sl["panel_15cat"]["total_papers"]
        assert net_new == p7_n - ov
        assert u15 == o8_n + net_new

        # 4-way role counts must partition confirmed Lean papers exactly
        for key, role_key in [("confirmed_v1", "roles_v1"), ("confirmed_v_latest", "roles_v_latest")]:
            for panel in ("orig8", "plus7", "panel_15cat"):
                total_confirmed = sl[panel][key]["count"]
                role_sum = sum(v["count"] for v in sl[panel][role_key].values())
                assert role_sum == total_confirmed, f"{sl['short_id']} {panel} {key}: {role_sum} != {total_confirmed}"


def test_phase_c1_eess_and_zero_baseline_invariants() -> None:
    data = json.loads(C1_SUMMARY.read_text(encoding="utf-8"))
    t0, t1, t2 = data["slices"]
    # Zero contemporaneous v1 baseline across all 15 categories in T0
    assert t0["panel_15cat"]["confirmed_v1"]["count"] == 0
    # Strict monotonic growth T0 < T1 < T2
    assert t0["panel_15cat"]["confirmed_v1"]["count"] < t1["panel_15cat"]["confirmed_v1"]["count"] < t2["panel_15cat"]["confirmed_v1"]["count"]
    assert t0["panel_15cat"]["roles_v1"]["eng_algorithmic_proof"]["count"] == 0
    assert t1["panel_15cat"]["roles_v1"]["eng_algorithmic_proof"]["count"] < t2["panel_15cat"]["roles_v1"]["eng_algorithmic_proof"]["count"]
    # 100% eess.* non-control union (SP U IV U AS) is 0 in T0 and T2, and 1 in T1 (2605.14610 in eess.SP);
    # eess.IV, eess.AS, cs.NI, cs.RO, cs.CE are strictly 0 across all 3 slices
    gt = data["grand_totals"]
    assert t0["complete_eess_archive"]["eess_non_sy_confirmed_v_latest"]["count"] == 0
    assert t1["complete_eess_archive"]["eess_non_sy_confirmed_v_latest"]["count"] == 1
    assert t2["complete_eess_archive"]["eess_non_sy_confirmed_v_latest"]["count"] == 0
    assert gt["eess_non_sy_3slice_confirmed_v1"]["count"] == 1
    assert gt["eess_non_sy_3slice_confirmed_v_latest"]["count"] == 1
    assert set(gt["persistent_zero_categories_v_latest_3slice"]) == {
        "cs.NI",
        "cs.RO",
        "eess.IV",
        "eess.AS",
        "cs.CE",
    }
    assert set(gt["persistent_zero_categories_v1_3slice"]) == {
        "cs.NI",
        "cs.RO",
        "cs.PF",
        "eess.IV",
        "eess.AS",
        "cs.CE",
    }


def test_plus7_slice_classifications_license_safe_and_consistent() -> None:
    for p in SLICE_CLS_PATHS:
        assert p.exists(), f"Missing {p}"
        doc = json.loads(p.read_text(encoding="utf-8"))
        assert doc["lean_candidate_count"] == len(doc["lean_results"])
        assert doc["lean_contributed_count"] == sum(
            1 for r in doc["lean_results"] if r["lean_usage_status"] == "lean_contributed"
        )
        for r in doc["lean_results"]:
            # Ensure no copyrighted full-text or abstract leaked into artifacts
            assert "abstract" not in r
            assert "full_text" not in r
            if r["lean_usage_status"] == "lean_contributed":
                assert r["role_4way"] in {
                    "eng_algorithmic_proof",
                    "operational_system_fv",
                    "pure_math_or_tcs",
                    "meta_formalization_system",
                }
