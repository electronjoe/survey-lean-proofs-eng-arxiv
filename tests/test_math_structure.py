"""Unit tests for Stage E1 mathematical structure parser (`src/screen_math_structure.py`)."""

from __future__ import annotations

import json
from pathlib import Path

from src.screen_math_structure import (
    classify_theorem_env,
    connect_eligibility,
    parse_html_structure,
    summarize_e1_t2,
    upsert_math_structure,
)

SAMPLE_LATEXML_THEORY = """<!DOCTYPE html>
<html>
<body>
<nav class="ltx_TOC">Should be ignored: Theorem 99</nav>
<article class="ltx_document">
  <section class="ltx_section">
    <h2 class="ltx_title ltx_title_section">1 Introduction</h2>
    <p>We study mirror descent for strongly convex optimization.</p>
  </section>
  <section class="ltx_section">
    <h2 class="ltx_title ltx_title_section">2 Theoretical Analysis</h2>
    <div class="ltx_theorem ltx_theorem_defn">
      <h6 class="ltx_title ltx_title_theorem"><span class="ltx_tag ltx_tag_theorem">Definition 1</span> (Strong convexity).</h6>
      <p>A function <math><semantics><mi>f</mi><annotation encoding="application/x-tex">f</annotation></semantics></math> is strongly convex.</p>
    </div>
    <div class="ltx_theorem ltx_theorem_thm">
      <h6 class="ltx_title ltx_title_theorem"><span class="ltx_tag ltx_tag_theorem">Theorem 2.1</span> (Convergence rate).</h6>
      <p>Under Assumption 1, the regret bound satisfies <math display="block"><semantics><mi>R</mi><annotation encoding="application/x-tex">R_T \\le O(\\sqrt{T})</annotation></semantics></math>.</p>
    </div>
    <div class="ltx_proof">
      <h6 class="ltx_title ltx_title_proof">Proof.</h6>
      <p>By standard convexity and telescoping sums we obtain the bound.</p>
    </div>
    <table class="ltx_equation"><tr><td>x=y</td></tr></table>
  </section>
  <section class="ltx_bibliography">
    <p>Navier-Stokes Sobolev space should be ignored in bibliography.</p>
  </section>
</article>
</body>
</html>
"""

SAMPLE_LATEXML_EMPIRICAL = """<!DOCTYPE html>
<html>
<body>
<article class="ltx_document">
  <section class="ltx_section">
    <h2 class="ltx_title ltx_title_section">1 Introduction</h2>
    <p>We introduce a robot grasping benchmark evaluated in Isaac Gym across 50 tasks.</p>
  </section>
  <section class="ltx_section">
    <h2 class="ltx_title ltx_title_section">2 Experiments</h2>
    <p>Our policy achieves 92.4% success rate compared to baselines (see Theorem 1 of Smith et al.).</p>
  </section>
</article>
</body>
</html>
"""


def test_classify_theorem_env_handles_custom_macros() -> None:
    assert classify_theorem_env("Theorem 2.1 (Main)", ["ltx_theorem", "ltx_theorem_thm"]) == "theorem"
    assert classify_theorem_env("Proposition 3.", ["ltx_theorem", "ltx_theorem_myprop"]) == "proposition"
    assert classify_theorem_env("", ["ltx_theorem", "ltx_theorem_lem"]) == "lemma"
    assert classify_theorem_env("Definition 1.", ["ltx_theorem", "ltx_theorem_definition"]) == "definition"
    assert classify_theorem_env("Invariant 2.", ["ltx_theorem", "ltx_theorem_inv"]) == "property_or_invariant"


def test_parse_html_structure_theory_paper() -> None:
    res = parse_html_structure(SAMPLE_LATEXML_THEORY)
    assert res["n_theorem"] == 1
    assert res["n_definition"] == 1
    assert res["n_proof"] == 1
    assert res["n_equation"] == 1
    assert res["n_display_math"] == 1
    assert res["has_theory_section"] == 1
    assert res["e1_bucket"] == "E1_formal_thm_proof"
    # Bibliography should be skipped, so Navier-Stokes cue in bib is NOT triggered
    assert "mathlib_barrier_cues" not in res["domain_cues"]
    assert "optimization_bounds" in res["domain_cues"]["tractable_math_cues"]
    # TeX annotation preserved without duplicating MathML text
    assert "$R_T \\le O(\\sqrt{T})$" in res["evidence_snippet"]
    assert "Theorem 2.1" in res["theorem_snippets"][0]


def test_parse_html_structure_empirical_paper() -> None:
    res = parse_html_structure(SAMPLE_LATEXML_EMPIRICAL)
    assert res["n_theorem"] == 0
    assert res["n_proof"] == 0
    assert res["has_theory_section"] == 0
    assert res["e1_bucket"] == "E1_no_formal_claims"
    assert "BODY_EXCERPT:" in res["evidence_snippet"]


def test_summarize_e1_t2_exports_per_category_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "elig.db"
    out_path = tmp_path / "e1_summary.json"
    conn = connect_eligibility(db_path)
    papers = [
        ("2611.00001", "math.OC", ["math.OC", "eess.SY"], 1, "eng_algorithmic_proof", parse_html_structure(SAMPLE_LATEXML_THEORY)),
        ("2611.00002", "cs.RO", ["cs.RO"], 0, None, parse_html_structure(SAMPLE_LATEXML_EMPIRICAL)),
    ]
    with conn:
        for aid, pcat, mcats, is_lean, role, parsed in papers:
            conn.execute(
                """
                INSERT INTO eligibility_papers (
                    arxiv_id, version, slice_id, title, abstract, primary_category,
                    all_categories_json, matched_15_cats_json, submitted_date,
                    in_t2_census, is_confirmed_lean, confirmed_role_4way
                ) VALUES (?, 1, '2026-11', 't', 'a', ?, ?, ?, '2026-11-01', 1, ?, ?)
                """,
                (aid, pcat, json.dumps(mcats), json.dumps(mcats), is_lean, role),
            )
            upsert_math_structure(
                conn,
                {"arxiv_id": aid, "version": 1, "fetch_source": "html", "http_status": 200, "error_msg": None, **parsed},
            )
    conn.close()

    res = summarize_e1_t2(db_path=db_path, out_path=out_path, panel_path=tmp_path / "nonexistent.json")
    assert out_path.exists()
    assert res["overall"]["total_papers"] == 2
    assert res["overall"]["e1_counts"]["E1_formal_thm_proof"] == 1
    assert res["overall"]["e1_counts"]["E1_no_formal_claims"] == 1
    assert res["overall"]["multi_category_15_overlap_papers"] == 1
    assert res["per_category"]["math.OC"]["total_papers"] == 1
    assert res["per_category"]["math.OC"]["primary_papers"] == 1
    assert res["per_category"]["eess.SY"]["total_papers"] == 1
    assert res["per_category"]["eess.SY"]["cross_list_papers"] == 1
    assert res["per_category"]["cs.RO"]["e1_counts"]["E1_no_formal_claims"] == 1
