#!/usr/bin/env python3
"""Compute Stage-4 Inter-Rater Reliability (Human vs. LLM and Human vs. Human).

Joins `artifacts/human_annotations/stage4_irr.csv` against
`artifacts/slices/*/classifications.json` and computes for each labeled field:
  - Exact agreement (p_o)
  - Cohen's kappa (nominal)
  - Krippendorff's alpha (nominal, exact coincidence-matrix formulation)
  - Confusion matrix
  - Item-level disagreement table for reconciliation

Reports metrics on:
  1. All paired items (for `lean_usage_status`, binary `is_lean_contributed`,
     and all 5 taxonomy fields).
  2. Mutually-agreed `lean_contributed` items (for the 4 conditional taxonomy
     fields: `paper_domain_role`, `authoring_paradigm`, `verification_tier`,
     `ai_agent_assisted`), preventing `(N/A, N/A)` inflation on non-contributed
     candidates.

When 2+ human annotators are present in `stage4_irr.csv`, automatically computes
pairwise Human vs. Human reliability AND multi-rater Krippendorff's alpha.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "artifacts" / "human_annotations" / "stage4_irr.csv"
DEFAULT_SLICES_DIR = REPO_ROOT / "artifacts" / "slices"

FIELDS = (
    "lean_usage_status",
    "paper_domain_role",
    "authoring_paradigm",
    "verification_tier",
    "ai_agent_assisted",
)

CONDITIONAL_FIELDS = (
    "paper_domain_role",
    "authoring_paradigm",
    "verification_tier",
    "ai_agent_assisted",
)

ALLOWED_ENUMS: dict[str, tuple[str, ...]] = {
    "lean_usage_status": (
        "lean_contributed",
        "lean_citation_or_discussion",
        "false_positive",
    ),
    "paper_domain_role": (
        "engineering_math_proof",
        "software_or_system_fv",
        "pure_tcs_or_math",
        "N/A",
    ),
    "authoring_paradigm": (
        "P1_paper_first_posthoc",
        "P2_lean_first",
        "P3_blueprint_sync",
        "P4_speclock_solve_distill",
        "P0_opaque_or_unspecified",
        "N/A",
    ),
    "verification_tier": (
        "Tier3_Gold",
        "Tier2_Silver",
        "Tier1_Bronze",
        "N/A",
    ),
    "ai_agent_assisted": (
        "explicitly_yes",
        "explicitly_no",
        "unclear",
        "N/A",
    ),
    "is_lean_contributed": (
        "yes",
        "no",
    ),
}


@dataclass(frozen=True)
class FieldMetrics:
    field: str
    scope: str
    n: int
    exact_agreement: float
    cohens_kappa: float | None
    krippendorff_alpha: float | None
    labels: list[str]
    confusion: dict[str, dict[str, int]]


@dataclass(frozen=True)
class Disagreement:
    slice_id: str
    arxiv_id: str
    field: str
    rater_a_name: str
    rater_a_label: str
    rater_b_name: str
    rater_b_label: str
    notes: str = ""


def exact_agreement(a: Sequence[str], b: Sequence[str]) -> float:
    """Proportion of exact matches between two equal-length label sequences."""
    if len(a) != len(b):
        raise ValueError(f"Mismatched lengths: {len(a)} vs {len(b)}")
    if not a:
        raise ValueError("Cannot compute agreement on empty sequence")
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def cohens_kappa(a: Sequence[str], b: Sequence[str]) -> float | None:
    """Compute unweighted nominal Cohen's kappa for two raters.

    Returns None when expected agreement p_e == 1.0 (zero variance across both raters).
    """
    if len(a) != len(b):
        raise ValueError(f"Mismatched lengths: {len(a)} vs {len(b)}")
    n = len(a)
    if n == 0:
        raise ValueError("Cannot compute Cohen's kappa on empty sequence")

    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca = Counter(a)
    cb = Counter(b)
    categories = set(ca.keys()) | set(cb.keys())
    pe = sum((ca[c] / n) * (cb[c] / n) for c in categories)
    denom = 1.0 - pe
    if abs(denom) < 1e-12:
        return None
    return (po - pe) / denom


def krippendorff_alpha_nominal(units: Sequence[Sequence[str | None]]) -> float | None:
    """Compute nominal Krippendorff's alpha from unit-by-rater ratings.

    `units` is a sequence of items; each item is a sequence of ratings from R >= 2
    raters (None denotes missing data). Units with fewer than 2 non-missing ratings
    are ignored per Krippendorff (2011).

    Returns None when expected disagreement D_e == 0 (zero variance) or when there
    are no pairable units.
    """
    value_totals: Counter[str] = Counter()
    diag_coinc = 0.0
    total_n = 0

    for unit in units:
        vals = [v for v in unit if v is not None]
        m_u = len(vals)
        if m_u < 2:
            continue
        counts = Counter(vals)
        total_n += m_u
        for val, c in counts.items():
            value_totals[val] += c
            diag_coinc += (c * (c - 1)) / (m_u - 1)

    if total_n < 2:
        return None

    sum_nc_nc1 = sum(c * (c - 1) for c in value_totals.values())
    denom = total_n * (total_n - 1) - sum_nc_nc1
    if denom == 0:
        return None

    # Exact algebraic form: alpha = 1 - D_o / D_e
    # where D_o = 1 - diag_coinc / total_n and D_e = denom / (total_n * (total_n - 1)).
    numer = (total_n - 1) * diag_coinc - sum_nc_nc1
    return numer / denom


def build_confusion_matrix(
    a: Sequence[str],
    b: Sequence[str],
    field: str | None = None,
) -> tuple[list[str], dict[str, dict[str, int]]]:
    """Build deterministic confusion matrix dict[row_label][col_label] = count."""
    if len(a) != len(b):
        raise ValueError(f"Mismatched lengths: {len(a)} vs {len(b)}")
    observed = set(a) | set(b)
    canonical = list(ALLOWED_ENUMS.get(field or "", ()))
    labels = [c for c in canonical if c in observed]
    labels.extend(sorted(observed - set(labels)))

    matrix: dict[str, dict[str, int]] = {r: {c: 0 for c in labels} for r in labels}
    for x, y in zip(a, b):
        matrix[x][y] += 1
    return labels, matrix


def load_llm_classifications(slices_dir: Path = DEFAULT_SLICES_DIR) -> dict[tuple[str, str], dict[str, str]]:
    """Load LLM Stage-4 labels keyed by (slice_id, arxiv_id)."""
    out: dict[tuple[str, str], dict[str, str]] = {}
    for cls_path in sorted(slices_dir.glob("*/classifications.json")):
        slice_id = cls_path.parent.name
        payload = json.loads(cls_path.read_text(encoding="utf-8"))
        for r in payload.get("lean_results", []):
            aid = r["arxiv_id"]
            out[(slice_id, aid)] = {
                "lean_usage_status": r["lean_usage_status"],
                "paper_domain_role": r["paper_domain_role"],
                "authoring_paradigm": r["authoring_paradigm"],
                "verification_tier": r.get("verification_tier_observed") or r.get("verification_tier") or "N/A",
                "ai_agent_assisted": r["ai_agent_assisted"],
            }
    return out


def load_human_annotations(csv_path: Path) -> dict[str, dict[tuple[str, str], dict[str, str]]]:
    """Load human annotations grouped by annotator_id -> (slice_id, arxiv_id) -> row."""
    by_annotator: dict[str, dict[tuple[str, str], dict[str, str]]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, 2):
            slice_id = (row.get("slice_id") or "").strip()
            arxiv_id = (row.get("arxiv_id") or "").strip()
            annotator_id = (row.get("annotator_id") or "").strip()
            if not slice_id or not arxiv_id or not annotator_id:
                continue
            status = (row.get("lean_usage_status") or "").strip()
            if not status:
                # Skip blank template rows gracefully if partially completed.
                continue

            record: dict[str, str] = {"notes": (row.get("notes") or "").strip()}
            for field in FIELDS:
                val = (row.get(field) or "").strip()
                if not val and field != "lean_usage_status" and status != "lean_contributed":
                    val = "N/A"
                if val not in ALLOWED_ENUMS[field]:
                    raise ValueError(
                        f"{csv_path}:{line_no} ({annotator_id} {slice_id}/{arxiv_id}): "
                        f"invalid value {val!r} for {field!r}; expected one of {ALLOWED_ENUMS[field]}"
                    )
                record[field] = val

            key = (slice_id, arxiv_id)
            ann_map = by_annotator.setdefault(annotator_id, {})
            if key in ann_map:
                raise ValueError(f"Duplicate row in {csv_path} for ({annotator_id}, {slice_id}, {arxiv_id})")
            ann_map[key] = record
    return by_annotator


def evaluate_pair(
    rater_a_name: str,
    rater_a: dict[tuple[str, str], dict[str, str]],
    rater_b_name: str,
    rater_b: dict[tuple[str, str], dict[str, str]],
) -> tuple[list[FieldMetrics], list[Disagreement]]:
    """Evaluate all fields (all-items + conditional lean_contributed) for two raters."""
    shared_keys = sorted(set(rater_a.keys()) & set(rater_b.keys()))
    if not shared_keys:
        raise ValueError(f"No overlapping items between {rater_a_name} and {rater_b_name}")

    metrics: list[FieldMetrics] = []
    disagreements: list[Disagreement] = []

    # 1. Binary lean_contributed vs non-contributed on all shared items.
    bin_a = ["yes" if rater_a[k]["lean_usage_status"] == "lean_contributed" else "no" for k in shared_keys]
    bin_b = ["yes" if rater_b[k]["lean_usage_status"] == "lean_contributed" else "no" for k in shared_keys]
    labels, cm = build_confusion_matrix(bin_a, bin_b, field="is_lean_contributed")
    metrics.append(
        FieldMetrics(
            field="is_lean_contributed",
            scope="all",
            n=len(shared_keys),
            exact_agreement=exact_agreement(bin_a, bin_b),
            cohens_kappa=cohens_kappa(bin_a, bin_b),
            krippendorff_alpha=krippendorff_alpha_nominal(list(zip(bin_a, bin_b))),
            labels=labels,
            confusion=cm,
        )
    )

    # 2. All 5 fields over all shared items.
    for field in FIELDS:
        vals_a = [rater_a[k][field] for k in shared_keys]
        vals_b = [rater_b[k][field] for k in shared_keys]
        labels, cm = build_confusion_matrix(vals_a, vals_b, field=field)
        metrics.append(
            FieldMetrics(
                field=field,
                scope="all",
                n=len(shared_keys),
                exact_agreement=exact_agreement(vals_a, vals_b),
                cohens_kappa=cohens_kappa(vals_a, vals_b),
                krippendorff_alpha=krippendorff_alpha_nominal(list(zip(vals_a, vals_b))),
                labels=labels,
                confusion=cm,
            )
        )
        for k, va, vb in zip(shared_keys, vals_a, vals_b):
            if va != vb:
                note_parts = []
                if rater_a[k].get("notes"):
                    note_parts.append(f"{rater_a_name}: {rater_a[k]['notes']}")
                if rater_b[k].get("notes"):
                    note_parts.append(f"{rater_b_name}: {rater_b[k]['notes']}")
                disagreements.append(
                    Disagreement(
                        slice_id=k[0],
                        arxiv_id=k[1],
                        field=field,
                        rater_a_name=rater_a_name,
                        rater_a_label=va,
                        rater_b_name=rater_b_name,
                        rater_b_label=vb,
                        notes=" | ".join(note_parts),
                    )
                )

    # 3. Conditional evaluation on mutually-agreed lean_contributed items.
    agreed_contrib_keys = [
        k
        for k in shared_keys
        if rater_a[k]["lean_usage_status"] == "lean_contributed"
        and rater_b[k]["lean_usage_status"] == "lean_contributed"
    ]
    if agreed_contrib_keys:
        for field in CONDITIONAL_FIELDS:
            vals_a = [rater_a[k][field] for k in agreed_contrib_keys]
            vals_b = [rater_b[k][field] for k in agreed_contrib_keys]
            labels, cm = build_confusion_matrix(vals_a, vals_b, field=field)
            metrics.append(
                FieldMetrics(
                    field=field,
                    scope="agreed_contributed",
                    n=len(agreed_contrib_keys),
                    exact_agreement=exact_agreement(vals_a, vals_b),
                    cohens_kappa=cohens_kappa(vals_a, vals_b),
                    krippendorff_alpha=krippendorff_alpha_nominal(list(zip(vals_a, vals_b))),
                    labels=labels,
                    confusion=cm,
                )
            )

    return metrics, disagreements


def evaluate_multirater_alpha(
    raters: dict[str, dict[tuple[str, str], dict[str, str]]],
) -> dict[str, dict[str, float | int | None]]:
    """Compute nominal Krippendorff's alpha across >=2 raters on all items and agreed_contributed."""
    rater_names = sorted(raters.keys())
    all_keys = sorted(set().union(*(r.keys() for r in raters.values())))
    results: dict[str, dict[str, float | int | None]] = {}

    for field in ("is_lean_contributed",) + FIELDS:
        units: list[list[str | None]] = []
        for k in all_keys:
            row: list[str | None] = []
            for rn in rater_names:
                if k not in raters[rn]:
                    row.append(None)
                elif field == "is_lean_contributed":
                    row.append("yes" if raters[rn][k]["lean_usage_status"] == "lean_contributed" else "no")
                else:
                    row.append(raters[rn][k][field])
            if sum(1 for v in row if v is not None) >= 2:
                units.append(row)
        results[f"{field} (all)"] = {
            "n_units": len(units),
            "krippendorff_alpha": krippendorff_alpha_nominal(units),
        }

    agreed_keys = [
        k
        for k in all_keys
        if all(k in raters[rn] and raters[rn][k]["lean_usage_status"] == "lean_contributed" for rn in rater_names)
    ]
    if agreed_keys:
        for field in CONDITIONAL_FIELDS:
            units = [[raters[rn][k][field] for rn in rater_names] for k in agreed_keys]
            results[f"{field} (agreed_contributed)"] = {
                "n_units": len(units),
                "krippendorff_alpha": krippendorff_alpha_nominal(units),
            }
    return results


def _fmt_score(val: float | None) -> str:
    return f"{val:.4f}" if val is not None else "N/A (0-var)"


def format_report(
    pair_name: str,
    rater_a_name: str,
    rater_b_name: str,
    metrics: list[FieldMetrics],
    disagreements: list[Disagreement],
) -> str:
    lines: list[str] = [f"## {pair_name}", ""]
    lines.append("| Field | Scope | n | Exact Agr. | Cohen's kappa | Krippendorff's alpha |")
    lines.append("| :--- | :--- | ---: | ---: | ---: | ---: |")
    for m in metrics:
        lines.append(
            f"| `{m.field}` | {m.scope} | {m.n} | {m.exact_agreement:.4f} "
            f"| {_fmt_score(m.cohens_kappa)} | {_fmt_score(m.krippendorff_alpha)} |"
        )
    lines.append("")

    lines.append(f"### Confusion Matrices (Rows = `{rater_a_name}`, Cols = `{rater_b_name}`)")
    lines.append("")
    # Show confusion matrices for `lean_usage_status (all)`, `is_lean_contributed (all)`,
    # and conditional fields on `agreed_contributed` (falling back to `all` if none agreed).
    scopes_present = {(m.field, m.scope) for m in metrics}
    for m in metrics:
        if m.field in CONDITIONAL_FIELDS and m.scope == "all" and (m.field, "agreed_contributed") in scopes_present:
            continue
        lines.append(f"#### `{m.field}` ({m.scope}, n={m.n})")
        lines.append("")
        header = "| " + rater_a_name + " \\\\ " + rater_b_name + " | " + " | ".join(f"`{c}`" for c in m.labels) + " |"
        sep = "| :--- | " + " | ".join("---:" for _ in m.labels) + " |"
        lines.append(header)
        lines.append(sep)
        for rlab in m.labels:
            row_vals = " | ".join(str(m.confusion[rlab][clab]) for clab in m.labels)
            lines.append(f"| `{rlab}` | {row_vals} |")
        lines.append("")

    lines.append(f"### Disagreement Table for Reconciliation ({len(disagreements)} disagreements)")
    lines.append("")
    if not disagreements:
        lines.append("*Zero disagreements across all paired fields.*")
    else:
        lines.append(f"| Slice | arXiv ID | Field | `{rater_a_name}` | `{rater_b_name}` | Notes |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for d in disagreements:
            note_escaped = d.notes.replace("|", "\\|")
            lines.append(
                f"| `{d.slice_id}` | `{d.arxiv_id}` | `{d.field}` | "
                f"`{d.rater_a_label}` | `{d.rater_b_label}` | {note_escaped} |"
            )
    lines.append("")
    return "\n".join(lines)


def metrics_to_dict(metrics: list[FieldMetrics], disagreements: list[Disagreement]) -> dict[str, Any]:
    return {
        "metrics": [
            {
                "field": m.field,
                "scope": m.scope,
                "n": m.n,
                "exact_agreement": round(m.exact_agreement, 6),
                "cohens_kappa": round(m.cohens_kappa, 6) if m.cohens_kappa is not None else None,
                "krippendorff_alpha": round(m.krippendorff_alpha, 6) if m.krippendorff_alpha is not None else None,
                "labels": m.labels,
                "confusion": m.confusion,
            }
            for m in metrics
        ],
        "disagreements": [
            {
                "slice_id": d.slice_id,
                "arxiv_id": d.arxiv_id,
                "field": d.field,
                "rater_a": d.rater_a_label,
                "rater_b": d.rater_b_label,
                "notes": d.notes,
            }
            for d in disagreements
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute Stage-4 IRR (Cohen's kappa, Krippendorff's alpha, confusion matrices).")
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Completed human annotations CSV.")
    ap.add_argument("--slices-dir", type=Path, default=DEFAULT_SLICES_DIR, help="Directory with slices/*/classifications.json.")
    ap.add_argument("--json-out", type=Path, default=None, help="Optional path to write structured JSON IRR summary.")
    args = ap.parse_args()

    if not args.csv.is_file():
        print(f"Annotation CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    llm_map = load_llm_classifications(args.slices_dir)
    human_by_id = load_human_annotations(args.csv)
    if not human_by_id:
        print(f"No completed annotation rows found in {args.csv}.", file=sys.stderr)
        sys.exit(1)

    annotators = sorted(human_by_id.keys())
    report_blocks: list[str] = ["# Stage-4 Inter-Rater Reliability Report", ""]
    json_summary: dict[str, Any] = {
        "annotators": annotators,
        "human_vs_llm": {},
        "human_vs_human": {},
        "multirater_alpha": {},
    }

    for ann in annotators:
        missing_llm = sorted(set(human_by_id[ann].keys()) - set(llm_map.keys()))
        if missing_llm:
            print(f"Warning: {ann} has items not in classifications.json: {missing_llm}", file=sys.stderr)
        m, dis = evaluate_pair(ann, human_by_id[ann], "LLM", llm_map)
        report_blocks.append(format_report(f"Human (`{ann}`) vs. LLM", ann, "LLM", m, dis))
        json_summary["human_vs_llm"][ann] = metrics_to_dict(m, dis)

    if len(annotators) >= 2:
        for ann_a, ann_b in itertools.combinations(annotators, 2):
            m, dis = evaluate_pair(ann_a, human_by_id[ann_a], ann_b, human_by_id[ann_b])
            key = f"{ann_a}_vs_{ann_b}"
            report_blocks.append(format_report(f"Human (`{ann_a}`) vs. Human (`{ann_b}`)", ann_a, ann_b, m, dis))
            json_summary["human_vs_human"][key] = metrics_to_dict(m, dis)

        # Multi-rater Krippendorff's alpha (Humans only, and Humans + LLM).
        human_only_alpha = evaluate_multirater_alpha(human_by_id)
        all_raters = dict(human_by_id)
        all_raters["LLM"] = {
            k: llm_map[k]
            for k in set().union(*(r.keys() for r in human_by_id.values()))
            if k in llm_map
        }
        all_raters_alpha = evaluate_multirater_alpha(all_raters)
        json_summary["multirater_alpha"] = {
            "humans_only": human_only_alpha,
            "humans_plus_llm": all_raters_alpha,
        }

        report_blocks.append("## Multi-Rater Krippendorff's Alpha")
        report_blocks.append("")
        report_blocks.append("| Field (Scope) | Humans-only alpha (n) | Humans+LLM alpha (n) |")
        report_blocks.append("| :--- | ---: | ---: |")
        for k in human_only_alpha:
            h_info = human_only_alpha[k]
            a_info = all_raters_alpha.get(k, {"n_units": 0, "krippendorff_alpha": None})
            report_blocks.append(
                f"| `{k}` | {_fmt_score(h_info['krippendorff_alpha'])} ({h_info['n_units']}) "
                f"| {_fmt_score(a_info['krippendorff_alpha'])} ({a_info['n_units']}) |"
            )
        report_blocks.append("")

    print("\n".join(report_blocks))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(json_summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
