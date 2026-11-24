# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2026-11-01` to `2026-11-19` (3 weeks)
- **Target categories (7):** `cs.CE`, `cs.GT`, `cs.PF`, `eess.AS`, `eess.IV`, `math.DS`, `physics.flu-dyn`
- **Corpus size:** 1339 unique papers (1336 full-text screened, 99.78% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 1321 unique papers
- **Confirmed papers contributing Lean proofs (all):** **32** (2.39% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **27** (2.04% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **7** (0.52% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **0**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CE` | 146 | 0 | 0.00% | 0 |
| `cs.GT` | 166 | 15 | 9.04% | 4 |
| `cs.PF` | 94 | 0 | 0.00% | 0 |
| `eess.AS` | 134 | 0 | 0.00% | 0 |
| `eess.IV` | 175 | 0 | 0.00% | 0 |
| `math.DS` | 360 | 15 | 4.17% | 2 |
| `physics.flu-dyn` | 278 | 2 | 0.72% | 1 |
| **Deduplicated Union** | **1339** | **32** | **2.39%** | **7** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_contributed` | 32 |
| `lean_citation_or_discussion` | 4 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 22 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 1 |
| `P4_speclock_solve_distill` | 4 |
| `P0_opaque_or_unspecified` | 5 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'pure_tcs_or_math': 25, 'engineering_math_proof': 7}
- **Observed Verification Tiers:** {'Tier3_Gold': 19, 'Tier1_Bronze': 10, 'Tier2_Silver': 3}
- **Artifact Availability:** {'public_lean_repo': 25, 'none': 4, 'broken_or_missing_repo': 3}
- **AI/Agent Assistance Disclosed:** {'explicitly_yes': 26, 'unclear': 6}
- **Target Categories (Lean Contributed):** {'cs.GT': 15, 'math.DS': 15, 'physics.flu-dyn': 2}
- **Static Risk Flags (`proof-methods.md`):** {'Mode10_ProofBloat': 14, 'Mode2_ScopeDowngrade': 13, 'Mode12_ProcessOpacity': 8, 'Mode6_SorryOrAxiomOrNativeDecide': 4, 'Mode7_MetaprogOrUnsafe': 2}

## 4. Detailed Inventory of Confirmed Lean Papers (32)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2611.24920](https://arxiv.org/abs/2611.24920) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **The Optimal Competitive Ratio for Subadditive Online Combinatorial Auc** — Formalizes in Lean 4 (+Mathlib) a sequence of finite subadditive online combinatorial auctions whose optimal online-to-prophet competitive ratio limsup is strictly below 4/9 - 1/4300 (< 1/2), with CI-checked kernel axiom audit and zero proof escapes. |
| [2611.24787](https://arxiv.org/abs/2611.24787) | `math.OA` | `math.DS` | `pure_tcs_or_math` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **A Poisson boundary solution to Connes' bicentralizer conjecture and Ka** — Pure operator-algebras paper (Connes' bicentralizer conjecture and Kadison's MASA problem) claiming Lean formalization of a subset of results (main line of Theorem A) without a public Lean repository. |
| [2611.22216](https://arxiv.org/abs/2611.22216) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `broken_or_missing_repo` | `unclear` | Mode12_ProcessOpacity | **Settling the Time and Structural Complexity of Bertrand Networks** — Proves PPAD-completeness, an EPTAS, and tight Theta(2^n) structural complexity for Bertrand networks (cs.GT); claims a Lean formalization via a GitHub link whose repository has 0 .lean files, no lakefile/toolchain, and no workflow details. |
| [2611.20966](https://arxiv.org/abs/2611.20966) | `math.DS` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `broken_or_missing_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **Finite-order exponential mixing does not imply the central limit theor** — Pure dynamical systems (math.DS) paper claiming Lean 4.35.0/Mathlib formalization (with ChatGPT 6.0 Astra assistance and an Audit.lean check) of counterexample theorems on finite-order exponential mixing vs. CLT, though the linked GitHub repo is inaccessible. |
| [2611.20890](https://arxiv.org/abs/2611.20890) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Nearly Settling the Complexity of Connected $\varepsilon$-Envy-Free Ca** — Formalizes the main query-complexity theorems and circuit-model PPAD/UEOPL computational reductions for connected epsilon-envy-free cake cutting in Lean 4 + Mathlib (~387k LoC, zero sorry/custom axioms, leanchecker replay and axiom audit), leaving general TM evaluation programs and randomized bounds informal. |
| [2611.19243](https://arxiv.org/abs/2611.19243) | `math.DS` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Veech dichotomy for specific covering surface over Veech surface** — Pure mathematics (math.DS) paper formalizing its main Veech dichotomy theorem for finite translation covers in Lean 4.35.0/Mathlib with transitive axiom and statement audits (no sorry/custom axioms), developed with ChatGPT/Codex assistance. |
| [2611.17292](https://arxiv.org/abs/2611.17292) | `cs.DS` | `cs.GT` | `pure_tcs_or_math` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode6_SorryOrAxiomOrNativeDecide, Mode12_ProcessOpacity | **The Submodular Secretary Problem: Tight $1-1/e$ for Monotone Objective** — Theoretical CS paper on the submodular secretary problem claiming an AI-written (GPT-6 Astra) Lean 4 formalization of all results using native_decide for finite numerical certificates, with no public repository. |
| [2611.17277](https://arxiv.org/abs/2611.17277) | `math.DS` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **On $L^p$ density of self-similar measures and Bernoulli convolutions** — Pure math (math.DS) paper on Lp densities of self-similar measures and continuous densities of Bernoulli convolutions, whose main theorems are post-hoc formalized in Lean 4 (47.8k LoC, zero sorry/custom axioms in Solution) by GPT-6 Astra / Codex with comparator and multi-kernel (Lean/NanoDa/con-ron) audit. |
| [2611.17223](https://arxiv.org/abs/2611.17223) | `cs.DS` | `cs.GT` | `pure_tcs_or_math` | `P4_speclock_solve_distill` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Combinatorial Bernoulli Factories with Polynomially Many Coins** — Formalizes the main exact-rounding and polynomial coin-flip/oracle-query complexity theorems for combinatorial Bernoulli factories (Interior, Universal, Birkhoff, Amplify) in Lean 4 via an automated spec-locked Codex/comparator pipeline, omitting bit-complexity/runtime and LP/GLS preprocessing. |
| [2611.16763](https://arxiv.org/abs/2611.16763) | `math.AG` | `math.DS` | `pure_tcs_or_math` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Composition loci, invariant Bezoutians, and finite-orbit correspondenc** — Pure algebraic geometry and dynamical systems paper on composition loci, Bezoutians, and finite-orbit correspondences that mentions AI-assisted partial Lean formalizations with no public repository or workflow details. |
| [2611.15751](https://arxiv.org/abs/2611.15751) | `math.CO` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode7_MetaprogOrUnsafe, Mode10_ProofBloat | **Shift-Symmetric Configurations in $d$-Dimensional Cellular Automata: E** — Lean 4 + Mathlib formalization of all numbered theorems, bounds, irreversibility, and detection results for shift-symmetric configurations in d-dimensional cellular automata, verified to Tier3_Gold via 370 SHA-256-frozen Props, build-failing axiom audits, kernel replay, and a hand PDF-to-Lean correspondence audit. |
| [2611.15711](https://arxiv.org/abs/2611.15711) | `cs.DS` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide | **Beyond Worst-Case Online Algorithms via Input Subsampling** — ITCS 2027 cs.DS/cs.GT paper on competitive ratios under input subsampling that provides a post-hoc Lean 4 + Mathlib companion repo verifying Section 4 ski-rental analytic series bounds and rational certificates using native_decide. |
| [2611.14756](https://arxiv.org/abs/2611.14756) | `math.DS` | `math.DS` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | none | **Stability of equilibria in discrete-time modified-gradient systems and** — Post-hoc Lean 4 + Mathlib formalization of the main discrete-time modified-gradient stability and basin-of-attraction theorems (Lemma 4.1, Theorem 5.1, Corollary 5.2, Theorem 6.1) with CI-verified standard-axiom audit. |
| [2611.14586](https://arxiv.org/abs/2611.14586) | `stat.ML` | `cs.GT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Finite-Cadence Refresh Equilibria for Streaming Prior-Anchored Ridge: ** — Proposes SPAR, a streaming prior-anchored ridge regression algorithm, and formalizes its deterministic algebraic core, refresh chain, OGD/Hedge regret bounds, and coupled contraction in Lean 4 (85 proved declarations, 0 sorry, Mathlib-backed, probability/RMT convergence left on paper). |
| [2611.12862](https://arxiv.org/abs/2611.12862) | `math.AP` | `physics.flu-dyn` | `pure_tcs_or_math` | `P4_speclock_solve_distill` (medium) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode10_ProofBloat | **Quantitative global regularity for Navier--Stokes equations with odd v** — Formalizes all three main global regularity theorems for 3D incompressible Navier-Stokes with odd viscosity on the cubic torus in a 207k-LoC Lean 4 / Mathlib repository using a challenge/solution spec-lock verified by lake comparator and leanchecker with only standard axioms. |
| [2611.11805](https://arxiv.org/abs/2611.11805) | `math.NA` | `math.DS` | `engineering_math_proof` | `P4_speclock_solve_distill` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Operator Learning of Microstructure-Dependent Internal-Variable Models** — Formalizes in Lean 4 (v4.35.0, Mathlib, LeanCert) the homogenization, spectral memory representation, universal approximation, and internal-variable dimension bounds for viscoelastic operator learning using Codex GPT-6 Astra and 331 multi-kernel Lean Comparator checks. |
| [2611.11641](https://arxiv.org/abs/2611.11641) | `cs.LO` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Spectral Stability, Fatou Basin Contraction, and Machine-Checked Multi** — Pure math paper on holomorphic extensions of the Syracuse/Collatz map with a post-hoc standalone Lean 4 script (0 sorry) verifying 20 rational algebraic/arithmetic identities (downgraded from full complex-analytic and 2-adic ergodic claims) and no lakefile or lean-toolchain. |
| [2611.11424](https://arxiv.org/abs/2611.11424) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **The Query Complexity of Envy-Free Division: Cake, Chores, and Mixed Re** — Formalizes in Lean 4.35.0 (1,391 audited modules, ~127.7k LoC, zero sorry/axioms) all four main Robertson-Webb query-complexity theorems for envy-free cake, chore, and mixed-resource division, with Codex/Astra AI assistance. |
| [2611.09615](https://arxiv.org/abs/2611.09615) | `cs.GT` | `cs.GT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **Contextual Search and Bilateral Trade with a Trace-Square-Root Potenti** — Full Lean 4 + Mathlib formalization (21 files, ~15k LoC, zero sorry/axiom, 34-#print-axioms Audit.lean) of all 22 statements and 4 online algorithms for O(sqrt(d)) contextual search and bilateral trade regret bounds. |
| [2611.09066](https://arxiv.org/abs/2611.09066) | `math.DS` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Hausdorff dimension of planar box-like self-affine sets with rotations** — Pure math (math.DS) paper proving Hausdorff and pointwise dimension formulas for planar box-like self-affine sets with rotations, accompanied by a 135k-LoC Claude-assisted Lean 4/Mathlib formalization (42/44 statements, all 3 headline theorems) audited with Comparator, NanoDa, con-ron, and Palomar preflight. |
| [2611.08591](https://arxiv.org/abs/2611.08591) | `math-ph` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | none | **Conley index theory for asymptotically autonomous systems and UV-to-IR** — Formalizes Conley index theory for asymptotically autonomous systems, UV-to-IR transport maps, and applications to Gubser, Bjorken, and O(N) flows in Lean 4/Mathlib (38.8k LoC, zero sorry/axioms) with Claude and GPT-5.6 Sol assistance. |
| [2611.07818](https://arxiv.org/abs/2611.07818) | `math.DS` | `math.DS` | `pure_tcs_or_math` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `unclear` | Mode12_ProcessOpacity | **Thurston algorithm for real entire maps: existence and uniqueness** — Pure math (math.DS) paper on Thurston's pullback algorithm for real entire maps whose V1 results were reportedly formalized in Lean 4 conditional on 25 classical statements, with no public repository. |
| [2611.07494](https://arxiv.org/abs/2611.07494) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Transparency in Team Contracts** — Post-hoc AI-assisted Lean 4 formalization (Tier3_Gold with --trust=0 and #print axioms audit) of the main information-theoretic 4/3, 9/8, and N-approximation theorems in cs.GT team contract design, excluding the paper's computational Theorem 4.4. |
| [2611.07395](https://arxiv.org/abs/2611.07395) | `math.AP` | `physics.flu-dyn` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide | **Rigorously Certified Neural-Network Computation of Nonlinear Water Wav** — Formalizes analytic residual, Hilbert-aliasing, and Taylor grid-to-continuum bounds in Lean 4 (WaveCAP) for a PINN-discovered gravity-capillary water-wave candidate, importing two Julia/Arb numerical bounds as explicit axioms without end-to-end Lean interval replay. |
| [2611.06896](https://arxiv.org/abs/2611.06896) | `cs.DS` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide, Mode7_MetaprogOrUnsafe, Mode10_ProofBloat | **Online Edge-Weighted Matching Beyond 0.55** — Formalizes the 0.556195 competitive guarantee for edge-weighted online bipartite matching with free disposal in Lean 4.19.0 (aided by OpenAI Astra and ~28.67M LoC of generated certificate proofs), conditioned on two explicit custom literature axioms and excluding running-time/tightness proofs. |
| [2611.06106](https://arxiv.org/abs/2611.06106) | `math.AG` | `math.DS` | `pure_tcs_or_math` | `P3_blueprint_sync` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **PCF All The Way Down** — AI-assisted Lean 4 + Mathlib formalization of the characteristic-zero algebraic dynamics theorem that post-critically finite self-maps remain PCF on preperiodic divisors all the way down, audited via leanblueprint and Palomar/Comparator. |
| [2611.05243](https://arxiv.org/abs/2611.05243) | `cs.LG` | `cs.GT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **Logarithmic Regret for Alternating Mirror Descent** — Proves an O(log T) regret bound for Alternating Online Mirror Descent in two-player zero-sum bilinear games and formalizes all 15 named manuscript results in a zero-sorry, axiom-audited Lean 4 repository (AltOMD-Lean) developed with GPT-5.6 Sol and GPT-6 Astra. |
| [2611.05221](https://arxiv.org/abs/2611.05221) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Efficient Equilibrium Computation in Colonel Blotto Games** — Post-hoc ChatGPT-generated Lean 4 formalization of all 18 named theorems for a cs.GT FPTAS and linear-time exact equilibrium paper on continuous Colonel Blotto games, audited with LeanEnvironmentAudit and leanchecker endpoint replay across ~585k LoC with an open cost-correspondence gap. |
| [2611.04934](https://arxiv.org/abs/2611.04934) | `cs.GT` | `cs.GT` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **The Complexity of Continuous Contract Design over Polymatroids** — Formalizes the mathematical core and operation/oracle counts of 81 results (76 full, 5 partial) on continuous contract design over polymatroids in a 53.6k-LoC sorry-free Lean 4/Mathlib repo with an explicit COVERAGE.md audit manifest and Claude assistance. |
| [2611.04575](https://arxiv.org/abs/2611.04575) | `math.CO` | `math.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **Polynomial configurations and pointwise averages along Piatetski--Shap** — Pure math (math.CO/math.DS) paper with a ChatGPT-generated public Lean 4 + Mathlib formalization (52 modules, 0 sorry/axiom/native_decide, 508-declaration #print axioms audit, and leanblueprint check) verifying all deductions for polynomial configurations and pointwise averages along Piatetski-Shapiro primes conditional on eight explicit external analytic/arithmetic input interfaces. |
| [2611.04545](https://arxiv.org/abs/2611.04545) | `cs.GT` | `cs.GT` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `broken_or_missing_repo` | `unclear` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Coercive at the equilibrium, monotone nowhere: exact convergence certi** — Proves local convergence certificates for learning in first-price auctions, with finite-algebra identities and leading-order inequalities checked in Lean 4/Mathlib (6,315 lines across 27 files), though the cited GitHub repo is inaccessible. |
| [2611.02465](https://arxiv.org/abs/2611.02465) | `math.CA` | `math.DS` | `pure_tcs_or_math` | `P4_speclock_solve_distill` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Pointwise Ergodic Theorems Along $\lfloor p^c\rfloor$ for Every $c>1$** — Lean 4 + Mathlib formalization (via Palomar Challenge/Solution spec-lock, Codex/Astra agent assistance, #print axioms, and Comparator multi-kernel audit) of pointwise ergodic theorems, variational estimates, and Möbius decay along ⌊p^c⌋. |

### Evidence Notes per Confirmed Lean Paper

#### [2611.24920](https://arxiv.org/abs/2611.24920) — The Optimal Competitive Ratio for Subadditive Online Combinatorial Auctions is Less Than 1/2
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['GPT-5', 'GPT-6'])
- **Evidence:** Single-commit repo (GO-EPFL/subadditive-online-combinatorial-auctions) with no blueprint or Challenge/Solution spec-lock; README, docs/Formalization.md, and docs/NumericalVerification.md explicitly state the Lean formalization and interval certificates were reconstructed from the accompanying manuscript.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `GO-EPFL/subadditive-online-combinatorial-auctions` (github):** `.lean` files=176, LoC=31393, theorems=2770, defs=1524, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.2`, ci=`[]`

#### [2611.24787](https://arxiv.org/abs/2611.24787) — A Poisson boundary solution to Connes' bicentralizer conjecture and Kadison's problem on MASA
- **Primary / Target Cats:** `math.OA` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['GPT-6 Astra', 'Gemini', 'harmonic'])
- **Evidence:** The paper notes only that 'Lean was also used to check a formalization of a short note consisting of the preliminaries in Subsection 2.2, Example 3.9, Theorem 4.1, and the whole of Section 5. These components form the main line of the proof of Theorem A,' with no public Lean repository (repos=[], local_repo_dirs=[]) and no further workflow detail.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2611.22216](https://arxiv.org/abs/2611.22216) — Settling the Time and Structural Complexity of Bertrand Networks
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['OpenAI Astra', 'Gemini Argon'])
- **Evidence:** Paper only states 'Lean formalization can be found in link.' (pointing to hajiaghayi/Bertrand, pushed 2026-11-19) with no description of Lean authoring workflow; the GitHub repo has total_files=1 (2456 KB) with lean_file_count=0, has_lakefile=false, has_lean_toolchain=false, has_blueprint_dir=false, and workflow_files=[].
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.20966](https://arxiv.org/abs/2611.20966) — Finite-order exponential mixing does not imply the central limit theorem for unique equilibrium states
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['OpenAI ChatGPT 6.0 (Astra)'])
- **Evidence:** 39-page math.DS paper with 32 theorem environments and a dedicated Section 9 ('Lean formalisation') stating that Theorems A, 7.3, 8.5, and Corollary 1.2 were formalised in Lean 4.35.0 using Mathlib (with AI assistance to develop and revise the Lean formalisation), with no mention of blueprint sync or spec-lock tooling; exact repo commit workflow is unobservable because the linked GitHub repo is inaccessible.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.20890](https://arxiv.org/abs/2611.20890) — Nearly Settling the Complexity of Connected $\varepsilon$-Envy-Free Cake Cutting
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude', 'Claude Code', 'OpenAI Codex'])
- **Evidence:** Manuscript proofs and LaTeX (v10-v27) were developed with Claude and Codex, and AI systems then formalized frozen manuscript targets in Lean 4 using custom TARGET_LOCK.json, CORRESPONDENCE.json, and an interactive inspector without leanblueprint/@[blueprint] or Challenge/Solution distillation.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `SimonWMackenzie/connected-envy-free-lean` (github):** `.lean` files=2774, LoC=387315, theorems=23623, defs=24491, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0`, ci=`[]`
- **Repo `harfe/fixed-point-theorems-lean4` (github):** `.lean` files=8, LoC=3071, theorems=82, defs=22, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.19243](https://arxiv.org/abs/2611.19243) — Veech dichotomy for specific covering surface over Veech surface
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT', 'Codex'])
- **Evidence:** The repository formalizes Theorem 1 of the pre-existing LaTeX paper (referenced by SHA-256 in PAPER-SOURCE-PROVENANCE.json), has no blueprint or Challenge/Solution files, and PROOF_NOTES.md notes that the Lean code adapts the paper's moduli/Hurwitz-space presentation into explicit families of curves and covers.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `Ryan-Hao-Jan/Veech-dichotomy-for-cover` (github):** `.lean` files=846, LoC=82993, theorems=4905, defs=1590, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.17292](https://arxiv.org/abs/2611.17292) — The Submodular Secretary Problem: Tight $1-1/e$ for Monotone Objectives, and Strictly Between $1/e$ and $1/2$ in General
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['GPT-6 Astra', 'Claude', 'Fable 5.2'])
- **Evidence:** Paper claims a Lean 4 formalization written by GPT-6 Astra proving every result (using native_decide for finite numerical certificates in appendices), while the manuscript was drafted with Claude and Fable 5.2, but provides no public repository URLs or Lean-LaTeX workflow/synchronization details.
- **Risk flags:** ['Mode6_SorryOrAxiomOrNativeDecide', 'Mode12_ProcessOpacity']

#### [2611.17277](https://arxiv.org/abs/2611.17277) — On $L^p$ density of self-similar measures and Bernoulli convolutions
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['GPT-6 Astra', 'OpenAI Codex'])
- **Evidence:** Human-authored mathematical paper ('The paper is written by the authors... GPT-6 Astra formalized all results from this paper') with post-hoc AI formalization (GPT-6 Astra / OpenAI Codex) packaged with Challenge.lean/Solution.lean and comparator/PalomarSubmission verification, without blueprint sync or paper distillation from Lean.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `ckkogler/lpselfsimilar-lean` (github):** `.lean` files=776, LoC=47794, theorems=2579, defs=312, sorry=5, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`['comparator', 'lake build']`

#### [2611.17223](https://arxiv.org/abs/2611.17223) — Combinatorial Bernoulli Factories with Polynomially Many Coins
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P4_speclock_solve_distill` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['OpenAI Codex', 'GPT-6 Astra', 'formalize-pdf', 'ChatGPT Astra', 'Claude Opus', 'Gemini Argon'])
- **Evidence:** Repo uses frozen Challenge.lean / Trusted.lean / SOURCE.md (freeze.json SHA-256), Solution.lean, and comparator.json (enable_nanoda: true), with README documenting the formalize-pdf pipeline where AI agents freeze the statement from the 21-page PDF before unconstrained Codex proof search and kernel/comparator verification.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `radniazadeh/bernoulli-poly` (github):** `.lean` files=56, LoC=10541, theorems=520, defs=168, sorry=4, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`

#### [2611.16763](https://arxiv.org/abs/2611.16763) — Composition loci, invariant Bezoutians, and finite-orbit correspondences
- **Primary / Target Cats:** `math.AG` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['ChatGPT', 'Codex', 'Claude'])
- **Evidence:** The paper discloses that GPT-based tools (ChatGPT and Codex) were used 'to assist with partial Lean formalizations,' while providing no public repository, URLs, or authoring workflow details.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2611.15751](https://arxiv.org/abs/2611.15751) — Shift-Symmetric Configurations in $d$-Dimensional Cellular Automata: Enumeration, Bounds, Irreversibility, and Detection
- **Primary / Target Cats:** `math.CO` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude', 'Codex'])
- **Evidence:** Paper v3.1 (shift_symmetry_d_dimensions.tex) was written informally first extending Banda et al. (2019), and the Lean 4 + Mathlib formalization was subsequently constructed against the paper text (S01-S11 cite v3.1 line numbers), using custom frozen Prop specs (SHA-256 fingerprinted via check_frozen.py), AuditPaper.lean, kernel_replay.lean, and a custom PDF-to-Lean correspondence audit viewer rather than LeanArchitect/leanblueprint (P3) or a pre-paper Challenge/Solution spec-lock (P4).
- **Risk flags:** ['Mode7_MetaprogOrUnsafe', 'Mode10_ProofBloat']
- **Repo `peterbanda/d-dim-shift-symmetry-in-ca` (github):** `.lean` files=109, LoC=28317, theorems=1481, defs=740, sorry=0, axiom=0, native_decide=0, unsafe=1, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.0-rc1`, ci=`[]`

#### [2611.15711](https://arxiv.org/abs/2611.15711) — Beyond Worst-Case Online Algorithms via Input Subsampling
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Codex'])
- **Evidence:** The paper develops the online-algorithm reductions and probabilistic definitions first and attaches a standalone Lean 4 + Mathlib companion repository (relyt871/BWCA-Online-Lean, documented in Appendix F) to verify analytic series properties and rational certificates for Section 4 lemmas without blueprint sync or Challenge/Solution spec-lock.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `relyt871/BWCA-Online-Lean` (github):** `.lean` files=13, LoC=5909, theorems=347, defs=158, sorry=0, axiom=0, native_decide=32, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.31.0`, ci=`[]`

#### [2611.14756](https://arxiv.org/abs/2611.14756) — Stability of equilibria in discrete-time modified-gradient systems and the multivariate breeder's equation
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` ([])
- **Evidence:** The repository contains no blueprint or spec-lock files (has_blueprint_dir=false, has_challenge_file=false, tex_file_count=0); README.md maps Lean theorems to arXiv v1 manuscript numbering and explicitly documents small differences between the Lean proofs and the already-written paper proofs.
- **Risk flags:** []
- **Repo `zenodo/24118844` (zenodo):** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `magbenji/discrete-modified-gradient-lean` (github):** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.14586](https://arxiv.org/abs/2611.14586) — Finite-Cadence Refresh Equilibria for Streaming Prior-Anchored Ridge: A Closed-Form Forgetting Window and Spectral Correction
- **Primary / Target Cats:** `stat.ML` / ['cs.GT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['GLM-5.3', 'DeepSeek V4.1 Flash'])
- **Evidence:** Appendix C provides a manual Result-to-declaration Map (Table 1) linking paper theorems/propositions to Lean 4 declarations in theory/lean/SparTheorems/, while Core.lean states it formalizes the algebraic core of the theory appendix; no blueprint-sync or spec-lock tooling is used.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `zenodo/23768172` (zenodo):** `.lean` files=7, LoC=1969, theorems=85, defs=11, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc4`, ci=`[]`

#### [2611.12862](https://arxiv.org/abs/2611.12862) — Quantitative global regularity for Navier--Stokes equations with odd viscosity on the cubic three-torus
- **Primary / Target Cats:** `math.AP` / ['physics.flu-dyn'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P4_speclock_solve_distill` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` (['Claude', 'GPT-6'])
- **Evidence:** Uses a frozen challenge.lean/solution.lean spec-lock verified via lake comparator (comparator.json and reports/comparator-2026-11-09.md) where the OddViscousNS library proves the locked theorems via alternative Lean proof routes rather than checking intermediate manuscript lemmas step-by-step, alongside mentions of AI tools (Claude, GPT-6) in the manuscript; however, some paper proof units/audits appear to have existed prior to Lean formalization.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `DavetheSlayer/OVNS-Lean` (github):** `.lean` files=3157, LoC=207152, theorems=35653, defs=10940, sorry=5, axiom=0, native_decide=0, unsafe=2, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.11805](https://arxiv.org/abs/2611.11805) — Operator Learning of Microstructure-Dependent Internal-Variable Models for Inelastic Homogenization: Approximation and Complexity
- **Primary / Target Cats:** `math.NA` / ['math.DS'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P4_speclock_solve_distill` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['OpenAI Codex GPT-6 Astra', 'OpenAI GPT-6.1 Sol'])
- **Evidence:** Paper states OpenAI Codex GPT-6 Astra formalized the theoretical results in Lean 4.35.0 and Lean Comparator verified proofs against separately specified theorem statements; repo has lean/Comparator/Challenges with 331 Comparator configs, CI comparator workflows, and MainResults.lean / READER_GUIDE.md / formalization.yaml aligning all 17 numbered statements to the manuscript.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `sgstepaniants/inelastic_hom_learn` (github):** `.lean` files=753, LoC=55284, theorems=2385, defs=477, sorry=702, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['comparator']`

#### [2611.11641](https://arxiv.org/abs/2611.11641) — Spectral Stability, Fatou Basin Contraction, and Machine-Checked Multipliers in Holomorphic Extensions of Generalized Syracuse Dynamics
- **Primary / Target Cats:** `cs.LO` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `unclear` ([])
- **Evidence:** Paper and companion Zenodo monograph develop complex-dynamic and 2-adic ergodic proofs informally first, with a standalone post-hoc Lean 4 file (anc/CollatzAttractor.lean, 215 lines, 20 theorems over ℚ using ring/norm_num) checking algebraic/arithmetic sub-identities listed in Section 7 Table 3, without leanblueprint, @[blueprint], Challenge/Solution spec-lock, or lakefile/lean-toolchain.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `arxiv-anc/2611.11641` (arxiv_ancillary):** `.lean` files=1, LoC=174, theorems=20, defs=10, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
- **Repo `zenodo/24060393` (zenodo):** `.lean` files=1, LoC=174, theorems=20, defs=10, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
- **Repo `zenodo/24060394` (zenodo):** `.lean` files=1, LoC=174, theorems=20, defs=10, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.11424](https://arxiv.org/abs/2611.11424) — The Query Complexity of Envy-Free Division: Cake, Chores, and Mixed Resources
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['OpenAI Codex', 'Astra', 'Fable 5.2'])
- **Evidence:** Separately maintained 61-page LaTeX manuscript mapped post-hoc/independently to Lean endpoints via JSON manifests (verification/coverage.json, verification/main_results.json) and scoped correspondence reviews; no leanblueprint, LeanArchitect, or Challenge/Solution spec-lock tooling.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `farhadi94/envy-free-division` (github):** `.lean` files=1402, LoC=127681, theorems=7189, defs=2857, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.09615](https://arxiv.org/abs/2611.09615) — Contextual Search and Bilateral Trade with a Trace-Square-Root Potential
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Gemini', 'Claude', 'ChatGPT'])
- **Evidence:** Single-commit GitHub repository (renatoppl/trace-square-root, 14,953 LoC across 21 Lean files) maps all 22 numbered paper statements and Algorithms 1-4 post-hoc without leanblueprint/LeanArchitect/Verso or Challenge/Solution spec-lock, explicitly noting where Lean proof routes differ from the paper exposition.
- **Risk flags:** []
- **Repo `renatoppl/trace-square-root` (github):** `.lean` files=21, LoC=14953, theorems=87, defs=91, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.27.0`, ci=`[]`

#### [2611.09066](https://arxiv.org/abs/2611.09066) — Hausdorff dimension of planar box-like self-affine sets with rotations
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Code', 'Claude Opus 5.5 (Anthropic)'])
- **Evidence:** Paper and formalization.yaml state that authors developed the mathematical ideas/proofs and separately used Claude Code / Claude Opus 5.5 to formalize the results against the TeX manuscript (tracked via SHA-256 fingerprints in paper-correspondence.yaml), with docs/correspondence.md noting several informal-vs-Lean proof divergences (e.g., Sarig vs Bowen, Berry-Esseen vs Kittle-Kogler); Challenge.lean/Solution.lean/comparator are used as a Palomar audit harness rather than P4 paper distillation from Lean.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `sascha2718/lean-diagonal-antidiagonal` (github):** `.lean` files=865, LoC=134934, theorems=7468, defs=1253, sorry=3, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`['comparator', 'lake build']`

#### [2611.08591](https://arxiv.org/abs/2611.08591) — Conley index theory for asymptotically autonomous systems and UV-to-IR connections
- **Primary / Target Cats:** `math-ph` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude', 'GPT-5.6 Sol'])
- **Evidence:** Lean docstrings reference paper LaTeX labels (e.g., thm:slab, prop:palmer) and README maps paper sections/results and documented gaps to Lean declarations, with no blueprint directory or @[blueprint]/\inputleannode sync annotations in the repo (single squashed commit preceding arXiv submission).
- **Risk flags:** []
- **Repo `stacks-ai/papers` (github):** `.lean` files=135, LoC=38826, theorems=2779, defs=791, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc4`, ci=`[]`

#### [2611.07818](https://arxiv.org/abs/2611.07818) — Thurston algorithm for real entire maps: existence and uniqueness
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['harmonic'])
- **Evidence:** Acknowledgements state Bernat Bassols-Cornudella helped formalise the first ArXiv version in Lean 4 conditional on 25 classical statements, with a Formalisation Summary available only by email and no public repository or workflow/blueprint details (V2 adds a new appendix; latex_signals.agent_tools matched 'harmonic' alongside an 'AI output was not used as a mathematical source' note).
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.07494](https://arxiv.org/abs/2611.07494) — Transparency in Team Contracts
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude', 'Gemini', 'OpenAI Codex'])
- **Evidence:** PROVENANCE.md states the Lean repo was developed post-hoc against the manuscript snapshot transparency_paper.zip and mapped in THEOREMS.md, with no LeanArchitect/leanblueprint or Challenge/Solution spec-lock tooling.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `wuzhuangtai00/transparency-lean` (github):** `.lean` files=49, LoC=5340, theorems=383, defs=154, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`

#### [2611.07395](https://arxiv.org/abs/2611.07395) — Rigorously Certified Neural-Network Computation of Nonlinear Water Waves at Near-Machine Precision
- **Primary / Target Cats:** `math.AP` / ['physics.flu-dyn'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['unspecified LLM'])
- **Evidence:** Public WaveCAP Lean 4 repo (33 files, 12.3k LoC) has no leanblueprint/LeanArchitect/Verso blueprint or Challenge/Solution comparator spec-lock; dedicated publication modules (PaperCertificate.lean, PaperAudit.lean, HalfDCConvention.lean) reconcile Lean's residual sign and DC coefficient conventions post hoc with the manuscript and Julia/Arb pipeline.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `michalshavitNYU/Rigorously-certified-water-waves` (github):** `.lean` files=33, LoC=12309, theorems=211, defs=74, sorry=0, axiom=4, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0-rc6`, ci=`[]`

#### [2611.06896](https://arxiv.org/abs/2611.06896) — Online Edge-Weighted Matching Beyond 0.55
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['OpenAI Astra'])
- **Evidence:** Public Lean 4.19.0 repo (4,860 files, ~28.67M LoC) accompanies the separately distributed paper without leanblueprint/LeanArchitect sync or Challenge/Solution spec-lock; Python generators produce large tournament certificates checked by Lean, while running-time, tightness, and optimization characterizations remain informal in the manuscript.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide', 'Mode7_MetaprogOrUnsafe', 'Mode10_ProofBloat']
- **Repo `farhadi94/online-edge-weighted-matching` (github):** `.lean` files=4860, LoC=28670443, theorems=63271, defs=138099, sorry=0, axiom=2, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`

#### [2611.06106](https://arxiv.org/abs/2611.06106) — PCF All The Way Down
- **Primary / Target Cats:** `math.AG` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P3_blueprint_sync` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Code', 'Codex', 'GPT-6', 'GPT-5'])
- **Evidence:** Paper started conventionally and was completed with AI; repo pairs a leanblueprint claim graph (char-zero/blueprint/src/content.tex with \lean{...}/\leanok and lean-status.json linking 32 nodes) with Palomar Challenge/Solution comparator packaging (comparator.json) built over the main library.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `tdupu/pcfawd-formalization` (github):** `.lean` files=1053, LoC=202819, theorems=7723, defs=2710, sorry=14, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['comparator']`

#### [2611.05243](https://arxiv.org/abs/2611.05243) — Logarithmic Regret for Alternating Mirror Descent
- **Primary / Target Cats:** `cs.LG` / ['cs.GT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['GPT-5.6 Sol', 'GPT-6 Astra'])
- **Evidence:** The paper explicitly states that the mathematical proof was developed using GPT-5.6 Sol and the Lean proof was formalized using GPT-6 Astra, with authors verifying proofs and revising the manuscript. The public repo contains no blueprint sync or Challenge/Solution spec-lock tooling, and uses post-hoc correspondence/audit documentation (CORRESPONDENCE.md and AltOMDAudit/README.md) mapping all 15 manuscript labels to Lean declarations.
- **Risk flags:** []
- **Repo `CoffeeAndConvexity/AltOMD-Lean` (github):** `.lean` files=79, LoC=11204, theorems=644, defs=199, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`[]`

#### [2611.05221](https://arxiv.org/abs/2611.05221) — Efficient Equilibrium Computation in Colonel Blotto Games
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT', 'GPT'])
- **Evidence:** Paper states ChatGPT generated the accompanying Lean implementation and formal proofs (after GPT helped work out proof details and manuscript drafts from authors' sketches); docs/paper-coverage.json maps all 18 paper LaTeX statement labels to Lean endpoints post-hoc with no leanblueprint or Challenge/Solution spec-lock.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `AbheekG/colonel-blotto-lean` (github):** `.lean` files=6123, LoC=585317, theorems=37671, defs=18989, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2611.04934](https://arxiv.org/abs/2611.04934) — The Complexity of Continuous Contract Design over Polymatroids
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** Lean files (Polymatroid.lean, Linear.lean) note they were taken from Paper/ and adapted/rewritten to follow Overleaf/STOC .tex drafts, tracked via a custom COVERAGE.md sync manifest rather than leanblueprint/@[blueprint] or comparator spec-lock; Claude assisted with checking bounds, formalizing proofs, and drafting text.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `zenodo/23895619` (zenodo):** `.lean` files=74, LoC=53595, theorems=1935, defs=817, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
- **Repo `philippwarode/contract-design-polymatroids-lean` (github):** `.lean` files=74, LoC=53595, theorems=1935, defs=817, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2611.04575](https://arxiv.org/abs/2611.04575) — Polynomial configurations and pointwise averages along Piatetski--Shapiro primes
- **Primary / Target Cats:** `math.CO` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT'])
- **Evidence:** The manuscript (Draft1.tex / revised Draft.tex) was written first and preserved unchanged ('Read all 1,273 lines of the authoritative source before choosing modules'), and ChatGPT was used afterward to generate the accompanying Lean 4 formalization; the repo also adds a companion leanblueprint==0.0.20 dependency graph synced with Lean declarations (evidence/BlueprintDeclarations.lean).
- **Risk flags:** []
- **Repo `HamedMousaviMath/Lean-Formalization-Polynomial-Configurations-and-Pointwise-Averages-Along-Piatetski--Shapiro-Primes` (github):** `.lean` files=84, LoC=12659, theorems=421, defs=141, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`

#### [2611.04545](https://arxiv.org/abs/2611.04545) — Coercive at the equilibrium, monotone nowhere: exact convergence certificates for learning in first-price auctions
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` ([])
- **Evidence:** Appendix C maps selected finite-algebra and real-analysis statements from Sections 4-6 (following Appendix A's chain) to Lean 4 / Mathlib v4.34.1 modules (lean/FirstPriceCertificates/, 27 files, 6,315 lines, 338 theorems), noting what each check takes as given while surrounding analytic arguments remain informal; no blueprint-sync or spec-lock tooling is mentioned, and the cited GitHub repo is inaccessible. latex_signals.agent_tools flagged 'claude' and 'harmonic', but 'harmonic' appears in Appendix F.11 ('the harmonic and the Airy well') and no snippet confirms AI-agent use.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2611.02465](https://arxiv.org/abs/2611.02465) — Pointwise Ergodic Theorems Along $\lfloor p^c\rfloor$ for Every $c>1$
- **Primary / Target Cats:** `math.CA` / ['math.DS'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P4_speclock_solve_distill` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Codex', 'Astra'])
- **Evidence:** Palomar submission repository with Challenge.lean / Solution.lean spec-lock and comparator.json, Codex (gpt-6.1-sol, gpt-6-luna, gpt-6.1-terra) and Astra agent-assisted formalization targeting the author's supplied LaTeX manuscript fractionalpowersofprimesfinal.tex, accompanied by semantic-audit.md and verification-report.md.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `anastasiosfragkosmath/Pointwise-Ergodic-Theorems-Along-floor-p-c-Palomar-Submission` (github):** `.lean` files=3933, LoC=788583, theorems=28459, defs=7224, sorry=3, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['comparator', 'lake build']`

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {}
- **Tool categories (contributed):** {}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Rocq` | 1 |

### Confirmed Beyond-Lean Papers
