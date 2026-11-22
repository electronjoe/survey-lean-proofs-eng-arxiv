#!/usr/bin/env python3
"""Build a clean, anonymized double-blind review artifact zip.

Packages:
  - src/
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

INCLUDE_DIRS = ("src", "workflows", "artifacts", "sandbox", "tests")
INCLUDE_FILES = ("pyproject.toml", "uv.lock")

FORBIDDEN_TOKENS = (
    "Moeller",
    "Krishnamachari",
    "ANRG",
    "USC",
    "electronjoe",
)

ANONYMIZED_README = """# Replication Package: Longitudinal Survey of Lean 4 Adoption in Engineering arXiv Preprints

*(Double-blind review artifact — author and institutional identifiers removed.)*

## Contents

- `src/` — Deterministic, zero-token Python pipeline (OAI-PMH ingestion, HTML5/PDF full-text screening, static LaTeX/GitHub/GitLab/Zenodo profiling, Stage-2 recall calibration, artifact export, longitudinal analysis, and zero-DB figure generation).
- `workflows/` — Parallel LLM classification (`classify_candidates.py`) and adversarial Layer-A semantic fidelity audit (`audit_layer_a.py`) prompts and strict JSON schemas.
- `artifacts/` — Version-controlled, license-safe structured outputs (`longitudinal_summary.json`, `slices/manifest.json`, per-slice `classifications.json`, `layer_a_audits.json`, `recall_calibration.json`, and `figure_inputs.json`).
- `sandbox/` — Security boundary specification for isolated Docker `lake build` and `#print axioms` verification.
- `tests/` — Unit tests for deterministic Lean/Beyond-Lean regex detectors, the comment-stripping Lean lexer, and LaTeX blueprint/AI-disclosure scanners.

## Quick Verification

```bash
uv sync --dev
uv run pytest
uv run python -m src.generate_figures --out-dir /tmp/repro_figures
```

Note: Heavy ephemeral SQLite databases (`data/*.db`) and cloned third-party Lean repositories (`data/repos/`) are excluded from this archive for size and third-party licensing compliance; all figures regenerate directly from `artifacts/`.
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
