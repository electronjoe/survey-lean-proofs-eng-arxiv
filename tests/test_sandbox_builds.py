"""Unit tests validating sandboxed Docker build logs, summary parity, and security invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SANDBOX_OUT = REPO_ROOT / "artifacts" / "sandbox_builds"


def test_sandbox_results_schema_and_security_invariants() -> None:
    summary = json.loads((SANDBOX_OUT / "summary.json").read_text(encoding="utf-8"))
    all_records = []

    for sl, expected_n in (("2026-11", 11), ("2026-05", 3)):
        data = json.loads((SANDBOX_OUT / f"results_{sl}.json").read_text(encoding="utf-8"))
        assert data["slice_id"] == sl
        inv = data["security_invariants"]
        assert inv["network_mode"] == "none"
        assert inv["user"] == "65534:65534"
        assert inv["cap_drop"] == "ALL"
        assert inv["no_new_privileges"] is True
        assert inv["readonly_source_mount"] is True

        recs = data["records"]
        assert len(recs) == expected_n
        for r in recs:
            assert r["network_mode"] == "none"
            assert "--network=none" in r["security_flags"]
            assert "--cap-drop=ALL" in r["security_flags"]
            assert r["build_status"] in ("pass", "fail_packaging", "fail_missing_local_dep", "fail_build", "timeout")
            if r["build_status"] == "pass":
                assert r["exit_code"] == 0
                assert r["total_theorems_checked"] > 0
                assert "axiom_check_error" not in r
        all_records.extend(recs)

    ov = summary["overall"]
    assert ov["total_attempted"] == len(all_records) == 14
    assert ov["pass_out_of_box"] == sum(1 for r in all_records if r["build_status"] == "pass")
    assert ov["total_theorems_checked_ootb"] == sum(
        int(r["total_theorems_checked"]) for r in all_records if r["build_status"] == "pass"
    )
    assert ov["of_reduce_bool_repos_ootb"] == []
    assert ov["fail_build_or_other"] == 0


def test_static_src_never_invokes_lake_or_lean() -> None:
    """Enforce the strict security boundary in sandbox/README.md: src/ never executes lake or lean."""
    forbidden = re.compile(r"""subprocess\.(?:run|Popen|check_call|check_output)\s*\(\s*\[\s*['"](?:lake|lean|elan)['"]""")
    for py in sorted((REPO_ROOT / "src").rglob("*.py")):
        txt = py.read_text(encoding="utf-8")
        assert not forbidden.search(txt), f"Security boundary violation: {py} invokes lake/lean/elan"
