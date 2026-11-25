# survey-lean-proofs-eng-arxiv

Empirical longitudinal study of engineering, optimization, systems, control, information theory, signal processing, security, and robotics arXiv preprints measuring **Lean 4 proof adoption**, **Lean↔LaTeX authoring paradigms**, **Stage-2 recall**, and **Layer-A semantic fidelity** (grounded in the taxonomy of [`docs/proof-methods.md`](docs/proof-methods.md)).

## Compiled Paper PDFs (Built Automatically in CI — Zero PDFs in Git)

Binary PDFs are **not committed to Git**. Every push to `main` regenerates all vector figures from git-tracked `artifacts/`, compiles every `papers/*/main.tex` variant cleanly via GitHub Actions, and publishes downloadable PDFs:

- **1-Click Latest PDF (Rolling Pre-Release):** [`arxiv-empirical.pdf` (`papers-latest` release)](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/releases/download/papers-latest/arxiv-empirical.pdf)
- **GitHub Actions Build Artifacts (Paper PDFs + Vector Figures):** [`build-papers.yml` workflow runs](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/actions/workflows/build-papers.yml)
- **Local Build:** `make -C papers/arxiv-empirical` (automatically regenerates missing figures from `artifacts/` into `papers/shared/figures/` and compiles `papers/arxiv-empirical/main.pdf`)

## Key Artifacts

- **Working Empirical Paper (LaTeX v0.7):** [`papers/arxiv-empirical/main.tex`](papers/arxiv-empirical/main.tex) ([`papers/shared/references.bib`](papers/shared/references.bib), [`papers/arxiv-empirical/Makefile`](papers/arxiv-empirical/Makefile))
- **Pre-Submission Audit Plan & Ground-Truth Ledger:** [`docs/audit_plan.md`](docs/audit_plan.md)
- **Progress Log & Next Steps:** [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md)
- **Scope Refinement & 15-Category Enlargement Plan:** [`docs/scope_refinement_and_future_actions.md`](docs/scope_refinement_and_future_actions.md) · [`docs/track1_4way_coding_rubric.md`](docs/track1_4way_coding_rubric.md)
- **Domain Scope Notes (Bhaskar Krishnamachari & Scott Moeller):** [`docs/research_notes_and_todo.md`](docs/research_notes_and_todo.md)
- **Publication Strategy Roadmap:** [`docs/publication_strategy.html`](docs/publication_strategy.html)
- **Error & Paradigm Taxonomy:** [`docs/proof-methods.md`](docs/proof-methods.md)
- **Machine-Readable Structured Artifacts (`artifacts/`, <1 MB, CC-BY-4.0):**
  - [`artifacts/slices/manifest.json`](artifacts/slices/manifest.json) — Declarative registry of all matched longitudinal slices (`2025-11` T0, `2026-05` T1, `2026-11` T2)
  - [`artifacts/longitudinal_summary.json`](artifacts/longitudinal_summary.json) — Aggregate cross-slice 8-category core metrics (`9,837` preprints, `0 → 5 → 39` contemporaneous `v1`, `1 → 7 → 39` `v_latest`)
  - [`artifacts/phase_c1_15cat_longitudinal.json`](artifacts/phase_c1_15cat_longitudinal.json) — **Full 15-category longitudinal panel (Phase C1, 100% of `eess.*`)**: `12,613` unique preprints (`99.61%` FT), contemporaneous `v1` `0 → 7 → 68` (`0.00% → 0.17% → 1.28%`, `7.6×` in 6 mo; `v_latest` `2 → 11 → 69`, `20.59×` YoY), strict `eng_algorithmic_proof` `0 → 3 → 26` (`6.77×`), plus per-slice `+7` 4-way classifications in `artifacts/slices/{2025-11,2026-05,2026-11}/plus7_classifications.json`
  - [`artifacts/phase_c2_plus7_audits.json`](artifacts/phase_c2_plus7_audits.json) & [`artifacts/slices/2026-11/plus7_layer_a_audits.json`](artifacts/slices/2026-11/plus7_layer_a_audits.json) — **Phase C2 targeted `+7` Stage-5 Layer-A audits (`n = 4`) & compact Docker kernel builds (`n = 3`)**: `35/35` (`274/274` combined) in-bounds `file:line` provenance, `0/4` (`0/22` combined 15-cat `eng_algorithmic_proof`) `material_undisclosed_drift_or_risk`, and `3/3 (100%)` OOTB `--network=none` Docker pass (`361` theorems audited; combined 15-cat compact: `14/17 = 82.4%` OOTB pass, `3,551` OOTB / `3,615` incl. synthetic theorems, `8/8` `Tier3_Gold` axiom-clean, `0/17` `Lean.ofReduceBool`)
  - [`artifacts/track1_sensitivity_summary.json`](artifacts/track1_sensitivity_summary.json), [`artifacts/scout_eng_tier12_2026_11_summary.json`](artifacts/scout_eng_tier12_2026_11_summary.json), & [`artifacts/track3_operational_fv_pilot.json`](artifacts/track3_operational_fv_pilot.json) — Phase A1/A2/B1 4-way stratification, +7 zero-token scout, and operational-FV pilot artifacts
  - [`artifacts/slices/2026-11/figure_inputs.json`](artifacts/slices/2026-11/figure_inputs.json), [`classifications.json`](artifacts/slices/2026-11/classifications.json), [`layer_a_audits.json`](artifacts/slices/2026-11/layer_a_audits.json), [`recall_calibration.json`](artifacts/slices/2026-11/recall_calibration.json)
  - [`artifacts/slices/2026-05/classifications.json`](artifacts/slices/2026-05/classifications.json), [`layer_a_audits.json`](artifacts/slices/2026-05/layer_a_audits.json) & [`artifacts/slices/2025-11/classifications.json`](artifacts/slices/2025-11/classifications.json)
  - [`artifacts/sandbox_builds/summary.json`](artifacts/sandbox_builds/summary.json), [`results_2026-11.json`](artifacts/sandbox_builds/results_2026-11.json), [`results_2026-05.json`](artifacts/sandbox_builds/results_2026-05.json), & [`results_plus7_2026-11.json`](artifacts/sandbox_builds/results_plus7_2026-11.json) — Isolated `--network=none` Docker `lake build` + programmatic `#print axioms` (`Lean.collectAxioms`) verification logs across all 14 orig-8 compact (`<15k` LoC) repos (`11/14` OOTB pass, `3,190` OOTB / `3,254` total theorems, `7/7` OOTB `Tier3_Gold` axiom-clean) plus all 3 net-new `+7` compact `eng_algorithmic_proof` repos (`3/3` OOTB pass, `361` theorems; combined 15-cat: `14/17 = 82.4%` OOTB pass, `3,551` OOTB / `3,615` total theorems, `0/17` `Lean.ofReduceBool`)
- **Rendered Survey Reports (`reports/`):**
  - [`reports/phase_c2_plus7_audits.md`](reports/phase_c2_plus7_audits.md) & [`reports/slices/2026-11/phase2_layer_a_audit_plus7.md`](reports/slices/2026-11/phase2_layer_a_audit_plus7.md) — **Phase C2 `+7` Layer-A semantic audits (`n = 4`) & compact Docker kernel verification (`n = 3`)** (`0/22` 15-cat `eng_algorithmic_proof` material undisclosed drift; `3/3` `+7` / `14/17` 15-cat compact OOTB Docker pass; `361` `+7` / `3,551` 15-cat OOTB theorems audited)
  - [`reports/phase_c1_15cat_longitudinal.md`](reports/phase_c1_15cat_longitudinal.md) — **Full 15-category longitudinal panel report (Phase C1, 100% of `eess.*`)** across **12,613** preprints (`0 → 7 → 68` `v1`, `2 → 11 → 69` `v_latest`, 4-way stratification, retroactive ledger, and targeted 4-repo Phase C2 queue)
  - [`reports/longitudinal_analysis.md`](reports/longitudinal_analysis.md) — **12-month longitudinal inflection analysis (8-category core)** across **9,837** preprints (T0: Nov 1–19, 2025; T1: May 1–19, 2026; T2: Nov 1–19, 2026; `v1` vs `v_latest` retroactive autoformalization + flat Beyond-Lean FV control)
  - [`reports/track1_sensitivity_analysis.md`](reports/track1_sensitivity_analysis.md), [`reports/scout_eng_tier12_2026_11.md`](reports/scout_eng_tier12_2026_11.md), & [`reports/track3_operational_fv_pilot.md`](reports/track3_operational_fv_pilot.md) — Track 1 4-way sensitivity, Track 2 +7 T2 scout, and Track 3 operational-FV pilot reports
  - [`reports/slices/2026-11/phase2_layer_a_audit.md`](reports/slices/2026-11/phase2_layer_a_audit.md) & [`reports/slices/2026-05/phase2_layer_a_audit.md`](reports/slices/2026-05/phase2_layer_a_audit.md) — Deep Layer-A semantic fidelity audits (Modes #1–#4) of **23** locally inspected `engineering_math_proof` Lean 4 repos (20 in T2 + 3 in T1)
  - [`reports/slices/2026-11/phase1_survey.md`](reports/slices/2026-11/phase1_survey.md), [`reports/slices/2026-05/phase1_survey.md`](reports/slices/2026-05/phase1_survey.md), [`reports/slices/2025-11/phase1_survey.md`](reports/slices/2025-11/phase1_survey.md) — Classified inventories across all three matched slices (`0 → 5 → 39` contemporaneous `v1`; `1 → 7 → 39` latest revision)
  - [`reports/slices/2026-11/recall_calibration.md`](reports/slices/2026-11/recall_calibration.md) — Stage-2 recall calibration auditing 200 random GitHub-linked negatives (333 repos checked; **0/200** missed Lean repos, 1.49% 95% upper bound) + 100 non-GitHub negatives
  - [`reports/slices/2026-11/phase0.md`](reports/slices/2026-11/phase0.md), [`reports/slices/2026-05/phase0.md`](reports/slices/2026-05/phase0.md), [`reports/slices/2025-11/phase0.md`](reports/slices/2025-11/phase0.md) — Zero-token deterministic full-text pre-screen & static repo stats

## Repository Layout

```text
survey-lean-proofs-eng-arxiv/
  README.md
  LICENSE                         # MIT (code) + CC-BY-4.0 (curated metadata/annotations)
  CITATION.cff                    # Standard citation metadata (GitHub / Zenodo)
  pyproject.toml / uv.lock
  .github/workflows/
    build-papers.yml              # Regenerates figures from artifacts/, compiles papers/*/main.tex,
                                  # uploads GH Actions PDFs + rolling `papers-latest` release
    ci.yml                        # Runs pytest, BibTeX audit, numeric consistency gate, zero-PDF & blind checks
  src/                            # Strictly static/deterministic Python pipeline & figures
    db.py                         # SQLite schema & idempotent upserts
    patterns.py                   # Deterministic Lean, Beyond-Lean, LaTeX, and static .lean scanners
    ingest_arxiv.py               # Stage 1: Bias-free multi-slice arXiv OAI-PMH (arXivRaw) ingest
    fetch_and_screen.py           # Stage 2: Polite HTML5/PDF full-text pre-screen
    profile_artifacts.py          # Stage 3: Strictly static LaTeX + GitHub/GitLab/Zenodo/arXiv-ancillary profiler
    calibrate_recall.py           # Stage-2 negative recall calibration via gh api
    export_workflow_inputs.py     # Export candidate bundles for parallel LLM classification
    prepare_phase2_audit.py       # Extract math-preserving Markdown & prep Layer-A audit bundles
    export_artifacts.py           # Export canonical, license-safe JSONs from SQLite -> artifacts/
    report_phase0.py              # Phase 0 markdown summary generator
    report_phase1.py              # Import classifications & generate Phase 1 report
    report_phase2.py              # Import Layer-A audits & generate Phase 2 report
    report_longitudinal.py        # Comparative T0 / T1 / T2 longitudinal analysis & JSON summary
    generate_figures.py           # Zero-DB vector PDF figure generator (reads artifacts/ by default)
  workflows/                      # Parallel LLM agent workflows (prompts + strict JSON schemas)
    classify_candidates.py        # Stage 4: Parallel candidate classifier (flash)
    audit_layer_a.py              # Stage 5: Adversarial Layer-A auditor (pro)
  sandbox/                        # Isolated Docker execution boundary (lake build / #print axioms)
  scripts/
    audit_bib.py                  # BibTeX hygiene, citation sync & --live arXiv API metadata audit
    check_paper_numbers.py        # Numeric consistency gate verifying main.tex against artifacts/
    pin_phase2_provenance.py      # Pins commit SHAs, toolchains & file:line checks for Phase-2 repos
    export_blind_artifact.py      # Builds verified double-blind review zip (dist/blind_artifact.zip)
  tests/
    test_patterns.py              # Unit tests for regex detectors, Lean lexer, and LaTeX scanners
    test_audit_bib.py             # Unit tests for BibTeX parser and hygiene checks
    test_check_paper_numbers.py   # Unit tests for numeric consistency gate and archive unpackers
  artifacts/                      # Git-tracked small structured outputs (<2 MB, license-safe)
    longitudinal_summary.json
    phase2_provenance.json        # Pinned commit SHAs, toolchains & 239/239 file:line provenance checks
    slices/
      manifest.json               # Declarative slice registry
      2025-11/                    # T0 classifications
      2026-05/                    # T1 classifications + Layer-A audits
      2026-11/                    # T2 classifications, Layer-A audits, recall calibration, figure inputs
    human_annotations/            # Schema & workflow for human IRR labels & commit-SHA pins
    sandbox_builds/               # Schema for isolated Docker kernel verification results
  reports/                        # Rendered Markdown reports (longitudinal + per-slice)
  papers/                         # ZERO PDFs in Git — built locally or via GitHub Actions
    shared/                       # Shared references.bib & generated figures/ (gitignored *.pdf)
    arxiv-empirical/              # Working empirical paper (main.tex + Makefile)
  docs/                           # Taxonomy (proof-methods.md), progress log, publication strategy
  data/                           # Gitignored local cache (SQLite DBs, cloned third-party repos)
```

## Quick Commands

```bash
# Install dependencies (including pytest dev group)
uv sync --dev

# Run unit tests and CI hygiene gates (BibTeX + paper-to-artifact numeric consistency)
uv run pytest
uv run python scripts/audit_bib.py
uv run python scripts/check_paper_numbers.py

# Regenerate all 6 vector PDF figures directly from git-tracked artifacts/ (no SQLite DB needed)
uv run python -m src.generate_figures

# Build the empirical paper PDF locally (auto-generates figures if missing)
make -C papers/arxiv-empirical

# Re-run isolated Docker lake build + #print axioms verification on compact repos (<15k LoC)
docker build -t lean-survey-sandbox:v1 sandbox/
uv run python sandbox/run_sandbox_audit.py                # Orig-8 compact cohort (n=14)
uv run python sandbox/run_sandbox_audit.py --cohort plus7 # Phase C2 +7 eng_alg compact cohort (n=3)

# Export a clean, verified double-blind review archive to dist/blind_artifact.zip
uv run python scripts/export_blind_artifact.py
```

See [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md) for full pipeline reproduction instructions (including SQLite ingestion, artifact export, and longitudinal regeneration).
