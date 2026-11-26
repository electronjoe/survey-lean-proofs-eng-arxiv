# Stage E2 Analysis: Lean 4 Eligibility & Denominator-Adjusted Adoption (T2, 2026-11)

- **Generated:** `2026-11-26T01:51:37+00:00`
- **Model:** `Gemini 4 Hydrogen (High) [gemini-4-hydrogen-tiered-high]` (`flash`, batched 5 papers/prompt, strictly blinded to `is_confirmed_lean`)
- **Sampling design:** `independent_per_category_3stratum_neyman_srs` (`30` draws/cat = `450` draws → **`439` unique T2 papers**: `428` net-new + `11` cached Pilot E0 `flash` hits)
- **T2 census frame:** `N = 5,303` (`5,293` full-text extracted in Stage E1 = `99.81%`)

## 1. Pooled T2 Denominators & Denominator-Adjusted Adoption (`N = 5,303`)

| Denominator Tier | Definition | Est. Share of T2 (95% CI) | Est. Papers (95% CI) | Matched T2 `v1` Lean | Conditional Rate (95% CI) |
|---|---|---:|---:|---:|---:|
| **Tier 0 (`N`)** | All T2 preprints | `100.0%` | `5,303` | `68` (all) | **`1.28%`** |
| **Tier 1 (`L1 ∪ L2`)** | Theorem-Bearing Math | `34.6%` [31.9%, 37.6%] | `1837` `[1694, 1993]` | `61` (Math+Alg) | **`3.32%`** [2.4%, 4.6%] |
| **Tier 2a (`L1`, Matched)** | Lean-Amenable Math | `26.9%` [24.0%, 29.9%] | `1426` `[1271, 1585]` | `49` (`L1` Math+Alg) | **`3.44%`** [2.4%, 5.1%] |
| **Tier 2-Frontier (`L2`, Matched)** | Mathlib-Blocked / Frontier | `7.8%` [5.7%, 10.0%] | `412` `[300, 532]` | `12` (`L2` Math+Alg) | **`2.92%`** [1.3%, 6.9%] |
| **Tier 2b (`L1 ∪ L3`, Matched)** | Broad Lean-Applicable | `29.4%` [26.2%, 32.6%] | `1557` `[1389, 1732]` | `53` (`L1∪L3` Non-Meta) | **`3.40%`** [2.4%, 5.0%] |

Pooled 5-class composition (`N = 5,303`): `L1` = **26.9%**, `L2` (Mathlib-blocked) = **7.8%**, `L3` (Op-FV) = **2.5%**, `L4` (Heuristic/Num) = **15.0%**, `L5` (Empirical/Survey) = **47.9%**. *(Note: Matched `L1` and `L2` numerators use each confirmed T2 `v1` adopter's strictly blinded Pilot E0 `flash` class, preventing `L2` frontier adopters in `math.DS`/`math.OC` from inflating `L1` denominators.)*

## 2. Per-Category Nested Denominators & Strictly Matched Conditional Adoption (All 15 Categories)

| Category | `N` | `L1`% | `L2`% | `L3`% | Tier 1 (`L1∪L2`) | Tier 2a (`L1`) | Raw `v1` | **Tier 1 (`Math+Alg \| L1∪L2`)** | **Tier 2a Matched (`L1 \| L1`)** | **Tier 2b Matched (`L1∪L3`)** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `math.OC` | 724 | 65.8% | 10.6% | 0.0% | 553 (76.4%) | 476 (65.8%) | 2.62% (19) | **2.9%** (16) [1.7%, 4.8%] | **2.5%** (12) [1.4%, 4.6%] | **2.5%** (12) [1.3%, 4.5%] |
| `cs.DC` | 335 | 18.4% | 0.0% | 16.2% | 62 (18.4%) | 62 (18.4%) | 1.79% (6) | **8.1%** (5) [2.3%, 15.3%] | **8.1%** (5) [2.2%, 16.2%] | **5.2%** (6) [1.9%, 11.8%] |
| `cs.IT` | 338 | 61.5% | 7.7% | 0.0% | 234 (69.2%) | 208 (61.5%) | 1.78% (6) | **2.6%** (6) [1.1%, 5.3%] | **2.9%** (6) [1.2%, 6.0%] | **2.9%** (6) [1.2%, 6.0%] |
| `cs.CR` | 629 | 23.7% | 0.0% | 19.4% | 149 (23.7%) | 149 (23.7%) | 1.11% (7) | **2.7%** (4) [0.7%, 6.0%] | **2.7%** (4) [0.7%, 6.2%] | **2.6%** (7) [1.1%, 5.4%] |
| `eess.SY` | 738 | 39.2% | 9.3% | 0.0% | 358 (48.6%) | 290 (39.2%) | 0.41% (3) | **0.8%** (3) [0.2%, 2.2%] | **1.0%** (3) [0.3%, 2.7%] | **1.0%** (3) [0.3%, 2.7%] |
| `eess.SP` | 462 | 26.7% | 5.2% | 0.0% | 148 (31.9%) | 124 (26.7%) | 0.00% (0) | **0.0%** (0) [0.0%, 2.4%] | **0.0%** (0) [0.0%, 2.8%] | **0.0%** (0) [0.0%, 2.8%] |
| `cs.NI` | 196 | 15.6% | 0.0% | 2.6% | 31 (15.6%) | 31 (15.6%) | 0.00% (0) | **0.0%** (0) [0.0%, 9.3%] | **0.0%** (0) [0.0%, 9.3%] | **0.0%** (0) [0.0%, 8.4%] |
| `cs.RO` | 1159 | 5.6% | 0.0% | 0.0% | 65 (5.6%) | 65 (5.6%) | 0.00% (0) | **0.0%** (0) [0.0%, 3.6%] | **0.0%** (0) [0.0%, 3.6%] | **0.0%** (0) [0.0%, 3.6%] |
| `cs.GT` | 166 | 88.4% | 4.6% | 0.7% | 154 (93.0%) | 147 (88.4%) | 9.04% (15) | **9.7%** (15) [6.0%, 15.5%] | **10.2%** (15) [6.2%, 16.5%] | **10.1%** (15) [6.1%, 16.2%] |
| `math.DS` | 360 | 34.5% | 58.5% | 0.0% | 335 (92.9%) | 124 (34.5%) | 3.89% (14) | **4.2%** (14) [2.5%, 6.8%] | **4.8%** (6) [1.9%, 12.1%] | **4.8%** (6) [1.8%, 12.0%] |
| `physics.flu-dyn` | 278 | 0.9% | 7.5% | 0.0% | 23 (8.4%) | 3 (0.9%) | 0.72% (2) | **8.6%** (2) [1.4%, 21.1%] | **76.9%**† (2) [2.7%, 95.7%] | **76.9%**† (2) [3.0%, 94.8%] |
| `cs.PF` | 94 | 14.4% | 0.0% | 2.0% | 14 (14.4%) | 14 (14.4%) | 0.00% (0) | **0.0%** (0) [0.0%, 18.3%] | **0.0%** (0) [0.0%, 18.3%] | **0.0%** (0) [0.0%, 16.7%] |
| `eess.IV` | 175 | 4.6% | 0.0% | 0.0% | 8 (4.6%) | 8 (4.6%) | 0.00% (0) | **0.0%** (0) [0.0%, 20.5%] | **0.0%**† (0) [0.0%, 20.7%] | **0.0%**† (0) [0.0%, 21.0%] |
| `eess.AS` | 134 | 1.5% | 0.0% | 0.0% | 2 (1.5%) | 2 (1.5%) | 0.00% (0) | **0.0%** (0) [0.0%, 38.0%] | **0.0%**† (0) [0.0%, 38.2%] | **0.0%**† (0) [0.0%, 37.7%] |
| `cs.CE` | 146 | 8.2% | 2.3% | 0.0% | 15 (10.5%) | 12 (8.2%) | 0.00% (0) | **0.0%** (0) [0.0%, 16.1%] | **0.0%** (0) [0.0%, 18.8%] | **0.0%** (0) [0.0%, 18.8%] |

*† Small-denominator flag (`N_hat < 10` papers): prefer Tier 1 (`L1 ∪ L2`) for stable rate comparisons.*

## 3. Stage E1 Deterministic Bucket vs. Stage E2 LLM Class (`n = 439` Unique T2 Papers)

| E1 Bucket | `L1` | `L2` | `L3` | `L4` | `L5` | Total |
|---|---:|---:|---:|---:|---:|---:|
| `E1_formal_thm_proof` | 135 | 32 | 4 | 8 | 11 | 190 |
| `E1_weak_or_unnumbered_math` | 6 | 2 | 5 | 60 | 116 | 189 |
| `E1_no_formal_claims` | 1 | 0 | 2 | 5 | 52 | 60 |

## 4. Mathlib-Blocked (`L2`) Barrier Breakdown (Across Sampled `L2` Papers)

- `pde_sobolev_continuum`: **11**
- `other`: **8**
- `stochastic_sde_ito`: **6**
- `measure_prob_asymptotics`: **5**
- `operator_spectral_infinite_dim`: **4**
