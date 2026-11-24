# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2025-11-01` to `2025-11-19` (3 weeks)
- **Target categories (7):** `cs.CE`, `cs.GT`, `cs.PF`, `eess.AS`, `eess.IV`, `math.DS`, `physics.flu-dyn`
- **Corpus size:** 849 unique papers (838 full-text screened, 98.70% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 845 unique papers
- **Confirmed papers contributing Lean proofs (all):** **1** (0.12% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **1** (0.12% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **0** (0.00% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **0**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CE` | 103 | 0 | 0.00% | 0 |
| `cs.GT` | 101 | 1 | 0.99% | 0 |
| `cs.PF` | 43 | 0 | 0.00% | 0 |
| `eess.AS` | 81 | 0 | 0.00% | 0 |
| `eess.IV` | 159 | 0 | 0.00% | 0 |
| `math.DS` | 189 | 0 | 0.00% | 0 |
| `physics.flu-dyn` | 181 | 0 | 0.00% | 0 |
| **Deduplicated Union** | **849** | **1** | **0.12%** | **0** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_contributed` | 1 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 1 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 0 |
| `P0_opaque_or_unspecified` | 0 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'pure_tcs_or_math': 1}
- **Observed Verification Tiers:** {'Tier3_Gold': 1}
- **Artifact Availability:** {'public_lean_repo': 1}
- **AI/Agent Assistance Disclosed:** {'explicitly_yes': 1}
- **Target Categories (Lean Contributed):** {'cs.GT': 1}
- **Static Risk Flags (`proof-methods.md`):** {'Mode2_ScopeDowngrade': 1, 'Mode10_ProofBloat': 1}

## 4. Detailed Inventory of Confirmed Lean Papers (1)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2511.13056](https://arxiv.org/abs/2511.13056) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **A Strongly Polynomial-Time 7/9-Approximation Algorithm for Maximin Sha** — Formalizes in Lean 4 (with Mathlib, leanchecker audit, and GPT-5/6 assistance) the 7/9-MMS allocation guarantee and polynomial search bounds of a strongly polynomial-time fair-division algorithm, omitting total RAM running-time/bit-complexity refinement. |

### Evidence Notes per Confirmed Lean Paper

#### [2511.13056](https://arxiv.org/abs/2511.13056) — A Strongly Polynomial-Time 7/9-Approximation Algorithm for Maximin Share Allocations
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['GPT-5.6 Pro', 'GPT-6 Pro', 'GPT-6.1 Sol'])
- **Evidence:** docs/research/seven_ninths_mms.md states the Lean development follows CONSOLIDATED_PROOF_REVISED.pdf and STOC_re7.tex, the paper says 'Finally, we formalize and verify our main results in Lean 4' with LLM interaction, and docs/knowledge (mdblueprint) contains no SevenNinths nodes.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `ARTHURCHOU/EconCSLib-7-9MMS` (github):** `.lean` files=695, LoC=125943, theorems=4063, defs=2190, sorry=48, axiom=0, native_decide=19, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0`, ci=`['lake build', 'leanchecker']`

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {}
- **Tool categories (contributed):** {}

| Formal Tool | Papers Contributing |
| :--- | ---: |

### Confirmed Beyond-Lean Papers
