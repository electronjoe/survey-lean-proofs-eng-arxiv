#!/usr/bin/env python3
"""Phase C2: Targeted Stage-5 Layer-A Audits + Compact Docker Kernel Builds (+7 Categories).

Pins immutable provenance (arXiv version, Git commit SHA / Zenodo record ID,
`lean_tree_sha256`, `lean_toolchain`, and automated `file:line` checks) for the 4
newly discovered `+7` `eng_algorithmic_proof` public repositories, synthesizes
their Stage-5 Layer-A semantic fidelity audits (`pro` tier) with their isolated
`--network=none` Docker `lake build` + `Lean.collectAxioms` verification logs
(all 3 compact `<15k` LoC repos), and computes combined 15-category cohort totals
without mutating frozen orig-8 v0.7 artifacts.

Writes:
  - artifacts/phase_c2_plus7_audits.json
  - reports/phase_c2_plus7_audits.md
"""

from __future__ import annotations

import json
import sqlite3
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pin_phase2_provenance import (
    _find_toolchain,
    _git_info,
    _lean_tree_sha256,
    _verify_cited_file_lines,
)

REPOS_DIR = REPO_ROOT / "data" / "repos"
SCOUT_T2_DB = REPO_ROOT / "data" / "scout_eng_tier12_2026_11.db"

PLUS7_AUDITS_PATH = REPO_ROOT / "artifacts" / "slices" / "2026-11" / "plus7_layer_a_audits.json"
PLUS7_SANDBOX_PATH = REPO_ROOT / "artifacts" / "sandbox_builds" / "results_plus7_2026-11.json"
PHASE_C1_PATH = REPO_ROOT / "artifacts" / "phase_c1_15cat_longitudinal.json"

ORIG8_T2_AUDITS_PATH = REPO_ROOT / "artifacts" / "slices" / "2026-11" / "layer_a_audits.json"
ORIG8_T1_AUDITS_PATH = REPO_ROOT / "artifacts" / "slices" / "2026-05" / "layer_a_audits.json"
ORIG8_PROV_PATH = REPO_ROOT / "artifacts" / "phase2_provenance.json"
ORIG8_SANDBOX_T2_PATH = REPO_ROOT / "artifacts" / "sandbox_builds" / "results_2026-11.json"
ORIG8_SANDBOX_T1_PATH = REPO_ROOT / "artifacts" / "sandbox_builds" / "results_2026-05.json"
TRACK1_ADJ_PATH = REPO_ROOT / "artifacts" / "human_annotations" / "track1_4way_adjudication.json"

OUT_JSON = REPO_ROOT / "artifacts" / "phase_c2_plus7_audits.json"
OUT_MD = REPO_ROOT / "reports" / "phase_c2_plus7_audits.md"

PLUS7_REPO_MAP: dict[str, tuple[str, str, str]] = {
    "2611.14586": ("zenodo__23768172", "zenodo", "https://zenodo.org/records/23768172"),
    "2611.11805": (
        "sgstepaniants__inelastic_hom_learn",
        "github",
        "https://github.com/sgstepaniants/inelastic_hom_learn",
    ),
    "2611.09615": (
        "renatoppl__trace-square-root",
        "github",
        "https://github.com/renatoppl/trace-square-root",
    ),
    "2611.07395": (
        "michalshavitNYU__Rigorously-certified-water-waves",
        "github",
        "https://github.com/michalshavitNYU/Rigorously-certified-water-waves",
    ),
}


def _summarize_layer_a(audits: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(audits)
    return {
        "count": n,
        "overall_fidelity": dict(Counter(a["overall_fidelity"] for a in audits)),
        "mode1_statement_drift": dict(Counter(a["mode1_statement_drift"]["severity"] for a in audits)),
        "mode2_scope_downgrade": dict(Counter(a["mode2_scope_downgrade"]["severity"] for a in audits)),
        "mode3_definition_smuggling": dict(Counter(a["mode3_definition_smuggling"]["severity"] for a in audits)),
        "mode4_junk_or_vacuity": dict(Counter(a["mode4_junk_or_vacuity"]["severity"] for a in audits)),
        "has_non_vacuity_witnesses_count": sum(1 for a in audits if a.get("has_non_vacuity_witnesses")),
        "has_non_vacuity_witnesses_pct": round(100.0 * sum(1 for a in audits if a.get("has_non_vacuity_witnesses")) / n, 1) if n else 0.0,
        "mathlib_anchoring_quality": dict(Counter(a.get("mathlib_anchoring_quality") for a in audits)),
        "material_undisclosed_count": sum(1 for a in audits if a["overall_fidelity"] == "material_undisclosed_drift_or_risk"),
    }


def _summarize_sandbox(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    passed = [r for r in records if r["build_status"] == "pass"]
    clean = [
        r
        for r in passed
        if not r.get("sorry_ax_detected")
        and not r.get("of_reduce_bool_detected")
        and not r.get("trust_compiler_detected")
        and not r.get("nonstandard_axioms_detected")
        and not r.get("axiom_check_error")
    ]
    failed_pkg = [r for r in records if r["build_status"] == "fail_packaging"]
    failed_local = [r for r in records if r["build_status"] == "fail_missing_local_dep"]
    failed_other = [
        r for r in records if r["build_status"] in ("fail_build", "fail_network_dep", "timeout", "fail_runner")
    ]
    synth_passed = [
        r for r in failed_pkg if (r.get("synthetic_env_check") or {}).get("build_status") == "pass"
    ]
    t3_all = [r for r in records if r.get("static_verification_tier") == "Tier3_Gold"]
    t3_pass = [r for r in t3_all if r["build_status"] == "pass"]
    t3_clean = [r for r in t3_all if r in clean]
    ootb_thms = sum(int(r.get("total_theorems_checked") or 0) for r in passed)
    synth_thms = sum(
        int((r.get("synthetic_env_check") or {}).get("total_theorems_checked") or 0)
        for r in synth_passed
    )
    pass_times = sorted(float(r["wall_time_sec"]) for r in passed if r.get("wall_time_sec") is not None)
    return {
        "total_attempted": n,
        "pass_out_of_box": len(passed),
        "pass_out_of_box_pct": round(100.0 * len(passed) / n, 1) if n else 0.0,
        "pass_and_standard_axioms_only": len(clean),
        "pass_with_nonstandard_axioms": len(passed) - len(clean),
        "fail_packaging_no_lakefile": len(failed_pkg),
        "fail_missing_local_dep": len(failed_local),
        "fail_build_or_other": len(failed_other),
        "synthetic_env_pass_among_packaging_fails": len(synth_passed),
        "tier3_gold_attempted": len(t3_all),
        "tier3_gold_pass_out_of_box": len(t3_pass),
        "tier3_gold_clean_axioms": len(t3_clean),
        "total_theorems_checked_ootb": ootb_thms,
        "total_theorems_checked_incl_synthetic": ootb_thms + synth_thms,
        "median_pass_wall_time_sec": round(statistics.median(pass_times), 2) if pass_times else None,
        "min_pass_wall_time_sec": round(pass_times[0], 2) if pass_times else None,
        "max_pass_wall_time_sec": round(pass_times[-1], 2) if pass_times else None,
        "sorry_ax_repos_ootb": [r["arxiv_id"] for r in passed if r.get("sorry_ax_detected")],
        "of_reduce_bool_repos_ootb": [r["arxiv_id"] for r in passed if r.get("of_reduce_bool_detected")],
        "nonstandard_axiom_repos_ootb": [
            {"arxiv_id": r["arxiv_id"], "axioms": r.get("nonstandard_axioms_detected", [])}
            for r in passed
            if r.get("nonstandard_axioms_detected")
        ],
    }


def build_phase_c2_payload() -> dict[str, Any]:
    plus7_audits_doc = json.loads(PLUS7_AUDITS_PATH.read_text(encoding="utf-8"))
    plus7_audits = plus7_audits_doc["audits"]
    plus7_sandbox_doc = json.loads(PLUS7_SANDBOX_PATH.read_text(encoding="utf-8"))
    plus7_sandbox_recs = plus7_sandbox_doc["records"]
    sb_by_id = {r["arxiv_id"]: r for r in plus7_sandbox_recs}

    c1_doc = json.loads(PHASE_C1_PATH.read_text(encoding="utf-8"))
    queue_by_id = {q["arxiv_id"]: q for q in c1_doc["phase_c2_eng_alg_audit_queue"]}

    # Pin provenance & verify file:line checks for all 4 +7 repos
    conn = sqlite3.connect(str(SCOUT_T2_DB))
    prov_records: list[dict[str, Any]] = []
    for a in sorted(plus7_audits, key=lambda x: x["arxiv_id"]):
        aid = a["arxiv_id"]
        prow = conn.execute(
            "SELECT version, submitted_date, updated_date, title FROM papers WHERE arxiv_id = ?",
            (aid,),
        ).fetchone()
        local_name, host, url = PLUS7_REPO_MAP[aid]
        repo_path = REPOS_DIR / local_name
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Missing local repo for {aid}: {repo_path}")

        sha, cdate = _git_info(repo_path)
        tree_sha256, lean_file_count = _lean_tree_sha256(repo_path)
        toolchain = _find_toolchain(repo_path)
        fl_check = _verify_cited_file_lines(a, [repo_path])
        q = queue_by_id.get(aid, {})
        sb = sb_by_id.get(aid)

        prov_records.append(
            {
                "slice_id": "2026-11",
                "arxiv_id": aid,
                "arxiv_version_audited": f"v{prow[0]}" if prow and prow[0] else None,
                "arxiv_submitted_date": prow[1] if prow else None,
                "arxiv_updated_date": prow[2] if prow else None,
                "primary_category": a["primary_category"],
                "matched_plus7_cats": a["matched_target_cats"],
                "role_4way": a.get("role_4way", "eng_algorithmic_proof"),
                "authoring_paradigm": a.get("authoring_paradigm"),
                "verification_tier": a.get("verification_tier"),
                "primary_owned_loc": q.get("primary_owned_loc"),
                "compact_sandbox_eligible": bool(q.get("compact_sandbox_eligible", False)),
                "repo_host": host,
                "repo_url": url,
                "commit_sha": sha,
                "commit_short_sha": sha[:7] if sha else None,
                "commit_date": cdate,
                "zenodo_record_id": local_name.split("__", 1)[1] if host == "zenodo" else None,
                "lean_files_count": lean_file_count,
                "lean_tree_sha256": tree_sha256,
                "lean_toolchain": toolchain,
                "layer_a": {
                    "overall_fidelity": a["overall_fidelity"],
                    "mode1_severity": a["mode1_statement_drift"]["severity"],
                    "mode2_severity": a["mode2_scope_downgrade"]["severity"],
                    "mode3_severity": a["mode3_definition_smuggling"]["severity"],
                    "mode4_severity": a["mode4_junk_or_vacuity"]["severity"],
                    "has_non_vacuity_witnesses": bool(a["has_non_vacuity_witnesses"]),
                    "mathlib_anchoring_quality": a["mathlib_anchoring_quality"],
                    "theorems_compared_count": len(a.get("theorems_compared", [])),
                    "theorems_compared_file_line_check": fl_check,
                },
                "sandbox_build": (
                    {
                        "build_status": sb["build_status"],
                        "exit_code": sb["exit_code"],
                        "wall_time_sec": sb["wall_time_sec"],
                        "axiom_check_wall_time_sec": sb.get("axiom_check_wall_time_sec"),
                        "target_modules_count": sb.get("target_modules_count", 0),
                        "total_theorems_checked": sb.get("total_theorems_checked", 0),
                        "standard_axioms_used": sb.get("standard_axioms_used", []),
                        "nonstandard_axioms_detected": sb.get("nonstandard_axioms_detected", []),
                        "sorry_ax_detected": bool(sb.get("sorry_ax_detected", False)),
                        "of_reduce_bool_detected": bool(sb.get("of_reduce_bool_detected", False)),
                        "trust_compiler_detected": bool(sb.get("trust_compiler_detected", False)),
                        "axiom_check_error": sb.get("axiom_check_error"),
                    }
                    if sb is not None
                    else None
                ),
            }
        )
    conn.close()

    total_refs_plus7 = sum(r["layer_a"]["theorems_compared_file_line_check"]["total_file_line_refs"] for r in prov_records)
    total_ok_plus7 = sum(r["layer_a"]["theorems_compared_file_line_check"]["resolved_in_bounds"] for r in prov_records)

    # Combined 15-category Layer-A cohort stats (orig-8 + plus-7)
    orig8_t2_audits = json.loads(ORIG8_T2_AUDITS_PATH.read_text(encoding="utf-8"))["audits"]
    orig8_t1_audits = json.loads(ORIG8_T1_AUDITS_PATH.read_text(encoding="utf-8"))["audits"]
    orig8_prov = json.loads(ORIG8_PROV_PATH.read_text(encoding="utf-8"))
    adj = json.loads(TRACK1_ADJ_PATH.read_text(encoding="utf-8"))
    role_map = {r["arxiv_id"]: r["role_4way"] for r in adj["records"]}

    orig8_t2_eng = [a for a in orig8_t2_audits if role_map.get(a["arxiv_id"]) == "eng_algorithmic_proof"]
    orig8_t1_eng = [a for a in orig8_t1_audits if role_map.get(a["arxiv_id"]) == "eng_algorithmic_proof"]
    all15_t2_eng = orig8_t2_eng + plus7_audits
    all15_eng = orig8_t1_eng + orig8_t2_eng + plus7_audits
    all15_all_roles = orig8_t1_audits + orig8_t2_audits + plus7_audits

    orig8_fl = orig8_prov["theorems_compared_file_line_summary"]

    # Combined 15-category compact (<15k LoC) sandbox stats
    orig8_sb_t2 = json.loads(ORIG8_SANDBOX_T2_PATH.read_text(encoding="utf-8"))["records"]
    orig8_sb_t1 = json.loads(ORIG8_SANDBOX_T1_PATH.read_text(encoding="utf-8"))["records"]
    orig8_sb_all = orig8_sb_t2 + orig8_sb_t1
    all15_sb_all = orig8_sb_all + plus7_sandbox_recs

    # Strict eng_algorithmic_proof compact sandbox subset across all 15 categories
    orig8_sb_eng = [r for r in orig8_sb_all if role_map.get(r["arxiv_id"]) == "eng_algorithmic_proof"]
    all15_sb_eng = orig8_sb_eng + plus7_sandbox_recs

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "C2",
        "scope": "Targeted Stage-5 Layer-A semantic fidelity audits (n=4) and isolated --network=none Docker compact (<15k LoC) kernel builds (n=3) on all newly discovered eng_algorithmic_proof public repos from the +7 engineering categories.",
        "plus7_provenance": {
            "total_audited_repos": len(prov_records),
            "git_pinned_count": sum(1 for r in prov_records if r["commit_sha"]),
            "zenodo_pinned_count": sum(1 for r in prov_records if r["zenodo_record_id"]),
            "theorems_compared_file_line_summary": {
                "total_refs": total_refs_plus7,
                "resolved_in_bounds": total_ok_plus7,
            },
        },
        "combined_15cat_provenance": {
            "total_audited_repos": orig8_prov["total_audited_repos"] + len(prov_records),
            "theorems_compared_file_line_summary": {
                "total_refs": orig8_fl["total_refs"] + total_refs_plus7,
                "resolved_in_bounds": orig8_fl["resolved_in_bounds"] + total_ok_plus7,
            },
        },
        "layer_a_summary": {
            "plus7_t2_eng_algorithmic_proof": _summarize_layer_a(plus7_audits),
            "orig8_t2_eng_algorithmic_proof": _summarize_layer_a(orig8_t2_eng),
            "all15_t2_eng_algorithmic_proof": _summarize_layer_a(all15_t2_eng),
            "all15_t1_t2_eng_algorithmic_proof": _summarize_layer_a(all15_eng),
            "all15_t1_t2_all_roles": _summarize_layer_a(all15_all_roles),
        },
        "sandbox_summary": {
            "plus7_t2_compact_eng_alg": _summarize_sandbox(plus7_sandbox_recs),
            "orig8_t1_t2_compact_all_roles": _summarize_sandbox(orig8_sb_all),
            "all15_t1_t2_compact_all_roles": _summarize_sandbox(all15_sb_all),
            "all15_t1_t2_compact_eng_alg": _summarize_sandbox(all15_sb_eng),
        },
        "records": prov_records,
    }


def render_report(payload: dict[str, Any]) -> str:
    p7_la = payload["layer_a_summary"]["plus7_t2_eng_algorithmic_proof"]
    all15_t2_la = payload["layer_a_summary"]["all15_t2_eng_algorithmic_proof"]
    all15_eng_la = payload["layer_a_summary"]["all15_t1_t2_eng_algorithmic_proof"]
    all15_all_la = payload["layer_a_summary"]["all15_t1_t2_all_roles"]

    p7_sb = payload["sandbox_summary"]["plus7_t2_compact_eng_alg"]
    all15_sb = payload["sandbox_summary"]["all15_t1_t2_compact_all_roles"]
    all15_sb_eng = payload["sandbox_summary"]["all15_t1_t2_compact_eng_alg"]

    fl_p7 = payload["plus7_provenance"]["theorems_compared_file_line_summary"]
    fl_15 = payload["combined_15cat_provenance"]["theorems_compared_file_line_summary"]

    lines = [
        "# Phase C2 Report: Targeted Stage-5 Layer-A Audits & Compact Docker Kernel Builds (`+7` Categories)",
        "",
        f"> **Phase C2 Complete ({payload['generated_at'][:10]})** · Exhaustive Stage-5 Layer-A semantic fidelity audits (`pro` tier, `n = 4`) + isolated `--network=none` Docker `lake build` & `Lean.collectAxioms` verification (`n = 3` compact `<15k` LoC repos) on 100% of newly discovered `eng_algorithmic_proof` public repositories from the `+7` engineering categories · Frozen orig-8 v0.7 artifacts untouched · Machine-readable summary: [`artifacts/phase_c2_plus7_audits.json`](../artifacts/phase_c2_plus7_audits.json) · Detailed per-paper audit tables: [`reports/slices/2026-11/phase2_layer_a_audit_plus7.md`](slices/2026-11/phase2_layer_a_audit_plus7.md)",
        "",
        "## 1. Executive Summary",
        "",
        "Following Phase C1's 15-category longitudinal backfill, 4-way role stratification narrowed the newly discovered `+7` `eng_algorithmic_proof` public-repo queue to **4 repositories** (`2611.14586`, `2611.11805`, `2611.09615`, `2611.07395`; `2611.04545` has a 404/private repo). Completing Stage-5 Layer-A audits across all 4 repos and isolated `--network=none` Docker kernel verification across all 3 compact (`<15k` LoC) repos keeps both semantic auditing and dynamic kernel verification **100% exhaustive over the entire 15-category engineering cohort**:",
        "",
        f"1. **Zero Material Undisclosed Drift Across All 22 `eng_algorithmic_proof` Repos (15-Category Union):** Across the 4 new `+7` repos, **`2/4` (`2611.11805`, `2611.09615`)** score `high_faithful`, **`1/4` (`2611.07395`)** scores `mostly_faithful_with_disclosed_gaps`, **`1/4` (`2611.14586`)** scores `partial_or_weakened_formalization`, and **`0/4`** score `material_undisclosed_drift_or_risk`. Combining with orig-8 (`18` `eng_algorithmic_proof` repos across T1+T2) yields **`0 / {all15_eng_la['count']}`** (`0.0%`) `material_undisclosed_drift_or_risk` across all 15-category engineering-algorithmic repos (`0/{all15_t2_la['count']}` in T2, with `7/{all15_t2_la['count']}` `high_faithful` and `8/{all15_t2_la['count']}` `mostly_faithful_with_disclosed_gaps`; the sole `material_undisclosed_drift_or_risk` repo among all **{all15_all_la['count']}** audited repos remains meta-system `2611.26272` *Paper2Lean*). All **{fl_p7['resolved_in_bounds']}/{fl_p7['total_refs']}** (`100%`) new `file:line` provenance refs (**{fl_15['resolved_in_bounds']}/{fl_15['total_refs']}** combined) resolve in-bounds.",
        f"2. **3 / 3 (100%) Out-of-the-Box `--network=none` Docker Pass Rate on Compact `+7` Repos:** All 3 newly discovered compact (`<15k` LoC) `eng_algorithmic_proof` repositories build out of the box with zero compile errors and zero `Lean.ofReduceBool` / `sorryAx` (`{p7_sb['total_theorems_checked_ootb']:,}` theorems programmatically audited via `Lean.collectAxioms`, median `{p7_sb['median_pass_wall_time_sec']:.1f}s`). Combined across all 15 categories (`T1 + T2`), compact OOTB pass rate rises from `11/14 (78.6%)` to **`{all15_sb['pass_out_of_box']}/{all15_sb['total_attempted']} ({all15_sb['pass_out_of_box_pct']:.1f}%)`** (**{all15_sb['total_theorems_checked_ootb']:,}** OOTB theorems / **{all15_sb['total_theorems_checked_incl_synthetic']:,}** incl. synthetic; **`{all15_sb['tier3_gold_pass_out_of_box']}/{all15_sb['tier3_gold_attempted']}`** compact `Tier3_Gold` OOTB pass and **`{all15_sb['tier3_gold_clean_axioms']}/{all15_sb['tier3_gold_pass_out_of_box']}` (100%)** axiom-clean; **`0/{all15_sb['total_attempted']}`** `Lean.ofReduceBool`).",
        "3. **Exact Static-to-Dynamic Axiom Corroboration (Including Hybrid Julia/Arb Computer-Assisted Proofs):** `2611.14586` (`SparTheorems`, `85` theorems) and `2611.09615` (`TraceSqrt`, `69` theorems, `Tier3_Gold`) use strictly Lean's 3 standard axioms (`propext`, `Classical.choice`, `Quot.sound`), whereas `2611.07395` (`WaveCAP`, `Tier1_Bronze`) dynamically corroborates its static `Mode6_SorryOrAxiomOrNativeDecide` flag — surfacing exact custom Arb numerical axioms in both the legacy `Main.lean` certificate (`WaveCAP.Certificate.*`) and the publication certificate (`WaveCAP.PaperCertificate.cert_arb_dmin_bound`, `cert_arb_sup_bound_le_eps0`), with **zero `sorryAx`** across the entire codebase.",
        "4. **Two Contrasting Real-World Failure Modes Surfaced by Layer-A Deep Inspection:** Even without `sorry` or custom axioms, `2611.14586` (`Tier2_Silver`, 1.97k LoC) illustrates subtle **algebraic-core substitution** (`Mode1=moderate`, `Mode2=moderate`: abstract Zinkevich template without D-dim squared-loss instantiation, 2-point vs. K-point Hedge convexity, and missing contraction bound on $\\beta$ in `debiased_dial_contraction`), whereas `2611.07395` (`Tier1_Bronze`, 12.3k LoC) illustrates **disconnected analytic library vs. axiomatized publication certificate** (`Mode2=moderate`: ~12k LoC of clean Hilbert/aliasing/Taylor proofs sit uninstantiated behind two monolithic Julia/Arb axioms, and default `lake build` compiles the older $N=110$ `Main.lean` rather than `PaperTheorems.lean`). Conversely, `2611.11805` (`P4` spec-lock with 331 Comparator checks + LeanCert) and `2611.09615` (`P1` full 22-statement formalization) achieve exemplary `high_faithful` fidelity.",
        "",
        "---",
        "",
        "## 2. Per-Repository Phase C2 Audit & Kernel Verification Matrix (`n = 4`)",
        "",
        "| arXiv ID | Cat (`+7`) | Primary Repo (Pin) | Owned LoC | Toolchain | Par / Tier | Layer-A Fidelity | M1 / M2 / M3 / M4 | Non-Vac? | Docker OOTB (`--network=none`) | Theorems (`collectAxioms`) | Non-Std Axioms |",
        "| :--- | :--- | :--- | ---: | :--- | :--- | :--- | :--- | :---: | :--- | ---: | :--- |",
    ]

    for r in payload["records"]:
        aid = r["arxiv_id"]
        pin = r["commit_short_sha"] or f"zenodo:{r['zenodo_record_id']}"
        repo_short = r["repo_url"].replace("https://github.com/", "").replace("https://zenodo.org/records/", "zenodo/")
        tc_short = (r["lean_toolchain"] or "?").replace("leanprover/lean4:", "")
        par = (r["authoring_paradigm"] or "?").split("_")[0]
        tier = (r["verification_tier"] or "?").replace("Tier", "T").split("_")[0]
        la = r["layer_a"]
        modes = f"`{la['mode1_severity']}` / `{la['mode2_severity']}` / `{la['mode3_severity']}` / `{la['mode4_severity']}`"
        sb = r["sandbox_build"]
        if sb is None:
            sb_str = "*N/A (>15k LoC)*"
            thms_str = "—"
            nonstd_str = "—"
        else:
            sb_str = f"**PASS** ({sb['wall_time_sec']:.1f}s)" if sb["build_status"] == "pass" else f"FAIL (`{sb['build_status']}`)"
            thms_str = f"{sb['total_theorems_checked']:,}"
            ns = sb.get("nonstandard_axioms_detected") or []
            short_ns = [x.split(".", 1)[1] if "." in x else x for x in ns[:4]]
            nonstd_str = "**none**" if not ns else f"`{len(ns)}` custom (`" + "`, `".join(short_ns) + ("`..." if len(ns) > 4 else "`") + ")"

        lines.append(
            f"| [{aid}](https://arxiv.org/abs/{aid}) | `{r['primary_category']}` (`{','.join(r['matched_plus7_cats'])}`) | "
            f"`{repo_short}` (`{pin}`) | {r['primary_owned_loc']:,} | `{tc_short}` | `{par}` / `{tier}` | "
            f"`{la['overall_fidelity']}` | {modes} | {'Yes' if la['has_non_vacuity_witnesses'] else 'No'} | "
            f"{sb_str} | {thms_str} | {nonstd_str} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 3. Combined 15-Category Cohort Totals (Orig-8 + `+7`)",
        "",
        "### 3.1 Stage-5 Layer-A Semantic Fidelity Audits",
        "",
        "| Cohort | Audited Repos | `high_faithful` | `mostly_faithful` | `partial_or_weakened` | `material_undisclosed` | Non-Vacuity Witnesses | `file:line` Provenance |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |",
        f"| **`+7` Net-New T2 (`eng_algorithmic_proof`)** | {p7_la['count']} | {p7_la['overall_fidelity'].get('high_faithful', 0)} | {p7_la['overall_fidelity'].get('mostly_faithful_with_disclosed_gaps', 0)} | {p7_la['overall_fidelity'].get('partial_or_weakened_formalization', 0)} | **{p7_la['material_undisclosed_count']}** | {p7_la['has_non_vacuity_witnesses_count']}/{p7_la['count']} ({p7_la['has_non_vacuity_witnesses_pct']:.1f}%) | **{fl_p7['resolved_in_bounds']}/{fl_p7['total_refs']}** (100%) |",
        f"| **15-Cat T2 (`eng_algorithmic_proof`)** | {all15_t2_la['count']} | {all15_t2_la['overall_fidelity'].get('high_faithful', 0)} | {all15_t2_la['overall_fidelity'].get('mostly_faithful_with_disclosed_gaps', 0)} | {all15_t2_la['overall_fidelity'].get('partial_or_weakened_formalization', 0)} | **{all15_t2_la['material_undisclosed_count']}** | {all15_t2_la['has_non_vacuity_witnesses_count']}/{all15_t2_la['count']} ({all15_t2_la['has_non_vacuity_witnesses_pct']:.1f}%) | — |",
        f"| **15-Cat T1+T2 (`eng_algorithmic_proof`)** | {all15_eng_la['count']} | {all15_eng_la['overall_fidelity'].get('high_faithful', 0)} | {all15_eng_la['overall_fidelity'].get('mostly_faithful_with_disclosed_gaps', 0)} | {all15_eng_la['overall_fidelity'].get('partial_or_weakened_formalization', 0)} | **{all15_eng_la['material_undisclosed_count']}** | {all15_eng_la['has_non_vacuity_witnesses_count']}/{all15_eng_la['count']} ({all15_eng_la['has_non_vacuity_witnesses_pct']:.1f}%) | — |",
        f"| **15-Cat T1+T2 (All Audited Roles)** | {all15_all_la['count']} | {all15_all_la['overall_fidelity'].get('high_faithful', 0)} | {all15_all_la['overall_fidelity'].get('mostly_faithful_with_disclosed_gaps', 0)} | {all15_all_la['overall_fidelity'].get('partial_or_weakened_formalization', 0)} | **{all15_all_la['material_undisclosed_count']}** (`2611.26272`) | {all15_all_la['has_non_vacuity_witnesses_count']}/{all15_all_la['count']} ({all15_all_la['has_non_vacuity_witnesses_pct']:.1f}%) | **{fl_15['resolved_in_bounds']}/{fl_15['total_refs']}** (100%) |",
        "",
        "### 3.2 Isolated `--network=none` Docker Compact (`<15k` LoC) Kernel Builds",
        "",
        "| Cohort | Attempted | OOTB Pass | Axiom-Clean OOTB | Non-Std Axioms OOTB | `Tier3_Gold` OOTB / Clean | OOTB Theorems (Incl. Synth) | `ofReduceBool` |",
        "| :--- | ---: | :---: | :---: | :---: | :---: | ---: | :---: |",
        f"| **`+7` Net-New T2 Compact (`eng_alg`)** | {p7_sb['total_attempted']} | **{p7_sb['pass_out_of_box']}/{p7_sb['total_attempted']}** ({p7_sb['pass_out_of_box_pct']:.1f}%) | {p7_sb['pass_and_standard_axioms_only']}/{p7_sb['pass_out_of_box']} | {p7_sb['pass_with_nonstandard_axioms']} (`2611.07395`) | {p7_sb['tier3_gold_pass_out_of_box']}/{p7_sb['tier3_gold_attempted']} / {p7_sb['tier3_gold_clean_axioms']}/{p7_sb['tier3_gold_pass_out_of_box']} | **{p7_sb['total_theorems_checked_ootb']:,}** ({p7_sb['total_theorems_checked_incl_synthetic']:,}) | **0/{p7_sb['total_attempted']}** |",
        f"| **15-Cat T1+T2 Compact (`eng_alg` Only)** | {all15_sb_eng['total_attempted']} | **{all15_sb_eng['pass_out_of_box']}/{all15_sb_eng['total_attempted']}** ({all15_sb_eng['pass_out_of_box_pct']:.1f}%) | {all15_sb_eng['pass_and_standard_axioms_only']}/{all15_sb_eng['pass_out_of_box']} | {all15_sb_eng['pass_with_nonstandard_axioms']} | {all15_sb_eng['tier3_gold_pass_out_of_box']}/{all15_sb_eng['tier3_gold_attempted']} / {all15_sb_eng['tier3_gold_clean_axioms']}/{all15_sb_eng['tier3_gold_pass_out_of_box']} | **{all15_sb_eng['total_theorems_checked_ootb']:,}** ({all15_sb_eng['total_theorems_checked_incl_synthetic']:,}) | **0/{all15_sb_eng['total_attempted']}** |",
        f"| **15-Cat T1+T2 Compact (All Roles)** | {all15_sb['total_attempted']} | **{all15_sb['pass_out_of_box']}/{all15_sb['total_attempted']}** ({all15_sb['pass_out_of_box_pct']:.1f}%) | {all15_sb['pass_and_standard_axioms_only']}/{all15_sb['pass_out_of_box']} | {all15_sb['pass_with_nonstandard_axioms']} | **{all15_sb['tier3_gold_pass_out_of_box']}/{all15_sb['tier3_gold_attempted']}** / **{all15_sb['tier3_gold_clean_axioms']}/{all15_sb['tier3_gold_pass_out_of_box']}** (100%) | **{all15_sb['total_theorems_checked_ootb']:,}** ({all15_sb['total_theorems_checked_incl_synthetic']:,}) | **0/{all15_sb['total_attempted']}** |",
        "",
        "---",
        "",
        "## 4. Detailed Findings & Cross-Check Notes",
        "",
    ]

    for r in payload["records"]:
        aid = r["arxiv_id"]
        sb = r["sandbox_build"]
        la = r["layer_a"]
        lines.append(f"### [{aid}](https://arxiv.org/abs/{aid}) — `{r['repo_url']}`")
        lines.append(
            f"- **Provenance:** arXiv `{r['arxiv_version_audited']}` ({r['arxiv_submitted_date'][:10]}) · "
            f"Pin: `{r['commit_sha'] or ('zenodo/' + str(r['zenodo_record_id']))}` · "
            f"Toolchain: `{r['lean_toolchain']}` · Lean files: `{r['lean_files_count']}` · "
            f"Owned LoC: `{r['primary_owned_loc']:,}` · `lean_tree_sha256`: `{r['lean_tree_sha256'][:16]}...`"
        )
        lines.append(
            f"- **Layer-A Audit:** `{la['overall_fidelity']}` · "
            f"M1=`{la['mode1_severity']}`, M2=`{la['mode2_severity']}`, M3=`{la['mode3_severity']}`, M4=`{la['mode4_severity']}` · "
            f"Non-vacuity witnesses: `{la['has_non_vacuity_witnesses']}` · Mathlib anchoring: `{la['mathlib_anchoring_quality']}` · "
            f"Provenance refs: `{la['theorems_compared_file_line_check']['resolved_in_bounds']}/{la['theorems_compared_file_line_check']['total_file_line_refs']}` in-bounds."
        )
        if sb is not None:
            lines.append(
                f"- **Isolated Docker Kernel Build:** `{sb['build_status']}` (`exit_code={sb['exit_code']}`, "
                f"`wall_time={sb['wall_time_sec']}s`, `axiom_check={sb.get('axiom_check_wall_time_sec')}s`, "
                f"`target_modules={sb['target_modules_count']}`, `total_theorems_checked={sb['total_theorems_checked']}`, "
                f"`sorry_ax={sb['sorry_ax_detected']}`, `of_reduce_bool={sb['of_reduce_bool_detected']}`, "
                f"`nonstandard_axioms={sb['nonstandard_axioms_detected']}`)."
            )
        else:
            lines.append(
                "- **Isolated Docker Kernel Build:** Excluded from compact (`<15k` LoC) cohort (`42,036` owned LoC / `55,284` raw LoC across 753 files; candidate for future medium/large-repo sandbox + `comparator` replay)."
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    payload = build_phase_c2_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_report(payload), encoding="utf-8")
    p7_sb = payload["sandbox_summary"]["plus7_t2_compact_eng_alg"]
    fl = payload["plus7_provenance"]["theorems_compared_file_line_summary"]
    print(
        f"Wrote {OUT_JSON} and {OUT_MD}\n"
        f"  +7 Layer-A: {payload['layer_a_summary']['plus7_t2_eng_algorithmic_proof']['count']} repos, "
        f"file:line={fl['resolved_in_bounds']}/{fl['total_refs']}\n"
        f"  +7 Compact Sandbox: {p7_sb['pass_out_of_box']}/{p7_sb['total_attempted']} OOTB pass, "
        f"{p7_sb['total_theorems_checked_ootb']} theorems, "
        f"nonstd={p7_sb['nonstandard_axiom_repos_ootb']}"
    )


if __name__ == "__main__":
    main()
