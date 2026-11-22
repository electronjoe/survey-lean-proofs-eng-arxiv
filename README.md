# survey-lean-proofs-eng-arxiv

Empirical longitudinal study of engineering, optimization, systems, control, information theory, signal processing, security, and robotics arXiv preprints measuring **Lean 4 proof adoption**, **Lean↔LaTeX authoring paradigms**, **Stage-2 recall**, and **Layer-A semantic fidelity** (grounded in the taxonomy of [`docs/proof-methods.md`](docs/proof-methods.md)).

## Compiled Paper PDFs (Built Automatically in CI — Zero PDFs in Git)

Binary PDFs are **not committed to Git**. Every push to `main` regenerates all vector figures from git-tracked `artifacts/`, compiles every `papers/*/main.tex` variant cleanly via GitHub Actions, and publishes downloadable PDFs:

- **1-Click Latest PDF (Rolling Pre-Release):** [`arxiv-empirical.pdf` (`papers-latest` release)](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/releases/download/papers-latest/arxiv-empirical.pdf)
- **GitHub Actions Build Artifacts (Paper PDFs + Vector Figures):** [`build-papers.yml` workflow runs](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/actions/workflows/build-papers.yml)
- **Local Build:** `make -C papers/arxiv-empirical` (automatically regenerates missing figures from `artifacts/` into `papers/shared/figures/` and compiles `papers/arxiv-empirical/main.pdf`)

## Key Artifacts

- **Working Empirical Paper (LaTeX v0.4):** [`papers/arxiv-empirical/main.tex`](papers/arxiv-empirical/main.tex) ([`papers/shared/references.bib`](papers/shared/references.bib), [`papers/arxiv-empirical/Makefile`](papers/arxiv-empirical/Makefile))
- **Pre-Submission Audit Plan & Ground-Truth Ledger:** [`docs/audit_plan.md`](docs/audit_plan.md)
- **Progress Log & Next Steps:** [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md)
- **Domain Scope Notes (Bhaskar Krishnamachari & Scott Moeller):** [`docs/research_notes_and_todo.md`](docs/research_notes_and_todo.md)
- **Publication Strategy Roadmap:** [`docs/publication_strategy.html`](docs/publication_strategy.html)
- **Error & Paradigm Taxonomy:** [`docs/proof-methods.md`](docs/proof-methods.md)
- **Machine-Readable Structured Artifacts (`artifacts/`, <1 MB, CC-BY-4.0):**
  - [`artifacts/slices/manifest.json`](artifacts/slices/manifest.json) — Declarative registry of all matched longitudinal slices (`2025-11` T0, `2026-05` T1, `2026-11` T2)
  - [`artifacts/longitudinal_summary.json`](artifacts/longitudinal_summary.json) — Aggregate cross-slice longitudinal metrics (`9,837` preprints, `0 → 5 → 39` contemporaneous `v1`, `1 → 7 → 39` `v_latest`)
  - [`artifacts/slices/2026-11/figure_inputs.json`](artifacts/slices/2026-11/figure_inputs.json), [`classifications.json`](artifacts/slices/2026-11/classifications.json), [`layer_a_audits.json`](artifacts/slices/2026-11/layer_a_audits.json), [`recall_calibration.json`](artifacts/slices/2026-11/recall_calibration.json)
  - [`artifacts/slices/2026-05/classifications.json`](artifacts/slices/2026-05/classifications.json), [`layer_a_audits.json`](artifacts/slices/2026-05/layer_a_audits.json) & [`artifacts/slices/2025-11/classifications.json`](artifacts/slices/2025-11/classifications.json)
- **Rendered Survey Reports (`reports/`):**
  - [`reports/longitudinal_analysis.md`](reports/longitudinal_analysis.md) — **12-month longitudinal inflection analysis** across **9,837** preprints (T0: Nov 1–19, 2025; T1: May 1–19, 2026; T2: Nov 1–19, 2026; `v1` vs `v_latest` retroactive autoformalization + flat Beyond-Lean FV control)
  - [`reports/slices/2026-11/phase2_layer_a_audit.md`](reports/slices/2026-11/phase2_layer_a_audit.md) & [`reports/slices/2026-05/phase2_layer_a_audit.md`](reports/slices/2026-05/phase2_layer_a_audit.md) — Deep Layer-A semantic fidelity audits (Modes #1–#4) of **20** locally inspected `engineering_math_proof` Lean 4 repos (17 in T2 + 3 in T1)
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
    phase2_provenance.json        # Pinned commit SHAs, toolchains & 196/196 file:line provenance checks
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

# Regenerate all 5 vector PDF figures directly from git-tracked artifacts/ (no SQLite DB needed)
uv run python -m src.generate_figures

# Build the empirical paper PDF locally (auto-generates figures if missing)
make -C papers/arxiv-empirical

# Export a clean, verified double-blind review archive to dist/blind_artifact.zip
uv run python scripts/export_blind_artifact.py
```

See [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md) for full pipeline reproduction instructions (including SQLite ingestion, artifact export, and longitudinal regeneration).
