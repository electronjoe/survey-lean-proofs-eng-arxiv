# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2026-11-01` to `2026-11-19` (3 weeks)
- **Target categories (8):** `cs.CR`, `cs.DC`, `cs.IT`, `cs.NI`, `cs.RO`, `eess.SP`, `eess.SY`, `math.OC`
- **Corpus size:** 4104 unique papers (4097 full-text screened, 99.83% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 4060 unique papers
- **Confirmed papers contributing Lean proofs (all):** **39** (0.95% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **36** (0.89% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **28** (0.68% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **12**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CR` | 629 | 7 | 1.11% | 4 |
| `cs.DC` | 335 | 6 | 1.79% | 0 |
| `cs.IT` | 338 | 6 | 1.78% | 6 |
| `cs.NI` | 196 | 0 | 0.00% | 0 |
| `cs.RO` | 1159 | 0 | 0.00% | 0 |
| `eess.SP` | 462 | 0 | 0.00% | 0 |
| `eess.SY` | 738 | 3 | 0.41% | 2 |
| `math.OC` | 724 | 19 | 2.62% | 17 |
| **Deduplicated Union** | **4104** | **39** | **0.95%** | **28** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_contributed` | 39 |
| `lean_citation_or_discussion` | 13 |
| `false_positive` | 3 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 28 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 3 |
| `P0_opaque_or_unspecified` | 8 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'engineering_math_proof': 28, 'software_or_system_fv': 4, 'pure_tcs_or_math': 7}
- **Observed Verification Tiers:** {'Tier2_Silver': 7, 'Tier1_Bronze': 13, 'Tier3_Gold': 19}
- **Artifact Availability:** {'public_lean_repo': 29, 'appendix_only': 1, 'none': 6, 'broken_or_missing_repo': 3}
- **AI/Agent Assistance Disclosed:** {'explicitly_yes': 30, 'unclear': 9}
- **Target Categories (Lean Contributed):** {'math.OC': 19, 'cs.CR': 7, 'cs.IT': 6, 'eess.SY': 3, 'cs.DC': 6}
- **Static Risk Flags (`proof-methods.md`):** {'Mode12_ProcessOpacity': 17, 'Mode10_ProofBloat': 12, 'Mode2_ScopeDowngrade': 10, 'Mode6_SorryOrAxiomOrNativeDecide': 3, 'Mode3_CustomDefs': 1}

## 4. Detailed Inventory of Confirmed Lean Papers (39)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2611.26272](https://arxiv.org/abs/2611.26272) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat, Mode12_ProcessOpacity | **Paper2Lean: Agentic Autoformalization of Mathematical Research Papers ** — Introduces Paper2Lean, an agentic autoformalization pipeline, and releases OptPaper-20, a 151k-LoC Lean 4 / Mathlib formalization of 20 mathematical optimization research papers with zero sorry/axioms. |
| [2611.26140](https://arxiv.org/abs/2611.26140) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `appendix_only` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Optimal Patrol Widths in the Infinite-Corridor Barrier-Guarding Game** — Optimal corridor barrier-guarding paper in math.OC whose main analytic and topological proofs are on paper while an accompanying ancillary Lean 4 (Mathlib v4.15.0) library verifies selected lemmas and finite rational certificate replays. |
| [2611.25599](https://arxiv.org/abs/2611.25599) | `cs.CR` | `cs.CR` | `software_or_system_fv` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `unclear` | Mode12_ProcessOpacity | **Tether: Verified Stateful Policy Engine for System-Level Monitoring of** — Tether implements a stateful agent security policy EDSL and verifies safety invariants in Lean 4, but provides no public Lean repository or authoring workflow details. |
| [2611.23762](https://arxiv.org/abs/2611.23762) | `quant-ph` | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Addressable transversal CCZ gates on almost good quantum LDPC codes an** — Post-hoc Mathlib-based Lean 4 formalization of three supporting algebraic lemmas (zero sorry/axioms) for an AI-generated companion note proving an assumption of the paper's quantum LDPC CCZ-gate construction, lacking lakefile/toolchain/CI and not covering the main theorems. |
| [2611.23080](https://arxiv.org/abs/2611.23080) | `cs.AI` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (medium) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Colombo: A Frontier-to-Frontier Autoresearch System for Oracle-Based O** — AI autoresearch system (Colombo) for oracle-based optimization claiming Lean-based formal certification of mathematical claims across 50+ Complexity Atlas settings, but providing only Colombo.pdf on Zenodo with no public Lean code. |
| [2611.22732](https://arxiv.org/abs/2611.22732) | `cs.CR` | `cs.CR` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **Provable Mixing Properties of Parallel Mixnets Revisited** — Analyzes parallel mixnets via statistical variance and concentration bounds for differential indistinguishability, claiming a full accompanying Lean mechanization at a public MPI-SWS GitLab repo carried out entirely by Claude. |
| [2611.22468](https://arxiv.org/abs/2611.22468) | `math.OC` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (low) | `Tier1_Bronze` | `broken_or_missing_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **A 5/2 Guarantee for Echelon Stock (s,S) Policies in One-Warehouse Mult** — Operations-research paper (math.OC) proving a 5/2 cost guarantee for echelon stock (s,S) policies in one-warehouse multi-retailer systems, claiming Lean 4 formalization of main results at a prove2.me URL with Claude mentioned in LaTeX signals and no inspectable Git/Lean repository. |
| [2611.20298](https://arxiv.org/abs/2611.20298) | `cs.PL` | `cs.CR` | `software_or_system_fv` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Type-Confusion Security** — Mechanizes type-confusion security proofs for an RPC/information-flow core calculus in Lean 4 using Mathlib, translated from pen-and-paper proofs with Codex and Claude Code assistance, with an axioms audit mentioned but no public repository URL provided. |
| [2611.20131](https://arxiv.org/abs/2611.20131) | `math.NA` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Quadrature-Induced Local Minima in Structure-Preserving Lotka-Volterra** — Optimal control and numerical analysis paper on Lotka-Volterra quadrature whose acknowledgment notes AI-assisted proof formalization/checking in Lean, but provides no public Lean files or workflow details. |
| [2611.19551](https://arxiv.org/abs/2611.19551) | `cs.CR` | `cs.CR` | `software_or_system_fv` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **TrustBound: Mechanized Completeness for Payment Epochs Initiated by AI** — Formalizes an admission-fencing and provider-contract closure model for AI-agent payment epochs in Lean 4.19.0 (zero sorry/custom axioms, checked via #print axioms, premise-removal mutations, and CI) alongside trace-checked Python service histories. |
| [2611.18455](https://arxiv.org/abs/2611.18455) | `stat.ML` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `unclear` | none | **Mesh-Free Weak-Form Regression for Learning Interaction Kernels from P** — Formalizes the paper's Theorem 1 (mean-field/particle SDE synchronous coupling and weak-form OLS/LASSO coefficient recovery bounds) in Lean 4 with zero sorry/custom axioms and full #print axioms and hash-lock audits. |
| [2611.18220](https://arxiv.org/abs/2611.18220) | `eess.SY` | `eess.SY` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode12_ProcessOpacity | **From Pen-and-Paper to Machine-Checked Proofs: Lean for System Identifi** — Tutorial introducing Lean 4 and Mathlib for system identification and control, formalizing elementary identifiability/invariance examples, an ARX/PEM template, and an almost-sure sharpening of Ljung (1999) Lemma 3.1 in a public repo with #print axioms checks but no lakefile/lean-toolchain/CI. |
| [2611.16781](https://arxiv.org/abs/2611.16781) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier2_Silver` | `public_lean_repo` | `unclear` | Mode12_ProcessOpacity | **Boundary Actuation of a Chain Fountain - Physically Admissible Trackin** — Control-theoretic analysis of boundary actuation for a chain fountain with a Lean 4 formalization (v0.18/v0.19, 722 named theorems) covering tracking, stochastic limits, and zero-gravity circulation via a zipped GitHub archive and a Theorem-to-Lean correspondence appendix. |
| [2611.16690](https://arxiv.org/abs/2611.16690) | `math.AG` | `math.OC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode6_SorryOrAxiomOrNativeDecide | **Hilbert's 17th problem for symmetric functions: undecidability and a c** — Post-hoc agent-generated Lean 4 formalization (~6.6k LoC) of the Diophantine reduction (Thm 2.2) and octic counterexample (Thm 3.1, Cor 3.6) with #guard_msgs axiom audits; both main theorems are sorry-free via an elementary hypercube bound, while cited Thm 3.2 (and Cor 3.3-3.4) has 1 sorry and decidability/Section 4 are unformalized. |
| [2611.15431](https://arxiv.org/abs/2611.15431) | `quant-ph` | `cs.IT` | `engineering_math_proof` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Subadditivity and the failure of strong subadditivity in the Nichols--** — Proves subadditivity and strong-subadditivity failure for Nichols-Wootters entropies (with cs.IT capacity applications) and claims AI-assisted Lean formal verification in the acknowledgments without providing a public Lean repository or workflow details. |
| [2611.15201](https://arxiv.org/abs/2611.15201) | `cs.DC` | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Sparse Matrix Multiplication Exponent 1.5 in the Low-bandwidth Model** — Lean 4 formalization (zero sorry in Solution, Comparator + multi-kernel audited) of an O(d^{3/2})-round supported sparse matrix multiplication algorithm and broadcast/aggregation lower bounds in a scalar-word low-bandwidth model, created post-hoc from the manuscript PDF with OpenAI Codex/GPT-6. |
| [2611.15128](https://arxiv.org/abs/2611.15128) | `cs.IT` | `cs.CR,cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Affine Combiners for Reed-Solomon Proximity Gaps** — AI-analyzed coding-theory/crypto-math paper proving Reed-Solomon affine-combiner MCA bounds, whose main RS theorems (Secs. 3–4, Thm. 5.2) were post-hoc formalized in Lean 4 inside leanEthereum/leanVM (20 AffineCombiner*.lean files, ~5k LoC) with CI escape-scanning and #print axioms audit, while Sec. 5 equal-degree reductions and Sec. 7 Reed-Muller extensions remain unformalized. |
| [2611.14756](https://arxiv.org/abs/2611.14756) | `math.DS` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | none | **Stability of equilibria in discrete-time modified-gradient systems and** — Post-hoc Lean 4 + Mathlib formalization of the main discrete-time modified-gradient stability and basin-of-attraction theorems (Lemma 4.1, Theorem 5.1, Corollary 5.2, Theorem 6.1) with CI-verified standard-axiom audit. |
| [2611.14475](https://arxiv.org/abs/2611.14475) | `math.FA` | `cs.IT` | `engineering_math_proof` | `P4_speclock_solve_distill` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Explicit restricted isometries with $k=m^{2/3-o(1)}$** — Formalizes all main theorems of an explicit RIP matrix construction (k = m^{2/3-o(1)}) and 2/3 barriers in Lean 4/Mathlib using AI agents under a frozen-statement and Comparator (NanoDa + Lean kernel) spec-lock, omitting only the polynomial running-time bound for 'explicit'. |
| [2611.13872](https://arxiv.org/abs/2611.13872) | `math.OC` | `math.OC` | `engineering_math_proof` | `P4_speclock_solve_distill` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **LongTails: Automated Research in Optimization** — LongTails is a Lean 4 framework for AI-assisted discovery of optimization algorithms and oracle-complexity bounds, spec-locked via Comparator and yielding >100 formally verified results in a public repository. |
| [2611.13585](https://arxiv.org/abs/2611.13585) | `cs.DS` | `math.OC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `broken_or_missing_repo` | `unclear` | Mode12_ProcessOpacity | **Approximating graphic TSP by b-matchings** — Combinatorial optimization / graph algorithms paper on graphic TSP approximation that claims supplementary Lean 4 (v4.19.0) / Mathlib formalization for stronger Table 2 bounds, but the linked GitHub repo contains zero .lean files or toolchain/CI metadata. |
| [2611.13584](https://arxiv.org/abs/2611.13584) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode10_ProofBloat | **Exact (Non-)Accelerations of Heavy-Ball Discretizations** — Formalizes all 88 numbered results of a 63-page optimization paper on heavy-ball/momentum discretizations in a 512-file (~55.3k LoC) Lean 4 library with manual ArticleMap correspondence, axiom auditing, and stock-kernel replay. |
| [2611.12680](https://arxiv.org/abs/2611.12680) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Wolfe's Minimum-Norm-Point Method Generalizes the Simplex Method** — Post-hoc Lean 4 formalization (WolfeSimplex on Zenodo, 23.9k LoC, 0 sorry/custom axioms, whole-project axiom and statement-boundary audits) verifying Theorem 1, Corollaries 1–4, and all 20 lemmas connecting Wolfe's minimum-norm-point method and the simplex method, developed with Claude/Claude Code assistance. |
| [2611.12585](https://arxiv.org/abs/2611.12585) | `math.NA` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | none | **A Large Gap between Galerkin Errors with and without Mesh-Uniform Regu** — Post-hoc Lean 4 formalization (by GPT-6 Astra, provided in arXiv v2 ancillary files) proving high-frequency spurious eigenpairs and error-bound failures for the standard cubic Hermite Galerkin scheme of the KdV equation. |
| [2611.11713](https://arxiv.org/abs/2611.11713) | `cs.IT` | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Binary Belief Propagation Fixed Points: Finiteness, Rigidity, and Topo** — Formally verifies all three main theorems (finiteness, rigidity, and logarithmic genus/size bounds) on binary belief propagation fixed points in Lean 4 with Mathlib and an automated transitive-axiom audit, alongside standalone Python rational interval certificates for a 18-vertex discriminant example. |
| [2611.10902](https://arxiv.org/abs/2611.10902) | `eess.SY` | `eess.SY` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade | **Bisect-Index-Choose: A Fast and Exact Algorithm for EV Charging under ** — EV charging optimization paper (eess.SY) contributing a Lean 4 + Mathlib formalization (~2,068 LoC) of its main theorems (Theorems 1-4 for K=2, Lemmas 1-2, strong duality, Table I, Appendices A-B, and Algorithm 1 evaluation bound) with a 34-theorem #print axioms manifest and zero sorry/custom axioms, though excluding K!=2 cases, bisection tolerances, and runtime bounds. |
| [2611.10810](https://arxiv.org/abs/2611.10810) | `cs.DB` | `cs.DC` | `software_or_system_fv` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode3_CustomDefs | **Extending DBLog-Based Incremental Snapshots to Handle Orphan Rows in C** — Extends DBLog incremental snapshots to delete orphan rows in CDC pipelines, formally verifying safety and convergence across six Isabelle/HOL theories ported to Lean 4 (zero sorry/custom axioms, audited via #print axioms) alongside bounded TLA+ models. |
| [2611.09169](https://arxiv.org/abs/2611.09169) | `math.OC` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **The multiplier step size in classical two-block ADMM: convergence and ** — Optimization paper (math.OC) on two-block ADMM step-size convergence and counterexamples claiming an accompanying Lean 4 formalization on ReasBook (optpku.github.io), while the linked GitHub repo only contains exact arithmetic certificates (0 Lean files) and acknowledges generative AI assistance. |
| [2611.09050](https://arxiv.org/abs/2611.09050) | `math.OC` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Resolvent-Diagonal Energy of Isospectral Jacobi Matrices** — Verifies mathematical theorems on resolvent-diagonal energy of isospectral Jacobi matrices and optimal Nesterov momentum endpoint gains in a 139.6k-LoC Lean 4 package (`jacobi`) with automated axiom auditing and kernel replay. |
| [2611.08172](https://arxiv.org/abs/2611.08172) | `cs.IT` | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Uniform Three-Fold Product Expansion of Algebraic-Geometry Codes over ** — Formalizes in Lean 4 (with ~200k LoC, zero sorry/custom axioms, and full-closure audit scripts) the main uniform 3-fold product expansion, sharp filling, and dual-family rate/distance theorems for algebraic-geometry codes on the Garcia-Stichtenoth tower over F_729. |
| [2611.05243](https://arxiv.org/abs/2611.05243) | `cs.LG` | `math.OC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **Logarithmic Regret for Alternating Mirror Descent** — Proves an O(log T) regret bound for Alternating Online Mirror Descent in two-player zero-sum bilinear games and formalizes all 15 named manuscript results in a zero-sorry, axiom-audited Lean 4 repository (AltOMD-Lean) developed with GPT-5.6 Sol and GPT-6 Astra. |
| [2611.05136](https://arxiv.org/abs/2611.05136) | `cs.CC` | `cs.CR` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Information Loss Is All You Need: $TC^0$ Pseudorandomness from Worst-C** — AI-generated 219k-LoC Lean 4 formalization of Theorem 9.9 (constructive Gaussian AFT sampler in a counted binary-operation model) with exhaustive transitive axiom audit (Audit.lean) and provenance manifest, covering one core theorem rather than the paper's full LWE-to-LAR/TC0-PRF/ReLU-hardness claims. |
| [2611.04876](https://arxiv.org/abs/2611.04876) | `cs.CR` | `cs.CR` | `engineering_math_proof` | `P4_speclock_solve_distill` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Leakage-Resilient Computation via Matrix Refreshing** — Formalizes continual matrix refreshing, NAND/stateful leakage-resilient circuit compilers, and expected-work simulators in Lean 4 (81k LoC) using ChatGPT under a comparator Challenge/Solution spec-lock (`Proofs.ReferenceClaims` vs `Proofs.ProvedClaims`). |
| [2611.04561](https://arxiv.org/abs/2611.04561) | `cs.DC` | `cs.DC,eess.SY` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat, Mode6_SorryOrAxiomOrNativeDecide | **Distributed LTL Synthesis under Arbitrary Message Adversaries** — Distributed LTL synthesis decidability characterization (nowhere-dense geometric image and repeated consensus) formalized post-hoc in ~929k LoC of Lean 4.30/Mathlib with Codex/Claude assistance; main Results and Paper endpoints pass #print axioms and Comparator+Nanoda kernel replay with only standard axioms, while two native_decide calls appear in an unimported falsification probe. |
| [2611.02256](https://arxiv.org/abs/2611.02256) | `cs.DC` | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Exact Shortest Paths and Maximum Flow in Planar Networks in the CONGES** — CONGEST planar-network SSSP and max-flow paper formalizing three supporting lemmas (Virtual Source, Dual Distance, discretized boosting) and auxiliary arguments in Lean 4/Mathlib without sorry or custom axioms, while leaving the main distributed algorithms and round bounds on paper. |
| [2611.02169](https://arxiv.org/abs/2611.02169) | `math.OC` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Split Cuts in Fixed Integer Dimensions** — Optimization paper (math.OC) on split cuts in fixed integer dimensions that discloses using OpenAI ChatGPT for Lean verification of proofs and calculations, with no public Lean artifact or workflow details. |
| [2611.02057](https://arxiv.org/abs/2611.02057) | `cs.DS` | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode6_SorryOrAxiomOrNativeDecide, Mode10_ProofBloat, Mode12_ProcessOpacity | **Paying for Fractional Error: Tight Constant-Round Approximation of Cov** — Formalizes all 81 named distributed-CONGEST covering-approximation results in a 166k-LoC Lean 4 repo with AI assistance; 73 statements use only standard axioms while 8 (including Theorem E and Corollary 1.1) depend on 7 declared external graph/topology axioms, with no CI and an incomplete rebuild of the export. |
| [2611.01761](https://arxiv.org/abs/2611.01761) | `cs.DC` | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Computation in Anonymous Directed Dynamic Networks: Exact Worst-Case T** — Public Lean 4 formalization (158k LoC, 2,104 files) produced with ChatGPT-6 Astra covering all 24 formal statements of a cs.DC distributed-counting paper, audited by a custom transitive axiom checker with zero sorry/axioms. |
| [2611.01384](https://arxiv.org/abs/2611.01384) | `math.OC` | `math.OC` | `engineering_math_proof` | `P0_opaque_or_unspecified` (medium) | `Tier1_Bronze` | `broken_or_missing_repo` | `unclear` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Benign population landscapes do not transfer to empirical risk minimiz** — Claims an accompanying Lean formalization of supporting Appendix C analytic bounds for nonsmooth phase retrieval, while main theorems and interval enclosures remain outside Lean and the linked GitHub repo is inaccessible. |

### Evidence Notes per Confirmed Lean Paper

#### [2611.26272](https://arxiv.org/abs/2611.26272) — Paper2Lean: Agentic Autoformalization of Mathematical Research Papers at Scale
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Paper2Lean', 'lean-lsp-mcp', 'Claude', 'Codex', 'DeepSeek', 'GPT-5', 'Kimina'])
- **Evidence:** Existing informal mathematical optimization papers (20 papers from 1983-2024) are converted post-hoc into Lean 4 projects via an agentic DAG extraction, statement formalization, semantic checking, proving, and human-audit pipeline in TTony2019/OptPaper, without leanblueprint/LeanArchitect sync (has_blueprint_dir=false) or Challenge.lean/Solution.lean comparator spec-lock.
- **Risk flags:** ['Mode10_ProofBloat', 'Mode12_ProcessOpacity']
- **Repo `TTony2019/OptPaper` (github):** `.lean` files=558, LoC=151214, theorems=3398, defs=724, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Repo `anthropics/fermats-last-theorem` (github):** `.lean` files=60478, LoC=11880614, theorems=598184, defs=95596, sorry=2, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`[]`
- **Repo `cameronfreer/lean4-skills` (github):** `.lean` files=66, LoC=1442, theorems=56, defs=96, sorry=0, axiom=4, native_decide=1, unsafe=2, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`['print axioms']`
- **Repo `oOo0oOo/lean-lsp-mcp` (github):** `.lean` files=20, LoC=123, theorems=23, defs=19, sorry=3, axiom=0, native_decide=0, unsafe=1, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['lake build']`

#### [2611.26140](https://arxiv.org/abs/2611.26140) — Optimal Patrol Widths in the Infinite-Corridor Barrier-Guarding Game
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['OpenAI GPT', 'Codex', 'Anthropic Claude', 'Google DeepMind Gemini', 'Antigravity'])
- **Evidence:** The paper presents analytic proofs and topological reductions in LaTeX (34 pages, 25 theorem environments) while attaching a Lean 4 / Mathlib v4.15.0 library in arXiv ancillary files (anc/README.md, ContinuumUpperCert.lean) specifically for selected algebraic lemmas and kernel replays of finite rational certificates alongside Python verifiers, with no mention of blueprint-sync or spec-lock tooling.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

#### [2611.25599](https://arxiv.org/abs/2611.25599) — Tether: Verified Stateful Policy Engine for System-Level Monitoring of Agents
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['Claude', 'Codex', 'Gemini'])
- **Evidence:** The paper implements an abstract action calculus and stateful policy language as a Lean 4 EDSL that compiles to a runtime monitor and proves safety invariants in Lean 4 (Table 1), but provides no public Lean repository (all listed repos have 0 .lean files) and no workflow details indicating paper-first, Lean-first, blueprint-sync, or spec-lock.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.23762](https://arxiv.org/abs/2611.23762) — Addressable transversal CCZ gates on almost good quantum LDPC codes and nearly optimal magic state protocols
- **Primary / Target Cats:** `quant-ph` / ['cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** Paper states the proof of Assumption 1.1 in a companion manuscript was generated using AI and is in a companion repo 'together with Lean formalizations of selected algebraic lemmas. We are revising the exposition and extending the Lean formalization, which does not yet cover the full argument.' The repo (CoprimeFrobenius.lean, 667 lines, 0 sorry) formalizes three lemmas from the companion PDF ('exactly as in the note') without blueprint sync, comparator spec-lock, lakefile, or lean-toolchain.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification` (github):** `.lean` files=1, LoC=589, theorems=36, defs=5, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.23080](https://arxiv.org/abs/2611.23080) — Colombo: A Frontier-to-Frontier Autoresearch System for Oracle-Based Optimization
- **Primary / Target Cats:** `cs.AI` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['GPT-5', 'Colombo'])
- **Evidence:** Section 2.4-2.5 describes an internal Colombo workflow where reviewed natural-language mathematical arguments are translated into pinned-toolchain Lean proofs (with kernel and semantic-alignment checks) and then composed into papers by a Paper Composer; however, the Zenodo artifact (zenodo/23438699) contains only Colombo.pdf and 0 .lean files, providing no public Lean code or direct visibility into how the paper's own claims and 50+ Atlas results were formalized.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.22732](https://arxiv.org/abs/2611.22732) — Provable Mixing Properties of Parallel Mixnets Revisited
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude', 'ChatGPT', 'Gemini'])
- **Evidence:** Paper states 'The main results of this paper have been verified in the mechanical proof assistant, Lean' with a public GitLab repository (https://gitlab.mpi-sws.org/FCS/mixnets-sync-public), and notes 'The Lean formalization that accompanies this paper was carried out entirely by Claude' alongside informal proofs (12 theorem environments) with no mention of blueprint sync or spec-lock tooling; local_repo_dirs is empty (only unrelated arXiv HTML GitHub repos were scraped).
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.22468](https://arxiv.org/abs/2611.22468) — A 5/2 Guarantee for Echelon Stock (s,S) Policies in One-Warehouse Multi-Retailer Systems
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`low`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** Snippet states 'The main results are formally verified in Lean 4; the formal proofs are public at https://prove2.me/missions/...' and mentions '...ical verification, and editing' alongside latex_signals.agent_tools=['Claude'], but repos=[] and local_repo_dirs=[] with no workflow/blueprint/spec-lock details provided in the truncated evidence.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.20298](https://arxiv.org/abs/2611.20298) — Type-Confusion Security
- **Primary / Target Cats:** `cs.PL` / ['cs.CR'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Codex', 'Claude Code'])
- **Evidence:** The AI Use section explicitly states that Codex and Claude Code assisted with Lean 4 development by 'assisting in the translation of pen-and-paper definitions and proofs', and the Data-Availability Statement notes a README.md manually mapping each paper result to its Lean definition, indicating post-hoc formalization of pen-and-paper proofs without blueprint or spec-lock tooling.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.20131](https://arxiv.org/abs/2611.20131) — Quadrature-Induced Local Minima in Structure-Preserving Lotka-Volterra Control
- **Primary / Target Cats:** `math.NA` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['AI tools (unspecified)'])
- **Evidence:** Only a single acknowledgment sentence mentions Lean ("These tools also assisted with formalizing and checking proofs in (Lean)"), and the linked GitHub repo (AleXXandreAutran/structure-preserving-lotka-volterra-control) is accessible with 148 files but lean_file_count: 0, has_lean_toolchain: false, and has_lakefile: false, leaving the formalization workflow and scope completely unspecified.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.19551](https://arxiv.org/abs/2611.19551) — TrustBound: Mechanized Completeness for Payment Epochs Initiated by AI Agents
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT', 'Codex', 'Claude'])
- **Evidence:** The LNCS manuscript (paper/lncs/main.tex) states the admission model and closure theorem informally with prose proofs and cites Lean declarations in footnotes and a verbatim excerpt, without LeanArchitect/leanblueprint (has_blueprint_dir=false) or comparator/spec-lock files (has_challenge_file=false, has_solution_file=false); formal/README.md notes supporting Lean models retained for provenance alongside the two core files (Admission.lean, StripeGate.lean). The paper explicitly discloses using OpenAI ChatGPT, Codex, and Anthropic Claude for code development, literature exploration, and manuscript editing.
- **Risk flags:** []
- **Repo `tokencraftdata/trustbound` (github):** `.lean` files=16, LoC=1332, theorems=160, defs=135, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`

#### [2611.18455](https://arxiv.org/abs/2611.18455) — Mesh-Free Weak-Form Regression for Learning Interaction Kernels from Particle Trajectories
- **Primary / Target Cats:** `stat.ML` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` ([])
- **Evidence:** The paper links github.com/inody/wmfki_lean as a Lean 4 formalization of Theorem 1. Repo files (README.md, Blueprint.md, Lean_Code/AXIOM_STATUS.md, scripts/verify.py, statement-lock.json, l4dc-statement-lock.json) show the manuscript's theorems existed first and were translated into hash-locked Lean specifications and verified against SHA-256 hashes of the manuscript's LaTeX environments, without LeanArchitect/leanblueprint/Verso or Challenge/Solution distillation.
- **Risk flags:** []
- **Repo `inody/wmfki_lean` (github):** `.lean` files=156, LoC=12236, theorems=495, defs=137, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2611.18220](https://arxiv.org/abs/2611.18220) — From Pen-and-Paper to Machine-Checked Proofs: Lean for System Identification
- **Primary / Target Cats:** `eess.SY` / ['eess.SY'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` (['Claude'])
- **Evidence:** Tutorial paper formalizing existing pen-and-paper textbook results (Ljung 1999 Lemma 3.1, basic identifiability, set invariance, ARX identifiability) in an accompanying repo manasdm/Lean-SysID (created Nov 2-3, 2026 before Nov 13, 2026 submission). Uses '-- ANCHOR:' comments to reproduce Lean snippets in the paper, with no blueprint directory, @[blueprint]/\inputleannode, or Challenge/Solution spec-lock.
- **Risk flags:** ['Mode12_ProcessOpacity']
- **Repo `forgi86/control-theory-in-lean` (github):** `.lean` files=7, LoC=1196, theorems=38, defs=28, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `manasdm/Lean-SysID` (github):** `.lean` files=4, LoC=528, theorems=21, defs=19, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.16781](https://arxiv.org/abs/2611.16781) — Boundary Actuation of a Chain Fountain - Physically Admissible Tracking, Stochastic Limits and Zero-Gravity Circulation
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier2_Silver` | **AI:** `unclear` (['Gemini'])
- **Evidence:** Paper derives nonlinear tracking, stochastic viability, and zero-gravity circulation conditions and documents their formalization via Appendix C ("Theorem-to-Lean correspondence and verification scope"), incremental completion of "remaining article deductions" (v0.18 -> v0.19.0), and a zipped Lean 4.33.0-rc1 source archive (`Chain_Fountain_Lean_GitHub.zip`) with no blueprint or spec-lock files (`has_blueprint_dir: false`, `has_challenge_file: false`, `has_solution_file: false`).
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.16690](https://arxiv.org/abs/2611.16690) — Hilbert's 17th problem for symmetric functions: undecidability and a counterexample
- **Primary / Target Cats:** `math.AG` / ['math.OC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude', 'Claude Fable 5.1', 'Codex'])
- **Evidence:** The paper states 'Finally, a Lean formalization of our proof was almost entirely generated by coding agents', and the repo README/AnyDim/Paper.lean explicitly restates the paper's theorems statement-by-statement with documented deviations and no blueprint-sync or comparator spec-lock tooling.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `MColbrook/AIM` (github):** `.lean` files=37, LoC=1870, theorems=128, defs=47, sorry=61, axiom=1, native_decide=1, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`['comparator', 'lake build']`
- **Repo `RobinSchabert/positive-sym-func-h17-undecidability-lean` (github):** `.lean` files=24, LoC=6592, theorems=564, defs=165, sorry=1, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc3`, ci=`[]`

#### [2611.15431](https://arxiv.org/abs/2611.15431) — Subadditivity and the failure of strong subadditivity in the Nichols--Wootters family of entropies
- **Primary / Target Cats:** `quant-ph` / ['cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['ChatGPT Pro (GPT-6 Pro)', 'Codex (gpt-6.1-sol)', 'Claude Opus 5.5', 'Claude Code'])
- **Evidence:** Acknowledgments state that AI tools (ChatGPT Pro / GPT-6 Pro, Codex / gpt-6.1-sol, and Claude Opus 5.5 via Claude Code) were used for 'double-checking, including formal verification of the results in Lean', and mention a 'verification package' for computations, but urls, repos, and local_repo_dirs are all empty and no Lean authoring workflow or scope details are provided.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.15201](https://arxiv.org/abs/2611.15201) — Sparse Matrix Multiplication Exponent 1.5 in the Low-bandwidth Model
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['OpenAI Codex', 'GPT-6', 'GPT-6 Astra', 'GPT-6.1 Sol'])
- **Evidence:** formalization.yaml and docs/manuscript.md state the 10-page paper PDF was supplied first ('Formalize the supplied PDF in Palomar style using multiple agents') with numbered claims and proofs unchanged in arXiv v1 (which only added the formalization DOI footnote and AI Methodology note). Although it uses Challenge.lean/Solution.lean and comparator spec-checking tooling, there was no post-proof distillation into a paper/blueprint, making it paper-first post-hoc formalization using a Challenge/Solution verification harness.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `zenodo/24127514` (zenodo):** `.lean` files=36, LoC=5307, theorems=267, defs=241, sorry=25, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`[]`

#### [2611.15128](https://arxiv.org/abs/2611.15128) — Affine Combiners for Reed-Solomon Proximity Gaps
- **Primary / Target Cats:** `cs.IT` / ['cs.CR', 'cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT 6 Astra', 'Claude Code Opus 5.5'])
- **Evidence:** The paper states that all proofs were initially carried out with AI and then 'The authors edited, verified, reorganized, and Lean-formalized the initial writeup' using ChatGPT 6 Astra (with theorem statements checked by Claude Code Opus 5.5). In the linked repo leanEthereum/leanVM (formal/lean_vm/LeanVM/Protocol/ToArkLib/Whir/AffineCombiner*.lean, 20 files, 4,963 LoC), docstrings cite '[CWYZ26]' (this paper) theorem/lemma/equation numbers post-hoc with no leanblueprint/LeanArchitect sync or Challenge/Solution comparator spec-lock.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `leanEthereum/leanVM` (github):** `.lean` files=2627, LoC=549901, theorems=26270, defs=15344, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0`, ci=`['lake build', 'print axioms']`

#### [2611.14756](https://arxiv.org/abs/2611.14756) — Stability of equilibria in discrete-time modified-gradient systems and the multivariate breeder's equation
- **Primary / Target Cats:** `math.DS` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` ([])
- **Evidence:** The repository contains no blueprint or spec-lock files (has_blueprint_dir=false, has_challenge_file=false, tex_file_count=0); README.md maps Lean theorems to arXiv v1 manuscript numbering and explicitly documents small differences between the Lean proofs and the already-written paper proofs.
- **Risk flags:** []
- **Repo `zenodo/24118844` (zenodo):** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `magbenji/discrete-modified-gradient-lean` (github):** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.14475](https://arxiv.org/abs/2611.14475) — Explicit restricted isometries with $k=m^{2/3-o(1)}$
- **Primary / Target Cats:** `math.FA` / ['cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P4_speclock_solve_distill` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Opus 5.5', 'Claude Code', 'GPT-6.1 Sol', 'GPT-6 Astra', 'Codex CLI', 'ChatGPT'])
- **Evidence:** Statements were drafted and frozen from the paper into ExplicitRIP/Frozen/ and Challenge.lean (with sorry), audited against the paper, then solved by parallel AI agents (Opus 5.5 orchestrator, GPT-6.1 Sol, GPT-6 Astra, Claude subagents) and verified against Solution.lean via Comparator (comparator.json, NanoDa enabled). Although the paper text and initial proof were drafted first/concurrently (Nov 7–10, 2026) rather than purely Lean-first, the repo explicitly uses frozen Challenge.lean/Solution.lean spec-locking and unconstrained AI proof search, with formalization also surfacing local fixes to cited arguments (footnote 2).
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `ckuemmerle/ExplicitRIPTwoThirds` (github):** `.lean` files=379, LoC=29967, theorems=1222, defs=258, sorry=4, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.13872](https://arxiv.org/abs/2611.13872) — LongTails: Automated Research in Optimization
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P4_speclock_solve_distill` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude', 'Codex', 'DeepSeek'])
- **Evidence:** Human/researcher fixes a formal Setup (assumptions, oracle model, accuracy criterion) in Lean 4 (LongTails/Setups/*.lean); AI agents (Claude, Codex, DeepSeek) search for algorithms and prove Complexity bounds (LongTails/Theorems/*.lean); run_comparator.py and CI (.github/workflows/verify.yml) dynamically generate Challenge modules from the fixed Setup and audit each solution with leanprover/comparator (restricting axioms to propext, Classical.choice, Quot.sound); verified Complexities are then deterministically converted to LaTeX/tables for the paper (LeanTeX/BudgetLatex.lean and paper §3/§B–C).
- **Risk flags:** []
- **Repo `k3nfalt/longtails` (github):** `.lean` files=4070, LoC=697377, theorems=34985, defs=11293, sorry=0, axiom=0, native_decide=0, unsafe=1, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`['comparator']`
- **Repo `leanprover/comparator` (github):** `.lean` files=46, LoC=875, theorems=42, defs=121, sorry=26, axiom=6, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['comparator', 'lake build', 'nanoda']`
- **Repo `optsuite/optlib` (github):** `.lean` files=43, LoC=15758, theorems=695, defs=113, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.13.0`, ci=`['lake build']`

#### [2611.13585](https://arxiv.org/abs/2611.13585) — Approximating graphic TSP by b-matchings
- **Primary / Target Cats:** `cs.DS` / ['math.OC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['GPT-5', 'GPT-6'])
- **Evidence:** Paper states main ideas and proofs are human-generated, human-explained, and self-contained in the manuscript/appendix, while Lean 4 (v4.19.0) over Mathlib (c44e0c8e) was used separately as 'Additional Evidence' to formalize stronger bounds for the last column of Table 2 (sketched in paper, cited as [36]). No blueprint or spec-lock tooling is present, though confidence is medium because the linked GitHub repo (Mehrdad-Sohrabi/Graphic-TSP) has lean_file_count: 0.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.13584](https://arxiv.org/abs/2611.13584) — Exact (Non-)Accelerations of Heavy-Ball Discretizations
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` ([])
- **Evidence:** Paper cites a Lean formalization in PolynomialRealizationsProgram/nesterov; the repo contains no blueprint directory, LeanArchitect annotations, or Challenge/Solution spec-lock, and instead maintains a manual correspondence table (nesterov/ArticleMap.md, referencing a SHA-256 digest of nesterov.tex) and ordered #check showcase (nesterov/Article.lean) mapping all 88 numbered article results to Lean declarations.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `dmivilensky/PolynomialRealizationsProgram` (github):** `.lean` files=7628, LoC=840767, theorems=48067, defs=21676, sorry=0, axiom=0, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2611.12680](https://arxiv.org/abs/2611.12680) — Wolfe's Minimum-Norm-Point Method Generalizes the Simplex Method
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude', 'Claude Code'])
- **Evidence:** The Lean 4 artifact (WolfeSimplex, archived on Zenodo in arXiv v2) contains 125 .lean files and 0 .tex files with no leanblueprint, LeanArchitect (@[blueprint]/\inputleannode), or Challenge/Solution spec-lock files. Its .gitignore excludes local reading copies of the unpublished manuscript (/samplepaper_*.tex, /PAPER_MAP.md) and /CLAUDE.md ('Claude Code working notes'), while docs/REVIEW.md and docs/COVERAGE.md record post-hoc alignment checks against an unchanged downloaded manuscript archive (SHA-256 9c07b865...).
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `zenodo/24136107` (zenodo):** `.lean` files=125, LoC=23932, theorems=1456, defs=566, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.12585](https://arxiv.org/abs/2611.12585) — A Large Gap between Galerkin Errors with and without Mesh-Uniform Regularity for the KdV Equation with Boundary Dissipation
- **Primary / Target Cats:** `math.NA` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['GPT-6 Astra', 'Claude', 'Codex'])
- **Evidence:** Comment states 'v2 adds Lean 4 proofs of the main results' and text explains the author tried to check the proof by hand, found its complexity too large, and had it formalized in Lean 4 by GPT-6 Astra (using contraction mappings instead of Rouché's theorem), with Appendix A documenting correspondence and build instructions (`lake build SLean`, Lean 4.35.0) rather than blueprint-sync or spec-lock tooling.
- **Risk flags:** []

#### [2611.11713](https://arxiv.org/abs/2611.11713) — Binary Belief Propagation Fixed Points: Finiteness, Rigidity, and Topological Complexity
- **Primary / Target Cats:** `cs.IT` / ['cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Large language model tools'])
- **Evidence:** No blueprint directory or Challenge/Solution spec-lock is present; TheoremB.lean explicitly references the manuscript ('論文 papers/bp-response-geometry/ の主定理 B'), and Section 8 and README.md document where the Lean formalization departs from the written proofs and which parts remain outside it, with LLM tools explicitly credited for writing the Lean formalization.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `TauCetiProject/TauCeti` (github):** `.lean` files=37714, LoC=0, theorems=0, defs=0, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
- **Repo `ywatanabex/bp-degree-syzygies-lean` (github):** `.lean` files=932, LoC=135060, theorems=7411, defs=3205, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `ywatanabex/bp-response-geometry-lean` (github):** `.lean` files=257, LoC=69875, theorems=3955, defs=1291, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.10902](https://arxiv.org/abs/2611.10902) — Bisect-Index-Choose: A Fast and Exact Algorithm for EV Charging under Minimum Charging Rates
- **Primary / Target Cats:** `eess.SY` / ['eess.SY'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` (['Claude'])
- **Evidence:** Public repo canberksaner/bic-public has a lean/ subdirectory (11 Lean 4 files, 2,068 non-empty LoC, Mathlib v4.36.0-rc2) with no blueprint directory, LeanArchitect annotations, or Challenge/Solution spec-lock files. README.md and Lean docstrings (e.g., Correctness.lean, Choose.lean, Everett.lean) explicitly map theorems to existing paper labels, equations, sections, and algorithm line numbers ('lines ch-while to ch-dec', '(eq:decomposition)', 'Lean's groups 0 and 1 are the paper's groups 1 and 2') and list which paper results are checked vs omitted, indicating post-hoc formalization of paper proofs. CheckAxioms.lean runs 34 #print axioms checks with zero sorry/axiom/native_decide. latex_signals.agent_tools lists 'Claude', without context in the repo or snippets.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `canberksaner/bic-public` (github):** `.lean` files=11, LoC=2068, theorems=102, defs=40, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.10810](https://arxiv.org/abs/2611.10810) — Extending DBLog-Based Incremental Snapshots to Handle Orphan Rows in CDC Pipelines
- **Primary / Target Cats:** `cs.DB` / ['cs.DC'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Fable 5.1', 'Claude Opus 5.5', 'Gemini'])
- **Evidence:** Primary formalization is in Isabelle/HOL (session Orphan_Absence) with a separate Lean 4 port in lean/ (OrphanAbsence, 6 of 7 theories, 10,862 LoC) mapped manually via tables in lean/README.md and lean/VERIFICATION.md; no LeanArchitect, leanblueprint, Verso, or Challenge/Solution comparator spec-lock tooling is used, and VERIFICATION.md documents post-hoc wording/list syncs between the paper, Isabelle, and Lean.
- **Risk flags:** ['Mode3_CustomDefs']
- **Repo `zenodo/22643866` (zenodo):** `.lean` files=6, LoC=2092, theorems=88, defs=34, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.2`, ci=`[]`
- **Repo `zenodo/24035424` (zenodo):** `.lean` files=24, LoC=10862, theorems=525, defs=108, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.2`, ci=`[]`

#### [2611.09169](https://arxiv.org/abs/2611.09169) — The multiplier step size in classical two-block ADMM: convergence and counterexamples
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` ([])
- **Evidence:** The paper states 'A Lean 4 formalization accompanying this work is available at https://optpku.github.io/ReasBook/versions/v4.32.0/papers/glowinski_admm_counterexample/.' right before the Acknowledgments ('Generative AI assisted manuscript preparation and parts of the mathematical...'). The only scraped GitHub repo (bqliu815/ADMM-Multiplier-Step-Size) contains 13 files with 0 .lean files, no lakefile/toolchain, and no blueprint or spec-lock files (it holds exact arithmetic certificates and verification scripts). No local_repo_dirs, Lean source files, or workflow details are present in the evidence to determine authoring order or verified scope.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.09050](https://arxiv.org/abs/2611.09050) — Resolvent-Diagonal Energy of Isospectral Jacobi Matrices
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Opus 5.5', 'ChatGPT-6.1 Sol'])
- **Evidence:** Manuscript states that Opus 5.5 and ChatGPT-6.1 Sol were used to edit the manuscript and prepare the Lean formalization package; the `jacobi/` subpackage maps proofs post-hoc to the printed paper numbering via `jacobi/Article.lean` and `jacobi/ArticleMap.md` (noting alternative proofs and excluded numerical figures) without `leanblueprint` (`@[blueprint]`, `\inputleannode`) or `Challenge.lean`/`Solution.lean` spec-lock.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `dmivilensky/PolynomialRealizationsProgram` (github):** `.lean` files=7628, LoC=840767, theorems=48067, defs=21676, sorry=0, axiom=0, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`

#### [2611.08172](https://arxiv.org/abs/2611.08172) — Uniform Three-Fold Product Expansion of Algebraic-Geometry Codes over a Fixed Field
- **Primary / Target Cats:** `cs.IT` / ['cs.IT'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Harmonic'])
- **Evidence:** The 76-page cs.IT manuscript states its principal conclusions were formally verified in Lean 4 in an accompanying artifact (dcass-121/d3-lean-verification) unpacked as a submission archive with no leanblueprint/LeanArchitect sync and no Challenge/Solution spec-lock (the scraper's has_solution_file flag is a false positive from *Resolution*.lean files). Both the paper and README map manuscript statements (Target 4.10 / Theorem C, Theorem A with a cruder explicit constant, Corollary B dual parameters, genus-ratio limit) to Lean endpoints while explicitly documenting omitted secondary results (Schur fullness, closed genus formula, general-field extension), characteristic of post-hoc formalization.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `dcass-121/d3-lean-verification` (github):** `.lean` files=2486, LoC=200335, theorems=8473, defs=5031, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.31.0`, ci=`[]`

#### [2611.05243](https://arxiv.org/abs/2611.05243) — Logarithmic Regret for Alternating Mirror Descent
- **Primary / Target Cats:** `cs.LG` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['GPT-5.6 Sol', 'GPT-6 Astra'])
- **Evidence:** The paper explicitly states that the mathematical proof was developed using GPT-5.6 Sol and the Lean proof was formalized using GPT-6 Astra, with authors verifying proofs and revising the manuscript. The public repo contains no blueprint sync or Challenge/Solution spec-lock tooling, and uses post-hoc correspondence/audit documentation (CORRESPONDENCE.md and AltOMDAudit/README.md) mapping all 15 manuscript labels to Lean declarations.
- **Risk flags:** []
- **Repo `CoffeeAndConvexity/AltOMD-Lean` (github):** `.lean` files=79, LoC=11204, theorems=644, defs=199, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`[]`

#### [2611.05136](https://arxiv.org/abs/2611.05136) — Information Loss Is All You Need: $TC^0$ Pseudorandomness from Worst-Case Lattices
- **Primary / Target Cats:** `cs.CC` / ['cs.CR'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` ([])
- **Evidence:** Paper manuscript was written/checked by the human author while the Lean 4 formalization of Theorem 9.9 (thm:df-constructive-aft) was generated separately by AI without editing LaTeX files ('No manuscript files were edited by this proof task' in provenance/upstream-manuscript-manifest.json) and without leanblueprint, LeanArchitect, Verso Blueprints, or comparator/Challenge.lean spec-lock tooling; alignment with concurrent manuscript edits was tracked manually via SHA-256 manifests.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `qianchen92/aft-lean-theorem99` (github):** `.lean` files=1794, LoC=219688, theorems=11051, defs=6431, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0-rc1`, ci=`[]`

#### [2611.04876](https://arxiv.org/abs/2611.04876) — Leakage-Resilient Computation via Matrix Refreshing
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P4_speclock_solve_distill` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT'])
- **Evidence:** `version-1.0/lean/comparator.json` locks `Proofs.ReferenceClaims` (importing `Refreshing.lean`, `Compiler.lean`, `EfficientSimulation.lean`, whose 3 main theorems and 38 certificates are deliberately stubbed with `by sorry`) against `Proofs.ProvedClaims` (complete sorry-free proofs under `Proofs/`), verified via `lake comparator --paranoid` (permitting only `propext`, `Quot.sound`, `Classical.choice`) and `scripts/check_lean_proof_layout.py`, accompanied by `annotated-specifications.pdf`; the paper explicitly states "The Lean formalization was done by ChatGPT" and that the authors iterated with the AI to simplify proofs and write the paper.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `sdziembowski/MatrixRefresh` (github):** `.lean` files=417, LoC=81481, theorems=3285, defs=1933, sorry=41, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.04561](https://arxiv.org/abs/2611.04561) — Distributed LTL Synthesis under Arbitrary Message Adversaries
- **Primary / Target Cats:** `cs.DC` / ['cs.DC', 'eess.SY'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Codex', 'Claude', 'GPT-6'])
- **Evidence:** Authors state they developed the mathematical characterization without AI, had an initial AI-assisted Lean/LaTeX exploration, then wrote a new manuscript from scratch without reusing the AI LaTeX draft, and 'Finally, we used AI again to formalize in Lean the statements and proofs as written in this paper.' Formalization supplements the paper via clickable badges to Paper/*.lean wrappers checked by scripts/check_paper_links.py, with no leanblueprint/LeanArchitect sync.
- **Risk flags:** ['Mode10_ProofBloat', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `BioDisCo/distributed_synthesis_lean` (github):** `.lean` files=2395, LoC=929448, theorems=20193, defs=20454, sorry=0, axiom=0, native_decide=2, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0`, ci=`[]`

#### [2611.02256](https://arxiv.org/abs/2611.02256) — Exact Shortest Paths and Maximum Flow in Planar Networks in the CONGEST Model
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude Opus 5.5'])
- **Evidence:** The paper and working notes (notes/NOTES.md, notes/LEMMA15.md, etc.) develop the CONGEST algorithms and proofs informally on paper, while lean/SsspFlow/ formalizes only selected supporting mathematical lemmas (Virtual Source, Dual Distance, discretized boosting, plus auxiliary recursion/tools) with explicit 'Not formalized' notes and no blueprint/LeanArchitect or Challenge/Solution spec-lock tooling. README.md explicitly states Claude Opus 5.5 was used to search literature, develop/check proofs, write scripts and the Lean formalization, and draft text.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs` (github):** `.lean` files=14, LoC=2191, theorems=132, defs=52, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc1`, ci=`[]`

#### [2611.02169](https://arxiv.org/abs/2611.02169) — Split Cuts in Fixed Integer Dimensions
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['OpenAI ChatGPT'])
- **Evidence:** The paper lists no public repositories or URLs and mentions Lean only once in an 'AI use disclosure' stating that the authors used OpenAI's ChatGPT to assist with 'checking of proofs and calculations including Lean verification', leaving the formalization workflow and verification scope unspecified.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.02057](https://arxiv.org/abs/2611.02057) — Paying for Fractional Error: Tight Constant-Round Approximation of Covering Problems with Short Broadcasts
- **Primary / Target Cats:** `cs.DS` / ['cs.DC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** The paper states in Section J that all 81 named results were formalized in Lean 4 across 1612 modules and that AI models (Claude in latex_signals) were used for independent reviews and Lean formalization. The repo has no blueprint directory, LeanArchitect annotations, or comparator Challenge/Solution lock (has_blueprint_dir=false, has_challenge_file=false, tex_file_count=0), instead using a post-hoc statement-level correspondence map (PaperIndex.lean, docs/correspondence.md, verification/statement-map.json).
- **Risk flags:** ['Mode6_SorryOrAxiomOrNativeDecide', 'Mode10_ProofBloat', 'Mode12_ProcessOpacity']
- **Repo `wwawrzy/paying-for-fractional-error-lean` (github):** `.lean` files=1617, LoC=166354, theorems=8757, defs=3745, sorry=0, axiom=10, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0`, ci=`[]`

#### [2611.01761](https://arxiv.org/abs/2611.01761) — Computation in Anonymous Directed Dynamic Networks: Exact Worst-Case Termination Time and Network-Wise Intractability
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Role:** `pure_tcs_or_math`
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT-6 Astra'])
- **Evidence:** paper.tex explicitly discloses using ChatGPT-6 Astra to produce Lean proofs for all results in the paper; the repo links existing numbered statements in paper.tex to Lean declarations post-hoc via claims.json and render_correspondence.py without leanblueprint, LeanArchitect, or Challenge/Solution spec-lock tooling.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `gadiluna/ADDN_lean` (github):** `.lean` files=2104, LoC=158351, theorems=6418, defs=6005, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.0`, ci=`[]`

#### [2611.01384](https://arxiv.org/abs/2611.01384) — Benign population landscapes do not transfer to empirical risk minimization in nonsmooth optimization
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Role:** `engineering_math_proof`
- **Paradigm:** `P0_opaque_or_unspecified` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['Claude', 'GPT-5', 'GPT-6'])
- **Evidence:** The paper states that an accompanying Lean formalization verifies identity (C.22), correlation bounds, angular series/remainder estimates, and uniform bound (C.31), while main moment theorems, covariance reduction, and numerical enclosures are outside Lean; however, the linked repo PenghaoWang1225/Phase-Retrieval is inaccessible (accessible: false) and no authoring workflow details are provided in the evidence.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {'citation_or_discussion': 19, 'formal_contributed': 12, 'false_positive': 3}
- **Tool categories (contributed):** {'ITP': 5, 'model_checker': 4, 'smt_sat': 2, 'protocol_verifier': 1}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Coq/Rocq` | 2 |
| `Z3` | 2 |
| `PRISM` | 2 |
| `tla_plus` | 2 |
| `SPIN` | 1 |
| `Promela` | 1 |
| `nuXmv` | 1 |
| `NuSMV` | 1 |
| `ROCQ` | 1 |
| `Coq` | 1 |
| `Tamarin` | 1 |
| `Rocq` | 1 |
| `Isabelle/HOL` | 1 |
| `Rocq / Coq` | 1 |
| `Verus` | 1 |
| `isabelle` | 1 |
| `TLA+` | 1 |
| `TLAPS` | 1 |

### Confirmed Beyond-Lean Papers

- **[2611.23811](https://arxiv.org/abs/2611.23811)** (`cs.DC`, `ITP`, tools=['Coq/Rocq']): Stephen: Verifying Sequencer-Aided Coordination Systems with Cross-View Prophecy — The paper formally verifies implementations of sequencer-aided coordination systems (NOPaxos, Corfu, LazyLog) using machine-checked proofs in Rocq/Grove.
- **[2611.23021](https://arxiv.org/abs/2611.23021)** (`eess.SY`, `smt_sat`, tools=['Z3']): Satisfiability Modulo Theories for Robust Synthesis of Signal Temporal Logic Specifications — Introduces a Satisfiability Modulo Theories (SMT) based encoding and synthesis method for Signal Temporal Logic (STL) specifications in robotic systems.
- **[2611.22408](https://arxiv.org/abs/2611.22408)** (`cs.CR`, `model_checker`, tools=['SPIN', 'Promela']): From Attack Tree to Model Checker: Binding CAPEC Patterns to Verify Robotic System Security — The paper presents a pipeline that mechanises the transition from CAPEC attack patterns to formal attacker models, emitting LTL properties and Promela models verified using SPIN.
- **[2611.22403](https://arxiv.org/abs/2611.22403)** (`cs.SE`, `model_checker`, tools=['nuXmv', 'NuSMV', 'ROCQ', 'Coq']): BehaVerify: A Formal Verification Tool for Behavior Trees — BehaVerify presents a verification toolbox for behavior trees that encodes into nuXmv for formal verification and incorporates tools like ROCQ.
- **[2611.20671](https://arxiv.org/abs/2611.20671)** (`cs.CR`, `protocol_verifier`, tools=['Tamarin']): MASTA: A Feedback-Scheduled Multi-Agent System for End-to-End Tamarin Modeling and Analysis — MASTA uses a multi-agent system to end-to-end model and verify security protocols using the Tamarin theorem prover.
- **[2611.18463](https://arxiv.org/abs/2611.18463)** (`cs.CR`, `ITP`, tools=['Rocq']): VellSSLH: Sound Type-Guided Selective Speculative Load Hardening for LLVM IR — VellSSLH: Sound Type-Guided Selective Speculative Load Hardening for LLVM IR, mechanized and proved in Rocq.
- **[2611.18055](https://arxiv.org/abs/2611.18055)** (`cs.PL`, `ITP`, tools=['Coq/Rocq']): DeCompCert: A Verified Decompiler for CompCert-Generated AArch64 — DeCompCert is a Rocq-verified decompiler for AArch64 assembly generated by CompCert.
- **[2611.12252](https://arxiv.org/abs/2611.12252)** (`cs.CR`, `model_checker`, tools=['PRISM']): Lessons Not Learned: Why Cross-Chain Bridges Keep Losing Billions the Same Way — The paper compiles security posture and rate-limit models into the PRISM model checker to perform exhaustive state-space search and bound bridge hack losses.
- **[2611.11506](https://arxiv.org/abs/2611.11506)** (`cs.CR`, `ITP`, tools=['Isabelle/HOL']): On the Relative Security of Prompt Injection: Mechanised Definitions, Defences and Verdicts for LLM Agents — Mechanised definitions, defences and verdicts for LLM agents proven or refuted in Isabelle/HOL.
- **[2611.07919](https://arxiv.org/abs/2611.07919)** (`cs.DC`, `smt_sat`, tools=['Z3']): Modular Parameterized Model Checking of Threshold-Based Distributed Algorithms — The paper introduces a modular parameterized model checking approach for threshold-based distributed algorithms, implemented and evaluated using the Z3 SMT solver.
- **[2611.05695](https://arxiv.org/abs/2611.05695)** (`cs.PL`, `ITP`, tools=['Rocq / Coq']): Demystifying Information Flow Downgrading using the Real--Ideal Paradigm — Demystifies information flow downgrading using the real-ideal paradigm and fully formalizes the results using the Rocq theorem prover.
- **[2611.02858](https://arxiv.org/abs/2611.02858)** (`cs.CR`, `model_checker`, tools=['PRISM']): Evaluating autonomous self-healing against persistent cyber-attacks — The paper uses the PRISM model checker to calculate steady-state probabilities and evaluate autonomous self-healing against cyber-attacks.