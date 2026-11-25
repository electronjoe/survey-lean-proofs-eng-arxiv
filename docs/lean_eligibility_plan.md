# Lean 4 Eligibility & Denominator-Adjusted Adoption Pipeline (Plan & Status)

**Purpose:** Measure what fraction of arXiv papers in each of the 15 surveyed engineering and applied-theory categories *could reasonably have used Lean 4*, enabling **denominator-adjusted (conditional) adoption rates** alongside raw whole-category rates in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex).

This document is the single source of truth for plan design, rubric definitions, token budgets, checkpoint status, and cross-session resumption.

---

## 1. Scientific Motivation & Nested Denominator Framework

Raw category adoption ($r_c^{\text{raw}} = k_c / N_c$) conflates two distinct phenomena:
1. **Disciplinary composition:** How many papers in a category even contain original formal mathematical claims (e.g., `cs.RO` and `eess.IV` are heavily empirical/experimental; `math.OC`, `math.DS`, and `cs.GT` are overwhelmingly theorem–proof).
2. **True adoption gap & Mathlib readiness:** Among papers *with* formal claims, what fraction sit in domains tractably formalizable in current Lean 4 + Mathlib vs. blocked by missing continuous/PDE/stochastic libraries?

To avoid conflating "contains a Theorem environment" with "tractably Lean-ready today" (which suffers from both PDE/SDE false positives and operational-FV/unnumbered-proof false negatives), we measure a **nested 3-tier denominator** anchored on the **T2 (`2026-11`, $N = 5{,}303$)** census (where `68/75 = 90.7%` of v1 confirmed Lean adoption occurs and every category has $N_c \ge 94$):

| Denominator Tier | Definition | Matched Numerator | Purpose |
|---|---|---|---|
| **Tier 0 ($N_c$)** | All T2 preprints in category $c$ | All confirmed Lean / Strict Eng. | Existing raw census baseline |
| **Tier 1 ($N_c^{\text{thm}}$)** | **Theorem-Bearing Papers (`L1 ∪ L2`)** — original deductive mathematical claims with proofs | Math/Alg. Lean (`eng_algorithmic + pure_math_tcs`) | Objective, skeptic-proof baseline independent of Mathlib maturity |
| **Tier 2a ($N_c^{\text{lean-math}}$)** | **Lean-Amenable Math (`L1`)** — theorems tractably formalizable in Lean 4 + Mathlib today | Math/Alg. Lean (and Strict `eng_algorithmic`) | Isolates Mathlib continuous-analysis barriers (`L2`) from community lag (`L1`) |
| **Tier 2b ($N_c^{\text{lean-broad}}$)** | **Broad Lean-Applicable (`L1 ∪ L3`)** — adds operational/protocol FV specs (`L3`) | All confirmed Lean excl. `meta_formalization_system` | Apples-to-apples denominator for `cs.DC`, `cs.CR`, `cs.NI`, `cs.PF` |

---

## 2. Five-Class Eligibility Rubric (`L1`–`L5`)

Every LLM-audited paper is assigned one mutually exclusive primary class:

* **`L1_lean_amenable_math`**: Asserts original mathematical/algorithmic theorems, propositions, or lemmas with deductive proofs (or complete proof arguments) whose mathematical dependencies are broadly tractable in Lean 4 + Mathlib today (e.g., finite-dimensional linear algebra/convex optimization, convergence/regret/sample-complexity bounds, discrete/combinatorial/graph/game theory, mechanism design, algebraic coding/information theory, elementary real analysis/probability, finite-state/discrete-time stability, cryptographic reductions over finite groups/rings).
* **`L2_mathlib_blocked_math` ("High-Barrier / Frontier Analysis")**: Asserts original rigorous mathematical theorems with deductive proofs, *but* core proofs rely heavily on advanced continuous/analytic/stochastic/infinite-dimensional infrastructure currently absent or highly immature in Mathlib 4 (e.g., nonlinear PDEs / Navier–Stokes / Sobolev weak solutions, Itô stochastic calculus / SDEs / SPDEs, deep random-matrix asymptotics, viscosity HJB solutions, infinite-dimensional operator algebras or étale/ergodic PDE regularity). *Pilot E0 calibration note:* `14/71` confirmed Lean math papers fall here — confirming these are **high-barrier / frontier** (formalizable only via partial sub-lemma scope or major custom Lean infrastructure), not strictly impossible.
* **`L3_operational_spec_fv`**: Primary formalizable artifact is **not** a classical mathematical theorem–proof, *but* an operational specification or correctness property of a software system, hardware/RTL/ISA design, distributed/consensus protocol, database/pipeline, type system, or security protocol (safety/liveness invariants, refinement, memory/type safety, protocol security) amenable to Lean 4 or specialized FV (TLA+/Coq/ProVerif/SMT).
* **`L4_heuristic_or_numerical_only`**: Contains equations, analytical derivations, or informal "propositions/observations" whose justification is heuristic (e.g., unrigorous linearization, dropping higher-order terms, physics scaling arguments), or whose guarantees are established only via numerical simulation or floating-point SDP/LMI/solver outputs without deductive proof.
* **`L5_empirical_or_survey`**: Empirical/experimental paper, ML architecture/benchmark paper, dataset/system/hardware prototype, or literature survey/position paper containing no original formal deductive claims (even if it cites prior theorems in background).

Auxiliary structured fields:
* `has_original_deductive_proof` (`bool`): True iff the paper asserts and deductively proves (in main text or appendix) at least one original mathematical claim or formal correctness property.
* `dominant_math_area` (`enum`): `optimization_convex_or_nonconvex`, `control_dynamical_systems`, `game_theory_econ_mechanism`, `info_coding_signal_theory`, `discrete_graph_tcs_crypto`, `pde_fluid_continuum_mechanics`, `stochastic_prob_statistics`, `systems_protocol_sw_hw_spec`, `none_or_empirical`.
* `primary_barrier_if_L2` (`enum`): `pde_sobolev_continuum`, `stochastic_sde_ito`, `measure_prob_asymptotics`, `operator_spectral_infinite_dim`, `numerical_floating_point_hybrid`, `other`, `N/A`.

---

## 3. Architecture (Option C2: Full T2 Zero-Token Census + Stratified Tier-2 LLM)

1. **Stage E0 — Pilot & Positive-Control Calibration (`n = 127` papers, deduplicated):**
   * `45` stratified random T2 papers (`3`/category across all 15 categories, seed `20261125`) + all **`82` confirmed Lean papers** across T0/T1/T2 as positive controls.
   * Validates: (a) LaTeXML `ltx_theorem`/`ltx_proof` parser precision & PDF fallback, (b) positive-control sensitivity (do confirmed `eng_algorithmic_proof` & `pure_math_or_tcs` Lean papers land in `L1` and `operational_system_fv` in `L3`?), and (c) rubric clarity before scaling.
2. **Stage E1 — Full T2 Zero-Token Structural Census (`N = 5,303` papers, 0 LLM tokens):**
   * [`src/screen_math_structure.py`](../src/screen_math_structure.py) fetches arXiv HTML5 (93.6% of T2; LaTeXML preserves `ltx_theorem`, `ltx_proof`, `ltx_equation`, and TeX `<annotation>`) with PDF fallback (6.4%).
   * Stores structural counts, domain-barrier keyword cues, and compact ≤2,400-char theorem/heading snippets in `data/eligibility_t2.db` (`math_structure` table).
   * Deterministically partitions all 5,303 T2 papers into `E1_formal_thm_proof`, `E1_weak_or_unnumbered_math`, and `E1_no_formal_claims`.
3. **Stage E2 — Stratified Compact LLM Classification (`~450` T2 papers, batched 5/prompt):**
   * [`workflows/classify_lean_eligibility.py`](../workflows/classify_lean_eligibility.py) classifies up to `25–30` `E1_formal_thm_proof` papers/category + `10` non-`E1_formal_thm_proof` recall-audit papers/category (`~450` total), spending **0 LLM tokens** on trivially empirical papers outside the small negative recall audit.
   * Applies Horvitz–Thompson / post-stratified estimation over the exact E1 census strata to produce unbiased per-category proportions (`L1`–`L5`) and propagated 95% CIs.
4. **Stage E3 — Validation & Optional Temporal Spot-Check:**
   * Blinded human IRR on `45` papers (`3`/category) computing Cohen's $\kappa$ on Tier 1 (`L1∪L2`) and 5-class (`L1`–`L5`).
   * Optional zero-token E1 stability spot-check on `150` random T0 papers (`10`/cat, <1 min, 0 tokens).
5. **Stage E4 — Paper Integration:**
   * Canonical git-tracked artifact `artifacts/lean_eligibility_t2.json`, report `reports/lean_eligibility_analysis.md`, vector figure `fig_eligibility_adjusted_adoption.pdf`, updated 15-category table in `papers/arxiv-empirical/main.tex`, and numeric gate checks in `scripts/check_paper_numbers.py`.

---

## 4. Token & Runtime Budget

| Stage | Scope | Wall-Clock / Network | Est. LLM Tokens | Model |
|---|---|---|---|---|
| **Pilot E0** | `45` random T2 + `82` confirmed Lean (`≤127` papers) | ~1–2 min | ~140K–200K (batched 5/call) | `flash` |
| **E1 Census** | All `5,303` T2 papers | ~35–45 min (polite `0.4s`) | **0** | Deterministic Python |
| **E2 Stratified** | `~450` T2 papers (stratified by E1 bucket) | 0 (cached snippets) | ~500K–600K (batched 5/call) | `flash` / `flash_lite` |
| **E3 Borderline (opt.)** | `40` borderline `L1`/`L2` papers | 0 | ~75K | `pro` |
| **E3 Human IRR** | `45` blinded papers | — | **0** | Human |
| **Total (C2 Standard)** | **Full T2 Tier-1 + Stratified Tier-2** | **~40–45 min** | **~700K–875K total** | Mostly `flash` |

---

## 5. Checkpoint & Status Tracker

| Checkpoint | Status | Key Outputs | Notes / Metrics |
|---|---|---|---|
| **0. Plan & Pipeline Code** | **Complete** (`2026-11-25`) | `docs/lean_eligibility_plan.md`, `src/screen_math_structure.py`, `workflows/classify_lean_eligibility.py`, `tests/test_math_structure.py` | Deterministic LaTeXML HTML5 + PDF structural parser + 5-per-prompt batched workflow (`3/3` unit tests pass) |
| **1. Pilot E0 (`45` T2 + `82` pos. controls)** | **Complete** (`2026-11-25`) | `artifacts/lean_eligibility_pilot_e0.json`, `reports/lean_eligibility_pilot_e0.md` | **Gate PASSED:** `127/127` fetched (`117` HTML, `10` PDF, `0` fail); blinded positive-control sensitivity = **`71/71` (`100.0%`)** math roles in `L1∪L2` (`80.3%` `L1`, `19.7%` `L2` frontier) & **`8/8` (`100.0%`)** `operational_system_fv` in `L3`; **`0/82`** unexpected mismatches; `E1_no_formal_claims` specificity = **`14/14` (`100%`)** non-eligible; `E1_formal_thm_proof` purity = **`91/92` (`98.9%`)** `L1∪L2∪L3` |
| **2. Full T2 E1 Census (`5,303` papers)** | **Ready Next** | `data/eligibility_t2.db`, `artifacts/lean_eligibility_e1_t2_summary.json` | Zero-token full-text structural scan (~35–45 min unattended polite fetch; 0 LLM tokens) |
| **3. Stratified E2 LLM (`~450` papers)** | Pending | `artifacts/lean_eligibility_t2.json`, `reports/lean_eligibility_analysis.md` | 3-stratum post-stratified estimation (`E1_formal`, `E1_weak`, `E1_none`) + propagated 95% CIs (~500K batched `flash` tokens) |
| **4. Human IRR & T0 Spot-Check** | Pending | `artifacts/human_annotations/eligibility_irr.csv` | 45-paper blinded IRR + 150-paper T0 zero-token check |
| **5. Paper & Figure Integration** | Pending | `fig_eligibility_adjusted_adoption.pdf`, `papers/arxiv-empirical/main.tex` | Table update, paired adoption figure, `check_paper_numbers.py` gate |

---

## 6. Reproduction Commands

```bash
# 1. Initialize unified T2 + positive-control DB (zero network, instant)
uv run python -m src.screen_math_structure init-db

# 2. Run Pilot E0 zero-token structural extraction (45 T2 + 82 confirmed Lean)
uv run python -m src.screen_math_structure fetch --cohort pilot_e0 --workers 3 --min-interval 0.4

# 3. Export compact batched inputs for Pilot E0 LLM classification
uv run python -m src.screen_math_structure export-e2 --cohort pilot_e0 --out data/eligibility_pilot_e0_in.json

# 4. Run workflows/classify_lean_eligibility.py via run_workflow (batched 5/prompt, flash)
#    -> writes data/eligibility_pilot_e0_out.json

# 5. Import Pilot E0 results & emit git-tracked artifact + Markdown report
uv run python -m src.screen_math_structure import-e2 \
  --cohort pilot_e0 \
  --in data/eligibility_pilot_e0_out.json \
  --artifact artifacts/lean_eligibility_pilot_e0.json \
  --report reports/lean_eligibility_pilot_e0.md

# 6. (After Pilot E0 sign-off) Full T2 zero-token E1 census (5,303 papers, resumable)
uv run python -m src.screen_math_structure fetch --cohort t2_all --workers 3 --min-interval 0.4
```
