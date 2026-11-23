# Survey Progress & Next Steps

**Last updated:** 2026-11-23  
**Status:** **Clean Multi-Variant Repository Layout + Longitudinal Baseline Slices (T0 Nov 2025 & T1 May 2026) + Complete Phase-2 Layer-A Audits ($n = 23$) + Sandboxed Docker Dynamic Kernel Verification ($n = 14$) + Pilot Paper v0.5 COMPLETE** (**9,837** preprints across 3 matched 19-day 8-category slices; 99.68% full-text coverage; contemporaneous `v1` adoption **0.00% → 0.15% → 0.95%** vs. flat Beyond-Lean control **1.52% → 1.33% → 1.17%**; **23** total Layer-A audited repos with `239/239` verified `file:line` citations; **14/14 compact repos dynamically audited in `--network=none` Docker**, `11/14 = 78.6%` OOTB pass, `3,190` OOTB theorems, `7/7` OOTB `Tier3_Gold` axiom-clean, `0/14` `Lean.ofReduceBool`; zero-PDF Git layout with automated CI figure & LaTeX builds).

---

## 1. Completed Milestones

- [x] **Reference Taxonomy & Scope Grounding**
  - Archived taxonomy of 12 failure modes, 5 verification gates, and 4 Lean↔LaTeX authoring paradigms in [`docs/proof-methods.md`](proof-methods.md).
  - Grounded Pilot v1 in USC ANRG's 6 core categories (`cs.DC`, `cs.NI`, `cs.IT`, `eess.SY`, `cs.CR`, `cs.RO`) and expanded Pilot v2 per Bhaskar's feedback ([`docs/research_notes_and_todo.md`](research_notes_and_todo.md)) to **`eess.SP`** and **`math.OC`**.
- [x] **Phase 0 (v1 + v2): Zero-Token Deterministic Pipeline**
  - Upgraded [`src/ingest_arxiv.py`](../src/ingest_arxiv.py) to arXiv's official OAI-PMH `arXivRaw` harvester (`oaipmh.arxiv.org/oai`) and updated [`src/db.py`](../src/db.py) to set-union `matched_target_cats_json` on conflict (`4,104` unique papers, Nov 1 – Nov 19, 2026; `4,060` excluding pure-TCS primary categories).
  - [`src/fetch_and_screen.py`](../src/fetch_and_screen.py) — **99.83% full-text coverage** (3,849 HTML5, 248 PDF, 7 HTTP 404s; 98.7% corpus reduction; **3.4×** recall over metadata-only: 55 Lean candidates vs 16 metadata-only).
  - [`src/profile_artifacts.py`](../src/profile_artifacts.py) — strictly static LaTeX + **GitHub** (up to 600 MB, including `leanEthereum/leanVM` and zipped Lean archives), **GitLab** (including self-hosted hosts), **Zenodo** REST API static archive profiler, and **arXiv `/src/` ancillary Lean tree/archive** unpacker (`27` unique primary Lean artifacts covering `28` T2 papers, **4.30M raw LoC** / **3.10M paper-owned LoC**).
  - [`src/calibrate_recall.py`](../src/calibrate_recall.py) — Stage-2 recall calibration across **200** random GitHub-linked negatives (`333` unique GitHub repos via `gh api` recursive trees) + **100** non-GitHub negatives → **0 / 200** missed Lean repos (**1.49%** 95% Clopper–Pearson upper bound; [`reports/slices/2026-11/recall_calibration.md`](../reports/slices/2026-11/recall_calibration.md)).
- [x] **Phase 1 (v1 + v2): Parallel `run_workflow` Classification & Unified SQLite Reporting**
  - Classified all 55 Lean candidates (`flash` read-only `research` agents; Lean-only in v2, skipping Beyond-Lean LLM spend) + re-classified Zenodo/`leanVM` upgrades (`2611.15201`, `2611.15128`, `2611.10810` → all upgraded to `Tier3_Gold`).
  - Updated [`src/report_phase1.py`](../src/report_phase1.py) to report across all SQLite rows → [`reports/slices/2026-11/phase1_survey.md`](../reports/slices/2026-11/phase1_survey.md).
- [x] **Phase 2 (v1 + v2 + Ancillary/Zip): Expanded Adversarial Layer-A Semantic Fidelity Audit (`n = 20` T2 + `3` T1 = `23` total)**
  - Expanded [`src/prepare_phase2_audit.py`](../src/prepare_phase2_audit.py) (with PDF fallback + `--unaudited-only`) and ran `pro` adversarial referee audits across all **20** locally inspected T2 `engineering_math_proof` packages (8 Pilot v1 + 9 Pilot v2 + 3 newly unpacked arXiv-ancillary/zipped packages `2611.26140`, `2611.16781`, `2611.12585`; [`reports/slices/2026-11/phase2_layer_a_audit.md`](../reports/slices/2026-11/phase2_layer_a_audit.md)) plus all **3** T1 packages ([`reports/slices/2026-05/phase2_layer_a_audit.md`](../reports/slices/2026-05/phase2_layer_a_audit.md)), with **`239/239` (100%)** resolved & in-bounds `file:line` provenance in [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json).
- [x] **Longitudinal Baseline Slices (T0: Nov 1–19, 2025 & T1: May 1–19, 2026) & Pilot Paper v0.4**
  - Upgraded [`src/ingest_arxiv.py`](../src/ingest_arxiv.py) with single-pass bias-free multi-slice OAI-PMH harvesting (omitting `until` for historical windows so later-revised preprints are never dropped — rescuing **35.4%** of Nov 2025 and **31.8%** of May 2026 papers) and verified counts against `arxiv.org/list`.
  - Screened, statically profiled, and `flash`-classified **T0 (`data/slice_2025_11.db`, 2,435 papers, 99.43% coverage)** and **T1 (`data/slice_2026_05.db`, 3,298 papers, 99.70% coverage)** without modifying `data/survey.db`.
  - Verified `v1` vs. `v_latest` on all revised historical Lean papers, uncovering **3 retroactive post-hoc autoformalizations** (`2511.15517`, `2605.09552`, `2605.19531`) totaling 374.6k LoC added 5–7 months after initial posting.
  - Audited all **3** cloned T1 `engineering_math_proof` repos (`pro` tier) → [`reports/slices/2026-05/phase2_layer_a_audit.md`](../reports/slices/2026-05/phase2_layer_a_audit.md) (total audited cohort: **20 repos**).
  - Built [`src/report_longitudinal.py`](../src/report_longitudinal.py) → [`reports/longitudinal_analysis.md`](../reports/longitudinal_analysis.md) + [`artifacts/longitudinal_summary.json`](../artifacts/longitudinal_summary.json), decoupled [`src/generate_figures.py`](../src/generate_figures.py) from SQLite using git-tracked `artifacts/`, and promoted the manuscript to [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (compiled PDFs published automatically via [`build-papers.yml`](../.github/workflows/build-papers.yml) and the [`papers-latest` release](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/releases/download/papers-latest/arxiv-empirical.pdf)).
- [x] **Clean Multi-Variant Repository Reorganization & CI/Open-Science Scaffolding**
  - Executed [`docs/reorg_plan.md`](reorg_plan.md): promoted `papers/shared/` & `papers/arxiv-empirical/` with zero PDFs in Git, added [`src/export_artifacts.py`](../src/export_artifacts.py) + [`artifacts/slices/manifest.json`](../artifacts/slices/manifest.json), normalized `reports/slices/{2025-11,2026-05,2026-11}/`, added [`scripts/export_blind_artifact.py`](../scripts/export_blind_artifact.py), [`sandbox/README.md`](../sandbox/README.md), [`tests/test_patterns.py`](../tests/test_patterns.py), `LICENSE`, `CITATION.cff`, and GitHub Actions workflows ([`build-papers.yml`](../.github/workflows/build-papers.yml), [`ci.yml`](../.github/workflows/ci.yml)).
- [x] **Pre-Submission Automated Audit & Hygiene Pass ([`docs/audit_plan.md`](audit_plan.md))**
  - **Pillar 1 (BibTeX & Live arXiv Audit):** Fixed all 6 background entries + `proofbridge2025` citation framing; added [`scripts/audit_bib.py`](../scripts/audit_bib.py) (offline CI + `--live` across all 53 arXiv eprints) and [`tests/test_audit_bib.py`](../tests/test_audit_bib.py).
  - **Pillar 2 (Immutable Provenance):** Pinned all 20 Layer-A repos (19 Git SHAs + 1 Zenodo record) in [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) and fixed both out-of-bounds `file:line` citations (`2611.05136`, `2611.15128`) → **`196/196` (100%) resolved & in-bounds**.
  - **Pillar 3 (Stage-3 Blind-Spot Closure & Numeric Consistency Gate):** Unpacked & profiled `2611.26140` (28.0k LoC), `2611.16781` (34.6k LoC), and `2611.12585` (60.7k LoC) — all zero `sorry`/custom `axiom`/`native_decide` — and retried `2611.22732` (`gitlab.mpi-sws.org`, persistent port-443/80 timeout). Added [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py) (CI gate + [`tests/test_check_paper_numbers.py`](../tests/test_check_paper_numbers.py)), verifying every bolded count, %, CI, multiplier, LoC, and table cell in `main.tex` against `artifacts/` (also catching and fixing `11.2× → 10.9×` exact YoY Stage-2 candidate ratio).
  - **Pillar 4 (arXiv Framing & AI Provenance):** Retitled away from "Survey" and added transcript-verified Table 7 AI provenance disclosure in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex).

- [x] **Sandboxed Docker Dynamic Kernel Verification (`n = 14` Compact Repos `<15k` LoC):**
  - Implemented strict two-phase clean-room harness under [`sandbox/`](../sandbox/README.md) (`Dockerfile`, `check_axioms.lean`, `container_entry.py`, `run_sandbox_audit.py`) with `--network=none`, `--user 65534:65534`, `--cap-drop=ALL`, `--security-opt=no-new-privileges:true`, and read-only source/toolchain/Mathlib-cache mounts.
  - Evaluated the exhaustive cohort of all **14** standalone primary Lean 4 repos `<15k` LoC across T2 (`n = 11`) and T1 (`n = 3`) and archived JSON logs in [`artifacts/sandbox_builds/`](../artifacts/sandbox_builds/README.md): **11/14 (78.6%)** OOTB pass (**3,190** theorems audited; median `28.4s`), **0/14** proof compile errors, **0/14** `Lean.ofReduceBool`, **7/8 (87.5%)** compact `Tier3_Gold` OOTB pass & **7/7 (100%)** axiom-clean (`2,263` theorems), `2/2` packaging-fail repos (`2611.18220`, `2611.23762`) pass axiom-clean in synthetic documented envs (`3,254` total theorems), `1/14` (`2605.02856`) fails due to missing `../qanary-*` local path deps, and `2/2` Mode #6 repos dynamically corroborated (`sorryAx` in 9/570 theorems of `2611.16690`; 11 custom axioms in `2605.16407`).
  - Added Figure 6 (`fig_sandbox_builds.pdf`), Section 7 + Table 7 in [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (Pilot v0.5), CI numeric checks in [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py), and [`tests/test_sandbox_builds.py`](../tests/test_sandbox_builds.py).

---

## 2. Headline Results (Longitudinal T0 / T1 / T2 & Pilot v0.5)

| Finding | Longitudinal / Pilot v0.4 Result (8 Categories) |
| :--- | :--- |
| **Total longitudinal corpus** | **9,837** unique preprints (**9,806** full-text screened = **99.68%**): T0 `2,435` (99.43%), T1 `3,298` (99.70%), T2 `4,104` (99.83%) |
| **Lean 4 adoption curve (`v1` contemp.)** | **0 / 2,435 (0.00%, 95% UB 0.12%)** → **5 / 3,298 (0.15%)** → **39 / 4,104 (0.95%)** — **6.3×** jump in 6 months (non-overlapping 95% CIs) |
| **Lean 4 adoption (`v_latest`)** | **1 (0.04%)** → **7 (0.21%)** → **39 (0.95%)** (**23.1×** YoY; **4.5×** in 6 mo), capturing 3 retroactive `v2` formalizations (`2511.15517`, `2605.09552`, `2605.19531`) |
| **Flat Beyond-Lean FV control (Stage 2)** | **1.52% (37)** → **1.33% (44)** → **1.17% (48)** — Lean 4 candidates (`3 → 19 → 55`) overtook all other FV tools combined in Nov 2026 |
| **Scale, AI & Tier shift (T1→T2 `v1`)** | Median owned LoC **749 → 29,005 (38.7×)** (total **3.10M** owned / **4.30M** raw across 28 scanned T2 papers); explicit AI disclosure **40% → 76.9%** (sole `explicitly_no` paper is May 2026 `2605.14610`); `Tier3_Gold` **0% → 48.7%** |
| **Stage-2 recall calibration (T2)** | **0 / 200** GitHub-linked negatives (333 repos checked; **1.49%** 95% Clopper–Pearson upper bound); **0 / 100** non-GitHub broad metadata hits |
| **T2 Engineering Math Proof slice** | **28 / 39 (71.8%)** — led by **`math.OC` (19/724 = 2.62%, 17 eng-math)**, `cs.DC` (1.79%), `cs.IT` (1.78%), `cs.CR` (1.11%), `eess.SY` (0.41%); `cs.NI` (0/559 across 3 slices) and `cs.RO` (0/2,431 across 3 slices) stay 0.00% |
| **Phase 2 Layer-A Audit (`n = 23` total)** | May 2026 `v1` repos (`2605.14610`, `2605.02856`) scored `partial` with `moderate` Mode #3 abstractions; **20/20 Oct–Nov 2026 author-owned repos** (19 T2 + Oct 2026 `v2` `2605.09552`; `13/20 = 65.0%` T2 non-vacuity witnesses, `239/239` verified `file:line` refs) have **0** moderate/severe M1 drift or M3 smuggling; **sole `material_undisclosed_drift_or_risk`** is bulk pipeline **`2611.26272` (*Paper2Lean*)**. |
| **Sandboxed Kernel Verification (`n = 14`, `<15k` LoC)** | **11/14 (78.6%)** OOTB pass in `--network=none` Docker (**3,190** OOTB theorems; **3,254** incl. synthetic; median `28.4s`), **0/14** compile errors, **0/14** `Lean.ofReduceBool`; **7/8** compact `Tier3_Gold` OOTB pass (**7/7 = 100%** axiom-clean); **2/2** Mode #6 flags dynamically corroborated (`sorryAx` in `2611.16690`, 11 custom axioms in `2605.16407`); all 3 OOTB fails are Mode #12 packaging/local-dep omissions (`2611.18220`, `2611.23762`, `2605.02856`). |

---

## 3. Prioritized Remaining Next Steps

*(Detailed pre-submission verification tracker and ground-truth audit ledger: [`docs/audit_plan.md`](audit_plan.md).)*

1. **Human IRR & Named-Finding Verification:**
   - [x] Audited & fixed all 54 BibTeX entries (`scripts/audit_bib.py --live` in CI), unpacked & Phase-2 Layer-A audited `2611.26140`/`2611.16781`/`2611.12585` (`n = 23` total audited repos), pinned commit SHAs / Zenodo / ancillary fingerprints & `239/239` clean `file:line` checks in [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json), added the CI numeric consistency gate [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py), and completed isolated Docker `lake build` + `#print axioms` verification on all 14 compact repos (`<15k` LoC) in [`artifacts/sandbox_builds/`](../artifacts/sandbox_builds/README.md).
   - [ ] Record independent human IRR calibration labels and human sign-off on named findings (+ clean-cohort false-negative spot-checks) under [`artifacts/human_annotations/`](../artifacts/human_annotations/README.md).
2. **Extend Sandboxed Dynamic Verification to Medium/Large Repos (`>15k` LoC) & `lake comparator` Replay:**
   - Extend `sandbox/run_sandbox_audit.py` to multi-10k LoC repos (`2611.12680`, `2611.14475`, `2611.26140`, `2611.16781`, `2611.12585`) and `comparator` replay on `P4` repos (`2611.15201`, `2611.14475`, `2611.04876`, `2611.13872`).
3. **Scoped Machine Learning Theory Arm (`cs.LG` / `stat.ML`):**
   - Run a 1-week window or stratified 1,000-paper sample of `cs.LG`/`stat.ML` to benchmark ML theory against `math.OC` and `cs.IT`.
4. **Standalone Periodic Runner (`agy -p`):**
   - Wrap the classifier prompt + JSON schema in `src/classify_cli.py` for unattended quarterly longitudinal snapshots (`T3: 2027-02`).

---

## 4. Reproducing / Extending the Pipeline

```bash
uv sync --dev
uv run pytest

# 1. Ingest arXiv metadata via official OAI-PMH arXivRaw harvester
uv run python -m src.ingest_arxiv --source oai --categories eess.SP math.OC --since 2026-11-01 --until 2026-11-22

# 2. Polite full-text HTML5/PDF fetch + deterministic pre-screen
uv run python -m src.fetch_and_screen --workers 6 --min-interval 0.25
uv run python -m src.fetch_and_screen --retry-failed --workers 6 --min-interval 0.25

# 3. Strictly static LaTeX + GitHub/GitLab/Zenodo profiler (requires `gh auth login`)
uv run python -m src.profile_artifacts
uv run python -m src.report_phase0

# 4. Stage-2 recall calibration on random Stage-2 negatives
uv run python -m src.calibrate_recall --gh-sample 200 --non-gh-sample 100

# 5. Export unclassified Lean candidates & run Stage 4 workflow
uv run python -m src.export_workflow_inputs --unclassified-only --lean-only --out data/workflow_inputs_v2.json
# After running workflows/classify_candidates.py -> data/workflow_outputs_v2.json:
uv run python -m src.report_phase1 --outputs data/workflow_outputs_v2.json

# 6. Phase 2 Layer-A semantic fidelity audit on unaudited engineering_math_proof repos
uv run python -m src.prepare_phase2_audit --unaudited-only --out data/phase2_inputs_v2.json
# After running workflows/audit_layer_a.py -> data/phase2_outputs_v2.json:
uv run python -m src.report_phase2 --outputs data/phase2_outputs_v2.json

# 7. Export canonical JSON artifacts, update longitudinal analysis, generate figures, and build paper
uv run python -m src.export_artifacts --all
uv run python -m src.report_longitudinal
uv run python -m src.generate_figures
make -C papers/arxiv-empirical

# 8. Run CI audit gates & build verified anonymized double-blind review archive
uv run python scripts/audit_bib.py
uv run python scripts/check_paper_numbers.py
uv run python scripts/export_blind_artifact.py
```
