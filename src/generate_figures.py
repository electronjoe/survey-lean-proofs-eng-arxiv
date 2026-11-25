"""Generate publication-quality vector PDF figures from `artifacts/unified_15cat_panel.json`.

Reads exclusively from the git-tracked canonical JSON artifact (zero SQLite dependency,
enabling clean regeneration in CI or any fresh clone). Uses clean, scholarly English labels
throughout (zero raw JSON enum strings, zero internal expansion badges).
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
DEFAULT_UNIFIED_PANEL = Path("artifacts/unified_15cat_panel.json")

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
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

ROLE_DISPLAY = {
    "eng_algorithmic_proof": "Engineering algorithmic proofs",
    "pure_math_or_tcs": "Pure math & TCS cross-lists",
    "operational_system_fv": "Operational system verification",
    "meta_formalization_system": "Autoformalization pipelines",
}

ROLE_SHORT = {
    "eng_algorithmic_proof": "Eng. Alg.",
    "pure_math_or_tcs": "Math/TCS",
    "operational_system_fv": "System FV",
    "meta_formalization_system": "Meta-Sys.",
}

TIER_SHORT = {
    "Tier3_Gold": "Gold",
    "Tier2_Silver": "Silver",
    "Tier1_Bronze": "Bronze",
}


def _save(fig: plt.Figure, name: str, out_dir: Path = FIG_DIR, save_previews: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight", dpi=300)
    if save_previews:
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(PREVIEW_DIR / f"{name}.png", bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"Saved {out_dir / f'{name}.pdf'}")


def make_pipeline_funnel(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    gt = panel["grand_totals"]
    t2 = next(s for s in panel["slices"] if s["short_id"] == "T2")
    rc = panel["recall_calibration"]
    la = panel["layer_a_audits"]
    sb = panel["sandbox_builds"]["overall"]

    total = gt["total_papers"]
    screened = gt["fulltext_screened"]
    s2_cands = gt["stage2_lean_candidates_total"]
    conf_v1 = gt["confirmed_v1_total"]
    conf_lat = gt["confirmed_v_latest_total"]
    t2_eng = t2["roles_v1"]["eng_algorithmic_proof"]["count"]
    n_la = la["total_audited"]
    n_sb = sb["total_attempted"]

    fig, ax = plt.subplots(figsize=(10.8, 3.45))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 3.45)
    ax.axis("off")

    stages = [
        ("Stage 1\nMetadata Census", f"{total:,}", "15 arXiv categories\n3 matched 19-day slices", "#EEF4FA", "#2B6CB0"),
        ("Stage 2\nFull-Text Screen", f"{screened:,}", f"{gt['fulltext_coverage_pct']:.2f}% HTML/PDF\nZero LLM tokens", "#E6F2FA", "#2B6CB0"),
        ("Stage 3\nStatic Profiling", f"{s2_cands}", f"{gt['stage2_pruned_pct']:.1f}% pruned\n{gt['fulltext_vs_meta_recall_ratio']:.1f}x metadata recall", "#E6F4F1", "#0F766E"),
        ("Stage 4\nRole Classification", f"{conf_v1} / {conf_lat}", f"Initial v1 / incl. rev.\n({t2_eng} T2 Eng. Alg.)", "#FEF3C7", "#B45309"),
        ("Stage 5a\nKernel Builds", f"{n_sb}", "100% of standalone\ncompact (<15k) repos", "#FDE68A", "#B45309"),
        ("Stage 5b\nSemantic Audit", f"{n_la}", "100% Eng. Alg. &\nMeta-System repos", "#EDE9FE", "#6D28D9"),
    ]

    box_w = 1.50
    box_h = 1.60
    gap = 0.28
    x0 = 0.20
    y0 = 1.62

    for i, (title, num, sub, fc, ec) in enumerate(stages):
        x = x0 + i * (box_w + gap)
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
        ax.text(x + box_w / 2, y0 + box_h - 0.22, title, ha="center", va="top", fontsize=7.8, fontweight="bold", color="#1A202C")
        ax.text(x + box_w / 2, y0 + 0.72, num, ha="center", va="center", fontsize=14.2 if len(num) <= 6 else 12.2, fontweight="bold", color=ec)
        ax.text(x + box_w / 2, y0 + 0.14, sub, ha="center", va="bottom", fontsize=6.9, color="#374151")

        if i > 0:
            prev_x = x0 + (i - 1) * (box_w + gap) + box_w + 0.04
            ax.annotate(
                "",
                xy=(x - 0.04, y0 + box_h / 2),
                xytext=(prev_x, y0 + box_h / 2),
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.32", color="#4B5563", lw=1.3),
            )

    # Bottom-left: Recall calibration callout
    s2_cx = x0 + 1 * (box_w + gap) + box_w / 2
    cal_x, cal_y, cal_w, cal_h = 0.20, 0.14, 6.45, 1.04
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
        f"Stage-2 Recall Calibration on {rc['total_t2_stage2_negatives']:,} T2 Negatives (Zero LLM Tokens)",
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="bold",
        color="#14532D",
    )
    ax.text(
        cal_x + 0.16,
        cal_y + 0.12,
        f"{rc['gh_sample_size']} stratified GitHub-linked negatives ({rc['gh_unique_repos_checked']} repositories checked) + {rc['non_gh_sample_size']} non-GitHub negatives:\n"
        f"{rc['confirmed_missed_lean_contributions']} / {rc['gh_sample_size']} confirmed missed Lean contributions  |  95% Clopper-Pearson upper bound <= {rc['confirmed_fn_95pct_upper_bound_pct']:.2f}%\n"
        f"{rc['non_gh_broad_meta_flags']} / {rc['non_gh_sample_size']} broad metadata proof flags among non-GitHub negatives",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color="#1F2937",
        linespacing=1.32,
    )

    # Bottom-right: Static profiling coverage callout
    cost_x, cost_y, cost_w, cost_h = 6.95, 0.14, 3.65, 1.04
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
        "Static Artifact Coverage (T2 Initial v1)",
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="bold",
        color="#1E293B",
    )
    t2_repos = t2["confirmed_v1"]["scanned_owned_repos"]
    t2_owned_m = t2["confirmed_v1"]["total_owned_loc"] / 1e6
    ax.text(
        cost_x + 0.15,
        cost_y + 0.12,
        "GitHub (incl. zipped archives), Zenodo & arXiv anc.\n"
        f"{t2_repos} scanned T2 repositories ({t2_owned_m:.2f}M paper-owned LoC)\n"
        "Strictly static lexer; builds isolated in clean-room Docker",
        ha="left",
        va="bottom",
        fontsize=6.9,
        color="#334155",
        linespacing=1.32,
    )

    _save(fig, "fig_pipeline_funnel", out_dir=out_dir, save_previews=save_previews)


def make_longitudinal_curve(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    slices = panel["slices"]
    x = np.array([0, 1, 2], dtype=float)
    x_labels = [
        f"T0: Nov 1–19, 2025\n(n = {slices[0]['total_papers']:,})",
        f"T1: May 1–19, 2026\n(n = {slices[1]['total_papers']:,})",
        f"T2: Nov 1–19, 2026\n(n = {slices[2]['total_papers']:,})",
    ]

    v1_pct = np.array([s["confirmed_v1"]["pct"] for s in slices])
    eng_pct = np.array([s["roles_v1"]["eng_algorithmic_proof"]["pct"] for s in slices])
    tcs_pct = np.array([s["roles_v1"]["pure_math_or_tcs"]["pct"] for s in slices])
    bey_pct = np.array([s["beyond_lean_stage2"]["pct"] for s in slices])

    def _yerr(blk_list: list[dict[str, Any]]) -> tuple[list[float], list[float]]:
        lo_l, hi_l = [], []
        for b in blk_list:
            pv = b["pct"]
            lo, hi = b["ci_95_pct"]
            lo_l.append(max(0.0, pv - lo))
            hi_l.append(max(0.0, hi - pv))
        return lo_l, hi_l

    v1_lo, v1_hi = _yerr([s["confirmed_v1"] for s in slices])
    eng_lo, eng_hi = _yerr([s["roles_v1"]["eng_algorithmic_proof"] for s in slices])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.1, 4.7), gridspec_kw={"width_ratios": [1.06, 1.18]})

    # --- Panel A ---
    ax1.plot(
        x, bey_pct,
        color="#64748B", linestyle="-.", marker="D", markersize=6.0, linewidth=1.8,
        label="Traditional FV tools (Stage-2 control)", zorder=3,
    )
    ax1.errorbar(
        x, v1_pct, yerr=[v1_lo, v1_hi],
        color="#1E3A8A", linestyle="-", marker="o", markersize=7.0, linewidth=2.5,
        capsize=4, capthick=1.2, elinewidth=1.2,
        label="All confirmed Lean (initial v1, 95% CI)", zorder=5,
    )
    ax1.plot(
        x, tcs_pct,
        color="#D97706", linestyle="--", marker="^", markersize=6.2, linewidth=1.9,
        label="Pure math & TCS cross-lists (initial v1)", zorder=4,
    )
    ax1.errorbar(
        x, eng_pct, yerr=[eng_lo, eng_hi],
        color="#0D9488", linestyle="-", marker="s", markersize=6.4, linewidth=2.2,
        capsize=3.5, capthick=1.1, elinewidth=1.1,
        label="Engineering algorithmic proofs (initial v1, 95% CI)", zorder=5,
    )

    ax1.text(0.0, bey_pct[0] + 0.06, f"{bey_pct[0]:.2f}% (n={slices[0]['beyond_lean_stage2']['count']})", ha="left", va="bottom", fontsize=7.4, color="#475569")
    ax1.text(1.0, bey_pct[1] + 0.06, f"{bey_pct[1]:.2f}% (n={slices[1]['beyond_lean_stage2']['count']})", ha="center", va="bottom", fontsize=7.4, color="#475569")
    ax1.text(2.05, bey_pct[2] - 0.03, f"{bey_pct[2]:.2f}% (n={slices[2]['beyond_lean_stage2']['count']})", ha="left", va="center", fontsize=7.4, color="#475569")

    ax1.text(2.05, v1_pct[2] + 0.03, f"{v1_pct[2]:.2f}% (n={slices[2]['confirmed_v1']['count']})", ha="left", va="center", fontsize=7.9, fontweight="bold", color="#1E3A8A")
    ax1.text(2.05, tcs_pct[2] + 0.03, f"{tcs_pct[2]:.2f}% (n={slices[2]['roles_v1']['pure_math_or_tcs']['count']})", ha="left", va="center", fontsize=7.6, fontweight="bold", color="#B45309")
    ax1.text(2.05, eng_pct[2] - 0.06, f"{eng_pct[2]:.2f}% (n={slices[2]['roles_v1']['eng_algorithmic_proof']['count']})", ha="left", va="center", fontsize=7.7, fontweight="bold", color="#0F766E")

    ax1.text(0.0, -0.09, f"0.00% (0 v1)\n[{slices[0]['confirmed_v_latest']['pct']:.2f}% w/ rev.]", ha="center", va="top", fontsize=7.2, fontweight="bold", color="#1E3A8A")
    ax1.text(1.0, -0.09, f"{v1_pct[1]:.2f}% ({slices[1]['confirmed_v1']['count']} v1)\n[Eng. Alg.: {eng_pct[1]:.2f}%]", ha="center", va="top", fontsize=7.2, fontweight="bold", color="#0F766E")

    mult_all = panel["multipliers"]["pooled_v1_t2_over_t1"]
    mult_eng = panel["multipliers"]["eng_alg_v1_t2_over_t1"]
    ax1.annotate(
        f"6-month surge (initial v1):\nAll roles: {mult_all:.1f}× ({v1_pct[1]:.2f}% → {v1_pct[2]:.2f}%)\nEng. algorithmic: {mult_eng:.2f}× ({eng_pct[1]:.2f}% → {eng_pct[2]:.2f}%)",
        xy=(1.55, 0.72),
        xytext=(0.64, 0.78),
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
    ax1.set_xlim(-0.26, 2.68)
    ax1.set_ylim(-0.30, 1.98)
    ax1.set_ylabel("Share of 15-Category Corpus (%)")
    ax1.set_title("(a) 12-Month Inflection & 4-Way Role Trajectories", pad=9)
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.0)

    # --- Panel B: Per-category trajectories (NO expansion stars!) ---
    t2_pc = slices[2]["per_category"]
    def _cat_lbl(cat: str, short: str) -> str:
        tot_p = t2_pc[cat]["confirmed_v1"]["pct"]
        eng_k = t2_pc[cat]["roles_v1"]["eng_algorithmic_proof"]
        eng_p = 100.0 * eng_k / t2_pc[cat]["total_papers"]
        if cat in ("cs.GT", "math.DS", "math.OC", "cs.IT"):
            return f"{short} ({tot_p:.2f}%; Eng.: {eng_p:.2f}%)"
        if cat == "cs.DC":
            return f"{short} ({tot_p:.2f}%; 0 Eng.)"
        return f"{short} ({tot_p:.2f}%)"

    cat_styles = [
        ("cs.GT",           "#B45309", "P", "-",  2.3, _cat_lbl("cs.GT", "cs.GT")),
        ("math.DS",         "#9333EA", "X", "-",  2.1, _cat_lbl("math.DS", "math.DS")),
        ("math.OC",         "#1D4ED8", "o", "-",  2.4, _cat_lbl("math.OC", "math.OC")),
        ("cs.DC",           "#0F766E", "s", "-",  1.8, _cat_lbl("cs.DC", "cs.DC")),
        ("cs.IT",           "#D97706", "^", "-",  1.9, _cat_lbl("cs.IT", "cs.IT")),
        ("cs.CR",           "#DC2626", "D", "-",  1.8, _cat_lbl("cs.CR", "cs.CR")),
        ("physics.flu-dyn", "#0284C7", "h", "--", 1.7, _cat_lbl("physics.flu-dyn", "flu-dyn")),
        ("eess.SY",         "#4F46E5", "v", "--", 1.6, _cat_lbl("eess.SY", "eess.SY")),
    ]
    label_y_override = {
        "cs.GT": 9.04,
        "math.DS": 4.20,
        "math.OC": 3.00,
        "cs.DC": 2.28,
        "cs.IT": 1.64,
        "cs.CR": 1.06,
        "physics.flu-dyn": 0.58,
        "eess.SY": 0.14,
    }

    for cat, col, mk, ls, lw, lbl in cat_styles:
        vals = [s["per_category"][cat]["confirmed_v1"]["pct"] for s in slices]
        ax2.plot(x, vals, color=col, marker=mk, linestyle=ls, linewidth=lw, markersize=5.6, zorder=4)
        ly = label_y_override[cat]
        ax2.text(2.06, ly, lbl, ha="left", va="center", fontsize=7.1, fontweight="bold" if cat in ("cs.GT", "math.DS", "math.OC") else "normal", color=col)
        if abs(ly - vals[2]) > 0.12:
            ax2.plot([2.01, 2.05], [vals[2], ly], color=col, lw=0.75, alpha=0.7)

    ax2.plot(x, [0.0, 0.0, 0.0], color="#9CA3AF", linestyle="-", linewidth=1.6, zorder=2)
    ax2.text(2.06, -0.36, "6 categories at 0.00% v1 (all 3 slices)\n+ eess.SP (0.24% → 0.00%)", ha="left", va="center", fontsize=6.9, color="#6B7280")

    ax2.annotate(
        "cs.GT & math.DS raw surges are\n78% pure math & TCS cross-lists;\ncs.GT & math.OC lead Eng. Alg.",
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
    ax2.set_xlim(-0.18, 3.16)
    ax2.set_ylim(-0.80, 9.75)
    ax2.set_ylabel("Confirmed Lean Initial v1 Adoption (%)")
    ax2.set_title("(b) Disciplinary Divergence Across All 15 Categories", pad=9)
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout(w_pad=1.6)
    _save(fig, "fig_longitudinal_curve", out_dir=out_dir, save_previews=save_previews)


def make_category_bifurcation(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    t2 = next(s for s in panel["slices"] if s["short_id"] == "T2")
    per_cat = t2["per_category"]
    cat_labels = {
        "cs.GT": "cs.GT (Game Theory / OR)",
        "math.DS": "math.DS (Dynamical Systems)",
        "math.OC": "math.OC (Opt. & Control)",
        "cs.DC": "cs.DC (Distributed Comp.)",
        "cs.IT": "cs.IT (Information Theory)",
        "cs.CR": "cs.CR (Crypto & Security)",
        "physics.flu-dyn": "physics.flu-dyn (Fluid Dyn.)",
        "eess.SY": "eess.SY (Systems & Control)",
        "eess.SP": "eess.SP (Signal Processing)",
        "eess.IV": "eess.IV (Image & Video)",
        "eess.AS": "eess.AS (Audio & Speech)",
        "cs.NI": "cs.NI (Networking)",
        "cs.RO": "cs.RO (Robotics)",
        "cs.PF": "cs.PF (Perf. & Queueing)",
        "cs.CE": "cs.CE (Comp. Engineering)",
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

    r_v1 = t2["roles_v1"]
    fig, ax = plt.subplots(figsize=(8.8, 5.5))
    n_zeros = sum(1 for c in order if per_cat[c]["confirmed_v1"]["count"] == 0)
    ax.axhspan(-0.5, n_zeros - 0.5, color="#F3F4F6", alpha=0.88, zorder=0)
    zero_sum = sum(per_cat[c]["total_papers"] for c in order if per_cat[c]["confirmed_v1"]["count"] == 0)
    non_sy_t2 = t2["eess_archive"]["eess_non_sy_unique_papers"]
    ax.text(
        11.25,
        (n_zeros - 1) / 2.0,
        f"Seven Zero-Adoption T2 Categories\n0 / {zero_sum:,} category-tagged papers (0.00%)\n"
        f"Incl. 0 / {non_sy_t2:,} across eess.SP, IV, and AS",
        ha="right",
        va="center",
        fontsize=7.9,
        fontweight="bold",
        color="#4B5563",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#D1D5DB", lw=1.0),
    )

    h = 0.66
    ax.barh(y, eng_pct, height=h, color="#1D4ED8", label=f"{ROLE_DISPLAY['eng_algorithmic_proof']} (n={r_v1['eng_algorithmic_proof']['count']})", zorder=3)
    ax.barh(y, tcs_pct, left=eng_pct, height=h, color="#D97706", label=f"{ROLE_DISPLAY['pure_math_or_tcs']} (n={r_v1['pure_math_or_tcs']['count']})", zorder=3)
    ax.barh(y, sys_pct, left=eng_pct + tcs_pct, height=h, color="#64748B", label=f"{ROLE_DISPLAY['operational_system_fv']} (n={r_v1['operational_system_fv']['count']})", zorder=3)
    ax.barh(y, meta_pct, left=eng_pct + tcs_pct + sys_pct, height=h, color="#DC2626", label=f"{ROLE_DISPLAY['meta_formalization_system']} (n={r_v1['meta_formalization_system']['count']})", zorder=3)

    for idx, c in enumerate(order):
        k = per_cat[c]["confirmed_v1"]["count"]
        k_eng = per_cat[c]["roles_v1"]["eng_algorithmic_proof"]
        n = per_cat[c]["total_papers"]
        pct = tot_pct[idx]
        if k > 0:
            eng_p = 100.0 * k_eng / n
            lbl = f"{pct:.2f}% ({k}/{n}; Eng. Alg.: {eng_p:.2f}%)"
            color = "#111827"
        else:
            lbl = f"0.00% (0/{n})"
            color = "#6B7280"
        ax.text(pct + 0.14, idx, lbl, va="center", ha="left", fontsize=7.6, fontweight="bold" if k > 0 else "normal", color=color)

    ax.set_yticks(y)
    ax.set_yticklabels([cat_labels[c] for c in order], fontsize=8.0)
    ax.set_xlabel("Confirmed Lean 4 Initial v1 Adoption (% of category submissions, Nov 1–19, 2026)")
    ax.set_title("4-Way Stratified Lean 4 Adoption Across All 15 Engineering arXiv Categories (T2)", pad=10)
    ax.set_xlim(0, 11.6)
    ax.grid(axis="x", linestyle=":", alpha=0.6, zorder=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="center right", bbox_to_anchor=(0.99, 0.56), frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.8)
    _save(fig, "fig_category_bifurcation", out_dir=out_dir, save_previews=save_previews)


def make_paradigms_and_loc(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    t2_v1_papers = [
        p for p in panel["confirmed_papers"] if p["short_id"] == "T2" and p["lean_in_v1"]
    ]
    n_t2 = len(t2_v1_papers)

    par_order = [
        ("P1_paper_first_posthoc", "Post-hoc (P1)\nPaper-First"),
        ("P0_opaque_or_unspecified", "Unspecified (P0)\nOpaque Workflow"),
        ("P4_speclock_solve_distill", "Pinned Spec (P4)\nSpec-Lock + Solve"),
        ("P3_blueprint_sync", "Blueprint Sync (P3)\nCo-Development"),
        ("P2_lean_first", "Lean-First (P2)\nAuto-Informalization"),
    ]
    par_tier = {k: Counter() for k, _ in par_order}
    for p in t2_v1_papers:
        par_tier[p["authoring_paradigm"]][p["verification_tier"]] += 1

    tier_totals = Counter(p["verification_tier"] for p in t2_v1_papers)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.9), gridspec_kw={"width_ratios": [1.02, 1.38]})

    # --- Panel A: Paradigms stacked by Verification Tier (n = 68) ---
    rev_par = list(reversed(par_order))
    yp = np.arange(len(rev_par))
    t3 = np.array([par_tier[k]["Tier3_Gold"] for k, _ in rev_par])
    t2_c = np.array([par_tier[k]["Tier2_Silver"] for k, _ in rev_par])
    t1 = np.array([par_tier[k]["Tier1_Bronze"] for k, _ in rev_par])
    tot = t3 + t2_c + t1

    ax1.barh(yp, t3, height=0.58, color="#059669", label=f"Gold tier (n={tier_totals['Tier3_Gold']})")
    ax1.barh(yp, t2_c, left=t3, height=0.58, color="#3B82F6", label=f"Silver tier (n={tier_totals['Tier2_Silver']})")
    ax1.barh(yp, t1, left=t3 + t2_c, height=0.58, color="#9CA3AF", label=f"Bronze tier (n={tier_totals['Tier1_Bronze']})")

    for i in range(len(rev_par)):
        pct = 100.0 * tot[i] / max(n_t2, 1)
        lbl = f"{tot[i]} ({pct:.1f}%)" if tot[i] > 0 else "0 (0.0%)"
        ax1.text(tot[i] + 0.8, i, lbl, va="center", ha="left", fontsize=8.2, fontweight="bold" if tot[i] > 0 else "normal", color="#111827" if tot[i] > 0 else "#9CA3AF")

    ax1.set_yticks(yp)
    ax1.set_yticklabels([lbl for _, lbl in rev_par], fontsize=8.2)
    ax1.set_xlim(0, 61)
    ax1.set_xlabel(f"Confirmed T2 Initial v1 Papers (n = {n_t2})")
    ax1.set_title("(a) Authoring Paradigms & Static Verification Tiers", pad=8)
    ax1.grid(axis="x", linestyle=":", alpha=0.6)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.8)

    # --- Panel B: Codebase Scale Distribution Across All 51 Scanned T2 Artifacts by 4-Way Role ---
    role_rows = [
        ("operational_system_fv", "Operational System\nVerification", "#64748B"),
        ("eng_algorithmic_proof", "Engineering\nAlgorithmic Proofs", "#1D4ED8"),
        ("pure_math_or_tcs", "Pure Math &\nTCS Cross-Lists", "#D97706"),
        ("meta_formalization_system", "Autoformalization\nPipelines", "#DC2626"),
    ]
    scanned = [p for p in t2_v1_papers if (p.get("primary_owned_loc") or 0) > 0]
    tier_marker = {"Tier3_Gold": "o", "Tier2_Silver": "s", "Tier1_Bronze": "^"}
    rng = np.random.default_rng(42)

    y_pos = np.arange(len(role_rows))
    role_y_labels = []
    for idx, (rk, rlbl, rcol) in enumerate(role_rows):
        sub = sorted([p for p in scanned if p["role_4way"] == rk], key=lambda x: x["primary_owned_loc"])
        locs = [p["primary_owned_loc"] for p in sub]
        role_y_labels.append(f"{rlbl}\n(n={len(sub)} scanned)")
        if not locs:
            continue
        q25, med, q75 = np.percentile(locs, [25, 50, 75])
        # Range bar (min to max) and thick IQR bar
        ax2.plot([min(locs), max(locs)], [idx, idx], color=rcol, alpha=0.35, lw=1.8, zorder=2)
        if len(locs) >= 3:
            ax2.plot([q25, q75], [idx, idx], color=rcol, alpha=0.75, lw=5.5, solid_capstyle="round", zorder=3)
        # Jittered individual repos
        jitter = rng.uniform(-0.18, 0.18, size=len(sub)) if len(sub) > 2 else np.linspace(-0.08, 0.08, len(sub))
        for p, jy in zip(sub, jitter):
            mk = tier_marker.get(p["verification_tier"], "o")
            ax2.scatter(
                p["primary_owned_loc"], idx + jy,
                s=34, color=rcol, marker=mk, alpha=0.88,
                edgecolors="white", linewidths=0.6, zorder=4,
            )
        # Median diamond + clean label
        ax2.scatter([med], [idx], s=78, color="white", edgecolors=rcol, linewidths=2.0, marker="D", zorder=5)
        med_str = f"{med/1000:.1f}k" if med >= 10000 else f"{int(med):,}"
        tot_k = sum(locs)
        tot_str = f"{tot_k/1e6:.2f}M" if tot_k >= 1e6 else f"{tot_k/1000:.0f}k"
        ax2.text(
            med, idx + 0.31, f"med: {med_str}  (sum: {tot_str})",
            ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=rcol,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.82),
        )

    # Highlight notable extremes cleanly (zero overlap with median labels)
    ax2.annotate(
        "2611.06896 (2.97M owned)",
        xy=(2966826, 1.94), xytext=(5.5e6, 1.54),
        fontsize=6.8, color="#92400E", ha="right",
        arrowprops=dict(arrowstyle="->", color="#B45309", lw=0.8),
    )
    ax2.annotate(
        "LongTails (697k)",
        xy=(697377, 3.0), xytext=(1.5e6, 3.0),
        fontsize=6.8, color="#991B1B", ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color="#DC2626", lw=0.8),
    )
    ax2.annotate(
        "Paper2Lean (151k)",
        xy=(151214, 2.94), xytext=(28000, 2.62),
        fontsize=6.8, color="#991B1B", ha="center",
        arrowprops=dict(arrowstyle="->", color="#DC2626", lw=0.8),
    )

    ax2.axvline(20000, color="#DC2626", linestyle="--", linewidth=1.1, alpha=0.75, zorder=1)
    ax2.text(23500, 0.08, "Proof-bloat threshold\n(20k LoC)", fontsize=7.1, color="#B91C1C", va="center", ha="left",
             bbox=dict(boxstyle="round,pad=0.22", facecolor="#FEF2F2", edgecolor="#FECACA", lw=0.8))

    ax2.set_xscale("log")
    ax2.set_xlim(120, 8.5e6)
    ax2.set_ylim(-0.55, 3.68)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(role_y_labels, fontsize=8.0)
    ax2.set_xlabel("Paper-Owned Non-Empty Lean 4 Lines of Code (log scale)")
    ax2.set_title(f"(b) Codebase Scale Across All {len(scanned)} Scanned T2 Repositories by Role", pad=8)
    ax2.grid(axis="x", which="major", linestyle=":", alpha=0.6, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    mk_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#4B5563", markersize=6.5, label="Gold tier"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#4B5563", markersize=6.2, label="Silver tier"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="#4B5563", markersize=6.8, label="Bronze tier"),
        plt.Line2D([0], [0], marker="D", color="w", markerfacecolor="white", markeredgecolor="#4B5563", markeredgewidth=1.6, markersize=6.5, label="Role median"),
    ]
    ax2.legend(handles=mk_handles, loc="lower left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=7.1)

    plt.tight_layout(w_pad=1.8)
    _save(fig, "fig_paradigms_and_loc", out_dir=out_dir, save_previews=save_previews)


def make_sandbox_builds(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    sb = panel["sandbox_builds"]
    records = list(sb["records"])
    ov = sb["overall"]
    if not records:
        return

    def _outcome_cat(r: dict[str, Any]) -> str:
        st = r["build_status"]
        if st == "pass":
            if r.get("nonstandard_axioms_detected") or r.get("sorry_ax_detected") or r.get("of_reduce_bool_detected"):
                return "pass_nonstd"
            return "pass_clean"
        if st == "fail_packaging":
            return "fail_packaging"
        if st == "fail_missing_local_dep":
            return "fail_local_dep"
        return "fail_build"

    cat_order = {"pass_clean": 0, "pass_nonstd": 1, "fail_packaging": 2, "fail_local_dep": 3, "fail_build": 4}
    cat_style = {
        "pass_clean": ("#059669", None, "Pass (standard axioms only)"),
        "pass_nonstd": ("#D97706", None, "Pass (custom axioms or sorry)"),
        "fail_packaging": ("#64748B", "///", "Packaging fail (missing build config)"),
        "fail_local_dep": ("#DC2626", None, "Packaging fail (missing local dep.)"),
        "fail_build": ("#7F1D1D", None, "Build / type-check failure"),
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

    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(12.2, max(6.0, 0.30 * len(records) + 0.5)),
        gridspec_kw={"width_ratios": [1.62, 1.0]},
    )

    y = np.arange(len(ordered_plot))
    for i, r in enumerate(ordered_plot):
        cat = _outcome_cat(r)
        col, _, _ = cat_style[cat]
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
                    ann = f"{t_str}  |  {thms:,} thms (sorry)"
                elif r.get("native_decide_detected"):
                    ann = f"{t_str}  |  {thms:,} thms ({len(nonstd)} native_decide axioms)"
                else:
                    ann = f"{t_str}  |  {thms:,} thms ({len(nonstd)} custom axioms)"
                txt_col = "#92400E"
            ax1.text(val * 1.14, i, ann, va="center", ha="left", fontsize=6.9, fontweight="bold" if cat == "pass_nonstd" else "normal", color=txt_col)
        elif cat == "fail_packaging":
            syn = r.get("synthetic_env_check") or {}
            syn_t = max(float(syn.get("wall_time_sec") or 15.0), 1.0)
            syn_thms = int(syn.get("total_theorems_checked") or 0)
            syn_ok = syn.get("build_status") == "pass"
            ax1.barh(i, syn_t, height=0.68, color="#E2E8F0", edgecolor="#475569", hatch="///", linewidth=0.9, zorder=3)
            if syn_ok:
                syn_lbl = f"No build config (synth.: {syn_t:.1f}s, {syn_thms} thms clean)"
            else:
                syn_lbl = f"No build config (synth. env. failed at {syn_t:.1f}s)"
            ax1.text(syn_t * 1.14, i, syn_lbl, va="center", ha="left", fontsize=6.8, style="italic", color="#334155")
        elif cat == "fail_local_dep":
            raw_t = float(r.get("wall_time_sec") or 0.86)
            val = max(raw_t, 0.7)
            ax1.barh(i, val, height=0.68, color=col, alpha=0.92, edgecolor="white", linewidth=0.6, zorder=3)
            ax1.text(val * 1.25, i, f"Fail {raw_t:.2f}s (missing local sibling deps)", va="center", ha="left", fontsize=6.9, fontweight="bold", color="#991B1B")
        else:
            raw_t = float(r.get("wall_time_sec") or 5.0)
            val = max(raw_t, 1.0)
            ax1.barh(i, val, height=0.68, color=col, alpha=0.92, edgecolor="white", linewidth=0.6, zorder=3)
            ax1.text(val * 1.15, i, f"Build fail ({raw_t:.1f}s)", va="center", ha="left", fontsize=6.9, fontweight="bold", color="#7F1D1D")

    y_labels = []
    for r in ordered_plot:
        sl_s = r["short_id"]
        tr_s = TIER_SHORT.get(r.get("static_verification_tier") or "", "?")
        rl_s = ROLE_SHORT.get(r.get("role_4way") or "", "?")
        loc = int(r.get("owned_loc") or 0)
        loc_s = f"{loc/1000:.1f}k" if loc >= 10000 else f"{loc:,}"
        y_labels.append(f"{r['arxiv_id']} ({sl_s}, {tr_s}, {rl_s}, {loc_s})")

    ax1.set_xscale("log")
    ax1.set_xlim(0.5, 1.4e5)
    ax1.set_yticks(y)
    ax1.set_yticklabels(y_labels, fontsize=6.8, family="monospace")
    ax1.set_xlabel("Offline Container Build Wall Time (seconds, log scale)")
    ax1.set_title(f"(a) Clean-Room Kernel Builds Across All {len(records)} Compact Repos (<15k LoC)", pad=9)
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
        (f"Gold Tier\n(n={len(t3_recs)})", t3_recs),
        (f"Silver Tier\n(n={len(t2_recs)})", t2_recs),
        (f"Bronze Tier\n(n={len(t1_recs)})", t1_recs),
        (f"All Compact\n(n={len(records)})", records),
    ]
    gx = np.arange(len(groups))
    active_cats = [k for k in ("pass_clean", "pass_nonstd", "fail_packaging", "fail_local_dep", "fail_build") if any(_outcome_cat(r) == k for r in records)]
    counts = {k: [] for k in active_cats}
    for _, grp in groups:
        c = Counter(_outcome_cat(r) for r in grp)
        for k in active_cats:
            counts[k].append(c[k])

    bottom = np.zeros(len(groups))
    for k in active_cats:
        vals = np.array(counts[k], dtype=float)
        col, _, lbl = cat_style[k]
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
    ymax = max(29.0, len(records) + 9.0)
    ax2.set_ylim(0, ymax)
    ax2.set_yticks(np.arange(0, int(ymax) + 1, 4))
    ax2.set_title("(b) Static Tier vs. Dynamic Kernel Outcome", pad=9)
    ax2.grid(axis="y", linestyle=":", alpha=0.6, zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#D1D5DB", fontsize=6.9)

    n_nd = len(ov.get("native_decide_repos_ootb", []))
    callout = (
        f"Out-of-the-box pass: {ov['pass_out_of_box']}/{ov['total_attempted']} ({ov['pass_out_of_box_pct']:.1f}%)\n"
        f"Theorems audited: {ov['total_theorems_checked_ootb']:,} OOTB ({ov['total_theorems_checked_incl_synthetic']:,} incl. synth.)\n"
        f"Gold tier OOTB: {ov['tier3_gold_pass_out_of_box']}/{ov['tier3_gold_attempted']} ({ov['tier3_gold_clean_axioms']}/{ov['tier3_gold_pass_out_of_box']} axiom-clean)\n"
        f"Compiler bypass (native_decide): {n_nd}/{ov['total_attempted']}  |  Build errors: {ov['fail_build_or_other']}/{ov['total_attempted']}"
    )
    ax2.text(
        0.025,
        0.67,
        callout,
        transform=ax2.transAxes,
        ha="left",
        va="center",
        fontsize=6.4,
        color="#1E293B",
        linespacing=1.34,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#F8FAFC", edgecolor="#94A3B8", lw=0.9),
    )

    plt.tight_layout(w_pad=1.8)
    _save(fig, "fig_sandbox_builds", out_dir=out_dir, save_previews=save_previews)


def make_phase2_heatmap(
    panel: dict[str, Any],
    out_dir: Path = FIG_DIR,
    save_previews: bool = False,
) -> None:
    audits = [dict(r) for r in panel["layer_a_audits"]["records"] if r["short_id"] == "T2"]
    for a in audits:
        a["par"] = (a.get("authoring_paradigm") or "?").split("_")[0]

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
                sev_score.get(a["mode1_severity"], 0)
                + sev_score.get(a["mode2_severity"], 0)
                + sev_score.get(a["mode3_severity"], 0)
                + sev_score.get(a["mode4_severity"], 0)
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
        "material_undisclosed_drift_or_risk": ("Material Drift", "#FEE2E2", "#991B1B"),
        "partial_or_weakened_formalization": ("Partial", "#FEF3C7", "#92400E"),
        "mostly_faithful_with_disclosed_gaps": ("Mostly Faithful", "#E0F2FE", "#075985"),
        "high_faithful": ("Highly Faithful", "#DCFCE7", "#166534"),
    }

    col_headers = [
        "Overall\nVerdict",
        "Statement\nDrift",
        "Scope\nDowngrade",
        "Custom\nDefinitions",
        "Junk /\nVacuity",
        "Non-Vac.\nWitnesses",
        "Mathlib\nAnchoring",
    ]
    n_rows = len(audits)
    n_cols = len(col_headers)

    fig, ax = plt.subplots(figsize=(10.8, max(6.4, 0.31 * n_rows + 0.1)))
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.invert_yaxis()

    for r_idx, a in enumerate(audits):
        ov_lbl, ov_bg, ov_fg = overall_short[a["overall_fidelity"]]
        cells = [
            (ov_lbl, ov_bg, ov_fg, True),
            (short_sev[a["mode1_severity"]], *sev_colors[a["mode1_severity"]], False),
            (short_sev[a["mode2_severity"]], *sev_colors[a["mode2_severity"]], False),
            (short_sev[a["mode3_severity"]], *sev_colors[a["mode3_severity"]], False),
            (short_sev[a["mode4_severity"]], *sev_colors[a["mode4_severity"]], False),
            (bool_colors[bool(a["has_non_vacuity_witnesses"])][2], bool_colors[bool(a["has_non_vacuity_witnesses"])][0], bool_colors[bool(a["has_non_vacuity_witnesses"])][1], False),
            (mathlib_colors[a["mathlib_anchoring_quality"]][2], mathlib_colors[a["mathlib_anchoring_quality"]][0], mathlib_colors[a["mathlib_anchoring_quality"]][1], False),
        ]
        for c_idx, (txt, bg, fg, is_bold) in enumerate(cells):
            rect = mpatches.Rectangle((c_idx + 0.03, r_idx + 0.06), 0.94, 0.88, facecolor=bg, edgecolor="white", linewidth=1.2)
            ax.add_patch(rect)
            fw = "bold" if (is_bold or txt in ("Moderate", "Severe", "Minor (undiscl.)")) else "normal"
            ax.text(c_idx + 0.5, r_idx + 0.5, txt, ha="center", va="center", fontsize=7.4, color=fg, fontweight=fw)

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
        f"{n_indep} Independent\nAuthor-Owned Repos\n(0 Material Drift;\n0 mod./sev. M3/M4)",
        ha="left",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="#166534",
    )

    row_labels = []
    for a in audits:
        role_s = ROLE_SHORT.get(a.get("role_4way") or "", "")
        if a["arxiv_id"] == "2611.26272":
            tag = "Meta-Sys., Bulk"
        elif role_s and role_s != "Eng. Alg.":
            tag = role_s
        else:
            tag = "Eng. Alg."
        row_labels.append(f"{a['arxiv_id']} ({a['primary_category']}, {a['par']}, {tag})")

    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels(col_headers, fontsize=8.1, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels(row_labels, fontsize=7.3, family="monospace")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        f"Adversarial Layer-A Semantic Fidelity Matrix Across All {n_rows} Audited T2 Repositories",
        pad=26,
        fontsize=10.6,
        fontweight="bold",
    )

    _save(fig, "fig_phase2_heatmap", out_dir=out_dir, save_previews=save_previews)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate vector PDF figures from canonical artifacts/unified_15cat_panel.json."
    )
    ap.add_argument("--unified-panel", type=Path, default=DEFAULT_UNIFIED_PANEL)
    ap.add_argument("--out-dir", type=Path, default=FIG_DIR)
    ap.add_argument("--save-previews", action="store_true", help="Also write PNG previews to data/fig_previews/.")
    args = ap.parse_args()

    if not args.unified_panel.exists():
        raise FileNotFoundError(
            f"Unified panel JSON not found: {args.unified_panel}. "
            "Run `uv run python -m scripts.build_unified_15cat_artifacts` first."
        )
    panel = json.loads(args.unified_panel.read_text(encoding="utf-8"))

    make_pipeline_funnel(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    make_longitudinal_curve(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    make_category_bifurcation(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    make_paradigms_and_loc(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    make_sandbox_builds(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    make_phase2_heatmap(panel, out_dir=args.out_dir, save_previews=args.save_previews)
    print("All 6 figures generated successfully.")


if __name__ == "__main__":
    main()
