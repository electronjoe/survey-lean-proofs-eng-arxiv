# Phase 0 Deterministic Probe Summary

- **Date window (submitted):** `2026-11-01T00:01:01Z` to `2026-11-19T18:58:31Z`
- **Total unique papers ingested:** 4104
- **Total papers screened:** 4104 (`html`: 3849, `pdf`: 248, `failed`: 7)
- **Lean strong hits (full text):** 47 *(vs. metadata-only: 16)*
- **Lean contextual-only hits:** 8
- **Confirmed public Lean GitHub repos found:** 28

## Breakdown by Target arXiv Category

| Category | Papers | Lean Strong | Lean Ctx | Other ITP | Model Checker | Protocol Verifier | SMT/SAT |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cs.CR` | 629 | 12 | 13 | 9 | 6 | 6 | 6 |
| `cs.DC` | 335 | 7 | 8 | 5 | 4 | 0 | 2 |
| `cs.IT` | 338 | 5 | 6 | 0 | 0 | 0 | 0 |
| `cs.NI` | 196 | 0 | 0 | 0 | 0 | 0 | 0 |
| `cs.RO` | 1159 | 0 | 1 | 1 | 2 | 0 | 2 |
| `eess.SP` | 462 | 0 | 0 | 0 | 0 | 0 | 0 |
| `eess.SY` | 738 | 3 | 3 | 2 | 0 | 0 | 6 |
| `math.OC` | 724 | 22 | 24 | 2 | 0 | 0 | 7 |

## Beyond-Lean Tool Counts (Deterministic Full-Text Hits)

| Group : Tool | Papers |
| :--- | ---: |
| `smt_sat:smt_general` | 19 |
| `itp:coq_rocq` | 15 |
| `protocol_verifier:tamarin` | 6 |
| `smt_sat:z3_cvc` | 5 |
| `itp:isabelle` | 4 |
| `model_checker:tla_plus` | 4 |
| `itp:dafny` | 3 |
| `model_checker:prism_storm` | 3 |
| `model_checker:nusmv_nuxmv` | 2 |
| `protocol_verifier:proverif` | 2 |
| `itp:hol_light_hol4` | 2 |
| `model_checker:spin_promela` | 1 |
| `protocol_verifier:easycrypt` | 1 |
| `model_checker:cbmc_esbmc` | 1 |

## Lean Strong Hits (47 papers)

### [2611.26272](https://arxiv.org/abs/2611.26272) — Paper2Lean: Agentic Autoformalization of Mathematical Research Papers at Scale
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-19` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Codex', 'DeepSeek', 'Deepseek', 'GPT-5', 'Kimina', 'deepseek', 'gpt-5'], 'tex_files_chars': 119026}`
- **Artifact URLs:** https://github.com/TTony2019/OptPaper, https://github.com/anthropics/fermats-last-theorem, https://github.com/cameronfreer/lean4-skills, https://github.com/deepseek-ai/deepseek-harness, https://github.com/oOo0oOo/lean-lsp-mcp
- **Lean Repo `TTony2019/OptPaper`:** `.lean` files=558, LoC=151214, theorems=3398, defs=724, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0-rc2`, ci=`[]`
- **Lean Repo `anthropics/fermats-last-theorem`:** `.lean` files=60478, LoC=11880614, theorems=598184, defs=95596, sorry=2, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`[]`
- **Lean Repo `cameronfreer/lean4-skills`:** `.lean` files=66, LoC=1442, theorems=56, defs=96, sorry=0, axiom=4, native_decide=1, unsafe=2, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`['print axioms']`
- **Lean Repo `oOo0oOo/lean-lsp-mcp`:** `.lean` files=20, LoC=123, theorems=23, defs=19, sorry=3, axiom=0, native_decide=0, unsafe=1, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['lake build']`
  - *lean_version:* `adient-like dissipative dynamical system with hessian-driven damping.: Application to optimization and mechanics. Journal de mathématiques pures et appliquées, 81(8):747–779, 2002. Anthropic (2026) Anthropic. Fermat’s last theorem in Lean 4. https://github.com/anthropics/fermats-last-theorem, September 2026. Complete m`
  - *mathlib:* `nto a dependency graph and coordinates specialized agents for statement formalization, semantic checking and repair, proof construction, and project integration. We evaluate Paper2Lean on 20 mathematical optimization research papers, using mathlib and a shared library of supporting results. All 20 automatically generat`
  - *leanprover:* `l the agents interact with Lean through Lean LSP MCP 22 2 https://github.com/oOo0oOo/lean-lsp-mcp, which provides compiler feedback, goal-state inspection, and semantic search capabilities. All formalizations use the Lean toolchain leanprover/lean4:v4.30.0-rc2. Research papers in optimization often rely on substantial `

### [2611.26140](https://arxiv.org/abs/2611.26140) — Optimal Patrol Widths in the Infinite-Corridor Barrier-Guarding Game
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-19` | **Source:** `html`
- **Comment:** 34 pages, 2 figures. Exact rational Python verifiers and a Lean 4 library for selected lemmas and finite certificates accompany the submission
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 25, 'agent_tools': ['Antigravity', 'Claude', 'Codex', 'Gemini'], 'tex_files_chars': 124283}`
  - *lean_version:* `er than $(2/q-1.235353)r$ throughout $0 < q\le1/40$. Rational spacetime and flux certificates give finite-speed bounds, including $6.944691333740r < W_{\mathrm{opt}}(1/4)\le8.10r$. 34 pages, 2 figures. Exact rational Python verifiers and a Lean 4 library for selected lemmas and finite certificates accompany the submiss`
  - *mathlib:* `s. Their entry points and hypotheses are indexed in anc/README.md. The finite checks complement the arguments on paper that turn capture surfaces, time budgets and clearance into statements about every transit. The accompanying Lean 4 and Mathlib v4.15.0 library contains the wall-budget algebra, selected phase and fan `

### [2611.25599](https://arxiv.org/abs/2611.25599) — Tether: Verified Stateful Policy Engine for System-Level Monitoring of Agents
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-19` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Codex', 'Gemini'], 'tex_files_chars': 186976}`
- **Artifact URLs:** https://github.com/UKGovernmentBEIS/control-arena, https://github.com/atlas-brown/sash, https://github.com/safety-research/red-teaming-auto-mode
  - *lean_version:* `semantics from observed system calls. Tether then enforces stateful policies over these inferred semantics, permitting actions to proceed only if they comply with the policy. Policies and action semantics are defined in an embedded DSL in Lean 4 capable of expressing diverse constraints, including information flow cont`
  - *in_lean_phrase:* `users can define verification queries (Fig. 5) and prove (or disprove with a counterexample) that the intended invariants hold. Using this mechanism, we verify the invariants in Tab. 1 for the benchmark policy. Table 1: Safety invariants proved in Lean 4 for the benchmark policy of §6, for any initial state and any abs`

### [2611.25174](https://arxiv.org/abs/2611.25174) — Formally Verified Semidefinite Programming
- **Primary / Target Cats:** `cs.SE` / ['math.OC'] | **Submitted:** `2026-11-18` | **Source:** `html`
- **Comment:** 9 pages. Comments welcome
- **Matched Lean Signals:** `['mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 1, 'agent_tools': ['Claude', 'Codex'], 'tex_files_chars': 58311}`
- **Artifact URLs:** https://github.com/PHart3/convopt-rust/tree/verus-v1.0.0
  - *mathlib:* `as small KKT residuals. Ours appears to be the first verified implementation of an SDP solver. Surprisingly, it also appears to offer the first verified implementation of spectral decomposition for real symmetric matrices, although Lean’s mathlib includes the spectral theorem, in noncomputable form, for Hermitian matri`

### [2611.23762](https://arxiv.org/abs/2611.23762) — Addressable transversal CCZ gates on almost good quantum LDPC codes and nearly optimal magic state protocols
- **Primary / Target Cats:** `quant-ph` / ['cs.IT'] | **Submitted:** `2026-11-18` | **Source:** `html`
- **Comment:** 69 pages + Appendices
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 62, 'agent_tools': ['Claude'], 'tex_files_chars': 318437}`
- **Artifact URLs:** https://github.com/guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification/
- **Lean Repo `guanyuzhu2014/Uniform-product-expansion---theory-and-Lean-certification`:** `.lean` files=1, LoC=589, theorems=36, defs=5, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
  - *lean_prover_phrase:* `preparation [87].11 1 The proof was generated entirely using AI and is available in the companion repository, together with Lean formalizations of selected algebraic lemmas. We are revising the exposition and extending the Lean formalization, which does not yet cover the full argument. We note that Bafna and Vyas formu`

### [2611.23080](https://arxiv.org/abs/2611.23080) — Colombo: A Frontier-to-Frontier Autoresearch System for Oracle-Based Optimization
- **Primary / Target Cats:** `cs.AI` / ['math.OC'] | **Submitted:** `2026-11-17` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'agent_tools': ['GPT-5'], 'tex_files_chars': 173637}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.23438699
  - *lean_prover_phrase:* `mplexity Bracket and triggers a new research round, with the review findings serving as additional evidence for targeted replanning. A package that passes independent natural-language review proceeds to Formal Certification. Findings from Lean formalization or semantic-alignment review are returned to the Brain in stru`

### [2611.22732](https://arxiv.org/abs/2611.22732) — Provable Mixing Properties of Parallel Mixnets Revisited
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-17` | **Source:** `html`
- **Comment:** 16 pages, 3 figures, 2 pages of appendix
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 12, 'agent_tools': ['Claude', 'Gemini'], 'tex_files_chars': 117993}`
  - *lean_prover_phrase:* `Claude, ChatGPT and Gemini, were used to revise the text to eliminate typos, grammatical errors, to improve flow and to make dedicated changes. Some simple but tedious algebraic manipulation in proofs was also off-loaded to AI-agents. The Lean formalization that accompanies this paper was carried out entirely by Claude`

### [2611.22468](https://arxiv.org/abs/2611.22468) — A 5/2 Guarantee for Echelon Stock (s,S) Policies in One-Warehouse Multi-Retailer Systems
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-17` | **Source:** `html`
- **Comment:** 70 pages, including a 32-page online appendix; 10 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 24, 'agent_tools': ['Claude'], 'tex_files_chars': 267456}`
  - *lean_version:* `ation, and editing. The author developed and verified the substantive research questions, theoretical framework, analysis, and results. The author takes sole responsibility for the paper’s content. The main results are formally verified in Lean 4; the formal proofs are public at https://prove2.me/missions/A_%245%2F2%24`
  - *in_lean_phrase:* `ical verification, and editing. The author developed and verified the substantive research questions, theoretical framework, analysis, and results. The author takes sole responsibility for the paper’s content. The main results are formally verified in Lean 4; the formal proofs are public at https://prove2.me/missions/A`

### [2611.22290](https://arxiv.org/abs/2611.22290) — A Little Advice Suffices: Diffie-Hellman Is as Hard as Discrete Logarithm
- **Primary / Target Cats:** `math.NT` / ['cs.CR'] | **Submitted:** `2026-11-17` | **Source:** `html`
- **Comment:** 15 pages. Developed with Claude Fable 5.2 and Claude Opus 5.5 (Anthropic); see "Use of AI". Companion paper on the hyperelliptic curve method: https://github.com/OctopusTide/hyperelliptic-curve-method
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 19, 'agent_tools': ['Claude'], 'tex_files_chars': 50069}`
- **Artifact URLs:** https://github.com/OctopusTide/hyperelliptic-curve-method, https://github.com/openai/math
  - *lean_prover_phrase:* `enny Chor and Oded Goldreich. On the power of two-point based sampling. Journal of Complexity, 5(1):96–106, 1989. [CT26] Cureton and Thorner. Zero-free half-plane for Dedekind zeta functions, 2026. Hexagon preprint 2610.00200, with Lean formalisation. [dB66] Nicolaas G. de Bruijn. On the number of positive integers and`

### [2611.21256](https://arxiv.org/abs/2611.21256) — Odd faces as a parameter for maximum independent set in embedded graphs
- **Primary / Target Cats:** `math.CO` / ['math.OC'] | **Submitted:** `2026-11-16` | **Source:** `html`
- **Comment:** 25 pages, 5 figures
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 24, 'tex_files_chars': 161908}`
  - *lean_version:* `. Oper. Res. Lett. 32 (4), pp. 299–301. External Links: ISSN 0167-6377,1872-7468, Document, Link, MathReview Entry Cited by: §1.2. [62] Robert D. Barish (2026) An FPT Algorithm for Maximum-Weight Independent Set in Embedded Graphs, in Lean 4. Note: Palomar, PALOMAR-2026-10-23-000015 v1 External Links: Link Cited by: §1`

### [2611.20298](https://arxiv.org/abs/2611.20298) — Type-Confusion Security
- **Primary / Target Cats:** `cs.PL` / ['cs.CR'] | **Submitted:** `2026-11-15` | **Source:** `html`
- **Comment:** The first two authors contributed equally to this work
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 40, 'agent_tools': ['Claude', 'Codex'], 'tex_files_chars': 313626}`
  - *lean_version:* `ncluding the language design, state-machine formulation, and the right abstractions, and we audited the result. Data-Availability Statement The supplementary material for this paper includes two artifacts: an appendix in PDF format and a Lean 4 (Moura and Ullrich, 2021) mechanization of the paper’s results. We will sub`
  - *mathlib:* `e standard classical axioms of Lean, namely propositional extensionality (propext), quotient soundness (Quot.sound), and choice (Classical.choice), which can be checked by running make axiom (AxiomsAudit.lean). The artifact uses Lean 4 and Mathlib (mathlib Community, 2020). The appendix includes more examples on CDA at`

### [2611.19551](https://arxiv.org/abs/2611.19551) — TrustBound: Mechanized Completeness for Payment Epochs Initiated by AI Agents
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-14` | **Source:** `html`
- **Comment:** 16 pages (LNCS), 2 figures, 8 tables. Code and Lean models: https://github.com/tokencraftdata/trustbound
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 1, 'agent_tools': ['Claude', 'Codex'], 'tex_files_chars': 44689}`
- **Artifact URLs:** https://github.com/tokencraftdata/trustbound
- **Lean Repo `tokencraftdata/trustbound`:** `.lean` files=16, LoC=1332, theorems=160, defs=135, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.19.0`, ci=`[]`
  - *lean_version:* `Coverage and discharge of every journaled identity imply ; no later transition can add a right or deliver an effect, giving (3). Truthful reports then identify exactly the executed journal entries, giving (4). The theorem is mechanized in Lean 4 [21] as four declarations.11 1 In Admission.lean: fenced_population_immuta`
  - *lean_prover_phrase:* `e 5 summarizes the results. All checks run from the public artifact without provider credentials or network access. Table 5: Summary of evaluation results. Counts measure different kinds of checks and should not be summed. Check Result Lean proofs (RQ1) 14 exported results checked; 8 premise-removal mutations rejected.`
  - *in_lean_phrase:* `Model and Closure Theorem The hotel example. Counterexecutions. Transfer to implementations. 4 Provider-Contract Model 5 Implementation 6 Evaluation 6.1 RQ1: Formal Checks 6.2 RQ2: What Evidence Can Show 6.3 RQ3: Service Histories Checked in Lean 6.4 RQ4: Client Behavior and Concurrency Generated schedules. Scripted cl`

### [2611.18455](https://arxiv.org/abs/2611.18455) — Mesh-Free Weak-Form Regression for Learning Interaction Kernels from Particle Trajectories
- **Primary / Target Cats:** `stat.ML` / ['math.OC'] | **Submitted:** `2026-11-13` | **Source:** `html`
- **Comment:** 47 pages, 8 figures
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 14, 'tex_files_chars': 156233}`
- **Artifact URLs:** https://github.com/inody/wmfki, https://github.com/inody/wmfki_lean
- **Lean Repo `inody/wmfki_lean`:** `.lean` files=156, LoC=12236, theorems=495, defs=137, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
  - *lean_version:* `nite-sample design requirement in Theorem 1. The oracle OLS bound then tends to zero, and choosing equality in (16) ensures the same for the LASSO bound. In the experiments, is instead selected using an independent validation trajectory. A Lean 4 formalization of Theorem 1 is available at https://github.com/inody/wmfki`

### [2611.18220](https://arxiv.org/abs/2611.18220) — From Pen-and-Paper to Machine-Checked Proofs: Lean for System Identification
- **Primary / Target Cats:** `eess.SY` / ['eess.SY'] | **Submitted:** `2026-11-13` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_verifiers', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 5, 'agent_tools': ['Claude', 'cursor'], 'tex_files_chars': 49702}`
- **Artifact URLs:** https://github.com/forgi86/control-theory-in-lean, https://github.com/forgi86/control-theory-in-leanAccessed, https://github.com/manasdm/Lean-SysID
- **Lean Repo `forgi86/control-theory-in-lean`:** `.lean` files=7, LoC=1196, theorems=38, defs=28, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Lean Repo `manasdm/Lean-SysID`:** `.lean` files=4, LoC=528, theorems=21, defs=19, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
  - *lean_version:* `every step. Interactive theorem proving offers a complement: the theorem and its proof are written as code, and every inference is checked by a small, trusted piece of software called the kernel. This paper serves as an introduction to the Lean 4 proof assistant for a system identification and control audience, assumin`
  - *mathlib:* `istants are not yet widely adopted in the control community. In system identification, to the best of our knowledge, no such effort has been reported to date. This paper serves as an introduction to Lean 4 (de Moura and Ullrich, 2021) and Mathlib (Avigad and Massot, 2025), its library of standard mathematical definitio`
  - *leanprover:* `al number and a hypothesis h stating ; after the colon comes the statement to be proved, namely ; finally, := by opens the proof in tactic mode, here a single tactic is written on line 3. The editor (VS Code, or the browser at https://live.lean-lang.org, opened with its code by the button ▶ Open in Lean Web on each lis`

### [2611.16781](https://arxiv.org/abs/2611.16781) — Boundary Actuation of a Chain Fountain - Physically Admissible Tracking, Stochastic Limits and Zero-Gravity Circulation
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Comment:** 61 pages, 16 figures
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'lean_macro': 75, 'theorem_envs': 19, 'agent_tools': ['Gemini'], 'tex_files_chars': 189047}`
- **Artifact URLs:** https://github.com/luchesart/Chain-fountain, https://github.com/luchesart/Chain-fountain/blob/main/Chain_Fountain_Lean_GitHub.zip, https://github.com/luchesart/MIACE/blob/2DOF-PID-shaping/ESM_3.pdf, https://github.com/luchesart/MIACE/blob/monotone-tracking/MIACE_Proofs_Companion.pdf
  - *lean_version:* `tion of the chain in three dimensions. Keywords: chain fountain; Mould effect; boundary actuation; nonlinear tracking; state constraints; robust control; Lyapunov stability; stochastic viability; backstepping; zero-gravity circulation; Lean 4 formalization. Public resources: Interactive simulator; project repository; L`
  - *mathlib:* `untainCompletion. The v0.19.0 release includes the original mathematical core, the zero-gravity extension and the completion results listed below. Its combined compilation and transitive axiom audit use Lean 4.33.0-rc1 with the same pinned mathlib, MathFin and Brownian-motion dependencies as the baseline. The source in`
  - *lean_prover_phrase:* `er’s global theorem, estimates on each existing finite prefix justify continuation to later times. This order closes the existence argument, whereas boundedness of an assumed all-time trajectory would leave its construction unresolved. The Lean proof first projects onto an outer state box to obtain a bounded extension,`

### [2611.16690](https://arxiv.org/abs/2611.16690) — Hilbert's 17th problem for symmetric functions: undecidability and a counterexample
- **Primary / Target Cats:** `math.AG` / ['math.OC'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Comment:** 17 pages, comments welcome
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 12, 'agent_tools': ['Claude', 'Codex'], 'tex_files_chars': 66964}`
- **Artifact URLs:** https://github.com/MColbrook/AIM/tree/main/research/solutions/559-univariate-trace-decidability, https://github.com/MColbrook/AIM/tree/main/research/solutions/559-univariate-trace-decidabilityLast, https://github.com/RobinSchabert/positive-sym-func-h17-undecidability-lean
- **Lean Repo `MColbrook/AIM`:** `.lean` files=37, LoC=1870, theorems=128, defs=47, sorry=61, axiom=1, native_decide=1, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`['comparator', 'lake build']`
- **Lean Repo `RobinSchabert/positive-sym-func-h17-undecidability-lean`:** `.lean` files=24, LoC=6592, theorems=564, defs=165, sorry=1, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc3`, ci=`[]`
  - *lean_prover_phrase:* `with additional assistance from Claude Fable 5.1 (Anthropic). The final presentation was written by the authors and AI was used to improve grammar, spelling and readability. The authors take full responsibility for the content. Finally, a Lean formalization of our proof was almost entirely generated by coding agents. T`

### [2611.16128](https://arxiv.org/abs/2611.16128) — CoordX Types: A Trustless, Swappable Type System for Shared Records
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-12` | **Source:** `html`
- **Comment:** 15 pages, 1 image, 8 tables, 1 code block
- **Matched Lean Signals:** `['in_lean_phrase']`
- **LaTeX Signals:** `{'tex_files_chars': 49838}`
  - *in_lean_phrase:* `ed becomes a “weird machine” [8] that an attacker can program. CBCL [9] applies LangSec to agent communication. It limits every message, including the definitions of new dialects, to the deterministic context-free class. Three invariants, checked in Lean, bound expansion, apply resource limits and keep the core vocabul`

### [2611.15201](https://arxiv.org/abs/2611.15201) — Sparse Matrix Multiplication Exponent 1.5 in the Low-bandwidth Model
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Comment:** Lean formalization available at https://doi.org/10.5281/zenodo.24127514
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 9, 'agent_tools': ['Codex', 'GPT-6'], 'tex_files_chars': 37746}`
- **Artifact URLs:** https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/paper.pdf
- **Lean Repo `zenodo/24127514`:** `.lean` files=36, LoC=5307, theorems=267, defs=241, sorry=25, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`[]`
  - *lean_prover_phrase:* `The upper bound was later improved to $O(d^{1.832})$ rounds. In this work, we give a deterministic algorithm that solves this problem in $O(d^{3/2})$ rounds in the supported setting, improving the previous bounds over fields and semirings. Lean formalization available at https://doi.org/10.5281/zenodo.24127514 Sparse M`

### [2611.15128](https://arxiv.org/abs/2611.15128) — Affine Combiners for Reed-Solomon Proximity Gaps
- **Primary / Target Cats:** `cs.IT` / ['cs.CR', 'cs.IT'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 22, 'agent_tools': ['Claude'], 'tex_files_chars': 138246}`
- **Artifact URLs:** https://github.com/leanEthereum/leanVM
- **Lean Repo `leanEthereum/leanVM`:** `.lean` files=2627, LoC=549901, theorems=26270, defs=15344, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0`, ci=`['lake build', 'print axioms']`
  - *lean_prover_phrase:* `for these combiners and immediately obtained Theorem 1.1. The analysis, including all proofs appearing in this paper, was carried out entirely with AI. The authors edited, verified, reorganized, and Lean-formalized the initial writeup. The Lean formalization was developed using ChatGPT 6 Astra, and the theorem statemen`

### [2611.15035](https://arxiv.org/abs/2611.15035) — RPX: Certifying Agent-Generated MILP Reformulations at Scale
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-11` | **Source:** `html`
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'leanblueprint_pkg': 3, 'theorem_envs': 4, 'tex_files_chars': 126768}`
  - *lean_version:* `22] Henry Robbins, Connor Lawless, Madeleine Udell, and Ellen Vitercik. FLARE: Verifying MILP reformulations with LLM-based theorem proving, 2026. arXiv:2608.25220. [23] Stefan Szeider. PBLean: Pseudo-boolean proof certificates for Lean 4, 2026. arXiv:2602.08692. [24] Jasper van Doornmalen, Leon Eifler, Ambros Gleixner`

### [2611.14756](https://arxiv.org/abs/2611.14756) — Stability of equilibria in discrete-time modified-gradient systems and the multivariate breeder's equation
- **Primary / Target Cats:** `math.DS` / ['math.OC'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 16 pages, 5 figures, 2 tables. Lean 4 formalization of the main results: https://github.com/magbenji/discrete-modified-gradient-lean (doi:10.5281/zenodo.24118844)
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 4, 'agent_tools': ['harmonic'], 'tex_files_chars': 53597}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.24118844, https://github.com/magbenji/discrete-modified-gradient-lean
- **Lean Repo `zenodo/24118844`:** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Lean Repo `magbenji/discrete-modified-gradient-lean`:** `.lean` files=6, LoC=670, theorems=23, defs=7, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
  - *lean_version:* `l. As further application of our results, the same conditions apply to the mean update of Gaussian evolutionary optimization algorithms, in which the covariance of the search population plays the role of $G$. 16 pages, 5 figures, 2 tables. Lean 4 formalization of the main results: https://github.com/magbenji/discrete-m`
  - *mathlib:* `basin of attraction results of [32]. Disclosure statement The author reports there are no competing interests to declare. Data availability statement No new data were generated in this study. Machine-checked proofs, in Lean 4 with the Mathlib library, of Lemma 4.1, Theorem 5.1, Corollary 5.2 and Theorem 6.1 are openly `

### [2611.14475](https://arxiv.org/abs/2611.14475) — Explicit restricted isometries with $k=m^{2/3-o(1)}$
- **Primary / Target Cats:** `math.FA` / ['cs.IT'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 16 pages
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'leanblueprint_pkg': 1, 'theorem_envs': 9, 'agent_tools': ['GPT-6', 'Harmonic'], 'tex_files_chars': 55064}`
- **Artifact URLs:** https://github.com/ckuemmerle/ExplicitRIPTwoThirds
- **Lean Repo `ckuemmerle/ExplicitRIPTwoThirds`:** `.lean` files=379, LoC=29967, theorems=1222, defs=258, sorry=4, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
  - *lean_version:* `ecked by the authors, who take full responsibility for the content of this paper. All theorems, lemmas and propositions of this paper, including the case of Zahl’s theorem used here (Theorem 6), have been formalized and machine-checked in Lean 4 with the Mathlib library; the running time of the construction in Theorem `
  - *mathlib:* `hors, who take full responsibility for the content of this paper. All theorems, lemmas and propositions of this paper, including the case of Zahl’s theorem used here (Theorem 6), have been formalized and machine-checked in Lean 4 with the Mathlib library; the running time of the construction in Theorem 1 is not part of`
  - *lean_prover_phrase:* `of this paper, including the case of Zahl’s theorem used here (Theorem 6), have been formalized and machine-checked in Lean 4 with the Mathlib library; the running time of the construction in Theorem 1 is not part of the formalization. The Lean formalization is maintained in the repository github.com/ckuemmerle/Explici`

### [2611.14083](https://arxiv.org/abs/2611.14083) — Sable: A Small-Field Sumcheck Argument for Bit-Exact Inference of Large Language Models
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 13, 'tex_files_chars': 225948}`
- **Artifact URLs:** https://github.com/BLAKE3-team/BLAKE3-specs, https://github.com/Plonky3/Plonky3, https://github.com/anthropics/FlashProve, https://github.com/moonmath-ai/Sable, https://github.com/zkonduit/ezkl
- **Lean Repo `anthropics/FlashProve`:** `.lean` files=29566, LoC=0, theorems=0, defs=0, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
  - *in_lean_phrase:* `the 64-bit Goldilocks field with Reed–Solomon codes, BLAKE2b Merkle trees and zero-knowledge proximity tests; the proof hides the weights, it is about MB per request, and the soundness, completeness and zero knowledge of the protocol are proved in Lean, while its C++ and CUDA programs are tested. On one H100 it proves `

### [2611.13872](https://arxiv.org/abs/2611.13872) — LongTails: Automated Research in Optimization
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Codex', 'DeepSeek'], 'tex_files_chars': 456916}`
- **Artifact URLs:** https://github.com/k3nfalt/longtails, https://github.com/k3nfalt/longtails/blob/main/LongTails/Algorithms/DampedGeneralizedAccelerated.lean, https://github.com/k3nfalt/longtails/blob/main/LongTails/Proofs/GeneralizedLogCharging.lean, https://github.com/k3nfalt/longtails/blob/main/LongTails/Proofs/GeneralizedSelfNormalizedConvergence.lean, https://github.com/k3nfalt/longtails/blob/main/LongTails/Setups/AdaptiveHeavyTailSimplex.lean
- **Lean Repo `k3nfalt/longtails`:** `.lean` files=4070, LoC=697377, theorems=34985, defs=11293, sorry=0, axiom=0, native_decide=0, unsafe=1, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0-rc2`, ci=`['comparator']`
- **Lean Repo `leanprover/comparator`:** `.lean` files=46, LoC=875, theorems=42, defs=121, sorry=26, axiom=6, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`['comparator', 'lake build', 'nanoda']`
- **Lean Repo `optsuite/optlib`:** `.lean` files=43, LoC=15758, theorems=695, defs=113, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.13.0`, ci=`['lake build']`
  - *lean_version:* `LongTails: Automated Research in Optimization We introduce LongTails, a framework for discovering and improving oracle-complexity bounds with formal verification in Lean 4. Using LongTails, we have already obtained more than 100 new results across a broad range of optimization problems, including generalized smoothness`
  - *mathlib:* `th uniformly better guarantees. The agents obtained a better Complexity in a single run lasting approximately 2–7 hours. 6 Related Work Formalized mathematics and optimization. Lean 4 [48] and the community-developed mathematical library mathlib [212] provide infrastructure for machine-checked mathematics. Within optim`
  - *leanprover:* `stochastic) gradient method. Note: Version 2, December 23, 2019. https://arxiv.org/abs/1907.04232v2 External Links: 1907.04232, Document, Link Cited by: Table 56. [211] The Comparator Contributors Comparator. Note: https://github.com/leanprover/comparatorGitHub repository. Accessed 4 November 2026 External Links: Link `

### [2611.13585](https://arxiv.org/abs/2611.13585) — Approximating graphic TSP by b-matchings
- **Primary / Target Cats:** `cs.DS` / ['math.OC'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 72 pages, 30 figures
- **Matched Lean Signals:** `['lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 36, 'agent_tools': ['GPT-5', 'GPT-6'], 'tex_files_chars': 269793}`
- **Artifact URLs:** https://github.com/Mehrdad-Sohrabi/Graphic-TSP
  - *lean_version:* `xpected reconnection charge. Additional Evidence from Lean-Verification. Though the main ideas for StarMatch and for these approximations are human-generated and human-explained, for the last column of Table 2, we formalized the proofs in Lean 4 (v4.19.0) over Mathlib (commit c44e0c8e), to find better constructions of `
  - *mathlib:* `harge. Additional Evidence from Lean-Verification. Though the main ideas for StarMatch and for these approximations are human-generated and human-explained, for the last column of Table 2, we formalized the proofs in Lean 4 (v4.19.0) over Mathlib (commit c44e0c8e), to find better constructions of the admissible vector,`

### [2611.13584](https://arxiv.org/abs/2611.13584) — Exact (Non-)Accelerations of Heavy-Ball Discretizations
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-10` | **Source:** `html`
- **Comment:** 63 pages, 7 figures, link to Lean formalization
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 77, 'agent_tools': ['Claude', 'harmonic'], 'tex_files_chars': 321629}`
- **Artifact URLs:** https://github.com/dmivilensky/PolynomialRealizationsProgram/tree/main/nesterov
- **Lean Repo `dmivilensky/PolynomialRealizationsProgram`:** `.lean` files=7628, LoC=840767, theorems=48067, defs=21676, sorry=0, axiom=0, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
  - *lean_prover_phrase:* `this family attaining the optimal leading constant 1. The flow also bounds the leading constant of every second-order stationary linear family with the same slow parameters $(\theta,y)$ and fixed finite memory. 63 pages, 7 figures, link to Lean formalization Exact (Non-)Accelerations of Heavy-Ball Discretizations Skip `

### [2611.12680](https://arxiv.org/abs/2611.12680) — Wolfe's Minimum-Norm-Point Method Generalizes the Simplex Method
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-09` | **Source:** `html`
- **Comment:** v2: Lean formalization archived at https://doi.org/10.5281/zenodo.24136107; author emails; minor corrections
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 26, 'agent_tools': ['Claude'], 'tex_files_chars': 156509}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.24136107
- **Lean Repo `zenodo/24136107`:** `.lean` files=125, LoC=23932, theorems=1456, defs=566, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`
  - *lean_version:* `on, inspired by [16], that makes the similarities of the methods apparent (Algorithms 1 and 2). Formally, we prove the following.11 1 Theorem 1, Corollaries 1–4, and all numbered supporting statements have been formally verified in Lean 4: https://doi.org/10.5281/zenodo.24136107. Theorem 1.1 Every bounded, non-degenera`
  - *lean_prover_phrase:* `zed and history-based rules. As a corollary, we obtain the first exponential example for the Lawson-Hanson algorithm for nonnegative least squares, as well as PSPACE-hardness of deciding whether the linopt rule ever uses a given point. v2: Lean formalization archived at https://doi.org/10.5281/zenodo.24136107; author e`
  - *in_lean_phrase:* `a formulation, inspired by [16], that makes the similarities of the methods apparent (Algorithms 1 and 2). Formally, we prove the following.11 1 Theorem 1, Corollaries 1–4, and all numbered supporting statements have been formally verified in Lean 4: https://doi.org/10.5281/zenodo.24136107. Theorem 1.1 Every bounded, n`

### [2611.12585](https://arxiv.org/abs/2611.12585) — A Large Gap between Galerkin Errors with and without Mesh-Uniform Regularity for the KdV Equation with Boundary Dissipation
- **Primary / Target Cats:** `math.NA` / ['math.OC'] | **Submitted:** `2026-11-09` | **Source:** `html`
- **Comment:** 57 pages, 2 figures. v2 adds Lean 4 proofs of the main results. Ancillary files: Lean 4 sources, programs and outputs
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'lean_macro': 247, 'theorem_envs': 25, 'agent_tools': ['Claude', 'Codex', 'GPT-6'], 'tex_files_chars': 227962}`
  - *lean_version:* `prove that neither bound holds for the S-scheme by using exact high-frequency spurious eigenpairs of the S-scheme. The existence of such eigenpairs for meshes with at least 512 elements and the failure of both bounds have proofs checked by Lean 4. The only premise is the mesh-uniform Crandall-Pazy estimate of the W-sch`
  - *mathlib:* `the nondegeneracy conditions. The author tried to check this proof by hand and found its complexity too large for a complete check. The author therefore had the proof formalized in Lean 4. The formalization was carried out by GPT-6 Astra. Mathlib has no Rouché theorem. The formal proof therefore uses contraction mappin`
  - *lean_prover_phrase:* `without GitHub Submit in GitHub Why HTML? Report Issue Back to Abstract Download PDF Contents Reading mode Colour theme 1 Introduction The datum and the high-frequency spurious eigenpairs. Lean proofs. Main results. What the gap does not say. An application. Related work. Organization. 2 Setting 2.1 The two schemes An `

### [2611.12310](https://arxiv.org/abs/2611.12310) — The Optimal Rate Constant of Heavy-Ball Momentum on Smooth Strongly Convex Functions
- **Primary / Target Cats:** `cs.LG` / ['math.OC'] | **Submitted:** `2026-11-09` | **Source:** `html`
- **Comment:** 41 pages, 1 figure. Code and exact certificates: https://github.com/marcoshernanz/heavy-ball-optimal-rate
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 16, 'agent_tools': ['harmonic'], 'tex_files_chars': 117731}`
- **Artifact URLs:** https://github.com/marcoshernanz/heavy-ball-optimal-rate
  - *lean_version:* `rates on functions of one variable, the first of the two riddles of Goujaud et al. [12] (their Open Problem 1), was settled negatively before this work. It was first answered by Fotopoulos et al. [7], in a blog post of July 7, 2026, with a Lean 4 formalization of the core construction that rests on two stated external `

### [2611.11713](https://arxiv.org/abs/2611.11713) — Binary Belief Propagation Fixed Points: Finiteness, Rigidity, and Topological Complexity
- **Primary / Target Cats:** `cs.IT` / ['cs.IT'] | **Submitted:** `2026-11-09` | **Source:** `html`
- **Comment:** 37 pages, 3 figures. Lean 4 formalization and interval certificates at https://github.com/ywatanabex/bp-response-geometry-lean
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_verifiers', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 9, 'tex_files_chars': 141954}`
- **Artifact URLs:** https://github.com/TauCetiProject/TauCeti, https://github.com/ywatanabex/bp-degree-syzygies-lean, https://github.com/ywatanabex/bp-response-geometry-lean
- **Lean Repo `TauCetiProject/TauCeti`:** `.lean` files=37714, LoC=0, theorems=0, defs=0, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`none`, ci=`[]`
- **Lean Repo `ywatanabex/bp-degree-syzygies-lean`:** `.lean` files=932, LoC=135060, theorems=7411, defs=3205, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
- **Lean Repo `ywatanabex/bp-response-geometry-lean`:** `.lean` files=257, LoC=69875, theorems=3955, defs=1291, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`
  - *lean_version:* `e field discriminant of an eighteen-vertex product model and recover its torus component's genus from the counts of distinct roots on all field cells. The three main theorems, including the logarithmic size bounds, are formally verified in Lean 4 with Mathlib. 37 pages, 3 figures. Lean 4 formalization and interval cert`
  - *mathlib:* `riminant of an eighteen-vertex product model and recover its torus component's genus from the counts of distinct roots on all field cells. The three main theorems, including the logarithmic size bounds, are formally verified in Lean 4 with Mathlib. 37 pages, 3 figures. Lean 4 formalization and interval certificates at `
  - *leanprover:* `d Quot.sound. In particular no declaration depends on sorryAx or on native_decide. At revision 4d0ae2b2 the audit reports declarations and theorems. The audit certifies this development, not every file of the repository. The toolchain is leanprover/lean4:v4.36.0-rc2. Mathlib is pinned to commit 1b1ccf4b, Tau Ceti to re`

### [2611.10902](https://arxiv.org/abs/2611.10902) — Bisect-Index-Choose: A Fast and Exact Algorithm for EV Charging under Minimum Charging Rates
- **Primary / Target Cats:** `eess.SY` / ['eess.SY'] | **Submitted:** `2026-11-07` | **Source:** `html`
- **Comment:** 10 pages, 6 figures. This work has been submitted to the IEEE for possible publication. Copyright may be transferred without notice, after which this version may no longer be accessible
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 7, 'agent_tools': ['Claude'], 'tex_files_chars': 68898}`
- **Artifact URLs:** https://github.com/canberksaner/bic-public, https://github.com/open-ev-data/open-ev-data-dataset/releases/tag/v1.24.0
- **Lean Repo `canberksaner/bic-public`:** `.lean` files=11, LoC=2068, theorems=102, defs=40, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc2`, ci=`[]`
  - *lean_version:* `n a low-cost microcontroller and show that it solves instances with up to 1000 EVs in a fraction of a control period.11 1 The implementation of BIC, the code to reproduce all results, and a formalization of theorems and lemmas in the Lean 4 proof assistant are available at https://github.com/canberksaner/bic-public. Th`

### [2611.10810](https://arxiv.org/abs/2611.10810) — Extending DBLog-Based Incremental Snapshots to Handle Orphan Rows in CDC Pipelines
- **Primary / Target Cats:** `cs.DB` / ['cs.DC'] | **Submitted:** `2026-11-07` | **Source:** `pdf`
- **Comment:** 15 pages, 4 figures, 2 tables. Isabelle/HOL, Lean 4 and TLA+ development: https://doi.org/10.5281/zenodo.24035424
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Gemini'], 'tex_files_chars': 90048}`
- **Artifact URLs:** https://github.com/postgres/postgres/blob/REL_18_0/src/backend/, https://github.com/postgres/postgres/blob/REL_18_0/src/backend/access/transam/xact.c
- **Lean Repo `zenodo/22643866`:** `.lean` files=6, LoC=2092, theorems=88, defs=34, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.2`, ci=`[]`
- **Lean Repo `zenodo/24035424`:** `.lean` files=24, LoC=10862, theorems=525, defs=108, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.2`, ci=`[]`
  - *lean_version:* `ey turn DBLog into a complete data synchronization engine whether a sink catches up on live changes or missing rows, holds wrong column values, or contains orphan rows. Their safety and convergence are formally verified in Isabelle/HOL and Lean 4. 15 pages, 4 figures, 2 tables. Isabelle/HOL, Lean 4 and TLA+ development`

### [2611.09736](https://arxiv.org/abs/2611.09736) — Safety Is $Π_1$, Provability Is $Σ_1$: One Framework for the Hugging Face Breach and OpenAI's Mathematical Proofs
- **Primary / Target Cats:** `cs.LG` / ['cs.CR'] | **Submitted:** `2026-11-06` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 4, 'tex_files_chars': 65748}`
- **Artifact URLs:** https://github.com/openai/math, https://huggingface.co/blog/security-incident-july-2026
  - *lean_version:* `roduced by an unreleased internal model that had been given roughly four thousand problems (OpenAI, 2026b). Press reports at release gave 722 manuscripts in 372 families, and as of 9 October the README gives 719. Many manuscripts come with Lean 4 formalizations. The formalization catalog includes Lean declarations for `
  - *mathlib:* `that is, on the consistency of Lean’s type theory when the theorem is , and on its soundness otherwise. The mathematical definitions. The definitions in question are the mathematical definitions of the system: in Lean, the definitions of Mathlib, such as that of ; in security, the specification , that is, the definitio`
  - *leanprover:* `inciples, 207–220, 2009. Lamport (1977) L. Lamport. Proving the correctness of multiprocess programs. IEEE Transactions on Software Engineering, SE-3(2):125–143, 1977. Lean 4.32.1 (2026) Lean FRO. Lean 4.32.1 release notes. https://lean-lang.org/doc/reference/latest/releases/v4.32.1/, 2026. Accessed 9 October 2026. Lea`

### [2611.09169](https://arxiv.org/abs/2611.09169) — The multiplier step size in classical two-block ADMM: convergence and counterexamples
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-06` | **Source:** `html`
- **Comment:** 24 pages
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 12, 'tex_files_chars': 86284}`
- **Artifact URLs:** https://github.com/bqliu815/ADMM-Multiplier-Step-Size
  - *lean_version:* `s, Appendix C bounds the uniform convergence endpoint using a unit-circle certificate and a separate periodic orbit. The exact endpoint remains open, as does the question of whether finite cycles account for every failure of convergence. A Lean 4 formalization accompanying this work is available at https://optpku.githu`

### [2611.09050](https://arxiv.org/abs/2611.09050) — Resolvent-Diagonal Energy of Isospectral Jacobi Matrices
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-06` | **Source:** `pdf`
- **Comment:** 56 pages, 2 figures, link to Lean formalization
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 35, 'agent_tools': ['Claude'], 'tex_files_chars': 288291}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.21818873, https://github.com/dmivilensky/PolynomialRealizationsProgram/tree/main/jacobi
- **Lean Repo `dmivilensky/PolynomialRealizationsProgram`:** `.lean` files=7628, LoC=840767, theorems=48067, defs=21676, sorry=0, axiom=0, native_decide=0, unsafe=5, blueprint_attr=0, toolchain=`leanprover/lean4:v4.34.1`, ci=`[]`
  - *lean_prover_phrase:* `-drift gain among nonnegative-link Jacobi realizations is $\sqrt{2}$ times the original gain. An explicit isospectral flow strictly improves the standard one-sided realization for $\alpha>-1/2$, $\alpha\ne1/2$. 56 pages, 2 figures, link to Lean formalization Resolvent-Diagonal Energy of Isospectral Jacobi Matrices Dmit`

### [2611.08172](https://arxiv.org/abs/2611.08172) — Uniform Three-Fold Product Expansion of Algebraic-Geometry Codes over a Fixed Field
- **Primary / Target Cats:** `cs.IT` / ['cs.IT'] | **Submitted:** `2026-11-05` | **Source:** `html`
- **Comment:** 76 pages
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 66, 'agent_tools': ['harmonic'], 'tex_files_chars': 331645}`
- **Artifact URLs:** https://github.com/dcass-121/d3-lean-verification
- **Lean Repo `dcass-121/d3-lean-verification`:** `.lean` files=2486, LoC=200335, theorems=8473, defs=5031, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.31.0`, ci=`[]`
  - *lean_version:* `ive a sufficient criterion for three-fold product expansion in terms of degree and genus ratios, yielding explicit families over every non-prime finite field of order at least $512$. The principal conclusions have been formally verified in Lean 4. 76 pages Uniform Three-Fold Product Expansion of Algebraic-Geometry Code`
  - *mathlib:* `ry B; the Schur fullness assertion of Corollary B and the closed genus formula of Section 3 are not among the formal endpoints, the latter being replaced by the formally proved genus-ratio limit . The development is pinned to Lean v4.31.0, Mathlib and a Riemann–Roch library for function fields, and its endpoint checks `
  - *in_lean_phrase:* `s. We also give a sufficient criterion for three-fold product expansion in terms of degree and genus ratios, yielding explicit families over every non-prime finite field of order at least $512$. The principal conclusions have been formally verified in Lean 4. 76 pages Uniform Three-Fold Product Expansion of Algebraic-G`

### [2611.10031](https://arxiv.org/abs/2611.10031) — zkARc: Succinctly Verifiable Proofs for Neurosymbolic Natural Language Formalization and Verification
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-05` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 5, 'tex_files_chars': 213729}`
- **Artifact URLs:** https://github.com/Lagrange-Labs/deep-prove, https://github.com/guardrails-ai/guardrails, https://github.com/langchain-ai/langchain, https://github.com/langchain-ai/langgraph, https://github.com/zkonduit/ezkl
  - *lean_prover_phrase:* `of-system and commitment assumptions, at substantially higher per-action proving cost (§10.1). Zero-knowledge proofs for solvers, neural networks and guardrails ZKSMT [29] checks SMT proof certificates in zero knowledge, zkPi [26] checks Lean proof terms, and zkLean [14] specifies ZK statements in Lean. Solver certific`

### [2611.05726](https://arxiv.org/abs/2611.05726) — Do Language Models Know Which Constraints Belong Together?
- **Primary / Target Cats:** `cs.LG` / ['math.OC'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Comment:** 69 pages, 5 figures, 31 tables. Code and data: https://github.com/junbolian/JointDW
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 27, 'agent_tools': ['Claude', 'DeepSeek', 'GPT-6', 'gpt-6'], 'tex_files_chars': 283010}`
- **Artifact URLs:** https://github.com/junbolian/JointDW
  - *lean_prover_phrase:* `Teshnizi et al., 2024; Liang et al., 2026). Generated formulations are checked by perturbation responses (Lian et al., 2026b), agreement across model families (Lian et al., 2026a), solver feedback (Zhu et al., 2026), and variable mappings, Lean proofs, or SMT solvers (Zhai et al., 2025; Robbins et al., 2026; Bhattachar`

### [2611.05243](https://arxiv.org/abs/2611.05243) — Logarithmic Regret for Alternating Mirror Descent
- **Primary / Target Cats:** `cs.LG` / ['math.OC'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 15, 'agent_tools': ['GPT-5', 'GPT-6'], 'tex_files_chars': 100214}`
- **Artifact URLs:** https://github.com/CoffeeAndConvexity/AltOMD-Lean
- **Lean Repo `CoffeeAndConvexity/AltOMD-Lean`:** `.lean` files=79, LoC=11204, theorems=644, defs=199, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.1`, ci=`[]`
  - *lean_prover_phrase:* `our assumptions hold for the negative entropy regularizer, thereby obtaining logarithmic regret for the alternating multiplicative weights updates algorithm. The regret bound also yields an duality-gap bound for the averaged strategies. A Lean formalization of the results is available at https://github.com/CoffeeAndCon`

### [2611.05136](https://arxiv.org/abs/2611.05136) — Information Loss Is All You Need: $TC^0$ Pseudorandomness from Worst-Case Lattices
- **Primary / Target Cats:** `cs.CC` / ['cs.CR'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['lean_prover_phrase', 'lean_verifiers']`
- **LaTeX Signals:** `{'theorem_envs': 65, 'tex_files_chars': 697912}`
- **Artifact URLs:** https://github.com/qianchen92/aft-lean-theorem99
- **Lean Repo `qianchen92/aft-lean-theorem99`:** `.lean` files=1794, LoC=219688, theorems=11051, defs=6431, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0-rc1`, ci=`[]`
  - *lean_verifiers:* `n the counted binary-operation model.11 1 https://github.com/qianchen92/aft-lean-theorem99 The project-specific code is entirely AI-generated. We checked only its main statement’s correspondence, compilation, and absence of sorryAx or nonstandard axioms, without verifying correspondence of the internal construction or `
  - *lean_prover_phrase:* `hardness of learning. 1.1 Our Results A fixed family for every polynomial sample budget. From Gaussian noise to deterministic information loss. Calibrating public randomness. Consequences for pseudorandomness and noiseless learning. Lean formalization. 1.2 Technical Overview I. Finding the error law that rounding can a`

### [2611.04876](https://arxiv.org/abs/2611.04876) — Leakage-Resilient Computation via Matrix Refreshing
- **Primary / Target Cats:** `cs.CR` / ['cs.CR'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 31, 'agent_tools': ['Claude'], 'tex_files_chars': 482436}`
- **Artifact URLs:** https://github.com/sdziembowski/MatrixRefresh, https://github.com/sdziembowski/MatrixRefresh/tree/main/version-1.0
- **Lean Repo `sdziembowski/MatrixRefresh`:** `.lean` files=417, LoC=81481, theorems=3285, defs=1933, sorry=41, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.35.0`, ci=`[]`
  - *lean_version:* `for polynomial-size circuits, a constant leakage fraction is tolerated with share length depending only on the security parameter. We formalize the refreshing bound, the composition and compiler guarantees, and the expected-work bounds in Lean 4. Our results also provide efficient simulation: the leakage can be reprodu`
  - *mathlib:* `ketch the extension to adaptivity within a refresh and discuss the extension to larger fields. Neither of these last two extensions is formalized. 6.1 Lean formalization Our formalization, written in Lean 4 [DBLP:conf/cade/Moura021] with mathlib [DBLP:conf/cpp/X20], covers the binary continual-refreshing bound (see Thm`
  - *lean_prover_phrase:* `products of local errors 5.4.3 A signed difference for each encoding 5.4.4 Expanding and summing marked terms 5.4.5 The common term and the final comparison 5.5 Concrete simulation and expected work 6 Formalization and extensions 6.1 Lean formalization 6.2 Adaptivity within a refresh 6.3 Stateful circuits 6.4 General f`

### [2611.04561](https://arxiv.org/abs/2611.04561) — Distributed LTL Synthesis under Arbitrary Message Adversaries
- **Primary / Target Cats:** `cs.DC` / ['cs.DC', 'eess.SY'] | **Submitted:** `2026-11-03` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 47, 'agent_tools': ['GPT-6'], 'tex_files_chars': 196308}`
- **Artifact URLs:** https://github.com/BioDisCo/distributed_synthesis_lean/blob/ba94ebc0d82b04d70600f1a03e5ee2d24164ab8b/DistributedSynthesis/Formalizations/ComponentTrees/GeneratingAlphabet.lean#L27, https://github.com/BioDisCo/distributed_synthesis_lean/blob/ba94ebc0d82b04d70600f1a03e5ee2d24164ab8b/DistributedSynthesis/Formalizations/ComponentTrees/Trees.lean#L62, https://github.com/BioDisCo/distributed_synthesis_lean/blob/ba94ebc0d82b04d70600f1a03e5ee2d24164ab8b/DistributedSynthesis/Formalizations/ComponentTrees/Trees.lean#L78, https://github.com/BioDisCo/distributed_synthesis_lean/blob/ba94ebc0d82b04d70600f1a03e5ee2d24164ab8b/DistributedSynthesis/Formalizations/Definition/DefLTL.lean, https://github.com/BioDisCo/distributed_synthesis_lean/blob/ba94ebc0d82b04d70600f1a03e5ee2d24164ab8b/DistributedSynthesis/Formalizations/Definition/DefNondeterministicOmegaAutomata.lean#L25
- **Lean Repo `BioDisCo/distributed_synthesis_lean`:** `.lean` files=2395, LoC=929448, theorems=20193, defs=20454, sorry=0, axiom=0, native_decide=2, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.30.0`, ci=`[]`
  - *lean_version:* `decidable in the general case for message adversaries as they are studied in the theory of distributed computing. We develop a new topological approach to establish this characterization. Results marked with have machine-checked proofs in Lean 4 using Mathlib (v4.30.0). Each proof badge links to a dedicated Lean file c`
  - *mathlib:* `the general case for message adversaries as they are studied in the theory of distributed computing. We develop a new topological approach to establish this characterization. Results marked with have machine-checked proofs in Lean 4 using Mathlib (v4.30.0). Each proof badge links to a dedicated Lean file containing the`
  - *lean_prover_phrase:* `ries 7 Decidability via Bounded Component Trees 7.1 The Block Automaton and Component Trees 7.2 Compressing Components 7.3 Symbolic Component Trees 7.4 Acceptance and the Decision Procedure 8 Conclusion A LTL Syntax and Semantics B Lean Formalization References License: CC BY 4.0 arXiv:2611.04561v1 [cs.DC] 03 Nov 2026 `

### [2611.02849](https://arxiv.org/abs/2611.02849) — TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System
- **Primary / Target Cats:** `cs.AI` / ['cs.DC'] | **Submitted:** `2026-11-02` | **Source:** `html`
- **Comment:** 35 pages (10-page main text, references, and appendix), 7 figures, 20 tables. Benchmark and harness: https://github.com/specula-org/TLAPS-Bench
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'agent_tools': ['Claude', 'Codex', 'Cursor', 'GPT-5', 'GPT-6'], 'tex_files_chars': 159820}`
- **Artifact URLs:** https://github.com/Disalg-ICS-NJU/zookeeper-tla-spec, https://github.com/Disalg-ICS-NJU/zookeeper-tla-spec/blob/9e9eb2e6ce1019fe70b6f5002aa5927e037fddf6/high-level-spec/Zab.tla, https://github.com/Disalg-ICS-NJU/zookeeper-tla-spec/blob/9e9eb2e6ce1019fe70b6f5002aa5927e037fddf6/low-level-spec/zk-3.7/ZkV3_7_0.tla, https://github.com/PirateshipOrg/pirateship-tla, https://github.com/PirateshipOrg/pirateship-tla/blob/19096c1de2f87c68a21311c9100a5bab423caa0e/pirateship.tla
- **Lean Repo `microsoft/CCF`:** `.lean` files=160, LoC=38155, theorems=1336, defs=932, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0`, ci=`['lake build']`
  - *lean_version:* `N. Z3: An Efficient SMT Solver. In Proceedings of the 14th International Conference on Tools and Algorithms for the Construction and Analysis of Systems (TACAS), March 2008. de Moura & Ullrich (2021) de Moura, L. and Ullrich, S. The Lean 4 Theorem Prover and Programming Language. In Proceedings of the 28th Internationa`

### [2611.02256](https://arxiv.org/abs/2611.02256) — Exact Shortest Paths and Maximum Flow in Planar Networks in the CONGEST Model
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Submitted:** `2026-11-01` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lakefile', 'lean_version', 'leanprover', 'mathlib']`
- **LaTeX Signals:** `{'theorem_envs': 1, 'agent_tools': ['Claude'], 'tex_files_chars': 241057}`
- **Artifact URLs:** https://github.com/ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs
- **Lean Repo `ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs`:** `.lean` files=14, LoC=2191, theorems=132, defs=52, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0-rc1`, ci=`[]`
  - *lean_version:* `11$ vertices it reports $37$ for a minimum cut of $15$. Two more shortest-path computations per level make it exact. The virtual-source lemma, the weighting of the face-disjoint graph and the corrected discretization are machine-checked in Lean 4 with Mathlib; all other arguments are proved on paper only. Numerical che`
  - *mathlib:* `it reports $37$ for a minimum cut of $15$. Two more shortest-path computations per level make it exact. The virtual-source lemma, the weighting of the face-disjoint graph and the corrected discretization are machine-checked in Lean 4 with Mathlib; all other arguments are proved on paper only. Numerical checks are not u`
  - *leanprover:* `pass, further runs. 8 Formal verification The formalization is in the directory lean/SsspFlow/ of the repository https://github.com/ssenge/ExactShortestPathsAndFlowsOnPlanarGraphs, at the tag arxiv-v1. It uses Lean 4 with the toolchain leanprover/lean4:v4.36.0-rc1 and Mathlib at the revision d875a8de5222f62cf1c2fafc798`

### [2611.02057](https://arxiv.org/abs/2611.02057) — Paying for Fractional Error: Tight Constant-Round Approximation of Covering Problems with Short Broadcasts
- **Primary / Target Cats:** `cs.DS` / ['cs.DC'] | **Submitted:** `2026-11-01` | **Source:** `pdf`
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 76, 'agent_tools': ['Claude'], 'tex_files_chars': 405359}`
- **Artifact URLs:** https://github.com/wwawrzy/paying-for-fractional-error-lean
- **Lean Repo `wwawrzy/paying-for-fractional-error-lean`:** `.lean` files=1617, LoC=166354, theorems=8757, defs=3745, sorry=0, axiom=10, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.29.0`, ci=`[]`
  - *lean_version:* `need a different budget transfer. Which local covering problems admit a rounding rule with slack at their critical coefficient? J Formal verification and acknowledgments We have formalized and checked all 81 named results of this paper in Lean 4. The formalization consists of 1612 modules and is available on GitHub.2 O`

### [2611.01761](https://arxiv.org/abs/2611.01761) — Computation in Anonymous Directed Dynamic Networks: Exact Worst-Case Termination Time and Network-Wise Intractability
- **Primary / Target Cats:** `cs.DC` / ['cs.DC'] | **Submitted:** `2026-11-01` | **Source:** `html`
- **Comment:** 37 pages, 3 figures
- **Matched Lean Signals:** `['lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 26, 'agent_tools': ['GPT-6'], 'tex_files_chars': 125998}`
- **Artifact URLs:** https://github.com/gadiluna/ADDN_lean
- **Lean Repo `gadiluna/ADDN_lean`:** `.lean` files=2104, LoC=158351, theorems=6418, defs=6005, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.32.0`, ci=`[]`
  - *lean_prover_phrase:* `e proof of Lemma 1 using Perron–Frobenius theory. Disclosure of AI assistance. We used the AI assistant GPT-6 Astra to refine and validate the multi-leader lower-bound construction (Sections 3.2 and D) and to produce formal proofs in the Lean proof assistant for all results in this paper. The Lean code is available at `

### [2611.01384](https://arxiv.org/abs/2611.01384) — Benign population landscapes do not transfer to empirical risk minimization in nonsmooth optimization
- **Primary / Target Cats:** `math.OC` / ['math.OC'] | **Submitted:** `2026-11-01` | **Source:** `html`
- **Comment:** 71 pages, 2 figures, 1 table
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase']`
- **LaTeX Signals:** `{'theorem_envs': 35, 'agent_tools': ['Claude', 'GPT-5', 'GPT-6'], 'tex_files_chars': 308604}`
- **Artifact URLs:** https://github.com/PenghaoWang1225/Phase-Retrieval, https://github.com/powergiant/qmd-prover
  - *lean_prover_phrase:* `iving Interval evaluation with this remainder gives Combining this enclosure with (C.21), we conclude that, for every fixed , Since , this establishes the choice in Theorems C.4 and 3.3. Verification and reproduction. The accompanying Lean formalization verifies the identity (C.22), the correlation bounds, the angular `
  - *in_lean_phrase:* `mpanying Lean formalization verifies the identity (C.22), the correlation bounds, the angular series and its remainder estimate, and the uniform bound (C.31). The moment theorems and covariance reduction are proved in the paper but are not formalized in Lean. The numerical enclosures are computed separately, outside Le`

## Lean Contextual-Only Hits (8 papers — review for recall)

- **[2611.25663](https://arxiv.org/abs/2611.25663)** (`cs.CR`) Correctable Enrollment and One-Transaction Seed Proofs for Ethereum's Post-Quantum Transition — `h to hash-based keys first, at a finalized checkpoint and under a stated bound on the attacker's voting power. We prove the account guarantees under explicit assumptions, model-check the rules, and implement the design in go-ethereum and a `
- **[2611.20296](https://arxiv.org/abs/2611.20296)** (`math.OC`) Descending Everest, Part III: Oracle Complexity of Monotone Variational Inequalities with $(L_0,L_1)$-Lipschitz Operators — `raints (Greenberg and Loizou, 2026). For a monotone operator without additional conditions, all these bounds either have the same quadratic order or are not expressed in terms of alone. In the LongTails repository (Tyurin et al., 2026), a L`
- **[2611.20131](https://arxiv.org/abs/2611.20131)** (`math.NA`) Quadrature-Induced Local Minima in Structure-Preserving Lotka-Volterra Control — `tion systems. Acknowledgment The author used AI tools to edit the language, organize the manuscript, and help write and review the code used in the numerical experiments. These tools also assisted with formalizing and checking proofs in (Le`
- **[2611.15431](https://arxiv.org/abs/2611.15431)** (`quant-ph`) Subadditivity and the failure of strong subadditivity in the Nichols--Wootters family of entropies — `Acknowledgments The authors used AI tools, namely ChatGPT Pro (GPT-6 Pro), Codex (gpt-6.1-sol) and Claude Opus 5.5 (via Claude Code), for literature search, computation and double-checking, including formal verification of the results in Le`
- **[2611.14147](https://arxiv.org/abs/2611.14147)** (`quant-ph`) Secure Information Flow in Quantum Programs — `of the 29th ACM SIGPLAN-SIGACT symposium on Principles of programming languages. 319–330. Ren et al. (2026) Yuanjie Ren, Zhicheng Zhang, Junyi Liu, Jinzheng Li, Yidi Qi, and Mingsheng Ying. 2026. QEDIA: Quantum Program Verification in Lean.`
- **[2611.08318](https://arxiv.org/abs/2611.08318)** (`cs.AI`) Learning the Task or Learning the Verifier? Rethinking Criteria Exposure in Embodied Self-Improvement — `transfer poorly across tasks. We further propose instruction-faithful criteria and show that they better reflect the performance of agent-generated programs. 22 pages, 8 figures, 10 tables. Project page: https://dagroup-pku.github.io/PyRUA-`
- **[2611.07496](https://arxiv.org/abs/2611.07496)** (`cs.DC`) ZYFA: Speed and Accuracy of FP8 FlashAttention on AMD CDNA4 — `nt, the same relation that Schraudolph’s fast exponential uses for IEEE floating-point numbers (Schraudolph, 1999). At head dimension the FP8 kernel computes this code with one multiply-add and one integer conversion, which we call lean P. `
- **[2611.02169](https://arxiv.org/abs/2611.02169)** (`math.OC`) Split Cuts in Fixed Integer Dimensions — `ve. For arbitrary continuous objectives, the example in (5.11) obstructs even finite exact termination. AI use disclosure The authors used OpenAI’s ChatGPT to assist with literature searches, checking of proofs and calculations including Le`
