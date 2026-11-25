"""Unit tests for `scripts/audit_bib.py` BibTeX parser and hygiene checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_bib import (
    check_offline_hygiene,
    extract_tex_citations,
    parse_bib,
)


def test_parse_and_clean_bib_passes() -> None:
    bib = """
@misc{demo2026,
  author        = {Jane Doe and John Smith},
  title         = {{Verified Bounds with $k=m^{2/3}$}},
  year          = {2026},
  eprint        = {2611.00001},
  archivePrefix = {arXiv},
  primaryClass  = {math.OC}
}
"""
    entries, parse_errors = parse_bib(bib)
    assert parse_errors == []
    assert len(entries) == 1
    assert entries[0].fields["title"] == "{Verified Bounds with $k=m^{2/3}$}"
    assert check_offline_hygiene(entries, []) == []


def test_detects_placeholder_authors_and_raw_utf8() -> None:
    bib = """
@misc{bad1,
  author        = {{Tool Authors}},
  title         = {Placeholder Entry},
  year          = {2026},
  eprint        = {2604.12345},
  archivePrefix = {arXiv}
}
@misc{bad2,
  author        = {Alice Müller and others},
  title         = {Truncated Entry},
  year          = {2026},
  eprint        = {2609.12345},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI}
}
"""
    entries, parse_errors = parse_bib(bib)
    assert parse_errors == []
    errs = check_offline_hygiene(entries, [])
    assert any("placeholder/truncated" in e and "bad1" in e for e in errs)
    assert any("missing 'primaryClass'" in e and "bad1" in e for e in errs)
    assert any("placeholder/truncated" in e and "bad2" in e for e in errs)
    assert any("non-ASCII" in e and "bad2" in e for e in errs)


def test_extract_tex_citations_ignores_comments() -> None:
    tex = r"""
See~\cite{alpha, beta} and \citep[Section 2]{gamma}.
% \cite{commented_out}
"""
    assert extract_tex_citations(tex) == {"alpha", "beta", "gamma"}


def test_repo_references_bib_passes_offline_audit() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    bib_path = repo_root / "papers" / "shared" / "references.bib"
    tex_path = repo_root / "papers" / "arxiv-empirical" / "main.tex"
    if not bib_path.is_file() or not tex_path.is_file():
        pytest.skip("Manuscript sources under papers/ are excluded from the blind artifact.")
    entries, parse_errors = parse_bib(bib_path.read_text(encoding="utf-8"))
    assert parse_errors == []
    assert check_offline_hygiene(entries, [tex_path]) == []
