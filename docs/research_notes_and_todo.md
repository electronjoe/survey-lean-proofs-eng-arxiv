# Research Scope Notes & Future Adjustments (Bhaskar Krishnamachari & Scott Moeller)

## Pilot v1 Scope (Currently Running — Unchanged)
- **Window:** 3 weeks (`2026-11-01` – `2026-11-22`, 3,160 unique papers)
- **arXiv Categories:** `cs.DC`, `cs.NI`, `cs.IT`, `eess.SY`, `cs.CR`, `cs.RO`
- **Tools tracked:** Lean (primary) + Beyond-Lean formal tools (baseline)
- **Note on CS Theory in Pilot v1:** Pure CS theory categories (`cs.CC`, `cs.DS`, `cs.LO`, `cs.DM`, `cs.FL`) were already excluded, though `cs.DC` still catches some theoretical distributed-algorithms papers (e.g., CONGEST / low-bandwidth matrix multiplication) and `cs.CR` catches software/protocol verification papers.

---

## Feedback from Bhaskar Krishnamachari (2026-11-22)

Key points from discussion:
1. **Exclude CS theory:** Pure CS theory is essentially mathematics; the target phenomenon is **engineering & applied theory**, not pure math / theoretical CS.
2. **Focus strictly on Lean (for the main study):** Keep beyond-Lean tagging only as an exploratory note for the initial pilot, then drop it in future runs.
   - *Rationale:* Traditional formal verification in **hardware/chip design** and **software verification** (e.g., TLA+, Coq/CompCert, Dafny, model checkers, protocol verifiers) are separate, mature, decades-old subfields—conflating them dilutes the signal.
3. **Core Research Question:** Where is **Lean** being used to **verify or supplement mathematical proofs in engineering theory papers**—specifically in fields like:
   - **Control theory** (`eess.SY`, `cs.SY`, `math.OC`)
   - **Communication theory & Information theory** (`cs.IT`, `eess.SP`)
   - **Signal processing** (`eess.SP`)
   - **Networking / wireless / systems theory** (`cs.NI`, `cs.DC` — excluding pure software verification & pure TCS)
   - **Potentially Machine Learning theory** (`cs.LG`, `stat.ML` — theoretical ML papers proving regret, convergence, generalization bounds)

---

## TODO: Adjustments for Pilot v2 / Full Study

- [ ] **Refine arXiv category set** toward ECE / engineering math-proof domains:
  - **Add:** `eess.SP` (Signal Processing — currently missing from Pilot v1!), `math.OC` (Optimization and Control), and evaluate a scoped slice of `cs.LG` / `stat.ML` (high volume; consider a dedicated ML-theory sub-study or targeted window).
  - **Trim / Filter:** Explicitly exclude papers whose primary category is CS theory (`cs.CC`, `cs.DS`, `cs.LO`, `cs.DM`, `cs.FL`, `cs.CG`) even when cross-listed into `cs.DC`/`cs.IT`, and distinguish **math-proof-in-engineering-theory** papers from **software/systems/hardware formal verification** papers (e.g., policy engines, VMs, CDC pipelines in `cs.CR`/`cs.DC`/`cs.DB`).
- [ ] **Drop Beyond-Lean classification track** in future automated runs (or keep zero-token regex counts only for appendix context) so all LLM budget goes into deeper Lean paradigm & error auditing.
- [ ] **Add a `paper_domain_role` classifier field** in Stage 4 distinguishing:
  1. `engineering_math_proof` (Lean verifies/supplements mathematical theorems in control, comms, signal processing, info theory, optimization, ML theory)
  2. `software_or_system_fv` (Lean verifies an implementation, VM, policy engine, protocol, or hardware/chip design)
  3. `pure_tcs_or_math` (pure theoretical CS / combinatorics / algebra cross-listed into engineering)
- [ ] **Phase 2 Deep Layer-A Audit:** Once scoped to `engineering_math_proof` Lean papers, run adversarial LaTeX ↔ Lean statement comparison (`proof-methods.md` Layer A Modes #1–#4) on the confirmed engineering-theory papers.

---

## Feedback from Scott Moeller (2026-11-24 — Post-v0.6 Review)

*(Full analysis, applicability matrix, and early exploration steps archived in [`docs/scope_refinement_and_future_actions.md`](scope_refinement_and_future_actions.md).)*

Key points to explore for v0.7 / archival submission or follow-on work:
1. **Sharper differentiation of three distinct populations (plus meta-systems):** Separate **(a) pure engineering / algorithmic proofs** (original target), **(b) theoretical math / CS cross-lists**, and **(c) software, hardware, database, and protocol operational-correctness proofs** (plus **meta autoformalization frameworks** like *Paper2Lean*/*LongTails*/*Colombo*), addressing the conditional IRR blur on `paper_domain_role` ($\kappa = 0.217$) and reporting stratified longitudinal curves rather than only pooled rates.
2. **Pull in additional pure-engineering domains:** Scout unscanned engineering arXiv categories (`eess.IV`, `eess.AS`, `cs.CE`, `math.NA`/`cs.NA`, `cs.PF`, `cs.GT`, `physics.flu-dyn`, `physics.comp-ph`) and off-arXiv engineering venues (TechRxiv, engrXiv, OpenAlex) to test adoption beyond the 8-category anchor.
3. **Re-examine failure-mode applicability for operational SW/HW/DB correctness works:** Audit whether our math-proof-derived "what often goes wrong" findings (Table 1, especially Layer A Modes #1–#4 such as `Mode3_CustomDefs` / Mathlib anchoring) transfer to hardware/database/software operational-correctness papers—or whether those works have a fundamentally different failure-mode profile (model-to-implementation refinement gap, fault/environment assumptions, trace/liveness vacuity, extraction TCB) warranting an explicit scope boundary and/or a separate study.

### Category Enlargement Decision (Bhaskar Krishnamachari, 2026-11-24)
- Grounded in USC Ming Hsieh ECE lab domains (Salman Avestimehr, Andreas Molisch, Mihailo Jovanovic, Antonio Ortega) plus **queueing theory**, **stochastic network control**, and **operations research**.
- **Whole-category census rule:** Take **entire arXiv categories** (100% census per matched window, zero sub-sampling), explicitly state in the paper which categories were kept vs. excluded, and justify each decision in terms of engineering applicability.
- **Approved +7 pure-engineering categories** (Tier 1 + Tier 2 minus `cs.MA`, ML [`stat.ML`/`cs.LG`], and tentatively `math.NA`): **`cs.PF`**, **`eess.IV`**, **`eess.AS`** (completing 100% of `eess.*`), **`cs.GT`**, **`cs.CE`**, **`physics.flu-dyn`**, and **`math.DS`** (`1,353` raw / `1,339` unique / `1,199` net-new Nov 1–19, 2026 papers; core panel grows **8 → 15 categories**, `5,303` unique T2 papers). **Phase A2 zero-token T2 scout DONE (2026-11-24)** ([`reports/scout_eng_tier12_2026_11.md`](../reports/scout_eng_tier12_2026_11.md)): `cs.PF` (`0/94`), `eess.IV` (`0/175`), `eess.AS` (`0/134`), `cs.CE` (`0/146`) are clean 0% nulls (completing 100% `eess.*` with `0/752` across `SP∪IV∪AS`); `physics.flu-dyn` = `2/278` (`0.72%`, both `math.AP` cross-lists); `math.DS` = `18/360` (`5.00%`); `cs.GT` = `16/166` (`9.64%`) → `36` Stage-2 Lean candidates (`34` net-new).
- **Excluded / Undecided:** `cs.MA`, `stat.ML`, `cs.LG` excluded per Bhaskar (avoiding AI/ML and multi-agent dilution); `math.NA` tentatively excluded/undecided (*"Would probably take out math.na.. not sure"* — A2 metadata probe of all `446` T2 `math.NA` papers found `3/4` metadata-strong hits already captured in our 15-cat panel and the sole net-new hit is `cs.AI` meta-system `2611.10961`); `math.PR` deferred pending Track 1 pure-math vs. engineering-theory filter validation.

### TODO: LaTeX Manuscript Updates for v0.7 (`papers/arxiv-empirical/main.tex`)
*(Detailed section-by-section drafting notes in [`docs/scope_refinement_and_future_actions.md`](scope_refinement_and_future_actions.md#latex-manuscript-drafting-notes-planned-v07-revisions-in-papersarxiv-empiricalmaintex).)*
- [ ] **Abstract & Sec. 1 (Intro):** Replace USC ANRG lab-anchor rationale with the whole-category **15-category engineering panel (including 100% of `eess.*`)** and state up front the 4-way separation (`eng_algorithmic_proof` vs. `operational_system_fv` vs. `pure_math_or_tcs` vs. `meta_formalization_system`).
- [ ] **Sec. 2 (Background / Taxonomy):** Add an explicit **Scope Boundary** note explaining why Table 1's Layer-A math-proof failure modes (especially `Mode3_CustomDefs` / Mathlib anchoring) do *not* naively apply to operational SW/HW/DB verification, and update `Domain Role` to the sharpened 4-way taxonomy.
- [ ] **Sec. 3 (Methodology):** Add a **Category Inclusion & Exclusion Table** listing all 15 kept whole arXiv categories and all major excluded category families (`math.*`/pure TCS, operational FV `cs.PL`/`cs.SE`/`cs.AR`/`cs.DB`/`cs.OS`, empirical AI/ML `cs.LG`/`cs.AI`/`cs.CL`/`cs.CV`/`cs.MA`/`stat.ML`, non-engineering sciences) with explicit engineering-applicability justifications, plus a note on whole-category cross-list transparency.
- [ ] **Secs. 4–6 (Results, Phase 2, Longitudinal):** Report both unfiltered 15-category census totals and strict `eng_algorithmic_proof`-only stratified curves/LoC/tier metrics (separating meta-systems like *LongTails*/*Paper2Lean*), highlight 100% `eess.*` coverage, and cite the 4-repo `operational_system_fv` diagnostic as empirical justification for keeping Phase 2 scoped to algorithmic/math proofs.
- [ ] **Sec. 8 (IRR) & Sec. 9 (Threats to Validity):** Add updated dual-rater IRR on the 4-way role taxonomy, plus explicit external-validity bullets for arXiv venue selection bias (TechRxiv/engrXiv/OpenAlex check), 19-day matched temporal windowing vs. whole-category completeness, and operational-FV non-generalizability.
- [ ] **CI Gate (`scripts/check_paper_numbers.py`):** Update automated numeric verification for all new v0.7 tables, stratified counts, and 15-category totals.
