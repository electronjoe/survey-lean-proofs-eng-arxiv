# Sandboxed Kernel Build Results (`lake build` & `#print axioms`)

This directory stores structured, license-safe JSON logs produced by isolated Docker builds executed under [`sandbox/`](../../sandbox/README.md).

## Archived Files & Schema

- `results_2026-11.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **11** standalone compact (`<15k` LoC) T2 repositories (`9/11` OOTB pass, `3,026` theorems audited OOTB + `64` synthetic).
- `results_2026-05.json` — Isolated build & programmatic `Lean.collectAxioms` logs for all **3** contemporaneous T1 scanned repositories (`2/3` OOTB pass, `164` theorems audited OOTB).
- `summary.json` — Aggregate cross-slice ground-truth metrics consumed by `src/generate_figures.py` and `scripts/check_paper_numbers.py`.

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
