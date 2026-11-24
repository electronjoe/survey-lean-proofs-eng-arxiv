# Track 1 Sensitivity Analysis: 4-Way Role Decomposition of Confirmed Lean 4 Preprints (T0–T2, n = 47)

> **Zero-Token Phase A1 Deliverable** · Rubric: [`docs/track1_4way_coding_rubric.md`](../docs/track1_4way_coding_rubric.md) · Adjudication: [`artifacts/human_annotations/track1_4way_adjudication.json`](../artifacts/human_annotations/track1_4way_adjudication.json) · Machine-readable output: [`artifacts/track1_sensitivity_summary.json`](../artifacts/track1_sensitivity_summary.json) · Phase B2 Dual-Rater Template: [`artifacts/human_annotations/track1_4way_coding_blank.csv`](../artifacts/human_annotations/track1_4way_coding_blank.csv)

## 1. Executive Summary — What Holds vs. What Shifts Under Strict `eng_algorithmic_proof`

Re-tabulating all **47** confirmed Lean 4 preprints (`T0`: 1 `v_latest` / 0 `v1`; `T1`: 7 `v_latest` / 5 `v1`; `T2`: 39 `v1` = `v_latest`) across the sharpened 4-way taxonomy (`eng_algorithmic_proof`, `operational_system_fv`, `pure_math_or_tcs`, `meta_formalization_system`) yields **five decisive empirical conclusions**:

1. **The 2026 Adoption Inflection Is Statistically Robust Even Under Strict Engineering-Only Filtering:** Restricting strictly to `eng_algorithmic_proof` moves the contemporaneous `v1` curve from **`0/2,435` (0.00%, 95% UB 0.12%) → `3/3,298` (0.09%, 95% CI [0.03%, 0.27%]) → `21/4,104` (0.51%, 95% CI [0.33%, 0.78%])** — a **5.62×** rate jump in 6 months with **strictly non-overlapping 95% Wilson CIs**. Even under an ultra-strict *non-borderline core* stress test (excluding all 8 borderline papers across T1–T2, leaving `16` T2 vs. `1` T1), the 6-month rate still jumps **12.87×** (`0.03% [0.01%, 0.17%] → 0.39% [0.24%, 0.63%]`, still non-overlapping!).
2. **Total Owned LoC Was Heavily Dominated by Pure-TCS & Meta-Systems (86.2%), While the *Median* Engineering Scale Jump (`39.2×`) Is Untouched:** Across the 28 scanned T2 repos (`3,104,750` owned LoC), **`pure_math_or_tcs`** (`1,827,866` LoC, **58.9%**, median `158,351`) and **`meta_formalization_system`** (`848,591` LoC, **27.3%**, median `424,295`) account for **86.2%** of all lines of code. Strict **`eng_algorithmic_proof`** contributes **`416,099` LoC (13.4%)** across 15 scanned repos, yet its median codebase scale still leaps from **`611` → `23,932` LoC (39.17×)** — virtually identical to the pooled `38.7×` shift (`749 → 29,005`), with no single contemporaneous T2 engineering paper exceeding `81.5k` LoC.
3. **`Tier3_Gold` Quality Share Actually *Increases* Under Strict Engineering Filtering:** `Tier3_Gold` rises from **48.7%** (`19/39`) pooled to **`52.4%` (11/21)** among T2 `eng_algorithmic_proof` papers (**73.3%** of scanned engineering repos!), outperforming `pure_math_or_tcs` (`45.5%`), `operational_system_fv` (`50.0%`), and `meta_formalization_system` (`33.3%`). Meanwhile, `P4` spec-lock splits cleanly: **1/3** (`2611.13872` *LongTails*) is a meta-system, leaving **2/21 (9.5%)** in `eng_algorithmic_proof` (`2611.04876`, `2611.14475`).
4. **Disciplinary Concentration Sharpens Dramatically (`cs.DC` Drops to 0 Pure-Engineering Papers):** Under the 4-way split, **100% of T2 `cs.DC` Lean papers (6/6)** are either `pure_math_or_tcs` (5) or `operational_system_fv` (1 — `cs.DB` DBLog), leaving **0** `eng_algorithmic_proof` papers in `cs.DC`. Strict engineering adoption is overwhelmingly concentrated in **`math.OC` (`13/724 = 1.80%`)**, **`cs.IT` (`4/338 = 1.18%`)**, **`cs.CR` (`3/629 = 0.48%`)**, and **`eess.SY` (`2/738 = 0.27%`)**.
5. **Phase 2 Layer-A Semantic Fidelity Has `0/15` Severe Failures Among Author-Owned T2 `eng_algorithmic_proof` Repos:** The sole `material_undisclosed_drift_or_risk` finding across all 23 Phase-2 audits (`2611.26272` *Paper2Lean*) belongs to **`meta_formalization_system`**, not `eng_algorithmic_proof`. Explicit AI disclosure in T2 is **`66.7%`** (`14/21`) for `eng_algorithmic_proof`, vs. **`90.9%`** (`10/11`) for `pure_math_or_tcs` and **`100.0%`** (`3/3`) for `meta_formalization_system`.

---

## 2. Stratified Longitudinal Adoption Curves (T0 → T1 → T2)

### 2.1 Contemporaneous (`v1`-at-Submission) Adoption Rates & 95% CIs

| Population / 4-Way Bucket | T0: Nov 2025 (N=2,435) | T1: May 2026 (N=3,298) | T2: Nov 2026 (N=4,104) | T2 Share of Confirmed | 6-Mo Rate Shift (`T1→T2`) |
| :--- | :--- | :--- | :--- | ---: | :--- |
| **Pooled (All 4 Buckets)** | 0 (0.00%, UB 0.12%) | 5 (0.15%, [0.06%, 0.35%]) | 39 (0.95%, [0.70%, 1.30%]) | 100.0% | **6.27×** |
| **1. `eng_algorithmic_proof` (Core Target)** | 0 (0.00%, UB 0.12%) | 3 (0.09%, [0.03%, 0.27%]) | 21 (0.51%, [0.33%, 0.78%]) | 53.8% | **5.62×** |
| ↳ *Strict Core (excl. borderline items)* | 0 (0.00%, UB 0.12%) | 1 (0.03%, [0.01%, 0.17%]) | 16 (0.39%, [0.24%, 0.63%]) | 41.0% | **12.87×** |
| 2. `operational_system_fv` | 0 (0.00%, UB 0.12%) | 1 (0.03%, [0.01%, 0.17%]) | 4 (0.10%, [0.04%, 0.25%]) | 10.3% | **3.22×** |
| 3. `pure_math_or_tcs` | 0 (0.00%, UB 0.12%) | 1 (0.03%, [0.01%, 0.17%]) | 11 (0.27%, [0.15%, 0.48%]) | 28.2% | **8.84×** |
| 4. `meta_formalization_system` | 0 (0.00%, UB 0.12%) | 0 (0.00%, UB 0.09%) | 3 (0.07%, [0.02%, 0.21%]) | 7.7% | 0 → active |

### 2.2 Latest-Revision (`v_latest`, Including 3 Retroactive `v2` Formalizations)

| Population / 4-Way Bucket | T0 `v_latest` (N=2,435) | T1 `v_latest` (N=3,298) | T2 `v_latest` (N=4,104) | Retroactive `v2` Additions |
| :--- | :--- | :--- | :--- | :--- |
| **Pooled (All 4 Buckets)** | 1 (0.04%, [0.01%, 0.23%]) | 7 (0.21%, [0.10%, 0.44%]) | 39 (0.95%, [0.70%, 1.30%]) | `2511.15517` (T0), `2605.09552` & `2605.19531` (T1) |
| **1. `eng_algorithmic_proof`** | 0 (0.00%, UB 0.12%) | 4 (0.12%, [0.05%, 0.31%]) | 21 (0.51%, [0.33%, 0.78%]) | `2605.09552` (*Phases of Muon*, T1, 340.3k LoC) |
| ↳ *Strict Core (excl. borderline)* | 0 (0.00%, UB 0.12%) | 2 (0.06%, [0.02%, 0.22%]) | 16 (0.39%, [0.24%, 0.63%]) | `2605.09552` (T1) |
| 2. `operational_system_fv` | 1 (0.04%, [0.01%, 0.23%]) | 2 (0.06%, [0.02%, 0.22%]) | 4 (0.10%, [0.04%, 0.25%]) | `2511.15517` (T0 Beluga), `2605.19531` (T1 PODC, 34.3k LoC) |
| 3. `pure_math_or_tcs` | 0 (0.00%, UB 0.12%) | 1 (0.03%, [0.01%, 0.17%]) | 11 (0.27%, [0.15%, 0.48%]) | None |
| 4. `meta_formalization_system` | 0 (0.00%, UB 0.12%) | 0 (0.00%, UB 0.09%) | 3 (0.07%, [0.02%, 0.21%]) | None |

---

## 3. T2 Codebase Scale, LoC Concentration, Paradigms, Tiers & AI Disclosure by 4-Way Bucket

| 4-Way Bucket (T2 Nov 2026) | Papers | Scanned Repos | Total Owned LoC (% of 3.10M) | Median Owned LoC (Range) | `Tier3_Gold` (of Bucket / Scanned) | Paradigms (`P1/P2/P3/P4/P0`) | Explicit AI (`yes/unc/no`) |
| :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| **1. `eng_algorithmic_proof`** | 21 | 15 | 416,099 (13.4%) | **23,932** (528–81,481) | 11 (52.4% / 73.3%) | `14/0/0/2/5` | 14/7/0 (66.7%) |
| ↳ *Strict Core (non-borderline)* | 16 | 12 | 357,500 (11.5%) | **18,084** (528–81,481) | 10 (62.5% / 83.3%) | `12/0/0/1/3` | 10/6/0 (62.5%) |
| 2. `operational_system_fv` | 4 | 2 | 12,194 (0.4%) | **6,097** (1,332–10,862) | 2 (50.0% / 100.0%) | `3/0/0/0/1` | 3/1/0 (75.0%) |
| 3. `pure_math_or_tcs` | 11 | 9 | 1,827,866 (58.9%) | **158,351** (2,191–929,448) | 5 (45.5% / 55.6%) | `10/0/0/0/1` | 10/1/0 (90.9%) |
| 4. `meta_formalization_system` | 3 | 2 | 848,591 (27.3%) | **424,295** (151,214–697,377) | 1 (33.3% / 50.0%) | `1/0/0/1/1` | 3/0/0 (100.0%) |
| **Pooled T2 Total** | 39 | 28 | 3,104,750 (100.0%) | **29,005** (528–929,448) | 19 (48.7% / 67.9%) | `28/0/0/3/8` | 30/9/0 (76.9%) |

### Scale Shift Comparison (`T1 v1 → T2 v1`)
- **Pooled:** median `749` (3 repos) → `29,005` (28 repos) = **38.7×**.
- **Strict `eng_algorithmic_proof`:** median `611` (2 repos: `473` & `749`) → `23,932` (15 repos) = **39.17×**.
- **Strict Core (non-borderline `eng_algorithmic_proof`):** median `0` (0 scanned T1 repos — `2605.03034` has no public repo) → `18,084` (12 repos, total `357,500` LoC, range `528`–`81,481`).

---

## 4. T2 Per-Category Breakdown Across the 8 Target Categories

| Category | T2 Total | Pooled Lean (%) | `eng_algorithmic_proof` (%) | `operational_system_fv` | `pure_math_or_tcs` | `meta_formalization_system` |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `math.OC` | 724 | 19 (2.62%) | **13 (1.80%)** | 0 | 3 | 3 |
| `cs.DC` | 335 | 6 (1.79%) | **0 (0.00%)** | 1 | 5 | 0 |
| `cs.IT` | 338 | 6 (1.78%) | **4 (1.18%)** | 0 | 2 | 0 |
| `cs.CR` | 629 | 7 (1.11%) | **3 (0.48%)** | 3 | 1 | 0 |
| `eess.SY` | 738 | 3 (0.41%) | **2 (0.27%)** | 0 | 1 | 0 |
| `eess.SP` | 462 | 0 (0.00%) | **0 (0.00%)** | 0 | 0 | 0 |
| `cs.NI` | 196 | 0 (0.00%) | **0 (0.00%)** | 0 | 0 | 0 |
| `cs.RO` | 1159 | 0 (0.00%) | **0 (0.00%)** | 0 | 0 | 0 |

*(Category counts sum to >39 because papers cross-listed across multiple target categories are counted in each matched category, consistent with `report_longitudinal.py`.)*

---

## 5. Phase 2 Layer-A Audits (n = 23) & Sandboxed Docker Builds (n = 14) by 4-Way Bucket

### 5.1 Phase 2 Adversarial Layer-A Semantic Fidelity Audits (`n = 23` Total: 20 T2 + 3 T1)

| 4-Way Bucket | Audited Repos (`T2` / `T1 v1` / `T1 retro`) | `high_faithful` | `mostly_faithful` | `partial_or_weakened` | `material_undisclosed_drift` | Non-Vacuity Witnesses |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| `eng_algorithmic_proof` | **18** (`15` / `2` / `1`) | 5 | 8 | 5 | **0** | 12/18 |
| `operational_system_fv` | **0** (`0` / `0` / `0`) | 0 | 0 | 0 | **0** | 0/0 |
| `pure_math_or_tcs` | **3** (`3` / `0` / `0`) | 1 | 2 | 0 | **0** | 2/3 |
| `meta_formalization_system` | **2** (`2` / `0` / `0`) | 1 | 0 | 0 | **1** | 1/2 |

### 5.2 Sandboxed Docker Dynamic Kernel Verification (`n = 14` Compact Repos `<15k` LoC)

| 4-Way Bucket | Attempted | OOTB Pass | OOTB Axiom-Clean | Non-Std Axioms / `sorryAx` | Packaging / Local-Dep Fail (Synth. Pass) | Theorems Checked (OOTB / Incl. Synth.) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `eng_algorithmic_proof` | 8 | 5 | 5 | 0 | 3 (2) | 1,439 / 1,503 |
| `operational_system_fv` | 3 | 3 | 2 | 1 | 0 (0) | 714 / 714 |
| `pure_math_or_tcs` | 3 | 3 | 2 | 1 | 0 (0) | 1,037 / 1,037 |
| `meta_formalization_system` | 0 | 0 | 0 | 0 | 0 (0) | 0 / 0 |

*(All 5 OOTB-passing compact `eng_algorithmic_proof` repos — plus both packaging-only synthetic passes `2611.18220` and `2611.23762` — are 100% axiom-clean; both non-standard-axiom/sorryAx hits occurred outside `eng_algorithmic_proof`: `2605.16407` in `operational_system_fv` and `2611.16690` in `pure_math_or_tcs`.)*

---

## 6. Old 3-Way → New 4-Way Migration Matrix & Stage-4 IRR Reconciliation Diagnostic

### 6.1 Migration Matrix (All 47 Confirmed Papers `v_latest`; T2 `n = 39` in Parentheses)

| Old v0.6 `paper_domain_role` | `eng_algorithmic_proof` | `operational_system_fv` | `pure_math_or_tcs` | `meta_formalization_system` | Total |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `engineering_math_proof` | 25 (21) | 0 (0) | 4 (4) | 3 (3) | **32 (28)** |
| `software_or_system_fv` | 0 (0) | 7 (4) | 0 (0) | 0 (0) | **7 (4)** |
| `pure_tcs_or_math` | 0 (0) | 0 (0) | 8 (7) | 0 (0) | **8 (7)** |

### 6.2 How the 4-Way Rubric Resolves the 9 v0.6 Blinded IRR Disagreements (`annotator_1` vs. LLM)

| arXiv ID | `annotator_1` (Old 3-Way) | LLM (Old 3-Way) | Adjudicated `role_4way` | Resolution Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| `2611.23080` | `pure_tcs_or_math` | `engineering_math_proof` | `meta_formalization_system` | `resolved_by_new_meta_bucket` (`G1_meta`) |
| `2611.13872` | `pure_tcs_or_math` | `engineering_math_proof` | `meta_formalization_system` | `resolved_by_new_meta_bucket` (`G1_meta`) |
| `2605.14610` | `pure_tcs_or_math` | `engineering_math_proof` | `eng_algorithmic_proof` *(borderline)* | `clarified_by_explicit_boundary_rule` (`G3_eng_algorithmic`) |
| `2605.19531` | `pure_tcs_or_math` | `software_or_system_fv` | `operational_system_fv` *(borderline)* | `clarified_by_explicit_boundary_rule` (`G2_operational_fv`) |
| `2605.02856` | `software_or_system_fv` | `engineering_math_proof` | `eng_algorithmic_proof` *(borderline)* | `clarified_by_explicit_boundary_rule` (`G3_eng_algorithmic`) |
| `2611.09050` | `pure_tcs_or_math` | `engineering_math_proof` | `pure_math_or_tcs` | `aligned_with_human_rater` (`G4_pure_math_tcs`) |
| `2611.01761` | `engineering_math_proof` | `pure_tcs_or_math` | `pure_math_or_tcs` | `clarified_by_explicit_boundary_rule` (`G4_pure_math_tcs`) |
| `2611.08172` | `pure_tcs_or_math` | `engineering_math_proof` | `pure_math_or_tcs` | `aligned_with_human_rater` (`G4_pure_math_tcs`) |
| `2611.01384` | `pure_tcs_or_math` | `engineering_math_proof` | `eng_algorithmic_proof` *(borderline)* | `clarified_by_explicit_boundary_rule` (`G3_eng_algorithmic`) |

- **Immediate structural fixes (4/9):** `2` meta-systems (`2611.13872`, `2611.23080`) move to the new `meta_formalization_system` bucket that `annotator_1` explicitly requested, and `2` pure-math cross-lists (`2611.08172`, `2611.09050`) align directly with `annotator_1` as `pure_math_or_tcs`.
- **Explicit boundary-rule clarifications (5/9):** `5` remaining items (`2605.02856`, `2605.14610`, `2605.19531`, `2611.01384`, `2611.01761`) map 1-to-1 to Rules B2–B4 in [`docs/track1_4way_coding_rubric.md`](../docs/track1_4way_coding_rubric.md) and will be independently re-coded by `annotator_1` and `annotator_2` in Phase B2.

---

## 7. Complete 47-Paper 4-Way Adjudication Inventory (`T0 + T1 + T2`, `v_latest`)

| Slice | arXiv ID | Timing | Prim. (`Targets`) | Old 3-Way | New `role_4way` | `verification_object` | Borderline? | Owned LoC | Tier / Par. |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | ---: | :--- |
| T0 | [2511.15517](https://arxiv.org/abs/2511.15517) | Retro `v2` | `cs.CR` (`cs.CR,cs.DC`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | — | Bronze / `P0` |
| T1 | [2605.02856](https://arxiv.org/abs/2605.02856) | `v1` | `cs.CR` (`cs.CR`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | Yes (`operational_system_fv`) | 749 | Silver / `P2` |
| T1 | [2605.03034](https://arxiv.org/abs/2605.03034) | `v1` | `cs.AI` (`cs.CR,eess.SY`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `physical_or_control_model` | No | — | Bronze / `P0` |
| T1 | [2605.05801](https://arxiv.org/abs/2605.05801) | `v1` | `cs.LO` (`cs.DC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | — | Bronze / `P1` |
| T1 | [2605.09552](https://arxiv.org/abs/2605.09552) | Retro `v2` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 340,325 | Gold / `P1` |
| T1 | [2605.14610](https://arxiv.org/abs/2605.14610) | `v1` | `stat.ME` (`eess.SP`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `numerical_or_stat_method` | Yes (`pure_math_or_tcs`) | 473 | Silver / `P1` |
| T1 | [2605.16407](https://arxiv.org/abs/2605.16407) | `v1` | `cs.LO` (`cs.CR`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | 2,381 | Bronze / `P1` |
| T1 | [2605.19531](https://arxiv.org/abs/2605.19531) | Retro `v2` | `cs.DC` (`cs.DC`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | Yes (`pure_math_or_tcs`) | 34,257 | Gold / `P1` |
| T2 | [2611.01384](https://arxiv.org/abs/2611.01384) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | Yes (`pure_math_or_tcs`) | — | Bronze / `P0` |
| T2 | [2611.01761](https://arxiv.org/abs/2611.01761) | `v1` | `cs.DC` (`cs.DC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 158,351 | Gold / `P1` |
| T2 | [2611.02057](https://arxiv.org/abs/2611.02057) | `v1` | `cs.DS` (`cs.DC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 166,354 | Bronze / `P1` |
| T2 | [2611.02169](https://arxiv.org/abs/2611.02169) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | Yes (`pure_math_or_tcs`) | — | Bronze / `P0` |
| T2 | [2611.02256](https://arxiv.org/abs/2611.02256) | `v1` | `cs.DC` (`cs.DC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 2,191 | Silver / `P1` |
| T2 | [2611.04561](https://arxiv.org/abs/2611.04561) | `v1` | `cs.DC` (`cs.DC,eess.SY`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 929,448 | Gold / `P1` |
| T2 | [2611.04876](https://arxiv.org/abs/2611.04876) | `v1` | `cs.CR` (`cs.CR`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 81,481 | Gold / `P4` |
| T2 | [2611.05136](https://arxiv.org/abs/2611.05136) | `v1` | `cs.CC` (`cs.CR`) | `engineering_math_proof` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 219,688 | Silver / `P1` |
| T2 | [2611.05243](https://arxiv.org/abs/2611.05243) | `v1` | `cs.LG` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 11,204 | Gold / `P1` |
| T2 | [2611.08172](https://arxiv.org/abs/2611.08172) | `v1` | `cs.IT` (`cs.IT`) | `engineering_math_proof` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 200,335 | Gold / `P1` |
| T2 | [2611.09050](https://arxiv.org/abs/2611.09050) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 139,600 | Gold / `P1` |
| T2 | [2611.09169](https://arxiv.org/abs/2611.09169) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | — | Bronze / `P0` |
| T2 | [2611.10810](https://arxiv.org/abs/2611.10810) | `v1` | `cs.DB` (`cs.DC`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | 10,862 | Gold / `P1` |
| T2 | [2611.10902](https://arxiv.org/abs/2611.10902) | `v1` | `eess.SY` (`eess.SY`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 2,068 | Gold / `P1` |
| T2 | [2611.11713](https://arxiv.org/abs/2611.11713) | `v1` | `cs.IT` (`cs.IT`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 69,875 | Gold / `P1` |
| T2 | [2611.12585](https://arxiv.org/abs/2611.12585) | `v1` | `math.NA` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `numerical_or_stat_method` | No | 60,664 | Silver / `P1` |
| T2 | [2611.12680](https://arxiv.org/abs/2611.12680) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 23,932 | Gold / `P1` |
| T2 | [2611.13584](https://arxiv.org/abs/2611.13584) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 55,300 | Gold / `P1` |
| T2 | [2611.13585](https://arxiv.org/abs/2611.13585) | `v1` | `cs.DS` (`math.OC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | — | Bronze / `P1` |
| T2 | [2611.13872](https://arxiv.org/abs/2611.13872) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`meta_formalization_system`** | `meta_proving_pipeline` | No | 697,377 | Gold / `P4` |
| T2 | [2611.14475](https://arxiv.org/abs/2611.14475) | `v1` | `math.FA` (`cs.IT`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | Yes (`pure_math_or_tcs`) | 29,967 | Gold / `P4` |
| T2 | [2611.14756](https://arxiv.org/abs/2611.14756) | `v1` | `math.DS` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `physical_or_control_model` | No | 670 | Gold / `P1` |
| T2 | [2611.15128](https://arxiv.org/abs/2611.15128) | `v1` | `cs.IT` (`cs.CR,cs.IT`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | 4,963 | Gold / `P1` |
| T2 | [2611.15201](https://arxiv.org/abs/2611.15201) | `v1` | `cs.DC` (`cs.DC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 5,307 | Gold / `P1` |
| T2 | [2611.15431](https://arxiv.org/abs/2611.15431) | `v1` | `quant-ph` (`cs.IT`) | `engineering_math_proof` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | — | Bronze / `P0` |
| T2 | [2611.16690](https://arxiv.org/abs/2611.16690) | `v1` | `math.AG` (`math.OC`) | `pure_tcs_or_math` | **`pure_math_or_tcs`** | `abstract_math_or_tcs_theorem` | No | 6,592 | Silver / `P1` |
| T2 | [2611.16781](https://arxiv.org/abs/2611.16781) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `physical_or_control_model` | No | 34,579 | Silver / `P1` |
| T2 | [2611.18220](https://arxiv.org/abs/2611.18220) | `v1` | `eess.SY` (`eess.SY`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `physical_or_control_model` | No | 528 | Gold / `P1` |
| T2 | [2611.18455](https://arxiv.org/abs/2611.18455) | `v1` | `stat.ML` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `numerical_or_stat_method` | No | 12,236 | Gold / `P1` |
| T2 | [2611.19551](https://arxiv.org/abs/2611.19551) | `v1` | `cs.CR` (`cs.CR`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | 1,332 | Gold / `P1` |
| T2 | [2611.20131](https://arxiv.org/abs/2611.20131) | `v1` | `math.NA` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `numerical_or_stat_method` | No | — | Bronze / `P0` |
| T2 | [2611.20298](https://arxiv.org/abs/2611.20298) | `v1` | `cs.PL` (`cs.CR`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | — | Bronze / `P1` |
| T2 | [2611.22468](https://arxiv.org/abs/2611.22468) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | — | Bronze / `P0` |
| T2 | [2611.22732](https://arxiv.org/abs/2611.22732) | `v1` | `cs.CR` (`cs.CR`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | No | — | Bronze / `P1` |
| T2 | [2611.23080](https://arxiv.org/abs/2611.23080) | `v1` | `cs.AI` (`math.OC`) | `engineering_math_proof` | **`meta_formalization_system`** | `meta_proving_pipeline` | No | — | Bronze / `P0` |
| T2 | [2611.23762](https://arxiv.org/abs/2611.23762) | `v1` | `quant-ph` (`cs.IT`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `algorithm_convergence_or_bound` | Yes (`pure_math_or_tcs`) | 589 | Silver / `P1` |
| T2 | [2611.25599](https://arxiv.org/abs/2611.25599) | `v1` | `cs.CR` (`cs.CR`) | `software_or_system_fv` | **`operational_system_fv`** | `operational_sw_hw_db_protocol` | No | — | Bronze / `P0` |
| T2 | [2611.26140](https://arxiv.org/abs/2611.26140) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`eng_algorithmic_proof`** | `physical_or_control_model` | Yes (`pure_math_or_tcs`) | 28,043 | Bronze / `P1` |
| T2 | [2611.26272](https://arxiv.org/abs/2611.26272) | `v1` | `math.OC` (`math.OC`) | `engineering_math_proof` | **`meta_formalization_system`** | `meta_proving_pipeline` | No | 151,214 | Silver / `P1` |
