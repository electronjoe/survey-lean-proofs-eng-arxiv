"""Dynamic run_workflow script: parallel classification of Lean & Beyond-Lean candidates.

Reads data/workflow_inputs.json, fans out lightweight agents with strict JSON schemas,
and writes results to data/workflow_outputs.json.
"""

import json
from pathlib import Path

inputs_path = Path(args.get("inputs_path", "data/workflow_inputs.json"))
outputs_path = Path(args.get("outputs_path", "data/workflow_outputs.json"))
lean_model = args.get("lean_model", "flash")
other_model = args.get("other_model", "flash_lite")
batch_size = int(args.get("batch_size", 10))

data = json.loads(inputs_path.read_text())
lean_candidates = data["lean_candidates"]
beyond_lean_candidates = data["beyond_lean_candidates"]

LEAN_SCHEMA = {
    "type": "object",
    "properties": {
        "arxiv_id": {"type": "string"},
        "lean_usage_status": {
            "type": "string",
            "enum": ["lean_contributed", "lean_citation_or_discussion", "false_positive"],
        },
        "paper_domain_role": {
            "type": "string",
            "enum": ["engineering_math_proof", "software_or_system_fv", "pure_tcs_or_math", "N/A"],
        },
        "role_4way": {
            "type": "string",
            "enum": [
                "eng_algorithmic_proof",
                "operational_system_fv",
                "pure_math_or_tcs",
                "meta_formalization_system",
                "N/A",
            ],
        },
        "verification_object": {
            "type": "string",
            "enum": [
                "algorithm_convergence_or_bound",
                "physical_or_control_model",
                "numerical_or_stat_method",
                "operational_sw_hw_db_protocol",
                "abstract_math_or_tcs_theorem",
                "meta_proving_pipeline",
                "N/A",
            ],
        },
        "other_formal_tools_contributed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "authoring_paradigm": {
            "type": "string",
            "enum": [
                "P1_paper_first_posthoc",
                "P2_lean_first",
                "P3_blueprint_sync",
                "P4_speclock_solve_distill",
                "P0_opaque_or_unspecified",
                "N/A",
            ],
        },
        "paradigm_confidence": {
            "type": "string",
            "enum": ["high", "medium", "low", "N/A"],
        },
        "paradigm_evidence": {"type": "string"},
        "verification_tier_observed": {
            "type": "string",
            "enum": ["Tier3_Gold", "Tier2_Silver", "Tier1_Bronze", "N/A"],
        },
        "ai_agent_assisted": {
            "type": "string",
            "enum": ["explicitly_yes", "explicitly_no", "unclear", "N/A"],
        },
        "ai_tools_mentioned": {
            "type": "array",
            "items": {"type": "string"},
        },
        "artifact_availability": {
            "type": "string",
            "enum": ["public_lean_repo", "appendix_only", "broken_or_missing_repo", "none", "N/A"],
        },
        "static_risk_flags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "one_line_summary": {"type": "string"},
    },
    "required": [
        "arxiv_id",
        "lean_usage_status",
        "paper_domain_role",
        "role_4way",
        "verification_object",
        "other_formal_tools_contributed",
        "authoring_paradigm",
        "paradigm_confidence",
        "paradigm_evidence",
        "verification_tier_observed",
        "ai_agent_assisted",
        "ai_tools_mentioned",
        "artifact_availability",
        "static_risk_flags",
        "one_line_summary",
    ],
}

BEYOND_LEAN_SCHEMA = {
    "type": "object",
    "properties": {
        "arxiv_id": {"type": "string"},
        "formal_usage_status": {
            "type": "string",
            "enum": ["formal_contributed", "citation_or_discussion", "false_positive"],
        },
        "tools_contributed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "tool_category": {
            "type": "string",
            "enum": ["ITP", "model_checker", "protocol_verifier", "smt_sat", "mixed", "N/A"],
        },
        "one_line_summary": {"type": "string"},
    },
    "required": [
        "arxiv_id",
        "formal_usage_status",
        "tools_contributed",
        "tool_category",
        "one_line_summary",
    ],
}

LEAN_RUBRIC = """You are classifying an engineering/systems/control/CS arXiv paper for a formal-verification survey.
Base your judgment strictly on the provided evidence (and if `local_repo_dirs` is non-empty, you MAY read README.md, lakefile.*, or 1-2 representative .lean files inside that local directory to confirm authoring workflow and static risks).

Taxonomy of Lean <-> LaTeX Authoring Paradigms (from proof-methods.md):
- P1_paper_first_posthoc: Paper/proofs developed informally first; Lean formalization created afterward or loosely attached without synchronized blueprint/spec-lock tooling.
- P2_lean_first: Lean proof developed first and the human manuscript/exposition was written or auto-informalized directly against the Lean code.
- P3_blueprint_sync: Spec-pinned synchronized co-development using LeanArchitect (@[blueprint], \\inputleannode), leanblueprint, or Verso Blueprints keeping LaTeX and Lean structurally synced.
- P4_speclock_solve_distill: Frozen Challenge.lean / Solution.lean spec-lock (e.g., via `comparator`), unconstrained (often AI) proof search, followed by conceptual distillation/refactoring into a clean paper/blueprint.
- P0_opaque_or_unspecified: Paper clearly claims Lean verification/formalization of its own results, but provides neither public Lean code nor enough workflow detail to tell which paradigm was used.
- N/A: Paper does NOT contribute Lean proofs of its own results (either `lean_citation_or_discussion` or `false_positive`).

Verification Tiers (observed from static evidence only):
- Tier3_Gold: Main theorem(s) publicly formalized in Lean, zero sorry/custom axiom/native_decide, AND evidence of rigorous spec/kernel audit (e.g., blueprint sync, comparator, multi-kernel/leanchecker, `#print axioms`, or explicit audit manifest).
- Tier2_Silver: Public Lean repo with real compiling-looking proofs (0 sorry/axiom or minor gaps), partial/supporting lemmas or standard `lake build` without comparator/multi-kernel/blueprint sync.
- Tier1_Bronze: Claimed Lean verification without public artifact, OR contains `sorry`/custom `axiom`/`native_decide`, OR unchecked agent-only dump.
- N/A: Not `lean_contributed`.

Static Risk Flags (include any clearly evidenced):
- Mode2_ScopeDowngrade (only partial/supporting lemma or simplified model formalized vs headline claim)
- Mode3_CustomDefs (ONLY for `eng_algorithmic_proof` or `pure_math_or_tcs` papers: heavy custom mathematical definitions with little/no Mathlib anchoring where standard Mathlib objects exist. Do NOT apply `Mode3_CustomDefs` to `operational_system_fv` repos solely for lacking Mathlib imports — state machines, DB/CDC logs, protocols, ISAs, and type calculi legitimately use zero-dependency Lean 4 core!)
- Mode6_SorryOrAxiomOrNativeDecide (`sorry`, tactic `admit` [NOT inductive constructors named `admit`], custom `axiom`, or `native_decide` present)
- Mode7_MetaprogOrUnsafe (`unsafe`, `implemented_by`, `#eval`, or notation/macro overrides)
- Mode10_ProofBloat (very large/verbose Lean codebase relative to claims, e.g., >20k LoC; note for `operational_system_fv`, large multi-module protocol mechanizations with clean structure/audits are expected baseline boilerplate rather than bloat)
- Mode12_ProcessOpacity (no public repo, missing toolchain/CI, or unclear verification scope)
- OpFV_RefinementGap (for `operational_system_fv` only: abstract Lean model verified without mechanized refinement or verified extraction to the real software/DB/hardware implementation)
- OpFV_SafetyOnlyNoLiveness (for `operational_system_fv` only: safety/invariant preservation proved without mechanized liveness/progress)

4-Way Domain Role (`role_4way`, for `lean_contributed` papers; use `N/A` otherwise — apply strictly in sequential Gate 1 -> Gate 4 order per `docs/track1_4way_coding_rubric.md`):
- Gate 1 -> `meta_formalization_system`: Primary contribution is an automated proving/autoformalization system, agentic pipeline, or benchmark generating/verifying Lean proofs across *other* problems/papers (e.g., Paper2Lean, LongTails, Colombo).
- Gate 2 -> `operational_system_fv`: Primary verified object is operational correctness (safety, liveness, crash consistency, type/memory safety, policy enforcement, RTL/ISA equivalence, consensus/protocol state machines) of a software system, DB/CDC pipeline, hardware/chip design, VM, or security protocol.
- Gate 3 -> `eng_algorithmic_proof`: Proves mathematical/analytical properties (convergence, stability, regret, optimality, error bounds, identifiability, capacity/decoding guarantees, physical/dynamical/PDE bounds) of a concrete engineering algorithm, controller, estimator, numerical solver, or physical/cyber-physical system.
- Gate 4 -> `pure_math_or_tcs`: Primary contribution is a theorem in pure mathematics (algebra, geometry, number theory, ergodic theory, operator algebras), theoretical CS (complexity classes, CONGEST/graph algorithms, combinatorics, formal logic), or foundational quantum information.

Also populate `verification_object` (`algorithm_convergence_or_bound`, `physical_or_control_model`, `numerical_or_stat_method`, `operational_sw_hw_db_protocol`, `abstract_math_or_tcs_theorem`, `meta_proving_pipeline`, or `N/A`) and legacy `paper_domain_role` (mapping `eng_algorithmic_proof` or `meta_formalization_system` -> `engineering_math_proof`, `operational_system_fv` -> `software_or_system_fv`, `pure_math_or_tcs` -> `pure_tcs_or_math`, `N/A` -> `N/A`).

Be conservative: if a paper only cites Lean/Mathlib in related work or evaluates LLM theorem proving benchmarks on Lean without formalizing its own paper's theorems, classify as `lean_citation_or_discussion`. If "Lean" means lean manufacturing/architecture/body mass, classify as `false_positive`."""

BEYOND_LEAN_RUBRIC = """You are classifying an arXiv paper that matched a non-Lean formal verification keyword (Coq/Rocq, Isabelle, Agda, TLA+, PRISM, UPPAAL, NuSMV, Alloy, Maude, Tamarin, ProVerif, EasyCrypt, Z3/CVC5/SMT, Dafny, etc.).
Based ONLY on the provided metadata and matched snippets (do not browse the web or run commands):
- Classify `formal_usage_status`:
  - `formal_contributed`: The authors actually used a formal verifier/prover/model checker/SMT solver to verify or synthesize results in this paper.
  - `citation_or_discussion`: Only mentions/cites formal tools in background/related work/future work.
  - `false_positive`: Ambiguous keyword hit unrelated to formal verification (e.g., optical prism, alloy metal, spin physics, etc.).
- List canonical `tools_contributed` (empty list if not `formal_contributed`)."""


def make_lean_prompt(item):
    # Compact payload to keep token usage lean
    compact = {
        "arxiv_id": item["arxiv_id"],
        "title": item["title"],
        "primary_category": item["primary_category"],
        "matched_target_cats": item["matched_target_cats"],
        "submitted_date": item["submitted_date"],
        "comment": item["comment"],
        "journal_ref": item["journal_ref"],
        "abstract": item["abstract"],
        "urls": item["urls"][:8],
        "lean_hits": item["lean_hits"],
        "other_hits_tools": {g: list(t.keys()) for g, t in item["other_hits"].items()},
        "latex_signals": item["latex_signals"],
        "repos": item["repos"],
        "local_repo_dirs": item["local_repo_dirs"],
    }
    return f"Classify Lean paper {item['arxiv_id']}.\n\n{LEAN_RUBRIC}\n\nEvidence JSON:\n```json\n{json.dumps(compact, indent=2)}\n```"


def make_other_prompt(item):
    compact = {
        "arxiv_id": item["arxiv_id"],
        "title": item["title"],
        "primary_category": item["primary_category"],
        "matched_target_cats": item["matched_target_cats"],
        "abstract": item["abstract"],
        "other_hits": item["other_hits"],
        "urls": item["urls"][:5],
    }
    return f"Classify Beyond-Lean paper {item['arxiv_id']}.\n\n{BEYOND_LEAN_RUBRIC}\n\nEvidence JSON:\n```json\n{json.dumps(compact, indent=2)}\n```"


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


phase("Classify Lean Candidates")
log(f"Classifying {len(lean_candidates)} Lean candidates using model={lean_model}...")
lean_results = []
for idx, batch in enumerate(chunks(lean_candidates, batch_size), 1):
    res = await parallel(
        batch,
        lambda item: agent(
            make_lean_prompt(item),
            schema=LEAN_SCHEMA,
            role=f"Lean {item['arxiv_id']}",
            type_name="research",
            model=lean_model,
        ),
    )
    lean_results.extend(res)
    log(f"  Completed Lean batch {idx} ({len(lean_results)}/{len(lean_candidates)})")

phase("Classify Beyond-Lean Candidates")
log(f"Classifying {len(beyond_lean_candidates)} Beyond-Lean candidates using model={other_model}...")
other_results = []
for idx, batch in enumerate(chunks(beyond_lean_candidates, batch_size), 1):
    res = await parallel(
        batch,
        lambda item: agent(
            make_other_prompt(item),
            schema=BEYOND_LEAN_SCHEMA,
            role=f"Formal {item['arxiv_id']}",
            type_name="research",
            model=other_model,
        ),
    )
    other_results.extend(res)
    log(f"  Completed Beyond-Lean batch {idx} ({len(other_results)}/{len(beyond_lean_candidates)})")

phase("Save Outputs")
out = {
    "lean_model": lean_model,
    "other_model": other_model,
    "lean_results": lean_results,
    "beyond_lean_results": other_results,
}
outputs_path.parent.mkdir(parents=True, exist_ok=True)
outputs_path.write_text(json.dumps(out, indent=2))
log(f"Saved {len(lean_results)} Lean + {len(other_results)} Beyond-Lean classifications to {outputs_path}")
print(json.dumps({
    "lean_total": len(lean_results),
    "lean_contributed": sum(1 for r in lean_results if r["lean_usage_status"] == "lean_contributed"),
    "beyond_lean_total": len(other_results),
    "beyond_lean_contributed": sum(1 for r in other_results if r["formal_usage_status"] == "formal_contributed"),
}))
