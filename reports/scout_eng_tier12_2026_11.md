# Phase A2 Zero-Token T2 Scout: +7 Approved Engineering Categories & `math.NA` Metadata Probe

> **Zero-Token Phase A2 Deliverable (2026-11-24)** · Scratch DBs: `data/scout_eng_tier12_2026_11.db` (+7 approved categories) & `data/scout_math_na_meta_2026_11.db` (`math.NA` metadata-only) · `data/survey.db` **strictly untouched** (`4,104` papers / `89` classifications) · Full Stage-2 hit snippets: [`reports/slices/2026-11/phase0_scout_eng_tier12.md`](slices/2026-11/phase0_scout_eng_tier12.md) · Machine-readable summary: [`artifacts/scout_eng_tier12_2026_11_summary.json`](../artifacts/scout_eng_tier12_2026_11_summary.json)

## 1. Executive Summary

Running the exact bias-free OAI-PMH `arXivRaw` harvester (`--no-oai-until`, T2 window `2026-11-01`–`2026-11-19`) and deterministic Stage-2 full-text screen (`src/fetch_and_screen.py`, **0 LLM tokens**) across the **+7 Bhaskar-approved engineering categories** (`cs.PF`, `eess.IV`, `eess.AS`, `cs.GT`, `cs.CE`, `physics.flu-dyn`, `math.DS`) ingested **1,339 unique preprints** (`1,353` raw category appearances; `140` overlapping with the original 8-category T2 corpus → **1,199 net-new papers**, expanding the combined **15-category T2 panel to 5,303 unique papers**) with **99.78% full-text coverage** (`1,247` HTML5, `89` PDF, `3` HTTP 404 withdrawn papers).

Five sharp empirical findings emerge immediately — *before spending a single LLM token*:

1. **Four Clean 0.00% Null Results Complete the Disciplinary Bifurcation Picture:** **`cs.PF`** (`0/94`), **`eess.IV`** (`0/175`), **`eess.AS`** (`0/134`), and **`cs.CE`** (`0/146`) all have **literally zero Stage-2 Lean candidates** (`0` strong, `0` contextual-only).
2. **100% of arXiv's `eess.*` Archive Measured (`1,466` Unique T2 Papers):** Combining `eess.SY` (`738`) and `eess.SP` (`462`) from `data/survey.db` with `eess.IV` (`175`) and `eess.AS` (`134`) from this scout completes a **100% whole-archive census of `eess.*` (`1,466` unique papers; `985` primary `eess.*`)**. Across the three signal/image/audio processing categories (`eess.SP` $\cup$ `eess.IV` $\cup$ `eess.AS`), Stage-2 Lean prevalence is **`0 / 752` (0.00%, 95% one-sided Clopper–Pearson UB `0.40%`)** — all `3` `eess.*` Lean papers sit exclusively in `eess.SY` (Systems & Control).
3. **`cs.GT` Is the Highest-Density Stage-2 Pocket Yet Measured (`9.64%`), Followed by `math.DS` (`5.00%`):**
   - **`cs.GT`** yielded **`16 / 166` (9.64%)** Stage-2 Lean candidates (`14` strong + `2` contextual-only, and *both* contextual-only hits — `2611.07494` and `2611.05221` — link to `*-lean` GitHub repositories!), exceeding even `math.OC` (`25/724 = 3.45%` Stage-2)! `15/16` are net-new (`1` overlap: `2611.05243` *AltOMD-Lean*). Titles span algorithmic game theory/mechanism design/auctions, online matching, and auction-learning convergence — a prime testbed for Track 1's 4-way taxonomy (`eng_algorithmic_proof` vs. `pure_math_or_tcs`).
   - **`math.DS`** yielded **`18 / 360` (5.00%)** Stage-2 Lean candidates (`15` strong + `3` contextual-only; `17` net-new + `1` overlap: `2611.14756`), heavily weighted toward pure-math ergodic theory, arithmetic dynamics, and Veech surfaces (`math.CO`, `math.CA`, `math.AG`, `math.OA`, `math-ph`, `cs.LO`, pure `math.DS`), alongside applied dynamics/operator-learning papers (`2611.14756`, `2611.11805`, `2611.02237`).
4. **`physics.flu-dyn` Shows Real PDE-Formalization Activity (`2/278 = 0.72%`) — Strictly via `math.AP` Cross-Lists:** Both hits are net-new, full-featured Lean 4 / Mathlib formalizations with public GitHub repos (`2611.12862` odd-viscosity Navier–Stokes `OVNS-Lean`; `2611.07395` rigorously certified neural-network nonlinear water waves `Rigorously-certified-water-waves`), while primary-`physics.flu-dyn` preprints remain **`0 / 204` (0.00%)**.
5. **Full-Text Screening Remains Essential (`2.58×` Overall, `4.67×` in `cs.GT`) & Lean Outnumbers Beyond-Lean FV `3.4×`:** Metadata-only screening caught only `12` of the `31` `lean_strong` hits (**2.58×** recall gain; **4.67×** in `cs.GT`: `3 → 14`). Across all `1,339` papers, all Beyond-Lean FV tools combined (`other_itp=5`, `smt_sat=4`, `model_checker=0`, `proto_verifier=0`) totaled only **`9` papers (`0.67%`)** vs. **`36` Stage-2 Lean candidates (`2.69%`)**. Only **`34` net-new candidates** require Stage-3 profiling + Stage-4 LLM classification in Phase C1.

---

## 2. Per-Category Stage-2 Yield Table (T2: `2026-11-01` – `2026-11-19`)

### 2.1 The +7 Approved Categories (`data/scout_eng_tier12_2026_11.db`)

| Category | Total Papers (`Prim` / `X-list`) | Net-New vs. Orig-8 (`Overlap`) | Full-Text Screened (`Fail`) | Meta `lean_strong` | Stage-2 `lean_strong` (`Prim` / `New`) | Stage-2 `ctx_only` (`New`) | **Total Stage-2 Lean Cands** (`Rate`, 95% CI / UB) | Beyond-Lean Any FV (`ITP`/`SMT`) |
| :--- | :---: | :---: | :---: | ---: | :---: | :---: | :---: | :---: |
| **`cs.GT`** | 166 (`117` / `49`) | 146 (`20`) | 165 (`1`) | 3 | **14** (`8` / `13`) | 2 (`2`) | **16** (**9.64%**, [6.02%, 15.08%]) | 0 (`0`/`0`) |
| **`math.DS`** | 360 (`219` / `141`) | 336 (`24`) | 359 (`1`) | 7 | **15** (`6` / `14`) | 3 (`3`) | **18** (**5.00%**, [3.19%, 7.77%]) | 2 (`1`/`1`) |
| **`physics.flu-dyn`** | 278 (`204` / `74`) | 273 (`5`) | 278 (`0`) | 2 | **2** (`0` / `2`) | 0 (`0`) | **2** (**0.72%**, [0.20%, 2.58%]) | 1 (`1`/`0`) |
| **`cs.PF`** | 94 (`24` / `70`) | 43 (`51`) | 94 (`0`) | 0 | **0** (`0` / `0`) | 0 (`0`) | **0** (**0.00%**, UB 3.14%) | 3 (`1`/`2`) |
| **`eess.IV`** | 175 (`126` / `49`) | 156 (`19`) | 175 (`0`) | 0 | **0** (`0` / `0`) | 0 (`0`) | **0** (**0.00%**, UB 1.70%) | 2 (`1`/`1`) |
| **`eess.AS`** | 134 (`79` / `55`) | 123 (`11`) | 133 (`1`) | 0 | **0** (`0` / `0`) | 0 (`0`) | **0** (**0.00%**, UB 2.21%) | 1 (`1`/`0`) |
| **`cs.CE`** | 146 (`92` / `54`) | 130 (`16`) | 146 (`0`) | 0 | **0** (`0` / `0`) | 0 (`0`) | **0** (**0.00%**, UB 2.03%) | 0 (`0`/`0`) |
| **Unique +7 Total** | **1,339** *(raw sum 1,353)* | **1,199** (`140`) | **1,336** (`3`; 99.78%) | **12** | **31** (`29` net-new) | **5** (`5` net-new) | **36** (**2.69%**, `34` net-new) | **9** (`5`/`4`) |
| **Combined 15-Cat T2** | **5,303** *(4,104 + 1,199)* | — | **5,293** (`10`; 99.81%) | **28** | **80** | **9** | **89** (**1.68%**) | **57** *(raw)* |

*(Note: All 3 failed fetches in `+7` are HTTP 404 withdrawn papers: `2611.13243v3` [`cs.LG`], `2611.11714v2` [`cs.MA`], and `2611.01482v2` [`math.DS`, notably withdrawn with comment: "This paper is being withdrawn as it relies heavily on AI-generated arguments that have not been thoroughly verified."].)*

### 2.2 Complete 100% `eess.*` Archive Census (T2: `2026-11-01` – `2026-11-19`)

| `eess.*` Category | T2 Unique Papers (`Primary`) | Stage-2 Lean Candidates | Confirmed Lean (`v1`) | Status |
| :--- | :---: | :---: | :---: | :--- |
| `eess.SY` (Systems & Control) | 738 (`467`) | 3 (0.41%) | 3 (0.41%; 2 strict eng-alg) | Active (from `survey.db`) |
| `eess.SP` (Signal Processing) | 462 (`313`) | 0 (0.00%) | 0 (0.00%) | Clean 0% null (`survey.db`) |
| `eess.IV` (Image & Video Processing) | 175 (`126`) | 0 (0.00%) | 0 (0.00%) | Clean 0% null (A2 scout) |
| `eess.AS` (Audio & Speech Processing) | 134 (`79`) | 0 (0.00%) | 0 (0.00%) | Clean 0% null (A2 scout) |
| **Non-Control `eess.*` Union (`SP` $\cup$ `IV` $\cup$ `AS`)** | **752** | **0 (0.00%, 95% UB 0.40%)** | **0 (0.00%)** | **Zero Stage-2 hits** |
| **100% `eess.*` Archive Union** | **1,466** (`985`) | **3 (0.20%)** | **3 (0.20%)** | **100% confined to `eess.SY`** |

---

## 3. Complete Inventory of +7 Stage-2 Lean Candidates (`n = 36`; `34` Net-New)

### 3.1 `cs.GT` Candidates (`n = 16`: `14` Strong + `2` Contextual-Only; `15` Net-New)

| arXiv ID | Primary | Signal | Meta Hit? | Status vs. Orig-8 | Repo / Artifact URL (first non-boilerplate) | Title |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `2611.24920` | `cs.GT` | strong | No | Net-new | `GO-EPFL/subadditive-online-combinatorial-auctions` | The Optimal Competitive Ratio for Subadditive Online Combinatorial Auctions is Less Than 1/2 |
| `2611.22216` | `cs.GT` | strong | No | Net-new | `hajiaghayi/Bertrand` | Settling the Time and Structural Complexity of Bertrand Networks |
| `2611.20890` | `cs.GT` | strong | No | Net-new | `SimonWMackenzie/connected-envy-free-lean` | Nearly Settling the Complexity of Connected $\varepsilon$-Envy-Free Cake Cutting |
| `2611.17292` | `cs.DS` | strong | No | Net-new | *(none extracted; mentions GPT-6 Astra Lean 4)* | The Submodular Secretary Problem: Tight $1-1/e$ for Monotone Objectives... |
| `2611.17223` | `cs.DS` | strong | No | Net-new | `radniazadeh/bernoulli-poly.git` | Combinatorial Bernoulli Factories with Polynomially Many Coins |
| `2611.15711` | `cs.DS` | strong | No | Net-new | `relyt871/BWCA-Online-Lean` | Beyond Worst-Case Online Algorithms via Input Subsampling |
| `2611.14974` | `cs.GT` | strong | No | Net-new | *(autoresearch/frontier challenge links — likely mention-only)* | Who Moved the Frontier? Paying Open Frontier Challenges with Free Identities |
| `2611.14586` | `stat.ML` | strong | **Yes** | Net-new | `doi.org/10.5281/zenodo.23768172` | Finite-Cadence Refresh Equilibria for Streaming Prior-Anchored Ridge |
| `2611.11424` | `cs.GT` | strong | No | Net-new | `farhadi94/envy-free-division` | The Query Complexity of Envy-Free Division: Cake, Chores, and Mixed Resources |
| `2611.09615` | `cs.GT` | strong | No | Net-new | `renatoppl/trace-square-root` | Contextual Search and Bilateral Trade with a Trace-Square-Root Potential |
| `2611.06896` | `cs.DS` | strong | No | Net-new | `farhadi94/online-edge-weighted-matching` | Online Edge-Weighted Matching Beyond 0.55 |
| `2611.05243` | `cs.LG` | strong | No | **In `survey.db`** (`lean_contributed`) | `CoffeeAndConvexity/AltOMD-Lean` | Logarithmic Regret for Alternating Mirror Descent |
| `2611.04934` | `cs.GT` | strong | **Yes** | Net-new | `philippwarode/contract-design-polymatroids-lean` + Zenodo | The Complexity of Continuous Contract Design over Polymatroids |
| `2611.04545` | `cs.GT` | strong | **Yes** | Net-new | `blubin/firstprice-certificates` | Coercive at the equilibrium, monotone nowhere: exact convergence certificates for learning in first-price auctions |
| `2611.07494` | `cs.GT` | **ctx_only** | No | Net-new | `wuzhuangtai00/transparency-lean` *(real Lean repo!)* | Transparency in Team Contracts |
| `2611.05221` | `cs.GT` | **ctx_only** | No | Net-new | `AbheekG/colonel-blotto-lean` *(real Lean repo!)* | Efficient Equilibrium Computation in Colonel Blotto Games |

### 3.2 `math.DS` Candidates (`n = 18`: `15` Strong + `3` Contextual-Only; `17` Net-New)

| arXiv ID | Primary | Signal | Meta Hit? | Status vs. Orig-8 | Repo / Artifact URL (first non-boilerplate) | Title |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `2611.20966` | `math.DS` | strong | **Yes** | Net-new | `Manzatto/equilibrium-states-finite-order-mixing-clt-counterexample` | Finite-order exponential mixing does not imply the central limit theorem for unique equilibrium states |
| `2611.19243` | `math.DS` | strong | No | Net-new | `Ryan-Hao-Jan/Veech-dichotomy-for-cover` | Veech dichotomy for specific covering surface over Veech surface |
| `2611.17277` | `math.DS` | strong | No | Net-new | `ckkogler/lpselfsimilar-lean` | On $L^p$ density of self-similar measures and Bernoulli convolutions |
| `2611.15751` | `math.CO` | strong | **Yes** | Net-new | `peterbanda/d-dim-shift-symmetry-in-ca` | Shift-Symmetric Configurations in $d$-Dimensional Cellular Automata |
| `2611.14756` | `math.DS` | strong | **Yes** | **In `survey.db`** (`lean_contributed`) | `magbenji/discrete-modified-gradient-lean` + Zenodo | Stability of equilibria in discrete-time modified-gradient systems and the multivariate breeder's equation |
| `2611.11805` | `math.NA` | strong | **Yes** | Net-new | `sgstepaniants/inelastic_hom_learn` | Operator Learning of Microstructure-Dependent Internal-Variable Models for Inelastic Homogenization |
| `2611.11641` | `cs.LO` | strong | **Yes** | Net-new | `zenodo.org/records/24060394` | Spectral Stability, Fatou Basin Contraction, and Machine-Checked Multipliers in Generalized Syracuse Dynamics |
| `2611.09066` | `math.DS` | strong | No | Net-new | `sascha2718/lean-diagonal-antidiagonal` | Hausdorff dimension of planar box-like self-affine sets with rotations |
| `2611.08591` | `math-ph` | strong | **Yes** | Net-new | `stacks-ai/papers/.../conley-index-dynamical-systems` | Conley index theory for asymptotically autonomous systems and UV-to-IR connections |
| `2611.07818` | `math.DS` | strong | No | Net-new | *(none extracted; thanks Lean formalization helper)* | Thurston algorithm for real entire maps: existence and uniqueness |
| `2611.06106` | `math.AG` | strong | No | Net-new | `tdupu/pcfawd-formalization` *(with blueprint!)* | PCF All The Way Down |
| `2611.04575` | `math.CO` | strong | No | Net-new | `HamedMousaviMath/Lean-Formalization-Polynomial-Configurations-...` | Polynomial configurations and pointwise averages along Piatetski--Shapiro primes |
| `2611.02465` | `math.CA` | strong | **Yes** | Net-new | `anastasiosfragkosmath/Pointwise-Ergodic-Theorems-Along-floor-p-c-...` | Pointwise Ergodic Theorems Along $\lfloor p^c \rfloor$ for Every $c>1$ |
| `2611.02237` | `cs.LG` | strong | No | Net-new | *(mentions `qchk`/Lean/Mathlib — check ancillary/Zenodo in Stage 3)* | Nonreciprocal Spherical Attention and Retrieval: Sharp Coarsening Clocks and Certified Score Correction |
| `2611.02167` | `math.CA` | strong | No | Net-new | `openai/math` *(likely mention-only critique of OpenAI preprint)* | On a hybrid trilinear Hilbert transform |
| `2611.26622` | `math.CO` | ctx_only | No | Net-new | `openai/math` *(likely citation-only)* | Quasipolynomial pyjamas |
| `2611.24787` | `math.OA` | ctx_only | No | Net-new | `openai/math` *(text says "Lean was also used to...")* | A Poisson boundary solution to Connes' bicentralizer conjecture and Kadison's problem on MASA |
| `2611.16763` | `math.AG` | ctx_only | No | Net-new | *(text says "assist with partial Lean formalizations")* | Composition loci, invariant Bezoutians, and finite-orbit correspondences |

### 3.3 `physics.flu-dyn` Candidates (`n = 2`: `2` Strong + `0` Contextual-Only; `2` Net-New)

| arXiv ID | Primary | Signal | Meta Hit? | Status vs. Orig-8 | Repo / Artifact URL | Title |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `2611.12862` | `math.AP` | strong | **Yes** | Net-new | `DavetheSlayer/OVNS-Lean` | Quantitative global regularity for Navier--Stokes equations with odd viscosity on the cubic three-torus |
| `2611.07395` | `math.AP` | strong | **Yes** | Net-new | `michalshavitNYU/Rigorously-certified-water-waves` (`.../tree/main/Lean`) | Rigorously Certified Neural-Network Computation of Nonlinear Water Waves at Near-Machine Precision |

---

## 4. `math.NA` Metadata-Only Probe (For Bhaskar's Decision)

Ingested via OAI-PMH (`2026-11-01`–`2026-11-19`) into `data/scout_math_na_meta_2026_11.db` (metadata-only, ~10s, **0 full-text fetches, 0 LLM tokens**):

- **Total T2 `math.NA` papers:** **`446`** (`335` primary `math.NA`, `111` cross-listed)
- **Overlap with existing corpora:** `49` overlap with original 8 (`data/survey.db`), `47` overlap with `+7`, **`92` overlap with the combined 15-category panel → `354` net-new papers** (would take ~4 min to full-text screen if later approved).
- **Metadata-only Lean hits:** **`4` `meta_lean_strong` + `1` `meta_lean_ctx_only`** (`0` metadata Beyond-Lean FV):

| arXiv ID | Primary | Meta Signal | Already Captured? | Title |
| :--- | :--- | :---: | :---: | :--- |
| `2611.13584` | `math.OC` | strong | **Yes — in `survey.db`** (`lean_contributed`, `eng_algorithmic_proof`) | Exact (Non-)Accelerations of Heavy-Ball Discretizations |
| `2611.12585` | `math.NA` | strong | **Yes — in `survey.db`** (`lean_contributed`, `eng_algorithmic_proof`) | A Large Gap between Galerkin Errors with and without Mesh-Uniform Regularity for the KdV Equation... |
| `2611.11805` | `math.NA` | strong | **Yes — in `+7` (`math.DS`)** | Operator Learning of Microstructure-Dependent Internal-Variable Models for Inelastic Homogenization |
| `2611.10961` | `cs.AI` | strong | No (`cs.AI`/`cs.LG`/`math.NA`) | Improving Analytic Constants via Interpretable AI-Guided Lean Proof Refinement *(meta-system)* |
| `2611.21570` | `math.NA` | ctx_only | No (`cs.MS`/`math.NA`) | Trustworthy Numerical Software in the Age of AI: What Would Turing Do? *(essay/commentary)* |

- **Takeaway for Bhaskar:** **3 of the 4** metadata-strong `math.NA` Lean papers are *already captured* by our 15-category panel (`survey.db` + `math.DS`), and the sole net-new metadata-strong hit (`2611.10961`) is a `cs.AI` AI-proving meta-system. Applying our empirical `2.6×–3.4×` full-text recall multiplier suggests full-text screening the `354` net-new `math.NA` papers would likely add only **~4–8** net-new Stage-2 candidates (several of which would likely be numerical-math / applied-math theorems). Keeping `math.NA` out of the 15-category core panel (per Bhaskar's lean) is well-supported by the metadata evidence, and a 4-minute full-text scout remains trivial if he decides to include it later.

---

## 5. Implications & Recommended Next Steps (Phase B → Phase C1)

1. **All +7 yields validate the Bhaskar 15-category whole-category design:** We get **four crisp 0.00% null results** (`eess.IV`, `eess.AS`, `cs.PF`, `cs.CE`, completing **100% of `eess.*`**), **two `math.AP`→`physics.flu-dyn` PDE/water-wave formalizations**, and **two surging adoption pockets (`cs.GT` at 9.64%, `math.DS` at 5.00%)**.
2. **Track 1's 4-way taxonomy is *indispensable* before Phase C1 classification:** As anticipated, `math.DS` has a high share of pure-math ergodic/arithmetic dynamics and `cs.GT` mixes algorithmic game theory / TCS complexity with auction-learning & optimization convergence. Running Phase B2 (dual-rater validation of the 4-way rubric) before classifying the **34 net-new Stage-2 candidates** ensures we only run Stage-4 LLM classification once under a validated rubric.
3. **Low Phase C1 Cost:** Stage-3 static profiling + Stage-4 LLM classification on the `+7` T2 slice needs only **34 net-new papers** (and **0 papers** in `cs.PF`, `eess.IV`, `eess.AS`, `cs.CE`).
