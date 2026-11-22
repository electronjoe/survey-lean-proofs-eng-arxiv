"""Phase 2 dynamic run_workflow: Deep Layer-A semantic drift audit on cloned engineering_math_proof papers.

Fetches no network data; each read-only `research` agent (model='pro') reads the local
math-preserving paper markdown and the local cloned Lean repository to check Modes #1-#4
from proof-methods.md (statement drift, scope downgrading, definition smuggling, junk/vacuity).
"""

import json
from pathlib import Path

inputs_path = Path(args.get("inputs_path", "data/phase2_inputs.json"))
outputs_path = Path(args.get("outputs_path", "data/phase2_outputs.json"))
audit_model = args.get("audit_model", "pro")

data = json.loads(inputs_path.read_text())
targets = data["targets"]

MODE_OBJ = {
    "type": "object",
    "properties": {
        "severity": {
            "type": "string",
            "enum": ["none", "minor_disclosed", "minor_undisclosed", "moderate", "severe"],
        },
        "summary": {"type": "string"},
        "concrete_examples": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["severity", "summary", "concrete_examples"],
}

AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "arxiv_id": {"type": "string"},
        "primary_repo_audited": {"type": "string"},
        "overall_fidelity": {
            "type": "string",
            "enum": [
                "high_faithful",
                "mostly_faithful_with_disclosed_gaps",
                "partial_or_weakened_formalization",
                "material_undisclosed_drift_or_risk",
            ],
        },
        "theorems_compared": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "paper_claim": {"type": "string"},
                    "lean_declaration": {"type": "string"},
                    "lean_file_and_line": {"type": "string"},
                    "alignment_verdict": {
                        "type": "string",
                        "enum": [
                            "faithful",
                            "disclosed_narrower_or_omitted",
                            "undisclosed_hypothesis_strengthening",
                            "undisclosed_conclusion_weakening",
                            "custom_def_risk",
                            "not_found_in_lean",
                        ],
                    },
                    "delta_notes": {"type": "string"},
                },
                "required": [
                    "paper_claim",
                    "lean_declaration",
                    "lean_file_and_line",
                    "alignment_verdict",
                    "delta_notes",
                ],
            },
        },
        "mode1_statement_drift": MODE_OBJ,
        "mode2_scope_downgrade": MODE_OBJ,
        "mode3_definition_smuggling": MODE_OBJ,
        "mode4_junk_or_vacuity": MODE_OBJ,
        "has_non_vacuity_witnesses": {"type": "boolean"},
        "mathlib_anchoring_quality": {
            "type": "string",
            "enum": ["strong_mathlib", "mixed_custom_and_mathlib", "mostly_custom_defs"],
        },
        "notable_good_practices": {
            "type": "array",
            "items": {"type": "string"},
        },
        "executive_verdict": {"type": "string"},
    },
    "required": [
        "arxiv_id",
        "primary_repo_audited",
        "overall_fidelity",
        "theorems_compared",
        "mode1_statement_drift",
        "mode2_scope_downgrade",
        "mode3_definition_smuggling",
        "mode4_junk_or_vacuity",
        "has_non_vacuity_witnesses",
        "mathlib_anchoring_quality",
        "notable_good_practices",
        "executive_verdict",
    ],
}

AUDIT_RUBRIC = """You are an adversarial formal-verification referee conducting a **Phase 2 Layer-A Semantic Fidelity Audit** (following proof-methods.md Modes #1-#4) on an engineering/applied-theory paper and its local Lean 4 repository.

Your workflow (strictly read-only on local files — do NOT run network calls or lake build):
1. Read the paper's abstract, main theorem statements, and formalization/verification sections from `paper_markdown_path` (use grep/targeted line reads if the file is long).
2. Inspect the primary paper repository under `cloned_repos` (note: if multiple repos are listed, focus on the repository that actually formalizes THIS paper's results, e.g. `Lean-SysID` for 2611.18220 or `bp-response-geometry-lean` for 2611.11713). Start with README.md, any correspondence/audit/Challenge/Main/Theorem index files, and then read the exact Lean theorem declarations AND the custom definitions they depend on.
3. Pair **2 to 5 principal theorems/results** from the paper with their exact Lean declaration names and `file:line` locations.
4. Scrutinize all four Layer-A failure modes rigorously and cite exact `file:line` and declaration names:
   - **Mode #1 (Statement & Hypothesis Drift — Type i vs Type ii):** Compare hypotheses, quantifiers, domains (e.g., `Real` vs `Nat`/`Int`, finite vs infinite, extra boundedness/regularity/positivity/non-degeneracy assumptions), and conclusions between prose and Lean. Distinguish *undisclosed* drift from explicitly disclosed gaps.
   - **Mode #2 (Scope Downgrading / Headline-to-Certificate Mismatch):** Does Lean check the actual headline theorem in the abstract, or only a special case, weaker constant, or auxiliary lemma? Note whether the gap is prominently disclosed in the abstract/intro (`minor_disclosed`) vs hidden/buried (`moderate`/`severe`).
   - **Mode #3 (Definition Smuggling & Mathlib Anchoring):** Inspect the transitive definitions used in the main theorem signatures. Are they anchored to standard Mathlib objects, or are key mathematical concepts re-defined as custom predicates/structures that could subtly diverge from textbook definitions or make the theorem artificially easy?
   - **Mode #4 (Junk Values & Vacuous Truth):** Check for unguarded division (`1 / 0 = 0`), truncated `Nat` subtraction (`a - b = 0`), empty-type / potentially contradictory hypotheses, and whether the repo includes explicit non-vacuity witnesses (`example : ∃ ...`) or concrete instantiations proving hypotheses are jointly satisfiable.

Be fair, precise, and evidence-driven: never invent discrepancies that aren't in the code, and never rubber-stamp a paper without actually reading the Lean theorem signatures and their underlying definitions!"""


def make_prompt(t):
    return (
        f"Audit Layer-A semantic fidelity for arXiv:{t['arxiv_id']} — {t['title']}\n\n"
        f"{AUDIT_RUBRIC}\n\n"
        f"Target metadata:\n```json\n{json.dumps(t, indent=2)}\n```"
    )


phase("Phase 2 Layer-A Semantic Drift Audit")
log(f"Launching {len(targets)} parallel '{audit_model}' auditor agents...")

results = await parallel(
    targets,
    lambda t: agent(
        make_prompt(t),
        schema=AUDIT_SCHEMA,
        role=f"Audit {t['arxiv_id']}",
        type_name="research",
        model=audit_model,
    ),
)

phase("Save Phase 2 Outputs")
outputs_path.parent.mkdir(parents=True, exist_ok=True)
outputs_path.write_text(json.dumps({"audit_model": audit_model, "audits": results}, indent=2))
log(f"Saved {len(results)} Layer-A audits to {outputs_path}")
print(
    json.dumps(
        [
            {
                "arxiv_id": r["arxiv_id"],
                "overall_fidelity": r["overall_fidelity"],
                "m1": r["mode1_statement_drift"]["severity"],
                "m2": r["mode2_scope_downgrade"]["severity"],
                "m3": r["mode3_definition_smuggling"]["severity"],
                "m4": r["mode4_junk_or_vacuity"]["severity"],
            }
            for r in results
        ],
        indent=2,
    )
)
