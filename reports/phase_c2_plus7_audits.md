# Phase C2 Report: Targeted Stage-5 Layer-A Audits & Compact Docker Kernel Builds (`+7` Categories)

> **Phase C2 Complete (2026-11-25)** · Exhaustive Stage-5 Layer-A semantic fidelity audits (`pro` tier, `n = 4`) + isolated `--network=none` Docker `lake build` & `Lean.collectAxioms` verification (`n = 3` compact `<15k` LoC repos) on 100% of newly discovered `eng_algorithmic_proof` public repositories from the `+7` engineering categories · Frozen orig-8 v0.7 artifacts untouched · Machine-readable summary: [`artifacts/phase_c2_plus7_audits.json`](../artifacts/phase_c2_plus7_audits.json) · Detailed per-paper audit tables: [`reports/slices/2026-11/phase2_layer_a_audit_plus7.md`](slices/2026-11/phase2_layer_a_audit_plus7.md)

## 1. Executive Summary

Following Phase C1's 15-category longitudinal backfill, 4-way role stratification narrowed the newly discovered `+7` `eng_algorithmic_proof` public-repo queue to **4 repositories** (`2611.14586`, `2611.11805`, `2611.09615`, `2611.07395`; `2611.04545` has a 404/private repo). Completing Stage-5 Layer-A audits across all 4 repos and isolated `--network=none` Docker kernel verification across all 3 compact (`<15k` LoC) repos keeps both semantic auditing and dynamic kernel verification **100% exhaustive over the entire 15-category engineering cohort**:

1. **Zero Material Undisclosed Drift Across All 22 `eng_algorithmic_proof` Repos (15-Category Union):** Across the 4 new `+7` repos, **`2/4` (`2611.11805`, `2611.09615`)** score `high_faithful`, **`1/4` (`2611.07395`)** scores `mostly_faithful_with_disclosed_gaps`, **`1/4` (`2611.14586`)** scores `partial_or_weakened_formalization`, and **`0/4`** score `material_undisclosed_drift_or_risk`. Combining with orig-8 (`18` `eng_algorithmic_proof` repos across T1+T2) yields **`0 / 22`** (`0.0%`) `material_undisclosed_drift_or_risk` across all 15-category engineering-algorithmic repos (`0/19` in T2, with `7/19` `high_faithful` and `8/19` `mostly_faithful_with_disclosed_gaps`; the sole `material_undisclosed_drift_or_risk` repo among all **27** audited repos remains meta-system `2611.26272` *Paper2Lean*). All **35/35** (`100%`) new `file:line` provenance refs (**274/274** combined) resolve in-bounds.
2. **3 / 3 (100%) Out-of-the-Box `--network=none` Docker Pass Rate on Compact `+7` Repos:** All 3 newly discovered compact (`<15k` LoC) `eng_algorithmic_proof` repositories build out of the box with zero compile errors and zero `Lean.ofReduceBool` / `sorryAx` (`361` theorems programmatically audited via `Lean.collectAxioms`, median `312.8s`). Combined across all 15 categories (`T1 + T2`), compact OOTB pass rate rises from `11/14 (78.6%)` to **`14/17 (82.4%)`** (**3,551** OOTB theorems / **3,615** incl. synthetic; **`8/9`** compact `Tier3_Gold` OOTB pass and **`8/8` (100%)** axiom-clean; **`0/17`** `Lean.ofReduceBool`).
3. **Exact Static-to-Dynamic Axiom Corroboration (Including Hybrid Julia/Arb Computer-Assisted Proofs):** `2611.14586` (`SparTheorems`, `85` theorems) and `2611.09615` (`TraceSqrt`, `69` theorems, `Tier3_Gold`) use strictly Lean's 3 standard axioms (`propext`, `Classical.choice`, `Quot.sound`), whereas `2611.07395` (`WaveCAP`, `Tier1_Bronze`) dynamically corroborates its static `Mode6_SorryOrAxiomOrNativeDecide` flag — surfacing exact custom Arb numerical axioms in both the legacy `Main.lean` certificate (`WaveCAP.Certificate.*`) and the publication certificate (`WaveCAP.PaperCertificate.cert_arb_dmin_bound`, `cert_arb_sup_bound_le_eps0`), with **zero `sorryAx`** across the entire codebase.
4. **Two Contrasting Real-World Failure Modes Surfaced by Layer-A Deep Inspection:** Even without `sorry` or custom axioms, `2611.14586` (`Tier2_Silver`, 1.97k LoC) illustrates subtle **algebraic-core substitution** (`Mode1=moderate`, `Mode2=moderate`: abstract Zinkevich template without D-dim squared-loss instantiation, 2-point vs. K-point Hedge convexity, and missing contraction bound on $\beta$ in `debiased_dial_contraction`), whereas `2611.07395` (`Tier1_Bronze`, 12.3k LoC) illustrates **disconnected analytic library vs. axiomatized publication certificate** (`Mode2=moderate`: ~12k LoC of clean Hilbert/aliasing/Taylor proofs sit uninstantiated behind two monolithic Julia/Arb axioms, and default `lake build` compiles the older $N=110$ `Main.lean` rather than `PaperTheorems.lean`). Conversely, `2611.11805` (`P4` spec-lock with 331 Comparator checks + LeanCert) and `2611.09615` (`P1` full 22-statement formalization) achieve exemplary `high_faithful` fidelity.

---

## 2. Per-Repository Phase C2 Audit & Kernel Verification Matrix (`n = 4`)

| arXiv ID | Cat (`+7`) | Primary Repo (Pin) | Owned LoC | Toolchain | Par / Tier | Layer-A Fidelity | M1 / M2 / M3 / M4 | Non-Vac? | Docker OOTB (`--network=none`) | Theorems (`collectAxioms`) | Non-Std Axioms |
| :--- | :--- | :--- | ---: | :--- | :--- | :--- | :--- | :---: | :--- | ---: | :--- |
| [2611.07395](https://arxiv.org/abs/2611.07395) | `math.AP` (`physics.flu-dyn`) | `michalshavitNYU/Rigorously-certified-water-waves` (`e775377`) | 12,309 | `v4.29.0-rc6` | `P1` / `T1` | `mostly_faithful_with_disclosed_gaps` | `minor_disclosed` / `moderate` / `minor_disclosed` / `minor_disclosed` | No | **PASS** (312.8s) | 207 | `4` custom (`cert_arb_dmin_bound`, `cert_arb_sup_bound_le_eps0`, `PaperCertificate.cert_arb_dmin_bound`, `PaperCertificate.cert_arb_sup_bound_le_eps0`) |
| [2611.09615](https://arxiv.org/abs/2611.09615) | `cs.GT` (`cs.GT`) | `renatoppl/trace-square-root` (`8b3d893`) | 14,953 | `v4.27.0` | `P1` / `T3` | `high_faithful` | `minor_disclosed` / `minor_disclosed` / `none` / `none` | No | **PASS** (779.0s) | 69 | **none** |
| [2611.11805](https://arxiv.org/abs/2611.11805) | `math.NA` (`math.DS`) | `sgstepaniants/inelastic_hom_learn` (`8c65f32`) | 42,036 | `v4.35.0` | `P4` / `T3` | `high_faithful` | `minor_disclosed` / `minor_disclosed` / `none` / `none` | Yes | *N/A (>15k LoC)* | — | — |
| [2611.14586](https://arxiv.org/abs/2611.14586) | `stat.ML` (`cs.GT`) | `zenodo/23768172` (`zenodo:23768172`) | 1,969 | `v4.35.0-rc4` | `P1` / `T2` | `partial_or_weakened_formalization` | `moderate` / `moderate` / `minor_undisclosed` / `minor_undisclosed` | No | **PASS** (77.8s) | 85 | **none** |

---

## 3. Combined 15-Category Cohort Totals (Orig-8 + `+7`)

### 3.1 Stage-5 Layer-A Semantic Fidelity Audits

| Cohort | Audited Repos | `high_faithful` | `mostly_faithful` | `partial_or_weakened` | `material_undisclosed` | Non-Vacuity Witnesses | `file:line` Provenance |
| :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| **`+7` Net-New T2 (`eng_algorithmic_proof`)** | 4 | 2 | 1 | 1 | **0** | 1/4 (25.0%) | **35/35** (100%) |
| **15-Cat T2 (`eng_algorithmic_proof`)** | 19 | 7 | 8 | 4 | **0** | 11/19 (57.9%) | — |
| **15-Cat T1+T2 (`eng_algorithmic_proof`)** | 22 | 7 | 9 | 6 | **0** | 13/22 (59.1%) | — |
| **15-Cat T1+T2 (All Audited Roles)** | 27 | 9 | 11 | 6 | **1** (`2611.26272`) | 16/27 (59.3%) | **274/274** (100%) |

### 3.2 Isolated `--network=none` Docker Compact (`<15k` LoC) Kernel Builds

| Cohort | Attempted | OOTB Pass | Axiom-Clean OOTB | Non-Std Axioms OOTB | `Tier3_Gold` OOTB / Clean | OOTB Theorems (Incl. Synth) | `ofReduceBool` |
| :--- | ---: | :---: | :---: | :---: | :---: | ---: | :---: |
| **`+7` Net-New T2 Compact (`eng_alg`)** | 3 | **3/3** (100.0%) | 2/3 | 1 (`2611.07395`) | 1/1 / 1/1 | **361** (361) | **0/3** |
| **15-Cat T1+T2 Compact (`eng_alg` Only)** | 11 | **8/11** (72.7%) | 7/8 | 1 | 5/6 / 5/5 | **1,800** (1,864) | **0/11** |
| **15-Cat T1+T2 Compact (All Roles)** | 17 | **14/17** (82.4%) | 11/14 | 3 | **8/9** / **8/8** (100%) | **3,551** (3,615) | **0/17** |

---

## 4. Detailed Findings & Cross-Check Notes

### [2611.07395](https://arxiv.org/abs/2611.07395) — `https://github.com/michalshavitNYU/Rigorously-certified-water-waves`
- **Provenance:** arXiv `v1` (2026-11-05) · Pin: `e7753774cdebd3858dbc2349e21bda9e0bed003b` · Toolchain: `leanprover/lean4:v4.29.0-rc6` · Lean files: `33` · Owned LoC: `12,309` · `lean_tree_sha256`: `6e5ef3cc222e0336...`
- **Layer-A Audit:** `mostly_faithful_with_disclosed_gaps` · M1=`minor_disclosed`, M2=`moderate`, M3=`minor_disclosed`, M4=`minor_disclosed` · Non-vacuity witnesses: `False` · Mathlib anchoring: `strong_mathlib` · Provenance refs: `10/10` in-bounds.
- **Isolated Docker Kernel Build:** `pass` (`exit_code=0`, `wall_time=312.8s`, `axiom_check=347.8s`, `target_modules=32`, `total_theorems_checked=207`, `sorry_ax=False`, `of_reduce_bool=False`, `nonstandard_axioms=['WaveCAP.cert_arb_dmin_bound', 'WaveCAP.cert_arb_sup_bound_le_eps0', 'WaveCAP.PaperCertificate.cert_arb_dmin_bound', 'WaveCAP.PaperCertificate.cert_arb_sup_bound_le_eps0']`).

### [2611.09615](https://arxiv.org/abs/2611.09615) — `https://github.com/renatoppl/trace-square-root`
- **Provenance:** arXiv `v1` (2026-11-06) · Pin: `8b3d893ab6931d6f792d4deae2702fb567f545d6` · Toolchain: `leanprover/lean4:v4.27.0` · Lean files: `21` · Owned LoC: `14,953` · `lean_tree_sha256`: `42c53aedb9d840fd...`
- **Layer-A Audit:** `high_faithful` · M1=`minor_disclosed`, M2=`minor_disclosed`, M3=`none`, M4=`none` · Non-vacuity witnesses: `False` · Mathlib anchoring: `strong_mathlib` · Provenance refs: `5/5` in-bounds.
- **Isolated Docker Kernel Build:** `pass` (`exit_code=0`, `wall_time=779.02s`, `axiom_check=116.82s`, `target_modules=20`, `total_theorems_checked=69`, `sorry_ax=False`, `of_reduce_bool=False`, `nonstandard_axioms=[]`).

### [2611.11805](https://arxiv.org/abs/2611.11805) — `https://github.com/sgstepaniants/inelastic_hom_learn`
- **Provenance:** arXiv `v1` (2026-11-09) · Pin: `8c65f3273b7c15ec46187ca9337fe4ada5fd2302` · Toolchain: `leanprover/lean4:v4.35.0` · Lean files: `753` · Owned LoC: `42,036` · `lean_tree_sha256`: `5879dc65765bc8e3...`
- **Layer-A Audit:** `high_faithful` · M1=`minor_disclosed`, M2=`minor_disclosed`, M3=`none`, M4=`none` · Non-vacuity witnesses: `True` · Mathlib anchoring: `strong_mathlib` · Provenance refs: `10/10` in-bounds.
- **Isolated Docker Kernel Build:** Excluded from compact (`<15k` LoC) cohort (`42,036` owned LoC / `55,284` raw LoC across 753 files; candidate for future medium/large-repo sandbox + `comparator` replay).

### [2611.14586](https://arxiv.org/abs/2611.14586) — `https://zenodo.org/records/23768172`
- **Provenance:** arXiv `v1` (2026-11-10) · Pin: `zenodo/23768172` · Toolchain: `leanprover/lean4:v4.35.0-rc4` · Lean files: `7` · Owned LoC: `1,969` · `lean_tree_sha256`: `00628704227d85a2...`
- **Layer-A Audit:** `partial_or_weakened_formalization` · M1=`moderate`, M2=`moderate`, M3=`minor_undisclosed`, M4=`minor_undisclosed` · Non-vacuity witnesses: `False` · Mathlib anchoring: `mixed_custom_and_mathlib` · Provenance refs: `10/10` in-bounds.
- **Isolated Docker Kernel Build:** `pass` (`exit_code=0`, `wall_time=77.84s`, `axiom_check=12.97s`, `target_modules=7`, `total_theorems_checked=85`, `sorry_ax=False`, `of_reduce_bool=False`, `nonstandard_axioms=[]`).
