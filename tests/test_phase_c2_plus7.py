"""Unit tests validating Phase C2 (+7 eng_algorithmic_proof) Layer-A audits,
compact Docker kernel builds, immutable provenance, and combined 15-category parity.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUS7_AUDITS = REPO_ROOT / "artifacts" / "slices" / "2026-11" / "plus7_layer_a_audits.json"
PLUS7_SANDBOX = REPO_ROOT / "artifacts" / "sandbox_builds" / "results_plus7_2026-11.json"
PHASE_C2_SUMMARY = REPO_ROOT / "artifacts" / "phase_c2_plus7_audits.json"
ORIG8_SANDBOX_SUMMARY = REPO_ROOT / "artifacts" / "sandbox_builds" / "summary.json"
ORIG8_PROV = REPO_ROOT / "artifacts" / "phase2_provenance.json"

EXPECTED_PLUS7_AUDIT_IDS = {"2611.14586", "2611.11805", "2611.09615", "2611.07395"}
EXPECTED_PLUS7_COMPACT_IDS = {"2611.14586", "2611.09615", "2611.07395"}


def test_plus7_layer_a_audits_schema_and_hygiene() -> None:
    assert PLUS7_AUDITS.is_file(), "Missing plus7_layer_a_audits.json"
    raw = PLUS7_AUDITS.read_text(encoding="utf-8")
    assert "/root/" not in raw, "Local absolute path leaked into plus7_layer_a_audits.json"
    doc = json.loads(raw)
    assert doc["slice_id"] == "2026-11"
    assert doc["audit_count"] == len(doc["audits"]) == 4
    assert {a["arxiv_id"] for a in doc["audits"]} == EXPECTED_PLUS7_AUDIT_IDS
    for a in doc["audits"]:
        assert a["role_4way"] == "eng_algorithmic_proof"
        assert "abstract" not in a
        assert "full_text" not in a
        assert a["overall_fidelity"] in {
            "high_faithful",
            "mostly_faithful_with_disclosed_gaps",
            "partial_or_weakened_formalization",
            "material_undisclosed_drift_or_risk",
        }
        assert len(a["theorems_compared"]) >= 2


def test_plus7_sandbox_builds_security_and_axioms() -> None:
    assert PLUS7_SANDBOX.is_file(), "Missing results_plus7_2026-11.json"
    doc = json.loads(PLUS7_SANDBOX.read_text(encoding="utf-8"))
    inv = doc["security_invariants"]
    assert inv["network_mode"] == "none"
    assert inv["user"] == "65534:65534"
    assert inv["cap_drop"] == "ALL"
    assert inv["no_new_privileges"] is True
    assert inv["readonly_source_mount"] is True

    recs = doc["records"]
    assert len(recs) == 3
    assert {r["arxiv_id"] for r in recs} == EXPECTED_PLUS7_COMPACT_IDS

    by_id = {r["arxiv_id"]: r for r in recs}
    for r in recs:
        assert r["network_mode"] == "none"
        assert "--network=none" in r["security_flags"]
        assert "--cap-drop=ALL" in r["security_flags"]
        assert r["build_status"] == "pass"
        assert r["exit_code"] == 0
        assert r["total_theorems_checked"] > 0
        assert r["owned_loc"] is not None and r["owned_loc"] < 15000
        assert "axiom_check_error" not in r
        assert r["sorry_ax_detected"] is False
        assert r["of_reduce_bool_detected"] is False
        assert r["trust_compiler_detected"] is False

    # 2611.14586 & 2611.09615 are axiom-clean; 2611.07395 dynamically corroborates custom Arb axioms
    assert by_id["2611.14586"]["nonstandard_axioms_detected"] == []
    assert by_id["2611.09615"]["nonstandard_axioms_detected"] == []
    assert len(by_id["2611.07395"]["nonstandard_axioms_detected"]) >= 2

    sm = doc["summary"]
    assert sm["total_attempted"] == 3
    assert sm["pass_out_of_box"] == 3
    assert sm["pass_and_standard_axioms_only"] == 2
    assert sm["pass_with_nonstandard_axioms"] == 1
    assert sm["tier3_gold_attempted"] == 1
    assert sm["tier3_gold_pass_out_of_box"] == 1
    assert sm["tier3_gold_clean_axioms"] == 1
    assert sm["of_reduce_bool_repos_ootb"] == []
    assert sm["total_theorems_checked_ootb"] == sum(int(r["total_theorems_checked"]) for r in recs)


def test_phase_c2_combined_summary_and_provenance_parity() -> None:
    assert PHASE_C2_SUMMARY.is_file(), "Missing phase_c2_plus7_audits.json"
    c2 = json.loads(PHASE_C2_SUMMARY.read_text(encoding="utf-8"))
    orig8_prov = json.loads(ORIG8_PROV.read_text(encoding="utf-8"))
    orig8_sb = json.loads(ORIG8_SANDBOX_SUMMARY.read_text(encoding="utf-8"))
    p7_sb = json.loads(PLUS7_SANDBOX.read_text(encoding="utf-8"))

    # Provenance: 100% file:line resolved & in-bounds
    fl_p7 = c2["plus7_provenance"]["theorems_compared_file_line_summary"]
    assert fl_p7["total_refs"] > 0
    assert fl_p7["resolved_in_bounds"] == fl_p7["total_refs"]
    for rec in c2["records"]:
        chk = rec["layer_a"]["theorems_compared_file_line_check"]
        assert chk["unresolved"] == []
        assert chk["out_of_bounds"] == []
        assert rec["commit_sha"] or rec["zenodo_record_id"]

    # Combined 15-cat provenance & Layer-A parity
    assert c2["combined_15cat_provenance"]["total_audited_repos"] == orig8_prov["total_audited_repos"] + 4 == 27
    fl_15 = c2["combined_15cat_provenance"]["theorems_compared_file_line_summary"]
    assert fl_15["resolved_in_bounds"] == fl_15["total_refs"]
    assert c2["layer_a_summary"]["all15_t2_eng_algorithmic_proof"]["count"] == 19
    assert c2["layer_a_summary"]["all15_t1_t2_eng_algorithmic_proof"]["count"] == 22
    assert c2["layer_a_summary"]["all15_t1_t2_eng_algorithmic_proof"]["material_undisclosed_count"] == 0
    assert c2["layer_a_summary"]["all15_t1_t2_all_roles"]["count"] == 27

    # Combined 15-cat compact sandbox parity
    sb15 = c2["sandbox_summary"]["all15_t1_t2_compact_all_roles"]
    assert sb15["total_attempted"] == orig8_sb["overall"]["total_attempted"] + 3 == 17
    assert sb15["pass_out_of_box"] == orig8_sb["overall"]["pass_out_of_box"] + p7_sb["summary"]["pass_out_of_box"]
    assert (
        sb15["total_theorems_checked_ootb"]
        == orig8_sb["overall"]["total_theorems_checked_ootb"] + p7_sb["summary"]["total_theorems_checked_ootb"]
    )
    assert sb15["of_reduce_bool_repos_ootb"] == []
