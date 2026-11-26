"""Stage E1: Strictly deterministic, zero-token mathematical structure extractor
for Lean 4 eligibility / denominator-adjusted adoption analysis.

Parses arXiv LaTeXML HTML5 semantic DOM classes (`ltx_theorem`, `ltx_proof`,
`ltx_equation`, section titles, and `<annotation encoding="application/x-tex">`)
with an anchored structural regex fallback for PDF-only preprints.

Persists results and compact evidence snippets (<=2,400 chars) into a dedicated
SQLite DB (`data/eligibility_t2.db`) without modifying existing survey DBs.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import random
import re
import sqlite3
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx
from pypdf import PdfReader

DEFAULT_ELIGIBILITY_DB = Path("data/eligibility_t2.db")
UNIFIED_PANEL_PATH = Path("artifacts/unified_15cat_panel.json")
USER_AGENT = "survey-lean-proofs-eng-arxiv/0.2 (academic research survey; polite structural fetcher)"

ALL15_CATS: list[str] = [
    "math.OC",
    "cs.DC",
    "cs.IT",
    "cs.CR",
    "eess.SY",
    "eess.SP",
    "cs.NI",
    "cs.RO",
    "cs.GT",
    "math.DS",
    "physics.flu-dyn",
    "cs.PF",
    "eess.IV",
    "eess.AS",
    "cs.CE",
]

SOURCE_DBS_T2 = [
    Path("data/survey.db"),
    Path("data/scout_eng_tier12_2026_11.db"),
]

SOURCE_DBS_ALL = [
    Path("data/survey.db"),
    Path("data/scout_eng_tier12_2026_11.db"),
    Path("data/slice_2026_05.db"),
    Path("data/scout_eng_tier12_2026_05.db"),
    Path("data/slice_2025_11.db"),
    Path("data/scout_eng_tier12_2025_11.db"),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS eligibility_papers (
    arxiv_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    slice_id TEXT NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    primary_category TEXT NOT NULL,
    all_categories_json TEXT NOT NULL,
    matched_15_cats_json TEXT NOT NULL,
    submitted_date TEXT NOT NULL,
    comment TEXT,
    in_t2_census INTEGER NOT NULL DEFAULT 0,
    is_confirmed_lean INTEGER NOT NULL DEFAULT 0,
    confirmed_role_4way TEXT,
    confirmed_slice_id TEXT,
    in_pilot_e0 INTEGER NOT NULL DEFAULT 0,
    pilot_strata_cat TEXT
);

CREATE TABLE IF NOT EXISTS math_structure (
    arxiv_id TEXT PRIMARY KEY REFERENCES eligibility_papers(arxiv_id),
    version INTEGER NOT NULL,
    fetch_source TEXT NOT NULL,            -- 'html', 'pdf', 'failed'
    http_status INTEGER,
    error_msg TEXT,
    text_chars INTEGER NOT NULL DEFAULT 0,
    n_theorem INTEGER NOT NULL DEFAULT 0,
    n_lemma INTEGER NOT NULL DEFAULT 0,
    n_proposition INTEGER NOT NULL DEFAULT 0,
    n_corollary INTEGER NOT NULL DEFAULT 0,
    n_claim_or_fact INTEGER NOT NULL DEFAULT 0,
    n_conjecture INTEGER NOT NULL DEFAULT 0,
    n_definition INTEGER NOT NULL DEFAULT 0,
    n_assumption INTEGER NOT NULL DEFAULT 0,
    n_remark_or_example INTEGER NOT NULL DEFAULT 0,
    n_property_or_invariant INTEGER NOT NULL DEFAULT 0,
    n_other_env INTEGER NOT NULL DEFAULT 0,
    n_proof INTEGER NOT NULL DEFAULT 0,
    proof_chars INTEGER NOT NULL DEFAULT 0,
    n_equation INTEGER NOT NULL DEFAULT 0,
    n_display_math INTEGER NOT NULL DEFAULT 0,
    has_theory_section INTEGER NOT NULL DEFAULT 0,
    has_appendix_proofs INTEGER NOT NULL DEFAULT 0,
    e1_bucket TEXT NOT NULL,               -- 'E1_formal_thm_proof', 'E1_weak_or_unnumbered_math', 'E1_no_formal_claims', 'E1_fetch_failed'
    section_headings_json TEXT NOT NULL DEFAULT '[]',
    domain_cues_json TEXT NOT NULL DEFAULT '{}',
    theorem_snippets_json TEXT NOT NULL DEFAULT '[]',
    evidence_snippet TEXT NOT NULL DEFAULT '',
    extracted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eligibility_classifications (
    arxiv_id TEXT PRIMARY KEY REFERENCES eligibility_papers(arxiv_id),
    cohort TEXT NOT NULL,
    model_tier TEXT NOT NULL,
    eligibility_class TEXT NOT NULL,
    has_original_deductive_proof INTEGER NOT NULL,
    dominant_math_area TEXT NOT NULL,
    primary_barrier_if_L2 TEXT NOT NULL,
    confidence TEXT NOT NULL,
    rationale TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    classified_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ep_t2 ON eligibility_papers(in_t2_census);
CREATE INDEX IF NOT EXISTS idx_ep_pilot ON eligibility_papers(in_pilot_e0);
CREATE INDEX IF NOT EXISTS idx_ms_bucket ON math_structure(e1_bucket);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_eligibility(db_path: Path = DEFAULT_ELIGIBILITY_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA)
    return conn


# ---------------------------------------------------------------------------
# Environment classification & deterministic domain cue patterns
# ---------------------------------------------------------------------------

_ENV_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("theorem", re.compile(r"^(?:main\s+)?(?:theorem|thm)\b", re.I)),
    ("lemma", re.compile(r"^(?:key\s+|main\s+)?(?:lemma|lem)\b", re.I)),
    ("proposition", re.compile(r"^(?:proposition|prop)\b", re.I)),
    ("corollary", re.compile(r"^(?:corollary|cor)\b", re.I)),
    ("claim_or_fact", re.compile(r"^(?:claim|fact|observation|sublemma)\b", re.I)),
    ("conjecture", re.compile(r"^(?:conjecture|conj)\b", re.I)),
    ("definition", re.compile(r"^(?:definition|defn|def)\b", re.I)),
    ("assumption", re.compile(r"^(?:assumption|assump|hypothesis|condition|standing\s+assumption)\b", re.I)),
    ("property_or_invariant", re.compile(r"^(?:property|invariant|requirement|guarantee|specification|safety|liveness|security)\b", re.I)),
    ("remark_or_example", re.compile(r"^(?:remark|rem|example|ex|note|problem|question|algorithm|notation)\b", re.I)),
]

_CLASS_SUFFIX_MAP: list[tuple[str, re.Pattern[str]]] = [
    ("theorem", re.compile(r"^ltx_theorem_(?:main)?(?:theorem|thm|teo)s?$", re.I)),
    ("lemma", re.compile(r"^ltx_theorem_(?:lemma|lem)s?$", re.I)),
    ("proposition", re.compile(r"^ltx_theorem_(?:proposition|prop)s?$", re.I)),
    ("corollary", re.compile(r"^ltx_theorem_(?:corollary|cor)s?$", re.I)),
    ("claim_or_fact", re.compile(r"^ltx_theorem_(?:claim|fact|obs|observation)s?$", re.I)),
    ("conjecture", re.compile(r"^ltx_theorem_(?:conjecture|conj)s?$", re.I)),
    ("definition", re.compile(r"^ltx_theorem_(?:definition|defn|def)s?$", re.I)),
    ("assumption", re.compile(r"^ltx_theorem_(?:assumption|assump|hyp|hypothesis|cond)s?$", re.I)),
    ("property_or_invariant", re.compile(r"^ltx_theorem_(?:property|invariant|spec|safety|liveness)s?$", re.I)),
    ("remark_or_example", re.compile(r"^ltx_theorem_(?:remark|rem|example|ex|note|problem|alg|notation)s?$", re.I)),
]

_THEORY_HEADING_RE = re.compile(
    r"\b(?:theoretical\s+(?:analysis|results?|guarantees?|foundations?)|"
    r"convergence\s+analysis|main\s+(?:results?|theorems?)|"
    r"mathematical\s+(?:analysis|formulation|preliminaries)|"
    r"stability\s+analysis|regret\s+analysis|error\s+(?:analysis|bounds?)|"
    r"security\s+(?:analysis|proofs?)|correctness\s+(?:analysis|proofs?)|"
    r"proofs?\s+of|omitted\s+proofs?|technical\s+proofs?|formal\s+analysis)\b",
    re.I,
)

_APPENDIX_PROOF_RE = re.compile(
    r"\b(?:appendix|supplementary|omitted\s+proofs?|proof\s+of\s+(?:theorem|lemma|proposition))\b",
    re.I,
)

# Zero-token domain barrier & tractability cues (informational features for E1/E2)
DOMAIN_CUE_REGEXES: dict[str, dict[str, re.Pattern[str]]] = {
    "mathlib_barrier_cues": {
        "pde_sobolev": re.compile(r"\b(?:Navier[- ]Stokes|Sobolev\s+space|weak\s+solution|elliptic\s+PDE|parabolic\s+PDE|hyperbolic\s+PDE|Euler\s+equations?|Boltzmann\s+equation|Burgers\s+equation|Galerkin|H\^\{?[12]\}?\s*norm)\b", re.I),
        "stochastic_sde_ito": re.compile(r"\b(?:It[oô]\s+(?:calculus|lemma|integral|formula)|stochastic\s+differential\s+equation|Fokker[- ]Planck|Brownian\s+motion|Wiener\s+process|martingale\s+central\s+limit|SPDE|McKean[- ]Vlasov)\b", re.I),
        "viscosity_hjb": re.compile(r"\b(?:Hamilton[- ]Jacobi[- ]Bellman|viscosity\s+solution|Pontryagin\s+maximum\s+principle)\b", re.I),
        "random_matrix_heavy": re.compile(r"\b(?:Marchenko[- ]Pastur|Stieltjes\s+transform|free\s+probability|random\s+matrix\s+theory|replica\s+method)\b", re.I),
    },
    "tractable_math_cues": {
        "optimization_bounds": re.compile(r"\b(?:convex\s+optimization|strongly\s+convex|Lipschitz\s+gradient|regret\s+bound|convergence\s+rate|sublinear\s+regret|mirror\s+descent|saddle\s+point|KKT\s+conditions?|duality\s+gap)\b", re.I),
        "game_mech_discrete": re.compile(r"\b(?:Nash\s+equilibrium|incentive\s+compatib|truthful\s+mechanism|envy[- ]free|competitive\s+ratio|approximation\s+ratio|NP[- ]hard|query\s+complexity|matroid|submodular)\b", re.I),
        "info_coding_crypto": re.compile(r"\b(?:channel\s+capacity|mutual\s+information|error[- ]correcting\s+code|LDPC|polar\s+code|Reed[- ]Solomon|Cram[eé]r[- ]Rao|IND[- ]CPA|zero[- ]knowledge|learning\s+with\s+errors)\b", re.I),
        "control_lyapunov_lmi": re.compile(r"\b(?:Lyapunov\s+function|control\s+barrier\s+function|linear\s+matrix\s+inequality|LQR|MPC|asymptotically\s+stable|exponentially\s+stable|input[- ]to[- ]state\s+stabil)\b", re.I),
    },
    "operational_fv_cues": {
        "protocol_state_machine": re.compile(r"\b(?:state\s+machine|bisimulation|operational\s+semantics|type\s+safety|memory\s+safety|linearizabil|Byzantine\s+fault|consensus\s+protocol|crash\s+consisten|model\s+check|symbolic\s+execution|TLA\+|ProVerif|Tamarin|Coq|Isabelle|Dafny|Z3)\b", re.I),
    },
}


def classify_theorem_env(title_text: str, classes: list[str]) -> str:
    """Classify a LaTeXML `ltx_theorem` block into a canonical bucket."""
    cleaned = re.sub(r"\s+", " ", title_text).strip()
    for bucket, pat in _ENV_PATTERNS:
        if pat.match(cleaned):
            return bucket
    for cls in classes:
        for bucket, pat in _CLASS_SUFFIX_MAP:
            if pat.match(cls):
                return bucket
    return "other_env"


def _scan_domain_cues(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for group, pats in DOMAIN_CUE_REGEXES.items():
        hits = [name for name, pat in pats.items() if pat.search(text)]
        if hits:
            out[group] = hits
    return out


# ---------------------------------------------------------------------------
# LaTeXML HTML5 Structural Parser
# ---------------------------------------------------------------------------

class _LaTeXMLStructureParser(HTMLParser):
    """Extracts theorem/proof/equation counts, headings, and clean snippets from arXiv HTML5."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._stack: list[tuple[str, set[str]]] = []
        self._skip_depth = 0  # script, style, svg, nav, bibliography
        self._in_math_depth = 0
        self._in_tex_annotation = False

        # Active block capture
        self._active_thm_depth: int | None = None
        self._active_thm_classes: list[str] = []
        self._active_thm_title_depth: int | None = None
        self._active_thm_title_buf: list[str] = []
        self._active_thm_body_buf: list[str] = []

        self._active_proof_depth: int | None = None
        self._active_proof_chars = 0

        self._active_heading_depth: int | None = None
        self._active_heading_buf: list[str] = []

        # Collected metrics
        self.env_counts: Counter[str] = Counter()
        self.n_proof = 0
        self.proof_chars = 0
        self.n_equation = 0
        self.n_display_math = 0
        self.text_chunks: list[str] = []
        self.section_headings: list[str] = []
        self.theorem_blocks: list[dict[str, str]] = []

    def _current_depth(self) -> int:
        return len(self._stack)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        cls_str = attr_map.get("class") or ""
        cls_list = cls_str.split()
        cls_set = set(cls_list)
        self._stack.append((tag, cls_set))
        depth = self._current_depth()

        # Skip boilerplate/noise trees
        if tag in ("script", "style", "svg", "nav") or "ltx_bibliography" in cls_set or "ltx_TOC" in cls_set:
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return

        # MathML handling: keep clean TeX from <annotation encoding="application/x-tex">
        if tag == "math":
            self._in_math_depth += 1
            if attr_map.get("display") == "block":
                self.n_display_math += 1
            return
        if self._in_math_depth > 0:
            if tag == "annotation" and "tex" in (attr_map.get("encoding") or "").lower():
                self._in_tex_annotation = True
                self._emit_text(" $")
            return

        # Equations
        if "ltx_equation" in cls_set or "ltx_equationgroup" in cls_set:
            self.n_equation += 1

        # Section headings (not theorem/proof titles)
        if (
            self._active_heading_depth is None
            and self._active_thm_depth is None
            and (
                "ltx_title_section" in cls_set
                or "ltx_title_subsection" in cls_set
                or "ltx_title_appendix" in cls_set
            )
        ):
            self._active_heading_depth = depth
            self._active_heading_buf = []

        # Theorem-like environments (outermost only)
        if self._active_thm_depth is None and "ltx_theorem" in cls_set:
            self._active_thm_depth = depth
            self._active_thm_classes = cls_list
            self._active_thm_title_buf = []
            self._active_thm_body_buf = []

        if self._active_thm_depth is not None and self._active_thm_title_depth is None:
            if "ltx_title_theorem" in cls_set or "ltx_tag_theorem" in cls_set:
                self._active_thm_title_depth = depth

        # Proof environments
        if self._active_proof_depth is None and "ltx_proof" in cls_set:
            self._active_proof_depth = depth
            self._active_proof_chars = 0
            self.n_proof += 1

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        depth = self._current_depth()
        popped_tag, cls_set = self._stack.pop()

        if popped_tag in ("script", "style", "svg", "nav") or "ltx_bibliography" in cls_set or "ltx_TOC" in cls_set:
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return
        if self._skip_depth > 0:
            return

        if popped_tag == "annotation" and self._in_tex_annotation:
            self._emit_text("$ ")
            self._in_tex_annotation = False
            return
        if popped_tag == "math" and self._in_math_depth > 0:
            self._in_math_depth -= 1
            return
        if self._in_math_depth > 0:
            return

        if self._active_heading_depth == depth:
            heading = re.sub(r"\s+", " ", "".join(self._active_heading_buf)).strip()
            if heading and len(self.section_headings) < 60:
                self.section_headings.append(heading[:140])
            self._active_heading_depth = None

        if self._active_thm_title_depth == depth:
            self._active_thm_title_depth = None

        if self._active_thm_depth == depth:
            title_txt = re.sub(r"\s+", " ", "".join(self._active_thm_title_buf)).strip()
            body_txt = re.sub(r"\s+", " ", "".join(self._active_thm_body_buf)).strip()
            env_kind = classify_theorem_env(title_txt or body_txt[:40], self._active_thm_classes)
            self.env_counts[env_kind] += 1
            if env_kind in ("theorem", "proposition", "lemma", "corollary", "claim_or_fact", "property_or_invariant", "definition"):
                if len(self.theorem_blocks) < 25:
                    snippet = body_txt[:480]
                    if title_txt and not snippet.startswith(title_txt[:15]):
                        snippet = f"{title_txt} {snippet}".strip()[:480]
                    self.theorem_blocks.append({"kind": env_kind, "text": snippet})
            self._active_thm_depth = None

        if self._active_proof_depth == depth:
            self.proof_chars += self._active_proof_chars
            self._active_proof_depth = None

        if popped_tag in ("p", "div", "section", "li", "br", "tr"):
            self._emit_text("\n")

    def _emit_text(self, text: str) -> None:
        self.text_chunks.append(text)
        if self._active_heading_depth is not None:
            self._active_heading_buf.append(text)
        if self._active_thm_title_depth is not None:
            self._active_thm_title_buf.append(text)
        if self._active_thm_depth is not None:
            self._active_thm_body_buf.append(text)
        if self._active_proof_depth is not None:
            self._active_proof_chars += len(text)

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_math_depth > 0 and not self._in_tex_annotation:
            return
        self._emit_text(data)


def parse_html_structure(raw_html: str) -> dict[str, Any]:
    parser = _LaTeXMLStructureParser()
    parser.feed(raw_html)
    full_text = re.sub(r"[ \t]+", " ", "".join(parser.text_chunks))
    full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()
    return _finalize_structure(
        env_counts=parser.env_counts,
        n_proof=parser.n_proof,
        proof_chars=parser.proof_chars,
        n_equation=parser.n_equation,
        n_display_math=parser.n_display_math,
        section_headings=parser.section_headings,
        theorem_blocks=parser.theorem_blocks,
        full_text=full_text,
    )


# ---------------------------------------------------------------------------
# PDF Fallback Structural Parser (for ~6% non-HTML5 papers)
# ---------------------------------------------------------------------------

_PDF_ENV_LINE_RE = re.compile(
    r"(?m)^[ \t]*(Theorem|Proposition|Lemma|Corollary|Claim|Fact|Conjecture|Definition|Assumption|Property|Invariant|Remark|Example)"
    r"[ \t]+(?:\d+(?:\.\d+)*|[A-Z](?:\.\d+)*|[IVX]+)?[ \t]*(?:\([^)\n]{1,80}\))?[ \t]*[.:]"
)
_PDF_PROOF_LINE_RE = re.compile(
    r"(?m)^[ \t]*(?:Proof|Sketch\s+of\s+Proof|Proof\s+Sketch|Proof\s+of\s+(?:Theorem|Proposition|Lemma|Corollary)\b[^.\n]{0,40})[ \t]*[.:]"
)
_PDF_SECTION_LINE_RE = re.compile(
    r"(?m)^[ \t]*(?:[1-9]\d*(?:\.\d+)?|[A-Z](?:\.\d+)?)[ \t]+([A-Z][A-Za-z0-9 ,:/\-]{3,90})[ \t]*$"
)
_PDF_EQNO_RE = re.compile(r"(?m)\(\d+(?:\.\d+)?\)[ \t]*$")


def parse_pdf_structure(raw_pdf: bytes) -> dict[str, Any]:
    reader = PdfReader(io.BytesIO(raw_pdf))
    parts: list[str] = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
            if txt:
                parts.append(txt)
        except Exception:
            pass
    full_text = "\n".join(parts)

    env_counts: Counter[str] = Counter()
    theorem_blocks: list[dict[str, str]] = []
    for m in _PDF_ENV_LINE_RE.finditer(full_text):
        label = m.group(1)
        kind = classify_theorem_env(label, [])
        env_counts[kind] += 1
        if kind in ("theorem", "proposition", "lemma", "corollary", "claim_or_fact", "property_or_invariant", "definition"):
            if len(theorem_blocks) < 20:
                snippet = re.sub(r"\s+", " ", full_text[m.start() : m.start() + 480]).strip()
                theorem_blocks.append({"kind": kind, "text": snippet})

    proof_matches = list(_PDF_PROOF_LINE_RE.finditer(full_text))
    n_proof = len(proof_matches)
    # Approximate proof chars (up to 1500 chars per proof block)
    proof_chars = sum(min(1500, max(100, len(full_text) - m.start())) for m in proof_matches)

    n_equation = len(_PDF_EQNO_RE.findall(full_text))
    section_headings: list[str] = []
    for m in _PDF_SECTION_LINE_RE.finditer(full_text):
        h = m.group(1).strip()
        if len(h) <= 100 and len(section_headings) < 60:
            section_headings.append(h)

    return _finalize_structure(
        env_counts=env_counts,
        n_proof=n_proof,
        proof_chars=proof_chars,
        n_equation=n_equation,
        n_display_math=n_equation,
        section_headings=section_headings,
        theorem_blocks=theorem_blocks,
        full_text=full_text,
    )


def _select_representative_snippets(theorem_blocks: list[dict[str, str]], max_items: int = 4) -> list[str]:
    """Pick up to `max_items` representative claim snippets, prioritizing Theorem > Prop > Lemma > Cor > Property > Def."""
    priority = {
        "theorem": 0,
        "proposition": 1,
        "lemma": 2,
        "corollary": 3,
        "claim_or_fact": 4,
        "property_or_invariant": 5,
        "definition": 6,
    }
    ordered = sorted(
        enumerate(theorem_blocks),
        key=lambda pair: (priority.get(pair[1]["kind"], 9), pair[0]),
    )
    selected: list[str] = []
    for _, blk in ordered:
        txt = blk["text"].strip()
        if txt and txt not in selected:
            selected.append(txt[:450])
        if len(selected) >= max_items:
            break
    return selected


def _finalize_structure(
    env_counts: Counter[str],
    n_proof: int,
    proof_chars: int,
    n_equation: int,
    n_display_math: int,
    section_headings: list[str],
    theorem_blocks: list[dict[str, str]],
    full_text: str,
) -> dict[str, Any]:
    n_theorem = env_counts["theorem"]
    n_lemma = env_counts["lemma"]
    n_proposition = env_counts["proposition"]
    n_corollary = env_counts["corollary"]
    n_claim_or_fact = env_counts["claim_or_fact"]
    n_conjecture = env_counts["conjecture"]
    n_definition = env_counts["definition"]
    n_assumption = env_counts["assumption"]
    n_remark_or_example = env_counts["remark_or_example"]
    n_property_or_invariant = env_counts["property_or_invariant"]
    n_other_env = env_counts["other_env"]

    n_core_claims = n_theorem + n_proposition + n_lemma + n_corollary + n_claim_or_fact
    headings_blob = " | ".join(section_headings)
    has_theory_section = int(bool(_THEORY_HEADING_RE.search(headings_blob)))
    has_appendix_proofs = int(bool(_APPENDIX_PROOF_RE.search(headings_blob)))
    domain_cues = _scan_domain_cues(full_text)
    has_opfv_cue = bool(domain_cues.get("operational_fv_cues"))

    if (n_core_claims >= 1 and n_proof >= 1) or (n_core_claims >= 2):
        e1_bucket = "E1_formal_thm_proof"
    elif (
        n_core_claims == 1
        or n_proof >= 1
        or n_property_or_invariant >= 1
        or has_theory_section
        or has_opfv_cue
        or n_equation >= 15
    ):
        e1_bucket = "E1_weak_or_unnumbered_math"
    else:
        e1_bucket = "E1_no_formal_claims"

    rep_snippets = _select_representative_snippets(theorem_blocks, max_items=4)

    # Build compact evidence snippet (<=2,400 chars) for E2 LLM
    parts: list[str] = []
    if section_headings:
        parts.append("SECTIONS: " + " ; ".join(section_headings[:16]))
    if rep_snippets:
        parts.append("CLAIMS:\n" + "\n---\n".join(rep_snippets))
    elif full_text:
        # Grab a short middle excerpt when no theorem environments exist (helps detect unnumbered proofs / op-FV)
        mid = max(0, min(len(full_text) // 4, len(full_text) - 900))
        excerpt = re.sub(r"\s+", " ", full_text[mid : mid + 900]).strip()
        parts.append("BODY_EXCERPT: " + excerpt)
    evidence_snippet = "\n\n".join(parts)[:2400]

    return {
        "text_chars": len(full_text),
        "n_theorem": n_theorem,
        "n_lemma": n_lemma,
        "n_proposition": n_proposition,
        "n_corollary": n_corollary,
        "n_claim_or_fact": n_claim_or_fact,
        "n_conjecture": n_conjecture,
        "n_definition": n_definition,
        "n_assumption": n_assumption,
        "n_remark_or_example": n_remark_or_example,
        "n_property_or_invariant": n_property_or_invariant,
        "n_other_env": n_other_env,
        "n_proof": n_proof,
        "proof_chars": proof_chars,
        "n_equation": n_equation,
        "n_display_math": n_display_math,
        "has_theory_section": has_theory_section,
        "has_appendix_proofs": has_appendix_proofs,
        "e1_bucket": e1_bucket,
        "section_headings": section_headings[:30],
        "domain_cues": domain_cues,
        "theorem_snippets": rep_snippets,
        "evidence_snippet": evidence_snippet,
    }


# ---------------------------------------------------------------------------
# Polite HTTP Fetcher (same discipline as src/fetch_and_screen.py)
# ---------------------------------------------------------------------------

class _RateLimiter:
    def __init__(self, min_interval: float) -> None:
        self._lock = threading.Lock()
        self._min_interval = min_interval
        self._next_ok = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_ok:
                sleep_for = self._next_ok - now
                self._next_ok += self._min_interval
            else:
                sleep_for = 0.0
                self._next_ok = now + self._min_interval
        if sleep_for > 0:
            time.sleep(sleep_for)

    def backoff(self, seconds: float) -> None:
        with self._lock:
            target = time.monotonic() + seconds
            if target > self._next_ok:
                self._next_ok = target


def _polite_get(client: httpx.Client, limiter: _RateLimiter, url: str) -> httpx.Response:
    for attempt in range(4):
        limiter.wait()
        try:
            resp = client.get(url, follow_redirects=True)
            if resp.status_code in (429, 503):
                retry_after = float(resp.headers.get("Retry-After", 10 * (attempt + 1)))
                print(f"  [backoff {retry_after:.0f}s] status={resp.status_code} url={url}", flush=True)
                limiter.backoff(retry_after)
                continue
            return resp
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Exhausted retries for {url}")


def fetch_and_extract_one(
    client: httpx.Client,
    limiter: _RateLimiter,
    row: dict[str, Any],
) -> dict[str, Any]:
    arxiv_id = row["arxiv_id"]
    version = int(row["version"])
    html_url = f"https://arxiv.org/html/{arxiv_id}v{version}"
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}v{version}"

    fetch_source = "failed"
    http_status: int | None = None
    error_msg: str | None = None
    parsed: dict[str, Any] | None = None

    try:
        r = _polite_get(client, limiter, html_url)
        http_status = r.status_code
        ctype = r.headers.get("content-type", "").lower()
        if r.status_code == 200 and "html" in ctype and len(r.text) > 1500 and "No HTML for" not in r.text[:1000]:
            cand = parse_html_structure(r.text)
            if cand["text_chars"] >= 800:
                parsed = cand
                fetch_source = "html"
    except Exception as exc:
        error_msg = f"html:{exc}"

    if parsed is None:
        try:
            r_pdf = _polite_get(client, limiter, pdf_url)
            http_status = r_pdf.status_code
            ctype = r_pdf.headers.get("content-type", "").lower()
            if r_pdf.status_code == 200 and ("pdf" in ctype or r_pdf.content[:4] == b"%PDF"):
                parsed = parse_pdf_structure(r_pdf.content)
                fetch_source = "pdf"
                error_msg = None
            else:
                error_msg = f"pdf_status={r_pdf.status_code}"
        except Exception as exc:
            error_msg = f"pdf:{exc}"

    if parsed is None:
        parsed = {
            "text_chars": 0,
            "n_theorem": 0,
            "n_lemma": 0,
            "n_proposition": 0,
            "n_corollary": 0,
            "n_claim_or_fact": 0,
            "n_conjecture": 0,
            "n_definition": 0,
            "n_assumption": 0,
            "n_remark_or_example": 0,
            "n_property_or_invariant": 0,
            "n_other_env": 0,
            "n_proof": 0,
            "proof_chars": 0,
            "n_equation": 0,
            "n_display_math": 0,
            "has_theory_section": 0,
            "has_appendix_proofs": 0,
            "e1_bucket": "E1_fetch_failed",
            "section_headings": [],
            "domain_cues": {},
            "theorem_snippets": [],
            "evidence_snippet": "",
        }

    return {
        "arxiv_id": arxiv_id,
        "version": version,
        "fetch_source": fetch_source,
        "http_status": http_status,
        "error_msg": error_msg,
        **parsed,
    }


def upsert_math_structure(conn: sqlite3.Connection, res: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO math_structure (
            arxiv_id, version, fetch_source, http_status, error_msg, text_chars,
            n_theorem, n_lemma, n_proposition, n_corollary, n_claim_or_fact,
            n_conjecture, n_definition, n_assumption, n_remark_or_example,
            n_property_or_invariant, n_other_env, n_proof, proof_chars,
            n_equation, n_display_math, has_theory_section, has_appendix_proofs,
            e1_bucket, section_headings_json, domain_cues_json,
            theorem_snippets_json, evidence_snippet, extracted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            version = excluded.version,
            fetch_source = excluded.fetch_source,
            http_status = excluded.http_status,
            error_msg = excluded.error_msg,
            text_chars = excluded.text_chars,
            n_theorem = excluded.n_theorem,
            n_lemma = excluded.n_lemma,
            n_proposition = excluded.n_proposition,
            n_corollary = excluded.n_corollary,
            n_claim_or_fact = excluded.n_claim_or_fact,
            n_conjecture = excluded.n_conjecture,
            n_definition = excluded.n_definition,
            n_assumption = excluded.n_assumption,
            n_remark_or_example = excluded.n_remark_or_example,
            n_property_or_invariant = excluded.n_property_or_invariant,
            n_other_env = excluded.n_other_env,
            n_proof = excluded.n_proof,
            proof_chars = excluded.proof_chars,
            n_equation = excluded.n_equation,
            n_display_math = excluded.n_display_math,
            has_theory_section = excluded.has_theory_section,
            has_appendix_proofs = excluded.has_appendix_proofs,
            e1_bucket = excluded.e1_bucket,
            section_headings_json = excluded.section_headings_json,
            domain_cues_json = excluded.domain_cues_json,
            theorem_snippets_json = excluded.theorem_snippets_json,
            evidence_snippet = excluded.evidence_snippet,
            extracted_at = excluded.extracted_at
        """,
        (
            res["arxiv_id"],
            res["version"],
            res["fetch_source"],
            res.get("http_status"),
            res.get("error_msg"),
            res["text_chars"],
            res["n_theorem"],
            res["n_lemma"],
            res["n_proposition"],
            res["n_corollary"],
            res["n_claim_or_fact"],
            res["n_conjecture"],
            res["n_definition"],
            res["n_assumption"],
            res["n_remark_or_example"],
            res["n_property_or_invariant"],
            res["n_other_env"],
            res["n_proof"],
            res["proof_chars"],
            res["n_equation"],
            res["n_display_math"],
            res["has_theory_section"],
            res["has_appendix_proofs"],
            res["e1_bucket"],
            json.dumps(res["section_headings"]),
            json.dumps(res["domain_cues"]),
            json.dumps(res["theorem_snippets"]),
            res["evidence_snippet"],
            utc_now(),
        ),
    )


# ---------------------------------------------------------------------------
# DB Initialization & Stratified Sampling
# ---------------------------------------------------------------------------

def init_eligibility_db(
    db_path: Path = DEFAULT_ELIGIBILITY_DB,
    panel_path: Path = UNIFIED_PANEL_PATH,
    pilot_per_cat: int = 3,
    seed: int = 20261125,
) -> dict[str, int]:
    """Build `eligibility_papers` from existing T2 DBs + 82 confirmed Lean positive controls."""
    panel = json.loads(panel_path.read_text())
    confirmed_by_id = {p["arxiv_id"]: p for p in panel["confirmed_papers"]}
    all15_set = set(ALL15_CATS)

    # Gather all T2 papers from survey.db + scout_eng_tier12_2026_11.db
    papers: dict[str, dict[str, Any]] = {}
    for src_db in SOURCE_DBS_T2:
        con = sqlite3.connect(str(src_db))
        con.row_factory = sqlite3.Row
        for r in con.execute(
            "SELECT arxiv_id, version, title, abstract, primary_category, all_categories_json, submitted_date, comment FROM papers"
        ):
            aid = r["arxiv_id"]
            all_cats = set(json.loads(r["all_categories_json"] or "[]"))
            all_cats.add(r["primary_category"])
            if aid in papers:
                prev_cats = set(papers[aid]["all_categories"])
                merged = sorted(prev_cats | all_cats)
                papers[aid]["all_categories"] = merged
                papers[aid]["matched_15_cats"] = sorted(set(merged) & all15_set)
                papers[aid]["version"] = max(papers[aid]["version"], int(r["version"]))
            else:
                matched = sorted(all_cats & all15_set)
                papers[aid] = {
                    "arxiv_id": aid,
                    "version": int(r["version"]),
                    "slice_id": "2026-11",
                    "title": r["title"],
                    "abstract": r["abstract"],
                    "primary_category": r["primary_category"],
                    "all_categories": sorted(all_cats),
                    "matched_15_cats": matched,
                    "submitted_date": r["submitted_date"],
                    "comment": r["comment"],
                    "in_t2_census": 1,
                }
        con.close()

    # Add any T0/T1 confirmed Lean positive controls not already in T2
    missing_confirmed = set(confirmed_by_id.keys()) - set(papers.keys())
    if missing_confirmed:
        for src_db in SOURCE_DBS_ALL:
            if not src_db.exists():
                continue
            con = sqlite3.connect(str(src_db))
            con.row_factory = sqlite3.Row
            placeholders = ",".join("?" for _ in missing_confirmed)
            for r in con.execute(
                f"SELECT arxiv_id, version, title, abstract, primary_category, all_categories_json, submitted_date, comment "
                f"FROM papers WHERE arxiv_id IN ({placeholders})",
                tuple(missing_confirmed),
            ):
                aid = r["arxiv_id"]
                if aid in papers:
                    continue
                cp = confirmed_by_id[aid]
                all_cats = sorted(set(json.loads(r["all_categories_json"] or "[]")) | {r["primary_category"]})
                papers[aid] = {
                    "arxiv_id": aid,
                    "version": int(cp.get("version") or r["version"]),
                    "slice_id": cp["slice_id"],
                    "title": r["title"],
                    "abstract": r["abstract"],
                    "primary_category": r["primary_category"],
                    "all_categories": all_cats,
                    "matched_15_cats": sorted(set(all_cats) & all15_set),
                    "submitted_date": r["submitted_date"],
                    "comment": r["comment"],
                    "in_t2_census": 0,
                }
            con.close()
            missing_confirmed = set(confirmed_by_id.keys()) - set(papers.keys())
            if not missing_confirmed:
                break

    # Deterministic stratified Pilot E0 sample: 3 random T2 papers per category (preferring non-overlapping draws)
    rng = random.Random(seed)
    pilot_strata: dict[str, str] = {}
    for cat in ALL15_CATS:
        pool = sorted(
            aid
            for aid, p in papers.items()
            if p["in_t2_census"] == 1 and cat in p["matched_15_cats"] and aid not in pilot_strata
        )
        picks = rng.sample(pool, min(pilot_per_cat, len(pool)))
        for aid in picks:
            pilot_strata[aid] = cat

    conn = connect_eligibility(db_path)
    with conn:
        for aid, p in papers.items():
            cp = confirmed_by_id.get(aid)
            in_pilot = 1 if (aid in pilot_strata or cp is not None) else 0
            conn.execute(
                """
                INSERT INTO eligibility_papers (
                    arxiv_id, version, slice_id, title, abstract, primary_category,
                    all_categories_json, matched_15_cats_json, submitted_date, comment,
                    in_t2_census, is_confirmed_lean, confirmed_role_4way, confirmed_slice_id,
                    in_pilot_e0, pilot_strata_cat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    version = excluded.version,
                    matched_15_cats_json = excluded.matched_15_cats_json,
                    in_t2_census = excluded.in_t2_census,
                    is_confirmed_lean = excluded.is_confirmed_lean,
                    confirmed_role_4way = excluded.confirmed_role_4way,
                    confirmed_slice_id = excluded.confirmed_slice_id,
                    in_pilot_e0 = excluded.in_pilot_e0,
                    pilot_strata_cat = excluded.pilot_strata_cat
                """,
                (
                    aid,
                    p["version"],
                    p["slice_id"],
                    p["title"],
                    p["abstract"],
                    p["primary_category"],
                    json.dumps(p["all_categories"]),
                    json.dumps(p["matched_15_cats"]),
                    p["submitted_date"],
                    p["comment"],
                    p["in_t2_census"],
                    1 if cp is not None else 0,
                    cp["role_4way"] if cp is not None else None,
                    cp["slice_id"] if cp is not None else None,
                    in_pilot,
                    pilot_strata.get(aid),
                ),
            )
    conn.close()

    n_t2 = sum(1 for p in papers.values() if p["in_t2_census"] == 1)
    n_conf = sum(1 for aid in papers if aid in confirmed_by_id)
    n_pilot_total = sum(1 for aid in papers if aid in pilot_strata or aid in confirmed_by_id)
    return {
        "total_rows": len(papers),
        "t2_census": n_t2,
        "confirmed_lean_controls": n_conf,
        "pilot_random_t2": len(pilot_strata),
        "pilot_e0_unique_total": n_pilot_total,
    }


def run_fetch(
    db_path: Path = DEFAULT_ELIGIBILITY_DB,
    cohort: str = "pilot_e0",
    workers: int = 3,
    min_interval: float = 0.4,
    limit: int | None = None,
    retry_failed: bool = False,
) -> None:
    conn = connect_eligibility(db_path)
    cohort_where = "ep.in_pilot_e0 = 1" if cohort == "pilot_e0" else "ep.in_t2_census = 1"
    status_where = "(ms.arxiv_id IS NULL OR ms.fetch_source = 'failed')" if retry_failed else "ms.arxiv_id IS NULL"
    sql = f"""
        SELECT ep.arxiv_id, ep.version, ep.primary_category
        FROM eligibility_papers ep
        LEFT JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
        WHERE {cohort_where} AND {status_where}
        ORDER BY ep.arxiv_id ASC
    """
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    if limit is not None:
        rows = rows[:limit]
    total = len(rows)
    if total == 0:
        print(f"Cohort '{cohort}' already fetched.")
        conn.close()
        return

    print(f"Fetching math structure for {total} papers (cohort={cohort}, workers={workers}, min_interval={min_interval}s)...", flush=True)
    limiter = _RateLimiter(min_interval=min_interval)
    t0 = time.monotonic()
    counts: Counter[str] = Counter()
    done = 0

    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(30.0, connect=15.0),
        limits=httpx.Limits(max_connections=workers + 2, max_keepalive_connections=workers),
    ) as client:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(fetch_and_extract_one, client, limiter, r) for r in rows]
            for fut in as_completed(futs):
                res = fut.result()
                with conn:
                    upsert_math_structure(conn, res)
                done += 1
                counts[res["fetch_source"]] += 1
                counts[res["e1_bucket"]] += 1
                if done % 25 == 0 or done == total:
                    elapsed = time.monotonic() - t0
                    rate = done / max(elapsed, 0.1)
                    eta = (total - done) / max(rate, 0.01) / 60.0
                    print(
                        f"Progress {done}/{total} ({rate:.2f}/s, ETA {eta:.1f}m) | "
                        f"html={counts['html']} pdf={counts['pdf']} fail={counts['failed']} | "
                        f"formal={counts['E1_formal_thm_proof']} weak={counts['E1_weak_or_unnumbered_math']} "
                        f"none={counts['E1_no_formal_claims']}",
                        flush=True,
                    )
    conn.close()
    print(f"Finished cohort '{cohort}' ({total} papers) in {(time.monotonic() - t0)/60.0:.2f} min.", flush=True)


# ---------------------------------------------------------------------------
# Export E2 Inputs & Import/Summarize E2 Outputs
# ---------------------------------------------------------------------------

def compute_neyman_3stratum_plan(
    all_rows: list[dict[str, Any]],
    per_cat_budget: int = 30,
    cap_none: int = 4,
    min_formal: int = 10,
    min_weak: int = 6,
    seed_prefix: str = "e2_20261126",
) -> dict[str, Any]:
    """Build an unbiased independent per-category 3-stratum SRS plan with Neyman allocation.

    Within each of the 15 categories, draws independent SRS samples from the three fetched
    E1 strata (`E1_formal_thm_proof`, `E1_weak_or_unnumbered_math`, `E1_no_formal_claims`):
      - `E1_no_formal_claims`: fixed audit floor `min(cap_none, N_N)`
      - `E1_formal_thm_proof` / `E1_weak_or_unnumbered_math`: floors `min(min_formal, N_F)`
        and `min(min_weak, N_W)`, with remaining slots up to `per_cat_budget` allocated
        greedily by marginal finite-population-corrected Neyman variance reduction
        (conservative within-stratum SDs: 0.50 for formal, 0.40 for weak).

    Cross-listed papers are sampled independently per category (zero ordering bias) and
    deduplicated in `unique_ids` before LLM dispatch.
    """
    strata_keys = (
        ("E1_formal_thm_proof", "formal"),
        ("E1_weak_or_unnumbered_math", "weak"),
        ("E1_no_formal_claims", "none"),
    )
    sds = {"E1_formal_thm_proof": 0.50, "E1_weak_or_unnumbered_math": 0.40}
    per_cat_plan: dict[str, dict[str, Any]] = {}
    unique_ids: set[str] = set()

    for cat in ALL15_CATS:
        in_cat = [r for r in all_rows if cat in json.loads(r["matched_15_cats_json"])]
        pools = {
            b: sorted(r["arxiv_id"] for r in in_cat if r["e1_bucket"] == b)
            for b, _ in strata_keys
        }
        n_tot = len(in_cat)
        alloc = {
            "E1_formal_thm_proof": min(min_formal, len(pools["E1_formal_thm_proof"])),
            "E1_weak_or_unnumbered_math": min(min_weak, len(pools["E1_weak_or_unnumbered_math"])),
            "E1_no_formal_claims": min(cap_none, len(pools["E1_no_formal_claims"])),
        }
        target_tot = min(per_cat_budget, n_tot)
        while sum(alloc.values()) < target_tot:
            best_b = None
            best_gain = -1.0
            for b in ("E1_formal_thm_proof", "E1_weak_or_unnumbered_math"):
                nh_pop = len(pools[b])
                nh = alloc[b]
                if nh >= nh_pop or nh == 0:
                    continue
                wh = nh_pop / max(n_tot, 1)
                v0 = (wh**2) * ((nh_pop - nh) / max(nh_pop - 1, 1)) * (sds[b] ** 2 / nh)
                v1 = (wh**2) * ((nh_pop - nh - 1) / max(nh_pop - 1, 1)) * (sds[b] ** 2 / (nh + 1))
                if (v0 - v1) > best_gain:
                    best_gain = v0 - v1
                    best_b = b
            if best_b is None:
                break
            alloc[best_b] += 1

        cat_strata: dict[str, Any] = {}
        for b, short_k in strata_keys:
            rng = random.Random(f"{seed_prefix}_{cat}_{short_k[0].upper()}")
            picks = sorted(rng.sample(pools[b], alloc[b]))
            unique_ids.update(picks)
            cat_strata[b] = {
                "N_h": len(pools[b]),
                "n_h": len(picks),
                "sampled_ids": picks,
            }
        per_cat_plan[cat] = {
            "N_fetched": n_tot,
            "n_total": sum(alloc.values()),
            "strata": cat_strata,
        }

    return {
        "design": "independent_per_category_3stratum_neyman_srs",
        "per_cat_budget": per_cat_budget,
        "cap_none": cap_none,
        "min_formal": min_formal,
        "min_weak": min_weak,
        "seed_prefix": seed_prefix,
        "total_category_draws": sum(v["n_total"] for v in per_cat_plan.values()),
        "unique_sampled_ids": sorted(unique_ids),
        "per_category": per_cat_plan,
    }


def export_e2_inputs(
    db_path: Path = DEFAULT_ELIGIBILITY_DB,
    cohort: str = "pilot_e0",
    out_path: Path = Path("data/eligibility_pilot_e0_in.json"),
    per_cat_budget: int = 30,
    cap_none: int = 4,
    min_formal: int = 10,
    min_weak: int = 6,
    seed_prefix: str = "e2_20261126",
    skip_cached_model: str | None = "flash",
    plan_out_path: Path | None = None,
) -> dict[str, Any]:
    conn = connect_eligibility(db_path)
    sampling_plan: dict[str, Any] | None = None
    cached_ids: list[str] = []

    if cohort == "pilot_e0":
        rows = conn.execute(
            """
            SELECT ep.*, ms.fetch_source, ms.text_chars, ms.n_theorem, ms.n_lemma,
                   ms.n_proposition, ms.n_corollary, ms.n_claim_or_fact, ms.n_definition,
                   ms.n_assumption, ms.n_property_or_invariant, ms.n_proof, ms.n_equation,
                   ms.has_theory_section, ms.has_appendix_proofs, ms.e1_bucket,
                   ms.domain_cues_json, ms.evidence_snippet
            FROM eligibility_papers ep
            JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
            WHERE ep.in_pilot_e0 = 1
            ORDER BY ep.arxiv_id ASC
            """
        ).fetchall()
        selected_rows = [dict(r) for r in rows]
    elif cohort == "e2_stratified":
        all_rows = [
            dict(r)
            for r in conn.execute(
                """
                SELECT ep.*, ms.fetch_source, ms.text_chars, ms.n_theorem, ms.n_lemma,
                       ms.n_proposition, ms.n_corollary, ms.n_claim_or_fact, ms.n_definition,
                       ms.n_assumption, ms.n_property_or_invariant, ms.n_proof, ms.n_equation,
                       ms.has_theory_section, ms.has_appendix_proofs, ms.e1_bucket,
                       ms.domain_cues_json, ms.evidence_snippet
                FROM eligibility_papers ep
                JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
                WHERE ep.in_t2_census = 1 AND ms.e1_bucket != 'E1_fetch_failed'
                ORDER BY ep.arxiv_id ASC
                """
            ).fetchall()
        ]
        by_id = {r["arxiv_id"]: r for r in all_rows}
        sampling_plan = compute_neyman_3stratum_plan(
            all_rows,
            per_cat_budget=per_cat_budget,
            cap_none=cap_none,
            min_formal=min_formal,
            min_weak=min_weak,
            seed_prefix=seed_prefix,
        )
        already_classified: set[str] = set()
        if skip_cached_model:
            already_classified = {
                r["arxiv_id"]
                for r in conn.execute(
                    "SELECT arxiv_id FROM eligibility_classifications WHERE model_tier = ?",
                    (skip_cached_model,),
                ).fetchall()
            }
        unique_ids = sampling_plan["unique_sampled_ids"]
        cached_ids = [aid for aid in unique_ids if aid in already_classified]
        selected_rows = [by_id[aid] for aid in unique_ids if aid not in already_classified]
        if plan_out_path is not None:
            plan_out_path.parent.mkdir(parents=True, exist_ok=True)
            plan_out_path.write_text(json.dumps(sampling_plan, indent=2) + "\n")
    else:
        raise ValueError(f"Unknown cohort: {cohort}")

    conn.close()

    items = []
    for r in selected_rows:
        # IMPORTANT: Do NOT pass `is_confirmed_lean` or `confirmed_role_4way` to the LLM
        # so positive-control evaluation is strictly blinded!
        items.append(
            {
                "arxiv_id": r["arxiv_id"],
                "title": r["title"],
                "primary_category": r["primary_category"],
                "matched_15_cats": json.loads(r["matched_15_cats_json"]),
                "abstract": r["abstract"][:1800],
                "e1_bucket": r["e1_bucket"],
                "e1_counts": {
                    "theorem": r["n_theorem"],
                    "lemma": r["n_lemma"],
                    "proposition": r["n_proposition"],
                    "corollary": r["n_corollary"],
                    "claim_or_fact": r["n_claim_or_fact"],
                    "definition": r["n_definition"],
                    "assumption": r["n_assumption"],
                    "property_or_invariant": r["n_property_or_invariant"],
                    "proof": r["n_proof"],
                    "equation": r["n_equation"],
                    "has_theory_section": bool(r["has_theory_section"]),
                    "has_appendix_proofs": bool(r["has_appendix_proofs"]),
                },
                "domain_cues": json.loads(r["domain_cues_json"]),
                "evidence_snippet": r["evidence_snippet"],
            }
        )

    payload: dict[str, Any] = {
        "cohort": cohort,
        "generated_at": utc_now(),
        "count": len(items),
        "cached_count": len(cached_ids),
        "cached_ids": cached_ids,
        "items": items,
    }
    if sampling_plan is not None:
        payload["sampling_plan"] = sampling_plan
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    return {
        "cohort": cohort,
        "count": len(items),
        "cached_count": len(cached_ids),
        "unique_total": len(items) + len(cached_ids),
        "out_path": str(out_path),
    }


def import_e2_and_report_pilot(
    db_path: Path,
    in_path: Path,
    cohort: str,
    artifact_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    raw = json.loads(in_path.read_text())
    model_tier = raw.get("model", "flash")
    results = raw["results"]

    conn = connect_eligibility(db_path)
    with conn:
        for r in results:
            conn.execute(
                """
                INSERT INTO eligibility_classifications (
                    arxiv_id, cohort, model_tier, eligibility_class,
                    has_original_deductive_proof, dominant_math_area,
                    primary_barrier_if_L2, confidence, rationale, raw_json, classified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    cohort = excluded.cohort,
                    model_tier = excluded.model_tier,
                    eligibility_class = excluded.eligibility_class,
                    has_original_deductive_proof = excluded.has_original_deductive_proof,
                    dominant_math_area = excluded.dominant_math_area,
                    primary_barrier_if_L2 = excluded.primary_barrier_if_L2,
                    confidence = excluded.confidence,
                    rationale = excluded.rationale,
                    raw_json = excluded.raw_json,
                    classified_at = excluded.classified_at
                """,
                (
                    r["arxiv_id"],
                    cohort,
                    model_tier,
                    r["eligibility_class"],
                    int(bool(r["has_original_deductive_proof"])),
                    r["dominant_math_area"],
                    r["primary_barrier_if_L2"],
                    r["confidence"],
                    r["rationale"],
                    json.dumps(r),
                    utc_now(),
                ),
            )

    rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT ep.arxiv_id, ep.title, ep.primary_category, ep.matched_15_cats_json,
                   ep.in_t2_census, ep.is_confirmed_lean, ep.confirmed_role_4way,
                   ep.confirmed_slice_id, ep.pilot_strata_cat,
                   ms.fetch_source, ms.text_chars, ms.n_theorem, ms.n_lemma,
                   ms.n_proposition, ms.n_corollary, ms.n_claim_or_fact,
                   ms.n_property_or_invariant, ms.n_proof, ms.n_equation, ms.e1_bucket,
                   ec.eligibility_class, ec.has_original_deductive_proof,
                   ec.dominant_math_area, ec.primary_barrier_if_L2,
                   ec.confidence, ec.rationale
            FROM eligibility_papers ep
            JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
            JOIN eligibility_classifications ec ON ep.arxiv_id = ec.arxiv_id
            WHERE ep.in_pilot_e0 = 1
            ORDER BY ep.arxiv_id ASC
            """
        ).fetchall()
    ]
    conn.close()

    # Split into positive controls (82 confirmed Lean) and random T2 stratified sample (45)
    pos_controls = [r for r in rows if r["is_confirmed_lean"] == 1]
    random_t2 = [r for r in rows if r["pilot_strata_cat"] is not None]

    # Positive control breakdown by confirmed_role_4way
    pos_by_role: dict[str, dict[str, int]] = defaultdict(lambda: Counter())
    pos_e1_by_role: dict[str, dict[str, int]] = defaultdict(lambda: Counter())
    pos_mismatches: list[dict[str, Any]] = []
    for r in pos_controls:
        role = r["confirmed_role_4way"] or "unknown"
        cls = r["eligibility_class"]
        pos_by_role[role][cls] += 1
        pos_e1_by_role[role][r["e1_bucket"]] += 1
        expected_ok = (
            (role in ("eng_algorithmic_proof", "pure_math_or_tcs") and cls in ("L1_lean_amenable_math", "L2_mathlib_blocked_math"))
            or (role == "operational_system_fv" and cls in ("L3_operational_spec_fv", "L1_lean_amenable_math"))
            or (role == "meta_formalization_system")
        )
        if not expected_ok:
            pos_mismatches.append(
                {
                    "arxiv_id": r["arxiv_id"],
                    "title": r["title"],
                    "confirmed_role_4way": role,
                    "e1_bucket": r["e1_bucket"],
                    "eligibility_class": cls,
                    "rationale": r["rationale"],
                }
            )

    # E1 bucket vs E2 class confusion matrix across all pilot papers
    e1_vs_e2: dict[str, dict[str, int]] = defaultdict(lambda: Counter())
    for r in rows:
        e1_vs_e2[r["e1_bucket"]][r["eligibility_class"]] += 1

    # Random T2 stratified sample breakdown by category
    rand_by_cat: dict[str, dict[str, int]] = {}
    for cat in ALL15_CATS:
        sub = [r for r in random_t2 if r["pilot_strata_cat"] == cat]
        c = Counter(r["eligibility_class"] for r in sub)
        e1c = Counter(r["e1_bucket"] for r in sub)
        rand_by_cat[cat] = {
            "n": len(sub),
            "e1_formal_thm_proof": e1c["E1_formal_thm_proof"],
            "L1_lean_amenable_math": c["L1_lean_amenable_math"],
            "L2_mathlib_blocked_math": c["L2_mathlib_blocked_math"],
            "L3_operational_spec_fv": c["L3_operational_spec_fv"],
            "L4_heuristic_or_numerical_only": c["L4_heuristic_or_numerical_only"],
            "L5_empirical_or_survey": c["L5_empirical_or_survey"],
        }

    # Sensitivity metrics on positive controls
    eng_ctrl = [r for r in pos_controls if r["confirmed_role_4way"] == "eng_algorithmic_proof"]
    pure_ctrl = [r for r in pos_controls if r["confirmed_role_4way"] == "pure_math_or_tcs"]
    opfv_ctrl = [r for r in pos_controls if r["confirmed_role_4way"] == "operational_system_fv"]
    math_ctrl = eng_ctrl + pure_ctrl

    fetch_counts = Counter(r["fetch_source"] for r in rows)
    rand_class_totals = Counter(r["eligibility_class"] for r in random_t2)
    l2_barriers = Counter(r["primary_barrier_if_L2"] for r in rows if r["eligibility_class"] == "L2_mathlib_blocked_math")

    summary = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "cohort": cohort,
        "model_tier": model_tier,
        "counts": {
            "unique_pilot_papers": len(rows),
            "random_t2_stratified": len(random_t2),
            "confirmed_lean_positive_controls": len(pos_controls),
            "overlap_random_and_confirmed": sum(1 for r in rows if r["is_confirmed_lean"] == 1 and r["pilot_strata_cat"] is not None),
            "fetch_sources": dict(fetch_counts),
        },
        "positive_control_sensitivity": {
            "eng_algorithmic_n": len(eng_ctrl),
            "eng_algorithmic_L1_count": sum(1 for r in eng_ctrl if r["eligibility_class"] == "L1_lean_amenable_math"),
            "eng_algorithmic_L1_or_L2_count": sum(1 for r in eng_ctrl if r["eligibility_class"] in ("L1_lean_amenable_math", "L2_mathlib_blocked_math")),
            "eng_algorithmic_E1_formal_count": sum(1 for r in eng_ctrl if r["e1_bucket"] == "E1_formal_thm_proof"),
            "pure_math_tcs_n": len(pure_ctrl),
            "pure_math_tcs_L1_count": sum(1 for r in pure_ctrl if r["eligibility_class"] == "L1_lean_amenable_math"),
            "pure_math_tcs_L1_or_L2_count": sum(1 for r in pure_ctrl if r["eligibility_class"] in ("L1_lean_amenable_math", "L2_mathlib_blocked_math")),
            "pure_math_tcs_E1_formal_count": sum(1 for r in pure_ctrl if r["e1_bucket"] == "E1_formal_thm_proof"),
            "all_math_roles_n": len(math_ctrl),
            "all_math_roles_L1_or_L2_pct": round(
                100.0 * sum(1 for r in math_ctrl if r["eligibility_class"] in ("L1_lean_amenable_math", "L2_mathlib_blocked_math")) / max(len(math_ctrl), 1),
                1,
            ),
            "all_math_roles_L1_pct": round(
                100.0 * sum(1 for r in math_ctrl if r["eligibility_class"] == "L1_lean_amenable_math") / max(len(math_ctrl), 1),
                1,
            ),
            "opfv_n": len(opfv_ctrl),
            "opfv_L3_or_L1_count": sum(1 for r in opfv_ctrl if r["eligibility_class"] in ("L3_operational_spec_fv", "L1_lean_amenable_math")),
            "by_confirmed_role_e2": {k: dict(v) for k, v in pos_by_role.items()},
            "by_confirmed_role_e1": {k: dict(v) for k, v in pos_e1_by_role.items()},
            "unexpected_mismatches": pos_mismatches,
        },
        "e1_vs_e2_confusion": {k: dict(v) for k, v in e1_vs_e2.items()},
        "random_t2_sample": {
            "total": len(random_t2),
            "class_totals": dict(rand_class_totals),
            "by_category": rand_by_cat,
        },
        "l2_barriers": dict(l2_barriers),
        "records": [
            {
                "arxiv_id": r["arxiv_id"],
                "primary_category": r["primary_category"],
                "pilot_strata_cat": r["pilot_strata_cat"],
                "is_confirmed_lean": bool(r["is_confirmed_lean"]),
                "confirmed_role_4way": r["confirmed_role_4way"],
                "fetch_source": r["fetch_source"],
                "e1_bucket": r["e1_bucket"],
                "n_core_claims": r["n_theorem"] + r["n_lemma"] + r["n_proposition"] + r["n_corollary"] + r["n_claim_or_fact"],
                "n_proof": r["n_proof"],
                "n_equation": r["n_equation"],
                "eligibility_class": r["eligibility_class"],
                "has_original_deductive_proof": bool(r["has_original_deductive_proof"]),
                "dominant_math_area": r["dominant_math_area"],
                "primary_barrier_if_L2": r["primary_barrier_if_L2"],
                "confidence": r["confidence"],
                "rationale": r["rationale"],
            }
            for r in rows
        ],
    }

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(summary, indent=2))

    # Render Markdown report
    pcs = summary["positive_control_sensitivity"]
    lines = [
        "# Pilot E0 Report: Lean 4 Eligibility & Structural Extraction Calibration",
        "",
        f"- **Generated:** `{summary['generated_at']}`",
        f"- **Model tier (E2):** `{model_tier}` (strictly blinded to `is_confirmed_lean` and `role_4way`)",
        f"- **Pilot size:** `{len(rows)}` unique papers (`{len(random_t2)}` stratified random T2 [`3`/category × 15] + `{len(pos_controls)}` confirmed Lean positive controls; overlap = `{summary['counts']['overlap_random_and_confirmed']}`)",
        f"- **Fetch coverage:** `html={fetch_counts['html']}`, `pdf={fetch_counts['pdf']}`, `failed={fetch_counts['failed']}`",
        "",
        "## 1. Positive-Control Sensitivity (82 Confirmed Lean Papers, Blinded)",
        "",
        "| Confirmed Role (`role_4way`) | N | `E1_formal` | `L1` (Lean-Amenable) | `L2` (Mathlib-Blocked) | `L3` (Op-FV) | `L4` (Heuristic/Num) | `L5` (Empirical) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for role in ["eng_algorithmic_proof", "pure_math_or_tcs", "operational_system_fv", "meta_formalization_system"]:
        e2c = pos_by_role.get(role, {})
        e1c = pos_e1_by_role.get(role, {})
        tot = sum(e2c.values())
        lines.append(
            f"| `{role}` | {tot} | {e1c.get('E1_formal_thm_proof', 0)} | "
            f"{e2c.get('L1_lean_amenable_math', 0)} | {e2c.get('L2_mathlib_blocked_math', 0)} | "
            f"{e2c.get('L3_operational_spec_fv', 0)} | {e2c.get('L4_heuristic_or_numerical_only', 0)} | "
            f"{e2c.get('L5_empirical_or_survey', 0)} |"
        )

    lines.extend(
        [
            "",
            f"- **Math/Algorithmic positive controls (`eng_algorithmic_proof` + `pure_math_or_tcs`, `n={pcs['all_math_roles_n']}`):** "
            f"`{pcs['all_math_roles_L1_or_L2_pct']}%` classified as Theorem-Bearing (`L1 ∪ L2`), `{pcs['all_math_roles_L1_pct']}%` as `L1` Lean-Amenable.",
            f"- **Operational FV positive controls (`n={pcs['opfv_n']}`):** `{pcs['opfv_L3_or_L1_count']}/{pcs['opfv_n']}` classified as `L3` or `L1`.",
            f"- **Unexpected mismatches:** `{len(pos_mismatches)}`",
            "",
            "## 2. Stage E1 Deterministic Bucket vs. Stage E2 LLM Class (All Pilot Papers)",
            "",
            "| E1 Bucket | `L1` | `L2` | `L3` | `L4` | `L5` | Total |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for b in ["E1_formal_thm_proof", "E1_weak_or_unnumbered_math", "E1_no_formal_claims", "E1_fetch_failed"]:
        c = e1_vs_e2.get(b, {})
        tot = sum(c.values())
        if tot == 0:
            continue
        lines.append(
            f"| `{b}` | {c.get('L1_lean_amenable_math', 0)} | {c.get('L2_mathlib_blocked_math', 0)} | "
            f"{c.get('L3_operational_spec_fv', 0)} | {c.get('L4_heuristic_or_numerical_only', 0)} | "
            f"{c.get('L5_empirical_or_survey', 0)} | {tot} |"
        )

    lines.extend(
        [
            "",
            "## 3. Random Stratified T2 Pilot (`n = 45`, `3`/Category)",
            "",
            "| Category | n | `E1_formal` | `L1` | `L2` | `L3` | `L4` | `L5` |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for cat in ALL15_CATS:
        d = rand_by_cat[cat]
        lines.append(
            f"| `{cat}` | {d['n']} | {d['e1_formal_thm_proof']} | {d['L1_lean_amenable_math']} | "
            f"{d['L2_mathlib_blocked_math']} | {d['L3_operational_spec_fv']} | "
            f"{d['L4_heuristic_or_numerical_only']} | {d['L5_empirical_or_survey']} |"
        )

    if pos_mismatches:
        lines.extend(["", "## 4. Positive-Control Edge Cases / Mismatches to Inspect", ""])
        for m in pos_mismatches:
            lines.append(
                f"- **`{m['arxiv_id']}`** (`{m['confirmed_role_4way']}` → E1=`{m['e1_bucket']}`, E2=`{m['eligibility_class']}`): {m['rationale']}"
            )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n")
    return summary


# ---------------------------------------------------------------------------
# Stage E1 Full T2 Census Summary Export
# ---------------------------------------------------------------------------

E1_BUCKETS: tuple[str, ...] = (
    "E1_formal_thm_proof",
    "E1_weak_or_unnumbered_math",
    "E1_no_formal_claims",
    "E1_fetch_failed",
)


def _bucket_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    fetch_counts = Counter(r["fetch_source"] for r in rows)
    bucket_counts = Counter(r["e1_bucket"] for r in rows)
    fetched = total - fetch_counts["failed"]
    denom_all = max(total, 1)
    denom_fetched = max(fetched, 1)

    e1_counts = {b: bucket_counts[b] for b in E1_BUCKETS}
    e1_shares_of_total = {b: round(100.0 * bucket_counts[b] / denom_all, 2) for b in E1_BUCKETS}
    e1_shares_of_fetched = {
        b: round(100.0 * bucket_counts[b] / denom_fetched, 2)
        for b in E1_BUCKETS
        if b != "E1_fetch_failed"
    }

    cue_group_counts: Counter[str] = Counter()
    cue_detail_counts: Counter[str] = Counter()
    formal_cue_group_counts: Counter[str] = Counter()
    for r in rows:
        cues = r.get("_domain_cues")
        if cues is None:
            cues = json.loads(r["domain_cues_json"] or "{}")
        for grp, hits in cues.items():
            if hits:
                cue_group_counts[grp] += 1
                if r["e1_bucket"] == "E1_formal_thm_proof":
                    formal_cue_group_counts[grp] += 1
                for h in hits:
                    cue_detail_counts[f"{grp}.{h}"] += 1

    return {
        "total_papers": total,
        "fetched_papers": fetched,
        "fetch_coverage_pct": round(100.0 * fetched / denom_all, 2),
        "fetch_sources": {
            "html": fetch_counts["html"],
            "pdf": fetch_counts["pdf"],
            "failed": fetch_counts["failed"],
        },
        "e1_counts": e1_counts,
        "e1_shares_pct": e1_shares_of_total,
        "e1_shares_of_fetched_pct": e1_shares_of_fetched,
        "e1_formal_plus_weak_count": bucket_counts["E1_formal_thm_proof"] + bucket_counts["E1_weak_or_unnumbered_math"],
        "e1_formal_plus_weak_pct": round(
            100.0 * (bucket_counts["E1_formal_thm_proof"] + bucket_counts["E1_weak_or_unnumbered_math"]) / denom_all,
            2,
        ),
        "domain_cue_groups_all": {
            "mathlib_barrier_cues": cue_group_counts["mathlib_barrier_cues"],
            "tractable_math_cues": cue_group_counts["tractable_math_cues"],
            "operational_fv_cues": cue_group_counts["operational_fv_cues"],
        },
        "domain_cue_groups_in_e1_formal": {
            "mathlib_barrier_cues": formal_cue_group_counts["mathlib_barrier_cues"],
            "tractable_math_cues": formal_cue_group_counts["tractable_math_cues"],
            "operational_fv_cues": formal_cue_group_counts["operational_fv_cues"],
        },
        "domain_cue_details": dict(sorted(cue_detail_counts.items())),
    }


def summarize_e1_t2(
    db_path: Path = DEFAULT_ELIGIBILITY_DB,
    out_path: Path = Path("artifacts/lean_eligibility_e1_t2_summary.json"),
    panel_path: Path = UNIFIED_PANEL_PATH,
) -> dict[str, Any]:
    """Export a compact git-tracked Stage E1 T2 census summary artifact across all 15 categories."""
    conn = connect_eligibility(db_path)
    raw_rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT ep.arxiv_id, ep.primary_category, ep.matched_15_cats_json,
                   ep.is_confirmed_lean, ep.confirmed_role_4way, ep.in_pilot_e0,
                   ms.fetch_source, ms.http_status, ms.error_msg, ms.text_chars,
                   ms.n_theorem, ms.n_lemma, ms.n_proposition, ms.n_corollary,
                   ms.n_claim_or_fact, ms.n_definition, ms.n_property_or_invariant,
                   ms.n_proof, ms.n_equation, ms.has_theory_section,
                   ms.has_appendix_proofs, ms.e1_bucket, ms.domain_cues_json
            FROM eligibility_papers ep
            LEFT JOIN math_structure ms ON ep.arxiv_id = ms.arxiv_id
            WHERE ep.in_t2_census = 1
            ORDER BY ep.arxiv_id ASC
            """
        ).fetchall()
    ]
    conn.close()

    unfetched = [r["arxiv_id"] for r in raw_rows if r["e1_bucket"] is None]
    if unfetched:
        raise RuntimeError(
            f"{len(unfetched)} T2 papers have not been fetched yet (first 5: {unfetched[:5]}). "
            "Run `fetch --cohort t2_all` to completion before summarizing."
        )

    for r in raw_rows:
        r["_matched_15"] = json.loads(r["matched_15_cats_json"] or "[]")
        r["_domain_cues"] = json.loads(r["domain_cues_json"] or "{}")

    panel_t2_per_cat: dict[str, Any] = {}
    if panel_path.exists():
        panel = json.loads(panel_path.read_text())
        for sl in panel.get("slices", []):
            if sl.get("slice_id") == "2026-11":
                panel_t2_per_cat = sl.get("per_category", {})
                break

    overall = _bucket_stats(raw_rows)
    multi_cat_papers = sum(1 for r in raw_rows if len(r["_matched_15"]) > 1)

    confirmed_t2 = [r for r in raw_rows if r["is_confirmed_lean"] == 1]
    confirmed_t2_by_role: dict[str, dict[str, int]] = defaultdict(lambda: Counter())
    for r in confirmed_t2:
        confirmed_t2_by_role[r["confirmed_role_4way"] or "unknown"][r["e1_bucket"]] += 1

    per_category: dict[str, Any] = {}
    for cat in ALL15_CATS:
        incl = [r for r in raw_rows if cat in r["_matched_15"]]
        prim = [r for r in incl if r["primary_category"] == cat]
        xlist = len(incl) - len(prim)
        stats = _bucket_stats(incl)
        prim_stats = _bucket_stats(prim)

        # Remove verbose per-cue details inside per_category to keep artifact compact
        stats.pop("domain_cue_details", None)
        entry: dict[str, Any] = {
            **stats,
            "primary_papers": len(prim),
            "cross_list_papers": xlist,
            "primary_only": {
                "total_papers": prim_stats["total_papers"],
                "e1_counts": prim_stats["e1_counts"],
                "e1_shares_pct": prim_stats["e1_shares_pct"],
            },
        }
        if cat in panel_t2_per_cat:
            pcat = panel_t2_per_cat[cat]
            c_v1 = pcat.get("confirmed_v1", {}).get("count", 0)
            roles_v1 = pcat.get("roles_v1", {})
            math_alg_v1 = roles_v1.get("eng_algorithmic_proof", 0) + roles_v1.get("pure_math_or_tcs", 0)
            entry["panel_t2_total_papers"] = pcat.get("total_papers")
            entry["panel_t2_confirmed_v1"] = c_v1
            entry["panel_t2_confirmed_v1_math_alg"] = math_alg_v1
            entry["panel_t2_raw_v1_pct"] = pcat.get("confirmed_v1", {}).get("pct")
        per_category[cat] = entry

    eess_all_set = {"eess.SY", "eess.SP", "eess.IV", "eess.AS"}
    eess_non_sy_set = {"eess.SP", "eess.IV", "eess.AS"}
    eess_all_rows = [r for r in raw_rows if set(r["_matched_15"]) & eess_all_set]
    eess_non_sy_rows = [r for r in raw_rows if set(r["_matched_15"]) & eess_non_sy_set]
    eess_all_stats = _bucket_stats(eess_all_rows)
    eess_all_stats.pop("domain_cue_details", None)
    eess_non_sy_stats = _bucket_stats(eess_non_sy_rows)
    eess_non_sy_stats.pop("domain_cue_details", None)

    failed_ids = [
        {"arxiv_id": r["arxiv_id"], "primary_category": r["primary_category"], "http_status": r["http_status"], "error_msg": r["error_msg"]}
        for r in raw_rows
        if r["fetch_source"] == "failed"
    ]

    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "cohort": "t2_all",
        "slice_id": "2026-11",
        "notes": (
            "Zero-token deterministic Stage E1 structural census across all N=5,303 T2 (2026-11) preprints "
            "in the 15-category engineering & applied-theory panel. Per-category rows use inclusive category "
            "membership (primary + cross-list, matching artifacts/unified_15cat_panel.json), with primary-only "
            "sub-breakdowns included for reference. Note: math.OC has 725 inclusive papers here vs 724 in "
            "unified_15cat_panel.json because 2611.26800 (primary cs.GT, cross-listed math.OC) was harvested "
            "in scout_eng_tier12_2026_11.db after survey.db; total unique T2 papers (5,303) and all other 14 "
            "categories match unified_15cat_panel.json identically."
        ),
        "overall": {
            **overall,
            "multi_category_15_overlap_papers": multi_cat_papers,
            "t2_confirmed_lean_papers": len(confirmed_t2),
            "t2_confirmed_lean_by_role_e1": {k: dict(v) for k, v in sorted(confirmed_t2_by_role.items())},
        },
        "eess_archive": {
            "eess_all": eess_all_stats,
            "eess_non_sy": eess_non_sy_stats,
        },
        "per_category": per_category,
        "failed_fetches": failed_ids,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Deterministic Lean-eligibility structural extractor (Stage E1).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-db", help="Initialize eligibility_t2.db from T2 DBs + 82 confirmed Lean controls.")
    p_init.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    p_init.add_argument("--pilot-per-cat", type=int, default=3)
    p_init.add_argument("--seed", type=int, default=20261125)

    p_fetch = sub.add_parser("fetch", help="Fetch arXiv HTML5/PDF and run zero-token structural extraction.")
    p_fetch.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    p_fetch.add_argument("--cohort", choices=["pilot_e0", "t2_all"], default="pilot_e0")
    p_fetch.add_argument("--workers", type=int, default=3)
    p_fetch.add_argument("--min-interval", type=float, default=0.4)
    p_fetch.add_argument("--limit", type=int, default=None)
    p_fetch.add_argument("--retry-failed", action="store_true")

    p_exp = sub.add_parser("export-e2", help="Export compact blinded evidence bundle for E2 LLM workflow.")
    p_exp.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    p_exp.add_argument("--cohort", choices=["pilot_e0", "e2_stratified"], default="pilot_e0")
    p_exp.add_argument("--out", type=Path, default=Path("data/eligibility_pilot_e0_in.json"))
    p_exp.add_argument("--per-cat-budget", type=int, default=30)
    p_exp.add_argument("--cap-none", type=int, default=4)
    p_exp.add_argument("--min-formal", type=int, default=10)
    p_exp.add_argument("--min-weak", type=int, default=6)
    p_exp.add_argument("--seed-prefix", type=str, default="e2_20261126")
    p_exp.add_argument("--skip-cached-model", type=str, default="flash")
    p_exp.add_argument("--plan-out", type=Path, default=None)

    p_imp = sub.add_parser("import-e2", help="Import E2 LLM results and generate Pilot E0 artifact + report.")
    p_imp.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    p_imp.add_argument("--cohort", default="pilot_e0")
    p_imp.add_argument("--in", dest="in_path", type=Path, required=True)
    p_imp.add_argument("--artifact", type=Path, default=Path("artifacts/lean_eligibility_pilot_e0.json"))
    p_imp.add_argument("--report", type=Path, default=Path("reports/lean_eligibility_pilot_e0.md"))

    p_sum = sub.add_parser("summarize-e1", help="Export compact Stage E1 T2 census summary artifact.")
    p_sum.add_argument("--db", type=Path, default=DEFAULT_ELIGIBILITY_DB)
    p_sum.add_argument("--out", type=Path, default=Path("artifacts/lean_eligibility_e1_t2_summary.json"))
    p_sum.add_argument("--panel", type=Path, default=UNIFIED_PANEL_PATH)

    args = ap.parse_args()
    if args.cmd == "init-db":
        res = init_eligibility_db(db_path=args.db, pilot_per_cat=args.pilot_per_cat, seed=args.seed)
        print(json.dumps(res, indent=2))
    elif args.cmd == "fetch":
        run_fetch(
            db_path=args.db,
            cohort=args.cohort,
            workers=args.workers,
            min_interval=args.min_interval,
            limit=args.limit,
            retry_failed=args.retry_failed,
        )
    elif args.cmd == "export-e2":
        res = export_e2_inputs(
            db_path=args.db,
            cohort=args.cohort,
            out_path=args.out,
            per_cat_budget=args.per_cat_budget,
            cap_none=args.cap_none,
            min_formal=args.min_formal,
            min_weak=args.min_weak,
            seed_prefix=args.seed_prefix,
            skip_cached_model=args.skip_cached_model or None,
            plan_out_path=args.plan_out,
        )
        print(json.dumps(res, indent=2))
    elif args.cmd == "import-e2":
        res = import_e2_and_report_pilot(
            db_path=args.db,
            in_path=args.in_path,
            cohort=args.cohort,
            artifact_path=args.artifact,
            report_path=args.report,
        )
        print(json.dumps(res["counts"], indent=2))
        print(json.dumps(res["positive_control_sensitivity"], indent=2))
    elif args.cmd == "summarize-e1":
        res = summarize_e1_t2(db_path=args.db, out_path=args.out, panel_path=args.panel)
        print(json.dumps(res["overall"], indent=2))


if __name__ == "__main__":
    main()
