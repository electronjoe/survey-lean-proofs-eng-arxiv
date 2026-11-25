# Human Verification & IRR Plan (Steps 2–4 Open Efforts Tracker)

**Last updated:** 2026-11-24  
**Parent trackers:** [`docs/audit_plan.md`](audit_plan.md) · [`docs/PROGRESS_AND_NEXT_STEPS.md`](PROGRESS_AND_NEXT_STEPS.md)  
**Target output directory:** [`artifacts/human_annotations/`](../artifacts/human_annotations/README.md) (CC-BY-4.0, pseudonymous `annotator_1` / `annotator_2` IDs for double-blind compatibility)
**Status:** **Steps 2–5 COMPLETE (arXiv v0.6 Release Gate Passed)** — `4/4` named critiques + `5/5` clean spot-checks (`0/5` missed drift) + `n = 30` blinded Stage-4 IRR (`30/30`, $\kappa = 1.000, \alpha = 1.000$ on `lean_usage_status`) integrated into `papers/arxiv-empirical/main.tex` v0.6.

---

## Methodological Design & Transparency

Because verifying Lean 4 theorem signatures (Stage 5) and classifying arXiv preprints (Stage 4) demand different skill sets, this plan separates human verification into two transparent protocols:

1. **Steps 2 & 3 (Stage-5 Lean Code Verification — Guided Human Walkthrough):**
   - For each repository, an assistant presents the **exact raw paper excerpt**, the **exact raw Lean source lines** at the pinned commit SHA, and the draft manuscript text side-by-side, translating Lean 4 syntax into standard mathematical notation line-by-line.
   - The human author (`annotator_1`) directly inspects the raw source, checks whether the mathematical logic and scope match the paper, approves or revises the manuscript wording, and records sign-off in `artifacts/human_annotations/layer_a_human_verification.json`.
   - **Disclosure:** The manuscript will transparently state that human verification of Lean signatures used AI-assisted Lean syntax explanation while human authors directly inspected raw source lines and judged mathematical validity and fairness.
2. **Step 4 (Stage-4 Classification IRR — Strictly Blinded, Zero Lean Reading Required):**
   - Stage-4 labels (`lean_contributed` vs. `citation_only` / `false_positive`, `paper_domain_role`, `authoring_paradigm`, `verification_tier`, `ai_agent_assisted`) depend on paper abstracts, prose snippets, READMEs, and static profiler counts—requiring **no Lean code reading**.
   - Human annotator(s) label a **blinded** stratified sample (LLM outputs hidden) into `artifacts/human_annotations/stage4_irr.csv`, yielding an uncontaminated Human–LLM (and optionally Human–Human) Cohen's $\kappa$ / Krippendorff's $\alpha$.

---

## Step 2: Human Verification of the 4 Named Critiques (`4 / 4` Signed Off — COMPLETE)

All four upstream GitHub repositories were checked via `git ls-remote HEAD` on **2026-11-23**; **4/4 remain at the exact pinned commit SHAs** recorded in [`artifacts/phase2_provenance.json`](../artifacts/phase2_provenance.json) (zero post-snapshot commits pushed).

| # | arXiv ID | Repo & Pinned Commit | Live HEAD (2026-11-23) | Key Claims in `main.tex` to Confirm | Human Sign-Off | Outreach (Optional) |
| :-: | :--- | :--- | :--- | :--- | :---: | :---: |
| 1 | **`2611.26272`** (*Paper2Lean* / `OptPaper-20`, `v1`) | `TTony2019/OptPaper` @ `1bde49b` (2026-09-26) | Unchanged (`1bde49b`) | (a) Paper claims all discrepancies repaired / none unresolved; (b) `Moudafi_Oliny` scored 11/11 (100%) in Table 1 yet `thm_1.lean:1500` adds global `hB_lipschitz` vs. `IsCocoerciveWRT` (`def_5.lean:28-29`); (c) released partially-scored repos retain `Abbas` `hweak` premise (`rem_3.lean:33-57`), `Guler` `[FiniteDimensional ℝ H]` (`thm_3.lean:45-46`, docstring-disclosed), and `Attouch_Adly` bare `AntitoneOn` (`thm_9.lean:11-19`; tightened in `main.tex` to drop unverified external `$o(1/\ln t)$` claim). | `[x]` Co-reviewed (`annotator_1`, 2026-11-23) | `[ ]` |
| 2 | **`2611.04876`** (*MatrixRefresh*, `v1`) | `sdziembowski/MatrixRefresh` @ `7da3e11` (2026-11-16) | Unchanged (`7da3e11`) | `version-1.0/lean/Compiler.lean:1936-1978` defines comparator-checked `Compiler.main_theorem` over four statistical-distance privacy conjuncts, omitting standalone exact-correctness equality (proved internally in `Proofs/`). | `[x]` Co-reviewed (`annotator_1`, 2026-11-23) | `[ ]` |
| 3 | **`2605.14610`** (*Ku-PATP*, `v5`, T1) | `SZabolotnii/Ku-PATP-code-supplement` @ `69788a9` (2026-10-08) | Unchanged (`69788a9`) | Hardcoded tabular entropy formulas instead of Mathlib `MeasureTheory` integrals; `Lean/PATP/Entropy.lean:166-174` proves `Real.exp 1 / Real.sqrt 2` ($\approx 1.9221$, docstring `1.9230`) vs. paper §2.5 table `1.9300`. | `[x]` Co-reviewed (`annotator_1`, 2026-11-23) | `[ ]` |
| 4 | **`2605.02856`** (*Qanary*, `v2`, T1) | `rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856` @ `915da15` (2026-05-05) | Unchanged (`915da15`) | `MontgomeryPFPINI.lean:47-48` postulates closed-form two-branch map directly; `KStageComposition.lean:168-190` uses non-recursive two-case `match k` without induction; `lakefile.lean` references 4 unbundled `../qanary-*` sibling paths. | `[x]` Co-reviewed (`annotator_1`, 2026-11-23) | `[ ]` |

---

## Step 3: Clean-Cohort False-Negative Spot-Checks (`5 / 5` Signed Off — COMPLETE; `0 / 5` Missed Drift)

To test whether the `pro`-tier LLM auditor missed undisclosed drift in the `20/20` Oct–Nov 2026 clean author-owned cohort, we walked through **5 of the largest author-owned repositories** spanning `math.OC`, `cs.IT`, `math.NA`, T1+T2, and `P1`+`P4`:

| # | arXiv ID | Cat / Slice / Par | Scale (Owned LoC) | Auditor Verdict | Headline Boundary to Spot-Check | Human Sign-Off |
| :-: | :--- | :--- | ---: | :--- | :--- | :---: |
| 1 | **`2611.13872`** (*LongTails*) | `math.OC` / T2 / `P4` | 697,377 | `high_faithful` | Frozen `LongTails/Setups` specs + `verify.yml` comparator targets vs. paper oracle-complexity claims | `[x]` Co-reviewed (`annotator_1`, 2026-11-23; no missed drift) |
| 2 | **`2605.09552`** (*Phases of Muon*) | `math.OC` / T1 `v2` / `P1` | 340,300 | `mostly_faithful` | Main Muon phase-boundary theorems + `phaseOmegaTimesOK` guards + Mathlib Gaussian/Haar anchoring | `[x]` Co-reviewed (`annotator_1`, 2026-11-23; no missed drift) |
| 3 | **`2611.08172`** (*AG Codes 3-Fold Product*) | `cs.IT` / T2 / `P1` | 200,335 | `mostly_faithful` | Main AG code product-expansion theorems + custom algebraic-geometry definitions | `[x]` Co-reviewed (`annotator_1`, 2026-11-23; no missed drift) |
| 4 | **`2611.11713`** (*Binary BP Fixed Points*) | `cs.IT` / T2 / `P1` | 69,875 | `mostly_faithful` | Core BP response-geometry theorems + graph/factor-graph definitions | `[x]` Co-reviewed (`annotator_1`, 2026-11-23; no missed drift) |
| 5 | **`2611.12585`** (*KdV Galerkin Errors*) | `math.NA` / T2 anc. / `P1` | 60,664 | `mostly_faithful` | `CompanionFinal.main_theorem : P1 → Tails`, `tails_without_P1`, and `SLean.Bridge` weak-form equivalence | `[x]` Co-reviewed (`annotator_1`, 2026-11-23; no missed drift) |

---

## Step 4: Blinded Stage-4 Human IRR Plan (Zero Lean Reading Required)

### Sampling Design (`n = 30` Stratified Stage-2 Candidates)
Draw a reproducible, seeded stratified sample of **30 Stage-2 Lean candidates** across T2 (`n = 55`) and T1 (`n = 19`):
- **16 `lean_contributed` papers** stratified across:
  - All 3 domain roles (`engineering_math_proof`, `software_or_system_fv`, `pure_tcs_or_math`)
  - All observed paradigms (`P1`, `P4`, `P0`, plus T1 `P2`)
  - All 3 verification tiers (`Tier3_Gold`, `Tier2_Silver`, `Tier1_Bronze`) and AI-assistance labels (`explicitly_yes`, `unclear`, `explicitly_no`)
- **10 `citation_only` / `mentions_lean_future_work` candidates** (testing positive/negative boundary precision)
- **4 false positives / contextual-only borderline hits** (including contextual-only matches from T2)

### Execution Workflow
- [x] **4a. Build blinded review kit:** Created [`scripts/prepare_stage4_irr.py`](../scripts/prepare_stage4_irr.py) (`--seed 20261123`) generating:
  - A **blinded** CSV template ([`artifacts/human_annotations/stage4_irr_blank.csv`](../artifacts/human_annotations/stage4_irr_blank.csv)) matching [`artifacts/human_annotations/README.md`](../artifacts/human_annotations/README.md):
    `slice_id,arxiv_id,annotator_id,lean_usage_status,paper_domain_role,authoring_paradigm,verification_tier,ai_agent_assisted,notes`
  - A **self-contained, offline interactive HTML walkthrough** ([`docs/stage4_irr_walkthrough.html`](stage4_irr_walkthrough.html)) that opens locally in any browser (zero external dependencies, `localStorage` autosave, color-coded 5-step visual decision tree, auto-`N/A` short-circuiting for non-contributed hits, CSV import/resume, and one-click `stage4_irr.csv` export—verified 0 leaked LLM tokens).
  - A companion blinded Markdown dossier (`data/stage4_irr_dossier.md`, gitignored) containing each paper's title, abstract, Stage-2 matched prose snippets, README excerpt, and Stage-3 static counts—with **zero LLM predictions shown**.
- [x] **4b. Independent human annotation (arXiv-ready 1-rater tier COMPLETE):**
  - *arXiv-ready tier (1 rater):* `annotator_1` completed all 30 rows blindly via [`docs/stage4_irr_walkthrough.html`](stage4_irr_walkthrough.html) → archived in [`artifacts/human_annotations/stage4_irr.csv`](../artifacts/human_annotations/stage4_irr.csv).
  - *Archival peer-review tier (2 raters, optional before EMSE/ITP/NeurIPS):* `annotator_2` (Bhaskar) can independently complete the same 30 rows and append to `artifacts/human_annotations/stage4_irr.csv` (after fixing the static `has_solution_file` / full-sentence AI-context cues noted below).
- [x] **4c. Scoring & disagreement reconciliation (COMPLETE):** Ran `uv run python scripts/compute_irr.py --csv artifacts/human_annotations/stage4_irr.csv --json-out artifacts/human_annotations/stage4_irr_summary.json` ([`stage4_irr_summary.json`](../artifacts/human_annotations/stage4_irr_summary.json)):
  - **Primary inclusion boundary (`lean_usage_status` & binary `is_lean_contributed`, $n = 30$):** **30 / 30 (100.0%)**, **Cohen's $\kappa = 1.000$**, **Krippendorff's $\alpha = 1.000$** (`16/16` contributed, `10/10` citation/discussion, `4/4` false positives).
  - **All-item conditional attributes ($n = 30$):** `verification_tier` `0.833` ($\kappa = 0.754, \alpha = 0.758$), `authoring_paradigm` `0.800` ($\kappa = 0.690, \alpha = 0.695$), `ai_agent_assisted` `0.800` ($\kappa = 0.680, \alpha = 0.685$), `paper_domain_role` `0.700` ($\kappa = 0.573, \alpha = 0.568$).
  - **Mutually-agreed `lean_contributed` subset ($n = 16$, 26 total disagreements reconciled):** `verification_tier` `0.688` ($\kappa = 0.506, \alpha = 0.517$), `authoring_paradigm` `0.625` ($\kappa = 0.278, \alpha = 0.298$), `ai_agent_assisted` `0.625` ($\kappa = 0.165, \alpha = 0.188$), `paper_domain_role` `0.438` ($\kappa = 0.217, \alpha = 0.160$). Reconciled into 3 clean causes in Section 8.1 of `main.tex`: (a) evidence-window asymmetry & static-flag pitfalls (`11/26`, including `*Resolution*.lean` false `has_solution_file` chip and uncontextualized `.tex` AI chips on `2605.14610`/`2605.16407`), (b) genuine `pure_tcs_or_math` vs. `engineering_math_proof` boundary fuzziness & hybrid automated math-research frameworks (`9/26`, `2611.13872`/`2611.23080`), and (c) one genuine LLM rubric lenience on `2611.16690` (`sorry = 1` → strict `Tier1_Bronze`) plus partial-scope edge cases (`5/26`).

---

## Step 5: Integration & arXiv Preprint Release Gate (COMPLETE)

- [x] Integrated Steps 2–4 results (Section 8: blinded Stage-4 IRR Table + 3-cause reconciliation, guided Stage-5 co-review of 4/4 named critiques and 5/5 clean-cohort spot-checks) into [`papers/arxiv-empirical/main.tex`](../papers/arxiv-empirical/main.tex) (promoted to **v0.6**) and wired programmatic verification into [`scripts/check_paper_numbers.py`](../scripts/check_paper_numbers.py).
- [x] Updated [`docs/audit_plan.md`](audit_plan.md), [`docs/PROGRESS_AND_NEXT_STEPS.md`](PROGRESS_AND_NEXT_STEPS.md), and refreshed [`docs/publication_strategy.html`](publication_strategy.html).
- [x] Passed all CI gates (`uv run pytest`, `scripts/audit_bib.py --live`, `scripts/check_paper_numbers.py`, `scripts/export_blind_artifact.py`, clean `make -C papers/arxiv-empirical` with 0 warnings/overfull boxes) and exported & test-compiled the clean arXiv source tarball (`dist/arxiv-empirical-v0.6.tar.gz`).

---

## Post-Unification Follow-Up Items (15-Category Unified Manuscript)

- [ ] **Guided human co-review of the 2 post-expansion named critiques (`2611.07395`, `2611.14586`):** Source lines were deterministically verified on disk during Phase 1 of [`docs/paper_reorg_plan.md`](paper_reorg_plan.md), leaving `artifacts/human_annotations/layer_a_human_verification.json` at `4/4` human-signed initial critiques (`+ 5/5` clean spot-checks). Completing guided co-review on these two repositories brings human-signed critique coverage to `6/6 (100%)`.
- [ ] **Expand Phase B2 dual-rater 4-way IRR kit from `47` to `82` confirmed 15-category papers:** Refresh [`artifacts/human_annotations/track1_4way_coding_blank.csv`](../artifacts/human_annotations/track1_4way_coding_blank.csv) (currently seeded with the 47 pre-expansion papers) to cover all 82 confirmed 15-category papers (or a stratified 15-category sample) for independent `annotator_1` + `annotator_2` validation of the primary 4-way taxonomy.
