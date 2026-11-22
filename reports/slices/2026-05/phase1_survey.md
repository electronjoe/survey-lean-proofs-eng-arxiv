# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2026-05-01` to `2026-05-19` (3 weeks)
- **Target categories (8):** `cs.CR`, `cs.DC`, `cs.IT`, `cs.NI`, `cs.RO`, `eess.SP`, `eess.SY`, `math.OC`
- **Corpus size:** 3298 unique papers (3288 full-text screened, 99.70% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 3280 unique papers
- **Confirmed papers contributing Lean proofs (all):** **7** (0.21% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **5** (0.15% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **4** (0.12% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **0**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CR` | 685 | 3 | 0.44% | 2 |
| `cs.DC` | 315 | 2 | 0.63% | 0 |
| `cs.IT` | 327 | 0 | 0.00% | 0 |
| `cs.NI` | 227 | 0 | 0.00% | 0 |
| `cs.RO` | 740 | 0 | 0.00% | 0 |
| `eess.SP` | 419 | 1 | 0.24% | 1 |
| `eess.SY` | 456 | 1 | 0.22% | 1 |
| `math.OC` | 512 | 1 | 0.20% | 1 |
| **Deduplicated Union** | **3298** | **7** | **0.21%** | **4** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_citation_or_discussion` | 11 |
| `lean_contributed` | 7 |
| `false_positive` | 1 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 5 |
| `P2_lean_first` | 1 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 0 |
| `P0_opaque_or_unspecified` | 1 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'software_or_system_fv': 2, 'engineering_math_proof': 4, 'pure_tcs_or_math': 1}
- **Observed Verification Tiers:** {'Tier3_Gold': 2, 'Tier2_Silver': 2, 'Tier1_Bronze': 3}
- **Artifact Availability:** {'public_lean_repo': 5, 'appendix_only': 1, 'none': 1}
- **AI/Agent Assistance Disclosed:** {'explicitly_yes': 3, 'explicitly_no': 1, 'unclear': 3}
- **Target Categories (Lean Contributed):** {'cs.DC': 2, 'eess.SP': 1, 'cs.CR': 3, 'math.OC': 1, 'eess.SY': 1}
- **Static Risk Flags (`proof-methods.md`):** {'Mode2_ScopeDowngrade': 4, 'Mode12_ProcessOpacity': 3, 'Mode10_ProofBloat': 2, 'Mode3_CustomDefs': 1, 'Mode6_SorryOrAxiomOrNativeDecide': 1}

## 4. Detailed Inventory of Confirmed Lean Papers (7)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2605.19531](https://arxiv.org/abs/2605.19531) | `cs.DC` | `cs.DC` | `software_or_system_fv` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode3_CustomDefs, Mode10_ProofBloat | **Conflict-Freedom as a Progress Condition** — Formalizes all numbered results of a PODC'26 distributed computing paper on conflict-freedom and universal constructions in 34k LoC of Lean 4 (std-only, Claude Opus 5.5-assisted) with exhaustive axiom/import auditing and zero sorry/custom axioms. |
| [2605.14610](https://arxiv.org/abs/2605.14610) | `stat.ME` | `eess.SP` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_no` | Mode2_ScopeDowngrade | **Parametrically Adaptive Transition Polynomial: a Signed-Parity Continu** — Statistical/signal-processing paper introducing the PATP fractional-power basis with a small, zero-sorry public Lean 4 + Mathlib v4.26.0 supplement verifying only the algebraic boundary cases, degeneracy identities, entropy constants, and algebraic step of g_2(alpha). |
| [2605.16407](https://arxiv.org/abs/2605.16407) | `cs.LO` | `cs.CR` | `software_or_system_fv` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide | **Proof-Carrying Certificates for LLM Pipelines: A Trust-Boundary Archit** — Lean 4 reference artifact (25 files, ~2.4k LoC) formalizing 22 LLM trust-boundary certificate types and theorems with #print axioms audit (0 sorry/native_decide), downgraded scope (ℚ/2-layer), and 18 declared custom axioms for ML oracles and math placeholders. |
| [2605.09552](https://arxiv.org/abs/2605.09552) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode10_ProofBloat, Mode12_ProcessOpacity | **Phases of Muon: When Muon Eclipses SignSGD** — Formalizes 345 theorems and supporting lemmas for high-dimensional stochastic Muon vs SignSGD dynamics and phase diagrams in Lean 4 (340k+ LoC plus 14.5k LoC in alea-foundations) after freezing the audited LaTeX appendix. |
| [2605.05801](https://arxiv.org/abs/2605.05801) | `cs.LO` | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `appendix_only` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Self-Correcting Gossip Protocols** — Paper-first dynamic epistemic logic study of self-correcting gossip protocols (cs.LO/cs.DC) with an appendix Lean/Mathlib formalization (citing Aristotle) of its semantics and knowledge/belief properties, and no public Lean repository extracted. |
| [2605.03034](https://arxiv.org/abs/2605.03034) | `cs.AI` | `cs.CR,eess.SY` | `engineering_math_proof` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `unclear` | Mode12_ProcessOpacity | **Stable Agentic Control: Tool-Mediated LLM Architecture for Autonomous ** — Contributes a Lean 4/Mathlib formalization of closed-loop Lyapunov stability (controllability, ISS, observability) for a tool-mediated LLM cyber-defense control model, but provides no public Lean repository (only Appendix A proof sketches and a file table for an unlinked supplementary bundle). |
| [2605.02856](https://arxiv.org/abs/2605.02856) | `cs.CR` | `cs.CR` | `engineering_math_proof` | `P2_lean_first` (medium) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **The 1-Bit Barrier is Universal: k-Stage Pipeline Composition and Unifi** — Formalizes k-stage PF-PINI pipeline composition, a two-branch Montgomery reduction PF-PINI(2) bound, and an end-to-end 2*q^(2k-2) output-preimage cardinality bound over ZMod q in Lean 4 without sorry or custom axioms. |

### Evidence Notes per Confirmed Lean Paper

#### [2605.19531](https://arxiv.org/abs/2605.19531) — Conflict-Freedom as a Progress Condition
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Opus 5.5'])
- **Evidence:** The paper presents the distributed computing theory and proofs informally first (24-page PODC'26 extended version) and cites the Lean 4 formalization (Toyos-Marfurt, 2026) as Claude Opus 5.5-assisted supplementary material; the Zenodo repo maps every numbered result from main.tex into Paper.lean and STATUS.md post-hoc with no leanblueprint/LeanArchitect sync or spec-lock Challenge/Solution setup.
- **Risk flags:** ['Mode3_CustomDefs', 'Mode10_ProofBloat']
- **Repo `zenodo/23098310` (zenodo):** `.lean` files=101, LoC=34257, theorems=2061, defs=761, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.0`, ci=`[]`

#### [2605.14610](https://arxiv.org/abs/2605.14610) — Parametrically Adaptive Transition Polynomial: a Signed-Parity Continuous-alpha Extension of Kunchenko Stochastic Polynomials
- **Primary / Target Cats:** `stat.ME` / ['eess.SP'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_no` (['Claude Code'])
- **Evidence:** Lean files (PATP/Param.lean, PATP/Basis.lean, PATP/G2Algebra.lean) explicitly cross-reference manuscript sections (e.g., §3.2, §3.3, §4.2), README states the supplement repo is intentionally separate from the manuscript repo, and there is no blueprint sync (leanblueprint/LeanArchitect/Verso) or Challenge/Solution spec-lock.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `SZabolotnii/Ku-PATP-code-supplement` (github):** `.lean` files=8, LoC=473, theorems=25, defs=11, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.26.0`, ci=`[]`

#### [2605.16407](https://arxiv.org/abs/2605.16407) — Proof-Carrying Certificates for LLM Pipelines: A Trust-Boundary Architecture
- **Primary / Target Cats:** `cs.LO` / ['cs.CR'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` ([])
- **Evidence:** The GitHub/Zenodo artifact explicitly describes lean_artifact/ as a 'Companion reference implementation for the paper' compiling 22 certificate types 'from the paper', cites paper theorem/section numbers (e.g., Theorem 5.4, Theorem 25.1) with simplified formalizations (rational squared form instead of real sqrt, two-layer instead of n-layer composition, and AssuranceCard.lean noted as specified rather than compiled), uses a single commit right before arXiv submission, and has no blueprint sync or spec-lock tooling.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `zenodo/20144139` (zenodo):** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Repo `zenodo/20144140` (zenodo):** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Repo `gkoomullil/proof-carrying-certificates` (github):** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`

#### [2605.09552](https://arxiv.org/abs/2605.09552) — Phases of Muon: When Muon Eclipses SignSGD
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` ([])
- **Evidence:** The paper states that 'The resulting appendix was audited for style and correctness. Its statements and proofs were then formalized in Lean 4 with Mathlib and checked by machine, using standard results proved in the accompanying foundations library.' Consistently, lean/README.md states it 'Formalizes the appendix of Phases of Muon from the frozen camera-ready snapshot cr-2026-10-22' using a coverage.json manifest and Audit.lean/verify.py without leanblueprint, LeanArchitect, or Verso blueprint tooling.
- **Risk flags:** ['Mode10_ProofBloat', 'Mode12_ProcessOpacity']
- **Repo `mlexpos/alea-foundations` (github):** `.lean` files=30, LoC=14553, theorems=647, defs=53, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
- **Repo `mlexpos/phases-of-muon` (github):** `.lean` files=148, LoC=340325, theorems=12371, defs=1348, sorry=1, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2605.05801](https://arxiv.org/abs/2605.05801) — Self-Correcting Gossip Protocols
- **Primary / Target Cats:** `cs.LO` / ['cs.DC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Aristotle'])
- **Evidence:** Dedicated 'Appendix: formalizing self-correcting gossip in Lean' states the authors 'formalized the semantics for self-correcting gossip described in this paper using Lean and its mathematical library mathlib [21]', showing inline Lean lemmas (e.g., Corollary 14 knowledge_is_justified_true_belief) and a Figure 2 overview; LaTeX has 20 lean_macro hits and cites Aristotle [1] in the Lean appendix, with no LeanArchitect/leanblueprint/Verso or comparator/spec-lock signals and no repo URLs.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2605.03034](https://arxiv.org/abs/2605.03034) — Stable Agentic Control: Tool-Mediated LLM Architecture for Autonomous Cyber Defense
- **Primary / Target Cats:** `cs.AI` / ['cs.CR', 'eess.SY'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` ([])
- **Evidence:** Section 4 and Appendix A claim the 5-file Lean 4.30.0-rc1 + Mathlib project (ClosedLoopStability, zero sorry) is in supplementary materials, with only proof sketches and Table A2 in Appendix A; no public Lean repo URL exists (listed URLs are GOAD and EDR-Telemetry) and no authoring-order, blueprint, or spec-lock details are given. Note: Claude Sonnet 4 / Haiku 4.5 are evaluated as the cyber-defense controllers, not reported as Lean proof-authoring tools.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2605.02856](https://arxiv.org/abs/2605.02856) — The 1-Bit Barrier is Universal: k-Stage Pipeline Composition and Unified Leakage Bounds for Standard Modular Reductions in PQC Hardware
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P2_lean_first` (`medium`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude Opus 4.7'])
- **Evidence:** Public Lean 4 + Mathlib repo (rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856) with zero sorry/admit/axiom/native_decide, no blueprint sync or comparator spec-lock, and phase/audit comments (Basic.lean, KStageComposition.lean Phases 0-4, 'pre-draft audit', and reproduce.py matching declarations to 'source.md Table 3') indicating the Lean suite was developed before drafting the manuscript against it. Repo git commit history includes 'Co-Authored-By: Claude Opus 4.7 (1M context)', while reproduce.py lacks #print axioms, leanchecker, or CI workflows and relies on 4 local sibling repos.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `zenodo/19689480` (zenodo):** `.lean` files=8, LoC=451, theorems=16, defs=8, sorry=0, axiom=0, native_decide=1, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`
- **Repo `zenodo/19705450` (zenodo):** `.lean` files=5, LoC=494, theorems=11, defs=19, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`
- **Repo `rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856` (github):** `.lean` files=7, LoC=749, theorems=17, defs=4, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {}
- **Tool categories (contributed):** {}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Verus` | 1 |
| `coq_rocq` | 1 |

### Confirmed Beyond-Lean Papers
