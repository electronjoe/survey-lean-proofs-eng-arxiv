# Repository Reorganization Plan: Clean Multi-Variant Target Layout

**Date:** November 22, 2026  
**Repository:** `survey-lean-proofs-eng-arxiv`  
**Goal:** Transition from the initial single-pilot layout to a clean, reproducible, multi-variant research repository supporting multiple paper targets (`arxiv-empirical`, `magazine-cacm`, `itp-2027`, `neurips-db-2027`), quarterly longitudinal slices (`2025-11`, `2026-05`, `2026-11`, `2026-11-ml`, `2027-02`), version-controlled structured artifacts & human IRR annotations, isolated Docker verification, and double-blind artifact export.

---

## 1. Target Directory Layout

```text
survey-lean-proofs-eng-arxiv/
  README.md
  LICENSE                         # MIT (code) + CC-BY-4.0 (curated metadata/annotations)
  CITATION.cff                    # Standard citation metadata for Zenodo / GitHub
  pyproject.toml / uv.lock
  .gitignore                      # Ignores data/ cache, papers/**/*.pdf, & LaTeX build artifacts
  .github/
    workflows/
      build-papers.yml            # Regenerates figures from artifacts/, compiles all papers/*/main.tex,
                                  # uploads GH Actions PDF artifacts + rolling `papers-latest` Release
      ci.yml                      # Runs pytest + link/hygiene checks on every push & PR
  src/                            # Strictly static/deterministic Python pipeline & figures
  workflows/                      # LLM agent workflows (prompts + strict JSON schemas)
  sandbox/                        # Isolated Docker execution boundary (lake build / #print axioms)
    README.md                     # Security boundary spec + future Dockerfile scaffold
  scripts/
    export_blind_artifact.py      # Builds clean double-blind Zenodo/review zip (strips docs/ & papers/)
  tests/
    test_patterns.py              # Unit tests for regex detectors, Lean lexer, OAI date filters
  artifacts/                      # Git-tracked small structured outputs (<2 MB, license-safe)
    longitudinal_summary.json
    slices/
      manifest.json               # Declarative registry of all slices (dates, categories, status)
      2025-11/
        classifications.json
      2026-05/
        classifications.json
        layer_a_audits.json
      2026-11/
        classifications.json
        layer_a_audits.json
        recall_calibration.json
        figure_inputs.json        # Compact stats enabling zero-DB figure generation in CI
    human_annotations/
      README.md                   # Schema & workflow for IRR labels + human-verified SHA pins
    sandbox_builds/
      README.md                   # Schema for Docker lake build & #print axioms results
  reports/                        # Rendered Markdown reports
    longitudinal_analysis.md
    slices/
      2025-11/
        phase0.md
        phase1_survey.md
      2026-05/
        phase0.md
        phase1_survey.md
        phase2_layer_a_audit.md
      2026-11/
        phase0.md
        phase1_survey.md
        phase2_layer_a_audit.md
        recall_calibration.md
  papers/                         # ZERO PDFs committed to Git — built locally or via GitHub Actions!
    shared/                       # Single source of truth across all paper variants
      references.bib
      figures/                    # Generated on demand by `src/generate_figures.py` (gitignored *.pdf)
        .gitkeep
    arxiv-empirical/              # Moved from src/pilot/
      main.tex                    # Compiled main.pdf is gitignored & published as GH Actions artifact
      Makefile
  docs/
    proof-methods.md              # Moved from repo root
    PROGRESS_AND_NEXT_STEPS.md
    research_notes_and_todo.md
    publication_strategy.html
    reorg_plan.md
  data/                           # Gitignored heavy/ephemeral cache (NEVER committed)
    survey.db                     # Existing SQLite DBs untouched in place
    slice_2025_11.db
    slice_2026_05.db
    repos/                        # ~3.6 GB cloned third-party Lean repos
    phase2_papers/
    fig_previews/
```

---

## 2. Exact File Migration Map

| Current Path | New Path | Action | Notes |
| :--- | :--- | :--- | :--- |
| `src/pilot/main.tex` | `papers/arxiv-empirical/main.tex` | `git mv` | Update `\includegraphics` and `\bibliography` to `../shared/` |
| `src/pilot/main.pdf` | *(removed from Git; built in CI)* | `git rm` | Built locally via `make` & automatically via GitHub Actions artifact + `papers-latest` release |
| `src/pilot/Makefile` | `papers/arxiv-empirical/Makefile` | `git mv` + edit | Reference `../shared/references.bib` and build figures if missing |
| `src/pilot/references.bib` | `papers/shared/references.bib` | `git mv` | Single shared BibTeX for all paper variants |
| `src/pilot/figures/*.pdf` | *(removed from Git; regenerated into `papers/shared/figures/`)* | `git rm` | Regenerated deterministically from `artifacts/` in <5s locally & in GitHub Actions (0 PDFs in Git!) |
| `proof-methods.md` | `docs/proof-methods.md` | `git mv` | Consolidate internal taxonomy notes under `docs/` |
| `reports/slice_2025_11_phase0.md` | `reports/slices/2025-11/phase0.md` | `git mv` | Uniform per-slice report layout |
| `reports/slice_2025_11_survey.md` | `reports/slices/2025-11/phase1_survey.md` | `git mv` | Uniform per-slice report layout |
| `reports/slice_2026_05_phase0.md` | `reports/slices/2026-05/phase0.md` | `git mv` | Uniform per-slice report layout |
| `reports/slice_2026_05_survey.md` | `reports/slices/2026-05/phase1_survey.md` | `git mv` | Uniform per-slice report layout |
| `reports/slice_2026_05_phase2_audit.md` | `reports/slices/2026-05/phase2_layer_a_audit.md` | `git mv` | Uniform per-slice report layout |
| `reports/phase0_summary.md` | `reports/slices/2026-11/phase0.md` | `git mv` | Uniform per-slice report layout |
| `reports/phase1_survey.md` | `reports/slices/2026-11/phase1_survey.md` | `git mv` | Uniform per-slice report layout |
| `reports/phase2_layer_a_audit.md` | `reports/slices/2026-11/phase2_layer_a_audit.md` | `git mv` | Uniform per-slice report layout |
| `reports/recall_calibration.md` | `reports/slices/2026-11/recall_calibration.md` | `git mv` | Uniform per-slice report layout |
| `reports/longitudinal_analysis.md` | `reports/longitudinal_analysis.md` | keep | Cross-slice synthesis stays at `reports/` root |
| `data/longitudinal_summary.json` | `artifacts/longitudinal_summary.json` | copy + track | Promote small (~104 KB) machine-readable summary to Git |
| `data/wf_out_2025_11.json` | `artifacts/slices/2025-11/classifications.json` | copy + track | Promote T0 classifications (3.3 KB) |
| `data/wf_out_2026_05.json` | `artifacts/slices/2026-05/classifications.json` | copy + track | Promote T1 classifications (21 KB) |
| `data/phase2_out_2026_05.json` | `artifacts/slices/2026-05/layer_a_audits.json` | copy + track | Promote T1 Layer-A audits (61 KB) |
| `data/workflow_outputs.json` + `workflow_outputs_v2.json` | `artifacts/slices/2026-11/classifications.json` | export from `data/survey.db` (or merge) + track | Export canonical deduplicated T2 classifications from SQLite so v1+v2 are unified cleanly |
| `data/phase2_outputs.json` + `phase2_outputs_v2.json` | `artifacts/slices/2026-11/layer_a_audits.json` | export from `data/survey.db` (or merge) + track | Export canonical deduplicated 17 T2 Layer-A audits from SQLite |
| `data/recall_calibration.json` | `artifacts/slices/2026-11/recall_calibration.json` | copy + track | Promote recall calibration log (175 KB) |
| `data/*.db`, `data/repos/`, `data/phase2_papers/` | *(unchanged, gitignored)* | keep untouched | Never move/delete heavy SQLite DBs or 3.6 GB cloned repos |

---

## 3. Step-by-Step Execution Phases

### Phase 1 — Move LaTeX Paper to `papers/`, Remove Binary PDFs from Git & Create `papers/shared/`
1. Create `papers/shared/figures/.gitkeep` and `papers/arxiv-empirical/`.
2. Use `git mv` / `git rm`:
   - `git mv src/pilot/references.bib papers/shared/references.bib`
   - `git mv src/pilot/main.tex papers/arxiv-empirical/main.tex`
   - `git mv src/pilot/Makefile papers/arxiv-empirical/Makefile`
   - `git rm src/pilot/main.pdf src/pilot/figures/*.pdf` (eliminating all binary PDFs from Git!)
   - Delete stale untracked build files in `src/pilot/` (`*.aux`, `*.bbl`, `*.blg`, `*.fls`, `*.fdb_latexmk`, `*.log`, `*.out`) and remove empty `src/pilot/`.
3. Update `papers/arxiv-empirical/main.tex`:
   - Add `\graphicspath{{../shared/figures/}}` (and keep `\includegraphics{fig_*.pdf}` or `../shared/figures/fig_*.pdf`).
   - Change `\bibliography{references}` → `\bibliography{../shared/references}`.
   - Update internal report path mentions (`reports/recall_calibration.md` → `reports/slices/2026-11/recall_calibration.md`, `reports/phase2_layer_a_audit.md` → `reports/slices/2026-11/phase2_layer_a_audit.md`, `reports/slice_2026_05_phase2_audit.md` → `reports/slices/2026-05/phase2_layer_a_audit.md`).
4. Update `papers/arxiv-empirical/Makefile` so `main.pdf` depends on `main.tex ../shared/references.bib` (and provide a `figures` target invoking `uv run python -m src.generate_figures` from repo root if `../shared/figures/fig_pipeline_funnel.pdf` is missing).
5. Update `.gitignore`: replace `src/pilot/*.aux` ... `src/pilot/*.synctex.gz` with generalized `papers/**/*.pdf`, `papers/**/*.aux`, `papers/**/*.bbl`, `papers/**/*.blg`, `papers/**/*.fdb_latexmk`, `papers/**/*.fls`, `papers/**/*.log`, `papers/**/*.out`, `papers/**/*.synctex.gz`, plus `dist/`.

### Phase 2 — Promote Structured Outputs into Git-Tracked `artifacts/` (Enabling Zero-DB CI Figure Builds)
1. Create:
   - `artifacts/slices/2025-11/`, `artifacts/slices/2026-05/`, `artifacts/slices/2026-11/`
   - `artifacts/human_annotations/README.md` (documenting planned IRR CSV/JSON schema and commit-SHA verification records)
   - `artifacts/sandbox_builds/README.md` (documenting planned Docker `lake build` + `#print axioms` output schema)
2. Copy `data/longitudinal_summary.json` → `artifacts/longitudinal_summary.json`, `data/recall_calibration.json` → `artifacts/slices/2026-11/recall_calibration.json`, and T0/T1 JSON outputs into their slice folders.
3. Write `src/export_artifacts.py` (~140 lines) to export canonical, deduplicated, license-safe JSON files from each slice SQLite DB into `artifacts/slices/<slice_id>/`:
   - `classifications.json`, `layer_a_audits.json`, and `figure_inputs.json` (containing the exact aggregate counts, per-category counts, 39 confirmed Lean paper records with LoC/paradigm/tier, and 17 Layer-A audit rows needed by `src/generate_figures.py`—zero copyrighted full text, zero third-party code, <150 KB!).
4. Create `artifacts/slices/manifest.json` declaring `2025-11` (`T0`), `2026-05` (`T1`), and `2026-11` (`T2`) with exact `slice_id`, `label`, `start_date`, `end_date`, `categories`, `db_path`, `artifacts_dir`, and `reports_dir`.

### Phase 3 — Normalize `reports/` and `docs/`
1. `git mv proof-methods.md docs/proof-methods.md`.
2. `git mv` the 9 per-slice Markdown reports into `reports/slices/{2025-11,2026-05,2026-11}/` per the migration map above (leaving `reports/longitudinal_analysis.md` at `reports/` root).

### Phase 4 — Update Pipeline Scripts (`src/*.py`) to Use New Defaults & Zero-DB Figure Generation
Keep existing CLI flags backwards-compatible while updating defaults to the clean layout:
1. `src/generate_figures.py`:
   - `FIG_DIR = Path("papers/shared/figures")`
   - Read from git-tracked `artifacts/slices/2026-11/figure_inputs.json` + `artifacts/longitudinal_summary.json` **by default** (no `data/survey.db` required!), while preserving an optional `--from-db data/survey.db` mode for local DB inspection. This guarantees GitHub Actions (and any fresh `git clone`) can regenerate all 5 vector PDFs identically in seconds.
2. `src/report_longitudinal.py`:
   - Change `--json-out` default from `data/longitudinal_summary.json` → `artifacts/longitudinal_summary.json`.
   - Keep `--t0-db`, `--t1-db`, `--t2-db` defaults pointing to `data/slice_2025_11.db`, `data/slice_2026_05.db`, `data/survey.db` (since DBs stay untouched in `data/`), and optionally add `--manifest artifacts/slices/manifest.json` support.
3. `src/calibrate_recall.py`:
   - Change `out_json` default → `artifacts/slices/2026-11/recall_calibration.json` and `out_md` default → `reports/slices/2026-11/recall_calibration.md`.
4. `src/report_phase0.py`, `src/report_phase1.py`, `src/report_phase2.py`:
   - Update default report paths to `reports/slices/2026-11/{phase0.md,phase1_survey.md,phase2_layer_a_audit.md}` while preserving `--out`/`--report` CLI overrides.

### Phase 5 — Add GitHub Actions Paper-Build & CI Workflows + Open-Science Scaffolding
1. **`.github/workflows/build-papers.yml`** (Zero-Bloat Automated PDF Building & Artifact Storage):
   - Triggers on push/PR touching `papers/**`, `artifacts/**`, `src/generate_figures.py`, or `.github/workflows/build-papers.yml`, plus manual `workflow_dispatch`.
   - Step 1: Sets up Python + `uv` (`astral-sh/setup-uv@v5`) and runs `uv run python -m src.generate_figures` to generate all vector PDFs into `papers/shared/figures/` directly from git-tracked `artifacts/`.
   - Step 2: Dynamically discovers every paper variant `papers/*/main.tex` (excluding `papers/shared/`) and compiles each via `latexmk -pdf -interaction=nonstopmode main.tex` (using `xu-cheng/latex-action@v3` or TeX Live). Copies each built PDF to `dist/papers/<variant-name>.pdf` (e.g., `dist/papers/arxiv-empirical.pdf`).
   - Step 3: Uploads `dist/papers/*.pdf` and `papers/shared/figures/*.pdf` as **GitHub Actions Artifacts** (`actions/upload-artifact@v4`, 90-day retention) on every push and PR.
   - Step 4 (on pushes to `main` only, `permissions: contents: write`): Publishes/updates a rolling **`papers-latest` GitHub Release** (via `softprops/action-gh-release@v2` with `tag_name: papers-latest`, `prerelease: true`, overwriting assets on each push to `main`) so co-authors have a permanent, login-free 1-click PDF URL (`https://github.com/electronjoe/survey-lean-proofs-eng-arxiv/releases/download/papers-latest/arxiv-empirical.pdf`).
2. **`.github/workflows/ci.yml`:**
   - Runs `uv sync --dev`, `uv run pytest`, and automated link/anonymity verification on every push/PR.
3. **`LICENSE`:** Dual-friendly MIT License for code + explicit CC-BY-4.0 notice for curated datasets/annotations in `artifacts/`.
4. **`CITATION.cff`:** Standard GitHub/Zenodo citation metadata for Scott Moeller & Bhaskar Krishnamachari (2026).
5. **`sandbox/README.md`:** Document the strict isolation contract separating static `src/` from future Docker-based `lake build` + `#print axioms` verification (`--network=none`, read-only repo mounts, CPU/RAM/timeout caps).
6. **`scripts/export_blind_artifact.py`:** One-command script generating a clean, anonymized review zip (e.g. `dist/blind_artifact.zip`, gitignored) containing `src/`, `workflows/`, `artifacts/`, `sandbox/`, `tests/`, `pyproject.toml`, `uv.lock`, `LICENSE`, and an anonymized `README.md`—automatically excluding `docs/`, `papers/`, `data/`, and any author-identifying strings.
7. **`tests/test_patterns.py`:** Focused unit tests (`pytest` added under `[dependency-groups] dev` in `pyproject.toml`) testing `src/patterns.py`:
   - Strong vs. contextual Lean regex matching (including negative cases like `"lean manufacturing"`, `"lean startup"`)
   - Beyond-Lean formal-methods detectors
   - Comment-stripping Lean lexer (`--` line comments, `/- ... -/` nested block comments, ignoring `sorry`/`axiom` inside comments and strings)
   - LaTeX blueprint macro and AI-disclosure detection.

### Phase 6 — Update All Documentation & Cross-Links
Update every path reference and GitHub link in:
1. `README.md` (new layout tree, updated key-artifact links, direct `papers-latest` Release & GitHub Actions PDF links, `make -C papers/arxiv-empirical`, `uv run pytest`, `scripts/export_blind_artifact.py`).
2. `docs/PROGRESS_AND_NEXT_STEPS.md` (updated relative links & reproducible commands).
3. `docs/publication_strategy.html` (update all GitHub `blob/main/...` links to `papers/arxiv-empirical/main.tex`, `papers/shared/references.bib`, `docs/proof-methods.md`, `reports/slices/...`, and `artifacts/...`; point PDF download links to the `papers-latest` GitHub Release / Actions artifacts; re-run automated link validator!).

---

## 4. Verification & Acceptance Criteria

Before committing and pushing, ALL of the following checks must pass:
1. **Unit tests pass:** `uv run pytest` exits `0` with all tests passing.
2. **Artifacts & figures regenerate cleanly:**
   - `uv run python -m src.export_artifacts --all` populates `artifacts/slices/{2025-11,2026-05,2026-11}/` cleanly.
   - `uv run python -m src.report_longitudinal` updates `artifacts/longitudinal_summary.json` and `reports/longitudinal_analysis.md` with identical headline numbers (`9,837` preprints, `0 → 5 → 39` contemporaneous `v1`, `1 → 7 → 39` `v_latest`).
   - `uv run python -m src.generate_figures` regenerates all 5 vector PDFs in `papers/shared/figures/` cleanly.
3. **LaTeX compiles cleanly:** `make -C papers/arxiv-empirical` exits `0`, produces `papers/arxiv-empirical/main.pdf` with **0 LaTeX warnings, 0 errors, and 0 overfull hboxes**, and resolves all citations (`../shared/references.bib`) and all 5 figures (`../shared/figures/`).
4. **Blind artifact export works:** `uv run python scripts/export_blind_artifact.py --out /tmp/test_blind_artifact.zip` succeeds and contains zero occurrences of author/institution identifiers (`Moeller`, `Krishnamachari`, `ANRG`, `USC`, `electronjoe`).
5. **Link integrity verified:** Automated check confirms every relative Markdown link in `README.md` / `docs/PROGRESS_AND_NEXT_STEPS.md` and every GitHub `blob/main/...` link in `docs/publication_strategy.html` points to an existing git-tracked file.
6. **Git safety & zero-PDF check:** `git status` and `git ls-files '*.pdf'` confirm **zero `.pdf` files tracked in Git**, zero files under `data/` (no SQLite DBs, no `data/repos/` third-party code), and zero LaTeX aux/log artifacts staged; total added `artifacts/` size is `< 2 MB`.
7. **GitHub Actions workflow check:** Validate `.github/workflows/build-papers.yml` and `.github/workflows/ci.yml` YAML syntax (`python -c "import yaml..."` or `gh workflow list` after push) and verify the `build-papers` workflow succeeds on GitHub Actions after pushing to `main`, publishing `arxiv-empirical.pdf` as both a workflow artifact and an asset on the `papers-latest` release.

---

## 5. Safety & Rollback Guarantees
- `data/*.db`, `data/repos/`, and `data/phase2_papers/` are **never moved, modified, or deleted** during this migration.
- All tracked file relocations use `git mv` so full Git history and blame remain intact.
- Because the migration is committed as a single clean commit (or two logical commits: layout move + new tooling/tests), reverting is a single `git revert` if ever needed.
