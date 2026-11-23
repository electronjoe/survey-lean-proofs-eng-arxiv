"""Unit tests for scripts/compute_irr.py and blinding checks in prepare_stage4_irr.py."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pytest

from scripts.compute_irr import (
    build_confusion_matrix,
    cohens_kappa,
    evaluate_multirater_alpha,
    evaluate_pair,
    exact_agreement,
    krippendorff_alpha_nominal,
    load_human_annotations,
    load_llm_classifications,
)
from scripts.prepare_stage4_irr import CSV_COLUMNS, FORBIDDEN_BLIND_TOKENS, verify_blinding


def test_exact_agreement_and_kappa_perfect() -> None:
    a = ["lean_contributed", "lean_contributed", "false_positive", "lean_citation_or_discussion"]
    b = list(a)
    assert exact_agreement(a, b) == pytest.approx(1.0)
    assert cohens_kappa(a, b) == pytest.approx(1.0)
    assert krippendorff_alpha_nominal(list(zip(a, b))) == pytest.approx(1.0)


def test_kappa_zero_chance_agreement_and_alpha_finite_pop() -> None:
    # Balanced 2x2 table: [[1, 1], [1, 1]] -> po=0.5, pe=0.5 -> kappa = 0.0
    # Nominal Krippendorff's alpha with N=8, n_A=4, n_B=4:
    # D_o = 0.5, D_e = 1 - (4*3 + 4*3)/(8*7) = 32/56 = 4/7 => alpha = 1 - 7/8 = 0.125.
    a = ["A", "A", "B", "B"]
    b = ["A", "B", "A", "B"]
    assert exact_agreement(a, b) == pytest.approx(0.5)
    assert cohens_kappa(a, b) == pytest.approx(0.0)
    assert krippendorff_alpha_nominal(list(zip(a, b))) == pytest.approx(0.125)


def test_kappa_known_hand_calculation() -> None:
    # Confusion matrix:
    #       yes  no
    # yes [ 20,  5 ]  (row sum 25)
    # no  [ 10, 15 ]  (row sum 25)
    # col    30  20   (N = 50)
    # po = 35/50 = 0.70
    # pe = (25/50)*(30/50) + (25/50)*(20/50) = 0.30 + 0.20 = 0.50
    # kappa = (0.70 - 0.50) / (1 - 0.50) = 0.40
    a = ["yes"] * 25 + ["no"] * 25
    b = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
    assert exact_agreement(a, b) == pytest.approx(0.70)
    assert cohens_kappa(a, b) == pytest.approx(0.40)

    # Krippendorff's alpha: N=100, n_yes=55, n_no=45, diag_coinc=70
    # D_o = 1 - 70/100 = 0.30
    # D_e = 1 - (55*54 + 45*44)/(100*99) = 1 - 4950/9900 = 0.50
    # alpha = 1 - 0.30 / 0.50 = 0.40? Wait: 55*54=2970, 45*44=1980, sum=4950!
    # 4950/9900 = 0.5 exactly -> alpha = 0.40!
    assert krippendorff_alpha_nominal(list(zip(a, b))) == pytest.approx(0.40)


def test_kappa_negative_below_chance() -> None:
    a = ["A", "A", "B", "B"]
    b = ["B", "B", "A", "A"]
    assert exact_agreement(a, b) == pytest.approx(0.0)
    assert cohens_kappa(a, b) == pytest.approx(-1.0)
    # D_o = 1.0, D_e = 4/7 => alpha = 1 - 7/4 = -0.75
    assert krippendorff_alpha_nominal(list(zip(a, b))) == pytest.approx(-0.75)


def test_zero_variance_returns_none() -> None:
    a = ["A", "A", "A"]
    b = ["A", "A", "A"]
    assert exact_agreement(a, b) == pytest.approx(1.0)
    assert cohens_kappa(a, b) is None
    assert krippendorff_alpha_nominal(list(zip(a, b))) is None


def test_krippendorff_alpha_textbook_three_raters_with_missing() -> None:
    # Krippendorff (2011) canonical nominal reliability matrix (4 observers, 12 units, missing data).
    # Columns are units 1..12; rows are observers 1..4:
    # Obs1: 1, 2, 3, 3, 2, 1, 4, 1, 2, None, None, None
    # Obs2: 1, 2, 3, 3, 2, 2, 4, 1, 2, 5, None, 3
    # Obs3: None, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, None
    # Obs4: 1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, None
    # Known exact nominal alpha from Krippendorff (2011) = 0.74342105... (113/152)
    obs = [
        ["1", "2", "3", "3", "2", "1", "4", "1", "2", None, None, None],
        ["1", "2", "3", "3", "2", "2", "4", "1", "2", "5", None, "3"],
        [None, "3", "3", "3", "2", "3", "4", "2", "2", "5", "1", None],
        ["1", "2", "3", "3", "2", "4", "4", "1", "2", "5", "1", None],
    ]
    units = [[obs[r][u] for r in range(4)] for u in range(12)]
    alpha = krippendorff_alpha_nominal(units)
    assert alpha is not None
    assert math.isclose(alpha, 113 / 152, rel_tol=1e-9)


def test_confusion_matrix_canonical_order() -> None:
    labels, cm = build_confusion_matrix(
        ["Tier1_Bronze", "Tier3_Gold", "Tier3_Gold"],
        ["Tier2_Silver", "Tier3_Gold", "Tier1_Bronze"],
        field="verification_tier",
    )
    assert labels == ["Tier3_Gold", "Tier2_Silver", "Tier1_Bronze"]
    assert cm["Tier3_Gold"]["Tier3_Gold"] == 1
    assert cm["Tier3_Gold"]["Tier1_Bronze"] == 1
    assert cm["Tier1_Bronze"]["Tier2_Silver"] == 1


def test_end_to_end_human_vs_llm_and_human_vs_human(tmp_path: Path) -> None:
    slices_dir = tmp_path / "slices"
    s1 = slices_dir / "2026-11"
    s1.mkdir(parents=True)
    cls_data = {
        "slice_id": "2026-11",
        "lean_results": [
            {
                "arxiv_id": "2611.00001",
                "lean_usage_status": "lean_contributed",
                "paper_domain_role": "engineering_math_proof",
                "authoring_paradigm": "P1_paper_first_posthoc",
                "verification_tier_observed": "Tier3_Gold",
                "ai_agent_assisted": "explicitly_yes",
            },
            {
                "arxiv_id": "2611.00002",
                "lean_usage_status": "lean_contributed",
                "paper_domain_role": "software_or_system_fv",
                "authoring_paradigm": "P4_speclock_solve_distill",
                "verification_tier_observed": "Tier2_Silver",
                "ai_agent_assisted": "unclear",
            },
            {
                "arxiv_id": "2611.00003",
                "lean_usage_status": "lean_citation_or_discussion",
                "paper_domain_role": "N/A",
                "authoring_paradigm": "N/A",
                "verification_tier_observed": "N/A",
                "ai_agent_assisted": "N/A",
            },
            {
                "arxiv_id": "2611.00004",
                "lean_usage_status": "false_positive",
                "paper_domain_role": "N/A",
                "authoring_paradigm": "N/A",
                "verification_tier_observed": "N/A",
                "ai_agent_assisted": "N/A",
            },
        ],
    }
    (s1 / "classifications.json").write_text(json.dumps(cls_data), encoding="utf-8")

    csv_path = tmp_path / "stage4_irr.csv"
    rows = [
        # annotator_1 agrees on 3/4, disagrees on tier for 2611.00002
        ["2026-11", "2611.00001", "annotator_1", "lean_contributed", "engineering_math_proof", "P1_paper_first_posthoc", "Tier3_Gold", "explicitly_yes", "clear"],
        ["2026-11", "2611.00002", "annotator_1", "lean_contributed", "software_or_system_fv", "P4_speclock_solve_distill", "Tier3_Gold", "unclear", "comparator CI present"],
        ["2026-11", "2611.00003", "annotator_1", "lean_citation_or_discussion", "N/A", "N/A", "N/A", "N/A", ""],
        ["2026-11", "2611.00004", "annotator_1", "false_positive", "N/A", "N/A", "N/A", "N/A", ""],
        # annotator_2 agrees with LLM completely
        ["2026-11", "2611.00001", "annotator_2", "lean_contributed", "engineering_math_proof", "P1_paper_first_posthoc", "Tier3_Gold", "explicitly_yes", ""],
        ["2026-11", "2611.00002", "annotator_2", "lean_contributed", "software_or_system_fv", "P4_speclock_solve_distill", "Tier2_Silver", "unclear", ""],
        ["2026-11", "2611.00003", "annotator_2", "lean_citation_or_discussion", "", "", "", "", ""],
        ["2026-11", "2611.00004", "annotator_2", "false_positive", "", "", "", "", ""],
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)
        w.writerows(rows)

    llm = load_llm_classifications(slices_dir)
    humans = load_human_annotations(csv_path)
    assert sorted(humans.keys()) == ["annotator_1", "annotator_2"]

    m1, d1 = evaluate_pair("annotator_1", humans["annotator_1"], "LLM", llm)
    status_m = next(m for m in m1 if m.field == "lean_usage_status" and m.scope == "all")
    assert status_m.exact_agreement == pytest.approx(1.0)
    assert status_m.cohens_kappa == pytest.approx(1.0)
    assert len(d1) == 1
    assert d1[0].arxiv_id == "2611.00002"
    assert d1[0].field == "verification_tier"

    tier_cond = next(m for m in m1 if m.field == "verification_tier" and m.scope == "agreed_contributed")
    assert tier_cond.n == 2
    assert tier_cond.exact_agreement == pytest.approx(0.5)

    mh, dh = evaluate_pair("annotator_1", humans["annotator_1"], "annotator_2", humans["annotator_2"])
    assert len(dh) == 1
    assert next(m for m in mh if m.field == "is_lean_contributed").exact_agreement == pytest.approx(1.0)

    multi = evaluate_multirater_alpha(humans)
    assert multi["lean_usage_status (all)"]["krippendorff_alpha"] == pytest.approx(1.0)


def test_invalid_enum_raises_clear_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)
        w.writerow(["2026-11", "2611.00001", "annotator_1", "lean_contributed", "engineering_math_proof", "P1_paper_first_posthoc", "Tier3_gold", "unclear", ""])

    with pytest.raises(ValueError, match="invalid value 'Tier3_gold'"):
        load_human_annotations(csv_path)


def test_verify_blinding_catches_leaks(tmp_path: Path) -> None:
    dossier = tmp_path / "dossier.md"
    blank_csv = tmp_path / "blank.csv"
    html_app = tmp_path / "app.html"

    dossier.write_text("# Clean Blinded Dossier\n\nItem 1: arXiv 2611.00001\n", encoding="utf-8")
    with blank_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)
        w.writerow(["2026-11", "2611.00001", "annotator_1", "", "", "", "", "", ""])
    html_app.write_text(
        '<script id="blind-items-data" type="application/json">[{"arxiv_id":"2611.00001"}]</script>',
        encoding="utf-8",
    )
    assert verify_blinding(dossier, blank_csv, html_app) == []

    # Inject an LLM label leak into dossier and HTML items payload
    dossier.write_text(f"# Dossier\nPrediction: {FORBIDDEN_BLIND_TOKENS[0]}\n", encoding="utf-8")
    html_app.write_text(
        f'<script id="blind-items-data" type="application/json">[{{"arxiv_id":"2611.00001","hint":"{FORBIDDEN_BLIND_TOKENS[1]}"}}]</script>',
        encoding="utf-8",
    )
    violations = verify_blinding(dossier, blank_csv, html_app)
    assert len(violations) == 2
    assert any(FORBIDDEN_BLIND_TOKENS[0] in v for v in violations)
    assert any(FORBIDDEN_BLIND_TOKENS[1] in v for v in violations)
