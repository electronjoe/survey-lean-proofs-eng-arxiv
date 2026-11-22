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
