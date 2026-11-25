# survey-lean-proofs-eng-arxiv

Empirical longitudinal study of engineering, optimization, systems, control, information theory, signal processing, security, and robotics arXiv preprints measuring **Lean 4 proof adoption**, **Lean↔LaTeX authoring paradigms**, **Stage-2 recall**, and **Layer-A semantic fidelity** (grounded in the taxonomy of [`docs/proof-methods.md`](docs/proof-methods.md)).

## Compiled Paper PDFs (Built Automatically in CI — Zero PDFs in Git)

Binary PDFs are **not committed to Git**. Every push to `main` regenerates all vector figures from git-tracked `artifacts/`, compiles every `papers/*/main.tex` variant cleanly via GitHub Actions, and publishes downloadable PDFs:

- **1-Click Latest PDF (Rolling Pre-Release):** [`arxiv-empirical.pdf` (`papers-latest` release)](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/releases/download/papers-latest/arxiv-empirical.pdf)
- **GitHub Actions Build Artifacts (Paper PDFs + Vector Figures):** [`build-papers.yml` workflow runs](https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/actions/workflows/build-papers.yml)
- **Local Build:** `make -C papers/arxiv-empirical` (automatically regenerates missing figures from `artifacts/` into `papers/shared/figures/` and compiles `papers/arxiv-empirical/main.pdf`)

## Key Artifacts

- **Working Empirical Paper (Unified Single-Narrative 15-Category Manuscript):** [`papers/arxiv-empirical/main.tex`](papers/arxiv-empirical/main.tex) ([`papers/shared/references.bib`](papers/shared/references.bib), [`papers/arxiv-empirical/Makefile`](papers/arxiv-empirical/Makefile)) — 12,613-paper 15-category longitudinal panel (100% of `eess.*`), 4-way role stratification, 27-repo Layer-A audit (`0/22` engineering algorithmic material drift; `274/274` verified `file:line` refs; `6/6` human-signed named critiques + `5/5` clean spot-checks), 23/23 exhaustive compact Docker kernel builds (`18/23 = 78.3%` OOTB pass, `5,259` OOTB / `5,339` incl. synth theorems, `11/11` Gold axiom-clean), `0/250` stratified Stage-2 negative recall calibration (95% UB `1.19%`), 8/8 operational-FV boundary audit, off-arXiv check (TechRxiv/engrXiv/OpenAlex), blinded Stage-4 human IRR (`30/30`, $\kappa=1.000$), Appendix A 82-paper master ledger, and 89 live-verified BibTeX entries
- **Canonical Unified 15-Category Dataset:** [`artifacts/unified_15cat_panel.json`](artifacts/unified_15cat_panel.json) (synthesized via [`scripts/build_unified_15cat_artifacts.py`](scripts/build_unified_15cat_artifacts.py); sole input to [`src/generate_figures.py`](src/generate_figures.py) and [`scripts/check_paper_numbers.py`](scripts/check_paper_numbers.py))
- **Pre-Submission Audit Plan & Ground-Truth Ledger:** [`docs/audit_plan.md`](docs/audit_plan.md)
- **Progress Log & Next Steps:** [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md)
- **Scope Refinement, 15-Category Enlargement & Spin-Off Brief:** [`docs/scope_refinement_and_future_actions.md`](docs/scope_refinement_and_future_actions.md) · [`docs/track1_4way_coding_rubric.md`](docs/track1_4way_coding_rubric.md) · [`docs/operational_fv_spinoff_brief.md`](docs/operational_fv_spinoff_brief.md)
- **Domain Scope Notes (Bhaskar Krishnamachari & Scott Moeller):** [`docs/research_notes_and_todo.md`](docs/research_notes_and_todo.md)
- **Publication Strategy Roadmap:** [`docs/publication_strategy.html`](docs/publication_strategy.html)
- **Error & Paradigm Taxonomy:** [`docs/proof-methods.md`](docs/proof-methods.md)
- **Machine-Readable Structured Artifacts (`artifacts/`, <2 MB, CC-BY-4.0):**
  - [`artifacts/unified_15cat_panel.json`](artifacts/unified_15cat_panel.json) — **Canonical unified 15-category dataset (`<350 KB`)** synthesizing all 12,613 preprints across T0/T1/T2 (100% of `eess.*`), all 82 confirmed Lean preprints under harmonized 4-way roles, all 27 Layer-A semantic audits (`274/274` verified `file:line` refs; `0/22` engineering material drift), all **23/23** exhaustive compact (`<15k` LoC) Docker kernel builds (`18/23 = 78.3%` OOTB pass, `5,259` OOTB / `5,339` incl. synth theorems, `11/11` Gold axiom-clean), `0/250` Stage-2 negative recall calibration (95% UB `1.19%`), `8/8` operational-FV boundary audit, off-arXiv probe, and blinded human IRR; sole input to `src/generate_figures.py` and `scripts/check_paper_numbers.py`
  - [`artifacts/slices/manifest.json`](artifacts/slices/manifest.json) — Declarative registry of all matched longitudinal slices (`2025-11` T0, `2026-05` T1, `2026-11` T2) and 15-category panel metadata
  - [`artifacts/sandbox_builds/`](artifacts/sandbox_builds/README.md) (`results_2026-11.json`, `results_2026-05.json`, `results_plus7_2026-11.json`, `results_plus7_math.json`, `summary.json`) — Isolated `--network=none` Docker `lake build` + programmatic `Lean.collectAxioms` verification logs across all **23/23** standalone compact (`<15k` LoC) repositories
  - [`artifacts/off_arxiv_probe.json`](artifacts/off_arxiv_probe.json) — Zero-token off-arXiv bibliometric check (2025–2026): `0/7,849` TechRxiv + `0/2,662` engrXiv = **`0/10,511`** confirmed Lean 4 / Mathlib preprints (95% UB `0.029%`); OpenAlex `Mathlib` surges **`15.5×`** YoY (`235 → 3,632`), with Engineering (`fields/22`) at **`1.42%` (`55/3,867`)**
  - [`artifacts/track3_operational_fv_pilot.json`](artifacts/track3_operational_fv_pilot.json) — Complete **8/8** operational system-verification boundary audit (`4` cloned repos + `4` prose-only)
  - Per-stage and per-slice source logs feeding `unified_15cat_panel.json`: [`artifacts/phase_c1_15cat_longitudinal.json`](artifacts/phase_c1_15cat_longitudinal.json), [`artifacts/phase_c2_plus7_audits.json`](artifacts/phase_c2_plus7_audits.json), [`artifacts/phase2_provenance.json`](artifacts/phase2_provenance.json), [`artifacts/longitudinal_summary.json`](artifacts/longitudinal_summary.json), [`artifacts/track1_sensitivity_summary.json`](artifacts/track1_sensitivity_summary.json), [`artifacts/scout_eng_tier12_2026_11_summary.json`](artifacts/scout_eng_tier12_2026_11_summary.json), `artifacts/slices/{2025-11,2026-05,2026-11}/{classifications,plus7_classifications,layer_a_audits,plus7_layer_a_audits,recall_calibration,recall_calibration_plus7}.json`, and [`artifacts/human_annotations/`](artifacts/human_annotations/README.md)
- **Rendered Survey Reports (`reports/`):**
  - [`reports/phase_c1_15cat_longitudinal.md`](reports/phase_c1_15cat_longitudinal.md) & [`reports/phase_c2_plus7_audits.md`](reports/phase_c2_plus7_audits.md) — 15-category longitudinal panel (`12,613` preprints) and `+7` Stage-5/sandbox synthesis
  - [`reports/off_arxiv_probe.md`](reports/off_arxiv_probe.md) — Off-arXiv bibliometric triangulation across TechRxiv, engrXiv, and OpenAlex
  - [`reports/track3_operational_fv_pilot.md`](reports/track3_operational_fv_pilot.md) — Complete 8/8 operational system-verification boundary audit
  - [`reports/slices/2026-11/recall_calibration.md`](reports/slices/2026-11/recall_calibration.md) & [`reports/slices/2026-11/recall_calibration_plus7.md`](reports/slices/2026-11/recall_calibration_plus7.md) — Combined **`0/250`** Stage-2 GitHub negative recall calibration (`410` repos checked, 95% UB `1.19%`) + `0/125` non-GitHub negatives
  - [`reports/slices/2026-11/phase2_layer_a_audit.md`](reports/slices/2026-11/phase2_layer_a_audit.md), [`reports/slices/2026-11/phase2_layer_a_audit_plus7.md`](reports/slices/2026-11/phase2_layer_a_audit_plus7.md), & [`reports/slices/2026-05/phase2_layer_a_audit.md`](reports/slices/2026-05/phase2_layer_a_audit.md) — Deep Layer-A semantic fidelity audits across all **27** audited repositories (`24` in T2 + `3` in T1)
  - Per-slice Phase 0/1 & historical 8-cat reports: [`reports/longitudinal_analysis.md`](reports/longitudinal_analysis.md), [`reports/track1_sensitivity_analysis.md`](reports/track1_sensitivity_analysis.md), [`reports/scout_eng_tier12_2026_11.md`](reports/scout_eng_tier12_2026_11.md), and `reports/slices/{2025-11,2026-05,2026-11}/{phase0,phase1_survey,phase1_plus7}.md`

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
    probe_off_arxiv.py            # Zero-token off-arXiv bibliometric probe (TechRxiv/engrXiv/OpenAlex)
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

# Re-run isolated Docker lake build + #print axioms verification on compact repos (<15k LoC; n=23 total)
docker build -t lean-survey-sandbox:v1 sandbox/
uv run python sandbox/run_sandbox_audit.py                     # Initial-8 compact cohort (n=14)
uv run python sandbox/run_sandbox_audit.py --cohort plus7      # +7 engineering compact cohort (n=3)
uv run python sandbox/run_sandbox_audit.py --cohort plus7_math # +7 pure_math_or_tcs compact cohort (n=6)

# Export a clean, verified double-blind review archive to dist/blind_artifact.zip
uv run python scripts/export_blind_artifact.py
```

See [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md) for full pipeline reproduction instructions (including SQLite ingestion, artifact export, and longitudinal regeneration).
