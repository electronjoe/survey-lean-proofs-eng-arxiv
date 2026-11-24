# Phase C1 Report: Stage-3/4 Classification of `+7` Categories & Full 15-Category Longitudinal Backfill (T0 / T1 / T2)

> **Phase C1 Complete (2026-11-24)** · Full 15-category whole-category census (**100% of `eess.*`**) across three matched 19-day windows (`T0: Nov 1–19, 2025`, `T1: May 1–19, 2026`, `T2: Nov 1–19, 2026`) · Frozen orig-8 DBs untouched (`data/slice_2025_11.db`, `data/slice_2026_05.db`, `data/survey.db`) · `+7` DBs: `data/scout_eng_tier12_{2025_11,2026_05,2026_11}.db` · Machine-readable summary: [`artifacts/phase_c1_15cat_longitudinal.json`](../artifacts/phase_c1_15cat_longitudinal.json)

## 1. Executive Summary & Decision-Gate Verdict

Executing Stage-3 static profiling and Stage-4 LLM classification (`flash`, upgraded 4-way rubric with `role_decision_gate` and `borderline_flag`) on the `+7` approved engineering categories in T2 (`34` net-new Stage-2 candidates) confirmed **`30` net-new Lean-contributing papers** (`32` total in `+7` T2 including `2` orig-8 overlaps `2611.05243` & `2611.14756`), overwhelmingly validating promotion to a **full 15-category longitudinal panel**. We then executed the zero-token T0 (`2025-11`) and T1 (`2026-05`) historical backfill (`+1,812` unique / `+1,577` net-new preprints; `99.12%` full-text coverage; all `16` failed fetches verified HTTP 404 withdrawals), profiled and classified all `6` net-new historical Stage-2 candidates (`1` in T0, `5` in T1), and verified `v1` vs. `v_latest` on every revised paper.

Six headline empirical findings emerge across the complete **15-category longitudinal panel (`12,613` unique preprints; `12,564` full-text screened = `99.61%`)**:

1. **Zero-Baseline Inflection Holds Universally Across All 15 Categories:** Contemporaneous `v1` Lean 4 adoption jumps from **0 / 3,164** (0.00%, UB 0.09%) in T0 → **7 / 4,146** (0.17%, [0.08%, 0.35%]) in T1 → **68 / 5,303** (1.28%, [1.01%, 1.62%]) in T2 (**7.6×** 6-month jump, strictly non-overlapping 95% CIs). Under `v_latest`, adoption jumps **2 → 11 → 69** (`0.06% → 0.27% → 1.30%`, **20.59× YoY**), while the Stage-2 Beyond-Lean FV control stays flat/declining (**1.23% → 1.13% → 1.04%**).
2. **100% of arXiv's `eess.*` Archive Measured Longitudinally (`3,558` Unique Papers Across T0–T2):** Across all three non-control signal/image/audio processing categories (`eess.SP` $\cup$ `eess.IV` $\cup$ `eess.AS`), Lean 4 adoption is **1 / 1,958** (0.05%, [0.01%, 0.29%]) across the entire 12-month panel (`0/559` in T0, `1/647` in T1 — solely manual `eess.SP` paper `2605.14610` — and `0/752` in T2, 95% UB `0.40%`), with **`eess.IV` + `eess.AS`** strictly **`0 / 795`** (`0.00%`, 95% UB `0.38%`). In T2, `100%` (`3/3`) of `eess.*` Lean papers sit exclusively in **`eess.SY`** (Systems & Control).
3. **4-Way Stratification Exposes Massive Pure-Math/TCS Concentration Inside `cs.GT` & `math.DS`:** Of the `32` confirmed Lean papers in `+7` T2 (`31` `v1`, `32` `v_latest`), **`25 / 32` (`78.1%`)** are **`pure_math_or_tcs`** (`13/15` in `math.DS`, `11/15` in `cs.GT`, `1/2` in `physics.flu-dyn`), and only **`7 / 32` (`21.9%`, `5` net-new)** are strict **`eng_algorithmic_proof`**. Thus `cs.GT`'s raw `9.04%` (`15/166`) confirmed rate drops to **`2.41%` (`4/166`)** strict `eng_algorithmic_proof`, and `math.DS`'s `3.89%` `v1` (`4.17%` `v_latest`) drops to **`0.56%` (`2/360`)** — proving why Track 1's 4-way taxonomy is indispensable!
4. **Strict `eng_algorithmic_proof` Curve Across All 15 Categories:** Contemporaneous `v1` strict `eng_algorithmic_proof` adoption jumps from **0 / 3,164** (0.00%, UB 0.09%) → **3 / 4,146** (0.07%, [0.02%, 0.21%]) → **26 / 5,303** (0.49%, [0.33%, 0.72%]) (**6.77×** in 6 months; strictly non-overlapping 95% CIs). Meanwhile `pure_math_or_tcs` explodes **9.12×** in 6 months (`0 → 3 → 35` `v1`, `36` `v_latest`), surpassing `eng_algorithmic_proof` (`26`) in the 15-category census.
5. **Five Persistent 0.00% Engineering Categories Across All 3 Slices (+ `cs.PF` Zero in `v1`):** **`cs.NI`**, **`cs.RO`**, **`eess.IV`**, **`eess.AS`**, **`cs.CE`** have **0 confirmed Lean papers** in T0, T1, *and* T2 (`v1` and `v_latest`), while **`cs.PF`** (`0/200`) also remains `0.00%` in contemporaneous `v1` across all 3 slices (its sole `v_latest` hit is `cs.PL` cross-list `2605.01140` *SoCal*, an `operational_system_fv` compiler paper whose Lean mechanization was added retroactively in `v2` on Nov 13, 2026).
6. **Retroactive Autoformalization Confirmed as a Cross-Domain Phenomenon (`n = 7` Across 15 Categories, `6` Cross-Window):** Alongside the 3 orig-8 retroactive papers (`2511.15517`, `2605.09552`, `2605.19531`), the `+7` backfill uncovered **3 additional cross-window retroactive autoformalizations** (`2511.13056` *7/9-MMS* in `cs.GT`, adding 119.1k owned LoC 353 days later in `v3` using GPT-5.6/6/6.1; `2605.03338` in `math.DS` +127 days; `2605.01140` in `cs.PF` +196 days) plus 1 within-month T2 `v2` addition (`2611.07818`, +18 days on Nov 23, 2026).

---

## 2. 15-Category Longitudinal Adoption Curve (T0 → T1 → T2)

### 2.1 Overall Panel Comparison (Orig-8 vs. `+7` vs. Combined 15-Category Union)

| Panel / Metric | T0 (`2025-11`) | T1 (`2026-05`) | T2 (`2026-11`) | 6-Mo / YoY Shift |
| :--- | :---: | :---: | :---: | :---: |
| **15-Cat Unique Papers (FT Coverage)** | 3,164 (99.24%) | 4,146 (99.64%) | 5,303 (99.81%) | **12,613 total** (99.61%) |
| **15-Cat Stage-2 Lean Candidates** | 4 (0.13%) | 24 (0.58%) | 89 (1.68%) | **13.3× YoY** |
| **15-Cat Confirmed Lean (`v1` contemp.)** | **0 / 3,164** (0.00%, UB 0.09%) | **7 / 4,146** (0.17%, [0.08%, 0.35%]) | **68 / 5,303** (1.28%, [1.01%, 1.62%]) | **7.6× (6-mo)** |
| **15-Cat Confirmed Lean (`v_latest`)** | **2 / 3,164** (0.06%, [0.02%, 0.23%]) | **11 / 4,146** (0.27%, [0.15%, 0.47%]) | **69 / 5,303** (1.30%, [1.03%, 1.64%]) | **20.59× YoY / 4.9× (6-mo)** |
| **15-Cat Beyond-Lean FV Control (Stage 2)** | 39 (1.23%) | 47 (1.13%) | 55 (1.04%) | Flat / declining |
| **`+7` Standalone (`v1` contemp.)** | **0 / 849** (0.00%, UB 0.35%) | **2 / 963** (0.21%, [0.06%, 0.75%]) | **31 / 1,339** (2.32%, [1.64%, 3.27%]) | **11.15× (6-mo)** |
| **`+7` Standalone (`v_latest`)** | **1 / 849** (0.12%, [0.02%, 0.66%]) | **4 / 963** (0.42%, [0.16%, 1.06%]) | **32 / 1,339** (2.39%, [1.70%, 3.35%]) | **20.29× YoY** |
| **100% `eess.*` Archive (`v1` contemp.)** | **0 / 1,009** (0.00%, UB 0.30%) | **2 / 1,083** (0.18%, [0.05%, 0.67%]) | **3 / 1,466** (0.20%, [0.07%, 0.60%]) | T2: 100% in `eess.SY` |
| **Non-Control `eess.*` (`SP∪IV∪AS`, `v_latest`)** | **0 / 559** (0.00%, UB 0.53%) | **1 / 647** (0.15%, [0.03%, 0.87%]) | **0 / 752** (0.00%, UB 0.40%) | **1 / 1,958** (0.05%, [0.01%, 0.29%]) (3-slice) |

### 2.2 4-Way Role Stratification Across the Full 15-Category Panel (`v1` Contemporaneous vs. `v_latest`)

| 4-Way Role Bucket | T0 `v1` (`v_lat`) | T1 `v1` (`v_lat`) | T2 `v1` (`v_lat`) | T2 Share (`v1`) | T2 Strict Core (Excl. Borderline) | 6-Mo Jump (`v1`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`eng_algorithmic_proof`** (Eng. Algorithmic Proof) | 0 (0) [0.00%] | 3 (5) [0.07%] | **26** (26) [**0.49%**, [0.33%, 0.72%]] | 38.2% | 25 (0.47%) | **6.77×** |
| **`operational_system_fv`** (Operational System FV) | 0 (1) [0.00%] | 1 (3) [0.02%] | **4** (4) [**0.08%**, [0.03%, 0.19%]] | 5.9% | 4 (0.08%) | **3.13×** |
| **`pure_math_or_tcs`** (Pure Math / TCS) | 0 (1) [0.00%] | 3 (3) [0.07%] | **35** (36) [**0.66%**, [0.47%, 0.92%]] | 51.5% | 26 (0.49%) | **9.12×** |
| **`meta_formalization_system`** (Meta-Formalization System) | 0 (0) [0.00%] | 0 (0) [0.00%] | **3** (3) [**0.06%**, [0.02%, 0.17%]] | 4.4% | 3 (0.06%) | — |
| **15-Category Total** | **0** (2) [0.00%] | **7** (11) [0.17%] | **68** (69) [**1.28%**] | 100.0% | — | **7.6×** |

---

## 3. Complete 15-Category Per-Category Longitudinal Matrix (T0 / T1 / T2)

| Category | Group | T0 Papers (`v1`/`v_lat`) | T1 Papers (`v1`/`v_lat`) | T2 Papers (`v1`/`v_lat`) | T2 `v1` Rate | T2 `eng_alg` | T2 `pure_math` | T2 `op_fv` | T2 `meta` | 3-Slice Total (`v1`/`v_lat`) |
| :--- | :---: | :---: | :---: | :---: | :---: | ---: | ---: | ---: | ---: | :---: |
| **`math.OC`** | Orig-8 | 410 (`0`/`0`) | 512 (`0`/`1`) | 724 (`19`/`19`) | **2.62%** | 13 | 3 | 0 | 3 | 1,646 (`19`/`20`) |
| **`cs.DC`** | Orig-8 | 223 (`0`/`1`) | 315 (`1`/`2`) | 335 (`6`/`6`) | **1.79%** | 0 | 5 | 1 | 0 | 873 (`7`/`9`) |
| **`cs.IT`** | Orig-8 | 209 (`0`/`0`) | 327 (`0`/`0`) | 338 (`6`/`6`) | **1.78%** | 4 | 2 | 0 | 0 | 874 (`6`/`6`) |
| **`cs.CR`** | Orig-8 | 406 (`0`/`1`) | 685 (`3`/`3`) | 629 (`7`/`7`) | **1.11%** | 3 | 1 | 3 | 0 | 1,720 (`10`/`11`) |
| **`eess.SY`** | Orig-8 | 476 (`0`/`0`) | 456 (`1`/`1`) | 738 (`3`/`3`) | **0.41%** | 2 | 1 | 0 | 0 | 1,670 (`4`/`4`) |
| **`eess.SP`** | Orig-8 | 338 (`0`/`0`) | 419 (`1`/`1`) | 462 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 1,219 (`1`/`1`) |
| **`cs.NI`** | Orig-8 | 136 (`0`/`0`) | 227 (`0`/`0`) | 196 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 559 (`0`/`0`) |
| **`cs.RO`** | Orig-8 | 532 (`0`/`0`) | 740 (`0`/`0`) | 1159 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 2,431 (`0`/`0`) |
| **`cs.GT`** | +7 New | 101 (`0`/`1`) | 151 (`2`/`2`) | 166 (`15`/`15`) | **9.04%** | 4 | 11 | 0 | 0 | 418 (`17`/`18`) |
| **`math.DS`** | +7 New | 189 (`0`/`0`) | 203 (`0`/`1`) | 360 (`14`/`15`) | **3.89%** | 2 | 13 | 0 | 0 | 752 (`14`/`16`) |
| **`physics.flu-dyn`** | +7 New | 181 (`0`/`0`) | 172 (`0`/`0`) | 278 (`2`/`2`) | **0.72%** | 1 | 1 | 0 | 0 | 631 (`2`/`2`) |
| **`cs.PF`** | +7 New | 43 (`0`/`0`) | 63 (`0`/`1`) | 94 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 200 (`0`/`1`) |
| **`eess.IV`** | +7 New | 159 (`0`/`0`) | 155 (`0`/`0`) | 175 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 489 (`0`/`0`) |
| **`eess.AS`** | +7 New | 81 (`0`/`0`) | 91 (`0`/`0`) | 134 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 306 (`0`/`0`) |
| **`cs.CE`** | +7 New | 103 (`0`/`0`) | 139 (`0`/`0`) | 146 (`0`/`0`) | **0.00%** | 0 | 0 | 0 | 0 | 388 (`0`/`0`) |

---

## 4. `+7` T2 Stage-3/4 Deep Dive: Quality, Scale (Raw vs. Paper-Owned LoC), Paradigms & AI Disclosure

- **T2 `+7` Stage-2 → Stage-4 Yield:** `36` Stage-2 candidates (`34` net-new) → **`32` confirmed `lean_contributed`** (`30` net-new, `31` contemporaneous `v1`; `4` non-contributing `lean_citation_or_discussion`: `2611.14974`, `2611.02237` [Rocq], `2611.02167`, `2611.26622`).
- **4-Way Composition of `+7` T2 Confirmed (`n = 32`):** **`25` `pure_math_or_tcs` (`78.1%`)**, **`7` `eng_algorithmic_proof` (`21.9%`; `5` net-new + `2` overlap)**, `0` `operational_system_fv`, `0` `meta_formalization_system`.
- **Tiers (`+7` T2 `v_latest`):** {'Tier3_Gold': 19, 'Tier1_Bronze': 10, 'Tier2_Silver': 3} — **`19 / 32` (`59.4%`) `Tier3_Gold`** (`19 / 24` = **`79.2%`** of public-repo papers!). Note that on all `7` `Tier3_Gold` repos with static `sorry > 0` (`2611.17277`, `2611.17223`, `2611.12862`, `2611.11805`, `2611.09066`, `2611.06106`, `2611.02465`), 100% of `sorry` occurrences sit exclusively inside frozen `Challenge.lean` / `Comparator/Challenges/*.lean` spec-lock files while all solution files have `0 sorry`.
- **Paradigms (`+7` T2 `v_latest`):** {'P4_speclock_solve_distill': 4, 'P1_paper_first_posthoc': 22, 'P3_blueprint_sync': 1, 'P0_opaque_or_unspecified': 5} — `P4_speclock_solve_distill` appears in `4` `+7` T2 papers (`2611.17223`, `2611.11805`, `2611.02465`, `2611.12862`) alongside `P3_blueprint_sync` (`2611.06106`, *PCF All The Way Down*), while `P1_paper_first_posthoc` remains dominant (`22/32`).
- **AI Assistance (`+7` T2 `v_latest`):** {'explicitly_yes': 26, 'unclear': 6} — **`26 / 32` (`81.2%`)** explicitly disclose AI/LLM assistance (`0` `explicitly_no`).
- **Codebase Scale & Vendoring Hygiene (`+7` T2, `24` scanned primary repos):** Raw LoC totals **`31,518,174`** (dominated by `farhadi94/online-edge-weighted-matching`'s `25.66M` LoC exploration logs under `research/lean/`), while **paper-owned LoC** (excluding verified `vendor/`, `research/`, `inspector/`, and upstream `OAI/` mirrors) totals **`5,046,857`** with median **`38,826` LoC** (vs. `29,005` in orig-8 T2).

### 4.1 Complete Inventory of Net-New Confirmed `+7` Lean Papers Across T0, T1, and T2 (`n = 35`)

| Slice | arXiv ID | Cat (`+7`) | `v1`? | `role_4way` (Border?) | Paradigm | Tier | AI? | Owned LoC (Raw) | Primary Artifact |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :---: | ---: | :--- |
| T0 | [2511.13056](https://arxiv.org/abs/2511.13056) | `cs.GT` (`cs.GT`) | No (`v3`) | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 119,124 (125,943) | `ARTHURCHOU/EconCSLib-7-9MMS` |
| T1 | [2605.12537](https://arxiv.org/abs/2605.12537) | `cs.LO` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier2_Silver` | `unclear` | 129 | `arxiv-anc/2605.12537` |
| T1 | [2605.06194](https://arxiv.org/abs/2605.06194) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | 37,513 | `DominikPeters/ABCVotingLean` |
| T1 | [2605.03338](https://arxiv.org/abs/2605.03338) | `cs.NE` (`math.DS`) | No (`v2`) | `eng_algorithmic_proof` | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | — | *appendix_only* |
| T1 | [2605.01140](https://arxiv.org/abs/2605.01140) | `cs.PL` (`cs.PF`) | No (`v2`) | `operational_system_fv` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `explicitly_yes` | — | *none* |
| T2 | [2611.24920](https://arxiv.org/abs/2611.24920) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 31,393 | `GO-EPFL/subadditive-online-combinatorial-auctions` |
| T2 | [2611.24787](https://arxiv.org/abs/2611.24787) | `math.OA` (`math.DS`) | Yes | `pure_math_or_tcs` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `explicitly_yes` | — | *none* |
| T2 | [2611.22216](https://arxiv.org/abs/2611.22216) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `unclear` | — | *broken_or_missing_repo* |
| T2 | [2611.20966](https://arxiv.org/abs/2611.20966) | `math.DS` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | — | *broken_or_missing_repo* |
| T2 | [2611.20890](https://arxiv.org/abs/2611.20890) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 189,249 (387,315) | `SimonWMackenzie/connected-envy-free-lean` |
| T2 | [2611.19243](https://arxiv.org/abs/2611.19243) | `math.DS` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 38,864 (82,993) | `Ryan-Hao-Jan/Veech-dichotomy-for-cover` |
| T2 | [2611.17292](https://arxiv.org/abs/2611.17292) | `cs.DS` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `explicitly_yes` | — | *none* |
| T2 | [2611.17277](https://arxiv.org/abs/2611.17277) | `math.DS` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 47,794 | `ckkogler/lpselfsimilar-lean` |
| T2 | [2611.17223](https://arxiv.org/abs/2611.17223) | `cs.DS` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P4_speclock_solve_distill` | `Tier3_Gold` | `explicitly_yes` | 10,541 | `radniazadeh/bernoulli-poly` |
| T2 | [2611.16763](https://arxiv.org/abs/2611.16763) | `math.AG` (`math.DS`) | Yes | `pure_math_or_tcs` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `explicitly_yes` | — | *none* |
| T2 | [2611.15751](https://arxiv.org/abs/2611.15751) | `math.CO` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 28,317 | `peterbanda/d-dim-shift-symmetry-in-ca` |
| T2 | [2611.15711](https://arxiv.org/abs/2611.15711) | `cs.DS` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | 5,909 | `relyt871/BWCA-Online-Lean` |
| T2 | [2611.14586](https://arxiv.org/abs/2611.14586) | `stat.ML` (`cs.GT`) | Yes | `eng_algorithmic_proof` | `P1_paper_first_posthoc` | `Tier2_Silver` | `explicitly_yes` | 1,969 | `zenodo/23768172` |
| T2 | [2611.12862](https://arxiv.org/abs/2611.12862) | `math.AP` (`physics.flu-dyn`) | Yes | `pure_math_or_tcs` *(border)* | `P4_speclock_solve_distill` | `Tier3_Gold` | `unclear` | 207,152 | `DavetheSlayer/OVNS-Lean` |
| T2 | [2611.11805](https://arxiv.org/abs/2611.11805) | `math.NA` (`math.DS`) | Yes | `eng_algorithmic_proof` | `P4_speclock_solve_distill` | `Tier3_Gold` | `explicitly_yes` | 42,036 (55,284) | `sgstepaniants/inelastic_hom_learn` |
| T2 | [2611.11641](https://arxiv.org/abs/2611.11641) | `cs.LO` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier2_Silver` | `unclear` | 174 | `zenodo/24060393` |
| T2 | [2611.11424](https://arxiv.org/abs/2611.11424) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 127,681 | `farhadi94/envy-free-division` |
| T2 | [2611.09615](https://arxiv.org/abs/2611.09615) | `cs.GT` (`cs.GT`) | Yes | `eng_algorithmic_proof` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 14,953 | `renatoppl/trace-square-root` |
| T2 | [2611.09066](https://arxiv.org/abs/2611.09066) | `math.DS` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 94,929 (134,934) | `sascha2718/lean-diagonal-antidiagonal` |
| T2 | [2611.08591](https://arxiv.org/abs/2611.08591) | `math-ph` (`math.DS`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier2_Silver` | `explicitly_yes` | 38,826 | `stacks-ai/papers` |
| T2 | [2611.07818](https://arxiv.org/abs/2611.07818) | `math.DS` (`math.DS`) | No (`v2`) | `pure_math_or_tcs` | `P0_opaque_or_unspecified` | `Tier1_Bronze` | `unclear` | — | *none* |
| T2 | [2611.07494](https://arxiv.org/abs/2611.07494) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 5,340 | `wuzhuangtai00/transparency-lean` |
| T2 | [2611.07395](https://arxiv.org/abs/2611.07395) | `math.AP` (`physics.flu-dyn`) | Yes | `eng_algorithmic_proof` | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | 12,309 | `michalshavitNYU/Rigorously-certified-water-waves` |
| T2 | [2611.06896](https://arxiv.org/abs/2611.06896) | `cs.DS` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier1_Bronze` | `explicitly_yes` | 2,974,079 (28,670,443) | `farhadi94/online-edge-weighted-matching` |
| T2 | [2611.06106](https://arxiv.org/abs/2611.06106) | `math.AG` (`math.DS`) | Yes | `pure_math_or_tcs` | `P3_blueprint_sync` | `Tier3_Gold` | `explicitly_yes` | 202,819 | `tdupu/pcfawd-formalization` |
| T2 | [2611.05221](https://arxiv.org/abs/2611.05221) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 585,317 | `AbheekG/colonel-blotto-lean` |
| T2 | [2611.04934](https://arxiv.org/abs/2611.04934) | `cs.GT` (`cs.GT`) | Yes | `pure_math_or_tcs` *(border)* | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 53,595 | `philippwarode/contract-design-polymatroids-lean` |
| T2 | [2611.04575](https://arxiv.org/abs/2611.04575) | `math.CO` (`math.DS`) | Yes | `pure_math_or_tcs` | `P1_paper_first_posthoc` | `Tier3_Gold` | `explicitly_yes` | 12,659 | `HamedMousaviMath/Lean-Formalization-Polynomial-Configurations-and-Pointwise-Averages-Along-Piatetski--Shapiro-Primes` |
| T2 | [2611.04545](https://arxiv.org/abs/2611.04545) | `cs.GT` (`cs.GT`) | Yes | `eng_algorithmic_proof` | `P1_paper_first_posthoc` | `Tier1_Bronze` | `unclear` | — | *broken_or_missing_repo* |
| T2 | [2611.02465](https://arxiv.org/abs/2611.02465) | `math.CA` (`math.DS`) | Yes | `pure_math_or_tcs` | `P4_speclock_solve_distill` | `Tier3_Gold` | `explicitly_yes` | 309,078 (788,583) | `anastasiosfragkosmath/Pointwise-Ergodic-Theorems-Along-floor-p-c-Palomar-Submission` |

---

## 5. Retroactive Autoformalization Ledger (Full 15-Category Panel)

| Slice | arXiv ID | Panel | Cat (`15-cat`) | `role_4way` | `v1` Date | Lean Added | Owned LoC | Evidence Note |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | ---: | :--- |
| T0 | [2511.13056](https://arxiv.org/abs/2511.13056) | `plus7_net_new` | `cs.GT` (`cs.GT`) | `pure_math_or_tcs` | 2025-11-17 | `v3` (2026-11-05) (`+353d`) | 119,124 | v1 HTML (86.3k chars) has 0 Lean mentions; v3 (Nov 2026) adds 125.9k LoC EconCSLib 7/9-MMS Lean 4 formalization using GPT-5.6/6/6.1. |
| T0 | [2511.15517](https://arxiv.org/abs/2511.15517) | `orig8` | `cs.CR` (`cs.CR,cs.DC`) | `operational_system_fv` | 2025-11-19 | `v2` (2026-06-29) | — | Verified orig-8 retroactive formalization (see longitudinal_summary.json). |
| T1 | [2605.01140](https://arxiv.org/abs/2605.01140) | `plus7_net_new` | `cs.PL` (`cs.PF`) | `operational_system_fv` | 2026-05-01 | `v2` (2026-11-13) (`+196d`) | — | v1 HTML (125.8k chars) has 0 Lean mentions; v2 (Nov 2026) adds Claude-assisted Lean 4 type-safety mechanization for SoCal. |
| T1 | [2605.03338](https://arxiv.org/abs/2605.03338) | `plus7_net_new` | `cs.NE` (`math.DS`) | `eng_algorithmic_proof` | 2026-05-05 | `v2` (2026-09-09) (`+127d`) | — | v1 HTML (49.8k chars) has 0 Lean mentions; v2 (Sep 2026) adds Appendix N.1 Lean 4/Mathlib supplementary formalization. |
| T1 | [2605.09552](https://arxiv.org/abs/2605.09552) | `orig8` | `math.OC` (`math.OC`) | `eng_algorithmic_proof` | 2026-05-10 | `v2` (2026-10-27) | 340,325 | Verified orig-8 retroactive formalization (see longitudinal_summary.json). |
| T1 | [2605.19531](https://arxiv.org/abs/2605.19531) | `orig8` | `cs.DC` (`cs.DC`) | `operational_system_fv` | 2026-05-19 | `v2` (2026-11-02) | 34,257 | Verified orig-8 retroactive formalization (see longitudinal_summary.json). |
| T2 | [2611.07818](https://arxiv.org/abs/2611.07818) | `plus7_net_new` | `math.DS` (`math.DS`) | `pure_math_or_tcs` | 2026-11-05 | `v2` (2026-11-23) (`+18d`) | — | v1 HTML has 0 Lean mentions; v2 (Nov 23, 2026, 4 days after the Nov 19 window) adds acknowledgement of conditional Lean 4 formalization of v1. |

---

## 6. Targeted Phase C2 Queue (Net-New `+7` `eng_algorithmic_proof` Public Repos)

Because 4-way stratification cleanly separates `pure_math_or_tcs` (`25/32`) from strict `eng_algorithmic_proof` (`5` net-new T2 papers, `4` with public Lean repos; `2611.04545` has a 404/private repo), **keeping Phase-2 Layer-A semantic auditing and compact Docker kernel verification (`<15k` LoC) 100% exhaustive over the 15-category engineering cohort requires auditing only 4 repositories** (3 compact `<15k` LoC + 1 medium `42.0k` owned LoC):

| arXiv ID | Cat (`+7`) | Primary Repo | Owned LoC | Compact `<15k` Sandbox? | Paradigm / Tier |
| :--- | :--- | :--- | ---: | :---: | :--- |
| [2611.14586](https://arxiv.org/abs/2611.14586) | `stat.ML` (`cs.GT`) | `zenodo/23768172` (zenodo) | 1,969 | Yes | `P1_paper_first_posthoc` / `Tier2_Silver` |
| [2611.11805](https://arxiv.org/abs/2611.11805) | `math.NA` (`math.DS`) | `sgstepaniants/inelastic_hom_learn` (github) | 42,036 | No (>15k) | `P4_speclock_solve_distill` / `Tier3_Gold` |
| [2611.09615](https://arxiv.org/abs/2611.09615) | `cs.GT` (`cs.GT`) | `renatoppl/trace-square-root` (github) | 14,953 | Yes | `P1_paper_first_posthoc` / `Tier3_Gold` |
| [2611.07395](https://arxiv.org/abs/2611.07395) | `math.AP` (`physics.flu-dyn`) | `michalshavitNYU/Rigorously-certified-water-waves` (github) | 12,309 | Yes | `P1_paper_first_posthoc` / `Tier1_Bronze` |
