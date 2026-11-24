# Phase 0 Deterministic Probe Summary

- **Date window (submitted):** `2026-11-01T00:12:00Z` to `2026-11-19T23:54:20Z`
- **Total unique papers ingested:** 1339
- **Total papers screened:** 1339 (`html`: 1247, `pdf`: 89, `failed`: 3)
- **Lean strong hits (full text):** 31 *(vs. metadata-only: 12)*
- **Lean contextual-only hits:** 5
- **Confirmed public Lean GitHub repos found:** 0

## Breakdown by Target arXiv Category

| Category | Papers | Lean Strong | Lean Ctx | Other ITP | Model Checker | Protocol Verifier | SMT/SAT |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cs.CE` | 146 | 0 | 0 | 0 | 0 | 0 | 0 |
| `cs.GT` | 166 | 14 | 15 | 0 | 0 | 0 | 0 |
| `cs.PF` | 94 | 0 | 0 | 1 | 0 | 0 | 2 |
| `eess.AS` | 134 | 0 | 0 | 1 | 0 | 0 | 0 |
| `eess.IV` | 175 | 0 | 0 | 1 | 0 | 0 | 1 |
| `math.DS` | 360 | 15 | 18 | 1 | 0 | 0 | 1 |
| `physics.flu-dyn` | 278 | 2 | 2 | 1 | 0 | 0 | 0 |

## Beyond-Lean Tool Counts (Deterministic Full-Text Hits)

| Group : Tool | Papers |
| :--- | ---: |
| `itp:coq_rocq` | 5 |
| `smt_sat:smt_general` | 4 |
| `smt_sat:z3_cvc` | 2 |

## Lean Strong Hits (31 papers)

### [2611.24920](https://arxiv.org/abs/2611.24920) — The Optimal Competitive Ratio for Subadditive Online Combinatorial Auctions is Less Than 1/2
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-18` | **Source:** `html`
- **Comment:** 4 pages
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/GO-EPFL/subadditive-online-combinatorial-auctions
  - *lean_prover_phrase:* `t most three buyers. Thus four is the smallest number of buyers for which a guarantee can fail. A stronger upper bound. A construction with a growing number of buyers gives an upper bound of approximately , strictly below . The proof and Lean formalization are available in the GitHub repository. 2 The instance For inte`

### [2611.22216](https://arxiv.org/abs/2611.22216) — Settling the Time and Structural Complexity of Bertrand Networks
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-17` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/hajiaghayi/Bertrand
  - *lean_prover_phrase:* `ions and critically verifying Astra’s responses across iterative exchanges. OpenAI Astra was also used in drafting and revising the manuscript via detailed prompts from the authors, with Gemini Argon assisting in editing parts of the text. Lean formalization can be found in link. References Anshelevich and Sekar (2015)`

### [2611.20966](https://arxiv.org/abs/2611.20966) — Finite-order exponential mixing does not imply the central limit theorem for unique equilibrium states
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-16` | **Source:** `html`
- **Comment:** 39 pages, 0 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lakefile', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/Manzatto/equilibrium-states-finite-order-mixing-clt-counterexample
  - *lean_version:* `f)=0$. The system $(T,\mu)$ is exponentially mixing of order $R$ but not of order $R+1$ for H\"older observables, and $n^{-1/2}\sum_{i=0}^{n-1}f\circ T^i$ does not satisfy the central limit theorem. The main results have been formalised in Lean 4. 39 pages, 0 figures Finite-order exponential mixing does not imply the c`
  - *mathlib:* `ii) gives (iv). ∎ ∎ Proof of Corollary 1.2. Apply Theorem A to , whose equilibrium states are the measures of maximal entropy. ∎ 9. Lean formalisation Theorems A, 7.3 and 8.5 and Corollary 1.2 have been formalised in Lean 4.35.0 using Mathlib. The source code is available at https://github.com/Manzatto/equilibrium-stat`
  - *lakefile:* `nt contains no sorry placeholders or additional axioms. An audit of the project declarations verifies that their axiom dependencies are confined to propext, Classical.choice and Quot.sound. The compiler and dependency versions are fixed by lean-toolchain and lake-manifest.json. Compilation and axiom dependencies can be`

### [2611.20890](https://arxiv.org/abs/2611.20890) — Nearly Settling the Complexity of Connected $\varepsilon$-Envy-Free Cake Cutting
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-16` | **Source:** `html`
- **Comment:** 66 pages, 2 figures. We corrected the attribution in the seven-agent hardness proof to make explicit its use of the theorem of Hollender, Maystre and Risse that the Jordan Curve problem is UEOPL-hard. We also clarified the attribution of earlier algorithms and reductions and the assumptions behind prior query bounds. The main results are unchanged
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/SimonWMackenzie/connected-envy-free-lean, https://github.com/harfe/fixed-point-theorems-lean4
  - *lean_version:* `ship order. The standard approximate PPAD-membership result completes the classification, giving PPAD completeness from thirteen agents. Section 5 presents these computational reductions together. 1.3 Formal verification The accompanying Lean 4 development [29], using Mathlib [28], verifies the query theorems 3.1, 3.3,`
  - *mathlib:* `imate PPAD-membership result completes the classification, giving PPAD completeness from thirteen agents. Section 5 presents these computational reductions together. 1.3 Formal verification The accompanying Lean 4 development [29], using Mathlib [28], verifies the query theorems 3.1, 3.3, 4.1 and A.1. It also verifies `
  - *lean_prover_phrase:* `rs, allocation enumerators and separate implementations of proposed algorithms, and compiled and checked the manuscript. Much of the proof checking was also performed by AI systems assigned separate review tasks. The systems also wrote the Lean formalisation described in Section 1.3. 1 Introduction Cake cutting is a ce`

### [2611.19243](https://arxiv.org/abs/2611.19243) — Veech dichotomy for specific covering surface over Veech surface
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-14` | **Source:** `html`
- **Comment:** 9 pages, 2 figures
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/Ryan-Hao-Jan/Veech-dichotomy-for-cover
  - *lean_version:* `r periodic points and belong to . ∎ Acknowledgments The author would like to sincerely thank Professor Yitwah Cheung for helpful suggestions and discussions on possibility to construct more general surfaces satisfying Veech dichotomy. A Lean 4 formalization of Theorem 1, using mathlib, is available in the accompanying `
  - *mathlib:* `owledgments The author would like to sincerely thank Professor Yitwah Cheung for helpful suggestions and discussions on possibility to construct more general surfaces satisfying Veech dichotomy. A Lean 4 formalization of Theorem 1, using mathlib, is available in the accompanying code repository, together with instructi`

### [2611.17292](https://arxiv.org/abs/2611.17292) — The Submodular Secretary Problem: Tight $1-1/e$ for Monotone Objectives, and Strictly Between $1/e$ and $1/2$ in General
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Matched Lean Signals:** `['lean_verifiers', 'lean_version']`
  - *lean_version:* `aude Fable 5.2, working under the direction of the authors, and the manuscript was drafted with the assistance of Claude. The numerical constants in this paper were verified by computer in exact rational or directed-rounding arithmetic. A Lean 4 formalization, written by GPT-6 Astra, proves every result of this paper. `
  - *lean_verifiers:* `ounding arithmetic. A Lean 4 formalization, written by GPT-6 Astra, proves every result of this paper. It uses no axioms beyond Lean’s standard ones, except that some of the finite numerical certificates in the appendices are checked with native_decide, which also trusts Lean’s compiler. References [ABH+26] Hamed Abdi,`

### [2611.17277](https://arxiv.org/abs/2611.17277) — On $L^p$ density of self-similar measures and Bernoulli convolutions
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Comment:** 18 pages
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase']`
- **Artifact URLs:** https://github.com/ckkogler/l1-to-lp-supplementary-material, https://github.com/ckkogler/lpselfsimilar-lean
  - *lean_prover_phrase:* `rem 1.1. Various simplifications led to Lemma 2.1. Realising that Theorem 1.1 is quantitative, numerous conversations with GPT-6 Astra led to Theorem 1.2. The paper is written by the authors and we take responsibility for its correctness. Lean Formalization GPT-6 Astra formalized all results from this paper and all nec`
  - *in_lean_phrase:* `we apply the quantitative proof method of the latter result to establish explicit examples of Bernoulli convolutions with a continuous density going beyond the only previously known case of Garsia numbers. All new results of this paper are formalized in Lean. A contracting similarity on is a map of the form with , a or`

### [2611.17223](https://arxiv.org/abs/2611.17223) — Combinatorial Bernoulli Factories with Polynomially Many Coins
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version']`
- **Artifact URLs:** https://github.com/radniazadeh/bernoulli-poly.git
  - *lean_version:* `conversations with ChatGPT Astra, Claude Opus and Gemini Argon. The authors then substantially rewrote the proofs with the help of these models, and take full responsibility for the content of this work. The results were also formalized in Lean 4, and the formalization is available at https://github.com/radniazadeh/ber`
  - *in_lean_phrase:* `n a series of conversations with ChatGPT Astra, Claude Opus and Gemini Argon. The authors then substantially rewrote the proofs with the help of these models, and take full responsibility for the content of this work. The results were also formalized in Lean 4, and the formalization is available at https://github.com/r`

### [2611.15751](https://arxiv.org/abs/2611.15751) — Shift-Symmetric Configurations in $d$-Dimensional Cellular Automata: Enumeration, Bounds, Irreversibility, and Detection
- **Primary / Target Cats:** `math.CO` / ['math.DS'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/peterbanda/d-dim-shift-symmetry-in-ca
  - *lean_version:* `ric inputs. We give a detection algorithm with worst-case cost $O(n^d\sum_{p\mid n}\frac{p^d-1}{p-1})$ and an average-case analysis, exact for each subgroup test. The mathematical content of every numbered statement is formally verified in Lean 4, and the correspondence between each theorem, lemma, proposition, and cor`
  - *mathlib:* `d in research/experiments/README.md. 11 Formal verification The mathematical content of every numbered statement of Sections 2–10 and Appendices A and B has been formally verified in the Lean 4 proof assistant (v4.33.0-rc1) on top of the mathlib library: that of all definitions, lemmas, theorems, propositions, corollar`
  - *lean_prover_phrase:* `is exact precisely when the side length is prime, and as the dimension grows, the smallest prime factor of the side length alone sets the rate per cell at which such patterns become rare. All theorems were also verified by computer in the Lean proof assistant. Contents 1 Introduction 2 Model 3 Preliminaries 4 Enumerati`

### [2611.15711](https://arxiv.org/abs/2611.15711) — Beyond Worst-Case Online Algorithms via Input Subsampling
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Comment:** Accepted to ITCS 2027
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_verifiers', 'mathlib']`
- **Artifact URLs:** https://github.com/relyt871/BWCA-Online-Lean
  - *mathlib:* `1) (Set.Ioo 0 1) 7. Existence and uniqueness of . Lean proves that the magnitudes in the alternating series for decrease throughout . Even and odd finite sums therefore give rigorous lower and upper bounds. It combines these bounds with Mathlib’s enclosure of and exact rational arithmetic to prove opposite signs at two`
  - *lean_verifiers:* `y of this repository contains a standalone Lean project. Build instructions are given in the repository’s root README.md. All file paths below are relative to the repository root. Some finite rational computations are checked using Lean’s native_decide tactic. Every such application concerns an explicit rational equali`
  - *lean_prover_phrase:* `ounds D.2 Proof of Theorem E Proofs for the Arbitrary-Algorithm Tight Threshold E.1 Reducing via the weighted cost E.2 Non-negativity of the weighted cost Defining . E.3 Bounding and E.4 Proof of Theorem Positive direction. F Lean Proofs F.1 Lean certificates for Lemma 1. The endpoint-safe definition of . 2. The functi`

### [2611.14974](https://arxiv.org/abs/2611.14974) — Who Moved the Frontier? Paying Open Frontier Challenges with Free Identities
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/KellerJordan/modded-nanogpt, https://github.com/Layr-Labs/quantum-safe-bitcoin-challenge, https://github.com/karpathy/autoresearch, https://github.com/mutable-state-inc/autoresearch-at-home, https://github.com/proximity-prize/proximity-prize
  - *lean_prover_phrase:* `later, an operator keeps what it earned, as protection against front-running [16] would keep an earlier trade. Challenge Scorer; who draws the noise Open as run? Rule in use Rule our results would support better.codes [22] exact: a Lean proof checker O1 ?, O2 yes, O3 no discretionary awards once pay is committed: per-s`

### [2611.14756](https://arxiv.org/abs/2611.14756) — Stability of equilibria in discrete-time modified-gradient systems and the multivariate breeder's equation
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 16 pages, 5 figures, 2 tables. Lean 4 formalization of the main results: https://github.com/magbenji/discrete-modified-gradient-lean (doi:10.5281/zenodo.24118844)
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.24118844, https://github.com/magbenji/discrete-modified-gradient-lean
  - *lean_version:* `l. As further application of our results, the same conditions apply to the mean update of Gaussian evolutionary optimization algorithms, in which the covariance of the search population plays the role of $G$. 16 pages, 5 figures, 2 tables. Lean 4 formalization of the main results: https://github.com/magbenji/discrete-m`
  - *mathlib:* `basin of attraction results of [32]. Disclosure statement The author reports there are no competing interests to declare. Data availability statement No new data were generated in this study. Machine-checked proofs, in Lean 4 with the Mathlib library, of Lemma 4.1, Theorem 5.1, Corollary 5.2 and Theorem 6.1 are openly `

### [2611.14586](https://arxiv.org/abs/2611.14586) — Finite-Cadence Refresh Equilibria for Streaming Prior-Anchored Ridge: A Closed-Form Forgetting Window and Spectral Correction
- **Primary / Target Cats:** `stat.ML` / ['cs.GT'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 67 pages, 7 figures. Lean 4 formalization and code: [https://doi.org/10.5281/zenodo.23768172](https://doi.org/10.5281/zenodo.23768172)
- **Matched Lean Signals:** `['in_lean_phrase', 'lakefile', 'lean_version', 'mathlib']`
- **Artifact URLs:** http://github.com/jax-ml/jax, https://doi.org/10.5281/zenodo.23768172, https://doi.org/10.5281/zenodo.593816
  - *lean_version:* `uals. On a 27-configuration grid the calibrated window opens on drift without divergence, and the grid defaults transfer to an hourly electricity stream and to BCI IV 2b. The core algebra, refresh chain, and regret bounds are formalized in Lean 4. 67 pages, 7 figures. Lean 4 formalization and code: [https://doi.org/10.`
  - *mathlib:* `to their active subspace (Corollary 19). 3. A formalized core. The algebraic core, the finite-cadence refresh chain, the OGD and Hedge regret bounds, and the coupled contraction are formalized in Lean 4 (de Moura and Ullrich, 2021; The mathlib Community, 2020): 85 declarations, no sorry, and only the three standard axi`
  - *lakefile:* `headline theorems’ axiom dependencies are logged in theory/lean/axioms.log, regenerated by theory/lean/print_axioms.sh, all resting only on propext, Classical.choice, and Quot.sound. C.3 Build Recipe The project ships its own theory/lean/lakefile.toml, lean-toolchain, lake-manifest.json, and root import module; theory/`

### [2611.12862](https://arxiv.org/abs/2611.12862) — Quantitative global regularity for Navier--Stokes equations with odd viscosity on the cubic three-torus
- **Primary / Target Cats:** `math.AP` / ['physics.flu-dyn'] | **Submitted:** `2026-11-09` | **Source:** `pdf`
- **Comment:** 79 pages
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/DavetheSlayer/OVNS-Lean, https://github.com/DavetheSlayer/OVNS-Lean/tree/9bd811d918c2387b82f482ce15b7cf6df1ccf3a6
  - *lean_version:* `seven closed forced rectangles. We specify how finite certificates enter the analytic argument and distinguish minimization of a sufficient formula from sharpness for the original equation. All three main theorems are formally verified in Lean 4 with Mathlib. 79 pages QUANTITATIVE GLOBAL REGULARITY FOR NAVIER–STOKES EQ`
  - *mathlib:* `d forced rectangles. We specify how finite certificates enter the analytic argument and distinguish minimization of a sufficient formula from sharpness for the original equation. All three main theorems are formally verified in Lean 4 with Mathlib. 79 pages QUANTITATIVE GLOBAL REGULARITY FOR NAVIER–STOKES EQUATIONS WIT`
  - *lean_prover_phrase:* `of as- sistant Lean 4 with the Mathlib library [8, 32]. Both bounds of Theorem 1.2 and both cases of Theorem 1.3 are included. The formal theorems have no hypotheses beyond the conditions stated above, and their proofs contain no gaps. The Lean kernel accepts them using only the three standard axioms: propositional ext`

### [2611.11805](https://arxiv.org/abs/2611.11805) — Operator Learning of Microstructure-Dependent Internal-Variable Models for Inelastic Homogenization: Approximation and Complexity
- **Primary / Target Cats:** `math.NA` / ['math.DS'] | **Submitted:** `2026-11-09` | **Source:** `html`
- **Comment:** 52 pages, 12 figures, including appendices
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/sgstepaniants/inelastic_hom_learn
  - *lean_version:* `n viscoelasticity and crystal plasticity complement the theory, illustrating the roles of internal-variable dimension and sample complexity in learning homogenized responses from unit-cell data. Theoretical results are formally verified in Lean 4. 52 pages, 12 figures, including appendices Operator Learning of Microstr`
  - *mathlib:* `n an internal-variable Markovian model of the form 1.1 Main Results and Paper Overview In this subsection, we summarize our main results and outline the rest of the paper. We formally verified the theoretical results in Lean 4 [40] using mathlib [41]; details appear below. The formalization and verification instruction`
  - *in_lean_phrase:* `xperiments on viscoelasticity and crystal plasticity complement the theory, illustrating the roles of internal-variable dimension and sample complexity in learning homogenized responses from unit-cell data. Theoretical results are formally verified in Lean 4. 52 pages, 12 figures, including appendices Operator Learning`

### [2611.11641](https://arxiv.org/abs/2611.11641) — Spectral Stability, Fatou Basin Contraction, and Machine-Checked Multipliers in Holomorphic Extensions of Generalized Syracuse Dynamics
- **Primary / Target Cats:** `cs.LO` / ['math.DS'] | **Submitted:** `2026-11-08` | **Source:** `html`
- **Comment:** 3 pages, 3 tables; includes ancillary Lean 4 formalization (anc/CollatzAttractor.lean, 20 machine-checked theorems, 0 sorry) and Python verification suite (anc/collatz_complex_core.py, anc/collatz_mass_verifier.py). Companion replication archive: https://doi.org/10.5281/zenodo.24060394 (Concept DOI: https://doi.org/10.5281/zenodo.24060393)
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version']`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.24060393, https://doi.org/10.5281/zenodo.24060394, https://zenodo.org/records/24060394
  - *lean_version:* `lates $B(O_{1,2})$; (4) on $(\mathbb{Z}_2, \mu_{\mathrm{Haar}})$, the 2-adic Lyapunov exponent $\lambda_{\mathrm{Haar}} = \frac{1}{2}\ln(3/4) \approx -0.143841 < 0$ equals $\frac{1}{2}\ln|\mu_f(O_{1,2})|$; and (5) we certify 20 theorems in Lean 4 (anc/CollatzAttractor.lean, 0 sorry). These results establish local Fatou`
  - *in_lean_phrase:* `iversal Cycle Attractiveness and Multiplier Cohomology 4 Closed-Form Koenigs Linearization Curvature Jets 5 Universal Negative Schwarzian Derivative and Fatou–Julia Partition 6 The 2-Adic Haar–Fatou Resonance Identity 7 Machine-Checked Formalization in Lean 4 References License: arXiv.org perpetual non-exclusive licens`

### [2611.11424](https://arxiv.org/abs/2611.11424) — The Query Complexity of Envy-Free Division: Cake, Chores, and Mixed Resources
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-08` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/farhadi94/envy-free-division
  - *lean_version:* `at every sharper auxiliary ledger in the paper is formalized verbatim. Its endpoint manifest identifies the public Lean statements corresponding to the four theorems; those statements record the precise hypotheses. The source package pins Lean 4.35.0, mathlib, and the fixed-point library used for the chore construction`
  - *mathlib:* `per auxiliary ledger in the paper is formalized verbatim. Its endpoint manifest identifies the public Lean statements corresponding to the four theorems; those statements record the precise hypotheses. The source package pins Lean 4.35.0, mathlib, and the fixed-point library used for the chore construction. The verifie`
  - *lean_prover_phrase:* `Proceedings of the Twenty-Seventh International Joint Conference on Artificial Intelligence, pp. 226–232. External Links: Document, Link Cited by: §4. [9] A. Farhadi and M. Hajiaghayi (2026) The query complexity of envy-free division: Lean proofs and supporting materials. Note: Software and verification artifact Extern`

### [2611.09615](https://arxiv.org/abs/2611.09615) — Contextual Search and Bilateral Trade with a Trace-Square-Root Potential
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-06` | **Source:** `html`
- **Matched Lean Signals:** `['lean_version']`
- **Artifact URLs:** http://github.com/renatoppl/trace-square-root
  - *lean_version:* `or mean and covariance proxies. The authors have substantially rewritten the proofs (albeit with some help from Gemini, Claude, and ChatGPT) and take full responsibility for the content of this work. All the proofs have been formalized in Lean4 and can be found at this url. References [ARS14] K. Amin, A. Rostamizadeh, `

### [2611.09066](https://arxiv.org/abs/2611.09066) — Hausdorff dimension of planar box-like self-affine sets with rotations
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-06` | **Source:** `html`
- **Comment:** 58 pages, 2 figures, v2: Included reference to Palomar upload
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/sascha2718/lean-diagonal-antidiagonal
  - *lean_version:* `s in the paper. The authors have checked every argument themselves and every reference against the source, and take full responsibility for the content of this paper. Lean formalisation. The paper is accompanied by a formalisation in the Lean 4 theorem prover over Mathlib. Every numbered statement is recorded in the de`
  - *mathlib:* `have checked every argument themselves and every reference against the source, and take full responsibility for the content of this paper. Lean formalisation. The paper is accompanied by a formalisation in the Lean 4 theorem prover over Mathlib. Every numbered statement is recorded in the development, and every numbere`
  - *lean_prover_phrase:* `itions on which they depend, faithfully express the corresponding results in the paper. The authors have checked every argument themselves and every reference against the source, and take full responsibility for the content of this paper. Lean formalisation. The paper is accompanied by a formalisation in the Lean 4 the`

### [2611.08591](https://arxiv.org/abs/2611.08591) — Conley index theory for asymptotically autonomous systems and UV-to-IR connections
- **Primary / Target Cats:** `math-ph` / ['math.DS'] | **Submitted:** `2026-11-05` | **Source:** `html`
- **Comment:** 65 pages, 6 figures. Lean 4 formalization is available at https://github.com/stacks-ai/papers/tree/main/conley-index-dynamical-systems
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version']`
- **Artifact URLs:** https://github.com/stacks-ai/papers/tree/main/conley-index-dynamical-systems
  - *lean_version:* `low of the $(4+\epsilon)$-dimensional $O(N)$ model with cubic anisotropy, a shift of $N$ through $N=4$ has vanishing transport map, but a driven connection and a nonzero connecting homomorphism detect it at every rate. 65 pages, 6 figures. Lean 4 formalization is available at https://github.com/stacks-ai/papers/tree/ma`
  - *lean_prover_phrase:* `); Writing – review & editing (supporting). Mauricio M. Martinez: Validation (supporting); Writing – review & editing (supporting). Data Availability The data that support the findings of this study are available within the article. The Lean formalization of the results is openly available at https://github.com/stacks-`

### [2611.07818](https://arxiv.org/abs/2611.07818) — Thurston algorithm for real entire maps: existence and uniqueness
- **Primary / Target Cats:** `math.DS` / ['math.DS'] | **Submitted:** `2026-11-05` | **Source:** `html`
- **Comment:** V2 contains a new appendix showing that the proof also gives existence for certain families of maps which are only complex analytic on a neigbourhood of the real line
- **Matched Lean Signals:** `['lean_version']`
  - *lean_version:* `d any remaining errors. AI output was not used as a mathematical source; external results are attributed to the cited literature. I would like to also thank Bernat Bassols-Cornudella, who helped me to formalise the first ArXiv version via Lean 4, conditional on 25 classical statements. Please email me if you would like`

### [2611.07395](https://arxiv.org/abs/2611.07395) — Rigorously Certified Neural-Network Computation of Nonlinear Water Waves at Near-Machine Precision
- **Primary / Target Cats:** `math.AP` / ['physics.flu-dyn'] | **Submitted:** `2026-11-05` | **Source:** `html`
- **Comment:** 29 pages, 6 figures
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_verifiers', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/jax-ml/jax, https://github.com/michalshavitNYU/Rigorously-certified-water-waves, https://github.com/michalshavitNYU/Rigorously-certified-water-waves/blob/main/docs/supplementary_computer_assisted_accuracy_proof.pdf, https://github.com/michalshavitNYU/Rigorously-certified-water-waves/tree/main, https://github.com/michalshavitNYU/Rigorously-certified-water-waves/tree/main/Julia
  - *lean_version:* `iments and new solutions 2.2 Second-stage training and a near-machine-precision candidate 2.3 Certified residual estimates and formal verification in Lean 2.3.1 Rigorous certification by interval arithmetic 2.3.2 Formal verification in Lean 3 Discussion 4 Methods 4.1 PINN architecture 4.1.1 Neural representation 4.1.2 `
  - *mathlib:* `ved only at finitely many numerical evaluation points. Third, we formally verify the mathematical structure of the certification argument in Lean de Moura and Ullrich (2021), a proof assistant and functional programming language, and the mathlib library The mathlib Community (2020). At this level of accuracy, the numer`
  - *lean_verifiers:* `nometric modes and commutation with differentiation, aliasing estimates, product and composition derivative bounds, Taylor-record semantics, and the Taylor grid-to-continuum argument. The publication proof contains no sorry placeholders or sorryAx dependency. The Lean source code, certificate data and build instruction`

### [2611.06896](https://arxiv.org/abs/2611.06896) — Online Edge-Weighted Matching Beyond 0.55
- **Primary / Target Cats:** `cs.DS` / ['cs.GT'] | **Submitted:** `2026-11-04` | **Source:** `html`
- **Matched Lean Signals:** `['lean_version']`
- **Artifact URLs:** https://github.com/farhadi94/online-edge-weighted-matching
  - *lean_version:* `d dependency in requirements.txt. Both tournament runs must report PASS for every , with chords for and for . Run the programs with Python assertions enabled. The formal main theorem is in research/lean/tournament1000/Main1000.lean. With Lean 4.19.0 and the pinned dependencies installed, run make lean-main to compile i`

### [2611.06106](https://arxiv.org/abs/2611.06106) — PCF All The Way Down
- **Primary / Target Cats:** `math.AG` / ['math.DS'] | **Submitted:** `2026-11-04` | **Source:** `pdf`
- **Comment:** PALOMAR-2026-10-30-000004 v1
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'leanprover', 'mathlib']`
- **Artifact URLs:** https://github.com/leanprover-community/, https://github.com/leanprover-community/mathlib4/tree/56a005855ea17e0b0958f73ec801ae140b0a1679, https://github.com/leanprover/lean4/releases/tag/v4.35.0, https://github.com/sympy/sympy/releases/tag/1.13.2, https://github.com/tdupu/
  - *lean_version:* `ent shortened text was checked for proof dependencies, references, and LaTeX compilation. A compiled PDF cannot verify a mathematical assertion. A.8. Formalization. Theorem 1.1 (equivalently Theorem 8.1) and Corollary 8.2 are formalized in Lean 4 [lean, prover paper], version v4.35.0, against Mathlib [mathlib, source r`
  - *mathlib:* `references, and LaTeX compilation. A compiled PDF cannot verify a mathematical assertion. A.8. Formalization. Theorem 1.1 (equivalently Theorem 8.1) and Corollary 8.2 are formalized in Lean 4 [lean, prover paper], version v4.35.0, against Mathlib [mathlib, source revision 56a005855ea1] at tag v4.35.0. The paper-facing `
  - *leanprover:* `ent singularities and Hirzebruch–Jung resolutions, Author-hosted notes, Example 1.2. [stacks] The Stacks Project Authors, Stacks Project, https://stacks.math.columbia.edu, 2018. [mathlib] The mathlib Community, mathlib4, https://github.com/leanprover-community/ mathlib4/tree/56a005855ea17e0b0958f73ec801ae140b0a1679, 20`

### [2611.05243](https://arxiv.org/abs/2611.05243) — Logarithmic Regret for Alternating Mirror Descent
- **Primary / Target Cats:** `cs.LG` / ['cs.GT'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/CoffeeAndConvexity/AltOMD-Lean
  - *lean_prover_phrase:* `our assumptions hold for the negative entropy regularizer, thereby obtaining logarithmic regret for the alternating multiplicative weights updates algorithm. The regret bound also yields an duality-gap bound for the averaged strategies. A Lean formalization of the results is available at https://github.com/CoffeeAndCon`

### [2611.04934](https://arxiv.org/abs/2611.04934) — The Complexity of Continuous Contract Design over Polymatroids
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Comment:** 89 pages, 6 figures. The Lean 4 formalization is at https://github.com/philippwarode/contract-design-polymatroids-lean
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version']`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.23895619, https://github.com/philippwarode/contract-design-polymatroids-lean
  - *lean_version:* `ontaining zero. For general convex costs with an exact value and bounded-subgradient oracle, we obtain an oracle approximation scheme using approximate best responses and a supplied lower bound on positive welfare. 89 pages, 6 figures. The Lean 4 formalization is at https://github.com/philippwarode/contract-design-poly`
  - *lean_prover_phrase:* `s D.4 and D.3. It checked statements and proofs with exact rational computations, among them the inequalities of the parameter rule in Appendix C and the constructions of the lower bounds, and it formalized the results of this paper in the Lean proof assistant. It also drafted the remaining text from the authors’ notes`

### [2611.04575](https://arxiv.org/abs/2611.04575) — Polynomial configurations and pointwise averages along Piatetski--Shapiro primes
- **Primary / Target Cats:** `math.CO` / ['math.DS'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Comment:** 15 pages. An AI-assisted Lean development formalizes the deductions in the paper, conditional on eight explicitly documented families of external results. The development is available at https://github.com/HamedMousaviMath/Lean-Formalization-Polynomial-Configurations-and-Pointwise-Averages-Along-Piatetski--Shapiro-Primes
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase']`
- **Artifact URLs:** https://github.com/HamedMousaviMath/Lean-Formalization-Polynomial-Configurations-and-Pointwise-Averages-Along-Piatetski--Shapiro-Primes
  - *lean_prover_phrase:* `f polynomial multiple ergodic averages along the primes, arXiv:2505.15549v2 (2026). [16] H. Mousavi, Polynomial configurations and pointwise averages along Piatetski-Shapiro sequences, arXiv:2609.01847. 2026 Sep 1. [17] H. Mousavi, Lean formalization of polynomial configurations and pointwise averages along Piatetski–S`
  - *in_lean_phrase:* `development formalizes the deductions within the paper conditional on eight explicitly documented external analytic and arithmetic input interfaces. The external results and the remaining source-to-interface translations are not themselves proved in Lean. All mathematical statements, references, arguments, and final wo`

### [2611.04545](https://arxiv.org/abs/2611.04545) — Coercive at the equilibrium, monotone nowhere: exact convergence certificates for learning in first-price auctions
- **Primary / Target Cats:** `cs.GT` / ['cs.GT'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version', 'mathlib']`
- **Artifact URLs:** https://github.com/blubin/firstprice-certificates
  - *lean_version:* `e prior at every by interval arithmetic. For five or more bidders the same limit is conjectured. The exact identities behind these results, the leading-order inequalities of item 3 and the Bloch inequality of item 6 are machine-checked in Lean 4 (Appendix C). How to read the paper. Section 2 places the work and Section`
  - *mathlib:* `ueness of equilibrium points for concave -person games. Econometrica, 33(3):520–534, 1965. [44] Siegfried M. Rump. Verification methods: rigorous results using floating-point arithmetic. Acta Numerica, 19:287–449, 2010. [45] The mathlib Community. The Lean mathematical library. In Proceedings of the 9th ACM SIGPLAN Int`
  - *in_lean_phrase:* `mly in $m$ in the limit exactly when that minimum is positive, with a known rate; for one prior at every $m$ by interval arithmetic. For more bidders the limit is conjectured. The exact identities and leading-order inequalities are machine-checked in Lean. Coercive at the equilibrium, monotone nowhere: exact convergenc`

### [2611.02465](https://arxiv.org/abs/2611.02465) — Pointwise Ergodic Theorems Along $\lfloor p^c\rfloor$ for Every $c>1$
- **Primary / Target Cats:** `math.CA` / ['math.DS'] | **Submitted:** `2026-11-02` | **Source:** `html`
- **Comment:** Lean formalization at https://github.com/anastasiosfragkosmath/Pointwise-Ergodic-Theorems-Along-floor-p-c-Palomar-Submission
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/anastasiosfragkosmath/Pointwise-Ergodic-Theorems-Along-floor-p-c-Palomar-Submission
  - *lean_prover_phrase:* `fractional phase and higher-order discorrelation estimates. The same approach yields almost-everywhere convergence to for the M\"obius-weighted averages along $\left( \lfloor n^c \rfloor \right)_{n \in \mathbb{N}}$ throughout $1<p<\infty$. Lean formalization at https://github.com/anastasiosfragkosmath/Pointwise-Ergodic`

### [2611.02237](https://arxiv.org/abs/2611.02237) — Nonreciprocal Spherical Attention and Retrieval: Sharp Coarsening Clocks and Certified Score Correction
- **Primary / Target Cats:** `cs.LG` / ['math.DS'] | **Submitted:** `2026-11-01` | **Source:** `html`
- **Comment:** 42 pages, 9 figures, 10 tables. Includes mathematical appendices and ancillary reproducibility code
- **Matched Lean Signals:** `['leanprover', 'mathlib']`
- **Artifact URLs:** https://github.com/erikbern/ann-benchmarks, https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
  - *mathlib:* `qchk library checker both succeed. No project-defined axioms or admitted proofs are used. The assumption log explicitly lists standard classical-real and functional-extensionality dependencies. We do not call these proofs axiom-free. Lean/mathlib is a viable alternative for a larger analytic development, with axiom aud`
  - *leanprover:* `tence Transformers. all-MiniLM-L6-v2 model card. Full pinned revision recorded in the dataset manifests. https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2. [26] Lean reference manual. Axioms and trusted assumptions. https://lean-lang.org/doc/reference/latest/Axioms. [27] The Rocq Prover. Core language and k`

### [2611.02167](https://arxiv.org/abs/2611.02167) — On a hybrid trilinear Hilbert transform
- **Primary / Target Cats:** `math.CA` / ['math.DS'] | **Submitted:** `2026-11-01` | **Source:** `html`
- **Comment:** 95 pages, 3 figures
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **Artifact URLs:** https://github.com/openai/math/blob/main/preprints/An-L3-bound-for-the-trilinear-Hilbert-transform-October-5-2026/paper.pdf
  - *lean_prover_phrase:* `ailable in the official release repository. However, the proposed proof is written in an idiosyncratic and non-standard mathematical exposition, and unlike other selected results in the release, it still lacks an official, computer-checked Lean formalization. Furthermore, early independent audits using automated error-`

## Lean Contextual-Only Hits (5 papers — review for recall)

- **[2611.26622](https://arxiv.org/abs/2611.26622)** (`math.CO`) Quasipolynomial pyjamas — `ecke -functions. The initial works generated by OpenAI [19, 20, 21] demonstrated there are no zeros of Dirichlet -functions and finite Hecke -functions over in the half-plane . Subsequently Cureton and Thorner used AxiomProver to prove and `
- **[2611.24787](https://arxiv.org/abs/2611.24787)** (`math.OA`) A Poisson boundary solution to Connes' bicentralizer conjecture and Kadison's problem on MASA — `lier Poisson boundary manuscript and the unitary dilation argument used in Theorem F. With the assistance of GPT-6 Astra in applying these tools to Kadison’s problem, the author obtained a substantially simplified proof on 9 October 2026. L`
- **[2611.16763](https://arxiv.org/abs/2611.16763)** (`math.AG`) Composition loci, invariant Bezoutians, and finite-orbit correspondences — `enerate results for the rational case. GPT-based tools (ChatGPT and Codex, OpenAI) were used for literature searches, to suggest and check additional mathematical arguments and formulas, to revise the exposition, and to assist with partial `
- **[2611.07494](https://arxiv.org/abs/2611.07494)** (`cs.GT`) Transparency in Team Contracts — `ralizing the guarantee from pure to mixed equilibria (Appendix A). The models also assisted the proofs that translate the Potential Lemma into an improved poly-time approximation algorithm (Appendix D). We provide LLM-generated and verifed `
- **[2611.05221](https://arxiv.org/abs/2611.05221)** (`cs.GT`) Efficient Equilibrium Computation in Colonel Blotto Games — `GPT to help work out proof details from our sketches and ideas, optimize the FPTAS in Section 5 and improve its running-time bounds, and write preliminary drafts of parts of the manuscript. We also used ChatGPT to generate the accompanying `
