"""Dynamic run_workflow script: batched classification of arXiv papers into
Lean 4 eligibility tiers (L1-L5) for denominator-adjusted adoption analysis.

Batches 5 papers per agent prompt to minimize repeated rubric tokens (~1,100
tokens/paper total on flash/flash_lite). Strictly read-only, schema-locked.
"""

import json
from pathlib import Path

inputs_path = Path(args.get("inputs_path", "data/eligibility_pilot_e0_in.json"))
outputs_path = Path(args.get("outputs_path", "data/eligibility_pilot_e0_out.json"))
model_tier = args.get("model", "flash")
papers_per_prompt = int(args.get("papers_per_prompt", 5))
concurrency = int(args.get("concurrency", 8))

payload = json.loads(inputs_path.read_text())
items = payload["items"]

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "arxiv_id": {"type": "string"},
        "eligibility_class": {
            "type": "string",
            "enum": [
                "L1_lean_amenable_math",
                "L2_mathlib_blocked_math",
                "L3_operational_spec_fv",
                "L4_heuristic_or_numerical_only",
                "L5_empirical_or_survey",
            ],
        },
        "has_original_deductive_proof": {"type": "boolean"},
        "dominant_math_area": {
            "type": "string",
            "enum": [
                "optimization_convex_or_nonconvex",
                "control_dynamical_systems",
                "game_theory_econ_mechanism",
                "info_coding_signal_theory",
                "discrete_graph_tcs_crypto",
                "pde_fluid_continuum_mechanics",
                "stochastic_prob_statistics",
                "systems_protocol_sw_hw_spec",
                "none_or_empirical",
            ],
        },
        "primary_barrier_if_L2": {
            "type": "string",
            "enum": [
                "pde_sobolev_continuum",
                "stochastic_sde_ito",
                "measure_prob_asymptotics",
                "operator_spectral_infinite_dim",
                "numerical_floating_point_hybrid",
                "other",
                "N/A",
            ],
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
        "rationale": {"type": "string"},
    },
    "required": [
        "arxiv_id",
        "eligibility_class",
        "has_original_deductive_proof",
        "dominant_math_area",
        "primary_barrier_if_L2",
        "confidence",
        "rationale",
    ],
}

BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": ITEM_SCHEMA,
        }
    },
    "required": ["results"],
}

RUBRIC = """You are classifying engineering/applied-theory arXiv papers on whether they COULD REASONABLY HAVE USED Lean 4 (or a formal verifier) to validate their main claims.
Base your judgment ONLY on the provided JSON evidence (do NOT browse the web, read external files, or run commands).

Assign each paper EXACTLY ONE `eligibility_class`:
- `L1_lean_amenable_math`: Paper asserts and deductively proves original mathematical/algorithmic theorems, propositions, or lemmas whose core proof machinery is broadly tractable in Lean 4 + Mathlib today (e.g., finite-dimensional linear algebra, convex/nonconvex optimization convergence or regret bounds, game theory/mechanism design/auctions, discrete math/graphs/TCS/combinatorics, algebraic coding/information theory, cryptographic reductions over finite groups/rings, elementary real/complex analysis, finite-dim probability/concentration, discrete-time or finite-dim Lyapunov/control stability, symbolic/algebraic dynamical systems). NOTE: If a paper proves rigorous theorems in these areas, choose `L1_lean_amenable_math` even if formalizing it would still require nontrivial effort (weeks, not multi-year missing Mathlib foundations).
- `L2_mathlib_blocked_math`: Paper asserts and deductively proves original rigorous mathematical theorems, BUT its core proofs rely heavily on advanced continuous/analytic/stochastic infrastructure currently absent or highly immature in Mathlib 4 (e.g., nonlinear PDEs / Navier-Stokes / Euler / Sobolev weak solutions, Ito stochastic calculus / SDEs / SPDEs / Fokker-Planck, viscosity solutions of HJB PDEs, deep random-matrix asymptotics / free probability, heavy infinite-dimensional functional/operator-theoretic PDE regularity).
- `L3_operational_spec_fv`: Paper's primary formalizable contribution is NOT classical mathematical theorem-proving, BUT operational correctness of a software/hardware/distributed/network/cryptographic/database system or protocol (state-machine safety/liveness invariants, consensus, type/memory safety, compiler/VM/RTL/ISA equivalence, policy enforcement, protocol security models) amenable to Lean 4 or specialized FV (TLA+/Coq/ProVerif/SMT).
- `L4_heuristic_or_numerical_only`: Paper contains equations, derivations, or informal claims/propositions, BUT relies on heuristic approximations (e.g., dropping higher-order terms, physics scaling arguments, unrigorous linearizations) or establishes guarantees only numerically (simulations, floating-point SDP/LMI solvers) without deductive mathematical proofs.
- `L5_empirical_or_survey`: Empirical/experimental evaluation, ML architecture/training/benchmark paper, robotics/hardware prototype, dataset, or survey/position paper without original deductive proofs or formal system specs (even if it cites prior theorems in background, or builds an LLM autoformalization benchmark over external problems).

Rules:
- Judge by the paper's OWN main scientific claims, not cited background theorems.
- Do NOT rely blindly on `e1_bucket`: IEEE/systems papers sometimes have unnumbered analytical proofs (`L1`/`L2`) or operational protocol specs (`L3`) despite `e1_counts.theorem == 0`; conversely, some papers with 1 restated theorem are `L4` or `L5`.
- Set `primary_barrier_if_L2` to `N/A` unless `eligibility_class == "L2_mathlib_blocked_math"`.
- Keep `rationale` to ONE concise sentence (<=25 words) citing concrete evidence from the abstract/snippets.
- Return ONE entry in `results` for EVERY `arxiv_id` in the input list, preserving exact `arxiv_id` strings."""


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def make_batch_prompt(batch_items):
    ids = ", ".join(it["arxiv_id"] for it in batch_items)
    return (
        f"Classify {len(batch_items)} arXiv papers for Lean 4 eligibility: {ids}.\n\n"
        f"{RUBRIC}\n\n"
        f"Input papers JSON:\n```json\n{json.dumps(batch_items, indent=2)}\n```"
    )


batches = list(chunks(items, papers_per_prompt))
phase("Classify Lean Eligibility (Batched)")
log(f"Classifying {len(items)} papers in {len(batches)} batches (size={papers_per_prompt}, model={model_tier})...")

all_results = []
for wave_idx, wave in enumerate(chunks(batches, concurrency), 1):
    wave_res = await parallel(
        wave,
        lambda b: agent(
            make_batch_prompt(b),
            schema=BATCH_SCHEMA,
            role=f"Elig {b[0]['arxiv_id']}..{b[-1]['arxiv_id']} ({len(b)})",
            type_name="research",
            model=model_tier,
        ),
    )
    for b, res in zip(wave, wave_res):
        got = {r["arxiv_id"]: r for r in res["results"]}
        expected_ids = [it["arxiv_id"] for it in b]
        missing = [aid for aid in expected_ids if aid not in got]
        if missing:
            raise RuntimeError(f"Batch missing arxiv_ids: {missing}")
        for aid in expected_ids:
            all_results.append(got[aid])
    log(f"  Completed wave {wave_idx} ({len(all_results)}/{len(items)} papers)")

phase("Save Outputs")
out = {
    "cohort": payload.get("cohort", "unknown"),
    "model": model_tier,
    "papers_per_prompt": papers_per_prompt,
    "count": len(all_results),
    "results": all_results,
}
outputs_path.parent.mkdir(parents=True, exist_ok=True)
outputs_path.write_text(json.dumps(out, indent=2))

counts = {}
for r in all_results:
    c = r["eligibility_class"]
    counts[c] = counts.get(c, 0) + 1
log(f"Saved {len(all_results)} classifications to {outputs_path}: {counts}")
print(json.dumps({"count": len(all_results), "class_counts": counts}))
