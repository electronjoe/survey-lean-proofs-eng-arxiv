# Survey Progress & Next Steps

**Last updated:** 2026-11-22  
**Status:** Phase 0 (Ingest, Full-Text Pre-Screen, Static Repo Profiling), Phase 1 (Lightweight-Agent Classification), and **Phase 2 (Deep Layer-A Semantic Drift Audit on all 8 cloned `engineering_math_proof` repos + updated LaTeX Pilot Paper v0.2)** **COMPLETE**.

---

## 1. Completed Milestones

- [x] **Reference Taxonomy & Scope Grounding**
  - Archived taxonomy of 12 failure modes, 5 verification gates, and 4 Lean↔LaTeX authoring paradigms in [`proof-methods.md`](../proof-methods.md).
  - Audited USC ANRG's publication archive (`anrg.usc.edu/www/publications/`) and Bhaskar Krishnamachari's 2024–2026 arXiv footprint to define Pilot v1's 6 target categories: `cs.DC`, `cs.NI`, `cs.IT`, `eess.SY`, `cs.CR`, `cs.RO`.
  - Recorded Bhaskar's refinement notes for v2 in [`docs/research_notes_and_todo.md`](research_notes_and_todo.md).
- [x] **Phase 0: Zero-Token Deterministic Pipeline**
  - Built idempotent, SQLite-backed pipeline (`uv`-managed) in `src/`:
    - [`src/ingest_arxiv.py`](../src/ingest_arxiv.py) — arXiv API metadata ingest (`3,160` unique papers, Nov 1 – Nov 19, 2026).
    - [`src/fetch_and_screen.py`](../src/fetch_and_screen.py) — polite HTML5-first + PDF fallback full-text pre-screen (**99.84% coverage**: 2,969 HTML5, 186 PDF, 5 HTTP 404s; 98.0% corpus reduction before any LLM call; 3× recall over metadata-only).
    - [`src/profile_artifacts.py`](../src/profile_artifacts.py) — strictly static LaTeX `/src/` + authenticated `gh` GitHub repo profiler with 200 MB clone guard and comment-stripping Lean red-flag scanner.
    - [`src/report_phase0.py`](../src/report_phase0.py) — generated [`reports/phase0_summary.md`](../reports/phase0_summary.md).
- [x] **Phase 1: Parallel `run_workflow` Classification & Reporting**
  - Built [`src/export_workflow_inputs.py`](../src/export_workflow_inputs.py), [`workflows/classify_candidates.py`](../workflows/classify_candidates.py), and [`src/report_phase1.py`](../src/report_phase1.py).
  - Classified all 30 Lean candidates (`flash` read-only `research` agents inspecting local cloned repos) + 34 Beyond-Lean candidates (`flash_lite`) in <5 min with strict JSON schemas.
  - Generated [`reports/phase1_survey.md`](../reports/phase1_survey.md).
- [x] **Phase 2: Deep Layer-A Semantic Fidelity Audit (`engineering_math_proof` Cohort)**
  - Built [`src/prepare_phase2_audit.py`](../src/prepare_phase2_audit.py) (low-bandwidth math-preserving HTML5 extraction: 12.36 MB total across 8 papers), [`workflows/audit_layer_a.py`](../workflows/audit_layer_a.py) (8 parallel `pro` adversarial referee agents), and [`src/report_phase2.py`](../src/report_phase2.py).
  - Generated [`reports/phase2_layer_a_audit.md`](../reports/phase2_layer_a_audit.md) with theorem-by-theorem LaTeX↔Lean comparisons and exact `file:line` citations.
  - Folded Phases 0–2 into compiled LaTeX pilot paper v0.2: [`src/pilot/main.tex`](../src/pilot/main.tex) → [`src/pilot/main.pdf`](../src/pilot/main.pdf).

---

## 2. Pilot Headline Results (Go/No-Go = Strong GO)

| Finding | Pilot v1 Result |
| :--- | :--- |
| **Corpus screened** | 3,160 unique papers (3,155 full-text screened = 99.84%) |
| **Confirmed Lean-contributing papers** | **20** (0.63% of corpus) — already exceeding all non-Lean FV tools combined (**12**, 0.38%) |
| **Engineering Math Proof slice (Bhaskar's core focus)** | **11 / 20** (control/SysID, EV charging, coding/IT, belief propagation, RIP matrices, crypto math) |
| **Authoring Paradigms (`proof-methods.md`)** | `P1` Post-Hoc: **16 (80%)** · `P4` Spec-Lock (`comparator`): **2 (10%)** · `P0` Opaque: **2 (10%)** · `P2` Lean-First: **0** · `P3` Blueprint Sync: **0** |
| **Explicit AI/Agent Disclosure** | **16 / 20 (80%)** explicitly yes; 4 unclear; **0 explicitly human-only** |
| **Static Risk Signals** | `Mode12` Opacity: **9** · `Mode10` Proof Bloat (30k–929k LoC): **8** · `Mode2` Scope Downgrade: **7** · `Mode6` Axioms/`native_decide`: **2** |
| **Phase 2 Layer-A Audit (8 cloned `engineering_math_proof` repos)** | **0/8** definition smuggling (`Mode #3`); **7/8** clean on junk/vacuity (`Mode #4`); **8/8** have computational/algorithmic scope boundaries (`Mode #2`: 7 minor disclosed, 1 moderate); **5/8** lack explicit non-vacuity witnesses; **1** subtle undisclosed spec gap caught inside a `P4` comparator interface (`2611.04876`) |

---

## 3. Prioritized Next Steps

### High Priority (Remote Server Recommended for Downloads)
1. **Pilot v2 Scope Expansion (per Bhaskar's feedback in [`research_notes_and_todo.md`](research_notes_and_todo.md)):**
   - Add **`eess.SP`** (Signal Processing) and **`math.OC`** (Optimization & Control) over the same 3-week window (~300–600 MB download), and run Phase 2 Layer-A audits on any newly found `engineering_math_proof` Lean repos.
   - Filter out primary pure-TCS categories (`cs.CC`, `cs.DS`, `cs.LO`, `cs.DM`, `cs.FL`) even when cross-listed, and drop Beyond-Lean LLM classification in future passes so all budget goes to Lean engineering-math proofs.
2. **Recall Calibration & Non-GitHub Artifact Completeness (Referee-Proofing):**
   - Sample 50–100 random Stage-2 negatives (especially ones with GitHub links) and check via lightweight `gh api` tree queries (<2 MB!) whether any linked repo contains `lean-toolchain`/`*.lean` without naming Lean in the prose.
   - Extend `src/profile_artifacts.py` to statically inspect GitLab repos (`2611.22732`) and Zenodo archives (`2611.15201`, `2611.10810`).

### Medium Priority (Remote Server)
3. **Scoped Machine Learning Theory Arm (`cs.LG` / `stat.ML`):**
   - Run a 1-week window or stratified 1,000-paper sample of `cs.LG`/`stat.ML` (~1–3 GB download) as a dedicated ML-theory comparison arm.
4. **Historical Baseline Slices & Standalone Periodic Runner (`agy -p`):**
   - Run the exact same categories on 3-week slices from **Nov 2025** and **May 2026** to quantify the 2026 AI-Lean adoption curve.
   - Wrap the classifier prompt + JSON schema in a standalone `src/classify_cli.py` calling `agy -p --model gemini-3.8-flash-low --output-format json --json-schema ...` for unattended quarterly snapshots.

### Stretch / Optional (Remote Server with Docker)
5. **Sandboxed Lean Kernel Verification (`lake build` + `#print axioms`):**
   - For the compact engineering-math repos (<5k LoC: `Lean-SysID`, `bic-public`, `CoprimeFrobenius`, `trustbound`, `ExactShortestPathsAndFlowsOnPlanarGraphs`), run `lake build` + `#print axioms` inside an isolated Docker container (~5–15 GB Mathlib `.olean` cache) to verify out-of-the-box reproducibility.

---

## 4. Reproducing / Re-Running the Pipeline

```bash
uv sync

# 1. Ingest arXiv metadata for a date window
uv run python -m src.ingest_arxiv --since 2026-11-01 --until 2026-11-22

# 2. Polite full-text HTML5/PDF fetch + deterministic pre-screen
uv run python -m src.fetch_and_screen --workers 6 --min-interval 0.25
uv run python -m src.fetch_and_screen --retry-failed --workers 6 --min-interval 0.25

# 3. Strictly static LaTeX + GitHub repo profiler (requires `gh auth login`)
uv run python -m src.profile_artifacts

# 4. Generate Phase 0 report & export candidates for LLM classification
uv run python -m src.report_phase0
uv run python -m src.export_workflow_inputs

# 5. After running workflows/classify_candidates.py -> data/workflow_outputs.json:
uv run python -m src.report_phase1

# 6. Phase 2 Layer-A semantic drift audit on cloned engineering_math_proof repos:
uv run python -m src.prepare_phase2_audit
# After running workflows/audit_layer_a.py -> data/phase2_outputs.json:
uv run python -m src.report_phase2

# 7. Build the pilot LaTeX paper
make -C src/pilot
```
