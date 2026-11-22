# Survey Progress & Next Steps

**Last updated:** 2026-11-22  
**Status:** **Longitudinal Baseline Slices (T0 Nov 2025 & T1 May 2026) + Pilot Paper v0.4 COMPLETE** (**9,837** preprints across 3 matched 19-day 8-category slices; 99.68% full-text coverage; contemporaneous `v1` adoption **0.00% → 0.15% → 0.95%** vs. flat Beyond-Lean control **1.52% → 1.33% → 1.17%**; 3 retroactive `v2` Lean additions identified; 20 total Layer-A audited repos; compiled LaTeX Pilot Paper v0.4).

---

## 1. Completed Milestones

- [x] **Reference Taxonomy & Scope Grounding**
  - Archived taxonomy of 12 failure modes, 5 verification gates, and 4 Lean↔LaTeX authoring paradigms in [`proof-methods.md`](../proof-methods.md).
  - Grounded Pilot v1 in USC ANRG's 6 core categories (`cs.DC`, `cs.NI`, `cs.IT`, `eess.SY`, `cs.CR`, `cs.RO`) and expanded Pilot v2 per Bhaskar's feedback ([`docs/research_notes_and_todo.md`](research_notes_and_todo.md)) to **`eess.SP`** and **`math.OC`**.
- [x] **Phase 0 (v1 + v2): Zero-Token Deterministic Pipeline**
  - Upgraded [`src/ingest_arxiv.py`](../src/ingest_arxiv.py) to arXiv's official OAI-PMH `arXivRaw` harvester (`oaipmh.arxiv.org/oai`) and updated [`src/db.py`](../src/db.py) to set-union `matched_target_cats_json` on conflict (`4,104` unique papers, Nov 1 – Nov 19, 2026; `4,060` excluding pure-TCS primary categories).
  - [`src/fetch_and_screen.py`](../src/fetch_and_screen.py) — **99.83% full-text coverage** (3,849 HTML5, 248 PDF, 7 HTTP 404s; 98.7% corpus reduction; **3.4×** recall over metadata-only: 55 Lean candidates vs 16 metadata-only).
  - [`src/profile_artifacts.py`](../src/profile_artifacts.py) — strictly static LaTeX + **GitHub** (up to 600 MB, including `leanEthereum/leanVM`), **GitLab** (including self-hosted hosts), and **Zenodo** REST API static archive profiler (`24` unique primary Lean repos scanned, **4.17M LoC**).
  - [`src/calibrate_recall.py`](../src/calibrate_recall.py) — Stage-2 recall calibration across **200** random GitHub-linked negatives (`333` unique GitHub repos via `gh api` recursive trees) + **100** non-GitHub negatives → **0 / 200** missed Lean repos (**1.49%** 95% Clopper–Pearson upper bound; [`reports/recall_calibration.md`](../reports/recall_calibration.md)).
- [x] **Phase 1 (v1 + v2): Parallel `run_workflow` Classification & Unified SQLite Reporting**
  - Classified all 55 Lean candidates (`flash` read-only `research` agents; Lean-only in v2, skipping Beyond-Lean LLM spend) + re-classified Zenodo/`leanVM` upgrades (`2611.15201`, `2611.15128`, `2611.10810` → all upgraded to `Tier3_Gold`).
  - Updated [`src/report_phase1.py`](../src/report_phase1.py) to report across all SQLite rows → [`reports/phase1_survey.md`](../reports/phase1_survey.md).
- [x] **Phase 2 (v1 + v2): Expanded Adversarial Layer-A Semantic Fidelity Audit (`n = 17`)**
  - Expanded [`src/prepare_phase2_audit.py`](../src/prepare_phase2_audit.py) (with PDF fallback + `--unaudited-only`) and ran 9 new parallel `pro` adversarial referee audits alongside the original 8 → **17 audited `engineering_math_proof` repos** ([`reports/phase2_layer_a_audit.md`](../reports/phase2_layer_a_audit.md)).
  - Compiled Pilot Paper v0.3: [`src/pilot/main.tex`](../src/pilot/main.tex) → [`src/pilot/main.pdf`](../src/pilot/main.pdf).

- [x] **Longitudinal Baseline Slices (T0: Nov 1–19, 2025 & T1: May 1–19, 2026) & Pilot Paper v0.4**
  - Upgraded [`src/ingest_arxiv.py`](../src/ingest_arxiv.py) with single-pass bias-free multi-slice OAI-PMH harvesting (omitting `until` for historical windows so later-revised preprints are never dropped — rescuing **35.4%** of Nov 2025 and **31.8%** of May 2026 papers) and verified counts against `arxiv.org/list`.
  - Screened, statically profiled, and `flash`-classified **T0 (`data/slice_2025_11.db`, 2,435 papers, 99.43% coverage)** and **T1 (`data/slice_2026_05.db`, 3,298 papers, 99.70% coverage)** without modifying `data/survey.db`.
  - Verified `v1` vs. `v_latest` on all revised historical Lean papers, uncovering **3 retroactive post-hoc autoformalizations** (`2511.15517`, `2605.09552`, `2605.19531`) totaling 374.6k LoC added 5–7 months after initial posting.
  - Audited all **3** cloned T1 `engineering_math_proof` repos (`pro` tier) → [`reports/slice_2026_05_phase2_audit.md`](../reports/slice_2026_05_phase2_audit.md) (total audited cohort: **20 repos**).
  - Built [`src/report_longitudinal.py`](../src/report_longitudinal.py) → [`reports/longitudinal_analysis.md`](../reports/longitudinal_analysis.md), generated [`src/pilot/figures/fig_longitudinal_curve.pdf`](../src/pilot/figures/fig_longitudinal_curve.pdf), and compiled Pilot Paper v0.4 ([`src/pilot/main.tex`](../src/pilot/main.tex) → [`src/pilot/main.pdf`](../src/pilot/main.pdf)).

---

## 2. Headline Results (Longitudinal T0 / T1 / T2 & Pilot v0.4)

| Finding | Longitudinal / Pilot v0.4 Result (8 Categories) |
| :--- | :--- |
| **Total longitudinal corpus** | **9,837** unique preprints (**9,806** full-text screened = **99.68%**): T0 `2,435` (99.43%), T1 `3,298` (99.70%), T2 `4,104` (99.83%) |
| **Lean 4 adoption curve (`v1` contemp.)** | **0 / 2,435 (0.00%, 95% UB 0.12%)** → **5 / 3,298 (0.15%)** → **39 / 4,104 (0.95%)** — **6.3×** jump in 6 months (non-overlapping 95% CIs) |
| **Lean 4 adoption (`v_latest`)** | **1 (0.04%)** → **7 (0.21%)** → **39 (0.95%)** (**23.1×** YoY; **4.5×** in 6 mo), capturing 3 retroactive `v2` formalizations (`2511.15517`, `2605.09552`, `2605.19531`) |
| **Flat Beyond-Lean FV control (Stage 2)** | **1.52% (37)** → **1.33% (44)** → **1.17% (48)** — Lean 4 candidates (`3 → 19 → 55`) overtook all other FV tools combined in Nov 2026 |
| **Scale, AI & Tier shift (T1→T2 `v1`)** | Median owned LoC **749 → 23,932 (32.0×)**; explicit AI disclosure **40% → 76.9%** (sole `explicitly_no` paper is May 2026 `2605.14610`); `Tier3_Gold` **0% → 48.7%** |
| **Stage-2 recall calibration (T2)** | **0 / 200** GitHub-linked negatives (333 repos checked; **1.49%** 95% Clopper–Pearson upper bound); **0 / 100** non-GitHub broad metadata hits |
| **T2 Engineering Math Proof slice** | **28 / 39 (71.8%)** — led by **`math.OC` (19/724 = 2.62%, 17 eng-math)**, `cs.DC` (1.79%), `cs.IT` (1.78%), `cs.CR` (1.11%), `eess.SY` (0.41%); `cs.NI` (0/559 across 3 slices) and `cs.RO` (0/2,431 across 3 slices) stay 0.00% |
| **Phase 2 Layer-A Audit (`n = 20` total)** | May 2026 `v1` repos (`2605.14610`, `2605.02856`) scored `partial` with `moderate` Mode #3 abstractions; **17/17 Oct–Nov 2026 author-owned repos** (16 T2 + Oct 2026 `v2` `2605.09552`) have **0** moderate/severe M1 drift or M3 smuggling; **sole `material_undisclosed_drift_or_risk`** is bulk pipeline **`2611.26272` (*Paper2Lean*)**. |

---

## 3. Prioritized Remaining Next Steps

1. **Sandboxed Lean Kernel Verification in Docker (`lake build` + `#print axioms`):**
   - Execute isolated clean-room builds on compact engineering repos (`<5k` LoC: `Lean-SysID`, `bic-public`, `CoprimeFrobenius`, `discrete-modified-gradient-lean`, `trustbound`, `ExactShortestPathsAndFlowsOnPlanarGraphs`, `zenodo/24127514`, `Ku-PATP-code-supplement`, `qanary-k-stage-composition`) to measure out-of-the-box reproducibility.
2. **Scoped Machine Learning Theory Arm (`cs.LG` / `stat.ML`):**
   - Run a 1-week window or stratified 1,000-paper sample of `cs.LG`/`stat.ML` to benchmark ML theory against `math.OC` and `cs.IT`.
3. **Standalone Periodic Runner (`agy -p`):**
   - Wrap the classifier prompt + JSON schema in `src/classify_cli.py` for unattended quarterly longitudinal snapshots.

---

## 4. Reproducing / Extending the Pipeline

```bash
uv sync

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

# 7. Build the pilot LaTeX paper
make -C src/pilot
```
