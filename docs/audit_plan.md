# Pre-Submission Audit Plan & Ground-Truth Ledger

**Last updated:** 2026-11-25  
**Scope:** Systematic ground-truth verification of bibliography citations, named empirical/Layer-A findings, methodological weaknesses, and publication compliance for [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (v0.7, 15-category longitudinal panel) and [`papers/shared/references.bib`](../papers/shared/references.bib).

---

## Status Summary

| Pillar | Scope | Status | Key Artifact / Gate |
| :--- | :--- | :--- | :--- |
| **Pillar 1** | Deterministic + Semantic Bibliography Audit (all 65 entries, 64 arXiv eprints) | **DONE** | [`scripts/audit_bib.py`](../scripts/audit_bib.py) (CI + `--live`), [`tests/test_audit_bib.py`](../tests/test_audit_bib.py) |
| **Pillar 2 (Automated)** | Commit-SHA / Zenodo / Ancillary Pinning (27 repos: 23 orig-8 + 4 `+7`) + Automated `file:line` (`274/274`) & Named-Critique Verification | **DONE** | [`scripts/pin_phase2_provenance.py`](../scripts/pin_phase2_provenance.py), [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json), [`artifacts/phase_c2_plus7_audits.json`](../artifacts/phase_c2_plus7_audits.json) |
| **Pillar 2 (Human)** | Guided Human Co-Review of 4 Named Findings + 5 Clean-Cohort False-Negative Spot-Checks (`0/5` missed drift) | **DONE** | [`docs/human_verification_plan.md`](human_verification_plan.md), [`artifacts/human_annotations/layer_a_human_verification.json`](../artifacts/human_annotations/layer_a_human_verification.json) |
| **Pillar 3** | Closing Core Methodological Weaknesses (15-Category Longitudinal Panel `12,613` Papers, 4-Way Stratification, Off-arXiv Probe, Operational-FV Boundary + D2 Spin-Off, Automated Numeric Sync, Stage-3 Ancillary/Zip Unpacking, `n = 17` Compact Docker Kernel Builds, & Blinded Stage-4 Human IRR **DONE for arXiv v0.7**; 2nd Rater + Open-Weight Judge + ML Arm **OPEN for Archival Venues**) | **DONE (arXiv v0.7)** | [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py) (CI), [`artifacts/phase_c1_15cat_longitudinal.json`](../artifacts/phase_c1_15cat_longitudinal.json), [`artifacts/off_arxiv_probe.json`](../artifacts/off_arxiv_probe.json), [`artifacts/sandbox_builds/summary.json`](../artifacts/sandbox_builds/summary.json), [`artifacts/human_annotations/stage4_irr_summary.json`](../artifacts/human_annotations/stage4_irr_summary.json) |
| **Pillar 4** | Pre-Submission Policy & Framing Gates (arXiv Non-Survey Retitle + Whole-Category Disciplinary Scope Replacing Lab Anchor + AI Disclosure + Double-Blind Gate + v0.7 Promotion) | **DONE (arXiv v0.7)**; venue-tailored templates open | [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex), [`docs/operational_fv_spinoff_brief.md`](operational_fv_spinoff_brief.md), [`docs/publication_strategy.html`](publication_strategy.html) |

---

## Pillar 1: Deterministic + Semantic Bibliography Audit

### Ground-Truth Findings (2026-11-22)

All **54 entries** in [`papers/shared/references.bib`](../papers/shared/references.bib) (100% cited in `main.tex`, 0 uncited, 0 missing) were audited against live arXiv metadata (`export.arxiv.org/api/query`) and our local OAI-PMH SQLite databases:

- **47 / 47 surveyed arXiv preprints** (`arxiv2611_*`, `arxiv2605_*`, `arxiv2511_*`): Exact matches against OAI-PMH `arXivRaw` and live arXiv API (normalized 2 raw UTF-8 author names `K{\"u}mmerle`, `F{\"u}gger` to TeX escapes for BibTeX safety).
- **1 classic Lean 4 citation** (`demoura2021lean4`): Verified CADE-28 (2021) Springer reference; added DOI `10.1007/978-3-030-79876-5_37`.
- **6 background 2025–2026 arXiv entries** (`lines 10–56`): All 6 eprint IDs were real (0 hallucinated IDs), but **5 of 6 had defective BibTeX metadata** and **1 had an in-text citation misattribution**, all now resolved:

| BibTeX Key | arXiv ID | Defect Found Before Fix | Ground-Truth Resolution |
| :--- | :--- | :--- | :--- |
| `proofbridge2025` | `2510.15681` | Placeholder `{ProofBridge Authors}`, paraphrased title, **AND misattributed in `main.tex` L79 & L148** for *"hostile cross-LLM back-translation diffs"* / *"adversarial referee agents"* (live HTML has 0 hits for `back-translation`, `hostile`, `adversarial`, `referee`, or `audit`). | Updated to real 6 authors (`Jana et al.`) & real title (*Auto-Formalization of Natural Language Proofs in Lean via Joint Embeddings*, `cs.LO`). Fixed `main.tex` L79 to cite `proofbridge2025` accurately for *formal bidirectional equivalence checking* and moved cross-LLM semantic-auditing citations at L79 & L148 to `bastounis2026navier` (Fig. 3). |
| `leanatlas2026` | `2604.16347` | Placeholder `{Lean Atlas Authors}` + paraphrased title. | Updated to `Banri Yanahama and Akiyoshi Sannai` & exact arXiv title (`cs.HC`). Prose claims (Lean Compass pruning, semantic hallucination) verified against live HTML. |
| `axle2026` | `2606.26442` | Placeholder `{Axle Authors}` + paraphrased title. | Updated to 6 real authors (`Xin et al.`) & exact arXiv title (`cs.LO`). Prose stat (`95.7 s` median, `93.8%` completion under `600 s` = `6.2%` timeouts) verified in Table 3 of live HTML. |
| `bastounis2026navier` | `2610.08144` | Paraphrased subtitle (*Type I vs. Type II Autoformalization*). | Updated to exact arXiv title (`math.AP`). Type (i)/(ii), Lemma 8.6, Lemma 10.5, and ChatGPT-6 auditor (Fig. 3) verified in live HTML. |
| `zhu2026leanarchitect` | `2601.22554` | Paraphrased subtitle (*Synchronized Formalization Blueprints for Lean 4*). | Updated to exact arXiv title (*Automating Blueprint Generation for Humans and AI*, `cs.LO`). |
| `paglieri2026swarms` | `2609.04170` | Truncated author list (`Davide Paglieri and others`). | Expanded to all 6 authors (`cs.AI`). |

### Pillar 1 Checklist
- [x] Fix all 6 background entries + `demoura2021lean4` DOI + UTF-8 author escapes in [`papers/shared/references.bib`](../papers/shared/references.bib).
- [x] Fix misattributed `proofbridge2025` citations in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex).
- [x] Implement [`scripts/audit_bib.py`](../scripts/audit_bib.py) (offline CI gate + `--live` arXiv API check) and [`tests/test_audit_bib.py`](../tests/test_audit_bib.py).
- [x] Wire `uv run python scripts/audit_bib.py` into [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) and pass live verification on all 53 arXiv eprints (`0 issues`).
- [ ] Before promoting any additional references from [`docs/proof-methods.md`](proof-methods.md) (e.g., `2608.25449`, `2602.01291`, blog posts) into other paper variants (CACM / *Proc. IEEE* / ITP), run `scripts/audit_bib.py --live` and perform the same semantic claim-to-source check on each added citation.

---

## Pillar 2: Ground-Truth Verification of Named Findings & Commit Pinning

### Automated Ground-Truth Findings (2026-11-22)

1. **Pinned Immutable Provenance (`n = 23`):** [`scripts/pin_phase2_provenance.py`](../scripts/pin_phase2_provenance.py) exported [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) covering all 23 Layer-A audited repositories (20 Git commit SHAs + 1 Zenodo record `24136107` + 2 arXiv ancillary packages `2611.26140`/`2611.12585`, exact arXiv versions audited, `lean-toolchain`, and deterministic `.lean` tree SHA-256 hashes), with **`239/239` (100%)** resolved & in-bounds `file:line` citations.
2. **Direct Code Verification of the 4 Named Negative Findings:**
   - **`2611.26272` (*Paper2Lean* / `TTony2019/OptPaper`, `v1`, commit `1bde49b1bdcb`, 2026-09-26):**
     - Verified paper abstract/intro literally claims *"all identified discrepancies were repaired in the released projects"* and *"no unresolved discrepancies identified in the audit."*
     - Verified **strongest unflagged finding**: `Moudafi & Oliny` is scored `11/11 (100%)` faithful in Paper2Lean's Table 1, yet `thm_1.lean:1500` adds global Lipschitzness `hB_lipschitz`, whereas `IsCocoerciveWRT` (`def_5.lean:28-29`) is strictly weaker quasi-cocoercivity (quantified only over zeros $y \in (A+B)^{-1}(0)$).
     - Verified **nuance corrected in `main.tex`**: `Guler_1992/items/thm_3.lean:42-44` explicitly acknowledges `[FiniteDimensional ℝ H]` in its Lean docstring (while omitting it from the paper text, and Table 1 scores `Guler` as `34/35 = 97%`, `Abbas & Attouch` as `37/38 = 97%`, `Adly & Attouch` as `20/25 = 80%`). Updated `main.tex` wording to distinguish 100%-scored vs. partially-scored Table 1 items and docstring-only disclosures.
   - **`2611.04876` (*MatrixRefresh* / `sdziembowski/MatrixRefresh`, `v1`, commit `7da3e1162e0f`, 2026-11-16):** Verified `version-1.0/lean/Compiler.lean:1936-1978` defines `Compiler.main_theorem` solely over four statistical-distance privacy conjuncts; updated path/line citation in `main.tex`.
   - **`2605.14610` (*Ku-PATP* / `SZabolotnii/Ku-PATP-code-supplement`, `v5`, commit `69788a926f22`):** Verified `Lean/PATP/Entropy.lean:166-174` proves `Real.exp 1 / Real.sqrt 2` ($\approx 1.9221$, docstring L164 writes `1.9230`) vs. paper §2.5 table `1.9300`.
   - **`2605.02856` (*Qanary* / `rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856`, `v2`, commit `915da15f64a1`):** Verified `QanaryPaper7/MontgomeryPFPINI.lean:47-48` directly postulates the closed-form two-branch map and `QanaryPaper7/KStageComposition.lean:168-190` uses a non-recursive two-case `match k` without induction.
3. **Automated `file:line` Reference Audit Across All 20 `layer_a_audits.json` Entries (`196 / 196` Clean):**
   - Initially caught **2 out-of-bounds line citations** in raw LLM audit JSON (194/196). Both were verified against the cloned repos and corrected in `data/survey.db`, [`artifacts/slices/2026-11/layer_a_audits.json`](../artifacts/slices/2026-11/layer_a_audits.json), [`reports/slices/2026-11/phase2_layer_a_audit.md`](../reports/slices/2026-11/phase2_layer_a_audit.md), and [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json):
     - `2611.05136`: `ActualConstructiveSampler.lean:130-149` (88 lines) → `ActualConstructiveProgram.lean:130-149` (152 lines; namespace `CurrentAFT.ActualConstructiveSampler`, defining `public_matrix_error_independent` and `ideal_response_preserved`).
     - `2611.15128`: `AffineCombinerChart.lean:310-401` / `310-315` (322 lines) → `AffineCombinerFactor.lean:310-401` / `310-315` (406 lines; defining `hatP_eq`).
   - Re-running [`scripts/pin_phase2_provenance.py`](../scripts/pin_phase2_provenance.py) now verifies **196 / 196 (100%)** resolved & in-bounds (enforced by [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py)).

### Pillar 2 Checklist
- [x] Generate [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) with full 40-char commit SHAs, arXiv versions, toolchains, and automated `file:line` checks for all 20 audited repos.
- [x] Fix both out-of-bounds `file:line` citations (`2611.05136`, `2611.15128`) in SQLite, `layer_a_audits.json`, and `phase2_layer_a_audit.md` → **196/196** resolved & in-bounds.
- [x] Tighten named-finding prose and exact `file:line` / commit citations in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) and verify clean LaTeX + blind-artifact builds.
- [x] **Human verification of the 4 named critiques** (`2611.26272`, `2611.04876`, `2605.14610`, `2605.02856`) + live GitHub HEAD check (`4/4` unchanged on 2026-11-23); co-reviewed with AI syntax translation (`annotator_1`), tightened `Attouch_Adly` `thm_9.lean` wording in `main.tex` to drop unverified external `$o(1/\ln t)$` claim, and logged in [`artifacts/human_annotations/layer_a_human_verification.json`](../artifacts/human_annotations/layer_a_human_verification.json).
- [x] **False-negative spot-check on "clean" author-owned repos (`n = 5`):** Co-reviewed 5 of the largest clean author-owned repos (`2611.13872`, `2605.09552`, `2611.08172`, `2611.11713`, `2611.12585`) — **0/5 missed undisclosed drift**; logged in [`artifacts/human_annotations/layer_a_human_verification.json`](../artifacts/human_annotations/layer_a_human_verification.json).
- [ ] **Optional courtesy outreach:** Notify authors of `2611.26272` (and `2611.04876`, `2605.14610`, `2605.02856`) with exact commit SHAs and `file:line` findings prior to archival submission.

---

## Pillar 3: Closing Core Methodological Weaknesses

- [x] **Human Inter-Rater Reliability (IRR) for LLM-as-a-Judge (arXiv 1-rater tier COMPLETE; 2nd rater open for archival venues):**
  - Completed strictly blinded Stage-4 IRR on a deterministic stratified sample ($n = 30$ across T1/T2, seed `20261123`) via [`docs/stage4_irr_walkthrough.html`](stage4_irr_walkthrough.html), archived in [`artifacts/human_annotations/stage4_irr.csv`](../artifacts/human_annotations/stage4_irr.csv) and [`stage4_irr_summary.json`](../artifacts/human_annotations/stage4_irr_summary.json), scored by [`scripts/compute_irr.py`](../scripts/compute_irr.py): **30/30 (100.0%, $\kappa = 1.000, \alpha = 1.000$)** on `lean_usage_status`, moderate-to-substantial overall conditional agreement ($\kappa = 0.573\text{--}0.754$), and transparent 3-cause reconciliation of all 26 conditional disagreements across $n = 16$ agreed contributors. Paired with guided human co-review of 4/4 named Stage-5 critiques + 5/5 clean spot-checks (`0/5` missed drift) in [`layer_a_human_verification.json`](../artifacts/human_annotations/layer_a_human_verification.json) and integrated into `main.tex` v0.6 Section 8.
  - *(For EMSE / ACM TOSEM / NeurIPS D&B)*: Add independent second human rater (`annotator_2`) for Human–Human IRR and an open-weight judge baseline on a subset to verify judge-family robustness.
- [x] **Sandboxed Docker Dynamic Kernel Verification (`lake build` + `#print axioms`, `n = 14`):**
  - Built [`sandbox/Dockerfile`](../sandbox/Dockerfile), [`sandbox/check_axioms.lean`](../sandbox/check_axioms.lean), [`sandbox/container_entry.py`](../sandbox/container_entry.py), and [`sandbox/run_sandbox_audit.py`](../sandbox/run_sandbox_audit.py) enforcing a two-phase clean-room security boundary (`--network=none`, `--user 65534:65534`, `--cap-drop=ALL`, `--security-opt=no-new-privileges:true`, read-only source mounts).
  - Executed the exhaustive cohort of all **14** standalone primary Lean 4 repositories `<15k` LoC across T2 (`n = 11`) and T1 (`n = 3`) and archived structured JSON logs in [`artifacts/sandbox_builds/`](../artifacts/sandbox_builds/README.md) (`results_2026-11.json`, `results_2026-05.json`, `summary.json`): **11/14 (78.6%)** build out of the box (**3,190** theorems audited; median `28.4s`), **0/14** proof-compilation errors, **0/14** `Lean.ofReduceBool`, **7/8 (87.5%)** compact `Tier3_Gold` OOTB pass & **7/7 (100%)** axiom-clean (`2,263` theorems), `2/2` packaging-fail repos (`2611.18220`, `2611.23762`) pass axiom-clean in synthetic documented envs (`3,254` total audited theorems), `1/14` (`2605.02856`) fails missing `../qanary-*` sibling paths, and `2/2` Mode #6 repos dynamically corroborated (`sorryAx` in 9/570 theorems of `2611.16690`; 11 custom axioms in `2605.16407`).
  - Integrated Section 7 + Table 7 + Figure 6 (`fig_sandbox_builds.pdf`) into [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex), extended [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py) to gate all sandbox numbers/rows, and added [`tests/test_sandbox_builds.py`](../tests/test_sandbox_builds.py).
- [x] **Close Stage-3 Unprofiled Ancillary/Zip Artifacts & Retry `gitlab.mpi-sws.org`:**
  - Extended [`src/profile_artifacts.py`](../src/profile_artifacts.py) to unpack arXiv `/src/` ancillary Lean trees/nested tarballs and GitHub zipped Lean archives statically (with SHA-256 deduplication).
  - Unpacked & profiled **3 of 4** remaining blind spots — all **0 `sorry`**, **0 custom `axiom`**, **0 `native_decide`**: `2611.26140` (`28,043` LoC, 53 files, Lean `v4.15.0`), `2611.16781` (`34,579` LoC, 121 files, 1,192 `#print axioms`, Lean `v4.33.0-rc1`), and `2611.12585` (`60,664` LoC, 341 files, 2,715 `#print axioms`, Lean `v4.35.0`). T2 scanned confirmed papers rose `25 → 28` (`27` unique primary artifacts), median owned LoC rose `23,932 → 29,005` (`38.7×` over T1), total owned LoC rose `2.98M → 3.10M` (`4.30M` raw).
  - Retried `2611.22732` (`gitlab.mpi-sws.org/FCS/mixnets-sync-public`): DNS resolves (`139.19.205.205`), but ports 443 and 80 persistently time out from this host; documented in `main.tex`.
- [x] **Automated Paper-to-Artifact Numeric Consistency Gate ([`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py)):**
  - Programmatically verifies every bolded count, percentage, CI, multiplier, LoC aggregate, table cell (`tab:categories`, `tab:distributions`, all 39 rows of `tab:inventory`, `tab:longitudinal`), cross-artifact parity (`longitudinal_summary.json` vs. `artifacts/slices/*/figure_inputs.json`), recall calibration, and `phase2_provenance.json` (`196/196`).
  - Wired into [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) with drift-detection unit tests in [`tests/test_check_paper_numbers.py`](../tests/test_check_paper_numbers.py). Caught and fixed a pre-existing rounding inconsistency on the YoY Stage-2 Lean candidate rate multiplier (`11.2×` from rounded `1.34/0.12` → exact `10.9×`).
- [x] **Phase-2 Layer-A Semantic Audits on the 3 Newly Unpacked Packages (`2611.26140`, `2611.16781`, `2611.12585`):**
  - Completed `pro`-tier adversarial Layer-A audits (2026-11-23), raising the audited cohort from `20 → 23` (`20` in T2 + `3` in T1; `239/239` resolved in-bounds `file:line` refs): `2611.16781` scored `high_faithful` (`minor_undisclosed` M1, `minor_disclosed` M2, `none` M3/M4, `strong_mathlib`), `2611.12585` scored `mostly_faithful_with_disclosed_gaps` (`minor_disclosed` M1/M2, `none` M3/M4, `strong_mathlib`), and `2611.26140` scored `partial_or_weakened_formalization` (`minor_disclosed` M1, `moderate` M2 candidly omitting `W_opt`/`GuardsCorridor` game reductions, `none` M3/M4, `mixed_custom_and_mathlib`). All 3 include explicit non-vacuity witnesses (`13/20 = 65.0%` in T2) and preserve **0/20** moderate/severe M1/M3/M4 failures across all Oct–Nov 2026 author-owned repos.
- [ ] **ML-Theory Arm & Scope Hygiene:**
  - Run a scoped `cs.LG` / `stat.ML` arm (1-week window or stratified 1,000-paper sample) to benchmark ML theory against `math.OC` and `cs.IT`.
  - Audit calendar/conference-deadline confounders around Nov 1–19 and May 1–19, and replace USC ANRG lab-anchor rationale with an external IEEE/ACM disciplinary framing for archival variants.

---

## Pillar 4: Pre-Submission Policy & Framing Gates

### Completed for the arXiv Empirical Preprint (`papers/arxiv-empirical/main.tex`)
- [x] **Retitled & reframed away from "Survey"** across Title, Abstract, Section 3 heading, and captions in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (*An Empirical Longitudinal Measurement of arXiv Preprints...*) to avoid arXiv's un-refereed CS survey/position-paper desk-rejection policy (see [`docs/publication_strategy.html`](publication_strategy.html#L630-L649)).
- [x] **Added explicit `AI-Use Disclosure and Human Accountability` section + per-task model/effort provenance table (Table 7)** in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex), verified directly from all 150 execution transcripts (81 local + 69 remote):
  - Stage 4 Lean classification (`flash`, 80 runs): **Gemini 4 Hydrogen (High)** (`gemini-4-hydrogen-tiered-high`) via Google Antigravity `run_workflow`
  - Stage 4 Pilot v1 Beyond-Lean baseline (`flash_lite`, 34 runs): **Gemini 3.5 Flash-Lite** (`gemini-3.5-flash-lite`) via Google Antigravity `run_workflow`
  - Stage 5 Layer-A semantic audits (`pro`, 23 runs): **Gemini 4 Hydrogen (Extra High)** (`gemini-4-hydrogen-tiered-xhigh`) via Google Antigravity `run_workflow`
  - All code writing & manuscript drafting (Abstract + Sections 1–7): **Gemini 4 Neon (High)** (`gemini-4-neon-high`) via Google Antigravity CLI harness (with auxiliary interactive sessions on Gemini 4 Neon Medium and Gemini 4 Carbon High).
- [x] **Verified double-blind review packaging** via `uv run python scripts/export_blind_artifact.py` (`37 files`, `0 leaks`, enforced in CI).

### Downstream Venue-Specific Adaptations (Once Target Peer-Reviewed Venue Is Chosen)
- [ ] **Select primary downstream venue** (e.g., CACM / IEEE Software vs. ITP 2027 vs. EMSE / ACM TOSEM vs. NeurIPS 2027 D&B) and fork a venue-specific manuscript under `papers/<venue>/`.
- [ ] **Adapt AI-Use disclosure wording & placement to the chosen publisher:**
  - *IEEE (IEEE Software, Computer, TSE, Proc. IEEE):* Move drafting disclosure into **Acknowledgments** citing exact sections per PSPB §8.2.1.B.10.
  - *Elsevier / Cell Press (Patterns):* Use verbatim pre-References section title *"Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"*.
  - *Springer Nature (EMSE, Nature Machine Intelligence):* Pair Amber Tier declaration with human IRR ($\kappa$/$\alpha$) and an open-weight judge baseline in Methods.
  - *ACM (CACM, TOSEM, ASE) / NeurIPS / ITP:* Keep full Methods instrument documentation, complete venue paper checklists, and strip author/ANRG/GitHub identifiers for double-blind tracks.
