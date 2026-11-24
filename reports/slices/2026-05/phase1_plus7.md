# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2026-05-01` to `2026-05-19` (3 weeks)
- **Target categories (7):** `cs.CE`, `cs.GT`, `cs.PF`, `eess.AS`, `eess.IV`, `math.DS`, `physics.flu-dyn`
- **Corpus size:** 963 unique papers (958 full-text screened, 99.48% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 957 unique papers
- **Confirmed papers contributing Lean proofs (all):** **4** (0.42% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **3** (0.31% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **1** (0.10% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **0**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CE` | 139 | 0 | 0.00% | 0 |
| `cs.GT` | 151 | 2 | 1.32% | 0 |
| `cs.PF` | 63 | 1 | 1.59% | 0 |
| `eess.AS` | 91 | 0 | 0.00% | 0 |
| `eess.IV` | 155 | 0 | 0.00% | 0 |
| `math.DS` | 203 | 1 | 0.49% | 1 |
| `physics.flu-dyn` | 172 | 0 | 0.00% | 0 |
| **Deduplicated Union** | **963** | **4** | **0.42%** | **1** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_contributed` | 4 |
| `lean_citation_or_discussion` | 2 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 3 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 0 |
| `P0_opaque_or_unspecified` | 1 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'pure_tcs_or_math': 2, 'engineering_math_proof': 1, 'software_or_system_fv': 1}
- **Observed Verification Tiers:** {'Tier1_Bronze': 3, 'Tier2_Silver': 1}
- **Artifact Availability:** {'public_lean_repo': 2, 'appendix_only': 1, 'none': 1}
- **AI/Agent Assistance Disclosed:** {'explicitly_yes': 3, 'unclear': 1}
- **Target Categories (Lean Contributed):** {'cs.GT': 2, 'math.DS': 1, 'cs.PF': 1}
- **Static Risk Flags (`proof-methods.md`):** {'Mode2_ScopeDowngrade': 3, 'Mode12_ProcessOpacity': 3, 'Mode6_SorryOrAxiomOrNativeDecide': 1, 'OpFV_RefinementGap': 1}

## 4. Detailed Inventory of Confirmed Lean Papers (4)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2605.06194](https://arxiv.org/abs/2605.06194) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide | **Core Existence in Approval-Based Committee Elections with up to Seven ** — Proves core existence in approval-based committee elections for up to 7 voter types, with a post-hoc AI-assisted Lean 4 formalization of the n<=5 case in ABCVotingLean that relies on an unproved custom axiom (exists_fractional_budget_core). |
| [2605.03338](https://arxiv.org/abs/2605.03338) | `cs.NE` | `math.DS` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `appendix_only` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Symmetry, Defects, and Diffusion in Continuous-memory Recurrent Networ** — Analyzes equivariance, finite-horizon perturbation/leakage bounds, and decoder diffusion optimality for continuous-memory recurrent networks, with selected finite-horizon bounds claimed as machine-checked in a supplementary Lean 4/Mathlib project without a public repository URL. |
| [2605.12537](https://arxiv.org/abs/2605.12537) | `cs.LO` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Biprofile Deviation Logic: Report-Replacement Frames and Audit Witness** — Pure formal-logic/social-choice paper (cs.LO/cs.GT) with a small post-hoc Lean 4 core companion (DevNCore.lean, 129 LoC, 0 sorry) formalizing two-agent finite relational lemmas and factor closure, plus an Alloy 6.2.0 companion. |
| [2605.01140](https://arxiv.org/abs/2605.01140) | `cs.PL` | `cs.PF` | `software_or_system_fv` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity, OpFV_RefinementGap | **SoCal: A Language for Memory-Layout Factorization of Recursive Datatyp** — Introduces SoCal, a typed IR for memory-safe traversals over factored serialized ADTs with Lean 4 mechanized progress, preservation, and type-safety (in unlinked supplementary material), alongside the Colobus compiler to C. |

### Evidence Notes per Confirmed Lean Paper

#### [2605.06194](https://arxiv.org/abs/2605.06194) — Core Existence in Approval-Based Committee Elections with up to Seven Voter Types
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['gpt-5', 'codex', 'claude'])
- **Evidence:** The paper states that a Lean 4 formalization of its n<=5 existence result was produced autonomously in ~10h by gpt-5 in the codex /goal harness, Normality/Main.lean cites 'papers/corefewvoters.tex', and the public ABCVotingLean repo lacks blueprint or Challenge/Solution spec-lock tooling.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `DominikPeters/ABCVotingLean` (github):** `.lean` files=116, LoC=37513, theorems=1414, defs=531, sorry=0, axiom=1, native_decide=2, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.0`, ci=`[]`

#### [2605.03338](https://arxiv.org/abs/2605.03338) — Symmetry, Defects, and Diffusion in Continuous-memory Recurrent Networks
- **Primary / Target Cats:** `cs.NE` / ['math.DS'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Large language models'])
- **Evidence:** Manuscript proofs are primary while only selected finite-horizon and architecture-specific results are formalized in a supplementary Lean 4/Mathlib project mapped to manuscript claims in Appendix N.1; stochastic decoder bounds and PyTorch execution semantics remain unformalized, manuscript Lemma 11 bridges Lean directed-gap bounds to principal angles, and the AI use statement notes LLMs assisted in checking the Lean formalization, with no blueprint-sync or spec-lock tooling mentioned and no public repo URL provided.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2605.12537](https://arxiv.org/abs/2605.12537) — Biprofile Deviation Logic: Report-Replacement Frames and Audit Witnesses
- **Primary / Target Cats:** `cs.LO` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `unclear` ([])
- **Evidence:** Section 7.3 and the DevNCore.lean header describe the Lean file as a small, deliberately narrower companion formalizing two-agent finite relational lemmas and update-safety factor closure rather than the paper's main Hilbert system, Lindenbaum construction, or completeness theorem; no blueprint or spec-lock tooling is present.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `arxiv-anc/2605.12537` (arxiv_ancillary):** `.lean` files=1, LoC=129, theorems=5, defs=9, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2605.01140](https://arxiv.org/abs/2605.01140) — SoCal: A Language for Memory-Layout Factorization of Recursive Datatypes
- **Primary / Target Cats:** `cs.PL` / ['cs.PF'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** Paper claims a Lean 4 + Mathlib mechanization of Section 3 progress, preservation, and type-safety for SoCal in supplementary material (with AI assistance writing the Lean 4 mechanization and auxiliary proofs), but provides no public Lean repository (the sole URL m-a-d-n-e-s-s/madness has 0 .lean files) and no blueprint/spec-lock or authoring-order details.
- **Risk flags:** ['Mode12_ProcessOpacity', 'OpFV_RefinementGap']

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {}
- **Tool categories (contributed):** {}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Alloy` | 1 |

### Confirmed Beyond-Lean Papers
