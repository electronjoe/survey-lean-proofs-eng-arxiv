"""Unit tests for `scripts/check_paper_numbers.py` and ancillary/zip extraction in `src/profile_artifacts.py`."""

from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

from scripts.check_paper_numbers import (
    DEFAULT_PANEL,
    DEFAULT_TEX,
    run_all_checks,
)
from src.profile_artifacts import _extract_arxiv_ancillary_lean


def test_repo_paper_numbers_pass_consistency_gate() -> None:
    errors, stats = run_all_checks(
        tex_path=DEFAULT_TEX,
        panel_path=DEFAULT_PANEL,
    )
    assert errors == [], "Unexpected numeric or style drift:\n" + "\n".join(errors)
    assert stats["total_papers"] == 12613
    assert stats["t2_confirmed_v1"] == 68
    assert stats["t2_scanned_owned_repos"] == 51
    assert stats["inventory_eng_rows"] == 34
    assert stats["master_ledger_rows"] == 82
    assert stats["sandbox_repos"] == 23
    assert stats["layer_a_audited"] == 27


def test_detects_numeric_table_ci_loc_and_schema_drift(tmp_path: Path) -> None:
    tex = DEFAULT_TEX.read_text(encoding="utf-8")
    mutated = (
        tex.replace("12,613", "12,999")
        .replace(r"[1.01\%, 1.62\%]", r"[1.05\%, 1.69\%]")
        .replace("28,043", "27,000")
        .replace("5,259", "5,000")
        .replace("Engineering algorithmic proofs", r"\texttt{eng\_algorithmic\_proof}", 1)
    )
    bad_tex = tmp_path / "main.tex"
    bad_tex.write_text(mutated, encoding="utf-8")

    errors, _ = run_all_checks(
        tex_path=bad_tex,
        panel_path=DEFAULT_PANEL,
    )
    joined = "\n".join(errors)
    assert "12,613" in joined
    assert "T2 Wilson CI" in joined
    assert "2611.26140" in joined
    assert "5,259" in joined
    assert "eng_algorithmic_proof" in joined


def test_extract_arxiv_ancillary_lean_direct_and_nested_tar(tmp_path: Path) -> None:
    # Build an inner Lean tarball nested inside an outer arXiv source tarball.
    inner_buf = io.BytesIO()
    with tarfile.open(fileobj=inner_buf, mode="w:gz") as itf:
        lean_bytes = b"import Mathlib\ntheorem demo : True := trivial\n"
        info = tarfile.TarInfo("pkg/Demo.lean")
        info.size = len(lean_bytes)
        itf.addfile(info, io.BytesIO(lean_bytes))
        tc_bytes = b"leanprover/lean4:v4.35.0\n"
        tc_info = tarfile.TarInfo("pkg/lean-toolchain")
        tc_info.size = len(tc_bytes)
        itf.addfile(tc_info, io.BytesIO(tc_bytes))
    inner_raw = inner_buf.getvalue()

    outer_buf = io.BytesIO()
    with tarfile.open(fileobj=outer_buf, mode="w:gz") as otf:
        arc_info = tarfile.TarInfo("anc/demo_lean.tar.gz")
        arc_info.size = len(inner_raw)
        otf.addfile(arc_info, io.BytesIO(inner_raw))
        tex_bytes = b"\\documentclass{article}\\begin{document}Hi\\end{document}\n"
        tex_info = tarfile.TarInfo("main.tex")
        tex_info.size = len(tex_bytes)
        otf.addfile(tex_info, io.BytesIO(tex_bytes))

    prof = _extract_arxiv_ancillary_lean(outer_buf.getvalue(), "2611.99999", tmp_path)
    assert prof is not None
    assert prof["host"] == "arxiv_ancillary"
    assert prof["repo"] == "arxiv-anc/2611.99999"
    assert prof["lean_file_count"] == 1
    assert prof["lean_toolchain"] == "leanprover/lean4:v4.35.0"
    assert prof["lean_static_counts"]["loc_nonempty"] == 2
    assert prof["lean_static_counts"]["theorem_decl"] == 1
    assert prof["extracted_archives"] == ["anc/demo_lean.tar.gz"]


def test_extract_arxiv_ancillary_lean_nested_zip(tmp_path: Path) -> None:
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr("proj/Main.lean", "def x : Nat := 1\n#print axioms x\n")
    zraw = zbuf.getvalue()

    outer_buf = io.BytesIO()
    with tarfile.open(fileobj=outer_buf, mode="w:gz") as otf:
        info = tarfile.TarInfo("anc/lean_pkg.zip")
        info.size = len(zraw)
        otf.addfile(info, io.BytesIO(zraw))

    prof = _extract_arxiv_ancillary_lean(outer_buf.getvalue(), "2611.88888", tmp_path)
    assert prof is not None
    assert prof["lean_file_count"] == 1
    assert prof["lean_static_counts"]["loc_nonempty"] == 2
    assert prof["lean_static_counts"]["print_axioms"] == 1
