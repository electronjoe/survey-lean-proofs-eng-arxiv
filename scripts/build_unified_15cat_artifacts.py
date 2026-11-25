#!/usr/bin/env python3
"""Canonical Unified 15-Category Artifact Synthesizer (`artifacts/unified_15cat_panel.json`).

Reads the frozen SQLite databases (read-only) and provenance/audit JSONs across all 15
engineering arXiv categories and all 3 matched 19-day temporal windows (T0, T1, T2) to emit
a single compact, git-tracked, license-safe (<350 KB) JSON source of truth used by:
  - `src/generate_figures.py` (all 6 publication figures; zero SQLite dependency in CI)
  - `papers/arxiv-empirical/main.tex` (all 9 main-text tables + Appendix A 82-paper ledger)
  - `scripts/check_paper_numbers.py` (programmatic CI numeric verification)

Zero LLM tokens consumed; `data/*.db` files are never modified.
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.analyze_phase_c1_15cat import (
    ALL15_CATEGORIES,
    EESS_ALL,
    EESS_NON_SY,
    ORIG8_CATEGORIES,
    PLUS7_CATEGORIES,
    PLUS7_RETROACTIVE_V2_INFO,
    ROLES_4WAY,
    SLICE_SPECS,
    compute_owned_loc_for_repo,
    load_db_records,
    rate_summary,
    select_primary_lean_repo,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "artifacts" / "unified_15cat_panel.json"

# Cited third-party/sibling repos excluded when selecting a paper's primary artifact
SKIP_CITED_REPOS = {
    "anthropics/fermats-last-theorem",
    "cameronfreer/lean4-skills",
    "oOo0oOo/lean-lsp-mcp",
    "leanprover/comparator",
    "optsuite/optlib",
    "MColbrook/AIM",
    "forgi86/control-theory-in-lean",
    "TauCetiProject/TauCeti",
    "ywatanabex/bp-degree-syzygies-lean",
    "zenodo/22643866",
    "zenodo/24118844",
    "harfe/fixed-point-theorems-lean4",
}

# Verified orig-8 retroactive v2 metadata (from longitudinal_summary.json)
ORIG8_RETROACTIVE_INFO: dict[str, dict[str, Any]] = {
    "2511.15517": {
        "slice": "T0",
        "v1_date": "2025-11-19",
        "lean_added_version": 2,
        "lean_added_date": "2026-06-29",
        "lag_days": 222,
        "note": "v1 had 0 Lean mentions; v2 (Jun 2026) adds Appendix I Lean 4 mechanization of Beluga (repo inaccessible).",
    },
    "2605.09552": {
        "slice": "T1",
        "v1_date": "2026-05-11",
        "lean_added_version": 2,
        "lean_added_date": "2026-10-20",
        "lag_days": 162,
        "note": "v1 had 0 Lean mentions; v2 (Oct 2026) adds 340.3k LoC Lean 4 formalization of Phases of Muon.",
    },
    "2605.19531": {
        "slice": "T1",
        "v1_date": "2026-05-20",
        "lean_added_version": 2,
        "lean_added_date": "2026-11-04",
        "lag_days": 168,
        "note": "v1 had 0 Lean mentions; v2 (Nov 2026) adds 34.3k LoC zero-dep Lean 4 formalization of Conflict-Freedom.",
    },
}

# Papers whose raw monorepo LoC differs from verified paper-owned subpackage LoC
ORIG8_SUBPACKAGE_NOTES: dict[str, str] = {
    "2611.09050": "Paper-specific subpackage (139,600 LoC) inside multi-paper PolynomialRealizationsProgram monorepo.",
    "2611.13584": "Paper-specific subpackage (55,300 LoC) inside multi-paper PolynomialRealizationsProgram monorepo.",
    "2611.15128": "Paper-specific 20-file AffineCombiner subpackage (4,963 LoC) inside leanEthereum/leanVM monorepo.",
}

POST_UNPACKING_NOTES: dict[str, str] = {
    "2611.26140": "28,043 LoC recovered after statically unpacking arXiv ancillary archive; Stage-4 tier/flags frozen from initial pass.",
    "2611.16781": "34,579 LoC recovered after statically unpacking zipped GitHub archive; Stage-4 tier/flags frozen from initial pass.",
    "2611.12585": "60,664 LoC recovered after statically unpacking arXiv ancillary archive; Stage-4 tier/flags frozen from initial pass.",
}

# Harmonized static flag set: zero-dep operational_system_fv repos should not carry Mode3_CustomDefs
ZERO_DEP_OPFV_MODE3_EXEMPT = {"2611.10810", "2605.19531"}


def _clopper_pearson_upper_pct(k: int, n: int, alpha: float = 0.05) -> float:
    if n <= 0:
        return 100.0
    if k == 0:
        return round(100.0 * (1.0 - alpha ** (1.0 / n)), 4)
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        cdf = sum(math.comb(n, i) * (mid**i) * ((1.0 - mid) ** (n - i)) for i in range(k + 1))
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return round(100.0 * hi, 4)


def _safe_mult(a: float, b: float) -> float | None:
    return round(a / b, 2) if b > 0 else None


def _harmonize_static_flags(arxiv_id: str, role_4way: str, raw_flags: list[str]) -> list[str]:
    flags = list(raw_flags)
    if arxiv_id in ZERO_DEP_OPFV_MODE3_EXEMPT or (
        role_4way == "operational_system_fv" and "Mode3_CustomDefs" in flags
    ):
        flags = [f for f in flags if f != "Mode3_CustomDefs"]
    return sorted(set(flags))


def _summarize_paper_group(papers: list[dict[str, Any]], denom: int) -> dict[str, Any]:
    locs = [p["primary_owned_loc"] for p in papers if (p.get("primary_owned_loc") or 0) > 0]
    raw_locs = [p["primary_raw_loc"] for p in papers if (p.get("primary_raw_loc") or 0) > 0]
    risk_counts: Counter[str] = Counter()
    for p in papers:
        for fl in p.get("static_risk_flags", []):
            risk_counts[fl] += 1
    strict_core = [p for p in papers if not p.get("borderline_flag")]
    return {
        **rate_summary(len(papers), denom),
        "strict_core_count": len(strict_core),
        "strict_core_pct": round(100.0 * len(strict_core) / max(denom, 1), 4),
        "borderline_count": len(papers) - len(strict_core),
        "paradigms": dict(sorted(Counter(p["authoring_paradigm"] for p in papers).items())),
        "tiers": dict(sorted(Counter(p["verification_tier"] for p in papers).items())),
        "ai_assistance": dict(sorted(Counter(p["ai_agent_assisted"] for p in papers).items())),
        "artifact_availability": dict(sorted(Counter(p["artifact_availability"] for p in papers).items())),
        "static_risk_flags": dict(sorted(risk_counts.items())),
        "scanned_owned_repos": len(locs),
        "total_owned_loc": sum(locs),
        "total_raw_loc": sum(raw_locs),
        "median_owned_loc": int(statistics.median(locs)) if locs else 0,
        "min_owned_loc": min(locs) if locs else 0,
        "max_owned_loc": max(locs) if locs else 0,
        "arxiv_ids": sorted(p["arxiv_id"] for p in papers),
    }


def _build_layer_a_section(confirmed_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    prov_orig = json.loads((REPO_ROOT / "artifacts" / "phase2_provenance.json").read_text(encoding="utf-8"))
    prov_c2 = json.loads((REPO_ROOT / "artifacts" / "phase_c2_plus7_audits.json").read_text(encoding="utf-8"))

    prov_by_id: dict[str, dict[str, Any]] = {}
    for r in prov_orig.get("records", []):
        prov_by_id[r["arxiv_id"]] = r
    for r in prov_c2.get("records", []):
        prov_by_id[r["arxiv_id"]] = r

    audit_files = [
        ("2026-11", "T2", REPO_ROOT / "artifacts" / "slices" / "2026-11" / "layer_a_audits.json"),
        ("2026-05", "T1", REPO_ROOT / "artifacts" / "slices" / "2026-05" / "layer_a_audits.json"),
        ("2026-11", "T2", REPO_ROOT / "artifacts" / "slices" / "2026-11" / "plus7_layer_a_audits.json"),
    ]

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for slice_id, short_id, path in audit_files:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for a in doc.get("audits", []):
            aid = a["arxiv_id"]
            if aid in seen:
                continue
            seen.add(aid)
            paper = confirmed_by_id.get(aid, {})
            prov = prov_by_id.get(aid, {})
            fl_check = (
                prov.get("theorems_compared_file_line_check")
                or (prov.get("layer_a") or {}).get("theorems_compared_file_line_check")
                or {}
            )
            records.append(
                {
                    "arxiv_id": aid,
                    "slice_id": slice_id,
                    "short_id": short_id,
                    "primary_category": paper.get("primary_category") or a.get("primary_category"),
                    "matched_15_cats": paper.get("matched_15_cats", []),
                    "role_4way": paper.get("role_4way") or a.get("role_4way"),
                    "authoring_paradigm": paper.get("authoring_paradigm") or a.get("authoring_paradigm"),
                    "verification_tier": paper.get("verification_tier") or a.get("verification_tier"),
                    "primary_owned_loc": paper.get("primary_owned_loc", 0),
                    "lean_in_v1": paper.get("lean_in_v1", True),
                    "repo_host": prov.get("repo_host"),
                    "repo_url": prov.get("repo_url"),
                    "commit_sha": prov.get("commit_sha"),
                    "commit_short_sha": prov.get("commit_short_sha"),
                    "zenodo_record_id": prov.get("zenodo_record_id"),
                    "lean_toolchain": prov.get("lean_toolchain"),
                    "overall_fidelity": a["overall_fidelity"],
                    "mode1_severity": a["mode1_statement_drift"]["severity"],
                    "mode2_severity": a["mode2_scope_downgrade"]["severity"],
                    "mode3_severity": a["mode3_definition_smuggling"]["severity"],
                    "mode4_severity": a["mode4_junk_or_vacuity"]["severity"],
                    "has_non_vacuity_witnesses": bool(a.get("has_non_vacuity_witnesses")),
                    "mathlib_anchoring_quality": a.get("mathlib_anchoring_quality"),
                    "theorems_compared_count": len(a.get("theorems_compared", [])),
                    "file_line_refs_total": int(fl_check.get("total_file_line_refs", 0)),
                    "file_line_refs_resolved": int(fl_check.get("resolved_in_bounds", 0)),
                }
            )

    records.sort(key=lambda r: (0 if r["short_id"] == "T2" else 1, r["arxiv_id"]))

    def _agg(sub: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(sub)
        nw = sum(1 for r in sub if r["has_non_vacuity_witnesses"])
        return {
            "count": n,
            "overall_fidelity": dict(sorted(Counter(r["overall_fidelity"] for r in sub).items())),
            "mode1_severity": dict(sorted(Counter(r["mode1_severity"] for r in sub).items())),
            "mode2_severity": dict(sorted(Counter(r["mode2_severity"] for r in sub).items())),
            "mode3_severity": dict(sorted(Counter(r["mode3_severity"] for r in sub).items())),
            "mode4_severity": dict(sorted(Counter(r["mode4_severity"] for r in sub).items())),
            "has_non_vacuity_witnesses_count": nw,
            "has_non_vacuity_witnesses_pct": round(100.0 * nw / max(n, 1), 1),
            "mathlib_anchoring_quality": dict(sorted(Counter(r["mathlib_anchoring_quality"] for r in sub).items())),
            "material_undisclosed_count": sum(
                1 for r in sub if r["overall_fidelity"] == "material_undisclosed_drift_or_risk"
            ),
            "file_line_refs_total": sum(r["file_line_refs_total"] for r in sub),
            "file_line_refs_resolved": sum(r["file_line_refs_resolved"] for r in sub),
        }

    eng_all = [r for r in records if r["role_4way"] == "eng_algorithmic_proof"]
    eng_t2 = [r for r in eng_all if r["short_id"] == "T2"]
    eng_t1 = [r for r in eng_all if r["short_id"] == "T1"]
    meta_all = [r for r in records if r["role_4way"] == "meta_formalization_system"]
    tcs_all = [r for r in records if r["role_4way"] == "pure_math_or_tcs"]
    t2_all = [r for r in records if r["short_id"] == "T2"]

    return {
        "total_audited": len(records),
        "total_file_line_refs": sum(r["file_line_refs_total"] for r in records),
        "resolved_file_line_refs": sum(r["file_line_refs_resolved"] for r in records),
        "summary": {
            "all_t1_t2": _agg(records),
            "all_t2": _agg(t2_all),
            "eng_algorithmic_proof_all": _agg(eng_all),
            "eng_algorithmic_proof_t2": _agg(eng_t2),
            "eng_algorithmic_proof_t1": _agg(eng_t1),
            "meta_formalization_system_all": _agg(meta_all),
            "pure_math_or_tcs_contrast": _agg(tcs_all),
        },
        "records": records,
    }


def _build_sandbox_section(confirmed_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sb_dir = REPO_ROOT / "artifacts" / "sandbox_builds"
    sources = [
        sb_dir / "results_2026-11.json",
        sb_dir / "results_2026-05.json",
        sb_dir / "results_plus7_2026-11.json",
        sb_dir / "results_plus7_math.json",
    ]
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for p in sources:
        if not p.is_file():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for r in doc.get("records", []):
            aid = r["arxiv_id"]
            if aid in seen:
                continue
            seen.add(aid)
            paper = confirmed_by_id.get(aid, {})
            syn = r.get("synthetic_env_check")
            rec = {
                "arxiv_id": aid,
                "slice_id": r["slice_id"],
                "short_id": "T2" if r["slice_id"] == "2026-11" else "T1",
                "primary_category": paper.get("primary_category"),
                "matched_15_cats": paper.get("matched_15_cats", []),
                "role_4way": paper.get("role_4way") or r.get("role_4way"),
                "static_verification_tier": paper.get("verification_tier") or r.get("static_verification_tier"),
                "owned_loc": paper.get("primary_owned_loc") or r.get("owned_loc") or 0,
                "repo": r.get("repo"),
                "commit_sha": r.get("commit_sha"),
                "commit_short_sha": r["commit_sha"][:7] if r.get("commit_sha") else None,
                "zenodo_record_id": r.get("zenodo_record_id"),
                "lean_toolchain": r.get("lean_toolchain"),
                "build_mode": r.get("build_mode"),
                "build_status": r.get("build_status"),
                "exit_code": r.get("exit_code"),
                "wall_time_sec": r.get("wall_time_sec"),
                "axiom_check_wall_time_sec": r.get("axiom_check_wall_time_sec"),
                "total_theorems_checked": int(r.get("total_theorems_checked") or 0),
                "standard_axioms_used": r.get("standard_axioms_used", []),
                "nonstandard_axioms_detected": r.get("nonstandard_axioms_detected", []),
                "sorry_ax_detected": bool(r.get("sorry_ax_detected", False)),
                "of_reduce_bool_detected": bool(r.get("of_reduce_bool_detected", False)),
                "trust_compiler_detected": bool(r.get("trust_compiler_detected", False)),
                "native_decide_detected": bool(
                    r.get("of_reduce_bool_detected", False)
                    or r.get("trust_compiler_detected", False)
                    or any("native_decide" in a for a in r.get("nonstandard_axioms_detected", []))
                ),
                "unbundled_path_deps": r.get("unbundled_path_deps", []),
                "synthetic_env_check": (
                    {
                        "toolchain_used": syn.get("toolchain_used"),
                        "mathlib_rev_used": syn.get("mathlib_rev_used"),
                        "build_status": syn.get("build_status"),
                        "wall_time_sec": syn.get("wall_time_sec"),
                        "total_theorems_checked": int(syn.get("total_theorems_checked") or 0),
                        "nonstandard_axioms_detected": syn.get("nonstandard_axioms_detected", []),
                        "sorry_ax_detected": bool(syn.get("sorry_ax_detected", False)),
                        "of_reduce_bool_detected": bool(syn.get("of_reduce_bool_detected", False)),
                    }
                    if syn
                    else None
                ),
            }
            records.append(rec)

    role_order = {r: i for i, r in enumerate(ROLES_4WAY)}
    records.sort(key=lambda r: (role_order.get(r["role_4way"], 9), 0 if r["short_id"] == "T2" else 1, r["owned_loc"], r["arxiv_id"]))

    def _agg(sub: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(sub)
        passed = [r for r in sub if r["build_status"] == "pass"]
        clean = [
            r
            for r in passed
            if not r["sorry_ax_detected"]
            and not r["of_reduce_bool_detected"]
            and not r["trust_compiler_detected"]
            and not r["nonstandard_axioms_detected"]
        ]
        fail_pkg = [r for r in sub if r["build_status"] == "fail_packaging"]
        fail_local = [r for r in sub if r["build_status"] == "fail_missing_local_dep"]
        fail_build = [
            r
            for r in sub
            if r["build_status"] in ("fail_build", "fail_network_dep", "timeout", "fail_runner")
        ]
        syn_pass = [r for r in fail_pkg if (r.get("synthetic_env_check") or {}).get("build_status") == "pass"]
        syn_clean = [
            r
            for r in syn_pass
            if not (r.get("synthetic_env_check") or {}).get("sorry_ax_detected")
            and not (r.get("synthetic_env_check") or {}).get("of_reduce_bool_detected")
            and not (r.get("synthetic_env_check") or {}).get("nonstandard_axioms_detected")
        ]
        t3 = [r for r in sub if r["static_verification_tier"] == "Tier3_Gold"]
        t3_pass = [r for r in t3 if r["build_status"] == "pass"]
        t3_clean = [r for r in t3 if r in clean]
        times = [float(r["wall_time_sec"]) for r in passed if r.get("wall_time_sec") is not None]
        thms_ootb = sum(r["total_theorems_checked"] for r in passed)
        thms_syn = sum(int((r.get("synthetic_env_check") or {}).get("total_theorems_checked") or 0) for r in syn_pass)
        distinct_toolchains = sorted({r["lean_toolchain"] for r in sub if r.get("lean_toolchain")})
        return {
            "total_attempted": n,
            "pass_out_of_box": len(passed),
            "pass_out_of_box_pct": round(100.0 * len(passed) / max(n, 1), 1),
            "pass_and_standard_axioms_only": len(clean),
            "pass_with_nonstandard_axioms": len(passed) - len(clean),
            "fail_packaging_no_lakefile": len(fail_pkg),
            "fail_missing_local_dep": len(fail_local),
            "fail_build_or_other": len(fail_build),
            "synthetic_env_pass_among_packaging_fails": len(syn_pass),
            "synthetic_env_clean_among_packaging_fails": len(syn_clean),
            "tier3_gold_attempted": len(t3),
            "tier3_gold_pass_out_of_box": len(t3_pass),
            "tier3_gold_clean_axioms": len(t3_clean),
            "total_theorems_checked_ootb": thms_ootb,
            "total_theorems_checked_incl_synthetic": thms_ootb + thms_syn,
            "median_pass_wall_time_sec": round(statistics.median(times), 2) if times else 0.0,
            "min_pass_wall_time_sec": round(min(times), 2) if times else 0.0,
            "max_pass_wall_time_sec": round(max(times), 2) if times else 0.0,
            "distinct_pinned_toolchains_count": len(distinct_toolchains),
            "distinct_pinned_toolchains": distinct_toolchains,
            "sorry_ax_repos_ootb": [r["arxiv_id"] for r in passed if r["sorry_ax_detected"]],
            "of_reduce_bool_repos_ootb": [r["arxiv_id"] for r in passed if r["of_reduce_bool_detected"]],
            "native_decide_repos_ootb": [r["arxiv_id"] for r in passed if r["native_decide_detected"]],
            "nonstandard_axiom_repos_ootb": [
                {"arxiv_id": r["arxiv_id"], "axioms": r["nonstandard_axioms_detected"]}
                for r in passed
                if r["nonstandard_axioms_detected"]
            ],
        }

    by_role = {
        role: _agg([r for r in records if r["role_4way"] == role])
        for role in ROLES_4WAY
        if any(r["role_4way"] == role for r in records)
    }

    return {
        "selection_criterion": "All standalone primary Lean 4 repositories with < 15,000 paper-owned non-empty LoC across all 15 categories and all 4 roles (T1 + T2).",
        "overall": _agg(records),
        "by_role": by_role,
        "by_slice": {
            "T2": _agg([r for r in records if r["short_id"] == "T2"]),
            "T1": _agg([r for r in records if r["short_id"] == "T1"]),
        },
        "records": records,
    }


def _build_recall_section() -> dict[str, Any]:
    r0 = json.loads((REPO_ROOT / "artifacts" / "slices" / "2026-11" / "recall_calibration.json").read_text(encoding="utf-8"))
    p7_path = REPO_ROOT / "artifacts" / "slices" / "2026-11" / "recall_calibration_plus7.json"
    r1 = json.loads(p7_path.read_text(encoding="utf-8")) if p7_path.is_file() else None

    gh_n = r0["gh_sample_size"] + (r1["gh_sample_size"] if r1 else 0)
    gh_acc = r0["gh_accessible_papers"] + (r1["gh_accessible_papers"] if r1 else 0)
    gh_repos = r0["gh_unique_repos_checked"] + (r1["gh_unique_repos_checked"] if r1 else 0)
    non_gh_n = r0["non_gh_sample_size"] + (r1["non_gh_sample_size"] if r1 else 0)
    total_neg = r0["total_stage2_negatives"] + (r1["total_stage2_negatives"] if r1 else 0)
    total_gh_neg = r0["total_github_linked_negatives"] + (r1["total_github_linked_negatives"] if r1 else 0)
    total_non_gh_neg = r0["total_non_github_negatives"] + (r1["total_non_github_negatives"] if r1 else 0)

    r1_confirmed_hits = (
        int((r1.get("manual_adjudication") or {}).get("confirmed_missed_lean_contributions", r1["gh_lean_hits_count"]))
        if r1
        else 0
    )
    confirmed_hits = int(r0["gh_lean_hits_count"]) + r1_confirmed_hits
    raw_tree_hits = int(r0["gh_lean_hits_count"]) + (int(r1["gh_lean_hits_count"]) if r1 else 0)

    return {
        "total_t2_stage2_negatives": total_neg,
        "total_t2_github_linked_negatives": total_gh_neg,
        "total_t2_non_github_negatives": total_non_gh_neg,
        "gh_sample_size": gh_n,
        "gh_accessible_papers": gh_acc,
        "gh_unique_repos_checked": gh_repos,
        "raw_tree_hits": raw_tree_hits,
        "confirmed_missed_lean_contributions": confirmed_hits,
        "confirmed_fn_95pct_upper_bound_pct": _clopper_pearson_upper_pct(confirmed_hits, gh_n),
        "confirmed_acc_fn_95pct_upper_bound_pct": _clopper_pearson_upper_pct(confirmed_hits, gh_acc),
        "non_gh_sample_size": non_gh_n,
        "non_gh_broad_meta_flags": len(r0.get("non_gh_broad_meta_flags", []))
        + (len(r1.get("non_gh_broad_meta_flags", [])) if r1 else 0),
        "seeds": [r0["seed"]] + ([r1["seed"]] if r1 else []),
        "adjudicated_raw_hits": (r1.get("manual_adjudication") or {}).get("adjudicated_hits", []) if r1 else [],
    }


def _select_orig8_raw_loc(repos: list[dict[str, Any]], fallback_owned: int) -> int:
    lean_repos = [
        rp
        for rp in repos
        if rp.get("lean_file_count", 0) > 0
        and rp.get("repo") not in SKIP_CITED_REPOS
        and int(rp.get("lean_static_counts", {}).get("loc_nonempty", 0) or 0) > 0
    ]
    if not lean_repos:
        return fallback_owned
    best = max(lean_repos, key=lambda rp: int(rp.get("lean_static_counts", {}).get("loc_nonempty", 0) or 0))
    return int(best.get("lean_static_counts", {}).get("loc_nonempty", 0) or 0)


def build_unified_panel() -> dict[str, Any]:
    long_orig = json.loads((REPO_ROOT / "artifacts" / "longitudinal_summary.json").read_text(encoding="utf-8"))
    adj_doc = json.loads(
        (REPO_ROOT / "artifacts" / "human_annotations" / "track1_4way_adjudication.json").read_text(encoding="utf-8")
    )
    adj_by_id = {r["arxiv_id"]: r for r in adj_doc["records"]}

    orig8_confirmed_meta: dict[str, dict[str, Any]] = {}
    for sl in long_orig["slices"]:
        for p in sl["confirmed_papers"]:
            orig8_confirmed_meta[p["arxiv_id"]] = p

    slices_out: list[dict[str, Any]] = []
    all_confirmed_papers: list[dict[str, Any]] = []
    retroactive_ledger: list[dict[str, Any]] = []
    t2_union_confirmed_v1: list[dict[str, Any]] = []
    t2_union_confirmed_latest: list[dict[str, Any]] = []
    t2_total_papers = 0

    for spec in SLICE_SPECS:
        slice_id = spec["slice_id"]
        short_id = spec["short_id"]

        orig8_recs = load_db_records(spec["orig8_db"])
        plus7_recs = load_db_records(spec["plus7_db"])

        union_recs: dict[str, dict[str, Any]] = {}
        for aid in sorted(set(orig8_recs.keys()) | set(plus7_recs.keys())):
            in_o8 = aid in orig8_recs
            in_p7 = aid in plus7_recs
            base = dict(orig8_recs[aid] if in_o8 else plus7_recs[aid])
            cats_o8 = set(orig8_recs[aid]["matched_target_cats"]) if in_o8 else set()
            cats_p7 = set(plus7_recs[aid]["matched_target_cats"]) if in_p7 else set()
            base["matched_15_cats"] = sorted((cats_o8 | cats_p7) & set(ALL15_CATEGORIES))

            if base["lean_usage_status"] == "lean_contributed":
                if aid in adj_by_id:
                    a = adj_by_id[aid]
                    base["role_4way"] = a["role_4way"]
                    base["verification_object"] = a["verification_object"]
                    base["role_decision_gate"] = a.get("role_decision_gate") or a.get("decision_gate")
                    base["borderline_flag"] = bool(a.get("is_borderline", a.get("borderline_flag", False)))
                    base["borderline_note"] = a.get("borderline_note", "") or ""
                else:
                    raw = base["raw_cls"] or {}
                    base["role_4way"] = raw.get("role_4way", "N/A")
                    base["verification_object"] = raw.get("verification_object", "N/A")
                    base["role_decision_gate"] = raw.get("role_decision_gate", "N/A")
                    base["borderline_flag"] = bool(raw.get("borderline_flag", False))
                    base["borderline_note"] = raw.get("borderline_note", "") or ""

                base["legacy_static_risk_flags"] = list(base["static_risk_flags"])
                base["static_risk_flags"] = _harmonize_static_flags(aid, base["role_4way"], base["static_risk_flags"])

                if aid in orig8_confirmed_meta:
                    om = orig8_confirmed_meta[aid]
                    base["lean_in_v1"] = not bool(om.get("is_retroactive_v2", False))
                    base["primary_repo"] = om.get("primary_repo")
                    pr = str(base["primary_repo"] or "")
                    if not pr:
                        base["primary_repo_host"] = None
                    elif pr.startswith("zenodo/"):
                        base["primary_repo_host"] = "zenodo"
                    elif pr.startswith("arxiv-anc/"):
                        base["primary_repo_host"] = "arxiv_ancillary"
                    elif pr == "subpackage":
                        base["primary_repo_host"] = "github"
                    else:
                        base["primary_repo_host"] = "github"
                    base["primary_owned_loc"] = int(om.get("primary_owned_loc") or 0)
                    base["primary_raw_loc"] = _select_orig8_raw_loc(base["repos"], base["primary_owned_loc"])
                    base["vendor_exclusion_note"] = ORIG8_SUBPACKAGE_NOTES.get(aid)
                    base["post_unpacking_note"] = POST_UNPACKING_NOTES.get(aid)
                    base["retroactive_info"] = ORIG8_RETROACTIVE_INFO.get(aid) if not base["lean_in_v1"] else None
                else:
                    is_retro = aid in PLUS7_RETROACTIVE_V2_INFO
                    base["lean_in_v1"] = not is_retro
                    prim_rp = select_primary_lean_repo(base["repos"])
                    if prim_rp is not None:
                        raw_loc, owned_loc, exc_note = compute_owned_loc_for_repo(prim_rp)
                        base["primary_repo"] = prim_rp["repo"]
                        base["primary_repo_host"] = prim_rp.get("host", "github")
                        base["primary_raw_loc"] = raw_loc
                        base["primary_owned_loc"] = owned_loc
                        base["vendor_exclusion_note"] = exc_note
                    else:
                        base["primary_repo"] = None
                        base["primary_repo_host"] = None
                        base["primary_raw_loc"] = 0
                        base["primary_owned_loc"] = 0
                        base["vendor_exclusion_note"] = None
                    base["post_unpacking_note"] = None
                    base["retroactive_info"] = PLUS7_RETROACTIVE_V2_INFO.get(aid) if is_retro else None

                paper_rec = {
                    "arxiv_id": aid,
                    "slice_id": slice_id,
                    "short_id": short_id,
                    "title": " ".join((base["title"] or "").split()),
                    "primary_category": base["primary_category"],
                    "matched_15_cats": base["matched_15_cats"],
                    "submitted_date": base["submitted_date"],
                    "updated_date": base["updated_date"],
                    "version": int(base["version"] or 1),
                    "lean_in_v1": bool(base["lean_in_v1"]),
                    "role_4way": base["role_4way"],
                    "verification_object": base["verification_object"],
                    "role_decision_gate": base["role_decision_gate"],
                    "borderline_flag": bool(base["borderline_flag"]),
                    "authoring_paradigm": base["authoring_paradigm"],
                    "verification_tier": base["verification_tier"],
                    "ai_agent_assisted": base["ai_agent_assisted"],
                    "artifact_availability": base["artifact_availability"],
                    "static_risk_flags": base["static_risk_flags"],
                    "primary_repo": base["primary_repo"],
                    "primary_repo_host": base["primary_repo_host"],
                    "primary_owned_loc": int(base["primary_owned_loc"]),
                    "primary_raw_loc": int(base["primary_raw_loc"]),
                    "vendor_exclusion_note": base["vendor_exclusion_note"],
                    "post_unpacking_note": base["post_unpacking_note"],
                    "retroactive_info": base["retroactive_info"],
                }
                all_confirmed_papers.append(paper_rec)
                if not paper_rec["lean_in_v1"]:
                    retroactive_ledger.append(
                        {
                            "arxiv_id": aid,
                            "short_id": short_id,
                            "primary_category": paper_rec["primary_category"],
                            "matched_15_cats": paper_rec["matched_15_cats"],
                            "role_4way": paper_rec["role_4way"],
                            "primary_owned_loc": paper_rec["primary_owned_loc"],
                            **(paper_rec["retroactive_info"] or {}),
                        }
                    )
            else:
                base["role_4way"] = "N/A"
                base["lean_in_v1"] = False
                base["primary_owned_loc"] = 0
                base["primary_raw_loc"] = 0

            union_recs[aid] = base

        recs = list(union_recs.values())
        total = len(recs)
        screened = sum(1 for r in recs if r["fetch_source"] != "failed")
        html_n = sum(1 for r in recs if r["fetch_source"] == "html")
        pdf_n = sum(1 for r in recs if r["fetch_source"] == "pdf")
        failed_n = total - screened
        revised_n = sum(1 for r in recs if int(r.get("version") or 1) > 1)
        meta_strong = sum(1 for r in recs if r["meta_lean_strong"])
        s2_strong = sum(1 for r in recs if r["has_lean_strong"])
        s2_ctx_only = sum(1 for r in recs if (not r["has_lean_strong"]) and r["has_lean_contextual"])
        s2_total = s2_strong + s2_ctx_only
        beyond_any = sum(
            1
            for r in recs
            if r["has_other_itp"] or r["has_model_checker"] or r["has_protocol_verifier"] or r["has_smt_sat"]
        )

        slice_confirmed_latest = [p for p in all_confirmed_papers if p["short_id"] == short_id]
        slice_confirmed_v1 = [p for p in slice_confirmed_latest if p["lean_in_v1"]]

        if short_id == "T2":
            t2_union_confirmed_v1 = slice_confirmed_v1
            t2_union_confirmed_latest = slice_confirmed_latest
            t2_total_papers = total

        per_cat: dict[str, Any] = {}
        for cat in ALL15_CATEGORIES:
            crecs = [r for r in recs if cat in r["matched_15_cats"]]
            cn = len(crecs)
            c_scr = sum(1 for r in crecs if r["fetch_source"] != "failed")
            c_prim = sum(1 for r in crecs if r["primary_category"] == cat)
            c_s2 = sum(1 for r in crecs if r["has_lean_strong"] or r["has_lean_contextual"])
            c_beyond = sum(
                1
                for r in crecs
                if r["has_other_itp"] or r["has_model_checker"] or r["has_protocol_verifier"] or r["has_smt_sat"]
            )
            c_lat = [p for p in slice_confirmed_latest if cat in p["matched_15_cats"]]
            c_v1 = [p for p in c_lat if p["lean_in_v1"]]
            per_cat[cat] = {
                "total_papers": cn,
                "primary_papers": c_prim,
                "cross_list_papers": cn - c_prim,
                "fulltext_screened": c_scr,
                "fulltext_coverage_pct": round(100.0 * c_scr / max(cn, 1), 2),
                "stage2_lean_candidates": c_s2,
                "beyond_lean_any_fv": c_beyond,
                "confirmed_v1": rate_summary(len(c_v1), cn),
                "confirmed_v_latest": rate_summary(len(c_lat), cn),
                "roles_v1": {role: sum(1 for p in c_v1 if p["role_4way"] == role) for role in ROLES_4WAY},
                "roles_v_latest": {role: sum(1 for p in c_lat if p["role_4way"] == role) for role in ROLES_4WAY},
            }

        eess_all_recs = [r for r in recs if any(c in r["matched_15_cats"] for c in EESS_ALL)]
        eess_non_sy_recs = [r for r in recs if any(c in r["matched_15_cats"] for c in EESS_NON_SY)]
        eess_all_lat = [p for p in slice_confirmed_latest if any(c in p["matched_15_cats"] for c in EESS_ALL)]
        eess_all_v1 = [p for p in eess_all_lat if p["lean_in_v1"]]
        eess_non_sy_lat = [p for p in slice_confirmed_latest if any(c in p["matched_15_cats"] for c in EESS_NON_SY)]
        eess_non_sy_v1 = [p for p in eess_non_sy_lat if p["lean_in_v1"]]

        slices_out.append(
            {
                "slice_id": slice_id,
                "short_id": short_id,
                "label": spec["label"],
                "window": spec["window"],
                "total_papers": total,
                "fulltext_screened": screened,
                "fulltext_coverage_pct": round(100.0 * screened / max(total, 1), 2),
                "fetch_sources": {"html": html_n, "pdf": pdf_n, "failed": failed_n},
                "revised_v_gt_1": revised_n,
                "revised_v_gt_1_pct": round(100.0 * revised_n / max(total, 1), 1),
                "meta_lean_strong": meta_strong,
                "stage2_lean_strong": s2_strong,
                "stage2_lean_ctx_only": s2_ctx_only,
                "stage2_lean_candidates": s2_total,
                "stage2_lean_cand_pct": round(100.0 * s2_total / max(total, 1), 2),
                "stage2_pruned_pct": round(100.0 * (total - s2_total) / max(total, 1), 1),
                "beyond_lean_stage2": rate_summary(beyond_any, total),
                "confirmed_v1": _summarize_paper_group(slice_confirmed_v1, total),
                "confirmed_v_latest": _summarize_paper_group(slice_confirmed_latest, total),
                "roles_v1": {
                    role: _summarize_paper_group([p for p in slice_confirmed_v1 if p["role_4way"] == role], total)
                    for role in ROLES_4WAY
                },
                "roles_v_latest": {
                    role: _summarize_paper_group([p for p in slice_confirmed_latest if p["role_4way"] == role], total)
                    for role in ROLES_4WAY
                },
                "eess_archive": {
                    "eess_all_unique_papers": len(eess_all_recs),
                    "eess_all_confirmed_v1": rate_summary(len(eess_all_v1), len(eess_all_recs)),
                    "eess_all_confirmed_v_latest": rate_summary(len(eess_all_lat), len(eess_all_recs)),
                    "eess_non_sy_unique_papers": len(eess_non_sy_recs),
                    "eess_non_sy_confirmed_v1": rate_summary(len(eess_non_sy_v1), len(eess_non_sy_recs)),
                    "eess_non_sy_confirmed_v_latest": rate_summary(len(eess_non_sy_lat), len(eess_non_sy_recs)),
                },
                "per_category": per_cat,
            }
        )

    t0, t1, t2 = slices_out
    total_papers_3slice = sum(s["total_papers"] for s in slices_out)
    total_screened_3slice = sum(s["fulltext_screened"] for s in slices_out)
    total_s2_cands_3slice = sum(s["stage2_lean_candidates"] for s in slices_out)
    total_meta_strong_3slice = sum(s["meta_lean_strong"] for s in slices_out)
    total_eess_3slice = sum(s["eess_archive"]["eess_all_unique_papers"] for s in slices_out)
    total_eess_non_sy_3slice = sum(s["eess_archive"]["eess_non_sy_unique_papers"] for s in slices_out)
    eess_non_sy_v1_3slice = sum(s["eess_archive"]["eess_non_sy_confirmed_v1"]["count"] for s in slices_out)
    eess_non_sy_lat_3slice = sum(s["eess_archive"]["eess_non_sy_confirmed_v_latest"]["count"] for s in slices_out)

    per_cat_3slice: dict[str, Any] = {}
    for cat in ALL15_CATEGORIES:
        n3 = sum(s["per_category"][cat]["total_papers"] for s in slices_out)
        v1_3 = sum(s["per_category"][cat]["confirmed_v1"]["count"] for s in slices_out)
        lat_3 = sum(s["per_category"][cat]["confirmed_v_latest"]["count"] for s in slices_out)
        per_cat_3slice[cat] = {
            "total_papers_3slice": n3,
            "confirmed_v1_3slice": rate_summary(v1_3, n3),
            "confirmed_v_latest_3slice": rate_summary(lat_3, n3),
        }

    confirmed_by_id = {p["arxiv_id"]: p for p in all_confirmed_papers}

    # T2 distributions broken out by 4-way role + pooled (v1 and v_latest)
    t2_by_role_v1 = {
        role: _summarize_paper_group([p for p in t2_union_confirmed_v1 if p["role_4way"] == role], t2_total_papers)
        for role in ROLES_4WAY
    }
    t2_by_role_v1["pooled"] = _summarize_paper_group(t2_union_confirmed_v1, t2_total_papers)
    t2_by_role_v_latest = {
        role: _summarize_paper_group([p for p in t2_union_confirmed_latest if p["role_4way"] == role], t2_total_papers)
        for role in ROLES_4WAY
    }
    t2_by_role_v_latest["pooled"] = _summarize_paper_group(t2_union_confirmed_latest, t2_total_papers)

    # Load auxiliary audited summaries
    opfv = json.loads((REPO_ROOT / "artifacts" / "track3_operational_fv_pilot.json").read_text(encoding="utf-8"))
    off_arxiv = json.loads((REPO_ROOT / "artifacts" / "off_arxiv_probe.json").read_text(encoding="utf-8"))
    irr_sum = json.loads((REPO_ROOT / "artifacts" / "human_annotations" / "stage4_irr_summary.json").read_text(encoding="utf-8"))
    layer_a_human = json.loads(
        (REPO_ROOT / "artifacts" / "human_annotations" / "layer_a_human_verification.json").read_text(encoding="utf-8")
    )

    # Check math.NA probe DB if present
    math_na_probe = {"total_t2_papers": 446, "net_new_vs_15cat": 354, "meta_strong_hits": 4, "already_in_15cat": 3, "net_new_engineering_hits": 0}
    math_na_db = REPO_ROOT / "data" / "scout_math_na_meta_2026_11.db"
    if math_na_db.is_file():
        conn = sqlite3.connect(str(math_na_db))
        n_mna = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        conn.close()
        math_na_probe["total_t2_papers"] = n_mna

    # Sort master ledger by slice (T2 -> T1 -> T0), then arxiv_id descending
    slice_rank = {"T2": 0, "T1": 1, "T0": 2}
    all_confirmed_papers.sort(key=lambda p: (slice_rank[p["short_id"]], p["arxiv_id"]))

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "categories": {
            "all15": ALL15_CATEGORIES,
            "eess_all": EESS_ALL,
            "eess_non_sy": EESS_NON_SY,
        },
        "grand_totals": {
            "total_papers": total_papers_3slice,
            "fulltext_screened": total_screened_3slice,
            "fulltext_coverage_pct": round(100.0 * total_screened_3slice / max(total_papers_3slice, 1), 2),
            "stage2_lean_candidates_total": total_s2_cands_3slice,
            "stage2_pruned_pct": round(100.0 * (total_papers_3slice - total_s2_cands_3slice) / max(total_papers_3slice, 1), 1),
            "meta_lean_strong_total": total_meta_strong_3slice,
            "fulltext_vs_meta_recall_ratio": round(total_s2_cands_3slice / max(total_meta_strong_3slice, 1), 1),
            "confirmed_v1_total": sum(s["confirmed_v1"]["count"] for s in slices_out),
            "confirmed_v_latest_total": sum(s["confirmed_v_latest"]["count"] for s in slices_out),
            "retroactive_v2_total": len(retroactive_ledger),
            "complete_eess_3slice_unique_papers": total_eess_3slice,
            "eess_non_sy_3slice_unique_papers": total_eess_non_sy_3slice,
            "eess_non_sy_3slice_confirmed_v1": rate_summary(eess_non_sy_v1_3slice, total_eess_non_sy_3slice),
            "eess_non_sy_3slice_confirmed_v_latest": rate_summary(eess_non_sy_lat_3slice, total_eess_non_sy_3slice),
            "persistent_zero_categories_v1_3slice": [
                c for c in ALL15_CATEGORIES if per_cat_3slice[c]["confirmed_v1_3slice"]["count"] == 0
            ],
            "persistent_zero_categories_v_latest_3slice": [
                c for c in ALL15_CATEGORIES if per_cat_3slice[c]["confirmed_v_latest_3slice"]["count"] == 0
            ],
        },
        "multipliers": {
            "pooled_v1_t2_over_t1": _safe_mult(t2["confirmed_v1"]["pct"], t1["confirmed_v1"]["pct"]),
            "pooled_v_latest_t2_over_t1": _safe_mult(t2["confirmed_v_latest"]["pct"], t1["confirmed_v_latest"]["pct"]),
            "pooled_v_latest_t2_over_t0": _safe_mult(t2["confirmed_v_latest"]["pct"], t0["confirmed_v_latest"]["pct"]),
            "eng_alg_v1_t2_over_t1": _safe_mult(
                t2["roles_v1"]["eng_algorithmic_proof"]["pct"],
                t1["roles_v1"]["eng_algorithmic_proof"]["pct"],
            ),
            "eng_alg_v_latest_t2_over_t1": _safe_mult(
                t2["roles_v_latest"]["eng_algorithmic_proof"]["pct"],
                t1["roles_v_latest"]["eng_algorithmic_proof"]["pct"],
            ),
            "pure_math_tcs_v1_t2_over_t1": _safe_mult(
                t2["roles_v1"]["pure_math_or_tcs"]["pct"],
                t1["roles_v1"]["pure_math_or_tcs"]["pct"],
            ),
            "eng_alg_median_loc_t2_over_t1": _safe_mult(
                t2["roles_v1"]["eng_algorithmic_proof"]["median_owned_loc"],
                t1["roles_v1"]["eng_algorithmic_proof"]["median_owned_loc"],
            ),
            "pooled_median_loc_t2_over_t1": _safe_mult(
                t2["confirmed_v1"]["median_owned_loc"],
                t1["confirmed_v1"]["median_owned_loc"],
            ),
        },
        "slices": slices_out,
        "per_category_3slice_totals": per_cat_3slice,
        "t2_distributions_by_role_v1": t2_by_role_v1,
        "t2_distributions_by_role_v_latest": t2_by_role_v_latest,
        "retroactive_formalizations": retroactive_ledger,
        "confirmed_papers": all_confirmed_papers,
        "layer_a_audits": _build_layer_a_section(confirmed_by_id),
        "sandbox_builds": _build_sandbox_section(confirmed_by_id),
        "recall_calibration": _build_recall_section(),
        "operational_fv_audit": {
            "summary_counts": opfv["summary_counts"],
            "systems_fv_paradigm_distribution": opfv["systems_fv_paradigm_distribution"],
            "arxiv_ids": [p["arxiv_id"] for p in opfv["papers"]],
        },
        "off_arxiv_probe": {
            "window": off_arxiv["window"],
            "preprint_servers": {
                "techrxiv": {
                    k: off_arxiv["preprint_servers"]["techrxiv"][k]
                    for k in ("server", "crossref_prefix", "total_records_2025_2026", "unique_raw_hits", "confirmed_lean_tp_unique", "confirmed_95pct_ub_pct")
                },
                "engrxiv": {
                    k: off_arxiv["preprint_servers"]["engrxiv"][k]
                    for k in ("server", "crossref_prefix", "total_records_2025_2026", "unique_raw_hits", "confirmed_lean_tp_unique", "confirmed_95pct_ub_pct")
                },
                "combined": off_arxiv["preprint_servers"]["combined"],
            },
            "openalex": {
                "mathlib_all_fields": off_arxiv["openalex"]["mathlib_all_fields"],
                "engineering_field_22": {
                    k: v
                    for k, v in off_arxiv["openalex"]["engineering_field_22"].items()
                    if k not in ("off_arxiv_works", "all_mathlib_engineering_works")
                },
            },
        },
        "math_na_probe": math_na_probe,
        "human_validation": {
            "stage4_irr": irr_sum,
            "layer_a_human_co_review": {
                "total_reviewed": len(layer_a_human.get("records", [])),
                "named_critiques_reviewed": sum(
                    1 for r in layer_a_human.get("records", []) if r.get("cohort") == "named_critique"
                ),
                "clean_spot_checks_reviewed": sum(
                    1 for r in layer_a_human.get("records", []) if r.get("cohort") == "clean_spot_check"
                ),
                "named_critique_ids": [
                    r["arxiv_id"] for r in layer_a_human.get("records", []) if r.get("cohort") == "named_critique"
                ],
                "clean_spot_check_ids": [
                    r["arxiv_id"] for r in layer_a_human.get("records", []) if r.get("cohort") == "clean_spot_check"
                ],
            },
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build canonical artifacts/unified_15cat_panel.json.")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    payload = build_unified_panel()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    args.out.write_text(text, encoding="utf-8")
    size_kb = len(text.encode("utf-8")) / 1024.0
    print(
        f"Wrote {args.out} ({size_kb:.1f} KB): "
        f"N={payload['grand_totals']['total_papers']:,}, "
        f"confirmed={payload['grand_totals']['confirmed_v1_total']} v1 / {payload['grand_totals']['confirmed_v_latest_total']} latest, "
        f"layer_a={payload['layer_a_audits']['total_audited']}, "
        f"sandbox={payload['sandbox_builds']['overall']['total_attempted']}"
    )


if __name__ == "__main__":
    main()
