# Phase 0 Deterministic Probe Summary

- **Date window (submitted):** `2025-11-01T00:40:10Z` to `2025-11-19T23:12:28Z`
- **Total unique papers ingested:** 2435
- **Total papers screened:** 2435 (`html`: 2223, `pdf`: 198, `failed`: 14)
- **Lean strong hits (full text):** 2 *(vs. metadata-only: 0)*
- **Lean contextual-only hits:** 1
- **Confirmed public Lean GitHub repos found:** 2

## Breakdown by Target arXiv Category

| Category | Papers | Lean Strong | Lean Ctx | Other ITP | Model Checker | Protocol Verifier | SMT/SAT |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cs.CR` | 406 | 2 | 3 | 5 | 3 | 6 | 10 |
| `cs.DC` | 223 | 1 | 1 | 0 | 5 | 1 | 2 |
| `cs.IT` | 209 | 0 | 0 | 0 | 0 | 0 | 0 |
| `cs.NI` | 136 | 0 | 0 | 0 | 1 | 0 | 1 |
| `cs.RO` | 532 | 0 | 0 | 3 | 2 | 0 | 2 |
| `eess.SP` | 338 | 0 | 0 | 0 | 0 | 0 | 0 |
| `eess.SY` | 476 | 0 | 0 | 1 | 1 | 0 | 5 |
| `math.OC` | 410 | 0 | 0 | 1 | 0 | 0 | 3 |

## Beyond-Lean Tool Counts (Deterministic Full-Text Hits)

| Group : Tool | Papers |
| :--- | ---: |
| `smt_sat:smt_general` | 19 |
| `smt_sat:z3_cvc` | 7 |
| `model_checker:tla_plus` | 5 |
| `protocol_verifier:tamarin` | 5 |
| `protocol_verifier:proverif` | 5 |
| `itp:coq_rocq` | 5 |
| `model_checker:uppaal` | 4 |
| `itp:isabelle` | 4 |
| `protocol_verifier:easycrypt` | 3 |
| `itp:dafny` | 2 |
| `itp:why3_framac` | 2 |
| `itp:hol_light_hol4` | 2 |
| `model_checker:spin_promela` | 2 |
| `itp:pvs_acl2_mizar` | 2 |
| `model_checker:nusmv_nuxmv` | 1 |
| `itp:fstar` | 1 |
| `model_checker:cbmc_esbmc` | 1 |
| `itp:agda` | 1 |

## Lean Strong Hits (2 papers)

### [2511.15517](https://arxiv.org/abs/2511.15517) — Beluga: Block Synchronization for BFT Consensus Protocols
- **Primary / Target Cats:** `cs.CR` / ['cs.CR', 'cs.DC'] | **Submitted:** `2025-11-19` | **Source:** `html`
- **Matched Lean Signals:** `['in_lean_phrase', 'lean_prover_phrase', 'lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 36, 'tex_files_chars': 267756}`
- **Artifact URLs:** https://github.com/AUTHOR/REPO.git, https://github.com/PasinduTennage/mahi-mahi-consensus, https://github.com/RustCrypto/hashes, https://github.com/asonnino/beluga/blob/mysticeti-pull-attack/crates/orchestrator/assets/grafana-dashboard.json, https://github.com/asonnino/beluga/tree/mysticeti-pull-attack
- **Lean Repo `asonnino/mysticeti`:** `.lean` files=57, LoC=5603, theorems=139, defs=141, sorry=0, axiom=0, native_decide=0, unsafe=0, blueprint_attr=0, toolchain=`leanprover/lean4:v4.33.0`, ci=`['lake build']`
  - *lean_version:* `dissemination and its applications. In Proceedings of the 2021 ACM SIGSAC Conference on Computer and Communications Security, pp. 2705–2721. Cited by: §2.2.3, §2.2.3, Table 1. de Moura and Ullrich (2021) L. de Moura and S. Ullrich The Lean 4 Theorem Prover and Programming Language. In CADE, LNCS, pp. 625–635. External `
  - *lean_prover_phrase:* `eluga E The Pseudocode of the AC-based Push Protocol F Beluga Implementation G Experimental Setup H Pull Induction Attacks in DAG-based certified Synchronizer Protocol H.1 Review CBC-based Push Mechanism H.2 Pull Induction Attacks I Lean Formalisation I.1 What is Formalised I.2 What is Not Formalised I.3 Modelling Deta`
  - *in_lean_phrase:* `finition 1. The performance analyses of Beluga in the happy case and under adversarial settings are deferred to the full paper (Kichidis et al., 2025, Appendix C). All theorems in this section have been formalised with their proofs machine-checked in Lean (de Moura and Ullrich, 2021); the Lean code is provided in the a`

### [2511.11292](https://arxiv.org/abs/2511.11292) — KEM-IND-CCA-Preserving Compilation of Jasmin's ML-KEM
- **Primary / Target Cats:** `cs.PL` / ['cs.CR'] | **Submitted:** `2025-11-14` | **Source:** `html`
- **Matched Lean Signals:** `['lean_version']`
- **LaTeX Signals:** `{'theorem_envs': 7, 'tex_files_chars': 224325}`
- **Artifact URLs:** https://doi.org/10.5281/zenodo.21968144, https://github.com/Verified-zkEVM/VCV-io, https://github.com/formosa-crypto/formosa-mlkem
- **Lean Repo `Verified-zkEVM/VCV-io`:** `.lean` files=1777, LoC=402541, theorems=15478, defs=8024, sorry=13, axiom=7, native_decide=8, unsafe=7, blueprint_attr=0, toolchain=`leanprover/lean4:v4.36.0`, ci=`['lake build']`
  - *lean_version:* `nd Non-Interference Preservation for Compiler Transformations. Proc. ACM Program. Lang. 9, POPL (2025), 1506–1535. https://doi.org/10.1145/3704887 Verified-zkEVM (2024) Verified-zkEVM. 2024. VCV-io: Formalized Cryptography Proofs in Lean 4. Verified-zkEVM. https://github.com/Verified-zkEVM/VCV-io Accessed: 2026-04-22. `

## Lean Contextual-Only Hits (1 papers — review for recall)

- **[2511.15071](https://arxiv.org/abs/2511.15071)** (`cs.CR`) Towards Practical Zero-Knowledge Proof for PSPACE — `ulas, respectively. However, both frameworks lack support for quantifiers and therefore cannot address problems in PSPACE. A different direction is taken by zkPi [38], which encodes formal proofs from interactive theorem provers, primarily `
