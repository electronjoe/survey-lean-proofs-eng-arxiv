# survey-lean-proofs-eng-arxiv

Empirical survey of recent engineering, systems, control, information theory, security, and robotics arXiv preprints to measure **Lean 4 proof adoption**, **Lean↔LaTeX authoring paradigms**, and **verification hygiene** (grounded in the taxonomy of [`proof-methods.md`](proof-methods.md)).

## Key Artifacts

- **Working Pilot Paper (LaTeX):** [`src/pilot/main.tex`](src/pilot/main.tex) ([`references.bib`](src/pilot/references.bib), build with `make -C src/pilot`)
- **Progress Log & Next Steps:** [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md)
- **Domain Scope Notes (Bhaskar Krishnamachari & Scott Moeller):** [`docs/research_notes_and_todo.md`](docs/research_notes_and_todo.md)
- **Survey Reports:**
  - [`reports/phase2_layer_a_audit.md`](reports/phase2_layer_a_audit.md) — Deep Layer-A semantic fidelity audit (Modes #1–#4) of all 8 cloned `engineering_math_proof` Lean 4 repos
  - [`reports/phase1_survey.md`](reports/phase1_survey.md) — Classified inventory of 20 confirmed Lean papers + 12 Beyond-Lean baseline papers (Nov 1–19, 2026; 3,160 papers screened)
  - [`reports/phase0_summary.md`](reports/phase0_summary.md) — Zero-token deterministic full-text pre-screen & static repo stats
- **Error & Paradigm Taxonomy:** [`proof-methods.md`](proof-methods.md)

## Repository Layout

```text
src/
  db.py                     # SQLite schema & idempotent upserts (data/survey.db)
  patterns.py               # Deterministic Lean, Beyond-Lean, LaTeX, and static .lean scanners
  ingest_arxiv.py           # Stage 1: arXiv Atom API metadata ingest
  fetch_and_screen.py       # Stage 2: Polite HTML5/PDF full-text pre-screen
  profile_artifacts.py      # Stage 3: Strictly static LaTeX + GitHub repo profiler
  export_workflow_inputs.py # Export candidate bundles for parallel LLM classification
  report_phase0.py          # Phase 0 markdown summary generator
  report_phase1.py          # Import classifications & generate Phase 1 report
  pilot/                    # LaTeX working paper (main.tex, references.bib, Makefile)
workflows/
  classify_candidates.py    # Stage 4: Antigravity run_workflow parallel classifier
reports/                    # Generated Phase 0 & Phase 1 markdown reports
docs/                       # Progress log, next steps, and research scope notes
```

See [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md) for exact `uv` commands to reproduce or extend the survey.
