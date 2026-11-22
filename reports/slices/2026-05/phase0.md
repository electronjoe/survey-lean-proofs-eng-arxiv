# Phase 0 Deterministic Probe Summary

- **Date window (submitted):** `2026-05-01T00:05:54Z` to `2026-05-19T23:51:23Z`
- **Total unique papers ingested:** 3298
- **Total papers screened:** 3298 (`html`: 3141, `pdf`: 147, `failed`: 10)
- **Lean strong hits (full text):** 15 *(vs. metadata-only: 5)*
- **Lean contextual-only hits:** 4
- **Confirmed public Lean GitHub repos found:** 6

## Breakdown by Target arXiv Category

| Category | Papers | Lean Strong | Lean Ctx | Other ITP | Model Checker | Protocol Verifier | SMT/SAT |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cs.CR` | 685 | 8 | 9 | 9 | 7 | 5 | 9 |
| `cs.DC` | 315 | 3 | 3 | 1 | 4 | 0 | 3 |
| `cs.IT` | 327 | 1 | 2 | 0 | 0 | 0 | 0 |
| `cs.NI` | 227 | 0 | 0 | 0 | 0 | 0 | 0 |
| `cs.RO` | 740 | 0 | 0 | 1 | 0 | 0 | 2 |
| `eess.SP` | 419 | 1 | 1 | 0 | 0 | 0 | 0 |
| `eess.SY` | 456 | 1 | 1 | 1 | 1 | 0 | 6 |
| `math.OC` | 512 | 2 | 3 | 2 | 0 | 0 | 3 |

## Beyond-Lean Tool Counts (Deterministic Full-Text Hits)

| Group : Tool | Papers |
| :--- | ---: |
| `smt_sat:smt_general` | 23 |
| `itp:coq_rocq` | 9 |
| `smt_sat:z3_cvc` | 8 |
| `model_checker:tla_plus` | 6 |
| `model_checker:cbmc_esbmc` | 5 |
| `itp:dafny` | 5 |
| `itp:why3_framac` | 3 |
| `protocol_verifier:easycrypt` | 3 |
| `protocol_verifier:proverif` | 3 |
| `model_checker:spin_promela` | 2 |
| `itp:hol_light_hol4` | 1 |
| `model_checker:nusmv_nuxmv` | 1 |
| `protocol_verifier:tamarin` | 1 |
| `itp:isabelle` | 1 |

## Lean Strong Hits (15 papers)

### [2605.19742](https://arxiv.org/abs/2605.19742) — The Privacy Subsidy in Glosten-Milgrom: Bid-Ask Spread and Welfare under Flip-Noise Direction Observation
- **Primary / Target Cats:** `cs.GT` / ['cs.CR'] | **Submitted:** `2026-05-19` | **Source:** `html`
- **Comment:** 10 pages. Companion to arXiv:2605.15746
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 5, 'tex_files_chars': 26491}`
  - *lean_version:* `ysis would connect to LVR via repeated GM rounds and may yield a discrete analog of the additive LVR-plus-privacy decomposition conjectured in [11]. Mechanism design with endogenous treats the exchange designer’s privacy-utility trade-off. Lean 4 mechanization of the closed-form results across the cluster is a natural `

### [2605.19531](https://arxiv.org/abs/2605.19531) — Conflict-Freedom as a Progress Condition
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Submitted:** `2026-05-19` | **Source:** `html`
- **Comment:** 24 pages, 2 figures. This is an extended version of a conference article. The conference version of this article appears in the proceedings of the 2026 ACM Symposium on Principles of Distributed Computing (PODC'26)
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 14, 'agent_tools': ['Claude'], 'tex_files_chars': 145785}`
- **Artifact URLs:** https://dx.doi.org/10.5281/zenodo.23098310
- **Lean Repo `zenodo/23098310`:** `.lean` files=101, LoC=34257, theorems=2061, defs=761, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.0`, ci=`[]`
  - *lean_version:* `nto a conflict-free one using a helping mechanism. We conclude the paper with ramifications and open questions in Section 8. Detailed proofs are delegated to Appendix A. The model and results presented in this work have been formalized in Lean 4, available at (Toyos-Marfurt, 2026). In particular, every numbered lemma, `
  - *lean_prover_phrase:* `f the ACM SIGOPS 28th Symposium on Operating Systems Principles, SOSP ’21, New York, NY, USA, pp. 1–17. External Links: ISBN 9781450387095 Cited by: §2. Toyos-Marfurt (2026) G. Toyos-Marfurt Conflict freedom as a progress condition: a lean formalization. Zenodo. External Links: Document Cited by: §1. Whittaker et al. (`
  - *in_lean_phrase:* `an be turned into a conflict-free one using a helping mechanism. We conclude the paper with ramifications and open questions in Section 8. Detailed proofs are delegated to Appendix A. The model and results presented in this work have been formalized in Lean 4, available at (Toyos-Marfurt, 2026). In particular, every nu`

### [2605.17255](https://arxiv.org/abs/2605.17255) — CAM-Bench: A Benchmark for Computational and Applied Mathematics in Lean
- **Primary / Target Cats:** `cs.AI` / ['math.OC'] | **Submitted:** `2026-05-17` | **Source:** `html`
- **Comment:** Preprint. 44 pages, 7 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_verifiers', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'agent_tools': ['Aristotle', 'Claude', 'Deepseek', 'GPT-5', 'Gemini', 'aristotle', 'claude', 'deepseek', 'gemini', 'gpt-5'], 'tex_files_chars': 169586}`
- **Artifact URLs:** https://github.com/optpku/CAM-Bench, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
- **Lean Repo `optpku/CAM-Bench`:** `.lean` files=780, LoC=34332, theorems=1008, defs=2441, sorry=1000, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.28.0`, ci=`[]`
  - *lean_version:* `ation of mathematical reasoning in large language models. However, existing benchmarks mainly focus on Olympiad-style problems and algebraic domains, leaving computational and applied mathematics underrepresented. We introduce CAM-Bench, a Lean 4 theorem-proving benchmark of 1,000 Lean proof targets in computational an`
  - *mathlib:* `rem, and final Lean target. CAM-Bench complements existing formal mathematics benchmarks by targeting applied mathematics problems that rely on textbook concepts and elementary theorems, many of which are not directly available as standard Mathlib4 lemmas. We evaluate widely used large language models and formalization`
  - *lean_verifiers:* `n instance is counted as solved only if it is completed within 8 hours, the returned Lean project recompiles locally, preserves the original theorem statements and existing definitions, and contains no pseudo-proof artifacts such as sorry, sorryAx, admit, axiom, or unresolved exact?. Agent performance. Under this proto`

### [2605.14859](https://arxiv.org/abs/2605.14859) — Do Coding Agents Understand Least-Privilege Authorization?
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-05-14` | **Source:** `html`
- **Matched Lean Signals:** `['mathlib']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Codex', 'GPT-5', 'Gemini'], 'tex_files_chars': 114362}`
- **Artifact URLs:** https://github.com/evolvent-ai/Authbench, https://github.com/open-thoughts/OpenThoughts-TBLite, https://github.com/open-thoughts/OpenThoughts-TBLiteGitHub
  - *mathlib:* `naries rather than the deeper compiler subprocess tree that the chosen path actually requires. How the Policy Was Derived. GPT-5 begins on the correct abstraction layer. The trace models the task as reading the C sources under /workspace/mathlib, compiling object files, archiving them into libmath.a, linking and runnin`

### [2605.14610](https://arxiv.org/abs/2605.14610) — Parametrically Adaptive Transition Polynomial: a Signed-Parity Continuous-alpha Extension of Kunchenko Stochastic Polynomials
- **Primary / Target Cats:** `stat.ME` / ['eess.SP'] | **Submitted:** `2026-05-14` | **Source:** `html`
- **Comment:** 41 pages, 10 figures. Code and Lean 4 proofs: https://github.com/SZabolotnii/Ku-PATP-code-supplement
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 4, 'agent_tools': ['Claude'], 'tex_files_chars': 145828}`
- **Artifact URLs:** https://github.com/SZabolotnii/Ku-PATP-code-supplement
- **Lean Repo `SZabolotnii/Ku-PATP-code-supplement`:** `.lean` files=8, LoC=473, theorems=25, defs=11, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.26.0`, ci=`[]`
  - *lean_version:* `llustrations on canonical distributions are used to examine the finite-sample behavior of the signed-parity estimator and to mark the boundary of applicability for extremely heavy-tailed cases such as Cauchy. 41 pages, 10 figures. Code and Lean 4 proofs: https://github.com/SZabolotnii/Ku-PATP-code-supplement Parametric`
  - *mathlib:* `). Software stack. R , base stats, plus dplyr, tidyr, ggplot2 for tabulation and figures. No external PATP package is needed at runtime; all PMM routines are vendored in R/. The Lean 4 formalization referenced in Appendix A.2 builds with Mathlib v4.26.0 via lake build in the same repository. One-line recipe. git clone `
  - *lean_prover_phrase:* `mar, punctuation, and stylistic suggestions) was used during manuscript preparation, and the AI coding assistant Claude Code (Anthropic) was used to help write and debug the accompanying R pipeline. All scientific content, derivations, and Lean proofs are the author’s own work, and the author has verified and takes ful`

### [2605.16407](https://arxiv.org/abs/2605.16407) — Proof-Carrying Certificates for LLM Pipelines: A Trust-Boundary Architecture
- **Primary / Target Cats:** `cs.LO` / ['cs.CR'] | **Submitted:** `2026-05-13` | **Source:** `html`
- **Comment:** 83 pages, 1 figure, 12 tables
- **Matched Lean Signals:** `['lakefile', 'lean_prover_phrase', 'lean_verifiers', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 10, 'agent_tools': ['Claude', 'GPT-5', 'Gemini', 'claude', 'gemini', 'gpt-5'], 'tex_files_chars': 268158}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.20144139, https://doi.org/10.5281/zenodo.20144140, https://github.com/gkoomullil/proof-carrying-certificates
- **Lean Repo `zenodo/20144139`:** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Lean Repo `zenodo/20144140`:** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Lean Repo `gkoomullil/proof-carrying-certificates`:** `.lean` files=25, LoC=2381, theorems=46, defs=138, sorry=0, axiom=18, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
  - *lean_version:* `Proof-Carrying Certificates for LLM Pipelines: A Trust-Boundary Architecture We present a framework for verifying the deterministic structured computations surrounding a large language model rather than the model itself, extending a Lean 4 trust-boundary architecture to the generic interfaces of modern LLM pipelines. C`
  - *mathlib:* `orm the per-call deliverable for high-stakes deployments: patent and legal retrieval, regulated finance, clinical decision support, and agentic systems with irreversible side effects. A compiled Lean 4 reference artifact (Lean v4.30.0-rc2, Mathlib) covers all 22 certificate types, with 17 of 46 kernel-audited declarati`
  - *leanprover:* `Artifact archive. The archive layout is lean_artifact/ (the compiled Lean 4 project) and pilot_a/, pilot_b/, pilot_c/ (one self-contained Python project per pilot, with Pilot B′ co-located in pilot_b/). Lean 4 artifact pins. Toolchain: leanprover/lean4:v4.30.0-rc2 (recorded in lean_artifact/lean-toolchain). Mathlib com`

### [2605.15219](https://arxiv.org/abs/2605.15219) — NOVA: Fundamental Limits of Knowledge Discovery Through AI
- **Primary / Target Cats:** `cs.AI` / ['cs.IT'] | **Submitted:** `2026-05-12` | **Source:** `html`
- **Comment:** Added an explicit recursive retraining model showing how accepted outputs reshape future generation. New results characterize when repeated retraining suppresses undiscovered artifacts and when mixing updates with a fixed base distribution preserves exposure. Corrected the Zipf discovery-cost proof and expanded the analysis. Main results and implications remain unchanged
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 21, 'agent_tools': ['AlphaProof', 'DeepSeek'], 'tex_files_chars': 116751}`
  - *lean_version:* `by: §1.2, §1. Appendix A Motivating Examples Example 1: Discovering new mathematical proofs. Consider as the set of valid formal proofs of mathematical conjectures. A language model generates candidate proofs in a formal language (e.g., Lean 4). The verification step is performed by a proof assistant: the Lean type-che`

### [2605.11522](https://arxiv.org/abs/2605.11522) — State Twins: An Off-Chain Substrate for Agentic Reasoning over Decentralized Finance Protocols
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Submitted:** `2026-05-12` | **Source:** `html`
- **Comment:** 14 pages, 1 table, 7 listings; reference implementation at https://github.com/defipy-devs/defipy
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 1, 'agent_tools': ['Claude'], 'tex_files_chars': 67747}`
- **Artifact URLs:** https://github.com/defipy-devs/defipy, https://github.com/mds1/multicall
  - *lean_version:* `re complementary: their work targets exhaustive correctness verification of pool dynamics, ours targets agentic reasoning over an off-chain typed substrate that inherits their bound. Earlier theorem-proving work on constant-product AMMs in Lean 4 [5] addresses correctness in a similar formal-methods spirit but for the `

### [2605.09552](https://arxiv.org/abs/2605.09552) — Phases of Muon: When Muon Eclipses SignSGD
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-05-10` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 44, 'agent_tools': ['DeepSeek', 'Deepseek', 'Harmonic', 'harmonic'], 'tex_files_chars': 1067397}`
- **Artifact URLs:** http://github.com/google-deepmind, http://github.com/google/jax, https://github.com/mlexpos/alea-foundations, https://github.com/mlexpos/phases-of-muon
- **Lean Repo `mlexpos/alea-foundations`:** `.lean` files=30, LoC=14553, theorems=647, defs=53, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
- **Lean Repo `mlexpos/phases-of-muon`:** `.lean` files=148, LoC=340325, theorems=12371, defs=1348, sorry=1, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
  - *lean_version:* `e analysis with momentum and a complete proof of the dynamical comparison between the algorithm and its deterministic dynamics. The resulting appendix was audited for style and correctness. Its statements and proofs were then formalized in Lean 4 with Mathlib and checked by machine, using standard results proved in the`
  - *mathlib:* `ith momentum and a complete proof of the dynamical comparison between the algorithm and its deterministic dynamics. The resulting appendix was audited for style and correctness. Its statements and proofs were then formalized in Lean 4 with Mathlib and checked by machine, using standard results proved in the accompanyin`
  - *lean_prover_phrase:* `ation, for example to solve the deterministic equivalent. Proofs and code. The accompanying website provides interactive access to the statements, proof sketches and complete written proofs: https://mlexpos.github.io/phases-of-muon/. The Lean formalization is available at https://github.com/mlexpos/phases-of-muon, with`

### [2605.05801](https://arxiv.org/abs/2605.05801) — Self-Correcting Gossip Protocols
- **Primary / Target Cats:** `cs.LO` / ['cs.DC'] | **Submitted:** `2026-05-07` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'lean_macro': 20, 'theorem_envs': 14, 'agent_tools': ['Aristotle'], 'tex_files_chars': 157967}`
  - *lean_version:* `ssip in Lean. [22] Y. Moses and M.R. Tuttle (1988) Programming simultaneous actions using common knowledge. Algorithmica 3, pp. 121–169. External Links: Document Cited by: §1, §3.2, §3, §3. [23] L. d. Moura and S. Ullrich (2021) The Lean 4 Theorem Prover and Programming Language. In Automated Deduction – CADE 28, pp. 6`
  - *mathlib:* `ted by: §1, §2.1. [20] R. Kuznets, L. Prosperi, U. Schmid, and K. Fruzsa (2019) Epistemic reasoning with Byzantine-faulty agents. In Proc. of 12th FroCoS, pp. 259–276. Note: LNCS 11715 External Links: Document Cited by: §1. [21] T. mathlib Community (2020) The Lean mathematical library. In Proc. of 9th CPP, pp. 367–381`
  - *in_lean_phrase:* `) ⟹ (((b,k) @ b) ⋀ ((b,k) @ a) ⋀ (¬’(b, !k) @ a)) /– Corollary 14 -/ lemma knowledge_is_justified_true_belief {n} {a b : @Agent n} : ⊨ K a ((b,k) @ b) ⇔ K a ( ((b,k) @ b) ⋀ ((b,k) @ a) ⋀ (¬’ (b, !k) @ a)) Figure 2: Overview of results proven in Lean (with links to documentation). Experimental support, please view the b`

### [2605.03822](https://arxiv.org/abs/2605.03822) — KVerus: Scalable and Resilient Formal Verification Proof Generation for Rust Code
- **Primary / Target Cats:** `cs.SE` / ['cs.CR'] | **Submitted:** `2026-05-05` | **Source:** `html`
- **Comment:** Accepted at ASE 2026
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'cursor'], 'tex_files_chars': 73712}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.19937769, https://github.com/asterinas/KVerus, https://github.com/endorlabs/MIRAI, https://github.com/langchain-ai/langchain, https://github.com/rikosellic/verus-mathspec-bench
  - *lean_version:* `CortenMM. Verus-Bench was introduced by AutoVerus, whereas MBPP and Human-Eval were used by AlphaVerus. MathSpec-Bench22 2 https://github.com/rikosellic/verus-mathspec-bench is derived by translating mathematical developments from Lean 4 into Verus and is designed to stress lemma reuse and cross-module reasoning. Memor`

### [2605.03034](https://arxiv.org/abs/2605.03034) — Stable Agentic Control: Tool-Mediated LLM Architecture for Autonomous Cyber Defense
- **Primary / Target Cats:** `cs.AI` / ['cs.CR', 'eess.SY'] | **Submitted:** `2026-05-04` | **Source:** `html`
- **Comment:** 23 pages total (9 main paper + 16 appendices/references), 2 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 3, 'agent_tools': ['Claude', 'claude'], 'tex_files_chars': 84195}`
- **Artifact URLs:** https://github.com/Orange-Cyberdefense/GOAD, https://github.com/tsale/EDR-Telemetry, https://github.com/tsale/EDR-TelemetryCommunity-maintained
  - *lean_version:* `M agents use deterministic tools (Stackelberg best-response, Bayesian observer updates, attack-graph primitives) and select from finite action catalogs enforced at the tool-output interface. A composite Lyapunov function machine-checked in Lean 4 with zero sorry certifies controllability, observability from asymmetric `
  - *mathlib:* `com/en-us/defender-endpoint/linux-preferencesAccessed: 2026-04-27 Cited by: §C.1. Appendix A Formal Verification of Closed-Loop Stability We formally verify the stability guarantees of Theorem 1 using the Lean 4 proof assistant with the Mathlib mathematical library. The complete Lean source (five files, lines) is inclu`
  - *leanprover:* `quire encoding the finite catalog and diminishing-returns structure. A.3 Reproducing the Verification The Lean 4 project is included in the supplementary materials. To verify: Install elan: curl -sSf \ https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh Build: cd ClosedLoopStability lake update &`

### [2605.02856](https://arxiv.org/abs/2605.02856) — The 1-Bit Barrier is Universal: k-Stage Pipeline Composition and Unified Leakage Bounds for Standard Modular Reductions in PQC Hardware
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-05-04` | **Source:** `pdf`
- **Comment:** 30 pages, 0 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lakefile', 'lean_verifiers', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'tex_files_chars': 457138}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.19508454, https://doi.org/10.5281/zenodo.19625392, https://doi.org/10.5281/zenodo.19689480, https://doi.org/10.5281/zenodo.19705450, https://github.com/chipsalliance/caliptra-rtl/blob/main/Release_Notes.md
- **Lean Repo `zenodo/19689480`:** `.lean` files=8, LoC=451, theorems=16, defs=8, sorry=0, axiom=0, native_decide=1, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`
- **Lean Repo `zenodo/19705450`:** `.lean` files=5, LoC=494, theorems=11, defs=19, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`
- **Lean Repo `rayiskander2406/qanary-k-stage-composition-arXiv-2605.02856`:** `.lean` files=7, LoC=749, theorems=17, defs=4, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc1`, ci=`[]`
  - *lean_version:* `Arbitrary-depth $k$-stage masked NTT pipelines with fresh inter-stage masking and per-stage PF-PINI($\leq 2$) gadgets satisfy a per-observation cardinality bound of $2 \cdot q^{2k-2}$ on the preimage of any output value, machine-checked in Lean 4 with zero \texttt{sorry}. Under the standard (informal) semantic translat`
  - *mathlib:* `the MIT license: • Repository: https://github.com/rayiskander2406/qanary-k-stage-composition-arXiv- 2605.02856 (MIT, public). Zenodo DOI: 10.5281/zenodo.20041713. • Toolchain: Lean 4 v4.30.0-rc1 (managed via elan). • Pinned dependency: Mathlib at commit 322515540d7fd29ef8992b82c89044f86f02ac10. • License: MIT (artifact`
  - *leanprover:* `tion sanity checks and is not part of the exported proof surface. lakefile.lean, lake-manifest.json Build configuration with pinned Mathlib and four sibling-repo dependencies (Papers 3, 4, 5, 6). 27 Path Purpose lean-toolchain Pins leanprover/lean4:v4.30.0-rc1. LICENSE, CITATION.cff, .zenodo.json MIT license, machine-r`

### [2605.01047](https://arxiv.org/abs/2605.01047) — LLM Ghostbusters: Surgical Package Hallucination Suppression via Adaptive Unlearning
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-05-01` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'DeepSeek', 'Deepseek', 'GPT-5', 'Gemini', 'claude', 'deepseek'], 'tex_files_chars': 129401}`
  - *lean_prover_phrase:* `ksandr Churilov. The range shrinks, the threat remains: Re-evaluating LLM package hallucinations on the 2026 frontier-model cohort, 2026. [10] Leonardo de Moura, Soonho Kong, Jeremy Avigad, Floris van Doorn, and Jakob von Raumer. The Lean Theorem Prover (System Description). In Automated Deduction — CADE-25, volume 919`

### [2605.00487](https://arxiv.org/abs/2605.00487) — Zero-Knowledge Model Checking
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-05-01` | **Source:** `pdf`
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 3, 'tex_files_chars': 115080}`
- **Artifact URLs:** https://github.com/aiverification/zkmc, https://github.com/maidsafe/bls_, https://github.com/maidsafe/bls_bulletproofs
  - *lean_version:* `eichle. Efficient range proofs with transparent setup from bounded integer commitments. In EURO- CRYPT (3), volume 12698 of Lecture Notes in Computer Science, pages 247–277. Springer, 2021. [22] Leonardo de Moura and Sebastian Ullrich. The Lean 4 theorem prover and programming language. In CADE, volume 12699 of Lecture`

## Lean Contextual-Only Hits (4 papers — review for recall)

- **[2605.10401](https://arxiv.org/abs/2605.10401)** (`cs.AI`) LLM4Branch: Large Language Model for Discovering Efficient Branching Policies of Integer Programs — `ance guarantees for branching policies remains extremely difficult due to the NP-hard nature of the problem. To move toward deeper scientific discovery, future work could explore the integration of formal verification environments, such as `
- **[2605.16379](https://arxiv.org/abs/2605.16379)** (`cs.LG`) An Information-Theoretic Criterion for Efficient Data Synthesis — `aGeometry teams, 2024), and AlphaGeometry-style constrained synthesis reaches gold-medalist-level geometry solving (Trinh et al., 2024; Chervonyi et al., 2025). In formal proving, similar recipes scale to strong benchmark performance under `
- **[2605.03309](https://arxiv.org/abs/2605.03309)** (`cs.CR`) Cryptographic Registry Provenance: Structural Defense Against Dependency Confusion in AI Package Ecosystems — `egistry identity; the transparency log proves the publication was publicly witnessed. Formal verification of the verification chain. The six-level verification chain’s security properties (Theorems 7.3–9.3) could be mechanized in Rocq or Le`
- **[2605.01037](https://arxiv.org/abs/2605.01037)** (`cs.CR`) Certified Purity for Cognitive Workflow Executors: From Static Analysis to Cryptographic Attestation — `de for key algorithms and analysis of the build pipeline. Scope of “certified.” The term certified purity refers to the runtime certification gate’s mechanical check of purity certificates, not to mechanized proof in the sense of Rocq or Le`
