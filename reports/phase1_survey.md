# Phase 1 Survey Report: Lean & Formal Proofs in Recent Engineering/Systems arXiv Papers

- **Date window (submitted):** `2026-11-01` to `2026-11-19` (3 weeks)
- **Target categories (ANRG-aligned S3):** `cs.DC`, `cs.NI`, `cs.IT`, `eess.SY`, `cs.CR`, `cs.RO`
- **Corpus size:** 3160 unique papers (3155 full-text screened, 99.84% coverage)
- **Confirmed papers contributing Lean proofs:** **20** (0.63% of corpus)
- **Confirmed papers contributing non-Lean formal verification:** **12** (0.38% of corpus)

## 1. Lean Candidate Triage Summary

| Status | Count |
| :--- | ---: |
| `lean_contributed` | 20 |
| `lean_citation_or_discussion` | 7 |
| `false_positive` | 3 |

## 2. Authoring Paradigm Distribution (Confirmed Lean Papers, per `proof-methods.md`)

| Paradigm | Count |
| :--- | ---: |
| `P1_paper_first_posthoc` | 16 |
| `P2_lean_first` | 0 |
| `P3_blueprint_sync` | 0 |
| `P4_speclock_solve_distill` | 2 |
| `P0_opaque_or_unspecified` | 2 |

## 3. Verification Tiers, Artifacts, AI Assistance & Static Risk Flags

- **Domain Role (Bhaskar's lens):** {'software_or_system_fv': 4, 'engineering_math_proof': 11, 'pure_tcs_or_math': 5}
- **Observed Verification Tiers:** {'Tier1_Bronze': 7, 'Tier2_Silver': 4, 'Tier3_Gold': 9}
- **Artifact Availability:** {'none': 3, 'public_lean_repo': 17}
- **AI/Agent Assistance Disclosed:** {'unclear': 4, 'explicitly_yes': 16}
- **Target Categories (Lean Contributed):** {'cs.CR': 7, 'cs.IT': 6, 'eess.SY': 3, 'cs.DC': 6}
- **Static Risk Flags (`proof-methods.md`):** {'Mode12_ProcessOpacity': 9, 'Mode10_ProofBloat': 8, 'Mode2_ScopeDowngrade': 7, 'Mode6_SorryOrAxiomOrNativeDecide': 2}

## 4. Detailed Inventory of Confirmed Lean Papers (20)

| arXiv ID | Cat | Domain Role | Paradigm | Tier | Artifact | AI? | Risk Flags | Title / Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [2611.25599](https://arxiv.org/abs/2611.25599) | `cs.CR` | `software_or_system_fv` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `unclear` | Mode12_ProcessOpacity | **Tether: Verified Stateful Policy Engine for System-Level Monitoring of** — Tether implements a stateful agent security policy EDSL and verifies safety invariants in Lean 4, but provides no public Lean repository or authoring workflow details. |
| [2611.23762](https://arxiv.org/abs/2611.23762) | `quant-ph` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Addressable transversal CCZ gates on almost good quantum LDPC codes an** — Post-hoc Mathlib-based Lean 4 formalization of three supporting algebraic lemmas (zero sorry/axioms) for an AI-generated companion note proving an assumption of the paper's quantum LDPC CCZ-gate construction, lacking lakefile/toolchain/CI and not covering the main theorems. |
| [2611.22732](https://arxiv.org/abs/2611.22732) | `cs.CR` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **Provable Mixing Properties of Parallel Mixnets Revisited** — Analyzes parallel mixnets via statistical variance and concentration bounds for differential indistinguishability, claiming a full accompanying Lean mechanization at a public MPI-SWS GitLab repo carried out entirely by Claude. |
| [2611.20298](https://arxiv.org/abs/2611.20298) | `cs.PL` | `software_or_system_fv` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Type-Confusion Security** — Mechanizes type-confusion security proofs for an RPC/information-flow core calculus in Lean 4 using Mathlib, translated from pen-and-paper proofs with Codex and Claude Code assistance, with an axioms audit mentioned but no public repository URL provided. |
| [2611.19551](https://arxiv.org/abs/2611.19551) | `cs.CR` | `software_or_system_fv` | `P1_paper_first_posthoc` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | none | **TrustBound: Mechanized Completeness for Payment Epochs Initiated by AI** — Formalizes an admission-fencing and provider-contract closure model for AI-agent payment epochs in Lean 4.19.0 (zero sorry/custom axioms, checked via #print axioms, premise-removal mutations, and CI) alongside trace-checked Python service histories. |
| [2611.18220](https://arxiv.org/abs/2611.18220) | `eess.SY` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode12_ProcessOpacity | **From Pen-and-Paper to Machine-Checked Proofs: Lean for System Identifi** — Tutorial introducing Lean 4 and Mathlib for system identification and control, formalizing elementary identifiability/invariance examples, an ARX/PEM template, and an almost-sure sharpening of Ljung (1999) Lemma 3.1 in a public repo with #print axioms checks but no lakefile/lean-toolchain/CI. |
| [2611.15201](https://arxiv.org/abs/2611.15201) | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode12_ProcessOpacity | **Sparse Matrix Multiplication Exponent 1.5 in the Low-bandwidth Model** — Distributed computing theory paper proving an O(d^{3/2})-round deterministic sparse matrix multiplication algorithm in the low-bandwidth model, with an AI-generated Lean formalization deposited on Zenodo. |
| [2611.15128](https://arxiv.org/abs/2611.15128) | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (medium) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode12_ProcessOpacity | **Affine Combiners for Reed-Solomon Proximity Gaps** — Proves improved Reed-Solomon and Reed-Muller proximity gap bounds for affine combiners via AI-generated proofs and post-hoc Lean formalization (via ChatGPT 6 Astra and Claude Code Opus 5.5) excluding Sections 5, 7, and Appendix A, linking leanEthereum/leanVM (uncloned due to size). |
| [2611.14475](https://arxiv.org/abs/2611.14475) | `math.FA` | `engineering_math_proof` | `P4_speclock_solve_distill` (medium) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Explicit restricted isometries with $k=m^{2/3-o(1)}$** — Formalizes all main theorems of an explicit RIP matrix construction (k = m^{2/3-o(1)}) and 2/3 barriers in Lean 4/Mathlib using AI agents under a frozen-statement and Comparator (NanoDa + Lean kernel) spec-lock, omitting only the polynomial running-time bound for 'explicit'. |
| [2611.11713](https://arxiv.org/abs/2611.11713) | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Binary Belief Propagation Fixed Points: Finiteness, Rigidity, and Topo** — Formally verifies all three main theorems (finiteness, rigidity, and logarithmic genus/size bounds) on binary belief propagation fixed points in Lean 4 with Mathlib and an automated transitive-axiom audit, alongside standalone Python rational interval certificates for a 18-vertex discriminant example. |
| [2611.10902](https://arxiv.org/abs/2611.10902) | `eess.SY` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade | **Bisect-Index-Choose: A Fast and Exact Algorithm for EV Charging under ** — EV charging optimization paper (eess.SY) contributing a Lean 4 + Mathlib formalization (~2,068 LoC) of its main theorems (Theorems 1-4 for K=2, Lemmas 1-2, strong duality, Table I, Appendices A-B, and Algorithm 1 evaluation bound) with a 34-theorem #print axioms manifest and zero sorry/custom axioms, though excluding K!=2 cases, bisection tolerances, and runtime bounds. |
| [2611.10810](https://arxiv.org/abs/2611.10810) | `cs.DB` | `software_or_system_fv` | `P1_paper_first_posthoc` (medium) | `Tier2_Silver` | `public_lean_repo` | `unclear` | Mode2_ScopeDowngrade | **Extending DBLog-Based Incremental Snapshots to Handle Orphan Rows in C** — Formalizes safety and convergence of DBLog orphan-row CDC extensions primarily in Isabelle/HOL (plus TLA+/TLC) with main results re-proved in Lean 4 in a Zenodo artifact. |
| [2611.08172](https://arxiv.org/abs/2611.08172) | `cs.IT` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Uniform Three-Fold Product Expansion of Algebraic-Geometry Codes over ** — Formalizes in Lean 4 (with ~200k LoC, zero sorry/custom axioms, and full-closure audit scripts) the main uniform 3-fold product expansion, sharp filling, and dual-family rate/distance theorems for algebraic-geometry codes on the Garcia-Stichtenoth tower over F_729. |
| [2611.05136](https://arxiv.org/abs/2611.05136) | `cs.CC` | `engineering_math_proof` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade, Mode10_ProofBloat | **Information Loss Is All You Need: $TC^0$ Pseudorandomness from Worst-C** — AI-generated 219k-LoC Lean 4 formalization of Theorem 9.9 (constructive Gaussian AFT sampler in a counted binary-operation model) with exhaustive transitive axiom audit (Audit.lean) and provenance manifest, covering one core theorem rather than the paper's full LWE-to-LAR/TC0-PRF/ReLU-hardness claims. |
| [2611.04876](https://arxiv.org/abs/2611.04876) | `cs.CR` | `engineering_math_proof` | `P4_speclock_solve_distill` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Leakage-Resilient Computation via Matrix Refreshing** — Formalizes continual matrix refreshing, NAND/stateful leakage-resilient circuit compilers, and expected-work simulators in Lean 4 (81k LoC) using ChatGPT under a comparator Challenge/Solution spec-lock (`Proofs.ReferenceClaims` vs `Proofs.ProvedClaims`). |
| [2611.04561](https://arxiv.org/abs/2611.04561) | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat, Mode6_SorryOrAxiomOrNativeDecide | **Distributed LTL Synthesis under Arbitrary Message Adversaries** — Distributed LTL synthesis decidability characterization (nowhere-dense geometric image and repeated consensus) formalized post-hoc in ~929k LoC of Lean 4.30/Mathlib with Codex/Claude assistance; main Results and Paper endpoints pass #print axioms and Comparator+Nanoda kernel replay with only standard axioms, while two native_decide calls appear in an unimported falsification probe. |
| [2611.02256](https://arxiv.org/abs/2611.02256) | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier2_Silver` | `public_lean_repo` | `explicitly_yes` | Mode2_ScopeDowngrade | **Exact Shortest Paths and Maximum Flow in Planar Networks in the CONGES** — CONGEST planar-network SSSP and max-flow paper formalizing three supporting lemmas (Virtual Source, Dual Distance, discretized boosting) and auxiliary arguments in Lean 4/Mathlib without sorry or custom axioms, while leaving the main distributed algorithms and round bounds on paper. |
| [2611.02057](https://arxiv.org/abs/2611.02057) | `cs.DS` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier1_Bronze` | `public_lean_repo` | `explicitly_yes` | Mode6_SorryOrAxiomOrNativeDecide, Mode10_ProofBloat, Mode12_ProcessOpacity | **Paying for Fractional Error: Tight Constant-Round Approximation of Cov** — Formalizes all 81 named distributed-CONGEST covering-approximation results in a 166k-LoC Lean 4 repo with AI assistance; 73 statements use only standard axioms while 8 (including Theorem E and Corollary 1.1) depend on 7 declared external graph/topology axioms, with no CI and an incomplete rebuild of the export. |
| [2611.01761](https://arxiv.org/abs/2611.01761) | `cs.DC` | `pure_tcs_or_math` | `P1_paper_first_posthoc` (high) | `Tier3_Gold` | `public_lean_repo` | `explicitly_yes` | Mode10_ProofBloat | **Computation in Anonymous Directed Dynamic Networks: Exact Worst-Case T** — Public Lean 4 formalization (158k LoC, 2,104 files) produced with ChatGPT-6 Astra covering all 24 formal statements of a cs.DC distributed-counting paper, audited by a custom transitive axiom checker with zero sorry/axioms. |
| [2611.15431](https://arxiv.org/abs/2611.15431) | `quant-ph` | `engineering_math_proof` | `P0_opaque_or_unspecified` (high) | `Tier1_Bronze` | `none` | `explicitly_yes` | Mode12_ProcessOpacity | **Subadditivity and the failure of strong subadditivity in the Nichols--** — Proves subadditivity and strong-subadditivity failure for Nichols-Wootters entropies (with cs.IT capacity applications) and claims AI-assisted Lean formal verification in the acknowledgments without providing a public Lean repository or workflow details. |

### Evidence Notes per Confirmed Lean Paper

#### [2611.25599](https://arxiv.org/abs/2611.25599) — Tether: Verified Stateful Policy Engine for System-Level Monitoring of Agents
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `unclear` (['Claude', 'Codex', 'Gemini'])
- **Evidence:** The paper implements an abstract action calculus and stateful policy language as a Lean 4 EDSL that compiles to a runtime monitor and proves safety invariants in Lean 4 (Table 1), but provides no public Lean repository (all listed repos have 0 .lean files) and no workflow details indicating paper-first, Lean-first, blueprint-sync, or spec-lock.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.23762](https://arxiv.org/abs/2611.23762) — Addressable transversal CCZ gates on almost good quantum LDPC codes and nearly optimal magic state protocols
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** Paper states the proof of Assumption 1.1 in a companion manuscript was generated using AI and is in a companion repo 'together with Lean formalizations of selected algebraic lemmas. We are revising the exposition and extending the Lean formalization, which does not yet cover the full argument.' The repo (CoprimeFrobenius.lean, 667 lines, 0 sorry) formalizes three lemmas from the companion PDF ('exactly as in the note') without blueprint sync, comparator spec-lock, lakefile, or lean-toolchain.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification`:** `.lean` files=1, LoC=589, theorems=36, defs=5, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.22732](https://arxiv.org/abs/2611.22732) — Provable Mixing Properties of Parallel Mixnets Revisited
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude', 'ChatGPT', 'Gemini'])
- **Evidence:** Paper states 'The main results of this paper have been verified in the mechanical proof assistant, Lean' with a public GitLab repository (https://gitlab.mpi-sws.org/FCS/mixnets-sync-public), and notes 'The Lean formalization that accompanies this paper was carried out entirely by Claude' alongside informal proofs (12 theorem environments) with no mention of blueprint sync or spec-lock tooling; local_repo_dirs is empty (only unrelated arXiv HTML GitHub repos were scraped).
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.20298](https://arxiv.org/abs/2611.20298) — Type-Confusion Security
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Codex', 'Claude Code'])
- **Evidence:** The AI Use section explicitly states that Codex and Claude Code assisted with Lean 4 development by 'assisting in the translation of pen-and-paper definitions and proofs', and the Data-Availability Statement notes a README.md manually mapping each paper result to its Lean definition, indicating post-hoc formalization of pen-and-paper proofs without blueprint or spec-lock tooling.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.19551](https://arxiv.org/abs/2611.19551) — TrustBound: Mechanized Completeness for Payment Epochs Initiated by AI Agents
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT', 'Codex', 'Claude'])
- **Evidence:** The LNCS manuscript (paper/lncs/main.tex) states the admission model and closure theorem informally with prose proofs and cites Lean declarations in footnotes and a verbatim excerpt, without LeanArchitect/leanblueprint (has_blueprint_dir=false) or comparator/spec-lock files (has_challenge_file=false, has_solution_file=false); formal/README.md notes supporting Lean models retained for provenance alongside the two core files (Admission.lean, StripeGate.lean). The paper explicitly discloses using OpenAI ChatGPT, Codex, and Anthropic Claude for code development, literature exploration, and manuscript editing.
- **Risk flags:** []
- **Repo `tokencraftdata/trustbound`:** `.lean` files=16, LoC=1332, theorems=160, defs=135, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`

#### [2611.18220](https://arxiv.org/abs/2611.18220) — From Pen-and-Paper to Machine-Checked Proofs: Lean for System Identification
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` (['Claude'])
- **Evidence:** Tutorial paper formalizing existing pen-and-paper textbook results (Ljung 1999 Lemma 3.1, basic identifiability, set invariance, ARX identifiability) in an accompanying repo manasdm/Lean-SysID (created Nov 2-3, 2026 before Nov 13, 2026 submission). Uses '-- ANCHOR:' comments to reproduce Lean snippets in the paper, with no blueprint directory, @[blueprint]/\inputleannode, or Challenge/Solution spec-lock.
- **Risk flags:** ['Mode12_ProcessOpacity']
- **Repo `forgi86/control-theory-in-lean`:** `.lean` files=7, LoC=1196, theorems=38, defs=28, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `manasdm/Lean-SysID`:** `.lean` files=4, LoC=528, theorems=21, defs=19, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.15201](https://arxiv.org/abs/2611.15201) — Sparse Matrix Multiplication Exponent 1.5 in the Low-bandwidth Model
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Codex', 'GPT-6.1 Sol'])
- **Evidence:** Paper states AI tools (Codex, GPT-6.1 Sol) assisted with algorithm design, proof, literature, and text revision, adding 'Moreover, we used AI to formalize the results of this paper in Lean' with a Zenodo DOI (10.5281/zenodo.24127514), indicating post-hoc AI formalization without blueprint or spec-lock tooling.
- **Risk flags:** ['Mode12_ProcessOpacity']

#### [2611.15128](https://arxiv.org/abs/2611.15128) — Affine Combiners for Reed-Solomon Proximity Gaps
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['ChatGPT 6 Astra', 'Claude Code Opus 5.5'])
- **Evidence:** Paper states all analysis/proofs were carried out with AI and the authors 'edited, verified, reorganized, and Lean-formalized the initial writeup' using ChatGPT 6 Astra with theorem statements checked by Claude Code Opus 5.5, excluding Section 5, Section 7, and Appendix A; linked repo leanEthereum/leanVM has has_blueprint_dir=false and clone_skipped=size_kb=419885>200000 so file-level workflow could not be inspected.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode12_ProcessOpacity']
- **Repo `leanEthereum/leanVM`:** `.lean` files=2627, LoC=0, theorems=0, defs=0, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`

#### [2611.14475](https://arxiv.org/abs/2611.14475) — Explicit restricted isometries with $k=m^{2/3-o(1)}$
- **Paradigm:** `P4_speclock_solve_distill` (`medium`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Claude Opus 5.5', 'Claude Code', 'GPT-6.1 Sol', 'GPT-6 Astra', 'Codex CLI', 'ChatGPT'])
- **Evidence:** Statements were drafted and frozen from the paper into ExplicitRIP/Frozen/ and Challenge.lean (with sorry), audited against the paper, then solved by parallel AI agents (Opus 5.5 orchestrator, GPT-6.1 Sol, GPT-6 Astra, Claude subagents) and verified against Solution.lean via Comparator (comparator.json, NanoDa enabled). Although the paper text and initial proof were drafted first/concurrently (Nov 7–10, 2026) rather than purely Lean-first, the repo explicitly uses frozen Challenge.lean/Solution.lean spec-locking and unconstrained AI proof search, with formalization also surfacing local fixes to cited arguments (footnote 2).
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `ckuemmerle/ExplicitRIPTwoThirds`:** `.lean` files=379, LoC=29967, theorems=1222, defs=258, sorry=4, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.11713](https://arxiv.org/abs/2611.11713) — Binary Belief Propagation Fixed Points: Finiteness, Rigidity, and Topological Complexity
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Large language model tools'])
- **Evidence:** No blueprint directory or Challenge/Solution spec-lock is present; TheoremB.lean explicitly references the manuscript ('論文 papers/bp-response-geometry/ の主定理 B'), and Section 8 and README.md document where the Lean formalization departs from the written proofs and which parts remain outside it, with LLM tools explicitly credited for writing the Lean formalization.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `TauCetiProject/TauCeti`:** `.lean` files=37714, LoC=0, theorems=0, defs=0, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
- **Repo `ywatanabex/bp-degree-syzygies-lean`:** `.lean` files=932, LoC=135060, theorems=7411, defs=3205, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Repo `ywatanabex/bp-response-geometry-lean`:** `.lean` files=257, LoC=69875, theorems=3955, defs=1291, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.10902](https://arxiv.org/abs/2611.10902) — Bisect-Index-Choose: A Fast and Exact Algorithm for EV Charging under Minimum Charging Rates
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `unclear` (['Claude'])
- **Evidence:** Public repo canberksaner/bic-public has a lean/ subdirectory (11 Lean 4 files, 2,068 non-empty LoC, Mathlib v4.36.0-rc2) with no blueprint directory, LeanArchitect annotations, or Challenge/Solution spec-lock files. README.md and Lean docstrings (e.g., Correctness.lean, Choose.lean, Everett.lean) explicitly map theorems to existing paper labels, equations, sections, and algorithm line numbers ('lines ch-while to ch-dec', '(eq:decomposition)', 'Lean's groups 0 and 1 are the paper's groups 1 and 2') and list which paper results are checked vs omitted, indicating post-hoc formalization of paper proofs. CheckAxioms.lean runs 34 #print axioms checks with zero sorry/axiom/native_decide. latex_signals.agent_tools lists 'Claude', without context in the repo or snippets.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `canberksaner/bic-public`:** `.lean` files=11, LoC=2068, theorems=102, defs=40, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`

#### [2611.10810](https://arxiv.org/abs/2611.10810) — Extending DBLog-Based Incremental Snapshots to Handle Orphan Rows in CDC Pipelines
- **Paradigm:** `P1_paper_first_posthoc` (`medium`) | **Tier:** `Tier2_Silver` | **AI:** `unclear` (['Claude', 'Gemini'])
- **Evidence:** Paper extends the Generalized DBLog formal model and verifies safety and convergence primarily in Isabelle/HOL, with main results re-proved in Lean 4 (omitting Flink CDC range merge) and bounded TLA+/TLC models in a Zenodo artifact (doi:10.5281/zenodo.24035424); no blueprint-sync or spec-lock tooling is mentioned, and the Zenodo archive was not locally inspected (local_repo_dirs is empty). latex_signals.agent_tools hits Claude and Gemini without snippet context.
- **Risk flags:** ['Mode2_ScopeDowngrade']

#### [2611.08172](https://arxiv.org/abs/2611.08172) — Uniform Three-Fold Product Expansion of Algebraic-Geometry Codes over a Fixed Field
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Harmonic'])
- **Evidence:** The 76-page cs.IT manuscript states its principal conclusions were formally verified in Lean 4 in an accompanying artifact (dcass-121/d3-lean-verification) unpacked as a submission archive with no leanblueprint/LeanArchitect sync and no Challenge/Solution spec-lock (the scraper's has_solution_file flag is a false positive from *Resolution*.lean files). Both the paper and README map manuscript statements (Target 4.10 / Theorem C, Theorem A with a cruder explicit constant, Corollary B dual parameters, genus-ratio limit) to Lean endpoints while explicitly documenting omitted secondary results (Schur fullness, closed genus formula, general-field extension), characteristic of post-hoc formalization.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `dcass-121/d3-lean-verification`:** `.lean` files=2486, LoC=200335, theorems=8473, defs=5031, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.31.0`, ci=`[]`

#### [2611.05136](https://arxiv.org/abs/2611.05136) — Information Loss Is All You Need: $TC^0$ Pseudorandomness from Worst-Case Lattices
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` ([])
- **Evidence:** Paper manuscript was written/checked by the human author while the Lean 4 formalization of Theorem 9.9 (thm:df-constructive-aft) was generated separately by AI without editing LaTeX files ('No manuscript files were edited by this proof task' in provenance/upstream-manuscript-manifest.json) and without leanblueprint, LeanArchitect, Verso Blueprints, or comparator/Challenge.lean spec-lock tooling; alignment with concurrent manuscript edits was tracked manually via SHA-256 manifests.
- **Risk flags:** ['Mode2_ScopeDowngrade', 'Mode10_ProofBloat']
- **Repo `qianchen92/aft-lean-theorem99`:** `.lean` files=1794, LoC=219688, theorems=11051, defs=6431, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0-rc1`, ci=`[]`

#### [2611.04876](https://arxiv.org/abs/2611.04876) — Leakage-Resilient Computation via Matrix Refreshing
- **Paradigm:** `P4_speclock_solve_distill` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT'])
- **Evidence:** `version-1.0/lean/comparator.json` locks `Proofs.ReferenceClaims` (importing `Refreshing.lean`, `Compiler.lean`, `EfficientSimulation.lean`, whose 3 main theorems and 38 certificates are deliberately stubbed with `by sorry`) against `Proofs.ProvedClaims` (complete sorry-free proofs under `Proofs/`), verified via `lake comparator --paranoid` (permitting only `propext`, `Quot.sound`, `Classical.choice`) and `scripts/check_lean_proof_layout.py`, accompanied by `annotated-specifications.pdf`; the paper explicitly states "The Lean formalization was done by ChatGPT" and that the authors iterated with the AI to simplify proofs and write the paper.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `sdziembowski/MatrixRefresh`:** `.lean` files=417, LoC=81481, theorems=3285, defs=1933, sorry=41, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`

#### [2611.04561](https://arxiv.org/abs/2611.04561) — Distributed LTL Synthesis under Arbitrary Message Adversaries
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['Codex', 'Claude', 'GPT-6'])
- **Evidence:** Authors state they developed the mathematical characterization without AI, had an initial AI-assisted Lean/LaTeX exploration, then wrote a new manuscript from scratch without reusing the AI LaTeX draft, and 'Finally, we used AI again to formalize in Lean the statements and proofs as written in this paper.' Formalization supplements the paper via clickable badges to Paper/*.lean wrappers checked by scripts/check_paper_links.py, with no leanblueprint/LeanArchitect sync.
- **Risk flags:** ['Mode10_ProofBloat', 'Mode6_SorryOrAxiomOrNativeDecide']
- **Repo `BioDisCo/distributed_synthesis_lean`:** `.lean` files=2395, LoC=929448, theorems=20193, defs=20454, sorry=0, axiom=0, native_decide=2, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0`, ci=`[]`

#### [2611.02256](https://arxiv.org/abs/2611.02256) — Exact Shortest Paths and Maximum Flow in Planar Networks in the CONGEST Model
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier2_Silver` | **AI:** `explicitly_yes` (['Claude Opus 5.5'])
- **Evidence:** The paper and working notes (notes/NOTES.md, notes/LEMMA15.md, etc.) develop the CONGEST algorithms and proofs informally on paper, while lean/SsspFlow/ formalizes only selected supporting mathematical lemmas (Virtual Source, Dual Distance, discretized boosting, plus auxiliary recursion/tools) with explicit 'Not formalized' notes and no blueprint/LeanArchitect or Challenge/Solution spec-lock tooling. README.md explicitly states Claude Opus 5.5 was used to search literature, develop/check proofs, write scripts and the Lean formalization, and draft text.
- **Risk flags:** ['Mode2_ScopeDowngrade']
- **Repo `ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs`:** `.lean` files=14, LoC=2191, theorems=132, defs=52, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc1`, ci=`[]`

#### [2611.02057](https://arxiv.org/abs/2611.02057) — Paying for Fractional Error: Tight Constant-Round Approximation of Covering Problems with Short Broadcasts
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['Claude'])
- **Evidence:** The paper states in Section J that all 81 named results were formalized in Lean 4 across 1612 modules and that AI models (Claude in latex_signals) were used for independent reviews and Lean formalization. The repo has no blueprint directory, LeanArchitect annotations, or comparator Challenge/Solution lock (has_blueprint_dir=false, has_challenge_file=false, tex_file_count=0), instead using a post-hoc statement-level correspondence map (PaperIndex.lean, docs/correspondence.md, verification/statement-map.json).
- **Risk flags:** ['Mode6_SorryOrAxiomOrNativeDecide', 'Mode10_ProofBloat', 'Mode12_ProcessOpacity']
- **Repo `wwawrzy/paying-for-fractional-error-lean`:** `.lean` files=1617, LoC=166354, theorems=8757, defs=3745, sorry=0, axiom=10, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0`, ci=`[]`

#### [2611.01761](https://arxiv.org/abs/2611.01761) — Computation in Anonymous Directed Dynamic Networks: Exact Worst-Case Termination Time and Network-Wise Intractability
- **Paradigm:** `P1_paper_first_posthoc` (`high`) | **Tier:** `Tier3_Gold` | **AI:** `explicitly_yes` (['ChatGPT-6 Astra'])
- **Evidence:** paper.tex explicitly discloses using ChatGPT-6 Astra to produce Lean proofs for all results in the paper; the repo links existing numbered statements in paper.tex to Lean declarations post-hoc via claims.json and render_correspondence.py without leanblueprint, LeanArchitect, or Challenge/Solution spec-lock tooling.
- **Risk flags:** ['Mode10_ProofBloat']
- **Repo `gadiluna/ADDN_lean`:** `.lean` files=2104, LoC=158351, theorems=6418, defs=6005, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.0`, ci=`[]`

#### [2611.15431](https://arxiv.org/abs/2611.15431) — Subadditivity and the failure of strong subadditivity in the Nichols--Wootters family of entropies
- **Paradigm:** `P0_opaque_or_unspecified` (`high`) | **Tier:** `Tier1_Bronze` | **AI:** `explicitly_yes` (['ChatGPT Pro (GPT-6 Pro)', 'Codex (gpt-6.1-sol)', 'Claude Opus 5.5', 'Claude Code'])
- **Evidence:** Acknowledgments state that AI tools (ChatGPT Pro / GPT-6 Pro, Codex / gpt-6.1-sol, and Claude Opus 5.5 via Claude Code) were used for 'double-checking, including formal verification of the results in Lean', and mention a 'verification package' for computations, but urls, repos, and local_repo_dirs are all empty and no Lean authoring workflow or scope details are provided.
- **Risk flags:** ['Mode12_ProcessOpacity']

## 5. Beyond-Lean Formal Verification Baseline

- **Candidate triage:** {'citation_or_discussion': 19, 'formal_contributed': 12, 'false_positive': 3}
- **Tool categories (contributed):** {'ITP': 5, 'model_checker': 4, 'smt_sat': 2, 'protocol_verifier': 1}

| Formal Tool | Papers Contributing |
| :--- | ---: |
| `Coq/Rocq` | 2 |
| `Z3` | 2 |
| `PRISM` | 2 |
| `Isabelle/HOL` | 2 |
| `TLA+` | 2 |
| `SPIN` | 1 |
| `Promela` | 1 |
| `nuXmv` | 1 |
| `NuSMV` | 1 |
| `ROCQ` | 1 |
| `Coq` | 1 |
| `Tamarin` | 1 |
| `Rocq` | 1 |
| `Rocq / Coq` | 1 |
| `TLAPS` | 1 |
| `tla_plus` | 1 |

### Confirmed Beyond-Lean Papers

- **[2611.23811](https://arxiv.org/abs/2611.23811)** (`cs.DC`, `ITP`, tools=['Coq/Rocq']): Stephen: Verifying Sequencer-Aided Coordination Systems with Cross-View Prophecy — The paper formally verifies implementations of sequencer-aided coordination systems (NOPaxos, Corfu, LazyLog) using machine-checked proofs in Rocq/Grove.
- **[2611.23021](https://arxiv.org/abs/2611.23021)** (`eess.SY`, `smt_sat`, tools=['Z3']): Satisfiability Modulo Theories for Robust Synthesis of Signal Temporal Logic Specifications — Introduces a Satisfiability Modulo Theories (SMT) based encoding and synthesis method for Signal Temporal Logic (STL) specifications in robotic systems.
- **[2611.22408](https://arxiv.org/abs/2611.22408)** (`cs.CR`, `model_checker`, tools=['SPIN', 'Promela']): From Attack Tree to Model Checker: Binding CAPEC Patterns to Verify Robotic System Security — The paper presents a pipeline that mechanises the transition from CAPEC attack patterns to formal attacker models, emitting LTL properties and Promela models verified using SPIN.
- **[2611.22403](https://arxiv.org/abs/2611.22403)** (`cs.SE`, `model_checker`, tools=['nuXmv', 'NuSMV', 'ROCQ', 'Coq']): BehaVerify: A Formal Verification Tool for Behavior Trees — BehaVerify presents a verification toolbox for behavior trees that encodes into nuXmv for formal verification and incorporates tools like ROCQ.
- **[2611.20671](https://arxiv.org/abs/2611.20671)** (`cs.CR`, `protocol_verifier`, tools=['Tamarin']): MASTA: A Feedback-Scheduled Multi-Agent System for End-to-End Tamarin Modeling and Analysis — MASTA uses a multi-agent system to end-to-end model and verify security protocols using the Tamarin theorem prover.
- **[2611.18463](https://arxiv.org/abs/2611.18463)** (`cs.CR`, `ITP`, tools=['Rocq']): VellSSLH: Sound Type-Guided Selective Speculative Load Hardening for LLVM IR — VellSSLH: Sound Type-Guided Selective Speculative Load Hardening for LLVM IR, mechanized and proved in Rocq.
- **[2611.18055](https://arxiv.org/abs/2611.18055)** (`cs.PL`, `ITP`, tools=['Coq/Rocq']): DeCompCert: A Verified Decompiler for CompCert-Generated AArch64 — DeCompCert is a Rocq-verified decompiler for AArch64 assembly generated by CompCert.
- **[2611.12252](https://arxiv.org/abs/2611.12252)** (`cs.CR`, `model_checker`, tools=['PRISM']): Lessons Not Learned: Why Cross-Chain Bridges Keep Losing Billions the Same Way — The paper compiles security posture and rate-limit models into the PRISM model checker to perform exhaustive state-space search and bound bridge hack losses.
- **[2611.11506](https://arxiv.org/abs/2611.11506)** (`cs.CR`, `ITP`, tools=['Isabelle/HOL']): On the Relative Security of Prompt Injection: Mechanised Definitions, Defences and Verdicts for LLM Agents — Mechanised definitions, defences and verdicts for LLM agents proven or refuted in Isabelle/HOL.
- **[2611.07919](https://arxiv.org/abs/2611.07919)** (`cs.DC`, `smt_sat`, tools=['Z3']): Modular Parameterized Model Checking of Threshold-Based Distributed Algorithms — The paper introduces a modular parameterized model checking approach for threshold-based distributed algorithms, implemented and evaluated using the Z3 SMT solver.
- **[2611.05695](https://arxiv.org/abs/2611.05695)** (`cs.PL`, `ITP`, tools=['Rocq / Coq']): Demystifying Information Flow Downgrading using the Real--Ideal Paradigm — Demystifies information flow downgrading using the real-ideal paradigm and fully formalizes the results using the Rocq theorem prover.
- **[2611.02858](https://arxiv.org/abs/2611.02858)** (`cs.CR`, `model_checker`, tools=['PRISM']): Evaluating autonomous self-healing against persistent cyber-attacks — The paper uses the PRISM model checker to calculate steady-state probabilities and evaluate autonomous self-healing against cyber-attacks.