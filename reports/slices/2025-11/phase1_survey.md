# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2025-11-01` to `2025-11-19` (3 weeks)
- **Target categories (8):** `cs.CR`, `cs.DC`, `cs.IT`, `cs.NI`, `cs.RO`, `eess.SP`, `eess.SY`, `math.OC`
- **Corpus size:** 2435 unique papers (2421 full-text screened, 99.43% coverage)
- **Non-TCS-primary engineering corpus (excluding primary ['cs.CC', 'cs.CG', 'cs.DM', 'cs.DS', 'cs.FL', 'cs.LO']):** 2417 unique papers
- **Confirmed papers contributing Lean proofs (all):** **1** (0.04% of corpus)
- **Confirmed Lean papers (non-TCS primary):** **1** (0.04% of non-TCS corpus)
- **Confirmed `engineering_math_proof` Lean papers:** **0** (0.00% of corpus)
- **Confirmed Beyond-Lean formal verification (Pilot v1 baseline):** **0**

## 1. Category Breakdown & Lean Candidate Triage

| Category | Total Papers | Lean Contrib. | Lean (%) | Eng. Math Proof |
| :--- | ---: | ---: | ---: | ---: |
| `cs.CR` | 406 | 1 | 0.25% | 0 |
| `cs.DC` | 223 | 1 | 0.45% | 0 |
| `cs.IT` | 209 | 0 | 0.00% | 0 |
| `cs.NI` | 136 | 0 | 0.00% | 0 |
| `cs.RO` | 532 | 0 | 0.00% | 0 |
| `eess.SP` | 338 | 0 | 0.00% | 0 |
| `eess.SY` | 476 | 0 | 0.00% | 0 |
| `math.OC` | 410 | 0 | 0.00% | 0 |
| **Deduplicated Union** | **2435** | **1** | **0.04%** | **0** |

| Lean Triage Status | Count |
| :--- | ---: |
| `lean_citation_or_discussion` | 2 |
| `lean_contributed` | 1 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 0 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 0 |
| `P0_opaque_or_unspecified` | 1 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'software_or_system_fv': 1}
- **Observed Verification Tiers:** {'Tier1_Bronze': 1}
- **Artifact Availability:** {'broken_or_missing_repo': 1}
- **AI/Agent Assistance Disclosed:** {'unclear': 1}
- **Target Categories (Lean Contributed):** {'cs.CR': 1, 'cs.DC': 1}
- **Static Risk Flags (`proof-methods.md`):** {'Mode2_ScopeDowngrade': 1, 'Mode12_ProcessOpacity': 1}

## 4. Detailed Inventory of Confirmed Lean Papers (1)

| arXiv ID | Cat | Target Cats | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2511.15517](https://arxiv.org/abs/2511.15517) | `cs.CR` | `cs.CR,cs.DC` | `software_or_system_fv` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `broken_or_missing_repo` | `unclear` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Beluga: Block Synchronization for BFT Consensus Protocols** — Beluga claims machine-checked Lean proofs for all non-probabilistic theorems via uploaded 'Additional materials' and Appendix I, but provides no accessible public Lean repository for Beluga (the cloned asonnino/mysticeti Lean directory formalizes the separate Hydrozoan paper), yielding P0_opaque_or_unspecified and Tier1_Bronze. |

### Evidence Notes per Confirmed Lean Paper

#### [2511.15517](https://arxiv.org/abs/2511.15517) — Beluga: Block Synchronization for BFT Consensus Protocols
- **Primary / Target Cats:** `cs.CR` / ['cs.CR', 'cs.DC'] | **Role:** `software_or_system_fv`
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` ([])
- **Evidence:** Contribution (4) and Appendix I state that all non-probabilistic theorems are formalized in Lean with proof artefacts uploaded as 'Additional materials' and an appendix detailing what is/isn't formalized and paper-implicit choices made explicit; however, asonnino/beluga and AUTHOR/REPO are inaccessible, and the cloned asonnino/mysticeti repo's lean/ directory (Hydrozoan, Lean v4.33.0) is for a different paper, leaving Beluga's Lean code and authoring workflow unobservable.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `asonnino/mysticeti` (github):** `.lean` files=57, LoC=5603, theorems=139, defs=141, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.0`, ci=`['lake build']`

## 5. Beyond-Lean Formal Verification Baseline (Pilot v1 Categories)

- **Candidate triage:** {}
- **Tool categories (contributed):** {}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Rocq` | 1 |

### Confirmed Beyond-Lean Papers
