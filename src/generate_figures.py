"""Generate publication-quality vector PDF figures from git-tracked `artifacts/`.

By default reads `artifacts/slices/2026-11/figure_inputs.json` and
`artifacts/longitudinal_summary.json` (zero SQLite dependency, enabling clean
regeneration in GitHub Actions or any fresh clone). Pass `--from-db data/survey.db`
to extract figure inputs directly from a local SQLite database instead.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

FIG_DIR = Path("papers/shared/figures")
PREVIEW_DIR = Path("data/fig_previews")
DEFAULT_FIGURE_INPUTS = Path("artifacts/slices/2026-11/figure_inputs.json")
DEFAULT_LONGITUDINAL_SUMMARY = Path("artifacts/longitudinal_summary.json")

# Paper-specific subpackage LoC overrides for multi-paper monorepos (verified in Phase 2 audits)
SUBPACKAGE_LOC = {
    "2611.09050": (139600, "139.6k*"),
    "2611.13584": (55300, "55.3k*"),
    "2611.15128": (4963, "5.0k*"),
}
SKIP_CITED = {
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
}

# Global clean publication style
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.8,
        "xtick.color": "#333333",
        "ytick.color": "#222222",
        "pdf.fonttype": 42,  # TrueType fonts embedded cleanly in PDF
        "ps.fonttype": 42,
    }
)


def _save(fig: plt.Figure, name: str, out_dir: Path = FIG_DIR, save_previews: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight", dpi=300)
    if save_previews:
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(PREVIEW_DIR / f"{name}.png", bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"Saved {out_dir / f'{name}.pdf'}")


def make_pipeline_funnel(
    fig_data: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    funnel = fig_data["funnel"]
    total = funnel["total_papers"]
    screened = funnel["screened"]
    candidates = funnel["candidates"]
    negatives = funnel["negatives"]
    confirmed = funnel["confirmed"]
    eng_math = funnel["eng_math"]
    audited = funnel["audited"]

    fig, ax = plt.subplots(figsize=(10.4, 3.25))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 3.25)
    ax.axis("off")

    stages = [
        ("Stage 1\nOAI-PMH Ingest", f"{total:,}", "8 arXiv cats\n0 LLM tokens", "#EEF4FA", "#2B6CB0"),
        ("Stage 2\nFull-Text Screen", f"{screened:,}", "99.83% HTML/PDF\n0 LLM tokens", "#E6F2FA", "#2B6CB0"),
        ("Stage 3\nStatic Profiler", f"{candidates}", "98.7% pruned\n3.4x meta recall", "#E6F4F1", "#0F766E"),
        ("Stage 4\nflash Triage", f"{confirmed}", "Confirmed Lean\n(0.95% of corpus)", "#FEF3C7", "#B45309"),
        ("Engineering\nMath Slice", f"{eng_math}", "71.8% of Lean\n17 in math.OC", "#FDE68A", "#B45309"),
        ("Stage 5 (Phase 2)\npro Layer-A Audit", f"{audited}", "Line-by-line\nLaTeX <-> Lean", "#EDE9FE", "#6D28D9"),
    ]

    box_w = 1.44
    box_h = 1.55
    gap = 0.28
    x0 = 0.18
    y0 = 1.48

    centers = []
    for i, (title, num, sub, fc, ec) in enumerate(stages):
        x = x0 + i * (box_w + gap)
        centers.append((x + box_w / 2, y0 + box_h / 2))
        rect = FancyBboxPatch(
            (x, y0),
            box_w,
            box_h,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            facecolor=fc,
            edgecolor=ec,
            linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(x + box_w / 2, y0 + box_h - 0.26, title, ha="center", va="top", fontsize=7.8, fontweight="bold", color="#1A202C")
        ax.text(x + box_w / 2, y0 + 0.70, num, ha="center", va="center", fontsize=15, fontweight="bold", color=ec)
        ax.text(x + box_w / 2, y0 + 0.14, sub, ha="center", va="bottom", fontsize=7.0, color="#374151")

        if i > 0:
            prev_x = x0 + (i - 1) * (box_w + gap) + box_w + 0.04
            ax.annotate(
                "",
                xy=(x - 0.04, y0 + box_h / 2),
                xytext=(prev_x, y0 + box_h / 2),
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.32", color="#4B5563", lw=1.3),
            )

    # Branch down from Stage 2 to Recall Calibration box
    s2_cx = x0 + 1 * (box_w + gap) + box_w / 2
    cal_x, cal_y, cal_w, cal_h = 0.18, 0.12, 6.20, 0.98
    cal_rect = FancyBboxPatch(
        (cal_x, cal_y),
        cal_w,
        cal_h,
        boxstyle="round,pad=0.04,rounding_size=0.09",
        facecolor="#F0FDF4",
        edgecolor="#15803D",
        linewidth=1.4,
        linestyle="--",
    )
    ax.add_patch(cal_rect)
    ax.annotate(
        "",
        xy=(s2_cx, cal_y + cal_h + 0.04),
        xytext=(s2_cx, y0 - 0.04),
        arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.30", color="#15803D", lw=1.3, ls="--"),
    )
    ax.text(
        cal_x + 0.16,
        cal_y + cal_h - 0.14,
        f"Stage-2 Recall Calibration on {negatives:,} Negatives (0 LLM tokens)",
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="bold",
        color="#14532D",
    )
    ax.text(
        cal_x + 0.16,
        cal_y + 0.12,
        "200 random GitHub-linked negatives (333 repos via gh api) + 100 non-GH negatives:\n"
        "0 / 200 missed Lean repos  |  95% Clopper-Pearson upper bound <= 1.49%\n"
        "0 / 100 broad metadata flags among non-GitHub negatives",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color="#1F2937",
        linespacing=1.32,
    )

    # Branch callout on right for Zero-Token vs LLM cost
    cost_x, cost_y, cost_w, cost_h = 6.66, 0.12, 3.56, 0.98
    cost_rect = FancyBboxPatch(
        (cost_x, cost_y),
        cost_w,
        cost_h,
        boxstyle="round,pad=0.04,rounding_size=0.09",
        facecolor="#F8FAFC",
        edgecolor="#64748B",
        linewidth=1.1,
    )
    ax.add_patch(cost_rect)
    ax.text(
        cost_x + 0.15,
        cost_y + cost_h - 0.14,
        "Artifact Coverage (Stage 3)",
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="bold",
        color="#1E293B",
    )
    ax.text(
        cost_x + 0.15,
        cost_y + 0.12,
        "GitHub (<=600 MB, incl. leanVM) + Zenodo + GitLab\n"
        "24 unique primary Lean repos (4.17M LoC)\n"
        "Strictly static: zero untrusted lake build / #eval",
        ha="left",
        va="bottom",
        fontsize=6.9,
        color="#334155",
        linespacing=1.32,
    )

    _save(fig, "fig_pipeline_funnel", out_dir=out_dir, save_previews=save_previews)


def make_category_bifurcation(
    fig_data: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    cat_labels = {
        "math.OC": "math.OC\n(Opt. & Control)",
        "cs.DC": "cs.DC\n(Distrib. Comp.)",
        "cs.IT": "cs.IT\n(Info. Theory)",
        "cs.CR": "cs.CR\n(Crypto & Sec.)",
        "eess.SY": "eess.SY\n(Systems & Ctrl)",
        "eess.SP": "eess.SP\n(Signal Proc.)",
        "cs.NI": "cs.NI\n(Networking)",
        "cs.RO": "cs.RO\n(Robotics)",
    }

    bif = fig_data["category_bifurcation"]
    cat_total: Counter[str] = Counter(bif["cat_total"])
    cat_role: dict[str, Counter[str]] = {c: Counter(bif["cat_role"].get(c, {})) for c in cat_labels}

    # Order by total Lean % descending, then papers descending
    order = sorted(
        cat_labels.keys(),
        key=lambda c: (sum(cat_role[c].values()) / max(cat_total[c], 1), -cat_total[c]),
        reverse=True,
    )
    order = list(reversed(order))  # top bar at top of horizontal chart

    y = np.arange(len(order))
    eng_pct = np.array([100.0 * cat_role[c]["engineering_math_proof"] / cat_total[c] for c in order])
    tcs_pct = np.array([100.0 * cat_role[c]["pure_tcs_or_math"] / cat_total[c] for c in order])
    sys_pct = np.array([100.0 * cat_role[c]["software_or_system_fv"] / cat_total[c] for c in order])
    tot_pct = eng_pct + tcs_pct + sys_pct

    fig, ax = plt.subplots(figsize=(7.6, 4.4))

    # Highlight the 0% trio band
    ax.axhspan(-0.5, 2.5, color="#F3F4F6", alpha=0.85, zorder=0)
    ax.text(
        2.92,
        1.0,
        "Zero-Adoption Trio\n0 / 1,817 papers (0.00%)",
        ha="right",
        va="center",
        fontsize=8.2,
        fontweight="bold",
        color="#6B7280",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#D1D5DB", lw=1.0),
    )

    h = 0.62
    ax.barh(y, eng_pct, height=h, color="#1D4ED8", label="Engineering / Applied Math Proof (n=28)", zorder=3)
    ax.barh(y, tcs_pct, left=eng_pct, height=h, color="#D97706", label="Pure TCS / Math Cross-List (n=7)", zorder=3)
    ax.barh(y, sys_pct, left=eng_pct + tcs_pct, height=h, color="#64748B", label="Software / Systems FV (n=4)", zorder=3)

    for idx, c in enumerate(order):
        k = sum(cat_role[c].values())
        n = cat_total[c]
        pct = tot_pct[idx]
        lbl = f"{pct:.2f}%  ({k}/{n})" if k > 0 else f"0.00%  (0/{n})"
        color = "#111827" if k > 0 else "#6B7280"
        ax.text(pct + 0.06, idx, lbl, va="center", ha="left", fontsize=8.3, fontweight="bold" if k > 0 else "normal", color=color)

    ax.set_yticks(y)
    ax.set_yticklabels([cat_labels[c] for c in order], fontsize=8.4)
    ax.set_xlabel("Confirmed Lean-Contributing Papers (% of category submissions, Nov 1–19, 2026)")
    ax.set_title("Disciplinary Bifurcation of Lean 4 Adoption Across Eight Engineering arXiv Categories", pad=10)
    ax.set_xlim(0, 3.32)
    ax.grid(axis="x", linestyle=":", alpha=0.6, zorder=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", bbox_to_anchor=(0.99, 0.36), frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=8.0)

    _save(fig, "fig_category_bifurcation", out_dir=out_dir, save_previews=save_previews)


def make_paradigms_and_loc(
    fig_data: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    rows = fig_data["confirmed_lean_papers"]

    # Left panel: Paradigm x Verification Tier
    par_order = [
        ("P1_paper_first_posthoc", "P1: Paper-First\nPost-Hoc"),
        ("P0_opaque_or_unspecified", "P0: Opaque /\nUnspecified"),
        ("P4_speclock_solve_distill", "P4: Spec-Lock\n(comparator)"),
        ("P2_lean_first", "P2: Lean-First\nAuto-Informal."),
        ("P3_blueprint_sync", "P3: Blueprint\nSync (LeanArch.)"),
    ]
    par_tier = {k: Counter() for k, _ in par_order}
    for r in rows:
        par_tier[r["authoring_paradigm"]][r["verification_tier"]] += 1

    # Right panel: LoC bars for all 25 scanned papers
    loc_items = []
    for r in rows:
        aid = r["arxiv_id"]
        role = r.get("paper_domain_role")
        par = r["authoring_paradigm"]
        repos = [
            rp
            for rp in r.get("lean_repos", [])
            if rp.get("lean_file_count", 0) > 0 and rp["repo"] not in SKIP_CITED
        ]
        if not repos:
            continue
        if aid in SUBPACKAGE_LOC:
            loc, loc_str = SUBPACKAGE_LOC[aid]
        else:
            loc = repos[0].get("loc_nonempty", 0)
            loc_str = f"{loc/1000:.1f}k" if loc >= 10000 else f"{loc:,}"
        if loc <= 0:
            continue
        if aid == "2611.26272":
            cat_col = "#DC2626"  # Bulk Paper2Lean
        elif par == "P4_speclock_solve_distill":
            cat_col = "#0D9488"  # P4 Spec-Lock
        elif role == "engineering_math_proof":
            cat_col = "#2563EB"  # Eng Math P1
        elif role == "pure_tcs_or_math":
            cat_col = "#D97706"  # Pure TCS
        else:
            cat_col = "#64748B"  # Software/System FV
        tag = f"{aid} ({r['primary_category']})"
        loc_items.append((loc, tag, loc_str, cat_col))

    loc_items.sort(key=lambda x: x[0])  # ascending so largest is on top

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.4), gridspec_kw={"width_ratios": [1.0, 1.48]})

    # --- Panel A: Paradigms stacked by Tier ---
    rev_par = list(reversed(par_order))
    yp = np.arange(len(rev_par))
    t3 = np.array([par_tier[k]["Tier3_Gold"] for k, _ in rev_par])
    t2 = np.array([par_tier[k]["Tier2_Silver"] for k, _ in rev_par])
    t1 = np.array([par_tier[k]["Tier1_Bronze"] for k, _ in rev_par])
    tot = t3 + t2 + t1

    ax1.barh(yp, t3, height=0.58, color="#059669", label="Tier 3: Gold (n=19)")
    ax1.barh(yp, t2, left=t3, height=0.58, color="#3B82F6", label="Tier 2: Silver (n=7)")
    ax1.barh(yp, t1, left=t3 + t2, height=0.58, color="#9CA3AF", label="Tier 1: Bronze (n=13)")

    for i, (k, _) in enumerate(rev_par):
        pct = 100.0 * tot[i] / len(rows)
        lbl = f"{tot[i]} ({pct:.1f}%)" if tot[i] > 0 else "0 (0.0%)"
        ax1.text(tot[i] + 0.5, i, lbl, va="center", ha="left", fontsize=8.3, fontweight="bold" if tot[i] > 0 else "normal", color="#111827" if tot[i] > 0 else "#9CA3AF")

    ax1.set_yticks(yp)
    ax1.set_yticklabels([lbl for _, lbl in rev_par], fontsize=8.3)
    ax1.set_xlim(0, 35.5)
    ax1.set_xlabel("Confirmed Lean Papers (n = 39)")
    ax1.set_title("(a) Authoring Paradigms & Verification Tiers", pad=8)
    ax1.grid(axis="x", linestyle=":", alpha=0.6)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.8)

    # --- Panel B: Log-scale LoC across 25 scanned repos ---
    yl = np.arange(len(loc_items))
    locs = [x[0] for x in loc_items]
    tags = [x[1] for x in loc_items]
    lstrs = [x[2] for x in loc_items]
    cols = [x[3] for x in loc_items]

    ax2.barh(yl, locs, height=0.72, color=cols, alpha=0.92, zorder=3)
    ax2.set_xscale("log")
    ax2.axvline(20000, color="#DC2626", linestyle="--", linewidth=1.1, alpha=0.75, zorder=2)
    ax2.text(26000, 7.2, "Mode #10 Bloat\nthreshold (20k LoC)", fontsize=7.4, color="#B91C1C", va="center", ha="left",
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF2F2", edgecolor="#FECACA", lw=0.8))

    for i, (lv, ls) in enumerate(zip(locs, lstrs)):
        ax2.text(lv * 1.13, i, ls, va="center", ha="left", fontsize=7.2, color="#1F2937")

    ax2.set_yticks(yl)
    ax2.set_yticklabels(tags, fontsize=7.2, family="monospace")
    ax2.set_xlim(250, 3.2e6)
    ax2.set_xlabel("Non-Empty Lean 4 Lines of Code (log scale; *subpackage LoC)")
    ax2.set_title("(b) Codebase Scale Across 25 Scanned Lean Artifacts", pad=8)
    ax2.grid(axis="x", which="major", linestyle=":", alpha=0.6, zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    handles = [
        mpatches.Patch(color="#2563EB", label="Eng. Math (P1)"),
        mpatches.Patch(color="#0D9488", label="Eng. Math (P4 spec-lock)"),
        mpatches.Patch(color="#DC2626", label="Bulk Autoform. (Paper2Lean)"),
        mpatches.Patch(color="#D97706", label="Pure TCS / Math"),
        mpatches.Patch(color="#64748B", label="Software / Sys. FV"),
    ]
    ax2.legend(handles=handles, loc="lower right", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.2)

    plt.tight_layout(w_pad=2.0)
    _save(fig, "fig_paradigms_and_loc", out_dir=out_dir, save_previews=save_previews)


def make_phase2_heatmap(
    fig_data: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    audits = []
    for raw in fig_data["layer_a_audits"]:
        a = dict(raw)
        a["par"] = (a.get("authoring_paradigm") or "?").split("_")[0]
        audits.append(a)

    # Order: material_undisclosed_drift_or_risk (Paper2Lean) at top, then partial, then mostly_faithful, then high_faithful
    fidelity_rank = {
        "material_undisclosed_drift_or_risk": 0,
        "partial_or_weakened_formalization": 1,
        "mostly_faithful_with_disclosed_gaps": 2,
        "high_faithful": 3,
    }
    sev_score = {"none": 0, "minor_disclosed": 1, "minor_undisclosed": 2, "moderate": 3, "severe": 4}
    audits.sort(
        key=lambda a: (
            fidelity_rank.get(a["overall_fidelity"], 9),
            -(
                sev_score.get(a["mode1_statement_drift"]["severity"], 0)
                + sev_score.get(a["mode2_scope_downgrade"]["severity"], 0)
                + sev_score.get(a["mode3_definition_smuggling"]["severity"], 0)
                + sev_score.get(a["mode4_junk_or_vacuity"]["severity"], 0)
            ),
            a["arxiv_id"],
        )
    )

    short_sev = {
        "none": "None",
        "minor_disclosed": "Minor (discl.)",
        "minor_undisclosed": "Minor (undiscl.)",
        "moderate": "Moderate",
        "severe": "Severe",
    }
    sev_colors = {
        "none": ("#DCFCE7", "#166534"),
        "minor_disclosed": ("#E0F2FE", "#075985"),
        "minor_undisclosed": ("#FEF3C7", "#92400E"),
        "moderate": ("#FEE2E2", "#991B1B"),
        "severe": ("#FCA5A5", "#7F1D1D"),
    }
    bool_colors = {
        True: ("#DCFCE7", "#166534", "Yes"),
        False: ("#F3F4F6", "#6B7280", "No"),
    }
    mathlib_colors = {
        "strong_mathlib": ("#DCFCE7", "#166534", "Strong"),
        "mixed_custom_and_mathlib": ("#E0F2FE", "#075985", "Mixed"),
        "mostly_custom_defs": ("#FEE2E2", "#991B1B", "Custom"),
    }
    overall_short = {
        "material_undisclosed_drift_or_risk": ("Material Risk", "#FEE2E2", "#991B1B"),
        "partial_or_weakened_formalization": ("Partial", "#FEF3C7", "#92400E"),
        "mostly_faithful_with_disclosed_gaps": ("Mostly Faithful", "#E0F2FE", "#075985"),
        "high_faithful": ("High Faithful", "#DCFCE7", "#166534"),
    }

    col_headers = [
        "Overall\nVerdict",
        "Mode #1\nStmt. Drift",
        "Mode #2\nScope Gap",
        "Mode #3\nDef. Smug.",
        "Mode #4\nJunk / Vac.",
        "Non-Vac.\nWitness?",
        "Mathlib\nAnchor",
    ]
    n_rows = len(audits)
    n_cols = len(col_headers)

    fig, ax = plt.subplots(figsize=(10.2, 5.7))
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.invert_yaxis()

    for r_idx, a in enumerate(audits):
        ov_lbl, ov_bg, ov_fg = overall_short[a["overall_fidelity"]]
        cells = [
            (ov_lbl, ov_bg, ov_fg, True),
            (short_sev[a["mode1_statement_drift"]["severity"]], *sev_colors[a["mode1_statement_drift"]["severity"]], False),
            (short_sev[a["mode2_scope_downgrade"]["severity"]], *sev_colors[a["mode2_scope_downgrade"]["severity"]], False),
            (short_sev[a["mode3_definition_smuggling"]["severity"]], *sev_colors[a["mode3_definition_smuggling"]["severity"]], False),
            (short_sev[a["mode4_junk_or_vacuity"]["severity"]], *sev_colors[a["mode4_junk_or_vacuity"]["severity"]], False),
            (bool_colors[bool(a["has_non_vacuity_witnesses"])][2], bool_colors[bool(a["has_non_vacuity_witnesses"])][0], bool_colors[bool(a["has_non_vacuity_witnesses"])][1], False),
            (mathlib_colors[a["mathlib_anchoring_quality"]][2], mathlib_colors[a["mathlib_anchoring_quality"]][0], mathlib_colors[a["mathlib_anchoring_quality"]][1], False),
        ]
        for c_idx, (txt, bg, fg, is_bold) in enumerate(cells):
            rect = mpatches.Rectangle((c_idx + 0.03, r_idx + 0.06), 0.94, 0.88, facecolor=bg, edgecolor="white", linewidth=1.2)
            ax.add_patch(rect)
            fw = "bold" if (is_bold or txt in ("Moderate", "Severe", "Minor (undiscl.)")) else "normal"
            ax.text(c_idx + 0.5, r_idx + 0.5, txt, ha="center", va="center", fontsize=7.6, color=fg, fontweight=fw)

    # Bold divider separating Paper2Lean (bulk pipeline, row 0) from 16 author-owned repos (rows 1..16)
    ax.axhline(1.0, color="#991B1B", linewidth=2.2, linestyle="-", zorder=5)
    ax.text(
        n_cols + 0.08,
        0.5,
        "Bulk Pipeline\n(Paper2Lean)",
        ha="left",
        va="center",
        fontsize=7.6,
        fontweight="bold",
        color="#991B1B",
    )
    ax.text(
        n_cols + 0.08,
        9.0,
        "16 Independent\nAuthor-Owned\nEngineering Repos\n(0 mod/sev M1/M3/M4)",
        ha="left",
        va="center",
        fontsize=7.6,
        fontweight="bold",
        color="#166534",
    )

    row_labels = []
    for a in audits:
        suffix = " [BULK]" if a["arxiv_id"] == "2611.26272" else ""
        row_labels.append(f"{a['arxiv_id']} ({a['primary_category']}, {a['par']}){suffix}")

    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels(col_headers, fontsize=8.2, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels(row_labels, fontsize=7.8, family="monospace")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        "Phase 2 Adversarial Layer-A Semantic Fidelity Matrix (n = 17 Engineering-Math Repos)",
        pad=26,
        fontsize=10.8,
        fontweight="bold",
    )

    _save(fig, "fig_phase2_heatmap", out_dir=out_dir, save_previews=save_previews)


def make_longitudinal_curve(
    summary_path: Path = DEFAULT_LONGITUDINAL_SUMMARY,
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    if not summary_path.exists():
        raise FileNotFoundError(f"Longitudinal summary JSON not found: {summary_path}")
    data = json.loads(summary_path.read_text())
    slices = data["slices"]
    t0, t1, t2 = slices[0], slices[1], slices[2]

    x = np.array([0, 1, 2], dtype=float)
    x_labels = [
        f"T0: Nov 1–19, 2025\n(n = {t0['total_papers']:,})",
        f"T1: May 1–19, 2026\n(n = {t1['total_papers']:,})",
        f"T2: Nov 1–19, 2026\n(n = {t2['total_papers']:,})",
    ]

    v1_pct = np.array([s["v1"]["pct"] for s in slices])
    vl_pct = np.array([s["v_latest"]["pct"] for s in slices])
    cand_pct = np.array([s["stage2_lean_cand_pct"] for s in slices])
    bey_pct = np.array([s["stage2_beyond_any_pct"] for s in slices])

    # 95% error bars for v1 (Clopper-Pearson upper bound at k=0; Wilson CI otherwise)
    yerr_lo = []
    yerr_hi = []
    for s in slices:
        p = s["v1"]["pct"]
        if s["v1"]["count"] == 0:
            lo = 0.0
            hi = 100.0 * (1.0 - 0.05 ** (1.0 / s["total_papers"]))
        else:
            lo, hi = s["v1"]["wilson_95"]
        yerr_lo.append(max(0.0, p - lo))
        yerr_hi.append(max(0.0, hi - p))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.45), gridspec_kw={"width_ratios": [1.05, 1.12]})

    # --- Panel A: Aggregate Inflection vs Beyond-Lean Control ---
    ax1.plot(
        x, bey_pct,
        color="#64748B", linestyle="-.", marker="D", markersize=6.2, linewidth=1.8,
        label="Stage-2 Beyond-Lean FV control (all other tools)", zorder=3,
    )
    ax1.plot(
        x, cand_pct,
        color="#7C3AED", linestyle=":", marker="^", markersize=6.5, linewidth=1.9,
        label="Stage-2 Lean 4 candidates (full-text)", zorder=4,
    )
    ax1.plot(
        x, vl_pct,
        color="#0284C7", linestyle="--", marker="s", markersize=5.8, linewidth=1.6,
        label="Confirmed Lean (incl. retroactive v2 revisions)", zorder=4,
    )
    ax1.errorbar(
        x, v1_pct, yerr=[yerr_lo, yerr_hi],
        color="#1D4ED8", linestyle="-", marker="o", markersize=7.2, linewidth=2.6,
        capsize=4, capthick=1.3, elinewidth=1.3,
        label="Confirmed Lean (contemporaneous v1, 95% CI)", zorder=5,
    )

    # Direct annotations with carefully separated vertical offsets (zero overlap)
    ax1.text(0.0, bey_pct[0] - 0.10, f"{bey_pct[0]:.2f}% (n={t0['stage2_beyond_any']})", ha="left", va="top", fontsize=7.6, color="#475569")
    ax1.text(1.0, bey_pct[1] + 0.07, f"{bey_pct[1]:.2f}% (n={t1['stage2_beyond_any']})", ha="center", va="bottom", fontsize=7.6, color="#475569")
    ax1.text(2.05, bey_pct[2] - 0.05, f"{bey_pct[2]:.2f}%\n(n={t2['stage2_beyond_any']})", ha="left", va="center", fontsize=7.6, color="#475569")

    ax1.text(-0.02, cand_pct[0] + 0.14, f"{cand_pct[0]:.2f}% (n={t0['stage2_lean_candidates']})", ha="left", va="bottom", fontsize=7.5, color="#6D28D9")
    ax1.text(0.95, cand_pct[1] + 0.06, f"{cand_pct[1]:.2f}% (n={t1['stage2_lean_candidates']})", ha="right", va="bottom", fontsize=7.6, color="#6D28D9")
    ax1.text(2.05, cand_pct[2] + 0.08, f"{cand_pct[2]:.2f}%\n(n={t2['stage2_lean_candidates']})", ha="left", va="center", fontsize=7.6, fontweight="bold", color="#6D28D9")

    ax1.text(0.0, -0.08, "0.00% (0 v1)\n[0.04% latest]", ha="center", va="top", fontsize=7.4, fontweight="bold", color="#1E3A8A")
    ax1.text(1.0, -0.08, "0.15% (5 v1)\n[0.21% latest]", ha="center", va="top", fontsize=7.4, fontweight="bold", color="#1D4ED8")
    ax1.text(2.05, v1_pct[2] - 0.04, "0.95%\n(n=39)", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#1D4ED8")

    ax1.annotate(
        "6.3× jump in 6 mo\n(median LoC: 749 → 23.9k;\nAI discl.: 40% → 76.9%)",
        xy=(1.58, 0.59),
        xytext=(0.56, 1.00),
        ha="center",
        va="center",
        fontsize=7.3,
        fontweight="bold",
        color="#1E3A8A",
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#EFF6FF", edgecolor="#93C5FD", lw=1.0),
        arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.25, connectionstyle="arc3,rad=-0.16"),
    )

    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, fontsize=8.1)
    ax1.set_xlim(-0.28, 2.48)
    ax1.set_ylim(-0.30, 2.26)
    ax1.set_ylabel("Share of 8-Category Corpus (%)")
    ax1.set_title("(a) Lean 4 Inflection vs. Flat Beyond-Lean FV Control", pad=9)
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.1)

    # --- Panel B: Per-Category Contemporaneous v1 Trajectories ---
    cat_styles = [
        ("math.OC", "#1D4ED8", "o", "-", 2.4, "math.OC (2.62%)"),
        ("cs.DC",   "#0F766E", "s", "-", 2.0, "cs.DC (1.79%)"),
        ("cs.IT",   "#D97706", "^", "-", 2.0, "cs.IT (1.78%)"),
        ("cs.CR",   "#DC2626", "D", "-", 1.9, "cs.CR (1.11%)"),
        ("eess.SY", "#7C3AED", "v", "--", 1.7, "eess.SY (0.41%)"),
        ("eess.SP", "#6B7280", "P", ":", 1.5, "eess.SP (0.24%→0%)"),
    ]
    label_y_override = {
        "math.OC": 2.62,
        "cs.DC":   1.91,
        "cs.IT":   1.65,
        "cs.CR":   1.11,
        "eess.SY": 0.45,
        "eess.SP": 0.14,
    }

    for cat, col, mk, ls, lw, lbl in cat_styles:
        vals = [100.0 * s["v1"]["cat_lean"].get(cat, 0) / max(s["cat_total"].get(cat, 1), 1) for s in slices]
        ax2.plot(x, vals, color=col, marker=mk, linestyle=ls, linewidth=lw, markersize=6.0, zorder=4)
        ly = label_y_override[cat]
        ax2.text(2.06, ly, lbl, ha="left", va="center", fontsize=7.8, fontweight="bold" if vals[2] > 0 else "normal", color=col)
        if abs(ly - vals[2]) > 0.05:
            ax2.plot([2.01, 2.05], [vals[2], ly], color=col, lw=0.8, alpha=0.7)

    ax2.plot(x, [0.0, 0.0, 0.0], color="#9CA3AF", linestyle="-", linewidth=1.6, zorder=2)
    ax2.text(2.06, -0.05, "cs.NI & cs.RO (0.00%)", ha="left", va="center", fontsize=7.6, color="#6B7280")

    ax2.annotate(
        "Earliest v1 adopters\nin May 2026: cs.CR (0.44%),\ncs.DC (0.32%), eess.SP (0.24%)",
        xy=(1.0, 0.44),
        xytext=(0.72, 1.38),
        ha="center",
        va="center",
        fontsize=7.2,
        color="#374151",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#F9FAFB", edgecolor="#D1D5DB", lw=0.9),
        arrowprops=dict(arrowstyle="->", color="#6B7280", lw=1.0, connectionstyle="arc3,rad=-0.12"),
    )

    ax2.set_xticks(x)
    ax2.set_xticklabels(x_labels, fontsize=8.1)
    ax2.set_xlim(-0.18, 2.78)
    ax2.set_ylim(-0.20, 2.95)
    ax2.set_ylabel("Confirmed Lean v1 Adoption (%)")
    ax2.set_title("(b) Disciplinary Divergence Across Eight Categories (v1)", pad=9)
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout(w_pad=1.8)
    _save(fig, "fig_longitudinal_curve", out_dir=out_dir, save_previews=save_previews)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate vector PDF figures from git-tracked artifacts/ (or optional --from-db)."
    )
    ap.add_argument("--figure-inputs", type=Path, default=DEFAULT_FIGURE_INPUTS)
    ap.add_argument("--longitudinal-summary", type=Path, default=DEFAULT_LONGITUDINAL_SUMMARY)
    ap.add_argument(
        "--from-db",
        type=Path,
        default=None,
        help="Optional SQLite DB path (e.g. data/survey.db) to extract figure inputs directly.",
    )
    ap.add_argument("--out-dir", type=Path, default=FIG_DIR)
    ap.add_argument("--save-previews", action="store_true", help="Also write PNG previews to data/fig_previews/.")
    args = ap.parse_args()

    if args.from_db is not None:
        from src.export_artifacts import build_figure_inputs

        fig_data = build_figure_inputs(args.from_db, slice_id="from-db")
    else:
        if not args.figure_inputs.exists():
            raise FileNotFoundError(
                f"Figure inputs JSON not found: {args.figure_inputs}. "
                "Run `uv run python -m src.export_artifacts --all` or pass `--from-db data/survey.db`."
            )
        fig_data = json.loads(args.figure_inputs.read_text())

    make_pipeline_funnel(fig_data, out_dir=args.out_dir, save_previews=args.save_previews)
    make_category_bifurcation(fig_data, out_dir=args.out_dir, save_previews=args.save_previews)
    make_paradigms_and_loc(fig_data, out_dir=args.out_dir, save_previews=args.save_previews)
    make_phase2_heatmap(fig_data, out_dir=args.out_dir, save_previews=args.save_previews)
    make_longitudinal_curve(args.longitudinal_summary, out_dir=args.out_dir, save_previews=args.save_previews)
    print("All 5 figures generated successfully.")


if __name__ == "__main__":
    main()
