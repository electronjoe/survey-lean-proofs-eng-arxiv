# Survey Progress & Next Steps

**Last updated:** 2026-11-22  
**Status:** **Pilot v2 Scope Expansion + Referee-Proofing COMPLETE** (`eess.SP` + `math.OC` added → 4,104 papers; GitLab/Zenodo/`leanVM` artifact profiling; 200-paper Stage-2 recall calibration; 39 confirmed Lean papers; 17-paper Phase 2 Layer-A adversarial audit; compiled LaTeX Pilot Paper v0.3).

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

---

## 2. Pilot v2 Headline Results

| Finding | Pilot v2 Result (8 Categories) |
| :--- | :--- |
| **Corpus screened** | **4,104** unique papers (**4,097** full-text screened = **99.83%**; **4,060** non-TCS primary) |
| **Stage-2 recall calibration** | **0 / 200** GitHub-linked negatives (333 repos checked; **1.49%** 95% Clopper–Pearson upper bound); **0 / 100** non-GitHub broad metadata hits |
| **Confirmed Lean-contributing papers** | **39** (**0.95%** overall; **36 / 4,060 = 0.89%** non-TCS primary) |
| **Engineering Math Proof slice (Bhaskar's lens)** | **28 / 39 (71.8%)** — led by **`math.OC` (19/724 = 2.62%, 17 eng-math)**, `cs.IT` (6/338 = 1.78%), `cs.DC` (6/335 = 1.79%), `cs.CR` (7/629 = 1.11%), `eess.SY` (3/738 = 0.41%) |
| **Zero-adoption engineering categories** | **`eess.SP` (0/462)**, **`cs.NI` (0/196)**, **`cs.RO` (0/1,159)** — 0 / 1,817 papers |
| **Authoring Paradigms (`proof-methods.md`)** | `P1` Post-Hoc: **28 (71.8%)** · `P0` Opaque: **8 (20.5%)** · `P4` Spec-Lock (`comparator`): **3 (7.7%)** · `P2` Lean-First: **0** · `P3` Blueprint Sync: **0** |
| **Explicit AI/Agent Disclosure** | **30 / 39 (76.9%)** explicitly yes · 9 unclear · **0 explicitly human-only** |
| **Static Hygiene & Scale** | **4.17M LoC** across 24 unique scanned primary repos; `Tier3_Gold`: **19**, `Tier2_Silver`: **7**, `Tier1_Bronze`: **13**; `Mode12` Opacity: **17**, `Mode10` Bloat: **12**, `Mode2` Scope: **10**, `Mode6` Axiom/Sorry: **3** |
| **Phase 2 Layer-A Audit (`n = 17` `engineering_math_proof` repos)** | **16/16 independent author-owned repos** have **0** moderate/severe Mode #1 drift & **0** undisclosed Mode #3 smuggling (6 `high_faithful`, 8 `mostly_faithful_with_disclosed_gaps`, 2 `partial`); **sole `material_undisclosed_drift_or_risk` hit** is bulk automated pipeline **`2611.26272` (*Paper2Lean* / `OptPaper-20`)**! Non-vacuity witnesses: **10 / 17 (58.8%)**. |

---

## 3. Prioritized Remaining Next Steps

1. **Longitudinal Baseline Slices (Nov 2025 & May 2026):**
   - Run the exact same 8-category OAI-PMH pipeline on 3-week slices from **Nov 2025** and **May 2026** to quantify the 2026 AI-Lean adoption inflection curve (into separate DBs or date-sliced queries).
2. **Sandboxed Lean Kernel Verification in Docker (`lake build` + `#print axioms`):**
   - Execute isolated clean-room builds on compact engineering repos (`<5k` LoC: `Lean-SysID`, `bic-public`, `CoprimeFrobenius`, `discrete-modified-gradient-lean`, `trustbound`, `ExactShortestPathsAndFlowsOnPlanarGraphs`, `zenodo/24127514`) to measure out-of-the-box reproducibility.
3. **Scoped Machine Learning Theory Arm (`cs.LG` / `stat.ML`):**
   - Run a 1-week window or stratified 1,000-paper sample of `cs.LG`/`stat.ML` to benchmark ML theory against `math.OC` and `cs.IT`.
4. **Standalone Periodic Runner (`agy -p`):**
   - Wrap the classifier prompt + JSON schema in `src/classify_cli.py` for unattended quarterly snapshots.

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
