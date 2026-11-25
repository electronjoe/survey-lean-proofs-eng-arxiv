# Pilot E0 Report: Lean 4 Eligibility & Structural Extraction Calibration

- **Generated:** `2026-11-25T23:49:14+00:00`
- **Model tier (E2):** `flash` (strictly blinded to `is_confirmed_lean` and `role_4way`)
- **Pilot size:** `127` unique papers (`45` stratified random T2 [`3`/category × 15] + `82` confirmed Lean positive controls; overlap = `0`)
- **Fetch coverage:** `html=117`, `pdf=10`, `failed=0`

## 1. Positive-Control Sensitivity (82 Confirmed Lean Papers, Blinded)

| Confirmed Role (`role_4way`) | N | `E1_formal` | `L1` (Lean-Amenable) | `L2` (Mathlib-Blocked) | `L3` (Op-FV) | `L4` (Heuristic/Num) | `L5` (Empirical) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `eng_algorithmic_proof` | 31 | 30 | 27 | 4 | 0 | 0 | 0 |
| `pure_math_or_tcs` | 40 | 40 | 30 | 10 | 0 | 0 | 0 |
| `operational_system_fv` | 8 | 5 | 0 | 0 | 8 | 0 | 0 |
| `meta_formalization_system` | 3 | 0 | 1 | 0 | 0 | 0 | 2 |

- **Math/Algorithmic positive controls (`eng_algorithmic_proof` + `pure_math_or_tcs`, `n=71`):** `100.0%` classified as Theorem-Bearing (`L1 ∪ L2`), `80.3%` as `L1` Lean-Amenable.
- **Operational FV positive controls (`n=8`):** `8/8` classified as `L3` or `L1`.
- **Unexpected mismatches:** `0`

## 2. Stage E1 Deterministic Bucket vs. Stage E2 LLM Class (All Pilot Papers)

| E1 Bucket | `L1` | `L2` | `L3` | `L4` | `L5` | Total |
|---|---:|---:|---:|---:|---:|---:|
| `E1_formal_thm_proof` | 70 | 16 | 5 | 0 | 1 | 92 |
| `E1_weak_or_unnumbered_math` | 2 | 0 | 3 | 3 | 13 | 21 |
| `E1_no_formal_claims` | 0 | 0 | 0 | 1 | 13 | 14 |

## 3. Random Stratified T2 Pilot (`n = 45`, `3`/Category)

| Category | n | `E1_formal` | `L1` | `L2` | `L3` | `L4` | `L5` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `math.OC` | 3 | 3 | 2 | 1 | 0 | 0 | 0 |
| `cs.DC` | 3 | 1 | 1 | 0 | 0 | 0 | 2 |
| `cs.IT` | 3 | 2 | 2 | 0 | 0 | 0 | 1 |
| `cs.CR` | 3 | 2 | 2 | 0 | 0 | 0 | 1 |
| `eess.SY` | 3 | 1 | 1 | 0 | 0 | 1 | 1 |
| `eess.SP` | 3 | 1 | 1 | 0 | 0 | 0 | 2 |
| `cs.NI` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `cs.RO` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `cs.GT` | 3 | 3 | 3 | 0 | 0 | 0 | 0 |
| `math.DS` | 3 | 3 | 2 | 0 | 0 | 0 | 1 |
| `physics.flu-dyn` | 3 | 1 | 0 | 1 | 0 | 2 | 0 |
| `cs.PF` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `eess.IV` | 3 | 0 | 0 | 0 | 0 | 1 | 2 |
| `eess.AS` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `cs.CE` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
