# Phase D2 Scope Decision & Spin-Off Brief: Operational Software, Hardware, and Database Lean 4 FV

**Decision Date:** 2026-11-25  
**Status:** **ACCEPTED (Phase D2 Complete)** — Keep Operational SW/HW/DB Lean 4 FV (`cs.AR`, `cs.DB`, `cs.OS`, `cs.SE`, `cs.PL`) as a **separate follow-on study** rather than folding it into `papers/arxiv-empirical/main.tex` (v0.7).  
**Related Docs:** [`docs/scope_refinement_and_future_actions.md`](scope_refinement_and_future_actions.md) · [`reports/track3_operational_fv_pilot.md`](../reports/track3_operational_fv_pilot.md) · [`artifacts/track3_operational_fv_pilot.json`](../artifacts/track3_operational_fv_pilot.json) · [`docs/track1_4way_coding_rubric.md`](track1_4way_coding_rubric.md)

---

## 1. Decision Statement

We **explicitly do not ingest or fold** arXiv's operational systems/software/hardware/database formal-verification categories (`cs.AR`, `cs.DB`, `cs.OS`, `cs.SE`, `cs.PL`) into our v0.7 empirical engineering-proof manuscript ([`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex)). Instead:

1. **In v0.7 (15-Category Engineering Panel):** Incidental operational-FV papers that enter our 15 whole engineering categories via cross-listing (`n = 4` in T2 `v1`, `5.9%` of 68 confirmed papers; `n = 8` total `v_latest` across T0–T2 including Phase C1 `cs.PL`/`cs.PF` retroactive addition `2605.01140` *SoCal*) are retained transparently in whole-category census totals, cleanly separated under our 4-way role taxonomy (`operational_system_fv`), and used to establish an **empirically grounded external-validity boundary** (Section 2.1 `\ref{sec:opfv_boundary}` and Section 9).
2. **Separate Follow-On Study (Spin-Off):** Full empirical measurement and failure-mode auditing of Lean 4 in hardware/RTL (`cs.AR`), databases (`cs.DB`), operating systems (`cs.OS`), software engineering (`cs.SE`), and programming languages (`cs.PL`) is chartered as a standalone follow-on study (*working title: "Lean 4 as an Operational Formal-Methods Engine in Systems, Databases, and Hardware"*).

---

## 2. Empirical Justification (Why Folding Operational FV Into v0.7 Would Dilute & Mislead)

Our Phase B1 code-level diagnostic ([`reports/track3_operational_fv_pilot.md`](../reports/track3_operational_fv_pilot.md), [`artifacts/track3_operational_fv_pilot.json`](../artifacts/track3_operational_fv_pilot.json)) and Phase C1 15-category census ([`reports/phase_c1_15cat_longitudinal.md`](../reports/phase_c1_15cat_longitudinal.md)) established four concrete reasons why pooling operational FV with engineering algorithmic proofs is methodologically unsound:

1. **Systematic Layer-A math-proof rubric misfires (`2/4` cloned zero-dep repos):** Zero-dependency operational mechanizations (`2611.10810` DBLog CDC, 507 axiom-clean theorems in 11.2s; `2605.19531` PODC conflict-freedom, 2,061 theorems) intentionally omit Mathlib because no Mathlib abstraction exists for CDC logs or concurrent shared-memory executions. Applying our math-proof `Mode3_CustomDefs` heuristic generated false-positive "definition smuggling" flags on `2/4` cloned repos, while `2605.19531` tripped the `>20k`-LoC `Mode10_ProofBloat` threshold despite clean modular architecture.
2. **Orthogonal authoring paradigms (`0/7` use math-proof paradigms `P2`–`P4`):** None of the 7 audited operational-FV papers used Lean-first auto-informalization (`P2`), mathematical blueprints (`P3`: `LeanArchitect`/`Verso`), or `Challenge.lean`/`lake comparator` locks (`P4`). Instead, operational FV partitions into **(a) abstract design models** (`5/7`), **(b) executable Lean 4 policy EDSLs** (`1/7`, `2611.25599`), and **(c) certificate-schema oracle wrappers** (`1/7`, `2605.16407`)—with future `cs.AR`/`cs.SE`/`cs.PL` cohorts adding **verified extraction**, **translation validation / verified lifting**, and **stepwise refinement**.
3. **Dominant failure modes sit outside Table 1 (`7/7` refinement & environment gaps):** While Layer B/C modes (`sorry`/custom axioms, opacity) transfer sharply—even exposing a provably inconsistent custom axiom `innerProd_sub` (`0 = 1`) in `2605.16407`—the defining operational assurance risks are absent from our math-proof taxonomy:
   - **OpFV-1 (Model-to-Implementation Refinement Gap — `7/7`):** Abstract models verified without refinement or conformance to deployed code/RTL/SQL (e.g., Debezium/Flink or `stripe_gate.py`).
   - **OpFV-2 (Unproved Environment / Fault / Oracle Assumptions — `7/7`):** Deployment invariants and fault models (atomic snapshots, single-restart visibility, ML/crypto oracles) left unmechanized.
   - **OpFV-3 (Safety-Without-Liveness / Trace Vacuity — `4/7` lack mechanized Lean liveness):** Invariant preservation proved without progress or non-trivial execution reachability.
   - **OpFV-4 (Extraction / Runtime-Monitor / Cross-Kernel TCB Gaps — `4/7`):** Unverified Lean-to-C/Rust/Verilog lowering, runtime shims, or partial Isabelle-to-Lean port omissions.
   - **OpFV-5 (Evolution & Maintenance Debt — `3/7`):** Monolithic proofs breaking across routine system/RTL revisions.
4. **Clean statistical separation without delaying v0.7:** Inside our 15-category engineering panel, `operational_system_fv` accounts for only `4/68 (5.9%)` of T2 `v1` papers (`0.08%` corpus rate). Adding five high-volume systems/SE/PL categories (`cs.AR`, `cs.DB`, `cs.OS`, `cs.SE`, `cs.PL`) would require a redesigned Stage-5 operational-FV audit rubric, distinct benchmark controls (Coq/Rocq CompCert/Iris, Isabelle/seL4, Dafny, TLA+, Verus, Kani, JasperGold/SMT), and hundreds of additional Stage-4 classifications—delaying v0.7 submission while diluting its crisp focus on engineering mathematical & algorithmic proofs.

---

## 3. Chartered Scope for the Follow-On Operational-FV Study

When initiated as a separate project/manuscript, the follow-on study can reuse our zero-token pipeline (`src/ingest_arxiv.py`, `src/fetch_and_screen.py`, `src/profile_artifacts.py`, `sandbox/`) and already-upgraded `workflows/classify_candidates.py` (`role_4way`, `OpFV_RefinementGap`, `OpFV_SafetyOnlyNoLiveness`) with:
- **Target Categories:** `cs.AR`, `cs.DB`, `cs.OS`, `cs.SE`, `cs.PL` (plus the 8 operational-FV cross-lists already identified in T0–T2 of our 15-category study as seed cases).
- **Operational-FV Rubric:** Dedicated Stage-5 audit rubric scored on **OpFV-1 through OpFV-5** + Layer B/C (`sorry`/custom axioms, `bv_decide` vs. `native_decide` TCB trade-offs, metaprogramming, build reproducibility) rather than Mathlib-anchoring `Mode3_CustomDefs`.
- **Comparative Control:** Direct comparison of Lean 4 against established operational FV ecosystems (Rocq/Coq, Isabelle/HOL, Dafny, Verus, TLA+, SMT/model checkers) across matched longitudinal windows.
