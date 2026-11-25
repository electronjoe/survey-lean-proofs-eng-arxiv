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
DEFAULT_PHASE_C1 = Path("artifacts/phase_c1_15cat_longitudinal.json")
DEFAULT_PLUS7_AUDITS = Path("artifacts/slices/2026-11/plus7_layer_a_audits.json")
DEFAULT_PHASE_C2 = Path("artifacts/phase_c2_plus7_audits.json")
DEFAULT_SANDBOX_DIR = Path("artifacts/sandbox_builds")

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
    # Compute unique primary scanned artifact count & raw LoC dynamically from fig_data
    unique_primary_repos: dict[str, int] = {}
    for p in fig_data.get("confirmed_lean_papers", []):
        owned = [
            rp
            for rp in p.get("lean_repos", [])
            if rp.get("lean_file_count", 0) > 0
            and rp.get("repo") not in SKIP_CITED
            and rp.get("loc_nonempty", 0) > 0
        ]
        if not owned:
            continue
        best = max(owned, key=lambda rp: rp.get("loc_nonempty", 0))
        unique_primary_repos[best["repo"]] = max(
            unique_primary_repos.get(best["repo"], 0), int(best["loc_nonempty"])
        )
    n_unique_primary = len(unique_primary_repos)
    raw_primary_loc_m = sum(unique_primary_repos.values()) / 1e6

    ax.text(
        cost_x + 0.15,
        cost_y + 0.12,
        "GitHub (<=600 MB, incl. zips) + Zenodo + arXiv anc.\n"
        f"{n_unique_primary} unique primary Lean artifacts ({raw_primary_loc_m:.2f}M LoC)\n"
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
    phase_c1_path: Path = DEFAULT_PHASE_C1,
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    if phase_c1_path.is_file():
        c1 = json.loads(phase_c1_path.read_text(encoding="utf-8"))
        t2_p15 = next(s["panel_15cat"] for s in c1["slices"] if s["short_id"] == "T2")
        per_cat = t2_p15["per_category"]
        cat_labels = {
            "cs.GT": "cs.GT* (Game Theory / OR)",
            "math.DS": "math.DS* (Dynamical Sys.)",
            "math.OC": "math.OC (Opt. & Control)",
            "cs.DC": "cs.DC (Distrib. Comp.)",
            "cs.IT": "cs.IT (Info. Theory)",
            "cs.CR": "cs.CR (Crypto & Sec.)",
            "physics.flu-dyn": "physics.flu-dyn* (Fluids)",
            "eess.SY": "eess.SY (Systems & Ctrl)",
            "eess.SP": "eess.SP (Signal Proc.)",
            "eess.IV": "eess.IV* (Image & Video)",
            "eess.AS": "eess.AS* (Audio & Speech)",
            "cs.NI": "cs.NI (Networking)",
            "cs.RO": "cs.RO (Robotics)",
            "cs.PF": "cs.PF* (Perf. / Queueing)",
            "cs.CE": "cs.CE* (Comp. Eng.)",
        }
        order = sorted(
            cat_labels.keys(),
            key=lambda c: (
                per_cat[c]["confirmed_v1"]["pct"],
                per_cat[c]["roles_v1"]["eng_algorithmic_proof"] / max(per_cat[c]["total_papers"], 1),
                -per_cat[c]["total_papers"],
            ),
            reverse=True,
        )
        order = list(reversed(order))
        y = np.arange(len(order))
        eng_pct = np.array([100.0 * per_cat[c]["roles_v1"]["eng_algorithmic_proof"] / per_cat[c]["total_papers"] for c in order])
        tcs_pct = np.array([100.0 * per_cat[c]["roles_v1"]["pure_math_or_tcs"] / per_cat[c]["total_papers"] for c in order])
        sys_pct = np.array([100.0 * per_cat[c]["roles_v1"]["operational_system_fv"] / per_cat[c]["total_papers"] for c in order])
        meta_pct = np.array([100.0 * per_cat[c]["roles_v1"]["meta_formalization_system"] / per_cat[c]["total_papers"] for c in order])
        tot_pct = eng_pct + tcs_pct + sys_pct + meta_pct

        r_v1 = t2_p15["roles_v1"]
        fig, ax = plt.subplots(figsize=(8.6, 5.5))
        n_zeros = sum(1 for c in order if per_cat[c]["confirmed_v1"]["count"] == 0)
        ax.axhspan(-0.5, n_zeros - 0.5, color="#F3F4F6", alpha=0.88, zorder=0)
        zero_sum = sum(per_cat[c]["total_papers"] for c in order if per_cat[c]["confirmed_v1"]["count"] == 0)
        ax.text(
            10.85,
            (n_zeros - 1) / 2.0,
            f"Seven Zero-Adoption T2 Categories\n0 / {zero_sum:,} category-tagged papers (0.00%)\n"
            f"Incl. 0/752 across eess.SP ∪ IV ∪ AS (100% eess.*)",
            ha="right",
            va="center",
            fontsize=7.9,
            fontweight="bold",
            color="#4B5563",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#D1D5DB", lw=1.0),
        )

        h = 0.66
        ax.barh(y, eng_pct, height=h, color="#1D4ED8", label=f"Eng. Algorithmic Proof (n={r_v1['eng_algorithmic_proof']['count']})", zorder=3)
        ax.barh(y, tcs_pct, left=eng_pct, height=h, color="#D97706", label=f"Pure Math / TCS Cross-List (n={r_v1['pure_math_or_tcs']['count']})", zorder=3)
        ax.barh(y, sys_pct, left=eng_pct + tcs_pct, height=h, color="#64748B", label=f"Operational SW/DB/Sys FV (n={r_v1['operational_system_fv']['count']})", zorder=3)
        ax.barh(y, meta_pct, left=eng_pct + tcs_pct + sys_pct, height=h, color="#DC2626", label=f"Meta-Formalization System (n={r_v1['meta_formalization_system']['count']})", zorder=3)

        for idx, c in enumerate(order):
            k = per_cat[c]["confirmed_v1"]["count"]
            k_eng = per_cat[c]["roles_v1"]["eng_algorithmic_proof"]
            n = per_cat[c]["total_papers"]
            pct = tot_pct[idx]
            if k > 0:
                eng_p = 100.0 * k_eng / n
                lbl = f"{pct:.2f}% ({k}/{n}; eng-alg: {eng_p:.2f}%)"
                color = "#111827"
            else:
                lbl = f"0.00% (0/{n})"
                color = "#6B7280"
            ax.text(pct + 0.12, idx, lbl, va="center", ha="left", fontsize=7.6, fontweight="bold" if k > 0 else "normal", color=color)

        ax.set_yticks(y)
        ax.set_yticklabels([cat_labels[c] for c in order], fontsize=8.0)
        ax.set_xlabel("Confirmed Lean 4 v1 Adoption (% of category submissions, Nov 1–19, 2026; * = +7 expansion)")
        ax.set_title("4-Way Stratified Lean 4 Adoption Across All 15 Engineering arXiv Categories (T2)", pad=10)
        ax.set_xlim(0, 11.2)
        ax.grid(axis="x", linestyle=":", alpha=0.6, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="center right", bbox_to_anchor=(0.99, 0.56), frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.8)
        _save(fig, "fig_category_bifurcation", out_dir=out_dir, save_previews=save_previews)
        return

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
    ax2.set_yticklabels(tags, fontsize=6.9, family="monospace")
    ax2.set_xlim(250, 3.2e6)
    ax2.set_xlabel("Non-Empty Lean 4 Lines of Code (log scale; *subpackage LoC)")
    ax2.set_title(f"(b) Codebase Scale Across {len(loc_items)} Scanned Lean Artifacts", pad=8)
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
    plus7_audits_path: Path = DEFAULT_PLUS7_AUDITS,
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    audits = []
    seen_ids: set[str] = set()
    for raw in fig_data["layer_a_audits"]:
        a = dict(raw)
        a["par"] = (a.get("authoring_paradigm") or "?").split("_")[0]
        a["_is_plus7"] = False
        audits.append(a)
        seen_ids.add(a["arxiv_id"])

    if plus7_audits_path.is_file():
        p7 = json.loads(plus7_audits_path.read_text(encoding="utf-8"))
        for raw in p7.get("audits", []):
            if raw["arxiv_id"] in seen_ids:
                continue
            a = dict(raw)
            a["par"] = (a.get("authoring_paradigm") or "?").split("_")[0]
            a["_is_plus7"] = True
            audits.append(a)
            seen_ids.add(a["arxiv_id"])

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

    fig, ax = plt.subplots(figsize=(10.5, max(6.4, 0.31 * n_rows + 0.1)))
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
            ax.text(c_idx + 0.5, r_idx + 0.5, txt, ha="center", va="center", fontsize=7.4, color=fg, fontweight=fw)

    # Bold divider separating Paper2Lean (bulk pipeline, row 0) from independent author-owned repos (rows 1..n_rows-1)
    n_indep = sum(1 for a in audits if a["arxiv_id"] != "2611.26272")
    ax.axhline(1.0, color="#991B1B", linewidth=2.2, linestyle="-", zorder=5)
    ax.text(
        n_cols + 0.08,
        0.5,
        "Bulk Pipeline\n(Paper2Lean)",
        ha="left",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="#991B1B",
    )
    ax.text(
        n_cols + 0.08,
        1.0 + (n_rows - 1) / 2.0,
        f"{n_indep} Independent\nAuthor-Owned Repos\n(0 Material Risk;\n0 mod/sev M3/M4)",
        ha="left",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="#166534",
    )

    row_labels = []
    for a in audits:
        if a["arxiv_id"] == "2611.26272":
            suffix = " [BULK]"
        elif a.get("_is_plus7"):
            suffix = " [+7]"
        else:
            suffix = ""
        row_labels.append(f"{a['arxiv_id']} ({a['primary_category']}, {a['par']}){suffix}")

    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels(col_headers, fontsize=8.1, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels(row_labels, fontsize=7.5, family="monospace")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        f"Phase 2 Adversarial Layer-A Semantic Fidelity Matrix (n = {n_rows} T2 Repos Across 15 Categories)",
        pad=26,
        fontsize=10.6,
        fontweight="bold",
    )

    _save(fig, "fig_phase2_heatmap", out_dir=out_dir, save_previews=save_previews)


def make_longitudinal_curve(
    summary_path: Path = DEFAULT_LONGITUDINAL_SUMMARY,
    phase_c1_path: Path = DEFAULT_PHASE_C1,
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    if phase_c1_path.is_file():
        c1 = json.loads(phase_c1_path.read_text(encoding="utf-8"))
        slices = c1["slices"]
        p15s = [s["panel_15cat"] for s in slices]
        x = np.array([0, 1, 2], dtype=float)
        x_labels = [
            f"T0: Nov 1–19, 2025\n(n = {p15s[0]['total_papers']:,})",
            f"T1: May 1–19, 2026\n(n = {p15s[1]['total_papers']:,})",
            f"T2: Nov 1–19, 2026\n(n = {p15s[2]['total_papers']:,})",
        ]

        v1_pct = np.array([p["confirmed_v1"]["pct"] for p in p15s])
        eng_pct = np.array([p["roles_v1"]["eng_algorithmic_proof"]["pct"] for p in p15s])
        tcs_pct = np.array([p["roles_v1"]["pure_math_or_tcs"]["pct"] for p in p15s])
        bey_pct = np.array([p["beyond_lean_stage2"]["pct"] for p in p15s])

        def _yerr(blk_list: list[dict[str, Any]]) -> tuple[list[float], list[float]]:
            lo_l, hi_l = [], []
            for b in blk_list:
                pv = b["pct"]
                lo, hi = b["ci_95_pct"]
                lo_l.append(max(0.0, pv - lo))
                hi_l.append(max(0.0, hi - pv))
            return lo_l, hi_l

        v1_lo, v1_hi = _yerr([p["confirmed_v1"] for p in p15s])
        eng_lo, eng_hi = _yerr([p["roles_v1"]["eng_algorithmic_proof"] for p in p15s])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.9, 4.65), gridspec_kw={"width_ratios": [1.06, 1.16]})

        # --- Panel A: 15-Cat Pooled + 4-Way Stratified Curves vs Beyond-Lean Control ---
        ax1.plot(
            x, bey_pct,
            color="#64748B", linestyle="-.", marker="D", markersize=6.0, linewidth=1.8,
            label="Stage-2 Beyond-Lean FV control (all other tools)", zorder=3,
        )
        ax1.errorbar(
            x, v1_pct, yerr=[v1_lo, v1_hi],
            color="#1E3A8A", linestyle="-", marker="o", markersize=7.0, linewidth=2.5,
            capsize=4, capthick=1.2, elinewidth=1.2,
            label="15-Cat Pooled Confirmed Lean (v1, 95% CI)", zorder=5,
        )
        ax1.plot(
            x, tcs_pct,
            color="#D97706", linestyle="--", marker="^", markersize=6.2, linewidth=1.9,
            label="4-Way: pure_math_or_tcs (v1)", zorder=4,
        )
        ax1.errorbar(
            x, eng_pct, yerr=[eng_lo, eng_hi],
            color="#0D9488", linestyle="-", marker="s", markersize=6.4, linewidth=2.2,
            capsize=3.5, capthick=1.1, elinewidth=1.1,
            label="4-Way: strict eng_algorithmic_proof (v1, 95% CI)", zorder=5,
        )

        # Annotations (clean vertical spacing)
        ax1.text(0.0, bey_pct[0] + 0.06, f"{bey_pct[0]:.2f}% (n={p15s[0]['beyond_lean_stage2']['count']})", ha="left", va="bottom", fontsize=7.4, color="#475569")
        ax1.text(1.0, bey_pct[1] + 0.06, f"{bey_pct[1]:.2f}% (n={p15s[1]['beyond_lean_stage2']['count']})", ha="center", va="bottom", fontsize=7.4, color="#475569")
        ax1.text(2.05, bey_pct[2] - 0.03, f"{bey_pct[2]:.2f}% (n={p15s[2]['beyond_lean_stage2']['count']})", ha="left", va="center", fontsize=7.4, color="#475569")

        ax1.text(2.05, v1_pct[2] + 0.03, f"1.28% (n=68)", ha="left", va="center", fontsize=7.9, fontweight="bold", color="#1E3A8A")
        ax1.text(2.05, tcs_pct[2] + 0.03, f"0.66% (n=35)", ha="left", va="center", fontsize=7.6, fontweight="bold", color="#B45309")
        ax1.text(2.05, eng_pct[2] - 0.06, f"0.49% (n=26)", ha="left", va="center", fontsize=7.7, fontweight="bold", color="#0F766E")

        ax1.text(0.0, -0.09, "0.00% (0 v1)\n[0.06% latest]", ha="center", va="top", fontsize=7.2, fontweight="bold", color="#1E3A8A")
        ax1.text(1.0, -0.09, "0.17% (7 v1)\n[eng: 0.07%]", ha="center", va="top", fontsize=7.2, fontweight="bold", color="#0F766E")

        mult_all = c1["multipliers"]["panel_15cat_v1_t2_over_t1"]
        mult_eng = c1["multipliers"]["panel_15cat_eng_alg_v1_t2_over_t1"]
        ax1.annotate(
            f"6-mo v1 surge:\nPooled: {mult_all:.1f}× (0.17%→1.28%)\nStrict eng-alg: {mult_eng:.2f}× (0.07%→0.49%)",
            xy=(1.55, 0.72),
            xytext=(0.64, 0.80),
            ha="center",
            va="center",
            fontsize=7.2,
            fontweight="bold",
            color="#1E3A8A",
            bbox=dict(boxstyle="round,pad=0.32", facecolor="#EFF6FF", edgecolor="#93C5FD", lw=1.0),
            arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.2, connectionstyle="arc3,rad=-0.12"),
        )

        ax1.set_xticks(x)
        ax1.set_xticklabels(x_labels, fontsize=8.0)
        ax1.set_xlim(-0.26, 2.66)
        ax1.set_ylim(-0.30, 1.98)
        ax1.set_ylabel("Share of 15-Category Corpus (%)")
        ax1.set_title("(a) 15-Cat Longitudinal Inflection & 4-Way Stratification", pad=9)
        ax1.grid(axis="y", linestyle=":", alpha=0.6)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.0)

        # --- Panel B: Per-Category Contemporaneous v1 Trajectories across 15 Categories ---
        cat_styles = [
            ("cs.GT",           "#B45309", "P", "-", 2.3, "cs.GT* (9.04%; eng 2.41%)"),
            ("math.DS",         "#9333EA", "X", "-", 2.1, "math.DS* (3.89%; eng 0.56%)"),
            ("math.OC",         "#1D4ED8", "o", "-", 2.4, "math.OC (2.62%; eng 1.80%)"),
            ("cs.DC",           "#0F766E", "s", "-", 1.8, "cs.DC (1.79%; 0 eng)"),
            ("cs.IT",           "#D97706", "^", "-", 1.9, "cs.IT (1.78%; eng 1.18%)"),
            ("cs.CR",           "#DC2626", "D", "-", 1.8, "cs.CR (1.11%)"),
            ("physics.flu-dyn", "#0284C7", "h", "--", 1.7, "flu-dyn* (0.72%)"),
            ("eess.SY",         "#4F46E5", "v", "--", 1.6, "eess.SY (0.41%)"),
        ]
        label_y_override = {
            "cs.GT": 9.04,
            "math.DS": 4.15,
            "math.OC": 2.95,
            "cs.DC": 2.25,
            "cs.IT": 1.62,
            "cs.CR": 1.05,
            "physics.flu-dyn": 0.58,
            "eess.SY": 0.16,
        }

        for cat, col, mk, ls, lw, lbl in cat_styles:
            vals = [p["per_category"][cat]["confirmed_v1"]["pct"] for p in p15s]
            ax2.plot(x, vals, color=col, marker=mk, linestyle=ls, linewidth=lw, markersize=5.6, zorder=4)
            ly = label_y_override[cat]
            ax2.text(2.06, ly, lbl, ha="left", va="center", fontsize=7.1, fontweight="bold" if cat in ("cs.GT", "math.DS", "math.OC") else "normal", color=col)
            if abs(ly - vals[2]) > 0.12:
                ax2.plot([2.01, 2.05], [vals[2], ly], color=col, lw=0.75, alpha=0.7)

        # Persistent zero v1 band (6 categories + eess.SP returning to 0)
        ax2.plot(x, [0.0, 0.0, 0.0], color="#9CA3AF", linestyle="-", linewidth=1.6, zorder=2)
        ax2.text(2.06, -0.34, "6 cats 0.00% v1 (all 3 slices)\n+ eess.SP (0.24%→0%)", ha="left", va="center", fontsize=6.9, color="#6B7280")

        ax2.annotate(
            "cs.GT & math.DS surges are\n78.1% pure_math_or_tcs;\nmath.OC leads eng-alg (1.80%)",
            xy=(1.75, 6.2),
            xytext=(0.72, 6.65),
            ha="center",
            va="center",
            fontsize=7.1,
            color="#374151",
            bbox=dict(boxstyle="round,pad=0.30", facecolor="#FFFBEB", edgecolor="#FCD34D", lw=0.9),
            arrowprops=dict(arrowstyle="->", color="#B45309", lw=1.0, connectionstyle="arc3,rad=-0.10"),
        )

        ax2.set_xticks(x)
        ax2.set_xticklabels(x_labels, fontsize=8.0)
        ax2.set_xlim(-0.18, 3.08)
        ax2.set_ylim(-0.78, 9.75)
        ax2.set_ylabel("Confirmed Lean v1 Adoption (%)")
        ax2.set_title("(b) Disciplinary Divergence Across All 15 Categories (v1)", pad=9)
        ax2.grid(axis="y", linestyle=":", alpha=0.6)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        plt.tight_layout(w_pad=1.6)
        _save(fig, "fig_longitudinal_curve", out_dir=out_dir, save_previews=save_previews)
        return

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
    ax1.plot(x, bey_pct, color="#64748B", linestyle="-.", marker="D", markersize=6.2, linewidth=1.8, label="Stage-2 Beyond-Lean FV control (all other tools)", zorder=3)
    ax1.plot(x, cand_pct, color="#7C3AED", linestyle=":", marker="^", markersize=6.5, linewidth=1.9, label="Stage-2 Lean 4 candidates (full-text)", zorder=4)
    ax1.plot(x, vl_pct, color="#0284C7", linestyle="--", marker="s", markersize=5.8, linewidth=1.6, label="Confirmed Lean (incl. retroactive v2 revisions)", zorder=4)
    ax1.errorbar(x, v1_pct, yerr=[yerr_lo, yerr_hi], color="#1D4ED8", linestyle="-", marker="o", markersize=7.2, linewidth=2.6, capsize=4, capthick=1.3, elinewidth=1.3, label="Confirmed Lean (contemporaneous v1, 95% CI)", zorder=5)
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
    plt.tight_layout(w_pad=1.8)
    _save(fig, "fig_longitudinal_curve", out_dir=out_dir, save_previews=save_previews)


def make_sandbox_builds(
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    phase_c2_path: Path = DEFAULT_PHASE_C2,
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    """Two-panel figure summarizing isolated Docker lake build + #print axioms verification."""
    summary_path = sandbox_dir / "summary.json"
    if not summary_path.is_file():
        print(f"Skipping fig_sandbox_builds (missing {summary_path})")
        return

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for sl in ("2026-11", "2026-05"):
        rp = sandbox_dir / f"results_{sl}.json"
        if rp.is_file():
            for rec in json.loads(rp.read_text(encoding="utf-8")).get("records", []):
                r = dict(rec)
                r["_is_plus7"] = False
                records.append(r)
                seen_ids.add(r["arxiv_id"])

    p7_sb = sandbox_dir / "results_plus7_2026-11.json"
    if p7_sb.is_file():
        for rec in json.loads(p7_sb.read_text(encoding="utf-8")).get("records", []):
            if rec["arxiv_id"] not in seen_ids:
                r = dict(rec)
                r["_is_plus7"] = True
                records.append(r)
                seen_ids.add(r["arxiv_id"])

    if not records:
        return

    tier_short = {"Tier3_Gold": "T3", "Tier2_Silver": "T2", "Tier1_Bronze": "T1"}
    slice_short = {"2026-11": "T2", "2026-05": "T1"}

    def _outcome_cat(r: dict[str, Any]) -> str:
        st = r["build_status"]
        if st == "pass":
            if r.get("nonstandard_axioms_detected") or r.get("sorry_ax_detected") or r.get("of_reduce_bool_detected"):
                return "pass_nonstd"
            return "pass_clean"
        if st == "fail_packaging":
            return "fail_packaging"
        return "fail_local_dep"

    cat_order = {"pass_clean": 0, "pass_nonstd": 1, "fail_packaging": 2, "fail_local_dep": 3}
    cat_style = {
        "pass_clean": ("#059669", None, "OOTB Pass + Standard Axioms Only"),
        "pass_nonstd": ("#D97706", None, "OOTB Pass + Nonstandard Axioms"),
        "fail_packaging": ("#64748B", "///", "OOTB Packaging Fail (Pass in Synth. Env.)"),
        "fail_local_dep": ("#DC2626", None, "OOTB Fail: Missing Local Path Dep"),
    }

    ordered = sorted(
        records,
        key=lambda r: (
            cat_order[_outcome_cat(r)],
            -(r.get("wall_time_sec") or 0.0) if r["build_status"] == "pass" else (r.get("owned_loc") or 0),
            r["arxiv_id"],
        ),
    )
    ordered_plot = list(reversed(ordered))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, max(5.6, 0.34 * len(records) + 0.2)), gridspec_kw={"width_ratios": [1.58, 1.0]})

    # --- Panel (a): Per-repo build wall time (log scale) & axiom outcome ---
    y = np.arange(len(ordered_plot))
    for i, r in enumerate(ordered_plot):
        cat = _outcome_cat(r)
        col, hatch, _ = cat_style[cat]
        if r["build_status"] == "pass":
            val = max(float(r.get("wall_time_sec") or 1.0), 1.0)
            ax1.barh(i, val, height=0.68, color=col, alpha=0.92, edgecolor="white", linewidth=0.6, zorder=3)
            thms = int(r.get("total_theorems_checked") or 0)
            t_str = f"{val:,.0f}s" if val >= 100 else f"{val:.1f}s"
            if cat == "pass_clean":
                ann = f"{t_str}  |  {thms:,} thms (clean)"
                txt_col = "#065F46"
            else:
                nonstd = r.get("nonstandard_axioms_detected", [])
                if r.get("sorry_ax_detected"):
                    ann = f"{t_str}  |  {thms:,} thms (sorryAx!)"
                else:
                    ann = f"{t_str}  |  {thms:,} thms ({len(nonstd)} custom axioms!)"
                txt_col = "#92400E"
            ax1.text(val * 1.14, i, ann, va="center", ha="left", fontsize=7.1, fontweight="bold" if cat == "pass_nonstd" else "normal", color=txt_col)
        elif cat == "fail_packaging":
            syn = r.get("synthetic_env_check") or {}
            syn_t = float(syn.get("wall_time_sec") or 20.0)
            syn_thms = int(syn.get("total_theorems_checked") or 0)
            ax1.barh(
                i, syn_t, height=0.68, color="#E2E8F0", edgecolor="#475569",
                hatch="///", linewidth=0.9, zorder=3,
            )
            ax1.text(
                syn_t * 1.14, i,
                f"No lakefile  (synth: {syn_t:.1f}s, {syn_thms} thms clean)",
                va="center", ha="left", fontsize=6.9, style="italic", color="#334155",
            )
        else:
            raw_t = float(r.get("wall_time_sec") or 0.86)
            val = max(raw_t, 0.65)
            ax1.barh(i, val, height=0.68, color=col, alpha=0.92, edgecolor="white", linewidth=0.6, zorder=3)
            ax1.text(
                val * 1.25, i,
                f"FAIL {raw_t:.2f}s  (missing ../qanary-* sibling deps)",
                va="center", ha="left", fontsize=7.0, fontweight="bold", color="#991B1B",
            )

    y_labels = []
    for r in ordered_plot:
        sl_s = slice_short.get(r["slice_id"], r["slice_id"])
        tr_s = tier_short.get(r.get("static_verification_tier") or "", "?")
        loc = int(r.get("owned_loc") or 0)
        loc_s = f"{loc/1000:.1f}k" if loc >= 10000 else f"{loc:,}"
        p7_tag = ",+7" if r.get("_is_plus7") else ""
        y_labels.append(f"{r['arxiv_id']} ({sl_s},{tr_s},{loc_s}{p7_tag})")

    ax1.set_xscale("log")
    ax1.set_xlim(0.5, 9.5e4)
    ax1.set_yticks(y)
    ax1.set_yticklabels(y_labels, fontsize=7.1, family="monospace")
    ax1.set_xlabel("Isolated Container Wall Time (seconds, log scale; --network=none)")
    ax1.set_title(f"(a) Sandboxed Build & Axiom Audit (All {len(records)} Compact Repos <15k LoC)", pad=9)
    ax1.grid(axis="x", which="major", linestyle=":", alpha=0.6, zorder=1)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    n_fails = sum(1 for r in ordered_plot if r["build_status"] != "pass")
    if 0 < n_fails < len(ordered_plot):
        ax1.axhline(n_fails - 0.5, color="#94A3B8", linestyle="--", linewidth=1.0, zorder=2)

    # --- Panel (b): Static Verification Tier vs Dynamic Kernel Ground-Truth ---
    t3_recs = [r for r in records if r.get("static_verification_tier") == "Tier3_Gold"]
    t2_recs = [r for r in records if r.get("static_verification_tier") == "Tier2_Silver"]
    t1_recs = [r for r in records if r.get("static_verification_tier") == "Tier1_Bronze"]
    groups = [
        (f"Tier 3: Gold\n(n={len(t3_recs)})", t3_recs),
        (f"Tier 2: Silver\n(n={len(t2_recs)})", t2_recs),
        (f"Tier 1: Bronze\n(n={len(t1_recs)})", t1_recs),
        (f"All Compact\n(<15k, n={len(records)})", records),
    ]
    gx = np.arange(len(groups))
    counts = {k: [] for k in ("pass_clean", "pass_nonstd", "fail_packaging", "fail_local_dep")}
    for _, grp in groups:
        c = Counter(_outcome_cat(r) for r in grp)
        for k in counts:
            counts[k].append(c[k])

    bottom = np.zeros(len(groups))
    for k in ("pass_clean", "pass_nonstd", "fail_packaging", "fail_local_dep"):
        vals = np.array(counts[k], dtype=float)
        col, hatch, lbl = cat_style[k]
        if k == "fail_packaging":
            ax2.bar(gx, vals, bottom=bottom, width=0.56, color="#E2E8F0", edgecolor="#475569", hatch="///", linewidth=0.9, label=lbl, zorder=3)
        else:
            ax2.bar(gx, vals, bottom=bottom, width=0.56, color=col, edgecolor="white", linewidth=0.8, label=lbl, zorder=3)
        for xi, v in enumerate(vals):
            if v >= 1:
                tc = "#1E293B" if k == "fail_packaging" else "white"
                ax2.text(xi, bottom[xi] + v / 2.0, f"{int(v)}", ha="center", va="center", fontsize=8.3, fontweight="bold", color=tc, zorder=4)
        bottom += vals

    ax2.set_xticks(gx)
    ax2.set_xticklabels([g[0] for g in groups], fontsize=7.8)
    ax2.set_ylabel("Number of Repositories")
    ymax = max(22.5, len(records) + 5.5)
    ax2.set_ylim(0, ymax)
    ax2.set_yticks(np.arange(0, int(ymax) + 1, 2))
    ax2.set_title("(b) Static Tier vs. Dynamic Kernel Ground Truth", pad=9)
    ax2.grid(axis="y", linestyle=":", alpha=0.6, zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.0)

    if phase_c2_path.is_file() and len(records) > summary["overall"]["total_attempted"]:
        ov = json.loads(phase_c2_path.read_text(encoding="utf-8"))["sandbox_summary"]["all15_t1_t2_compact_all_roles"]
    else:
        ov = summary["overall"]
    callout = (
        f"OOTB Pass: {ov['pass_out_of_box']}/{ov['total_attempted']} ({100.0*ov['pass_out_of_box']/ov['total_attempted']:.1f}%)\n"
        f"Theorems audited: {ov['total_theorems_checked_ootb']:,} OOTB ({ov['total_theorems_checked_incl_synthetic']:,} incl. synth.)\n"
        f"Tier3_Gold: {ov['tier3_gold_pass_out_of_box']}/{ov['tier3_gold_attempted']} OOTB ({ov['tier3_gold_clean_axioms']}/{ov['tier3_gold_pass_out_of_box']} axiom-clean)\n"
        f"Lean.ofReduceBool: 0/{ov['total_attempted']}  |  Proof compile errors: 0/{ov['total_attempted']}"
    )
    ax2.text(
        0.025,
        0.64,
        callout,
        transform=ax2.transAxes,
        ha="left",
        va="center",
        fontsize=6.6,
        color="#1E293B",
        linespacing=1.34,
        bbox=dict(boxstyle="round,pad=0.34", facecolor="#F8FAFC", edgecolor="#94A3B8", lw=0.9),
    )

    plt.tight_layout(w_pad=1.8)
    _save(fig, "fig_sandbox_builds", out_dir=out_dir, save_previews=save_previews)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate vector PDF figures from git-tracked artifacts/ (or optional --from-db)."
    )
    ap.add_argument("--figure-inputs", type=Path, default=DEFAULT_FIGURE_INPUTS)
    ap.add_argument("--longitudinal-summary", type=Path, default=DEFAULT_LONGITUDINAL_SUMMARY)
    ap.add_argument("--sandbox-dir", type=Path, default=DEFAULT_SANDBOX_DIR)
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
    make_sandbox_builds(args.sandbox_dir, out_dir=args.out_dir, save_previews=args.save_previews)
    print("All 6 figures generated successfully.")


if __name__ == "__main__":
    main()
