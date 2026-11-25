# Stage-2 Recall Calibration Report

- **Random seed:** `20261125`
- **Total Stage-2 negatives (full-text screened):** 1162
- **Stage-2 negatives with non-boilerplate GitHub links:** 332 (28.6%)
- **GitHub-linked negative sample audited:** **50** papers (77 unique GitHub repos queried via `gh api` recursive trees; **48** papers had ≥1 accessible public repo)
- **Missed Lean repositories found in GitHub-linked negative sample:** **1 / 50** (2.00%)
- **95% Clopper–Pearson upper bound on hidden-Lean rate among GitHub-linked negatives:** **9.14%** (or **9.51%** conditioning on accessible repos)
- **Non-GitHub negative sample checked for broad metadata/comment keywords:** **25** papers (0 broad keyword matches for manual review)

## Missed Lean Repos Discovered in GitHub-Linked Negatives

- **[2611.08673](https://arxiv.org/abs/2611.08673)** (`cs.DS`) Optimal Contention Resolution from Samples — repos: `[('openai/math', 53549, ['lean/ComparatorChallenges/AbhyankarSathaye.lean', 'lean/ComparatorChallenges/AffineBernstein.lean', 'lean/ComparatorChallenges/AlgorithmicThinTrees.lean', 'lean/ComparatorChallenges/AmplitudeDamping.lean', 'lean/ComparatorChallenges/ArithmeticHierarchy.lean'])]`
  - **Manual Adjudication (`citation_only_not_lean_contribution`):** The sole GitHub URL in `2611.08673v1` is bibliographic citation `[28]` pointing to a PDF preprint inside `openai/math` (`preprints/One-Sample-Suffices-for-Matroid-Prophet-Inequalities-against-an-Almighty-Adversary-September-23-2026/final.pdf`). The paper contributes zero Lean code (its only occurrence of `"lean"` is *"We lean on a CRS of Feige and Vondrák"*).
  - **Confirmed missed Lean contributions:** **0 / 50** in the additional 7-category sample (**0 / 250** combined across all 15 categories; 410 unique GitHub repos queried; exact one-sided 95% Clopper–Pearson upper bound **1.19%**, or **1.23%** conditioning on 243 papers with accessible repos).
