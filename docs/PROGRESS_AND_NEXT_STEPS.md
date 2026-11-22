# Survey Progress & Next Steps

**Last updated:** 2026-11-22  
**Status:** Phase 0 (Ingest, Full-Text Pre-Screen, Static Repo Profiling) & Phase 1 (Lightweight-Agent Classification + Pilot LaTeX Report) **COMPLETE**.

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
  - Generated [`reports/phase1_survey.md`](../reports/phase1_survey.md) and working LaTeX pilot paper [`src/pilot/main.tex`](../src/pilot/main.tex) + [`src/pilot/references.bib`](../src/pilot/references.bib).

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

---

## 3. Prioritized Next Steps

### High Priority (Immediate)
1. **Pilot v2 Scope Expansion (per Bhaskar's feedback in [`research_notes_and_todo.md`](research_notes_and_todo.md)):**
   - Add **`eess.SP`** (Signal Processing) and **`math.OC`** (Optimization & Control) to the 3-week window (and consider a scoped/stratified slice of **`cs.LG` / `stat.ML`** theoretical ML papers).
   - Filter out primary pure-TCS categories (`cs.CC`, `cs.DS`, `cs.LO`, `cs.DM`, `cs.FL`) even when cross-listed, and drop Beyond-Lean LLM classification in future passes so all budget goes to Lean engineering-math proofs.
2. **Phase 2: Deep Layer-A Semantic Drift Audit (`proof-methods.md` Modes #1–#4):**
   - Run a stronger-model (`pro`/`inherit`) `run_workflow` pass over the **~9–11 `engineering_math_proof` papers with cloned Lean repos** (`2611.18220`, `2611.10902`, `2611.11713`, `2611.08172`, `2611.14475`, `2611.04876`, `2611.05136`, `2611.23762`).
   - Pair extracted LaTeX `\begin{theorem}` blocks against their corresponding Lean declarations + custom `def`/`structure` stacks to detect:
     - **Mode #1:** Silent hypothesis strengthening / conclusion weakening (Type i vs. Type ii drift)
     - **Mode #2:** Unstated scope downgrading between abstract/headline and Lean endpoints
     - **Mode #3:** Definition smuggling / weak Mathlib anchoring
     - **Mode #4:** Vacuous hypotheses & Lean junk-value traps (`1/0 = 0`, `Nat` subtraction saturation)

### Medium Priority (Before Academic Submission)
3. **Recall Calibration (Negative Spot-Check):**
   - Sample 50 random Stage-2 negatives (especially papers containing a GitHub link) and run `flash_lite` + GitHub tree check for `lean-toolchain` to bound false-negative rate empirically.
4. **Non-GitHub Artifact Support:**
   - Extend `src/profile_artifacts.py` to statically inspect GitLab repos (e.g., `2611.22732` on MPI-SWS GitLab) and Zenodo archives (e.g., `2611.15201`, `2611.10810`).
5. **Standalone Periodic Re-Run Runner (`agy -p`):**
   - Wrap `workflows/classify_candidates.py`'s prompt + JSON schema in a standalone `src/classify_cli.py` calling `agy -p --model gemini-3.8-flash-low --output-format json --json-schema ...` so monthly/quarterly snapshots can run unattended outside an interactive chat.

### Stretch / Optional
6. **Sandboxed Lean Kernel Verification:**
   - For the compact engineering-math repos (<5k LoC: `Lean-SysID`, `bic-public`, `CoprimeFrobenius`, `trustbound`), run `lake build` + `#print axioms` inside an isolated Docker container (no network, read-only mount) to obtain ground-truth kernel certification.

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

# 6. Build the pilot LaTeX paper
make -C src/pilot
```
