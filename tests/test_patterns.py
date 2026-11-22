"""Unit tests for deterministic detectors and Lean comment-stripping lexer in `src/patterns.py`."""

from __future__ import annotations

from src.patterns import (
    scan_latex_source,
    scan_lean_source,
    scan_text,
    strip_lean_comments,
)


class TestLeanTextDetectors:
    def test_strong_lean_signals(self) -> None:
        text = (
            "We formalize Theorem 3 in Lean 4 using Mathlib4, "
            "pinned via lakefile.toml and verified with lean4checker."
        )
        res = scan_text(text)
        assert res["has_lean_strong"] is True
        strong = res["lean_hits"]["strong"]
        assert "lean_version" in strong
        assert "mathlib" in strong
        assert "lakefile" in strong
        assert "lean_verifiers" in strong

    def test_strong_lean_blueprint_and_prover_phrase(self) -> None:
        text = "The proofs are synchronized with LeanArchitect using the Lean proof assistant."
        res = scan_text(text)
        assert res["has_lean_strong"] is True
        assert "lean_blueprint" in res["lean_hits"]["strong"]
        assert "lean_prover_phrase" in res["lean_hits"]["strong"]

    def test_contextual_lean_near_formal_terms(self) -> None:
        text = "All convergence lemmas were checked automatically in our Lean theorem environment."
        res = scan_text(text)
        assert res["has_lean_contextual"] is True
        assert res["lean_hits"]["contextual"]["count"] >= 1

    def test_false_positive_exclusions(self) -> None:
        noise_samples = [
            "We apply lean manufacturing principles to optimize theorem-like scheduling bounds.",
            "Our lean startup methodology improves verification of agile supply chains.",
            "The robot adjusts its lean angle while proving trajectory stability.",
            "Lean combustion mixtures were analyzed with an analytical proof of flame speed.",
            "We measure lean body mass and verify sensor calibration.",
        ]
        for sample in noise_samples:
            res = scan_text(sample)
            assert res["has_lean_strong"] is False, f"Unexpected strong hit on: {sample}"
            assert res["has_lean_contextual"] is False, f"Unexpected contextual hit on: {sample}"

    def test_repo_url_extraction(self) -> None:
        text = (
            "Artifacts are hosted at https://github.com/example/opt-lean.git, "
            "https://zenodo.org/records/12345678, and https://gitlab.example.edu/group/proj."
        )
        res = scan_text(text)
        assert "https://github.com/example/opt-lean.git" in res["urls"]
        assert "https://zenodo.org/records/12345678" in res["urls"]
        assert "https://gitlab.example.edu/group/proj" in res["urls"]


class TestBeyondLeanDetectors:
    def test_other_itps(self) -> None:
        res = scan_text("We mechanized the consensus invariant in Isabelle/HOL and compared with Rocq and Dafny.")
        assert res["has_other_itp"] is True
        itp = res["other_hits"]["itp"]
        assert "isabelle" in itp
        assert "coq_rocq" in itp
        assert "dafny" in itp

    def test_model_checkers(self) -> None:
        res = scan_text("Safety invariants are checked with TLA+ and timed automata are verified in UPPAAL.")
        assert res["has_model_checker"] is True
        mc = res["other_hits"]["model_checker"]
        assert "tla_plus" in mc
        assert "uppaal" in mc

    def test_protocol_verifiers_and_tamarin_disambiguation(self) -> None:
        pos = scan_text("We model the handshake protocol in Tamarin prover and ProVerif to verify authentication.")
        assert pos["has_protocol_verifier"] is True
        assert "tamarin" in pos["other_hits"]["protocol_verifier"]
        assert "proverif" in pos["other_hits"]["protocol_verifier"]

        # Bare biological "Tamarin" without security/protocol context must be filtered out
        neg = scan_text("We recorded vocalizations of the cotton-top Tamarin monkey in tropical forest canopies.")
        assert neg["has_protocol_verifier"] is False

    def test_smt_solvers(self) -> None:
        res = scan_text("Feasibility constraints are discharged via the Z3 SMT solver and cvc5.")
        assert res["has_smt_sat"] is True
        assert "z3_cvc" in res["other_hits"]["smt_sat"]


class TestLeanCommentStrippingAndScanner:
    def test_strip_line_and_nested_block_comments(self) -> None:
        code = (
            "import Mathlib\n"
            "-- sorry axiom native_decide in line comment\n"
            "/- outer comment\n"
            "   /- nested comment with sorry and admit -/\n"
            "   still inside outer comment: axiom fake : False\n"
            "-/\n"
            "theorem real_thm : True := trivial\n"
        )
        cleaned = strip_lean_comments(code)
        assert "sorry" not in cleaned
        assert "admit" not in cleaned
        assert "native_decide" not in cleaned
        assert "axiom fake" not in cleaned
        assert "theorem real_thm : True := trivial" in cleaned

    def test_scan_lean_source_ignores_red_flags_in_comments(self) -> None:
        code = (
            "import Mathlib.Analysis.Normed.Field.Basic\n"
            "-- Note: we replaced sorry and native_decide with a full proof\n"
            "/- Old draft used:\n"
            "   axiom cheated : False\n"
            "   /- nested: sorry admit -/\n"
            "-/\n"
            "@[blueprint]\n"
            "def helper (n : Nat) : Nat := n + 1\n"
            "theorem convergence : 1 + 1 = 2 := by rfl\n"
        )
        counts = scan_lean_source(code)
        assert counts.get("sorry", 0) == 0
        assert counts.get("admit", 0) == 0
        assert counts.get("custom_axiom", 0) == 0
        assert counts.get("native_decide", 0) == 0
        assert counts.get("def_decl") == 1
        assert counts.get("theorem_decl") == 1
        assert counts.get("mathlib_import") == 1
        assert counts.get("blueprint_attr") == 1
        assert counts["loc_nonempty"] == 9

    def test_scan_lean_source_detects_live_red_flags(self) -> None:
        code = (
            "axiom unproved_bound : True\n"
            "theorem t1 : True := by sorry\n"
            "theorem t2 : 2 + 2 = 4 := by native_decide\n"
            "unsafe def badImpl : Nat := 0\n"
            "#print axioms t2\n"
        )
        counts = scan_lean_source(code)
        assert counts["custom_axiom"] == 1
        assert counts["sorry"] == 1
        assert counts["native_decide"] == 1
        assert counts["unsafe_or_impl_by"] == 1
        assert counts["print_axioms"] == 1
        assert counts["theorem_decl"] == 2


class TestLatexScanner:
    def test_blueprint_macros_and_ai_disclosure(self) -> None:
        tex = (
            "\\usepackage{leanblueprint}\n"
            "\\begin{theorem}\\label{thm:main}\\lean{Opt.main}\\leanok\\uses{lem:aux}\n"
            "Main convergence result.\n"
            "\\end{theorem}\n"
            "\\inputleannode{Opt.main}\n"
            "Formalization was assisted by Claude and Aristotle.\n"
        )
        sig = scan_latex_source(tex)
        assert sig["leanblueprint_pkg"] == 1
        assert sig["theorem_envs"] == 1
        assert sig["lean_macro"] == 2
        assert sig["blueprint_uses"] == 1
        assert sig["inputleannode"] == 1
        assert set(sig["agent_tools"]) == {"Aristotle", "Claude"}
