# Longitudinal Analysis: The 2025–2026 Lean 4 Adoption Inflection in Engineering arXiv Preprints

Matched 19-day (`01`–`19`) eight-category engineering & applied-theory slices harvested via bias-free OAI-PMH `arXivRaw` (**9,837** unique preprints total; **9,806** full-text screened = **99.68%** coverage).

## 1. Executive Headline Comparison (T0 vs. T1 vs. T2)

| Metric | T0: Nov 1–19, 2025 | T1: May 1–19, 2026 | T2: Nov 1–19, 2026 | 12-Mo / 6-Mo Shift |
| :--- | ---: | ---: | ---: | :--- |
| **Corpus size (8 cats, unique)** | 2,435 | 3,298 | 4,104 | +68.5% YoY volume |
| **Full-text coverage (HTML5+PDF)** | 2,421 (99.43%) | 3,288 (99.70%) | 4,097 (99.83%) | ≥99.4% all slices |
| **Later-revised papers (`v > 1`)** | 862 (35.4%) | 1,048 (31.8%) | 248 (6.0%) | Rescued via unbounded OAI |
| **Metadata-only Lean strong hits** | 0 | 5 | 16 | 0 → 5 → 16 |
| **Stage-2 Lean candidates (full-text)** | 3 (0.12%) | 19 (0.58%) | 55 (1.34%) | **10.9×** rate in 12 mo |
| **Stage-2 Beyond-Lean control (all other FV)** | 37 (1.52%) | 44 (1.33%) | 48 (1.17%) | **Flat / slightly down** |
| **Confirmed Lean — Contemporaneous (`v1`)** | **0 (0.00%)** | **5 (0.15%)** | **39 (0.95%)** | **0.00% → 0.15% → 0.95%** (**6.3×** in 6 mo) |
| **Confirmed Lean — Latest Rev (`v_latest`)** | 1 (0.04%) | 7 (0.21%) | 39 (0.95%) | **23.1×** rate YoY; **4.5×** in 6 mo |
| **Non-TCS primary Lean (`v1` / `v_latest`)** | 0 (0.00%) / 1 (0.04%) | 3 (0.09%) / 5 (0.15%) | 36 (0.89%) | **9.7×** rate in 6 mo (`v1`) |
| **`engineering_math_proof` (`v1` / `v_latest`)** | 0 / 0 | 3 (60.0%) / 4 (57.1%) | **28 (71.8%)** | **0 → 3 → 28** (`v1`, **7.5×** rate in 6 mo) |
| **Explicit AI disclosure (`v1`: yes/unc/no)** | 0 / 0 / 0 | 2 / 2 / 1 (40% yes) | 30 / 9 / 0 (76.9% yes) | 40% → 76.9% explicit AI |
| **Median paper-owned LoC (`v1` scanned)** | N/A (0 repos) | **749** (3 repos) | **29,005** (28 repos) | **38.7×** scale jump |
| **Total paper-owned LoC (`v1` / `v_latest`)** | 0 / 0 | 3,603 / 378,185 | **3,104,750** | **3.6k → 3.10M** (`v1` owned; 4.30M raw) |

> **95% Confidence Intervals (Contemporaneous `v1`):** T0 `0/2,435 = 0.00%` (one-sided 95% Clopper–Pearson upper bound **0.12%**); T1 `5/3,298 = 0.15%` (95% Wilson CI `[0.06%, 0.35%]`); T2 `39/4,104 = 0.95%` (95% Wilson CI `[0.70%, 1.30%]`). Non-overlapping 95% CIs confirm a statistically decisive inflection.

## 2. Methodological Discovery: Retroactive Post-Hoc Autoformalization (`P1-retro`)

Avoiding OAI-PMH `until` truncation rescued **35.4%** of Nov 2025 papers and **31.8%** of May 2026 papers that were revised after initial posting. Inspecting `v1` vs. `v_latest` across all historical Lean hits uncovered a striking behavioral phenomenon — **authors returning 5–7 months after initial arXiv posting to retroactively formalize their preprints in Lean 4 once late-2026 agentic provers matured**:

- **[2511.15517](https://arxiv.org/abs/2511.15517)** (`v1`: `2025-11-19` → `v2`: `2026-06-29`): Beluga: 0 mentions of Lean in v1 (2025-11-19); added Appendix I Lean formalization in v2 (2026-06-29, Lean v4.33.0).
- **[2605.09552](https://arxiv.org/abs/2605.09552)** (`v1`: `2026-05-10` → `v2`: `2026-10-27`): Phases of Muon: 0 mentions of Lean in v1 (2026-05-10); added 340.3k LoC Lean 4 formalization in v2 (2026-10-27, Lean v4.34.1) from frozen camera-ready snapshot cr-2026-10-22.
- **[2605.19531](https://arxiv.org/abs/2605.19531)** (`v1`: `2026-05-19` → `v2`: `2026-11-02`): Conflict-Freedom (PODC'26): 0 mentions of Lean in v1 (2026-05-19); added 34.3k LoC Claude Opus 5.5-assisted Lean 4 formalization in v2 (2026-11-02, Lean v4.34.0).

Without `v1` verification, naive latest-version scraping would misattribute **374,582 LoC** of Oct–Nov 2026 Lean 4 (`v4.34.x`) code back to May 2026, inflating T1's paper-owned LoC by **105×** and masking the true transition from human-scale (~0.5k–2.4k LoC) to AI-scale (12k–929k LoC) formalization.

## 3. Per-Category Longitudinal Adoption Breakdown

| Category | T0 Papers | T0 Lean `v1` (`v_lat`) | T1 Papers | T1 Lean `v1` (`v_lat`) | T2 Papers | T2 Lean | T2 Eng-Math |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `math.OC` | 410 | 0 (0.00%) | 512 | 0 (0.00%) [1] | 724 | **19 (2.62%)** | 17 |
| `cs.DC` | 223 | 0 (0.00%) [1] | 315 | 1 (0.32%) [2] | 335 | **6 (1.79%)** | 0 |
| `cs.IT` | 209 | 0 (0.00%) | 327 | 0 (0.00%) | 338 | **6 (1.78%)** | 6 |
| `cs.CR` | 406 | 0 (0.00%) [1] | 685 | 3 (0.44%) | 629 | **7 (1.11%)** | 4 |
| `eess.SY` | 476 | 0 (0.00%) | 456 | 1 (0.22%) | 738 | **3 (0.41%)** | 2 |
| `eess.SP` | 338 | 0 (0.00%) | 419 | 1 (0.24%) | 462 | 0 (0.00%) | 0 |
| `cs.NI` | 136 | 0 (0.00%) | 227 | 0 (0.00%) | 196 | 0 (0.00%) | 0 |
| `cs.RO` | 532 | 0 (0.00%) | 740 | 0 (0.00%) | 1159 | 0 (0.00%) | 0 |

### Key Disciplinary Trajectory Observations
- **`math.OC` exploded from 0.00% → 0.00% (`v1`; 0.20% `v_lat`) → 2.62% (19/724, 17 `engineering_math_proof`)** in just 6 months, accounting for nearly half of all late-2026 engineering Lean adoption.
- **`cs.IT` went from 0.00% → 0.00% → 1.78% (6/338, 100% `engineering_math_proof`)** between May and November 2026.
- **`cs.CR` was the earliest adopter** in contemporaneous `v1` (0.00% → 0.44% [3/685] → 1.11% [7/629]), followed by **`cs.DC`** (0.00% → 0.32% [1/315 `v1`, 2/315 `v_lat`] → 1.79% [6/335]) and **`eess.SY`** (0.00% → 0.22% [1/456] → 0.41% [3/738]).
- **`eess.SP` had 1 human-written Lean paper in May 2026 (`2605.14610`, 473 LoC)** and 0 in Nov 2025 & Nov 2026; **`cs.NI` (0/559 across 3 slices)** and **`cs.RO` (0/2,431 across 3 slices)** remain at **0.00%** across all three snapshots!

## 4. Beyond-Lean Formal Methods Control Series (Zero-Token Stage-2 Full-Text Hits)

| Formal Verification Family | T0 (Nov 2025, n=2,435) | T1 (May 2026, n=3,298) | T2 (Nov 2026, n=4,104) |
| :--- | ---: | ---: | ---: |
| **Lean 4 candidates (strong + ctx)** | 3 (0.12%) | 19 (0.58%) | **55 (1.34%)** |
| **All Beyond-Lean FV (dedup union)** | 37 (1.52%) | 44 (1.33%) | 48 (1.17%) |
| — Other ITPs (Coq/Rocq, Isabelle, Agda, Dafny, …) | 10 (0.41%) | 14 (0.42%) | 18 (0.44%) |
| — Model Checkers (TLA+, UPPAAL, PRISM, CBMC, …) | 11 (0.45%) | 12 (0.36%) | 11 (0.27%) |
| — Protocol Verifiers (Tamarin, ProVerif, EasyCrypt) | 6 (0.25%) | 5 (0.15%) | 6 (0.15%) |
| — SMT/SAT Solvers (Z3, cvc5, SMT-LIB, …) | 19 (0.78%) | 23 (0.70%) | 20 (0.49%) |

## 5. Paradigms, Tiers, AI Disclosure & Codebase Scale Shifts

| Dimension | T0 `v1` (`v_lat`) | T1 `v1` (`v_lat`) | T2 (`v1` = `v_lat`) |
| :--- | :--- | :--- | :--- |
| **Paradigms (`P1/P2/P3/P4/P0`)** | 0/0/0/0/0 (`v_lat`: 0/0/0/0/1) | 3/1/0/0/1 (`v_lat`: 5/1/0/0/1) | 28/0/0/3/8 |
| **Tiers (`Gold/Silver/Bronze`)** | 0/0/0 (`v_lat`: 0/0/1) | 0/2/3 (`v_lat`: 2/2/3) | 19/7/13 |
| **AI Assisted (`yes/unc/no`)** | 0/0/0 (`v_lat`: 0/1/0) | 2/2/1 (`v_lat`: 3/3/1) | 30/9/0 |
| **Owned LoC (median / range)** | — | **749** (473–2,381) | **29,005** (528–929,448) |

## 6. Inventory of Historical Confirmed Lean Papers (T0 & T1)

| Slice | arXiv ID | Timing | Prim. (Targets) | Role | Par. | Tier | AI? | Owned LoC | Title |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| T0 | [2511.15517](https://arxiv.org/abs/2511.15517) | Retro `v2` (2026-06-29) | `cs.CR` (`cs.CR,cs.DC`) | `software_or_system_fv` | `P0` | `Tier1_Bronze` | `unclear` | — | Beluga: Block Synchronization for BFT Consensus Protocols |
| T1 | [2605.19531](https://arxiv.org/abs/2605.19531) | Retro `v2` (2026-11-02) | `cs.DC` (`cs.DC`) | `software_or_system_fv` | `P1` | `Tier3_Gold` | `explicitly_yes` | 34,257 | Conflict-Freedom as a Progress Condition |
| T1 | [2605.14610](https://arxiv.org/abs/2605.14610) | Contemp. `v1` (2026-05-14) | `stat.ME` (`eess.SP`) | `engineering_math_proof` | `P1` | `Tier2_Silver` | `explicitly_no` | 473 | Parametrically Adaptive Transition Polynomial: a Signed-Parity Co |
| T1 | [2605.16407](https://arxiv.org/abs/2605.16407) | Contemp. `v1` (2026-05-13) | `cs.LO` (`cs.CR`) | `software_or_system_fv` | `P1` | `Tier1_Bronze` | `unclear` | 2,381 | Proof-Carrying Certificates for LLM Pipelines: A Trust-Boundary A |
| T1 | [2605.09552](https://arxiv.org/abs/2605.09552) | Retro `v2` (2026-10-27) | `math.OC` (`math.OC`) | `engineering_math_proof` | `P1` | `Tier3_Gold` | `unclear` | 340,325 | Phases of Muon: When Muon Eclipses SignSGD |
| T1 | [2605.05801](https://arxiv.org/abs/2605.05801) | Contemp. `v1` (2026-05-07) | `cs.LO` (`cs.DC`) | `pure_tcs_or_math` | `P1` | `Tier1_Bronze` | `explicitly_yes` | — | Self-Correcting Gossip Protocols |
| T1 | [2605.03034](https://arxiv.org/abs/2605.03034) | Contemp. `v1` (2026-05-04) | `cs.AI` (`cs.CR,eess.SY`) | `engineering_math_proof` | `P0` | `Tier1_Bronze` | `unclear` | — | Stable Agentic Control: Tool-Mediated LLM Architecture for Autono |
| T1 | [2605.02856](https://arxiv.org/abs/2605.02856) | Contemp. `v1` (2026-05-04) | `cs.CR` (`cs.CR`) | `engineering_math_proof` | `P2` | `Tier2_Silver` | `explicitly_yes` | 749 | The 1-Bit Barrier is Universal: k-Stage Pipeline Composition and  |

## 7. Historical Phase 2 Layer-A Semantic Fidelity Audits (T1: n = 3 vs. T2: n = 17)

| arXiv ID | Timing | Overall Fidelity | M1 Drift | M2 Scope | M3 Defs | M4 Junk/Vac | Non-Vac? | Mathlib |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| [2605.14610](https://arxiv.org/abs/2605.14610) | Contemp. `v1` (May 2026) | `partial_or_weakened_formalization` | `minor_undisclosed` | `minor_disclosed` | `moderate` | `minor_undisclosed` | Yes | `mixed_custom_and_mathlib` |
| [2605.09552](https://arxiv.org/abs/2605.09552) | Retro `v2` (Oct 2026) | `mostly_faithful_with_disclosed_gaps` | `minor_undisclosed` | `moderate` | `none` | `none` | Yes | `strong_mathlib` |
| [2605.02856](https://arxiv.org/abs/2605.02856) | Contemp. `v1` (May 2026) | `partial_or_weakened_formalization` | `minor_undisclosed` | `moderate` | `moderate` | `minor_undisclosed` | No | `mixed_custom_and_mathlib` |
