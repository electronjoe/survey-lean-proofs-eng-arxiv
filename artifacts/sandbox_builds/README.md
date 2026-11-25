# Sandboxed Kernel Build Results (`lake build` & `#print axioms`)

This directory stores structured, license-safe JSON logs produced by isolated Docker builds executed under [`sandbox/`](../../sandbox/README.md).

## Archived Files & Schema

- `results_2026-11.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **11** standalone compact (`<15k` LoC) initial-8 T2 repositories (`9/11` OOTB pass, `3,026` theorems audited OOTB + `64` synthetic).
- `results_2026-05.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **3** contemporaneous initial-8 T1 scanned repositories (`2/3` OOTB pass, `164` theorems audited OOTB).
- `summary.json` — Aggregate cross-slice ground-truth metrics for the frozen initial-8 compact cohort (`n = 14`, verified by `tests/test_sandbox_builds.py`).
- `results_plus7_2026-11.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **3** compact (`<15k` LoC) `+7` `eng_algorithmic_proof` T2 repositories (`3/3` OOTB pass, `361` theorems audited OOTB, `2/3` axiom-clean, `2611.07395` dynamically corroborating 4 custom Julia/Arb axioms, `0/3` `sorryAx` / `Lean.ofReduceBool`).
- `results_plus7_math.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **6** remaining compact (`<15k` LoC) `+7` `pure_math_or_tcs` repositories (`2605.12537`, `2611.11641`, `2611.07494`, `2611.15711`, `2611.17223`, `2611.04575`), completing **`23/23 (100%)`** exhaustive all-role compact Docker kernel verification across all 15 categories (`18/23 = 78.3%` OOTB pass, `14/18` axiom-clean, `5,259` OOTB / `5,339` incl. synthetic theorems, `11/12` Gold OOTB and `11/11` [`100%`] Gold axiom-clean, `0/23` compile errors, `16` distinct toolchains, `1/23` `native_decide` [`2611.15711` Bronze pure-math/TCS; `0/11` engineering]).
- **Canonical unified 23-repository aggregate:** Synthesized into [`artifacts/unified_15cat_panel.json`](../unified_15cat_panel.json) (`sandbox_builds`) and consumed directly by `src/generate_figures.py` and `scripts/check_paper_numbers.py`.

### `results_<slice_id>.json`
One compact record per attempted Lean 4 repository build (strictly metadata and verifier summaries—never third-party source code or `.olean` build caches):

```json
{
  "schema_version": "1.0",
  "slice_id": "2026-11",
  "runner_image": "lean-survey-sandbox:v1",
  "records": [
    {
      "arxiv_id": "2611.XXXXX",
      "repo": "owner/repo",
      "commit_sha": "0000000000000000000000000000000000000000",
      "lean_toolchain": "leanprover/lean4:v4.34.0",
      "executed_at": "2026-12-01T00:00:00Z",
      "network_mode": "none",
      "timeout_sec": 1800,
      "exit_code": 0,
      "build_status": "pass",
      "wall_time_sec": 42.7,
      "axioms_by_theorem": {
        "Main.theorem_one": ["propext", "Classical.choice", "Quot.sound"]
      },
      "nonstandard_axioms_detected": [],
      "sorry_ax_detected": false,
      "of_reduce_bool_detected": false,
      "error_summary": ""
    }
  ]
}
```

## Security Invariant
- All untrusted `lake build` and `#print axioms` commands MUST execute inside the isolated container defined under [`sandbox/`](../../sandbox/README.md) with `--network=none`, read-only source mounts, and strict CPU/memory/time limits.
- Static analysis scripts in `src/` never invoke `lake` or `lean`.
