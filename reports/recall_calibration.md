# Stage-2 Recall Calibration Report

- **Random seed:** `20261122`
- **Total Stage-2 negatives (full-text screened):** 4042
- **Stage-2 negatives with non-boilerplate GitHub links:** 1390 (34.4%)
- **GitHub-linked negative sample audited:** **200** papers (333 unique GitHub repos queried via `gh api` recursive trees; **195** papers had ≥1 accessible public repo)
- **Missed Lean repositories found in GitHub-linked negative sample:** **0 / 200** (0.00%)
- **95% Clopper–Pearson upper bound on hidden-Lean rate among GitHub-linked negatives:** **1.49%** (or **1.52%** conditioning on accessible repos)
- **Non-GitHub negative sample checked for broad metadata/comment keywords:** **100** papers (0 broad keyword matches for manual review)

## Result

Zero missed Lean repositories (`*.lean`, `lean-toolchain`, or `lakefile.*`) were detected across the entire audited GitHub-linked Stage-2 negative sample.
