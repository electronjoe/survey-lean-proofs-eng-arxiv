#!/usr/bin/env python3
"""Prepare a strictly blinded Stage-4 human IRR review kit (n = 30).

Draws a deterministic, seeded stratified sample of 30 Stage-2 Lean candidates
across slices `2026-11` (`data/survey.db`) and `2026-05` (`data/slice_2026_05.db`):
  - 16 `lean_contributed` papers stratified across all 3 `paper_domain_role`
    values, all observed `authoring_paradigm` values (P1, P4, P0, and T1 P2),
    all 3 `verification_tier` values, and all `ai_agent_assisted` values
    (`explicitly_yes`, `unclear`, `explicitly_no`).
  - 10 `lean_citation_or_discussion` candidates.
  - 4 `false_positive` / contextual-only borderline hits.

Shuffles presentation order deterministically and outputs:
  1. `artifacts/human_annotations/stage4_irr_blank.csv`
     (pre-filled slice_id, arxiv_id, annotator_id; blank label columns).
  2. `data/stage4_irr_dossier.md`
     (gitignored, strictly blinded: title, arXiv URL, categories, abstract,
      Stage-2 matched prose snippets, Stage-3 static counts & README excerpts;
      ZERO LLM labels or Stage-4 classifications).

Runs an automated blinding self-check after writing both outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SLICES: dict[str, tuple[Path, Path]] = {
    "2026-11": (
        REPO_ROOT / "data" / "survey.db",
        REPO_ROOT / "artifacts" / "slices" / "2026-11" / "classifications.json",
    ),
    "2026-05": (
        REPO_ROOT / "data" / "slice_2026_05.db",
        REPO_ROOT / "artifacts" / "slices" / "2026-05" / "classifications.json",
    ),
}

DEFAULT_BLANK_CSV = REPO_ROOT / "artifacts" / "human_annotations" / "stage4_irr_blank.csv"
DEFAULT_DOSSIER_MD = REPO_ROOT / "data" / "stage4_irr_dossier.md"
DEFAULT_HTML_APP = REPO_ROOT / "docs" / "stage4_irr_walkthrough.html"

CSV_COLUMNS = [
    "slice_id",
    "arxiv_id",
    "annotator_id",
    "lean_usage_status",
    "paper_domain_role",
    "authoring_paradigm",
    "verification_tier",
    "ai_agent_assisted",
    "notes",
]

BOILERPLATE_URL_SUBSTRINGS = ("arXiv/html_feedback", "brucemiller/LaTeXML")

# Tokens that must NEVER appear in the blinded dossier or CSV data rows.
FORBIDDEN_BLIND_TOKENS = (
    "lean_contributed",
    "lean_citation_or_discussion",
    "false_positive",
    "engineering_math_proof",
    "software_or_system_fv",
    "pure_tcs_or_math",
    "P1_paper_first_posthoc",
    "P2_lean_first",
    "P3_blueprint_sync",
    "P4_speclock_solve_distill",
    "P0_opaque_or_unspecified",
    "Tier3_Gold",
    "Tier2_Silver",
    "Tier1_Bronze",
    "explicitly_yes",
    "explicitly_no",
    "verification_tier_observed",
    "paradigm_confidence",
    "paradigm_evidence",
    "static_risk_flags",
    "one_line_summary",
    "artifact_availability",
    "ai_tools_mentioned",
)


@dataclass(frozen=True)
class CandidateRecord:
    slice_id: str
    arxiv_id: str
    # Stage-4 labels used ONLY in memory for stratified sampling (never rendered!)
    lean_usage_status: str
    paper_domain_role: str
    authoring_paradigm: str
    verification_tier: str
    ai_agent_assisted: str
    # Stage-1 / Stage-2 / Stage-3 factual metadata rendered into the blinded dossier
    title: str
    abstract: str
    primary_category: str
    matched_target_cats: list[str]
    all_categories: list[str]
    submitted_date: str
    comment: str | None
    journal_ref: str | None
    fetch_source: str
    has_lean_strong: bool
    has_lean_contextual: bool
    lean_hits: dict[str, Any]
    other_hits: dict[str, Any]
    urls: list[str]
    latex_fetched: bool
    latex_signals: dict[str, Any]
    repos: list[dict[str, Any]]

    @property
    def is_contextual_only(self) -> bool:
        return (not self.has_lean_strong) and self.has_lean_contextual


def _clean_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for u in urls:
        if any(b in u for b in BOILERPLATE_URL_SUBSTRINGS):
            continue
        if u not in seen:
            seen.add(u)
            cleaned.append(u)
    return cleaned


def load_candidates(
    slice_configs: dict[str, tuple[Path, Path]] = DEFAULT_SLICES,
) -> list[CandidateRecord]:
    """Load all Stage-2 Lean candidates joined with Stage-3 profiles and Stage-4 strata."""
    records: list[CandidateRecord] = []
    for slice_id in sorted(slice_configs.keys()):
        db_path, cls_path = slice_configs[slice_id]
        if not db_path.is_file():
            raise FileNotFoundError(f"SQLite DB not found for slice {slice_id}: {db_path}")
        if not cls_path.is_file():
            raise FileNotFoundError(f"Classifications JSON not found for slice {slice_id}: {cls_path}")

        cls_payload = json.loads(cls_path.read_text(encoding="utf-8"))
        cls_by_id = {r["arxiv_id"]: r for r in cls_payload["lean_results"]}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT p.arxiv_id, p.title, p.abstract, p.primary_category,
                       p.all_categories_json, p.matched_target_cats_json,
                       p.submitted_date, p.comment, p.journal_ref,
                       s.fetch_source, s.has_lean_strong, s.has_lean_contextual,
                       s.lean_hits_json, s.other_hits_json, s.urls_json,
                       a.latex_fetched, a.latex_signals_json, a.repos_json
                FROM papers p
                JOIN screen_results s ON p.arxiv_id = s.arxiv_id
                LEFT JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
                WHERE s.has_lean_strong = 1 OR s.has_lean_contextual = 1
                ORDER BY p.arxiv_id ASC
                """
            ).fetchall()
        finally:
            conn.close()

        for row in rows:
            aid = row["arxiv_id"]
            if aid not in cls_by_id:
                raise KeyError(f"Stage-2 candidate {slice_id}/{aid} missing from {cls_path}")
            c = cls_by_id[aid]
            records.append(
                CandidateRecord(
                    slice_id=slice_id,
                    arxiv_id=aid,
                    lean_usage_status=c["lean_usage_status"],
                    paper_domain_role=c["paper_domain_role"],
                    authoring_paradigm=c["authoring_paradigm"],
                    verification_tier=c.get("verification_tier_observed") or c.get("verification_tier") or "N/A",
                    ai_agent_assisted=c["ai_agent_assisted"],
                    title=row["title"],
                    abstract=row["abstract"],
                    primary_category=row["primary_category"],
                    matched_target_cats=json.loads(row["matched_target_cats_json"] or "[]"),
                    all_categories=json.loads(row["all_categories_json"] or "[]"),
                    submitted_date=(row["submitted_date"] or "")[:10],
                    comment=row["comment"],
                    journal_ref=row["journal_ref"],
                    fetch_source=row["fetch_source"],
                    has_lean_strong=bool(row["has_lean_strong"]),
                    has_lean_contextual=bool(row["has_lean_contextual"]),
                    lean_hits=json.loads(row["lean_hits_json"] or "{}"),
                    other_hits=json.loads(row["other_hits_json"] or "{}"),
                    urls=_clean_urls(json.loads(row["urls_json"] or "[]")),
                    latex_fetched=bool(row["latex_fetched"]),
                    latex_signals=json.loads(row["latex_signals_json"] or "{}") if row["latex_signals_json"] else {},
                    repos=json.loads(row["repos_json"] or "[]") if row["repos_json"] else [],
                )
            )
    records.sort(key=lambda r: (r.slice_id, r.arxiv_id))
    return records


def _sample_contributed(
    pool: list[CandidateRecord],
    target_n: int,
    rng: random.Random,
) -> list[CandidateRecord]:
    """Deterministic greedy-quota + seeded stratified sampler for `lean_contributed`."""
    if len(pool) < target_n:
        raise ValueError(f"Not enough lean_contributed candidates: {len(pool)} < {target_n}")

    # Marginal minimum quotas ensuring every observed role, paradigm, tier, AI label,
    # and both slices are well represented without hardcoding arxiv_ids.
    quotas: list[tuple[str, str, int]] = [
        ("authoring_paradigm", "P2_lean_first", 1),
        ("ai_agent_assisted", "explicitly_no", 1),
        ("authoring_paradigm", "P4_speclock_solve_distill", 2),
        ("paper_domain_role", "software_or_system_fv", 3),
        ("paper_domain_role", "pure_tcs_or_math", 3),
        ("authoring_paradigm", "P0_opaque_or_unspecified", 3),
        ("verification_tier", "Tier2_Silver", 4),
        ("verification_tier", "Tier1_Bronze", 5),
        ("verification_tier", "Tier3_Gold", 5),
        ("ai_agent_assisted", "unclear", 4),
        ("ai_agent_assisted", "explicitly_yes", 8),
        ("paper_domain_role", "engineering_math_proof", 8),
        ("authoring_paradigm", "P1_paper_first_posthoc", 8),
        ("slice_id", "2026-05", 4),
        ("slice_id", "2026-11", 10),
    ]

    # Cap any quota to what actually exists in the pool.
    effective_quotas: list[tuple[str, str, int]] = []
    for attr, val, need in quotas:
        avail = sum(1 for r in pool if getattr(r, attr) == val)
        if avail > 0:
            effective_quotas.append((attr, val, min(need, avail)))

    selected: list[CandidateRecord] = []
    remaining = list(pool)

    while len(selected) < target_n:
        unsatisfied: list[tuple[str, str, int, list[CandidateRecord]]] = []
        for attr, val, need in effective_quotas:
            have = sum(1 for r in selected if getattr(r, attr) == val)
            deficit = need - have
            if deficit > 0:
                elig = [r for r in remaining if getattr(r, attr) == val]
                if elig:
                    unsatisfied.append((attr, val, deficit, elig))

        if unsatisfied:
            # Prioritize the scarcest unsatisfied quota (smallest eligible pool).
            unsatisfied.sort(key=lambda item: (len(item[3]), -item[2], item[0], item[1]))
            _, _, _, scarce_elig = unsatisfied[0]

            # Among candidates that satisfy the scarcest quota, pick one covering
            # the highest weighted sum of unsatisfied quotas (tie-break via rng).
            def _score(cand: CandidateRecord) -> float:
                s = 0.0
                for attr, val, deficit, elig in unsatisfied:
                    if getattr(cand, attr) == val:
                        s += 1.0 + (1.0 / max(len(elig), 1))
                return s

            scored = [(round(_score(c), 9), c) for c in scarce_elig]
            best_score = max(sc for sc, _ in scored)
            best_cands = [c for sc, c in scored if sc == best_score]
            pick = rng.choice(best_cands)
        else:
            pick = rng.choice(remaining)

        selected.append(pick)
        remaining.remove(pick)

    # Verify full coverage of every observed enum value in the contributed pool.
    for attr in ("paper_domain_role", "authoring_paradigm", "verification_tier", "ai_agent_assisted", "slice_id"):
        observed = {getattr(r, attr) for r in pool}
        covered = {getattr(r, attr) for r in selected}
        missing = observed - covered
        if missing:
            raise AssertionError(f"Stratification missed observed {attr} values: {sorted(missing)}")

    return selected


def _sample_citations(
    pool: list[CandidateRecord],
    target_n: int,
    rng: random.Random,
) -> list[CandidateRecord]:
    """Sample `lean_citation_or_discussion` proportionally across slices, keeping contextual-only hits."""
    if len(pool) < target_n:
        raise ValueError(f"Not enough citation/discussion candidates: {len(pool)} < {target_n}")

    by_slice: dict[str, list[CandidateRecord]] = {}
    for r in pool:
        by_slice.setdefault(r.slice_id, []).append(r)

    total_pool = len(pool)
    slice_ids = sorted(by_slice.keys())
    # Largest-remainder proportional allocation across slices.
    raw_alloc = {s: (len(by_slice[s]) * target_n) / total_pool for s in slice_ids}
    alloc = {s: int(raw_alloc[s]) for s in slice_ids}
    rem = target_n - sum(alloc.values())
    for s in sorted(slice_ids, key=lambda x: (-(raw_alloc[x] - alloc[x]), x))[:rem]:
        alloc[s] += 1

    selected: list[CandidateRecord] = []
    for s in slice_ids:
        sp = list(by_slice[s])
        k = alloc[s]
        ctx = [r for r in sp if r.is_contextual_only]
        chosen_s: list[CandidateRecord] = []
        if ctx and k >= 1:
            # Include at least one contextual-only citation candidate per slice if present.
            c_pick = rng.choice(ctx)
            chosen_s.append(c_pick)
            sp.remove(c_pick)
        if k - len(chosen_s) > 0:
            chosen_s.extend(rng.sample(sp, k - len(chosen_s)))
        selected.extend(chosen_s)
    return selected


def _sample_false_positives(
    all_records: list[CandidateRecord],
    already_selected_keys: set[tuple[str, str]],
    target_n: int,
    rng: random.Random,
) -> list[CandidateRecord]:
    """Select false_positive candidates, topping up from contextual-only borderline hits if needed."""
    fps = [
        r
        for r in all_records
        if r.lean_usage_status == "false_positive"
        and (r.slice_id, r.arxiv_id) not in already_selected_keys
    ]
    if len(fps) >= target_n:
        return rng.sample(fps, target_n)

    selected = list(fps)
    need = target_n - len(selected)
    borderline = [
        r
        for r in all_records
        if r.is_contextual_only
        and r.lean_usage_status != "false_positive"
        and (r.slice_id, r.arxiv_id) not in already_selected_keys
    ]
    if len(borderline) < need:
        raise ValueError(f"Not enough false_positive/contextual borderline hits to reach {target_n}")
    selected.extend(rng.sample(borderline, need))
    return selected


def draw_stratified_sample(
    records: list[CandidateRecord],
    seed: int = 20261123,
    n_contributed: int = 16,
    n_citation: int = 10,
    n_false_positive: int = 4,
) -> list[CandidateRecord]:
    """Draw a deterministic, shuffled stratified sample of 30 Stage-2 Lean candidates."""
    rng = random.Random(seed)
    contributed_pool = [r for r in records if r.lean_usage_status == "lean_contributed"]
    citation_pool = [r for r in records if r.lean_usage_status == "lean_citation_or_discussion"]

    s_contrib = _sample_contributed(contributed_pool, n_contributed, rng)
    s_cite = _sample_citations(citation_pool, n_citation, rng)
    chosen_keys = {(r.slice_id, r.arxiv_id) for r in s_contrib + s_cite}
    s_fp = _sample_false_positives(records, chosen_keys, n_false_positive, rng)

    combined = s_contrib + s_cite + s_fp
    if len({(r.slice_id, r.arxiv_id) for r in combined}) != len(combined):
        raise AssertionError("Duplicate candidate detected in stratified sample")

    # Sort canonically before deterministic shuffle so order reveals zero stratum info.
    combined.sort(key=lambda r: (r.slice_id, r.arxiv_id))
    rng.shuffle(combined)
    return combined


def _sanitize_snippet(text: str, max_chars: int = 420) -> str:
    clean = re.sub(r"\s+", " ", (text or "")).strip()
    if len(clean) > max_chars:
        clean = clean[: max_chars - 3].rstrip() + "..."
    return clean


def _format_repo_block(rp: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    repo_name = rp.get("repo", "unknown")
    host = rp.get("host", "github")
    accessible = rp.get("accessible", False)
    if not accessible:
        lines.append(f"- **`{repo_name}`** (`{host}`): *inaccessible / 404 or private*")
        return lines

    meta_parts = [f"host={host}"]
    if rp.get("stars") is not None:
        meta_parts.append(f"stars={rp['stars']}")
    if rp.get("created_at"):
        meta_parts.append(f"created={str(rp['created_at'])[:10]}")
    if rp.get("pushed_at"):
        meta_parts.append(f"pushed={str(rp['pushed_at'])[:10]}")
    if rp.get("size_kb") is not None:
        meta_parts.append(f"size_kb={rp['size_kb']}")
    lines.append(f"- **`{repo_name}`** ({', '.join(meta_parts)})")

    if rp.get("description"):
        lines.append(f"  - Description: {_sanitize_snippet(str(rp['description']), 260)}")

    counts_parts = [
        f"total_files={rp.get('total_files', 0)}",
        f"lean_files={rp.get('lean_file_count', 0)}",
        f"tex_files={rp.get('tex_file_count', 0)}",
    ]
    if rp.get("lean_toolchain"):
        counts_parts.append(f"toolchain=`{rp['lean_toolchain']}`")
    flags = []
    for k, label in (
        ("has_lakefile", "lakefile"),
        ("has_lean_toolchain", "lean-toolchain"),
        ("has_blueprint_dir", "blueprint_dir"),
        ("has_challenge_file", "Challenge.lean"),
        ("has_solution_file", "Solution.lean"),
    ):
        if rp.get(k):
            flags.append(label)
    if flags:
        counts_parts.append("files_present=[" + ", ".join(flags) + "]")
    lines.append(f"  - Repo structure: {', '.join(counts_parts)}")

    if rp.get("workflow_files"):
        lines.append(f"  - CI workflows: `{', '.join(rp['workflow_files'][:8])}`")
    if rp.get("ci_signals"):
        lines.append(f"  - CI signals: `{', '.join(rp['ci_signals'])}`")
    if rp.get("zenodo_files"):
        lines.append(f"  - Zenodo files: `{', '.join(rp['zenodo_files'][:6])}`")

    sc = rp.get("lean_static_counts") or {}
    if sc:
        ordered_keys = [
            "loc_nonempty",
            "theorem_decl",
            "def_decl",
            "mathlib_import",
            "sorry",
            "custom_axiom",
            "native_decide",
            "print_axioms",
            "unsafe_or_impl_by",
            "metaprog_override",
        ]
        sc_parts = []
        for k in ordered_keys:
            if k in sc:
                sc_parts.append(f"{k}={sc[k]}")
        for k in sorted(sc.keys()):
            if k not in ordered_keys:
                sc_parts.append(f"{k}={sc[k]}")
        lines.append(f"  - Static Lean counts (`lean_files_scanned={rp.get('lean_files_scanned', 0)}`): " + ", ".join(sc_parts))

    readme = (rp.get("readme_preview") or "").strip()
    if readme:
        # Neutralize markdown headings inside README previews so dossier TOC stays clean.
        preview = readme[:1200].rstrip()
        if len(readme) > 1200:
            preview += "\n[...truncated...]"
        preview = preview.replace("```", "'''")
        lines.append("  - **README excerpt:**")
        lines.append("    ```text")
        for rline in preview.splitlines():
            lines.append("    " + rline)
        lines.append("    ```")
    return lines


def render_dossier_markdown(sample: list[CandidateRecord], seed: int) -> str:
    """Render the strictly blinded Markdown review dossier."""
    out: list[str] = [
        "# Stage-4 Blinded Human IRR Review Dossier",
        "",
        f"- **Sample size:** {len(sample)} items (presentation order deterministically shuffled with `seed={seed}`)",
        "- **Blinding protocol:** Strictly blinded — zero LLM predictions, zero Stage-4 classifications, and zero `.lean` source files are shown.",
        "- **Coding rubric & allowed enum values:** See `artifacts/human_annotations/README.md`.",
        "- **Blank annotation sheet:** `artifacts/human_annotations/stage4_irr_blank.csv` (save completed labels to `artifacts/human_annotations/stage4_irr.csv`).",
        "",
        "---",
        "",
    ]

    for idx, rec in enumerate(sample, 1):
        out.append(f"## Item {idx} of {len(sample)} — `{rec.arxiv_id}` (Slice `{rec.slice_id}`)")
        out.append("")
        out.append(f"- **Title:** {_sanitize_snippet(rec.title, 400)}")
        out.append(f"- **arXiv URL:** https://arxiv.org/abs/{rec.arxiv_id}")
        out.append(f"- **Submitted:** `{rec.submitted_date}`")
        out.append(
            f"- **Categories:** primary=`{rec.primary_category}` | "
            f"matched_target=`{', '.join(rec.matched_target_cats)}` | "
            f"all=`{', '.join(rec.all_categories)}`"
        )
        if rec.comment:
            out.append(f"- **arXiv Comment:** {_sanitize_snippet(rec.comment, 350)}")
        if rec.journal_ref:
            out.append(f"- **Journal Ref:** {_sanitize_snippet(rec.journal_ref, 250)}")
        out.append("")

        out.append("### Abstract")
        out.append("")
        out.append(_sanitize_snippet(rec.abstract, 4000))
        out.append("")

        out.append("### Stage-2 Screening Signals & Matched Prose Snippets")
        out.append("")
        other_summary = (
            ", ".join(
                f"{grp}:[{', '.join(sorted(tools.keys()))}]"
                for grp, tools in sorted(rec.other_hits.items())
                if tools
            )
            or "none"
        )
        out.append(
            f"- **Fetch source:** `{rec.fetch_source}` | "
            f"**Strong Lean regex hit:** `{'yes' if rec.has_lean_strong else 'no'}` | "
            f"**Contextual Lean hit:** `{'yes' if rec.has_lean_contextual else 'no'}` | "
            f"**Other formal-tool hits:** {other_summary}"
        )
        if rec.urls:
            shown_urls = rec.urls[:10]
            out.append("- **Extracted URLs:** " + ", ".join(f"`{u}`" for u in shown_urls))
            if len(rec.urls) > 10:
                out.append(f"  *(+{len(rec.urls) - 10} more URLs omitted)*")
        else:
            out.append("- **Extracted URLs:** none")

        strong_dict = rec.lean_hits.get("strong") or {}
        if strong_dict:
            out.append("- **Strong Lean prose matches:**")
            for pat_name, payload in sorted(strong_dict.items()):
                cnt = payload.get("count", 0)
                snips = payload.get("snippets") or []
                out.append(f"  - Pattern `{pat_name}` (`count={cnt}`):")
                for s in snips[:4]:
                    out.append(f"    > \"{_sanitize_snippet(s, 360)}\"")

        ctx_dict = rec.lean_hits.get("contextual") or {}
        if ctx_dict:
            cnt = ctx_dict.get("count", 0)
            snips = ctx_dict.get("snippets") or []
            out.append(f"- **Contextual Lean prose matches (`count={cnt}`):**")
            for s in snips[:4]:
                out.append(f"  > \"{_sanitize_snippet(s, 360)}\"")

        out.append("")
        out.append("### Stage-3 Static Artifact Profile")
        out.append("")
        if rec.latex_signals:
            ls_parts = [f"{k}={json.dumps(v)}" for k, v in sorted(rec.latex_signals.items())]
            out.append(f"- **LaTeX signals** (`latex_fetched={rec.latex_fetched}`): " + ", ".join(ls_parts))
        else:
            out.append(f"- **LaTeX signals:** none (`latex_fetched={rec.latex_fetched}`)")

        if rec.repos:
            # Sort repos so Lean-containing repos appear first, then accessible repos.
            sorted_repos = sorted(
                rec.repos,
                key=lambda rp: (
                    -(rp.get("lean_file_count") or 0),
                    0 if rp.get("accessible") else 1,
                    str(rp.get("repo", "")),
                ),
            )
            lean_repos = [rp for rp in sorted_repos if (rp.get("lean_file_count") or 0) > 0]
            non_lean_repos = [rp for rp in sorted_repos if (rp.get("lean_file_count") or 0) == 0]
            detailed = lean_repos[:5]
            if len(detailed) < 4:
                detailed.extend(non_lean_repos[: 4 - len(detailed)])
            omitted_count = len(sorted_repos) - len(detailed)

            out.append(f"- **Linked repositories ({len(sorted_repos)} profiled):**")
            for rp in detailed:
                out.extend(_format_repo_block(rp))
            if omitted_count > 0:
                rest_names = [str(rp.get("repo", "?")) for rp in sorted_repos[len(detailed) : len(detailed) + 8]]
                suffix = f", ... (+{omitted_count - len(rest_names)} more)" if omitted_count > len(rest_names) else ""
                out.append(f"- *Additional non-Lean repos omitted ({omitted_count}):* `{', '.join(rest_names)}`{suffix}")
        else:
            out.append("- **Linked repositories:** none")

        out.append("")
        out.append("---")
        out.append("")

    return "\n".join(out)


def write_blank_csv(
    sample: list[CandidateRecord],
    out_path: Path,
    annotator_id: str = "annotator_1",
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for rec in sample:
            writer.writerow(
                {
                    "slice_id": rec.slice_id,
                    "arxiv_id": rec.arxiv_id,
                    "annotator_id": annotator_id,
                    "lean_usage_status": "",
                    "paper_domain_role": "",
                    "authoring_paradigm": "",
                    "verification_tier": "",
                    "ai_agent_assisted": "",
                    "notes": "",
                }
            )


def build_blind_items_payload(sample: list[CandidateRecord]) -> list[dict[str, Any]]:
    """Serialize ONLY Stage-1/2/3 factual evidence for each item (ZERO Stage-4 labels)."""
    items: list[dict[str, Any]] = []
    for idx, rec in enumerate(sample, 1):
        sorted_repos = sorted(
            rec.repos,
            key=lambda rp: (
                -(rp.get("lean_file_count") or 0),
                0 if rp.get("accessible") else 1,
                str(rp.get("repo", "")),
            ),
        )
        lean_repos = [rp for rp in sorted_repos if (rp.get("lean_file_count") or 0) > 0]
        non_lean_repos = [rp for rp in sorted_repos if (rp.get("lean_file_count") or 0) == 0]
        detailed_repos = lean_repos[:5]
        if len(detailed_repos) < 4:
            detailed_repos.extend(non_lean_repos[: 4 - len(detailed_repos)])

        compact_repos: list[dict[str, Any]] = []
        for rp in detailed_repos:
            readme = (rp.get("readme_preview") or "").strip()
            if len(readme) > 1500:
                readme = readme[:1500].rstrip() + "\n[...truncated...]"
            compact_repos.append(
                {
                    "repo": rp.get("repo", "unknown"),
                    "host": rp.get("host", "github"),
                    "accessible": bool(rp.get("accessible", False)),
                    "stars": rp.get("stars"),
                    "created_at": str(rp.get("created_at") or "")[:10],
                    "pushed_at": str(rp.get("pushed_at") or "")[:10],
                    "size_kb": rp.get("size_kb"),
                    "description": _sanitize_snippet(str(rp.get("description") or ""), 280)
                    if rp.get("description")
                    else "",
                    "total_files": rp.get("total_files", 0),
                    "lean_file_count": rp.get("lean_file_count", 0),
                    "tex_file_count": rp.get("tex_file_count", 0),
                    "lean_toolchain": rp.get("lean_toolchain") or "",
                    "has_lakefile": bool(rp.get("has_lakefile")),
                    "has_lean_toolchain": bool(rp.get("has_lean_toolchain")),
                    "has_blueprint_dir": bool(rp.get("has_blueprint_dir")),
                    "has_challenge_file": bool(rp.get("has_challenge_file")),
                    "has_solution_file": bool(rp.get("has_solution_file")),
                    "workflow_files": list(rp.get("workflow_files") or [])[:8],
                    "ci_signals": list(rp.get("ci_signals") or []),
                    "zenodo_files": list(rp.get("zenodo_files") or [])[:6],
                    "lean_files_scanned": rp.get("lean_files_scanned", 0),
                    "lean_static_counts": dict(rp.get("lean_static_counts") or {}),
                    "readme_preview": readme,
                }
            )

        omitted_repos = [str(rp.get("repo", "?")) for rp in sorted_repos[len(detailed_repos) :]]

        strong_matches = []
        for pat_name, payload in sorted((rec.lean_hits.get("strong") or {}).items()):
            strong_matches.append(
                {
                    "pattern": pat_name,
                    "count": payload.get("count", 0),
                    "snippets": [_sanitize_snippet(s, 400) for s in (payload.get("snippets") or [])[:4]],
                }
            )
        ctx_dict = rec.lean_hits.get("contextual") or {}
        contextual_matches = {
            "count": ctx_dict.get("count", 0),
            "snippets": [_sanitize_snippet(s, 400) for s in (ctx_dict.get("snippets") or [])[:4]],
        }
        other_tools = [
            {"group": grp, "tools": sorted(tools.keys())}
            for grp, tools in sorted(rec.other_hits.items())
            if tools
        ]

        items.append(
            {
                "idx": idx,
                "slice_id": rec.slice_id,
                "arxiv_id": rec.arxiv_id,
                "arxiv_url": f"https://arxiv.org/abs/{rec.arxiv_id}",
                "title": _sanitize_snippet(rec.title, 400),
                "abstract": _sanitize_snippet(rec.abstract, 4500),
                "primary_category": rec.primary_category,
                "matched_target_cats": list(rec.matched_target_cats),
                "all_categories": list(rec.all_categories),
                "submitted_date": rec.submitted_date,
                "comment": _sanitize_snippet(rec.comment, 380) if rec.comment else "",
                "journal_ref": _sanitize_snippet(rec.journal_ref, 260) if rec.journal_ref else "",
                "fetch_source": rec.fetch_source,
                "has_lean_strong": rec.has_lean_strong,
                "has_lean_contextual": rec.has_lean_contextual,
                "other_tools": other_tools,
                "urls": rec.urls[:10],
                "urls_omitted": max(0, len(rec.urls) - 10),
                "strong_matches": strong_matches,
                "contextual_matches": contextual_matches,
                "latex_fetched": rec.latex_fetched,
                "latex_signals": dict(rec.latex_signals),
                "repos": compact_repos,
                "total_repos_profiled": len(sorted_repos),
                "omitted_repos": omitted_repos[:10],
                "omitted_repos_total": len(omitted_repos),
            }
        )
    return items


def render_blind_html(sample: list[CandidateRecord], seed: int, annotator_id: str = "annotator_1") -> str:
    """Render a self-contained, offline, strictly blinded HTML annotation walkthrough."""
    payload = build_blind_items_payload(sample)
    # Escape </script> safely inside embedded JSON block.
    items_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    safe_annotator = json.dumps(annotator_id)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Stage-4 Blinded Human IRR Walkthrough (n={len(sample)})</title>
  <style>
    :root {{
      --bg: #eef2f7;
      --surface: #ffffff;
      --surface-alt: #f8fafc;
      --border: #d7e0ec;
      --border-strong: #b8c6d8;
      --text: #0f172a;
      --text-muted: #475569;
      --text-faint: #64748b;

      /* Step accent palette */
      --s1: #2563eb; --s1-soft: #eff6ff; --s1-border: #93c5fd;
      --s2: #4f46e5; --s2-soft: #eef2ff; --s2-border: #a5b4fc;
      --s3: #7c3aed; --s3-soft: #f5f3ff; --s3-border: #c4b5fd;
      --s4: #0d9488; --s4-soft: #f0fdfa; --s4-border: #5eead4;
      --s5: #c026d3; --s5-soft: #fdf4ff; --s5-border: #e879f9;

      /* Semantic palette */
      --ok: #059669; --ok-soft: #ecfdf5; --ok-border: #6ee7b7;
      --warn: #d97706; --warn-soft: #fffbeb; --warn-border: #fcd34d;
      --bad: #dc2626; --bad-soft: #fef2f2; --bad-border: #fca5a5;
      --gold: #b45309; --gold-soft: #fef3c7; --gold-border: #fbbf24;

      --radius: 12px;
      --shadow: 0 2px 6px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}

    /* Top sticky bar */
    header {{
      position: sticky;
      top: 0;
      z-index: 60;
      background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
      color: #f8fafc;
      padding: 11px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.18);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .brand h1 {{
      margin: 0;
      font-size: 16px;
      font-weight: 800;
      letter-spacing: -0.01em;
    }}
    .blind-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: rgba(56, 189, 248, 0.18);
      border: 1px solid rgba(56, 189, 248, 0.45);
      color: #bae6fd;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 999px;
      letter-spacing: 0.03em;
    }}
    .top-controls {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }}
    .annotator-box {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #cbd5e1;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 7px;
      padding: 4px 9px;
    }}
    .annotator-box input {{
      border: none;
      background: transparent;
      font-size: 12px;
      font-weight: 700;
      color: #ffffff;
      width: 90px;
      outline: none;
    }}
    .progress-wrap {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 7px;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 700;
      color: #e2e8f0;
    }}
    .progress-bar-track {{
      width: 68px;
      height: 7px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.2);
      overflow: hidden;
    }}
    .progress-bar-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #38bdf8, #34d399);
      transition: width 0.25s ease;
    }}
    .progress-wrap.done {{
      background: rgba(16, 185, 129, 0.25);
      border-color: rgba(52, 211, 153, 0.6);
      color: #a7f3d0;
    }}

    .btn {{
      appearance: none;
      border: 1px solid var(--border-strong);
      background: var(--surface);
      color: var(--text);
      font-size: 12.5px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.12s ease;
    }}
    .btn:hover {{ background: var(--surface-alt); border-color: #94a3b8; }}
    .btn:disabled {{ opacity: 0.45; cursor: not-allowed; }}
    .btn-dark {{
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.24);
      color: #f8fafc;
    }}
    .btn-dark:hover {{ background: rgba(255, 255, 255, 0.18); border-color: rgba(255, 255, 255, 0.4); }}
    .btn-primary {{
      background: var(--s1);
      border-color: var(--s1);
      color: #fff;
    }}
    .btn-primary:hover {{ background: #1d4ed8; border-color: #1d4ed8; }}
    .btn-ok {{
      background: #10b981;
      border-color: #10b981;
      color: #fff;
    }}
    .btn-ok:hover {{ background: #059669; border-color: #059669; }}
    .btn-ghost {{
      border-color: transparent;
      background: transparent;
      color: var(--text-muted);
    }}
    .btn-ghost:hover {{ background: var(--surface-alt); color: var(--text); }}

    /* Paper number navigation bar */
    .nav-strip {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 8px 20px;
      display: flex;
      align-items: center;
      gap: 5px;
      overflow-x: auto;
    }}
    .nav-dot {{
      min-width: 34px;
      height: 29px;
      padding: 0 6px;
      border-radius: 7px;
      border: 1.5px solid var(--border);
      background: var(--surface-alt);
      color: var(--text-muted);
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 2px;
      flex-shrink: 0;
      transition: all 0.12s ease;
    }}
    .nav-dot:hover {{ border-color: var(--s1); color: var(--s1); transform: translateY(-1px); }}
    .nav-dot.done-contrib {{ background: var(--ok-soft); border-color: var(--ok-border); color: var(--ok); }}
    .nav-dot.done-cite {{ background: var(--warn-soft); border-color: var(--warn-border); color: var(--warn); }}
    .nav-dot.done-fp {{ background: var(--bad-soft); border-color: var(--bad-border); color: var(--bad); }}
    .nav-dot.partial {{ background: #fef3c7; border-color: #f59e0b; color: #b45309; }}
    .nav-dot.active {{
      background: var(--s1);
      border-color: var(--s1);
      color: #fff;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
    }}

    /* Collapsible ELI5 Quick Guide drawer */
    .guide-drawer {{
      max-width: 1480px;
      margin: 12px auto 0;
      padding: 0 20px;
      display: none;
    }}
    .guide-drawer.open {{ display: block; }}
    .guide-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 18px;
      box-shadow: var(--shadow);
    }}
    .guide-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }}
    .guide-step {{
      border-radius: 9px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      font-size: 12.2px;
      background: var(--surface-alt);
    }}
    .guide-step h4 {{ margin: 0 0 4px; font-size: 12.8px; }}

    /* Completion celebration banner */
    .complete-banner {{
      max-width: 1480px;
      margin: 12px auto 0;
      padding: 0 20px;
      display: none;
    }}
    .complete-banner.show {{ display: block; }}
    .complete-card {{
      background: linear-gradient(90deg, #ecfdf5, #f0fdfa);
      border: 2px solid #34d399;
      border-radius: var(--radius);
      padding: 14px 18px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      box-shadow: var(--shadow);
    }}

    /* Main 2-column workspace */
    main {{
      max-width: 1480px;
      margin: 14px auto 40px;
      padding: 0 20px;
      display: grid;
      grid-template-columns: minmax(0, 1.28fr) minmax(390px, 0.96fr);
      gap: 18px;
      align-items: start;
    }}
    @media (max-width: 1060px) {{
      main {{ grid-template-columns: 1fr; }}
    }}

    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .panel-head {{
      padding: 13px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--surface-alt);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .panel-body {{ padding: 18px; }}
    .sticky-form {{
      position: sticky;
      top: 64px;
      max-height: calc(100vh - 80px);
      display: flex;
      flex-direction: column;
    }}
    .sticky-form .panel-body {{
      overflow-y: auto;
      flex: 1 1 auto;
    }}
    @media (max-width: 1060px) {{
      .sticky-form {{ position: static; max-height: none; }}
    }}

    /* 4-Tile Quick-Scan Evidence Dashboard */
    .signal-strip {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    @media (max-width: 780px) {{
      .signal-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    .sig-tile {{
      border-radius: 9px;
      padding: 10px 11px;
      border: 1.5px solid var(--border);
      background: var(--surface-alt);
    }}
    .sig-tile .sig-k {{
      font-size: 10.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-faint);
      margin-bottom: 3px;
    }}
    .sig-tile .sig-v {{
      font-size: 13px;
      font-weight: 800;
      color: var(--text);
      line-height: 1.25;
    }}
    .sig-tile .sig-sub {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
      line-height: 1.3;
    }}
    .sig-blue {{ background: var(--s1-soft); border-color: var(--s1-border); }}
    .sig-blue .sig-v {{ color: #1d4ed8; }}
    .sig-ok {{ background: var(--ok-soft); border-color: var(--ok-border); }}
    .sig-ok .sig-v {{ color: #047857; }}
    .sig-gold {{ background: var(--gold-soft); border-color: var(--gold-border); }}
    .sig-gold .sig-v {{ color: #92400e; }}
    .sig-warn {{ background: var(--warn-soft); border-color: var(--warn-border); }}
    .sig-warn .sig-v {{ color: #b45309; }}
    .sig-bad {{ background: var(--bad-soft); border-color: var(--bad-border); }}
    .sig-bad .sig-v {{ color: #b91c1c; }}
    .sig-purple {{ background: var(--s3-soft); border-color: var(--s3-border); }}
    .sig-purple .sig-v {{ color: #6d28d9; }}

    /* Evidence sections with color bars matching steps */
    .ev-section {{
      border: 1px solid var(--border);
      border-left-width: 4px;
      border-radius: 9px;
      padding: 13px 15px;
      margin-bottom: 14px;
      background: var(--surface);
    }}
    .ev-s1 {{ border-left-color: var(--s1); }}
    .ev-s2 {{ border-left-color: var(--s2); }}
    .ev-s3 {{ border-left-color: var(--s4); }}
    .ev-section-head {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      margin-bottom: 9px;
    }}
    .ev-section-title {{
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text);
    }}
    .cue-pill {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
    }}
    .paper-title {{
      margin: 4px 0 8px;
      font-size: 19px;
      font-weight: 800;
      line-height: 1.3;
      color: var(--text);
    }}
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin: 6px 0;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11.5px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--text-muted);
    }}
    .chip-blue {{ background: var(--s1-soft); border-color: var(--s1-border); color: #1d4ed8; }}
    .chip-indigo {{ background: var(--s2-soft); border-color: var(--s2-border); color: #4338ca; }}
    .chip-ok {{ background: var(--ok-soft); border-color: var(--ok-border); color: #047857; }}
    .chip-gold {{ background: var(--gold-soft); border-color: var(--gold-border); color: #92400e; }}
    .chip-warn {{ background: var(--warn-soft); border-color: var(--warn-border); color: #b45309; }}
    .chip-bad {{ background: var(--bad-soft); border-color: var(--bad-border); color: #b91c1c; }}
    .chip-purple {{ background: var(--s3-soft); border-color: var(--s3-border); color: #6d28d9; }}
    .chip-fuchsia {{ background: var(--s5-soft); border-color: var(--s5-border); color: #a21caf; }}

    .abstract-box {{
      font-size: 13.8px;
      color: #1e293b;
      line-height: 1.62;
    }}
    .comment-box {{
      font-size: 12.5px;
      color: #78350f;
      background: var(--warn-soft);
      border: 1px solid var(--warn-border);
      border-radius: 7px;
      padding: 7px 11px;
      margin: 8px 0 10px;
    }}
    .snippet-group {{ margin-bottom: 10px; }}
    .snippet-label {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 4px;
    }}
    blockquote.snippet {{
      margin: 0 0 6px;
      padding: 8px 12px;
      background: #f8fafc;
      border-left: 3px solid #f59e0b;
      border-radius: 0 7px 7px 0;
      font-size: 12.8px;
      color: #1e293b;
      word-break: break-word;
    }}
    mark.lean-hit {{
      background: #fef08a;
      color: #713f12;
      font-weight: 800;
      padding: 0 3px;
      border-radius: 3px;
      box-shadow: inset 0 -1px 0 #eab308;
    }}
    mark.ai-hit {{
      background: #f5d0fe;
      color: #701a75;
      font-weight: 700;
      padding: 0 3px;
      border-radius: 3px;
    }}
    .repo-card {{
      border: 1.5px solid var(--border);
      border-radius: 9px;
      padding: 11px 13px;
      margin-bottom: 10px;
      background: var(--surface-alt);
    }}
    .repo-card.has-lean {{
      border-color: var(--s4-border);
      background: #f7fffe;
    }}
    .repo-head {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      margin-bottom: 4px;
    }}
    .repo-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      font-weight: 800;
      color: var(--text);
    }}
    pre.readme-box {{
      margin: 7px 0 0;
      padding: 10px 12px;
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 7px;
      font-size: 11.5px;
      line-height: 1.48;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 210px;
    }}
    pre.readme-box.expanded {{ max-height: none; }}
    pre.readme-box mark.lean-hit {{ background: #fde047; color: #422006; }}
    pre.readme-box mark.ai-hit {{ background: #e879f9; color: #3b0764; }}
    .url-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-top: 8px;
    }}
    .url-link {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 11px;
      color: var(--s1);
      background: var(--s1-soft);
      border: 1px solid var(--s1-border);
      padding: 2px 7px;
      border-radius: 5px;
      text-decoration: none;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .url-link:hover {{ text-decoration: underline; }}

    /* Right pane stepper & colored question blocks */
    .stepper {{
      display: flex;
      gap: 5px;
      padding: 9px 18px;
      border-bottom: 1px solid var(--border);
      background: #ffffff;
      flex-wrap: wrap;
    }}
    .step-pill {{
      flex: 1 1 auto;
      text-align: center;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 6px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--text-faint);
    }}
    .step-pill.done {{ background: var(--ok-soft); border-color: var(--ok-border); color: var(--ok); }}
    .step-pill.na {{ background: #f1f5f9; border-color: #cbd5e1; color: #64748b; }}
    .step-pill.todo {{ background: var(--warn-soft); border-color: var(--warn-border); color: var(--warn); }}

    .short-circuit-banner {{
      background: var(--ok-soft);
      border: 1.5px solid var(--ok-border);
      border-radius: 9px;
      padding: 11px 13px;
      margin: 10px 0 14px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 12.5px;
      color: #065f46;
    }}

    .q-block {{
      border: 1.5px solid var(--border);
      border-top-width: 4px;
      border-radius: 10px;
      padding: 12px 13px;
      margin-bottom: 13px;
      background: var(--surface);
      transition: opacity 0.15s ease;
    }}
    .q-block.q-s1 {{ border-top-color: var(--s1); }}
    .q-block.q-s2 {{ border-top-color: var(--s2); }}
    .q-block.q-s3 {{ border-top-color: var(--s3); }}
    .q-block.q-s4 {{ border-top-color: var(--s4); }}
    .q-block.q-s5 {{ border-top-color: var(--s5); }}
    .q-block.disabled {{
      opacity: 0.38;
      pointer-events: none;
      background: #f8fafc;
    }}
    .q-header {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      margin-bottom: 9px;
    }}
    .q-title {{
      font-size: 13.5px;
      font-weight: 800;
      color: var(--text);
    }}
    .q-step-tag {{
      display: inline-block;
      color: #fff;
      font-size: 10.5px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 5px;
      margin-right: 6px;
      vertical-align: 1px;
    }}
    .q-look-hint {{
      font-size: 10.8px;
      font-weight: 700;
      color: var(--text-muted);
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 1px 8px;
    }}
    .opt-grid {{
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}
    .opt-card {{
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 9px 11px;
      cursor: pointer;
      background: var(--surface);
      text-align: left;
      transition: all 0.12s ease;
      display: flex;
      flex-direction: column;
      gap: 3px;
      width: 100%;
    }}
    .opt-card:hover {{ border-color: #94a3b8; background: #fafcff; transform: translateY(-1px); }}
    .opt-card.selected {{
      border-color: var(--s1);
      background: var(--s1-soft);
      box-shadow: 0 0 0 2.5px rgba(37, 99, 235, 0.18);
    }}
    .opt-card.tone-bad.selected {{
      border-color: var(--bad);
      background: var(--bad-soft);
      box-shadow: 0 0 0 2.5px rgba(220, 38, 38, 0.16);
    }}
    .opt-card.tone-warn.selected {{
      border-color: var(--warn);
      background: var(--warn-soft);
      box-shadow: 0 0 0 2.5px rgba(217, 119, 6, 0.16);
    }}
    .opt-card.tone-ok.selected {{
      border-color: var(--ok);
      background: var(--ok-soft);
      box-shadow: 0 0 0 2.5px rgba(5, 150, 105, 0.18);
    }}
    .opt-card.tone-gold.selected {{
      border-color: var(--gold);
      background: var(--gold-soft);
      box-shadow: 0 0 0 2.5px rgba(217, 119, 6, 0.18);
    }}
    .opt-card.tone-purple.selected {{
      border-color: var(--s3);
      background: var(--s3-soft);
      box-shadow: 0 0 0 2.5px rgba(124, 58, 237, 0.18);
    }}
    .opt-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .opt-name {{
      font-size: 13px;
      font-weight: 800;
      color: var(--text);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .opt-badge {{
      font-size: 10px;
      font-weight: 800;
      padding: 1px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .opt-enum {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 10.5px;
      color: var(--text-faint);
    }}
    .opt-desc {{
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.38;
    }}
    textarea.notes-input {{
      width: 100%;
      min-height: 58px;
      border: 1.5px solid var(--border-strong);
      border-radius: 8px;
      padding: 8px 10px;
      font-family: inherit;
      font-size: 12.5px;
      color: var(--text);
      resize: vertical;
    }}
    textarea.notes-input:focus {{
      outline: none;
      border-color: var(--s1);
      box-shadow: 0 0 0 2.5px rgba(37, 99, 235, 0.15);
    }}
    .form-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 16px;
      border-top: 1px solid var(--border);
      background: var(--surface-alt);
      flex-shrink: 0;
    }}
    .toast {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #0f172a;
      color: #f8fafc;
      padding: 10px 15px;
      border-radius: 9px;
      font-size: 12.5px;
      font-weight: 700;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.3);
      opacity: 0;
      pointer-events: none;
      transform: translateY(8px);
      transition: all 0.2s ease;
      z-index: 100;
    }}
    .toast.show {{ opacity: 1; transform: translateY(0); }}
    .empty-muted {{
      font-size: 12.5px;
      color: var(--text-faint);
      font-style: italic;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>Stage-4 Human IRR Walkthrough</h1>
      <span class="blind-badge">STRICTLY BLINDED &middot; n={len(sample)} &middot; seed={seed}</span>
    </div>
    <div class="top-controls">
      <button class="btn btn-dark" id="btn-guide" title="Toggle ELI5 coding cheat-sheet">ELI5 Guide</button>
      <label class="annotator-box" title="Pseudonymous ID saved into the CSV (e.g., annotator_1 or annotator_2)">
        Annotator:
        <input id="annotator-input" type="text" value="" />
      </label>
      <div id="progress-wrap" class="progress-wrap">
        <div class="progress-bar-track"><div id="progress-fill" class="progress-bar-fill"></div></div>
        <span id="progress-text">0 / {len(sample)}</span>
      </div>
      <button class="btn btn-dark" id="btn-import" title="Resume from a previously downloaded stage4_irr.csv">Import CSV</button>
      <input id="file-import" type="file" accept=".csv,text/csv" style="display:none" />
      <button class="btn btn-dark" id="btn-copy" title="Copy CSV text to clipboard">Copy CSV</button>
      <button class="btn btn-ok" id="btn-download" title="Download stage4_irr.csv">Download stage4_irr.csv</button>
      <button class="btn btn-dark" id="btn-reset" title="Clear locally saved answers">Reset</button>
    </div>
  </header>

  <nav id="nav-strip" class="nav-strip" aria-label="Paper navigation"></nav>

  <section id="guide-drawer" class="guide-drawer">
    <div class="guide-card">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">
        <div style="font-size:14px;font-weight:800;">5-Step Blinded Coding Cheat-Sheet (Zero Lean Code Needed!)</div>
        <button class="btn btn-ghost" id="btn-close-guide">Hide Guide &times;</button>
      </div>
      <div class="guide-grid">
        <div class="guide-step" style="border-top:3px solid var(--s1);">
          <h4 style="color:var(--s1);">1. Usage Status</h4>
          <strong>False Positive:</strong> coincidental "lean" word.<br/>
          <strong>Citation Only:</strong> discusses Lean or future work, no proofs here.<br/>
          <strong>Contributed:</strong> proves THIS paper's results in Lean &rarr; do Steps 2&ndash;5!
        </div>
        <div class="guide-step" style="border-top:3px solid var(--s2);">
          <h4 style="color:var(--s2);">2. Domain Role</h4>
          <strong>Eng Math:</strong> optimization, control, comms/coding, networks, ML/stats, crypto math.<br/>
          <strong>System/SW FV:</strong> VM, protocol, DB, policy engine, hardware.<br/>
          <strong>Pure TCS/Math:</strong> complexity, graph algos, pure math.
        </div>
        <div class="guide-step" style="border-top:3px solid var(--s3);">
          <h4 style="color:var(--s3);">3. Authoring Paradigm</h4>
          <strong>P1:</strong> paper first, Lean companion after.<br/>
          <strong>P2:</strong> Lean written first, paper from Lean.<br/>
          <strong>P3:</strong> blueprint sync (<code>blueprint_dir</code>).<br/>
          <strong>P4:</strong> spec-lock (<code>comparator</code> / Challenge.lean).<br/>
          <strong>P0:</strong> claims Lean, no public Lean files.
        </div>
        <div class="guide-step" style="border-top:3px solid var(--s4);">
          <h4 style="color:var(--s4);">4. Verification Tier</h4>
          <strong>Gold:</strong> public Lean repo + 0 sorry/axiom/native_decide + audit rigor (<code>#print axioms</code>, <code>comparator</code>, blueprint, CI).<br/>
          <strong>Silver:</strong> public clean/near-clean repo, basic <code>lake build</code> or partial.<br/>
          <strong>Bronze:</strong> no public repo OR has sorry/axiom/native_decide.
        </div>
        <div class="guide-step" style="border-top:3px solid var(--s5);">
          <h4 style="color:var(--s5);">5. AI Assistance</h4>
          <strong>Explicitly Yes:</strong> paper/README/LaTeX credits LLMs (Claude, Codex, GPT, Gemini, DeepSeek, Aristotle).<br/>
          <strong>Explicitly No:</strong> explicitly states human-only.<br/>
          <strong>Unclear:</strong> no clear statement either way.
        </div>
      </div>
    </div>
  </section>

  <section id="complete-banner" class="complete-banner">
    <div class="complete-card">
      <div>
        <div style="font-size:15px;font-weight:800;color:#065f46;">All {len(sample)} / {len(sample)} papers labeled!</div>
        <div style="font-size:12.5px;color:#047857;">
          Click <strong>Download stage4_irr.csv</strong>, save it to <code>artifacts/human_annotations/stage4_irr.csv</code>,
          then run <code>uv run python scripts/compute_irr.py</code> to compute Cohen's &kappa; &amp; Krippendorff's &alpha;.
        </div>
      </div>
      <button class="btn btn-ok" id="btn-download-banner">Download stage4_irr.csv</button>
    </div>
  </section>

  <main>
    <section class="panel" id="evidence-panel">
      <div class="panel-head">
        <div id="paper-counter" style="font-weight:800;font-size:14px;"></div>
        <div id="paper-links"></div>
      </div>
      <div class="panel-body" id="evidence-body"></div>
    </section>

    <aside class="panel sticky-form">
      <div class="panel-head">
        <div style="font-weight:800;font-size:14px;">Your Blinded Classification</div>
        <span id="item-status-badge" class="chip">Unlabeled</span>
      </div>
      <div id="stepper" class="stepper"></div>
      <div class="panel-body" id="form-body"></div>
      <div class="form-footer">
        <button class="btn" id="btn-prev" title="Alt + Left">&larr; Prev</button>
        <button class="btn btn-primary" id="btn-next-unlabeled" title="Jump to next incomplete item">Next Unlabeled</button>
        <button class="btn btn-primary" id="btn-next" title="Alt + Right">Next &rarr;</button>
      </div>
    </aside>
  </main>

  <div id="toast" class="toast"></div>

  <script id="blind-items-data" type="application/json">{items_json}</script>
  <script>
    (function () {{
      "use strict";
      const SEED = {seed};
      const DEFAULT_ANNOTATOR = {safe_annotator};
      const ITEMS = JSON.parse(document.getElementById("blind-items-data").textContent);
      const STORAGE_KEY = "stage4_irr_state_v1_seed_" + SEED;
      const CSV_COLS = [
        "slice_id",
        "arxiv_id",
        "annotator_id",
        "lean_usage_status",
        "paper_domain_role",
        "authoring_paradigm",
        "verification_tier",
        "ai_agent_assisted",
        "notes"
      ];

      const QUESTIONS = [
        {{
          key: "lean_usage_status",
          step: "Step 1",
          shortName: "1. Usage",
          stepClass: "q-s1",
          color: "var(--s1)",
          lookHint: "Look: Abstract + Yellow Snippets",
          title: "Did this paper prove or verify its own results in Lean?",
          conditional: false,
          options: [
            {{
              value: "false_positive",
              badge: "STOP -> N/A",
              badgeBg: "#fee2e2", badgeColor: "#991b1b",
              tone: "tone-bad",
              label: "False Positive (Not the Lean theorem prover)",
              desc: "The word 'lean' is coincidental (e.g., lean kernel/method, lean manufacturing, or an unrelated project/person name)."
            }},
            {{
              value: "lean_citation_or_discussion",
              badge: "STOP -> N/A",
              badgeBg: "#fef3c7", badgeColor: "#92400e",
              tone: "tone-warn",
              label: "Citation / Discussion / Future Work Only",
              desc: "Mentions Lean/Mathlib in related work, future work, or evaluates LLM provers on benchmarks without formalizing THIS paper's own results."
            }},
            {{
              value: "lean_contributed",
              badge: "UNLOCKS 2-5",
              badgeBg: "#d1fae5", badgeColor: "#065f46",
              tone: "tone-ok",
              label: "Contributed Lean Proofs / Verification",
              desc: "Authors actually used Lean to formalize or verify theorems, algorithms, or systems in THIS paper."
            }}
          ]
        }},
        {{
          key: "paper_domain_role",
          step: "Step 2",
          shortName: "2. Role",
          stepClass: "q-s2",
          color: "var(--s2)",
          lookHint: "Look: Categories + Abstract",
          title: "What kind of paper is this?",
          conditional: true,
          options: [
            {{
              value: "engineering_math_proof",
              badge: "ENG MATH",
              badgeBg: "#e0e7ff", badgeColor: "#3730a3",
              tone: "",
              label: "Engineering / Applied Math Proof",
              desc: "Mathematical theorems in engineering or applied theory (optimization, control, sysID, comms/coding/info theory, signal processing, networks, ML/stats theory, crypto math)."
            }},
            {{
              value: "software_or_system_fv",
              badge: "SYS / SW FV",
              badgeBg: "#e0f2fe", badgeColor: "#075985",
              tone: "",
              label: "Software / System / Protocol Verification",
              desc: "Verifies an actual implementation, VM, database/pipeline, policy engine, distributed protocol, or chip/hardware design."
            }},
            {{
              value: "pure_tcs_or_math",
              badge: "PURE TCS/MATH",
              badgeBg: "#f3e8ff", badgeColor: "#6b21a8",
              tone: "tone-purple",
              label: "Pure TCS or Pure Math (cross-listed)",
              desc: "Pure theoretical CS (complexity, graph/CONGEST algorithms, TSP approximation) or pure math cross-listed into engineering."
            }}
          ]
        }},
        {{
          key: "authoring_paradigm",
          step: "Step 3",
          shortName: "3. Paradigm",
          stepClass: "q-s3",
          color: "var(--s3)",
          lookHint: "Look: Snippets + Repo Structure + README",
          title: "How were the paper and Lean proof written together?",
          conditional: true,
          options: [
            {{
              value: "P1_paper_first_posthoc",
              badge: "P1 COMMON",
              badgeBg: "#ede9fe", badgeColor: "#5b21b6",
              tone: "tone-purple",
              label: "Paper-First / Post-hoc Companion",
              desc: "Paper/math developed informally first; Lean formalization built afterward or loosely attached without blueprint sync or spec-lock tooling."
            }},
            {{
              value: "P2_lean_first",
              badge: "P2",
              badgeBg: "#ede9fe", badgeColor: "#5b21b6",
              tone: "tone-purple",
              label: "Lean-First",
              desc: "Lean proof developed first, and the human manuscript/exposition was written or auto-informalized directly from the Lean code."
            }},
            {{
              value: "P3_blueprint_sync",
              badge: "P3 BLUEPRINT",
              badgeBg: "#ede9fe", badgeColor: "#5b21b6",
              tone: "tone-purple",
              label: "Blueprint Sync",
              desc: "Synchronized co-development using leanblueprint / LeanArchitect (@[blueprint], \\\\inputleannode) or Verso Blueprints keeping LaTeX & Lean synced."
            }},
            {{
              value: "P4_speclock_solve_distill",
              badge: "P4 SPEC-LOCK",
              badgeBg: "#ede9fe", badgeColor: "#5b21b6",
              tone: "tone-purple",
              label: "Spec-Lock -> Solve -> Distill",
              desc: "Frozen Challenge.lean / Solution.lean or comparator spec-lock, unconstrained (often AI) proof search, then conceptual distillation into a paper."
            }},
            {{
              value: "P0_opaque_or_unspecified",
              badge: "P0 NO REPO",
              badgeBg: "#f1f5f9", badgeColor: "#334155",
              tone: "",
              label: "Opaque / Unspecified",
              desc: "Paper clearly claims Lean verification of its own results, but provides NO public Lean code (0 .lean files / broken link) and insufficient workflow detail."
            }}
          ]
        }},
        {{
          key: "verification_tier",
          step: "Step 4",
          shortName: "4. Tier",
          stepClass: "q-s4",
          color: "var(--s4)",
          lookHint: "Look: Top Signal Tile 2 & 3 + Static Counts",
          title: "How rigorous is the Lean artifact (from static evidence)?",
          conditional: true,
          options: [
            {{
              value: "Tier3_Gold",
              badge: "GOLD",
              badgeBg: "#fef3c7", badgeColor: "#92400e",
              tone: "tone-gold",
              label: "Tier 3 — Gold (Clean + Audited)",
              desc: "Public Lean repo for main theorem(s), ZERO sorry / custom_axiom / native_decide, AND audit rigor (#print axioms, comparator, leanchecker/nanoda, blueprint sync, or audit CI)."
            }},
            {{
              value: "Tier2_Silver",
              badge: "SILVER",
              badgeBg: "#e2e8f0", badgeColor: "#334155",
              tone: "",
              label: "Tier 2 — Silver (Public, Basic Checks)",
              desc: "Public Lean repo with real compiling-looking proofs (0 sorry/axiom or minor gaps), partial/supporting lemmas or standard lake build without comparator/multi-kernel/blueprint sync."
            }},
            {{
              value: "Tier1_Bronze",
              badge: "BRONZE",
              badgeBg: "#ffedd5", badgeColor: "#9a3412",
              tone: "tone-warn",
              label: "Tier 1 — Bronze (Missing Repo or Red Flags)",
              desc: "Claimed Lean verification WITHOUT a public Lean artifact (lean_files=0 or broken link), OR contains sorry / custom_axiom / native_decide, OR unchecked agent dump."
            }}
          ]
        }},
        {{
          key: "ai_agent_assisted",
          step: "Step 5",
          shortName: "5. AI",
          stepClass: "q-s5",
          color: "var(--s5)",
          lookHint: "Look: Top Signal Tile 4 + Purple Highlights",
          title: "Did the authors disclose using AI/LLM agents for Lean proofs?",
          conditional: true,
          options: [
            {{
              value: "explicitly_yes",
              badge: "YES",
              badgeBg: "#fae8ff", badgeColor: "#86198f",
              tone: "tone-purple",
              label: "Explicitly Yes",
              desc: "Paper, snippets, README, or LaTeX agent_tools clearly indicate LLMs/AI coding or proving agents (Claude, Codex, GPT, Gemini, DeepSeek, Aristotle, etc.) helped with Lean."
            }},
            {{
              value: "explicitly_no",
              badge: "NO (HUMAN)",
              badgeBg: "#d1fae5", badgeColor: "#065f46",
              tone: "tone-ok",
              label: "Explicitly No",
              desc: "Paper or README explicitly states the Lean proofs were written by humans without AI assistance."
            }},
            {{
              value: "unclear",
              badge: "UNCLEAR",
              badgeBg: "#f1f5f9", badgeColor: "#475569",
              tone: "",
              label: "Unclear / Not Mentioned",
              desc: "Contributed Lean proofs, with no clear disclosure either way about AI assistance for the Lean formalization."
            }}
          ]
        }}
      ];

      let state = {{
        annotator_id: DEFAULT_ANNOTATOR,
        currentIdx: 0,
        answers: {{}}
      }};

      function itemKey(item) {{
        return item.slice_id + "::" + item.arxiv_id;
      }}

      function loadState() {{
        try {{
          const raw = localStorage.getItem(STORAGE_KEY);
          if (raw) {{
            const parsed = JSON.parse(raw);
            if (parsed && typeof parsed === "object") {{
              state.annotator_id = parsed.annotator_id || DEFAULT_ANNOTATOR;
              state.currentIdx = Math.max(0, Math.min(ITEMS.length - 1, Number(parsed.currentIdx) || 0));
              state.answers = parsed.answers && typeof parsed.answers === "object" ? parsed.answers : {{}};
            }}
          }}
        }} catch (_) {{}}
      }}

      function saveState() {{
        try {{
          localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        }} catch (_) {{}}
      }}

      function getAnswer(item) {{
        const k = itemKey(item);
        if (!state.answers[k]) {{
          state.answers[k] = {{
            lean_usage_status: "",
            paper_domain_role: "",
            authoring_paradigm: "",
            verification_tier: "",
            ai_agent_assisted: "",
            notes: ""
          }};
        }}
        return state.answers[k];
      }}

      function completionStatus(ans) {{
        if (!ans || !ans.lean_usage_status) return "empty";
        if (ans.lean_usage_status !== "lean_contributed") return "complete";
        const needed = ["paper_domain_role", "authoring_paradigm", "verification_tier", "ai_agent_assisted"];
        const filled = needed.filter((k) => ans[k] && ans[k] !== "N/A").length;
        return filled === needed.length ? "complete" : "partial";
      }}

      function escapeHtml(s) {{
        return String(s || "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");
      }}

      function highlightKeywords(text) {{
        let safe = escapeHtml(text);
        safe = safe.replace(
          /\\b(Lean(?:\\s*4)?|Mathlib|leanprover|comparator|blueprint|leanblueprint|Challenge\\.lean|Solution\\.lean|print axioms|sorry)\\b/gi,
          '<mark class="lean-hit">$1</mark>'
        );
        safe = safe.replace(
          /\\b(Claude|Codex|ChatGPT|GPT-?[0-9a-z.]*|Gemini|DeepSeek|Aristotle|Antigravity|Copilot|LLM|AI agent|AI-assisted|human-written|without AI)\\b/gi,
          '<mark class="ai-hit">$1</mark>'
        );
        return safe;
      }}

      function showToast(msg) {{
        const el = document.getElementById("toast");
        el.textContent = msg;
        el.classList.add("show");
        clearTimeout(el._timer);
        el._timer = setTimeout(() => el.classList.remove("show"), 2600);
      }}

      function renderNav() {{
        const nav = document.getElementById("nav-strip");
        let doneCount = 0;
        const html = ITEMS.map((item, i) => {{
          const ans = getAnswer(item);
          const st = completionStatus(ans);
          if (st === "complete") doneCount++;
          let stClass = "";
          let mark = "";
          if (st === "complete") {{
            mark = "&#10003;";
            if (ans.lean_usage_status === "lean_contributed") stClass = "done-contrib";
            else if (ans.lean_usage_status === "false_positive") stClass = "done-fp";
            else stClass = "done-cite";
          }} else if (st === "partial") {{
            stClass = "partial";
            mark = "&middot;";
          }}
          const cls = ["nav-dot", stClass, i === state.currentIdx ? "active" : ""].join(" ");
          return `<button class="${{cls}}" data-idx="${{i}}" title="Item ${{i + 1}}: ${{item.arxiv_id}} (${{st}})">${{i + 1}}${{mark ? " " + mark : ""}}</button>`;
        }}).join("");
        nav.innerHTML = html;

        const pct = Math.round((doneCount / ITEMS.length) * 100);
        document.getElementById("progress-fill").style.width = pct + "%";
        document.getElementById("progress-text").textContent = `${{doneCount}} / ${{ITEMS.length}}`;
        document.getElementById("progress-wrap").classList.toggle("done", doneCount === ITEMS.length);
        document.getElementById("complete-banner").classList.toggle("show", doneCount === ITEMS.length);

        nav.querySelectorAll(".nav-dot").forEach((btn) => {{
          btn.addEventListener("click", () => {{
            state.currentIdx = Number(btn.dataset.idx);
            saveState();
            renderAll();
          }});
        }});
      }}

      function buildSignalStrip(item) {{
        // Purely factual Stage-2 / Stage-3 summary tiles (zero LLM labels!)
        // Tile 1: Stage-2 Match
        const strongCnt = (item.strong_matches || []).reduce((acc, m) => acc + (m.count || 0), 0);
        const ctxCnt = (item.contextual_matches && item.contextual_matches.count) || 0;
        const t1Class = item.has_lean_strong ? "sig-blue" : "sig-warn";
        const t1Val = item.has_lean_strong ? "Strong Lean Regex" : "Contextual-Only Hit";
        const t1Sub = `${{strongCnt}} strong · ${{ctxCnt}} contextual match(es)`;

        // Tile 2: Public Lean Code
        const leanRepos = (item.repos || []).filter((r) => r.accessible && (r.lean_file_count || 0) > 0);
        const totalLeanFiles = leanRepos.reduce((acc, r) => acc + (r.lean_file_count || 0), 0);
        const totalLoc = leanRepos.reduce((acc, r) => acc + ((r.lean_static_counts && r.lean_static_counts.loc_nonempty) || 0), 0);
        const t2Class = totalLeanFiles > 0 ? "sig-ok" : "sig-bad";
        const t2Val = totalLeanFiles > 0 ? `${{totalLeanFiles.toLocaleString()}} .lean files` : "0 .lean files";
        const t2Sub = totalLeanFiles > 0
          ? `${{leanRepos.length}} Lean repo(s) · ${{totalLoc.toLocaleString()}} LoC`
          : `${{item.total_repos_profiled || 0}} repo(s) profiled, none with Lean`;

        // Tile 3: Cleanliness & Audit Rigor (factual static counts from primary Lean repo(s))
        let t3Class = "";
        let t3Val = "No Lean repo";
        let t3Sub = "Static Lean scan not applicable";
        if (leanRepos.length > 0) {{
          const primary = leanRepos[0];
          const sc = primary.lean_static_counts || {{}};
          const sorryC = sc.sorry || 0;
          const axC = sc.custom_axiom || 0;
          const ndC = sc.native_decide || 0;
          const printAx = sc.print_axioms || 0;
          const auditSignals = [];
          if (printAx > 0) auditSignals.push(`#print axioms (${{printAx}})`);
          if (primary.has_blueprint_dir) auditSignals.push("blueprint_dir");
          if (primary.has_challenge_file || primary.has_solution_file) auditSignals.push("Challenge/Solution");
          (primary.ci_signals || []).forEach((s) => auditSignals.push(`CI:${{s}}`));
          if (item.latex_signals && item.latex_signals.leanblueprint_pkg) auditSignals.push("leanblueprint");

          if (sorryC > 0 || axC > 0 || ndC > 0) {{
            t3Class = "sig-bad";
            t3Val = `Red flags in ${{primary.repo.split("/").pop()}}`;
            const bits = [];
            if (sorryC) bits.push(`sorry=${{sorryC}}`);
            if (axC) bits.push(`custom_axiom=${{axC}}`);
            if (ndC) bits.push(`native_decide=${{ndC}}`);
            t3Sub = bits.join(", ");
          }} else if (auditSignals.length > 0) {{
            t3Class = "sig-gold";
            t3Val = "0 sorry/axiom + Audit";
            t3Sub = auditSignals.slice(0, 3).join(" · ");
          }} else {{
            t3Class = "sig-ok";
            t3Val = "0 sorry/axiom/native_decide";
            t3Sub = "No comparator/blueprint/#print axioms detected";
          }}
        }}

        // Tile 4: LaTeX AI Tool Mentions
        const aiTools = (item.latex_signals && item.latex_signals.agent_tools) || [];
        const t4Class = aiTools.length > 0 ? "sig-purple" : "";
        const t4Val = aiTools.length > 0 ? aiTools.slice(0, 3).join(", ") : "None in LaTeX scan";
        const t4Sub = aiTools.length > 0
          ? `${{aiTools.length}} AI tool keyword(s) in .tex (check context!)`
          : (item.latex_fetched ? "Check snippets & README too" : "LaTeX source not fetched");

        return `
          <div class="signal-strip">
            <div class="sig-tile ${{t1Class}}">
              <div class="sig-k">Step 1 · Stage-2 Hit</div>
              <div class="sig-v">${{escapeHtml(t1Val)}}</div>
              <div class="sig-sub">${{escapeHtml(t1Sub)}}</div>
            </div>
            <div class="sig-tile ${{t2Class}}">
              <div class="sig-k">Step 3/4 · Public Lean</div>
              <div class="sig-v">${{escapeHtml(t2Val)}}</div>
              <div class="sig-sub">${{escapeHtml(t2Sub)}}</div>
            </div>
            <div class="sig-tile ${{t3Class}}">
              <div class="sig-k">Step 4 · Static Audit</div>
              <div class="sig-v">${{escapeHtml(t3Val)}}</div>
              <div class="sig-sub">${{escapeHtml(t3Sub)}}</div>
            </div>
            <div class="sig-tile ${{t4Class}}">
              <div class="sig-k">Step 5 · LaTeX AI Tools</div>
              <div class="sig-v">${{escapeHtml(t4Val)}}</div>
              <div class="sig-sub">${{escapeHtml(t4Sub)}}</div>
            </div>
          </div>`;
      }}

      function renderRepoCard(rp, rIdx) {{
        if (!rp.accessible) {{
          return `
            <div class="repo-card">
              <div class="repo-head">
                <span class="repo-name">${{escapeHtml(rp.repo)}}</span>
                <span class="chip chip-bad">Inaccessible / 404 or private</span>
              </div>
            </div>`;
        }}
        const hasLean = (rp.lean_file_count || 0) > 0;
        const sc = rp.lean_static_counts || {{}};
        const sorryCnt = sc.sorry || 0;
        const axiomCnt = sc.custom_axiom || 0;
        const nativeCnt = sc.native_decide || 0;
        const printAx = sc.print_axioms || 0;

        let chips = [];
        chips.push(`<span class="chip ${{hasLean ? "chip-ok" : ""}}">lean_files=${{rp.lean_file_count || 0}}</span>`);
        chips.push(`<span class="chip">total_files=${{rp.total_files || 0}}</span>`);
        if (rp.tex_file_count) chips.push(`<span class="chip">tex_files=${{rp.tex_file_count}}</span>`);
        if (rp.lean_toolchain) chips.push(`<span class="chip chip-blue">toolchain=${{escapeHtml(rp.lean_toolchain)}}</span>`);
        if (rp.has_blueprint_dir) chips.push(`<span class="chip chip-purple">blueprint_dir</span>`);
        if (rp.has_challenge_file) chips.push(`<span class="chip chip-purple">Challenge.lean</span>`);
        if (rp.has_solution_file) chips.push(`<span class="chip chip-purple">Solution.lean</span>`);
        (rp.ci_signals || []).forEach((sig) => {{
          const c = /comparator|nanoda|leanchecker|blueprint/i.test(sig) ? "chip-gold" : "chip-ok";
          chips.push(`<span class="chip ${{c}}">CI: ${{escapeHtml(sig)}}</span>`);
        }});

        let staticHtml = "";
        if (hasLean || Object.keys(sc).length > 0) {{
          const sChips = [];
          if (sc.loc_nonempty != null) sChips.push(`<span class="chip">LoC=${{sc.loc_nonempty.toLocaleString()}}</span>`);
          if (sc.theorem_decl != null) sChips.push(`<span class="chip">theorems=${{sc.theorem_decl.toLocaleString()}}</span>`);
          if (sc.def_decl != null) sChips.push(`<span class="chip">defs=${{sc.def_decl.toLocaleString()}}</span>`);
          if (sc.mathlib_import != null) sChips.push(`<span class="chip">mathlib_imports=${{sc.mathlib_import}}</span>`);

          if (sorryCnt > 0) sChips.push(`<span class="chip chip-bad">sorry=${{sorryCnt}}</span>`);
          if (axiomCnt > 0) sChips.push(`<span class="chip chip-bad">custom_axiom=${{axiomCnt}}</span>`);
          if (nativeCnt > 0) sChips.push(`<span class="chip chip-bad">native_decide=${{nativeCnt}}</span>`);
          if (hasLean && sorryCnt === 0 && axiomCnt === 0 && nativeCnt === 0) {{
            sChips.push(`<span class="chip chip-ok">&#10003; 0 sorry / 0 custom_axiom / 0 native_decide</span>`);
          }}
          if (printAx > 0) sChips.push(`<span class="chip chip-gold">#print axioms=${{printAx}}</span>`);
          if (sc.unsafe_or_impl_by) sChips.push(`<span class="chip chip-warn">unsafe/impl_by=${{sc.unsafe_or_impl_by}}</span>`);
          if (sc.metaprog_override) sChips.push(`<span class="chip">metaprog=${{sc.metaprog_override}}</span>`);

          staticHtml = `<div class="chip-row">${{sChips.join("")}}</div>`;
        }}

        let metaBits = [`host=${{rp.host}}`];
        if (rp.stars != null) metaBits.push(`stars=${{rp.stars}}`);
        if (rp.created_at) metaBits.push(`created=${{rp.created_at}}`);
        if (rp.pushed_at) metaBits.push(`pushed=${{rp.pushed_at}}`);

        let extraLines = "";
        if (rp.description) {{
          extraLines += `<div style="font-size:12.5px;color:var(--text-muted);margin-top:4px;">${{highlightKeywords(rp.description)}}</div>`;
        }}
        if (rp.workflow_files && rp.workflow_files.length) {{
          extraLines += `<div style="font-size:11.5px;color:var(--text-faint);margin-top:4px;"><strong>Workflows:</strong> <code>${{escapeHtml(rp.workflow_files.join(", "))}}</code></div>`;
        }}
        if (rp.zenodo_files && rp.zenodo_files.length) {{
          extraLines += `<div style="font-size:11.5px;color:var(--text-faint);margin-top:4px;"><strong>Zenodo files:</strong> <code>${{escapeHtml(rp.zenodo_files.join(", "))}}</code></div>`;
        }}

        let readmeHtml = "";
        if (rp.readme_preview) {{
          const rid = `readme-${{rIdx}}`;
          const needsToggle = rp.readme_preview.length > 460 || rp.readme_preview.split("\\n").length > 8;
          readmeHtml = `
            <div style="margin-top:7px;">
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <span style="font-size:11.5px;font-weight:700;color:var(--text-muted);">README Excerpt</span>
                ${{needsToggle ? `<button class="btn btn-ghost" style="padding:2px 7px;font-size:11px;" data-toggle-readme="${{rid}}">Expand / Collapse</button>` : ""}}
              </div>
              <pre id="${{rid}}" class="readme-box">${{highlightKeywords(rp.readme_preview)}}</pre>
            </div>`;
        }}

        return `
          <div class="repo-card ${{hasLean ? "has-lean" : ""}}">
            <div class="repo-head">
              <span class="repo-name">${{escapeHtml(rp.repo)}}</span>
              <span style="font-size:11.5px;color:var(--text-faint);">${{escapeHtml(metaBits.join(" · "))}}</span>
            </div>
            ${{extraLines}}
            <div class="chip-row">${{chips.join("")}}</div>
            ${{staticHtml}}
            ${{readmeHtml}}
          </div>`;
      }}

      function renderEvidence() {{
        const item = ITEMS[state.currentIdx];
        document.getElementById("paper-counter").textContent = `Item ${{item.idx}} of ${{ITEMS.length}} — arXiv:${{item.arxiv_id}} (Slice ${{item.slice_id}})`;
        document.getElementById("paper-links").innerHTML = `<a class="btn" href="${{item.arxiv_url}}" target="_blank" rel="noopener noreferrer">Open on arXiv &nearr;</a>`;

        const body = document.getElementById("evidence-body");

        let metaChips = [
          `<span class="chip chip-indigo">primary: ${{escapeHtml(item.primary_category)}}</span>`,
          `<span class="chip">target: ${{escapeHtml(item.matched_target_cats.join(", "))}}</span>`,
          `<span class="chip">all: ${{escapeHtml(item.all_categories.join(", "))}}</span>`,
          `<span class="chip">submitted: ${{escapeHtml(item.submitted_date)}}</span>`,
          `<span class="chip">source: ${{escapeHtml(item.fetch_source)}}</span>`
        ];
        if (item.other_tools && item.other_tools.length) {{
          const ot = item.other_tools.map((g) => `${{g.group}}:[${{g.tools.join(",")}}]`).join(" ");
          metaChips.push(`<span class="chip">other FV tools: ${{escapeHtml(ot)}}</span>`);
        }}

        let commentHtml = "";
        if (item.comment) {{
          commentHtml += `<div class="comment-box"><strong>arXiv Comment:</strong> ${{highlightKeywords(item.comment)}}</div>`;
        }}
        if (item.journal_ref) {{
          commentHtml += `<div class="comment-box" style="background:var(--surface-alt);border-color:var(--border);color:var(--text-muted);"><strong>Journal Ref:</strong> ${{escapeHtml(item.journal_ref)}}</div>`;
        }}

        let snipsHtml = "";
        if (item.strong_matches && item.strong_matches.length) {{
          item.strong_matches.forEach((m) => {{
            snipsHtml += `<div class="snippet-group"><div class="snippet-label">Strong pattern <code>${{escapeHtml(m.pattern)}}</code> (count=${{m.count}})</div>`;
            m.snippets.forEach((s) => {{
              snipsHtml += `<blockquote class="snippet">&ldquo;${{highlightKeywords(s)}}&rdquo;</blockquote>`;
            }});
            snipsHtml += `</div>`;
          }});
        }}
        if (item.contextual_matches && item.contextual_matches.snippets && item.contextual_matches.snippets.length) {{
          snipsHtml += `<div class="snippet-group"><div class="snippet-label">Contextual Lean matches (count=${{item.contextual_matches.count}})</div>`;
          item.contextual_matches.snippets.forEach((s) => {{
            snipsHtml += `<blockquote class="snippet">&ldquo;${{highlightKeywords(s)}}&rdquo;</blockquote>`;
          }});
          snipsHtml += `</div>`;
        }}
        if (!snipsHtml) {{
          snipsHtml = `<div class="empty-muted">No matched snippets stored.</div>`;
        }}

        let urlsHtml = "";
        if (item.urls && item.urls.length) {{
          urlsHtml = `<div class="url-list">` +
            item.urls.map((u) => `<a class="url-link" href="${{escapeHtml(u)}}" target="_blank" rel="noopener noreferrer">${{escapeHtml(u)}}</a>`).join("") +
            (item.urls_omitted > 0 ? `<span class="chip">+${{item.urls_omitted}} more</span>` : "") +
            `</div>`;
        }}

        const ls = item.latex_signals || {{}};
        let latexChips = [`<span class="chip">latex_fetched=${{item.latex_fetched ? "yes" : "no"}}</span>`];
        if (ls.agent_tools && ls.agent_tools.length) {{
          latexChips.push(`<span class="chip chip-fuchsia">LaTeX AI tools: ${{escapeHtml(ls.agent_tools.join(", "))}}</span>`);
        }}
        if (ls.leanblueprint_pkg) {{
          latexChips.push(`<span class="chip chip-purple">leanblueprint_pkg=true</span>`);
        }}
        if (ls.lean_macro) {{
          latexChips.push(`<span class="chip chip-blue">lean_macro=${{ls.lean_macro}}</span>`);
        }}
        if (ls.theorem_envs != null) {{
          latexChips.push(`<span class="chip">theorem_envs=${{ls.theorem_envs}}</span>`);
        }}
        if (ls.tex_files_chars != null) {{
          latexChips.push(`<span class="chip">tex_chars=${{ls.tex_files_chars.toLocaleString()}}</span>`);
        }}

        let reposHtml = "";
        if (item.repos && item.repos.length) {{
          reposHtml = item.repos.map((rp, idx) => renderRepoCard(rp, idx)).join("");
          if (item.omitted_repos_total > 0) {{
            reposHtml += `<div class="empty-muted">Additional non-Lean repos omitted (${{item.omitted_repos_total}}): <code>${{escapeHtml(item.omitted_repos.join(", "))}}</code></div>`;
          }}
        }} else {{
          reposHtml = `<div class="empty-muted">No linked code repositories profiled in Stage 3.</div>`;
        }}

        body.innerHTML = `
          ${{buildSignalStrip(item)}}

          <div class="ev-section ev-s2">
            <div class="ev-section-head">
              <span class="ev-section-title">Paper Metadata &amp; Abstract</span>
              <span class="cue-pill" style="background:var(--s2-soft);color:var(--s2);">Helps with Steps 1 &amp; 2</span>
            </div>
            <div class="chip-row">${{metaChips.join("")}}</div>
            <h2 class="paper-title">${{escapeHtml(item.title)}}</h2>
            ${{commentHtml}}
            <div class="abstract-box">${{highlightKeywords(item.abstract)}}</div>
          </div>

          <div class="ev-section ev-s1">
            <div class="ev-section-head">
              <span class="ev-section-title">Stage-2 Matched Prose Snippets &amp; URLs</span>
              <span class="cue-pill" style="background:var(--s1-soft);color:var(--s1);">Yellow = Lean/Audit · Pink = AI</span>
            </div>
            ${{snipsHtml}}
            ${{urlsHtml}}
          </div>

          <div class="ev-section ev-s3">
            <div class="ev-section-head">
              <span class="ev-section-title">Stage-3 Static Artifact Profile (LaTeX &amp; Repos)</span>
              <span class="cue-pill" style="background:var(--s4-soft);color:var(--s4);">Helps with Steps 3, 4 &amp; 5</span>
            </div>
            <div class="chip-row" style="margin-bottom:10px;">${{latexChips.join("")}}</div>
            ${{reposHtml}}
          </div>
        `;

        body.querySelectorAll("[data-toggle-readme]").forEach((btn) => {{
          btn.addEventListener("click", () => {{
            const pre = document.getElementById(btn.dataset.toggleReadme);
            if (pre) pre.classList.toggle("expanded");
          }});
        }});
      }}

      function renderStepper(ans) {{
        const isNonContrib = ans.lean_usage_status === "false_positive" || ans.lean_usage_status === "lean_citation_or_discussion";
        const stepper = document.getElementById("stepper");
        stepper.innerHTML = QUESTIONS.map((q) => {{
          let cls = "step-pill";
          let suffix = "";
          if (q.conditional && isNonContrib) {{
            cls += " na";
            suffix = " N/A";
          }} else if (ans[q.key] && ans[q.key] !== "N/A") {{
            cls += " done";
            suffix = " &#10003;";
          }} else if (!q.conditional || ans.lean_usage_status === "lean_contributed") {{
            cls += " todo";
          }}
          return `<span class="${{cls}}">${{q.shortName}}${{suffix}}</span>`;
        }}).join("");
      }}

      function renderForm() {{
        const item = ITEMS[state.currentIdx];
        const ans = getAnswer(item);
        const st = completionStatus(ans);
        const badge = document.getElementById("item-status-badge");
        if (st === "complete") {{
          badge.textContent = "&#10003; Complete";
          badge.innerHTML = "&#10003; Complete";
          badge.className = "chip chip-ok";
        }} else if (st === "partial") {{
          badge.textContent = "Finish Steps 2-5";
          badge.className = "chip chip-warn";
        }} else {{
          badge.textContent = "Unlabeled";
          badge.className = "chip";
        }}

        renderStepper(ans);

        const isNonContrib = ans.lean_usage_status === "false_positive" || ans.lean_usage_status === "lean_citation_or_discussion";
        const formBody = document.getElementById("form-body");

        let html = "";
        QUESTIONS.forEach((q, qIdx) => {{
          const disabled = q.conditional && isNonContrib;
          const curVal = ans[q.key] || "";
          const optsHtml = q.options.map((opt) => {{
            const sel = !disabled && curVal === opt.value;
            return `
              <button type="button" class="opt-card ${{opt.tone || ""}} ${{sel ? "selected" : ""}}" data-q="${{q.key}}" data-val="${{opt.value}}">
                <div class="opt-top">
                  <span class="opt-name">
                    <span class="opt-badge" style="background:${{opt.badgeBg}};color:${{opt.badgeColor}};">${{escapeHtml(opt.badge)}}</span>
                    ${{escapeHtml(opt.label)}}
                  </span>
                  <span class="opt-enum">${{escapeHtml(opt.value)}}</span>
                </div>
                <div class="opt-desc">${{escapeHtml(opt.desc)}}</div>
              </button>`;
          }}).join("");

          html += `
            <div class="q-block ${{q.stepClass}} ${{disabled ? "disabled" : ""}}">
              <div class="q-header">
                <div class="q-title"><span class="q-step-tag" style="background:${{q.color}};">${{q.step}}</span>${{escapeHtml(q.title)}}</div>
                ${{disabled ? '<span class="chip chip-ok">Auto: N/A</span>' : `<span class="q-look-hint">${{escapeHtml(q.lookHint)}}</span>`}}
              </div>
              <div class="opt-grid">${{optsHtml}}</div>
            </div>`;

          if (qIdx === 0 && isNonContrib) {{
            html += `
              <div class="short-circuit-banner">
                <div><strong>Done with Item ${{item.idx}}!</strong> Steps 2&ndash;5 are automatically set to <code>N/A</code>.</div>
                ${{state.currentIdx < ITEMS.length - 1 ? '<button type="button" class="btn btn-ok" id="btn-quick-next">Next Paper &rarr;</button>' : '<button type="button" class="btn btn-ok" id="btn-quick-unlabeled">Next Unlabeled &rarr;</button>'}}
              </div>`;
          }}
        }});

        html += `
          <div class="q-block" style="border-top-color:#64748b;">
            <div class="q-header">
              <div class="q-title">Optional Notes (ambiguities or rationale)</div>
            </div>
            <textarea id="notes-input" class="notes-input" placeholder="Optional brief note for disagreement reconciliation...">${{escapeHtml(ans.notes || "")}}</textarea>
          </div>`;

        formBody.innerHTML = html;

        formBody.querySelectorAll(".opt-card").forEach((btn) => {{
          btn.addEventListener("click", () => {{
            const qKey = btn.dataset.q;
            const val = btn.dataset.val;
            ans[qKey] = val;
            if (qKey === "lean_usage_status") {{
              if (val !== "lean_contributed") {{
                ans.paper_domain_role = "N/A";
                ans.authoring_paradigm = "N/A";
                ans.verification_tier = "N/A";
                ans.ai_agent_assisted = "N/A";
              }} else {{
                ["paper_domain_role", "authoring_paradigm", "verification_tier", "ai_agent_assisted"].forEach((k) => {{
                  if (ans[k] === "N/A") ans[k] = "";
                }});
              }}
            }}
            saveState();
            renderNav();
            renderForm();
          }});
        }});

        const quickNext = document.getElementById("btn-quick-next");
        if (quickNext) {{
          quickNext.addEventListener("click", () => {{
            state.currentIdx++;
            saveState();
            renderAll();
          }});
        }}
        const quickUnl = document.getElementById("btn-quick-unlabeled");
        if (quickUnl) {{
          quickUnl.addEventListener("click", () => document.getElementById("btn-next-unlabeled").click());
        }}

        const notesEl = document.getElementById("notes-input");
        notesEl.addEventListener("input", () => {{
          ans.notes = notesEl.value;
          saveState();
        }});

        document.getElementById("btn-prev").disabled = state.currentIdx === 0;
        document.getElementById("btn-next").disabled = state.currentIdx === ITEMS.length - 1;
      }}

      function csvEscape(v) {{
        const s = String(v == null ? "" : v);
        if (/[",\\n\\r]/.test(s)) {{
          return '"' + s.replace(/"/g, '""') + '"';
        }}
        return s;
      }}

      function buildCsvString() {{
        const lines = [CSV_COLS.join(",")];
        const annId = (state.annotator_id || DEFAULT_ANNOTATOR).trim() || DEFAULT_ANNOTATOR;
        ITEMS.forEach((item) => {{
          const ans = getAnswer(item);
          const status = ans.lean_usage_status || "";
          const isNon = status && status !== "lean_contributed";
          const row = [
            item.slice_id,
            item.arxiv_id,
            annId,
            status,
            isNon ? "N/A" : (ans.paper_domain_role || ""),
            isNon ? "N/A" : (ans.authoring_paradigm || ""),
            isNon ? "N/A" : (ans.verification_tier || ""),
            isNon ? "N/A" : (ans.ai_agent_assisted || ""),
            (ans.notes || "").replace(/\\r?\\n/g, " ").trim()
          ];
          lines.push(row.map(csvEscape).join(","));
        }});
        return lines.join("\\n") + "\\n";
      }}

      function parseCsvLine(line) {{
        const out = [];
        let cur = "";
        let inQ = false;
        for (let i = 0; i < line.length; i++) {{
          const ch = line[i];
          if (inQ) {{
            if (ch === '"' && line[i + 1] === '"') {{
              cur += '"';
              i++;
            }} else if (ch === '"') {{
              inQ = false;
            }} else {{
              cur += ch;
            }}
          }} else {{
            if (ch === '"') {{
              inQ = true;
            }} else if (ch === ",") {{
              out.push(cur);
              cur = "";
            }} else {{
              cur += ch;
            }}
          }}
        }}
        out.push(cur);
        return out;
      }}

      function importCsvText(text) {{
        const lines = text.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").split("\\n").filter((l) => l.trim().length > 0);
        if (lines.length < 2) {{
          showToast("CSV appears empty");
          return;
        }}
        const header = parseCsvLine(lines[0]).map((s) => s.trim());
        const idxMap = {{}};
        header.forEach((h, i) => (idxMap[h] = i));
        let imported = 0;
        const validKeys = new Set(ITEMS.map(itemKey));
        for (let r = 1; r < lines.length; r++) {{
          const cols = parseCsvLine(lines[r]);
          const sl = (cols[idxMap.slice_id] || "").trim();
          const aid = (cols[idxMap.arxiv_id] || "").trim();
          const k = sl + "::" + aid;
          if (!validKeys.has(k)) continue;
          const status = (cols[idxMap.lean_usage_status] || "").trim();
          if (!status) continue;
          const annId = (cols[idxMap.annotator_id] || "").trim();
          if (annId) state.annotator_id = annId;
          state.answers[k] = {{
            lean_usage_status: status,
            paper_domain_role: (cols[idxMap.paper_domain_role] || "").trim(),
            authoring_paradigm: (cols[idxMap.authoring_paradigm] || "").trim(),
            verification_tier: (cols[idxMap.verification_tier] || "").trim(),
            ai_agent_assisted: (cols[idxMap.ai_agent_assisted] || "").trim(),
            notes: (cols[idxMap.notes] || "").trim()
          }};
          imported++;
        }}
        document.getElementById("annotator-input").value = state.annotator_id;
        saveState();
        renderAll();
        showToast(`Imported ${{imported}} labeled rows from CSV`);
      }}

      function triggerDownload() {{
        const doneCount = ITEMS.filter((it) => completionStatus(getAnswer(it)) === "complete").length;
        const csv = buildCsvString();
        const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "stage4_irr.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        showToast(`Downloaded stage4_irr.csv (${{doneCount}}/${{ITEMS.length}} complete)`);
      }}

      function renderAll() {{
        renderNav();
        renderEvidence();
        renderForm();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }}

      loadState();
      const annInput = document.getElementById("annotator-input");
      annInput.value = state.annotator_id;
      annInput.addEventListener("input", () => {{
        state.annotator_id = annInput.value.trim() || DEFAULT_ANNOTATOR;
        saveState();
      }});

      document.getElementById("btn-guide").addEventListener("click", () => {{
        document.getElementById("guide-drawer").classList.toggle("open");
      }});
      document.getElementById("btn-close-guide").addEventListener("click", () => {{
        document.getElementById("guide-drawer").classList.remove("open");
      }});

      document.getElementById("btn-prev").addEventListener("click", () => {{
        if (state.currentIdx > 0) {{
          state.currentIdx--;
          saveState();
          renderAll();
        }}
      }});
      document.getElementById("btn-next").addEventListener("click", () => {{
        if (state.currentIdx < ITEMS.length - 1) {{
          state.currentIdx++;
          saveState();
          renderAll();
        }}
      }});
      document.getElementById("btn-next-unlabeled").addEventListener("click", () => {{
        for (let step = 1; step <= ITEMS.length; step++) {{
          const cand = (state.currentIdx + step) % ITEMS.length;
          if (completionStatus(getAnswer(ITEMS[cand])) !== "complete") {{
            state.currentIdx = cand;
            saveState();
            renderAll();
            return;
          }}
        }}
        showToast("All 30 items are complete! Ready to download stage4_irr.csv");
      }});

      document.getElementById("btn-download").addEventListener("click", triggerDownload);
      document.getElementById("btn-download-banner").addEventListener("click", triggerDownload);

      document.getElementById("btn-copy").addEventListener("click", async () => {{
        const csv = buildCsvString();
        try {{
          await navigator.clipboard.writeText(csv);
          showToast("Copied CSV to clipboard");
        }} catch (_) {{
          showToast("Clipboard blocked — use Download stage4_irr.csv");
        }}
      }});

      document.getElementById("btn-import").addEventListener("click", () => {{
        document.getElementById("file-import").click();
      }});
      document.getElementById("file-import").addEventListener("change", (ev) => {{
        const file = ev.target.files && ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => importCsvText(String(reader.result || ""));
        reader.readAsText(file);
        ev.target.value = "";
      }});

      document.getElementById("btn-reset").addEventListener("click", () => {{
        if (!confirm("Clear all locally saved labels in this browser?")) return;
        state.answers = {{}};
        state.currentIdx = 0;
        saveState();
        renderAll();
        showToast("Cleared local progress");
      }});

      document.addEventListener("keydown", (ev) => {{
        if (ev.altKey && ev.key === "ArrowLeft" && state.currentIdx > 0) {{
          ev.preventDefault();
          state.currentIdx--;
          saveState();
          renderAll();
        }} else if (ev.altKey && ev.key === "ArrowRight" && state.currentIdx < ITEMS.length - 1) {{
          ev.preventDefault();
          state.currentIdx++;
          saveState();
          renderAll();
        }}
      }});

      renderAll();
    }})();
  </script>
</body>
</html>
"""


def verify_blinding(dossier_path: Path, blank_csv_path: Path, html_app_path: Path | None = None) -> list[str]:
    """Scan generated dossier, blank CSV data rows, and HTML items payload for leaked Stage-4 LLM tokens."""
    violations: list[str] = []
    dossier_text = dossier_path.read_text(encoding="utf-8")
    for tok in FORBIDDEN_BLIND_TOKENS:
        if re.search(rf"\b{re.escape(tok)}\b", dossier_text):
            violations.append(f"{dossier_path.name}: leaked forbidden token {tok!r}")

    with blank_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != CSV_COLUMNS:
            violations.append(f"{blank_csv_path.name}: unexpected header {reader.fieldnames}")
        for row_idx, row in enumerate(reader, 1):
            for col in CSV_COLUMNS[3:]:
                if (row.get(col) or "").strip() != "":
                    violations.append(f"{blank_csv_path.name} row {row_idx}: non-empty label col {col!r}")
            row_blob = " ".join(str(v) for v in row.values())
            for tok in FORBIDDEN_BLIND_TOKENS:
                if re.search(rf"\b{re.escape(tok)}\b", row_blob):
                    violations.append(f"{blank_csv_path.name} row {row_idx}: leaked token {tok!r}")

    if html_app_path is not None and html_app_path.is_file():
        html_text = html_app_path.read_text(encoding="utf-8")
        m = re.search(
            r'<script id="blind-items-data" type="application/json">(.*?)</script>',
            html_text,
            flags=re.DOTALL,
        )
        if not m:
            violations.append(f"{html_app_path.name}: missing blind-items-data JSON block")
        else:
            items_blob = m.group(1)
            for tok in FORBIDDEN_BLIND_TOKENS:
                if re.search(rf"\b{re.escape(tok)}\b", items_blob):
                    violations.append(f"{html_app_path.name} items payload: leaked forbidden token {tok!r}")

    return violations


def main() -> None:
    ap = argparse.ArgumentParser(description="Build blinded Stage-4 human IRR kit (n = 30).")
    ap.add_argument("--seed", type=int, default=20261123, help="Deterministic RNG seed (default: 20261123).")
    ap.add_argument("--annotator-id", default="annotator_1", help="Pseudonymous annotator ID (default: annotator_1).")
    ap.add_argument("--blank-csv", type=Path, default=DEFAULT_BLANK_CSV, help="Output blank CSV path.")
    ap.add_argument("--dossier-md", type=Path, default=DEFAULT_DOSSIER_MD, help="Output blinded Markdown dossier path.")
    ap.add_argument("--html-app", type=Path, default=DEFAULT_HTML_APP, help="Output self-contained blinded HTML app path.")
    ap.add_argument("--n-contributed", type=int, default=16)
    ap.add_argument("--n-citation", type=int, default=10)
    ap.add_argument("--n-false-positive", type=int, default=4)
    args = ap.parse_args()

    records = load_candidates(DEFAULT_SLICES)
    sample = draw_stratified_sample(
        records,
        seed=args.seed,
        n_contributed=args.n_contributed,
        n_citation=args.n_citation,
        n_false_positive=args.n_false_positive,
    )

    args.dossier_md.parent.mkdir(parents=True, exist_ok=True)
    args.dossier_md.write_text(render_dossier_markdown(sample, seed=args.seed), encoding="utf-8")
    write_blank_csv(sample, args.blank_csv, annotator_id=args.annotator_id)
    args.html_app.parent.mkdir(parents=True, exist_ok=True)
    args.html_app.write_text(
        render_blind_html(sample, seed=args.seed, annotator_id=args.annotator_id),
        encoding="utf-8",
    )

    violations = verify_blinding(args.dossier_md, args.blank_csv, args.html_app)
    if violations:
        print("BLINDING VERIFICATION FAILED:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    # Print aggregate (non-item-identifying) coverage summary so per-item blinding stays intact.
    status_counts = Counter(r.lean_usage_status for r in sample)
    slice_counts = Counter(r.slice_id for r in sample)
    contribs = [r for r in sample if r.lean_usage_status == "lean_contributed"]
    print(f"Prepared blinded Stage-4 IRR kit (n={len(sample)}, seed={args.seed}):")
    print(f"  Blank CSV : {args.blank_csv}")
    print(f"  Dossier MD: {args.dossier_md}")
    print(f"  HTML App  : {args.html_app}")
    print(f"  Blinding check: PASSED (0 forbidden LLM tokens leaked)")
    print(f"  Aggregate slice counts  : {dict(sorted(slice_counts.items()))}")
    print(f"  Aggregate status counts : {dict(sorted(status_counts.items()))}")
    print(
        "  Contributed strata coverage: "
        f"roles={len({r.paper_domain_role for r in contribs})}/3, "
        f"paradigms={len({r.authoring_paradigm for r in contribs})}/4, "
        f"tiers={len({r.verification_tier for r in contribs})}/3, "
        f"ai_labels={len({r.ai_agent_assisted for r in contribs})}/3"
    )


if __name__ == "__main__":
    main()
