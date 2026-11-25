# Off-arXiv Engineering Bibliometric Check (TechRxiv, engrXiv, and OpenAlex)

> **Generated:** `2026-11-25T01:45:33Z` · **Window:** `2025-01-01` – `2026-11-25` · **Cost:** 0 LLM tokens · **Artifact:** [`artifacts/off_arxiv_probe.json`](../artifacts/off_arxiv_probe.json)

## 1. Executive Summary

To test whether arXiv venue selection bias masks substantial hidden Lean 4 theorem-proving adoption in non-arXiv engineering channels (IEEE, mechanical/civil/industrial engineering), we executed a deterministic zero-token bibliometric probe across **TechRxiv** (IEEE's preprint server), **engrXiv** (Engineering Archive), and **OpenAlex** (global scholarly index) covering **2025–2026**:

1. **Zero Lean 4 / Mathlib preprints on TechRxiv & engrXiv (`0 / 10,511`, 95% UB `0.029%`):** Across **7,849** TechRxiv preprints and **2,662** engrXiv preprints published in 2025–2026, Crossref queries for `Mathlib` and `leanprover` return **0 / 0** hits on both servers, and every raw `"Lean 4"` match (**7** on TechRxiv, **6** on engrXiv) is a domain false positive (Lean Six Sigma, Lean Manufacturing, Lean Hydrogen Combustion, or Time-Series Lean Notation).
2. **OpenAlex independently corroborates the 2026 global Lean/Mathlib inflection (`235 → 3,632`, `15.5×` YoY):** Across all scholarly disciplines in OpenAlex, `Mathlib`-matching works jumped **`15.5×`** from 2025 to 2026 (`3,867` total), heavily concentrated in Computer Science and Mathematics.
3. **Engineering represents only `1.42%` (`55/3,867`) of OpenAlex `Mathlib` works—and `30.9%` (`17/55`) already have an arXiv version:** Out of `2,313,125` total OpenAlex Engineering (`fields/22`) works in 2025–2026, only **`55`** match `Mathlib` (`0.24` per 10,000 works; `0` in 2025 → `55` in 2026), leaving only **`38`** off-arXiv-only Engineering `Mathlib` records worldwide. This confirms that our arXiv-measured disciplinary bifurcation and near-zero adoption outside optimization/control/info-theory/game-theory/dynamics are not artifacts of arXiv sampling.

## 2. Engineering Preprint Servers (Crossref API, 2025-01-01 to 2026-11-25)

| Preprint Server | Crossref Prefix | Total 2025–2026 Records | `"Lean 4"` Raw Hits | `Mathlib` Hits | `leanprover` Hits | Confirmed Lean 4 TP | 95% Clopper–Pearson UB |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **TechRxiv** (IEEE) | `10.36227` | 7,849 | 7 (all FP) | 0 | 0 | **0** | 0.038% |
| **engrXiv** (Eng. Archive) | `10.31224` | 2,662 | 6 (all FP) | 0 | 0 | **0** | 0.113% |
| **Combined** | — | **10,511** | **13** (all FP) | **0** | **0** | **0** | **0.029%** |

## 3. OpenAlex Global `Mathlib` Distribution by Primary Field (2025–2026)

| OpenAlex Primary Field | `Mathlib` Works (2025–2026) | Share (%) |
| :--- | ---: | ---: |
| Computer Science (`17`) | 1,612 | 41.69% |
| Mathematics (`26`) | 1,542 | 39.88% |
| Physics and Astronomy (`31`) | 426 | 11.02% |
| Engineering (`22`) | 55 | 1.42% |
| Arts and Humanities (`12`) | 51 | 1.32% |
| Economics, Econometrics and Finance (`20`) | 41 | 1.06% |
| Decision Sciences (`18`) | 39 | 1.01% |
| Social Sciences (`33`) | 27 | 0.70% |

### 3.1 OpenAlex Engineering (`fields/22`) `Mathlib` Breakdown (`n = 55`)

- **Year split:** `0` (2025) → `55` (2026)
- **arXiv vs. Off-arXiv:** **`17/55` (`30.9%`)** have an arXiv location/DOI; **`38/55` (`69.1%`)** are off-arXiv-only.
- **Companion Engineering (`fields/22`) queries:** `"Lean 4" formalization` = `52` works; `"Lean 4" "theorem prover"` = `14` works.

| Off-arXiv-Only OpenAlex Engineering `Mathlib` Work (2025–2026) | Year | Primary Source | Subfield |
| :--- | :---: | :--- | :--- |
| Lean 4 formalization for "Spectral stability for strong ideal-gas shock layers" | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| The Vibrating String with Formal Verification in Lean 4. La Conjecture de la Cordelette Vibrante Vérification  | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| The Frohmanian Tether: A Machine-Checked Audit of Its Architecture and Obstructions | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Aerospace Engineering |
| Weyl's boundary-layer theorems formalised in Lean 4: existence and uniqueness for the Blasius and Homann probl | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| Syntonic Nav: Against Adaptive Filters | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Aerospace Engineering |
| lean-mechanics: classical, continuum and discrete mechanics in Lean 4 | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Ku-Mellin-PATP: reproducibility code | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| TH44 / VM-2 Exact Non-Commuting Collapse Surface | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| ITU Tier 1+ #4: Semiconductor Scaling (K_semi) | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Electrical and Electronic Engineering |
| SpectralDissipationInvariant: Machine-Checked Lean 4 Quadratic Energy & L² Convergence Criterion for Dissipati | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| ITU Tier 1+ #13: Robotics (K_robot) | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| ns-lean4-pipeline: Reproducibility artifact for "A Scaling Invariant at Direction-Field Creases in 3D Navier-S | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| Metriplectic Completion of the Frohmanian Symplectic Tether: An Assembled Finite-Dimensional Viscous System, t | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| A lossless four-bus power system with 18 real power flow solutions | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Electrical and Electronic Engineering |
| TH43: The Effective Collapse Threshold under Online Estimation | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Complete Evolution Representations for Spatial Rigid-Body Contact Dynamics | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Cyclic Industrial Symbiosis: A Lean Proof of the N-Partner Product Condition | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Industrial and Manufacturing Engineering |
| Complete Evolution Representations for Planar Rigid-Body Contact Dynamics | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| A Local Displacement-Only Action for an Odd-Mass Continuum Model | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Mechanics of Materials |
| TH47 / VC-1: Universal Vector Converse | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| The Geometric Siphon: research repository | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| The Identification Duality | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Minimum inter-event time for ordinal (Kendall τ_b) event triggers: proofs, counterexamples and an open conject | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| The Starflower Framework: A Unified Theory of Structural Computational Invariance and Bio-Mimetic Robotic Arch | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Electrical and Electronic Engineering |
| Precedence-constrained Scheduling of Unit Jobs is Polynomial for Every Fixed Number of Machines | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Industrial and Manufacturing Engineering |
| Syntonic Nav V2.0: A Navigation Filter with No Parameter Table | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Aerospace Engineering |
| The Syntonic Capacity Theorem and Extensions: Gaussian, Correlated, and Non-Gaussian Adaptive-Tracking Bounds | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Theorem U′-Local: The Local Exponent Law of the Syntonic Window | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Aerospace Engineering |
| Syntonic Nav: Against Truth-Tuned Rivals | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Aerospace Engineering |
| Applied Identity Physics: Every Power-Limited Drive Is One Relation — a · α · v_e = 2, the Specific-Mass Decom | 2026 | PhilPapers (PhilPapers Foundation) | Aerospace Engineering |
| Experimental Realization of Zero-Payload Interplanetary Data Teleportation via Algorithmic Topological Resonan | 2026 | Research Square | Electrical and Electronic Engineering |
| Independently Checkable Certificates for Connected DC Optimal Transmission Switching | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Electrical and Electronic Engineering |
| Vector/Matrix Syntony: Matrix-Geometric-Mean Scaling and Per-Mode Capacity for Multi-Axis Adaptive Systems | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Control and Systems Engineering |
| Applied Identity Physics Identity Vector Amplification-IVA Peak, One Corridor Across Exhaust Velocity, Mass Ra | 2026 | PhilPapers (PhilPapers Foundation) | Aerospace Engineering |
| Uniform Inf–Sup Stability of Quartic and Quintic Scott–Vogelius Elements on Freudenthal Meshes: A Protected Ra | 2026 | SSRN Electronic Journal | Computational Mechanics |
| Uniform inf–sup stability of quartic and quintic Scott–Vogelius elements on Freudenthal meshes: a protected ra | 2026 | Research Square | Computational Mechanics |
| SpectraNS-3D: a reproducible numerical methodology for unforced 3D incompressible Navier–Stokes vortex-tube st | 2026 | Zenodo (CERN European Organization for Nuclear Research) | Computational Mechanics |
| Asymptotic Subspace Consensus in Dynamic Networks | 2026 | DROPS (Schloss Dagstuhl – Leibniz Center for Informatics) | Control and Systems Engineering |
