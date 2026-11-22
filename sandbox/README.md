# Isolated Execution Sandbox (`lake build` & `#print axioms`)

This directory defines the strict security boundary separating **static analysis** (`src/`) from future **dynamic Lean 4 kernel verification** (`lake build`, `lean4checker`, `SafeVerify`, and `#print axioms`) on untrusted third-party repositories.

## Security Boundary Contract

Untrusted Lean 4 repositories can execute arbitrary code during `lake build` via:
- `lakefile.lean` metaprogramming / custom build scripts
- Lean `#eval`, `unsafe`, `@[implemented_by]`, or `native_decide`
- Malicious Git submodules or build hooks

Therefore, **no script under `src/` ever invokes `lake` or `lean`**. All dynamic verification runs exclusively inside an ephemeral container orchestrated from `sandbox/` with the following mandatory isolation invariants:

1. **Zero network access during builds:** `--network=none` during `lake build` and `#print axioms` (any pre-fetched Mathlib `.olean` cache or toolchain is mounted read-only or prepared in a separate non-repo base image layer).
2. **Read-only source mounts:** Third-party repositories from `data/repos/<owner>/<repo>` are copied into an ephemeral container scratch volume or mounted `:ro` with build outputs directed to a disposable tmpfs/workdir.
3. **Unprivileged execution:** Run as a non-root UID/GID (`--user 65534:65534`), `--cap-drop=ALL`, and `--security-opt=no-new-privileges:true`.
4. **Hard resource limits:** Enforce explicit `--cpus`, `--memory`, `--pids-limit`, and wall-clock timeouts (e.g., 30 minutes per repository) to bound proof-search/compilation DoS.
5. **Structured output only:** The sandbox emits only compact, license-safe JSON logs conforming to [`artifacts/sandbox_builds/README.md`](../artifacts/sandbox_builds/README.md)—never committing third-party source trees or `.olean` artifacts.

## Planned Layout

```text
sandbox/
  README.md                 # This security boundary specification
  Dockerfile                # (Planned) Minimal elan + Lean 4 toolchain runner image
  run_sandbox_audit.py      # (Planned) Orchestrator invoking docker run --network=none
  check_axioms.lean         # (Planned) Harness invoking #print axioms on exported theorems
```
