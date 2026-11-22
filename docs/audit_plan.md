# Pre-Submission Audit Plan & Ground-Truth Ledger

**Last updated:** 2026-11-22  
**Scope:** Systematic ground-truth verification of bibliography citations, named empirical/Layer-A findings, methodological weaknesses, and publication compliance for [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) and [`papers/shared/references.bib`](../papers/shared/references.bib).

---

## Status Summary

| Pillar | Scope | Status | Key Artifact / Gate |
| :--- | :--- | :--- | :--- |
| **Pillar 1** | Deterministic + Semantic Bibliography Audit (all 54 entries) | **DONE** | [`scripts/audit_bib.py`](../scripts/audit_bib.py) (CI + `--live`), [`tests/test_audit_bib.py`](../tests/test_audit_bib.py) |
| **Pillar 2 (Automated)** | Commit-SHA / Zenodo Pinning (20 repos) + Automated `file:line` & Named-Critique Verification | **DONE** | [`scripts/pin_phase2_provenance.py`](../scripts/pin_phase2_provenance.py), [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) |
| **Pillar 2 (Human)** | Independent Human Verification of Named Findings + Clean-Cohort False-Negative Check | **OPEN** | [`artifacts/human_annotations/`](../artifacts/human_annotations/README.md) |
| **Pillar 3** | Closing Core Methodological Weaknesses (IRR, Docker Builds, Scope/ML Arm, Numeric Sync) | **OPEN** | [`artifacts/sandbox_builds/`](../artifacts/sandbox_builds/README.md), `scripts/check_paper_numbers.py` |
| **Pillar 4** | Pre-Submission Policy & Framing Gates (arXiv Non-Survey Retitle + AI Disclosure + Double-Blind Gate) | **DONE (arXiv)**; venue-tailored templates open | [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex), [`docs/publication_strategy.html`](publication_strategy.html) |

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

1. **Pinned Immutable Provenance (`n = 20`):** [`scripts/pin_phase2_provenance.py`](../scripts/pin_phase2_provenance.py) exported [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) covering all 20 Layer-A audited repositories (19 Git commit SHAs + 1 Zenodo record `24136107`, exact arXiv versions audited, `lean-toolchain`, and deterministic `.lean` tree SHA-256 hashes).
2. **Direct Code Verification of the 4 Named Negative Findings:**
   - **`2611.26272` (*Paper2Lean* / `TTony2019/OptPaper`, `v1`, commit `1bde49b1bdcb`, 2026-09-26):**
     - Verified paper abstract/intro literally claims *"all identified discrepancies were repaired in the released projects"* and *"no unresolved discrepancies identified in the audit."*
     - Verified **strongest unflagged finding**: `Moudafi & Oliny` is scored `11/11 (100%)` faithful in Paper2Lean's Table 1, yet `thm_1.lean:1500` adds global Lipschitzness `hB_lipschitz`, whereas `IsCocoerciveWRT` (`def_5.lean:28-29`) is strictly weaker quasi-cocoercivity (quantified only over zeros $y \in (A+B)^{-1}(0)$).
     - Verified **nuance corrected in `main.tex`**: `Guler_1992/items/thm_3.lean:42-44` explicitly acknowledges `[FiniteDimensional ℝ H]` in its Lean docstring (while omitting it from the paper text, and Table 1 scores `Guler` as `34/35 = 97%`, `Abbas & Attouch` as `37/38 = 97%`, `Adly & Attouch` as `20/25 = 80%`). Updated `main.tex` wording to distinguish 100%-scored vs. partially-scored Table 1 items and docstring-only disclosures.
   - **`2611.04876` (*MatrixRefresh* / `sdziembowski/MatrixRefresh`, `v1`, commit `7da3e1162e0f`, 2026-11-16):** Verified `version-1.0/lean/Compiler.lean:1936-1978` defines `Compiler.main_theorem` solely over four statistical-distance privacy conjuncts; updated path/line citation in `main.tex`.
   - **`2605.14610` (*Ku-PATP* / `SZabolotnii/Ku-PATP-code-supplement`, `v5`, commit `69788a926f22`):** Verified `Lean/PATP/Entropy.lean:166-174` proves `Real.exp 1 / Real.sqrt 2` ($\approx 1.9221$, docstring L164 writes `1.9230`) vs. paper §2.5 table `1.9300`.
   - **`2605.02856` (*Qanary* / `rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856`, `v2`, commit `915da15f64a1`):** Verified `QanaryPaper7/MontgomeryPFPINI.lean:47-48` directly postulates the closed-form two-branch map and `QanaryPaper7/KStageComposition.lean:168-190` uses a non-recursive two-case `match k` without induction.
3. **Automated `file:line` Reference Audit Across All 20 `layer_a_audits.json` Entries:**
   - **194 / 196** `*.lean:line` citations in `theorems_compared` resolve to existing files with in-bounds line numbers.
   - **2 out-of-bounds line citations flagged in raw LLM audit JSON** (neither is cited in `main.tex`, but both should be corrected during human review):
     - `2611.05136`: `ActualConstructiveSampler.lean:130-149` (file has `88` lines).
     - `2611.15128`: `AffineCombinerChart.lean:310-401` (file has `322` lines).

### Pillar 2 Checklist
- [x] Generate [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) with full 40-char commit SHAs, arXiv versions, toolchains, and automated `file:line` checks for all 20 audited repos.
- [x] Tighten named-finding prose and exact `file:line` / commit citations in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) and verify clean LaTeX + blind-artifact builds.
- [ ] **Human verification of the 4 named critiques** (`2611.26272`, `2611.04876`, `2605.14610`, `2605.02856`) + check whether any of those 4 GitHub repos pushed newer commits fixing the issues after our snapshot dates; record in [`artifacts/human_annotations/layer_a_human_verification.json`](../artifacts/human_annotations/README.md).
- [ ] **False-negative spot-check on "clean" author-owned repos:** Independently human-audit 4–5 of the 16/17 "clean" author-owned repos (prioritizing the largest codebases: `2611.08172`, `2611.13872`, `2605.09552`, `2611.11713`) to test whether the LLM auditor missed undisclosed drift in the positive cohort.
- [ ] **Optional courtesy outreach:** Notify authors of `2611.26272` (and `2611.04876`, `2605.14610`, `2605.02856`) with exact commit SHAs and `file:line` findings prior to archival submission.

---

## Pillar 3: Closing Core Methodological Weaknesses

- [ ] **Human Inter-Rater Reliability (IRR) for LLM-as-a-Judge (Stages 4 & 5):**
  - Two humans independently annotate a stratified sample (all 20 Layer-A audit verdicts + ~30 Stage-4 candidates including borderline `citation_only`/false-positive items).
  - Archive labels in `artifacts/human_annotations/stage4_irr.csv` and `layer_a_human_verification.json`; compute and report Cohen's $\kappa$ / Krippendorff's $\alpha$.
  - *(For EMSE / ACM TOSEM / NeurIPS D&B)*: Run an open-weight judge baseline on a subset to verify judge-family robustness.
- [ ] **Sandboxed Docker Dynamic Kernel Verification (`lake build` + `#print axioms`):**
  - Execute clean-room isolated builds under [`sandbox/`](../sandbox/README.md) on compact engineering repos (`<15k` LoC: `Lean-SysID`, `bic-public`, `CoprimeFrobenius`, `discrete-modified-gradient-lean`, `trustbound`, `ExactShortestPathsAndFlowsOnPlanarGraphs`, `zenodo/24127514`, `Ku-PATP-code-supplement`, `qanary-k-stage-composition`, `AltOMD-Lean`, `wmfki_lean`).
  - Archive machine-readable pass/fail, exact `#print axioms`, and `comparator` results in [`artifacts/sandbox_builds/`](../artifacts/sandbox_builds/README.md) to ground-truth static `Tier3_Gold` labels.
- [ ] **Unprofiled Artifacts, ML-Theory Arm & Scope Hygiene:**
  - Unpack the 3 arXiv ancillary/zipped artifacts (`2611.26140`, `2611.16781`, `2611.12585`) and retry `2611.22732` (`gitlab.mpi-sws.org`) to close remaining Stage-3 blind spots.
  - Run a scoped `cs.LG` / `stat.ML` arm (1-week window or stratified 1,000-paper sample) to benchmark ML theory against `math.OC` and `cs.IT`.
  - Audit calendar/conference-deadline confounders around Nov 1–19 and May 1–19, and replace USC ANRG lab-anchor rationale with an external IEEE/ACM disciplinary framing for archival variants.
- [ ] **Automated Paper-to-Artifact Numeric Consistency Check (`scripts/check_paper_numbers.py`):**
  - Programmatically verify every headline count, percentage, CI, and LoC figure in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) against [`artifacts/longitudinal_summary.json`](../artifacts/longitudinal_summary.json) and `artifacts/slices/*/figure_inputs.json` in CI.

---

## Pillar 4: Pre-Submission Policy & Framing Gates

### Completed for the arXiv Empirical Preprint (`papers/arxiv-empirical/main.tex`)
- [x] **Retitled & reframed away from "Survey"** across Title, Abstract, Section 3 heading, and captions in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (*An Empirical Longitudinal Measurement of arXiv Preprints...*) to avoid arXiv's un-refereed CS survey/position-paper desk-rejection policy (see [`docs/publication_strategy.html`](publication_strategy.html#L630-L649)).
- [x] **Added explicit `AI-Use Disclosure and Human Accountability` section** in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) separating (1) AI as an empirical research instrument (`run_workflow` `flash`/`flash_lite`/`pro` read-only agents, date, prompts/schemas in `workflows/`) from (2) AI-assisted engineering & drafting under full human verification and responsibility.
- [x] **Verified double-blind review packaging** via `uv run python scripts/export_blind_artifact.py` (`36 files`, `0 leaks`, enforced in CI).

### Downstream Venue-Specific Adaptations (Once Target Peer-Reviewed Venue Is Chosen)
- [ ] **Select primary downstream venue** (e.g., CACM / IEEE Software vs. ITP 2027 vs. EMSE / ACM TOSEM vs. NeurIPS 2027 D&B) and fork a venue-specific manuscript under `papers/<venue>/`.
- [ ] **Adapt AI-Use disclosure wording & placement to the chosen publisher:**
  - *IEEE (IEEE Software, Computer, TSE, Proc. IEEE):* Move drafting disclosure into **Acknowledgments** citing exact sections per PSPB §8.2.1.B.10.
  - *Elsevier / Cell Press (Patterns):* Use verbatim pre-References section title *"Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"*.
  - *Springer Nature (EMSE, Nature Machine Intelligence):* Pair Amber Tier declaration with human IRR ($\kappa$/$\alpha$) and an open-weight judge baseline in Methods.
  - *ACM (CACM, TOSEM, ASE) / NeurIPS / ITP:* Keep full Methods instrument documentation, complete venue paper checklists, and strip author/ANRG/GitHub identifiers for double-blind tracks.
