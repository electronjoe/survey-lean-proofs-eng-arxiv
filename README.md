# survey-lean-proofs-eng-arxiv

Empirical survey of recent engineering, optimization, systems, control, information theory, signal processing, security, and robotics arXiv preprints to measure **Lean 4 proof adoption**, **Lean↔LaTeX authoring paradigms**, **Stage-2 recall**, and **Layer-A semantic fidelity** (grounded in the taxonomy of [`proof-methods.md`](proof-methods.md)).

## Key Artifacts

- **Working Pilot Paper (LaTeX v0.4):** [`src/pilot/main.tex`](src/pilot/main.tex) ([`references.bib`](src/pilot/references.bib), build with `make -C src/pilot`)
- **Progress Log & Next Steps:** [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md)
- **Domain Scope Notes (Bhaskar Krishnamachari & Scott Moeller):** [`docs/research_notes_and_todo.md`](docs/research_notes_and_todo.md)
- **Survey Reports:**
  - [`reports/longitudinal_analysis.md`](reports/longitudinal_analysis.md) — **12-month longitudinal inflection analysis** across **9,837** preprints (T0: Nov 1–19, 2025; T1: May 1–19, 2026; T2: Nov 1–19, 2026; `v1` vs `v_latest` retroactive autoformalization + flat Beyond-Lean FV control)
  - [`reports/phase2_layer_a_audit.md`](reports/phase2_layer_a_audit.md) & [`reports/slice_2026_05_phase2_audit.md`](reports/slice_2026_05_phase2_audit.md) — Deep Layer-A semantic fidelity audits (Modes #1–#4) of **20** locally inspected `engineering_math_proof` Lean 4 repos (17 in T2 + 3 in T1)
  - [`reports/phase1_survey.md`](reports/phase1_survey.md), [`reports/slice_2026_05_survey.md`](reports/slice_2026_05_survey.md), [`reports/slice_2025_11_survey.md`](reports/slice_2025_11_survey.md) — Classified inventories across all three matched slices (`0 → 5 → 39` contemporaneous `v1`; `1 → 7 → 39` latest revision)
  - [`reports/recall_calibration.md`](reports/recall_calibration.md) — Stage-2 recall calibration auditing 200 random GitHub-linked negatives (333 repos checked; **0/200** missed Lean repos, 1.49% 95% upper bound) + 100 non-GitHub negatives
  - [`reports/phase0_summary.md`](reports/phase0_summary.md) — Zero-token deterministic full-text pre-screen & static repo stats
- **Error & Paradigm Taxonomy:** [`proof-methods.md`](proof-methods.md)

## Repository Layout

```text
src/
  db.py                     # SQLite schema & idempotent upserts (survey.db, slice_2025_11.db, slice_2026_05.db)
  patterns.py               # Deterministic Lean, Beyond-Lean, LaTeX, and static .lean scanners
  ingest_arxiv.py           # Stage 1: Bias-free multi-slice arXiv OAI-PMH (arXivRaw) & Atom API ingest
  fetch_and_screen.py       # Stage 2: Polite HTML5/PDF full-text pre-screen
  profile_artifacts.py      # Stage 3: Strictly static LaTeX + GitHub/GitLab/Zenodo profiler
  calibrate_recall.py       # Referee-proofing: Stage-2 negative recall calibration via gh api
  export_workflow_inputs.py # Export candidate bundles for parallel LLM classification
  prepare_phase2_audit.py   # Extract math-preserving Markdown & prep Layer-A audit bundles
  report_phase0.py          # Phase 0 markdown summary generator
  report_phase1.py          # Import classifications & generate unified Phase 1 report
  report_phase2.py          # Import Layer-A audits & generate unified Phase 2 report
  report_longitudinal.py    # Comparative T0 / T1 / T2 longitudinal analysis & JSON summary
  generate_figures.py       # Generate vector PDF figures (incl. fig_longitudinal_curve.pdf) for pilot paper
  pilot/                    # LaTeX working paper (main.tex v0.4, references.bib, figures/, Makefile)
workflows/
  classify_candidates.py    # Stage 4: Antigravity run_workflow parallel classifier (flash)
  audit_layer_a.py          # Stage 5: Antigravity run_workflow Layer-A auditor (pro)
reports/                    # Generated Phase 0, Phase 1, Phase 2, and recall calibration reports
docs/                       # Progress log, next steps, and research scope notes
```

See [`docs/PROGRESS_AND_NEXT_STEPS.md`](docs/PROGRESS_AND_NEXT_STEPS.md) for exact `uv` commands to reproduce or extend the survey.
