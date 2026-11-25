"""Unit tests for the off-arXiv bibliometric probe (scripts/probe_off_arxiv.py & artifacts/off_arxiv_probe.json)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.probe_off_arxiv import classify_preprint_hit, clopper_pearson_upper_pct

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBE_JSON = REPO_ROOT / "artifacts" / "off_arxiv_probe.json"


def test_classify_preprint_hit_filters_manufacturing_and_combustion_fps() -> None:
    fp1 = classify_preprint_hit("Optimizing Lean Six Sigma Methodologies for Electrical Equipment Manufacturing")
    assert fp1["is_lean_theorem_prover"] is False
    assert fp1["false_positive_cues"]

    fp2 = classify_preprint_hit("Multi-Physics Modeling of Lean Hydrogen Combustion and NOx Formation")
    assert fp2["is_lean_theorem_prover"] is False

    tp = classify_preprint_hit("Formalizing Control Stability Bounds in Lean 4 with Mathlib")
    assert tp["is_lean_theorem_prover"] is True
    assert "mathlib" in tp["tp_matches"]


def test_off_arxiv_probe_artifact_schema_and_consistency() -> None:
    assert PROBE_JSON.is_file(), "Missing artifacts/off_arxiv_probe.json"
    data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))

    ps = data["preprint_servers"]
    tr = ps["techrxiv"]
    ex = ps["engrxiv"]
    comb = ps["combined"]
    assert comb["total_records_2025_2026"] == tr["total_records_2025_2026"] + ex["total_records_2025_2026"]
    assert comb["confirmed_lean_tp_unique"] == tr["confirmed_lean_tp_unique"] + ex["confirmed_lean_tp_unique"]
    assert comb["confirmed_lean_tp_unique"] == 0
    assert abs(comb["confirmed_95pct_ub_pct"] - clopper_pearson_upper_pct(comb["total_records_2025_2026"])) < 0.001

    oa_all = data["openalex"]["mathlib_all_fields"]
    oa_eng = data["openalex"]["engineering_field_22"]
    assert oa_all["count_2026"] > oa_all["count_2025"]
    assert oa_eng["mathlib_count_2025_2026"] == oa_eng["mathlib_with_arxiv_version"] + oa_eng["mathlib_off_arxiv_only"]
    assert len(oa_eng["off_arxiv_works"]) == oa_eng["mathlib_off_arxiv_only"]
