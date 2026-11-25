#!/usr/bin/env python3
"""Build a clean, anonymized double-blind review artifact zip.

Packages:
  - src/
  - scripts/ (excluding export_blind_artifact.py, which lists forbidden author tokens)
  - workflows/
  - artifacts/
  - sandbox/
  - tests/
  - pyproject.toml
  - uv.lock
  - LICENSE (with author/institution copyright line anonymized)
  - README.md (auto-generated anonymized reproduction guide)

Excludes:
  - docs/, papers/, data/, dist/, .git/, .venv/, __pycache__/, *.pyc

After building the archive, scans every included text file to verify that ZERO
author/institution identifying tokens appear anywhere inside the zip.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "dist" / "blind_artifact.zip"

INCLUDE_DIRS = ("src", "scripts", "workflows", "artifacts", "sandbox", "tests")
INCLUDE_FILES = ("pyproject.toml", "uv.lock")
SKIP_REL_PATHS = {"scripts/export_blind_artifact.py"}

FORBIDDEN_TOKENS = (
    "Moeller",
    "Krishnamachari",
    "ANRG",
    "USC",
    "electronjoe",
)

ANONYMIZED_README = """# Replication Package: Longitudinal Empirical Study of Lean 4 Adoption in Engineering arXiv Preprints

*(Double-blind review artifact — author and institutional identifiers removed.)*

## Contents

- `src/` — Deterministic, zero-token Python pipeline (OAI-PMH ingestion, HTML5/PDF full-text screening, static LaTeX/GitHub/GitLab/Zenodo/arXiv-ancillary profiling, Stage-2 recall calibration, artifact export, longitudinal analysis, and zero-DB vector figure generation).
- `scripts/` — Canonical 15-category artifact synthesizer (`build_unified_15cat_artifacts.py`), paper-to-artifact numeric consistency gate (`check_paper_numbers.py`), BibTeX hygiene auditor (`audit_bib.py`), IRR preparation/scoring (`prepare_stage4_irr.py`, `compute_irr.py`), off-arXiv bibliometric probe (`probe_off_arxiv.py`), and provenance pinning (`pin_phase2_provenance.py`).
- `workflows/` — Parallel read-only LLM classification (`classify_candidates.py`) and adversarial Layer-A semantic fidelity audit (`audit_layer_a.py`) prompts and strict JSON schemas.
- `artifacts/` — Version-controlled, license-safe structured outputs centered on the canonical unified 15-category dataset (`unified_15cat_panel.json`: 12,613 preprints across T0/T1/T2, 82 confirmed Lean preprints, 27 Layer-A semantic audits, 23 compact Docker kernel builds, 250-paper Stage-2 recall calibration, 8-paper operational-FV boundary audit, off-arXiv probe, and blinded human IRR), plus per-slice and per-stage JSON logs.
- `sandbox/` — Clean-room `--network=none` Docker harness (`Dockerfile`, `check_axioms.lean`, `container_entry.py`, `run_sandbox_audit.py`) for dynamic `lake build` and programmatic `Lean.collectAxioms` verification.
- `tests/` — Unit and integrity test suite covering deterministic detectors, Lean lexer, canonical 15-category panel parity, sandbox logs, off-arXiv classification, IRR scoring, BibTeX hygiene, and numeric gate logic.

## Quick Verification

```bash
uv sync --dev
uv run pytest
uv run python -m src.generate_figures --out-dir /tmp/repro_figures
```

Note: Heavy ephemeral SQLite databases (`data/*.db`), cloned third-party Lean repositories (`data/repos/`), and non-anonymous manuscript sources (`papers/`, `docs/`) are excluded from this archive for size, double-blind anonymity, and third-party licensing compliance; manuscript-specific file tests skip gracefully when `papers/` is absent, while all pipeline, artifact-parity, sandbox, IRR, and figure-generation checks run directly from `artifacts/`.
"""

SKIP_DIR_NAMES = {"__pycache__", ".venv", ".pytest_cache", ".git", "node_modules"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".db", ".sqlite", ".pdf"}


def _anonymize_license(raw: str) -> str:
    return re.sub(
        r"^Copyright \(c\) .*$",
        "Copyright (c) 2026 Anonymous Authors (double-blind review artifact)",
        raw,
        flags=re.MULTILINE,
    )


def _iter_source_files(root: Path) -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    for fname in INCLUDE_FILES:
        p = root / fname
        if p.is_file():
            items.append((p, fname))
    for dname in INCLUDE_DIRS:
        dpath = root / dname
        if not dpath.is_dir():
            continue
        for p in sorted(dpath.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if any(part in SKIP_DIR_NAMES for part in rel.parts):
                continue
            if rel.as_posix() in SKIP_REL_PATHS:
                continue
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            items.append((p, rel.as_posix()))
    return items


def verify_zip_anonymity(zip_path: Path) -> list[str]:
    """Return a list of '<arcname>: <token>' violations found in the zip archive."""
    violations: list[str] = []
    # Use word boundaries for short acronyms (ANRG, USC) to avoid matching substrings like 'manuscript' or 'PlusCal'.
    token_patterns = [
        (tok, re.compile(rf"\b{re.escape(tok)}\b", re.IGNORECASE))
        for tok in FORBIDDEN_TOKENS
    ]
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            raw = zf.read(info.filename)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for tok, pat in token_patterns:
                if pat.search(text):
                    violations.append(f"{info.filename}: matched forbidden token {tok!r}")
    return violations


def build_blind_artifact(out_path: Path = DEFAULT_OUT, repo_root: Path = REPO_ROOT) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    files = _iter_source_files(repo_root)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src_path, arcname in files:
            zf.write(src_path, arcname=arcname)
        license_path = repo_root / "LICENSE"
        if license_path.is_file():
            zf.writestr("LICENSE", _anonymize_license(license_path.read_text(encoding="utf-8")))
        zf.writestr("README.md", ANONYMIZED_README)

    violations = verify_zip_anonymity(out_path)
    if violations:
        out_path.unlink(missing_ok=True)
        msg = "Blind artifact anonymity check FAILED:\n  - " + "\n  - ".join(violations)
        raise RuntimeError(msg)

    size_kb = out_path.stat().st_size / 1024.0
    print(f"Built verified blind artifact: {out_path} ({len(files) + 2} files, {size_kb:.1f} KiB, 0 leaks)")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Build an anonymized double-blind review zip archive.")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output zip path (default: dist/blind_artifact.zip).")
    args = ap.parse_args()
    try:
        build_blind_artifact(out_path=args.out)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
