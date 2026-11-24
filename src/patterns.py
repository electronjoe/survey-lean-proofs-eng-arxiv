"""Deterministic full-text, LaTeX, and Lean-source signal detectors.

Aligned with the taxonomy of authoring paradigms (Paradigms 1-4) and
12 failure modes documented in proof-methods.md.
"""

from __future__ import annotations

import re
from typing import Any

# --- 1. Lean Strong Signals (unambiguous Lean theorem prover references) ---
LEAN_STRONG_PATTERNS: dict[str, re.Pattern[str]] = {
    "lean_version": re.compile(r"\bLean\s*[34](?:\.\d+)*\b"),
    "mathlib": re.compile(r"\bMathlib4?\b", re.IGNORECASE),
    "leanprover": re.compile(r"leanprover(?:-community)?|lean-lang\.org", re.IGNORECASE),
    "lakefile": re.compile(r"\blakefile\.(?:lean|toml)\b|\blean-toolchain\b", re.IGNORECASE),
    "lean_blueprint": re.compile(
        r"\b(?:LeanArchitect|leanblueprint|Verso\s+Blueprints?|inputleannode|leanok)\b",
        re.IGNORECASE,
    ),
    "lean_verifiers": re.compile(
        r"\b(?:lean4?checker|SafeVerify|Lean\s+Atlas|ProofBridge|LeanCopilot|sorryAx|native_decide|con-leche|con-ron)\b"
    ),
    "lean_prover_phrase": re.compile(
        r"\bLean\s+(?:proof\s+assistant|theorem\s+prover|formalization|formalisation|codebase|kernel|tactic|proofs?)\b",
        re.IGNORECASE,
    ),
    "in_lean_phrase": re.compile(
        r"\b(?:formaliz\w*|formalis\w*|mechaniz\w*|mechanis\w*|verified|checked|proved|proven)\s+(?:in|using|with)\s+Lean\b",
        re.IGNORECASE,
    ),
}

# --- 2. Lean Contextual Signal ("Lean" near formal-proof terminology) ---
LEAN_WORD_RE = re.compile(r"\bLean\b")
LEAN_CONTEXT_POSITIVE_RE = re.compile(
    r"\b(?:theorem|lemma|proof|prover|formaliz\w*|formalis\w*|mechaniz\w*|verif\w*|"
    r"assistant|tactic|type\s+theory|dependent\s+type|mathlib|coq|rocq|isabelle|"
    r"agda|sorry|axiom|kernel|autoformaliz\w*|blueprint|soundness|certified)\b",
    re.IGNORECASE,
)
LEAN_CONTEXT_NOISE_RE = re.compile(
    r"\b(?:lean\s+(?:manufacturing|startup|production|management|sigma|six\s+sigma|"
    r"enterprise|software|agile|construction|supply|angle|body|mass|tissue|meat|"
    r"beef|burn|mixture|combustion|forward|backward|left|right|into|on|against|toward))\b",
    re.IGNORECASE,
)

# --- 3. Beyond-Lean Formal Verification Tools (grouped by category) ---
OTHER_ITP_PATTERNS: dict[str, re.Pattern[str]] = {
    "coq_rocq": re.compile(
        r"\b(?:Rocq|Coq\s+(?:proof\s+assistant|theorem\s+prover|formaliz\w*|formalis\w*|mechaniz\w*|verified|proofs?)|"
        r"(?:in|using|with)\s+Coq\b|SSReflect|CompCert|VST\b)"
    ),
    "isabelle": re.compile(
        r"\b(?:Isabelle/HOL|Isabelle/ZF|Isabelle\s+(?:proof\s+assistant|theorem\s+prover|formaliz\w*|verified|proofs?)|"
        r"(?:in|using|with)\s+Isabelle\b)"
    ),
    "agda": re.compile(r"\bAgda\b"),
    "hol_light_hol4": re.compile(r"\b(?:HOL\s+Light|HOL4|CakeML)\b"),
    "dafny": re.compile(r"\bDafny\b"),
    "fstar": re.compile(r"\bF\*\s+(?:program|verif\w*|proof|language|code)\b|\bLow\*(?!\w)|\bEverParse\b"),
    "pvs_acl2_mizar": re.compile(r"\b(?:ACL2|Metamath|Mizar|PVS\s+(?:theorem\s+prover|specification|verifier))\b"),
    "why3_framac": re.compile(r"\b(?:Why3|Frama-C|Verus\s+verifier|Kani\s+verifier)\b"),
}

MODEL_CHECKER_PATTERNS: dict[str, re.Pattern[str]] = {
    "tla_plus": re.compile(r"\bTLA\+(?!\w)|\b(?:PlusCal|TLAPS)\b"),
    "prism_storm": re.compile(
        r"\b(?:PRISM\s+(?:model\s+check\w*|probabilistic|tool|verifier)|"
        r"(?:Storm|PRISM)\s+model\s+checker|"
        r"model\s+check\w*[^.\n]{0,60}\b(?:PRISM|Storm)\b)",
        re.IGNORECASE,
    ),
    "uppaal": re.compile(r"\bUPPAAL\b"),
    "nusmv_nuxmv": re.compile(r"\b(?:NuSMV|nuXmv)\b"),
    "spin_promela": re.compile(r"\b(?:Promela|SPIN\s+model\s+checker)\b", re.IGNORECASE),
    "alloy_maude": re.compile(
        r"\b(?:Alloy\s+(?:analyzer|model|specification|formal)|Maude\s+(?:rewriting|specification|model|system))\b",
        re.IGNORECASE,
    ),
    "cbmc_esbmc": re.compile(r"\b(?:CBMC|ESBMC|SeaHorn|CPAchecker)\b"),
}

PROTOCOL_VERIFIER_PATTERNS: dict[str, re.Pattern[str]] = {
    "tamarin": re.compile(r"\bTamarin\s*(?:prover|model|protocol|verif\w*)?\b"),
    "proverif": re.compile(r"\bProVerif\b"),
    "easycrypt": re.compile(r"\b(?:EasyCrypt|CryptoVerif|Jasmin\s+compiler|Verifpal|Squirrel\s+prover)\b"),
}

SMT_SAT_PATTERNS: dict[str, re.Pattern[str]] = {
    "z3_cvc": re.compile(
        r"\b(?:Z3\s+(?:SMT|solver|prover|theorem)|SMT\s+solver\s+Z3|cvc5|CVC4|SMT-LIB|Yices|Boolector|Bitwuzla|dReal)\b",
        re.IGNORECASE,
    ),
    "smt_general": re.compile(r"\b(?:SMT\s+solver|satisfiability\s+modulo\s+theories)\b", re.IGNORECASE),
}

# --- 4. Repository / Artifact URLs ---
REPO_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:"
    r"github\.com|gitlab\.[A-Za-z0-9.\-]+|codeberg\.org|bitbucket\.org|"
    r"zenodo\.org|osf\.io|huggingface\.co|(?:dx\.)?doi\.org/10\.5281/zenodo\.\d+"
    r")(?:/[A-Za-z0-9_.\-/]*)?",
    re.IGNORECASE,
)

# --- 5. LaTeX Blueprint / Workflow Signals (for Stage 3 on Lean hits) ---
LATEX_SIGNAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "inputleannode": re.compile(r"\\inputleannode\b"),
    "lean_macro": re.compile(r"\\lean\{|\\leanok\b|\\leansym\b|\\leanposition\b"),
    "blueprint_uses": re.compile(r"\\uses\{|\\proves\{"),
    "leanblueprint_pkg": re.compile(r"leanblueprint|LeanArchitect|verso", re.IGNORECASE),
    "theorem_envs": re.compile(r"\\begin\{(?:theorem|lemma|proposition|corollary|thm|lem|prop|cor)\}"),
    "agent_tools": re.compile(
        r"\b(?:Claude|GPT-[456]|o[134]-|Gemini|DeepSeek|Aristotle|AlphaProof|LeanCopilot|"
        r"Goedel-Prover|Kimina|DeepSeek-Prover|Harmonic|Cursor|Codex|Antigravity)\b",
        re.IGNORECASE,
    ),
}

# --- 6. Static Lean Source Red Flags & Paradigm Markers (Layer B/C + Paradigms 3/4) ---
LEAN_CODE_PATTERNS: dict[str, re.Pattern[str]] = {
    "sorry": re.compile(r"(?<![A-Za-z0-9_])sorry(?![A-Za-z0-9_])"),
    "admit": re.compile(r"(?:(?:^|[;·])\s*|\bby\s+)admit(?=\s*(?:$|[;)]|--))", re.MULTILINE),
    "custom_axiom": re.compile(r"^\s*(?:private\s+|protected\s+)?axiom\s+", re.MULTILINE),
    "native_decide": re.compile(r"\bnative_decide\b|\bLean\.ofReduceBool\b|\bofReduceNat\b"),
    "unsafe_or_impl_by": re.compile(r"^\s*unsafe\s+|@\[[^\]]*implemented_by\b", re.MULTILINE),
    "eval_cmd": re.compile(r"^\s*#eval\b", re.MULTILINE),
    "print_axioms": re.compile(r"#print\s+axioms\b"),
    "metaprog_override": re.compile(
        r"^\s*(?:local\s+|scoped\s+)?(?:notation|macro|macro_rules|elab|syntax)\b", re.MULTILINE
    ),
    "blueprint_attr": re.compile(r"@\[[^\]]*blueprint\b"),
    "theorem_decl": re.compile(
        r"^\s*(?:private\s+|protected\s+)?(?:theorem|lemma)\s+", re.MULTILINE
    ),
    "def_decl": re.compile(
        r"^\s*(?:private\s+|protected\s+|noncomputable\s+)?(?:def|structure|inductive|class|abbrev)\s+",
        re.MULTILINE,
    ),
    "mathlib_import": re.compile(r"^\s*import\s+Mathlib\b", re.MULTILINE),
    "non_vacuity_example": re.compile(r"^\s*example\s*[^:=]*∃", re.MULTILINE),
}


def _clean_snippet(text: str, start: int, end: int, radius: int = 240) -> str:
    lo = max(0, start - radius)
    hi = min(len(text), end + radius)
    snippet = text[lo:hi].replace("\n", " ")
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet


def _find_group_hits(
    text: str,
    patterns: dict[str, re.Pattern[str]],
    max_snippets: int = 4,
) -> dict[str, dict[str, Any]]:
    hits: dict[str, dict[str, Any]] = {}
    for name, pat in patterns.items():
        matches = list(pat.finditer(text))
        if not matches:
            continue
        snippets = [_clean_snippet(text, m.start(), m.end()) for m in matches[:max_snippets]]
        hits[name] = {"count": len(matches), "snippets": snippets}
    return hits


def scan_text(text: str, extra_urls: list[str] | None = None) -> dict[str, Any]:
    """Run all deterministic detectors on extracted paper text."""
    lean_strong = _find_group_hits(text, LEAN_STRONG_PATTERNS)

    # Contextual "Lean" hits (filtered to exclude obvious non-prover phrases)
    lean_ctx_snippets: list[str] = []
    lean_ctx_count = 0
    for m in LEAN_WORD_RE.finditer(text):
        window = text[max(0, m.start() - 280) : min(len(text), m.end() + 280)]
        near = text[max(0, m.start() - 20) : min(len(text), m.end() + 45)]
        if LEAN_CONTEXT_NOISE_RE.search(near):
            continue
        if LEAN_CONTEXT_POSITIVE_RE.search(window):
            lean_ctx_count += 1
            if len(lean_ctx_snippets) < 5:
                lean_ctx_snippets.append(_clean_snippet(text, m.start(), m.end()))

    lean_hits: dict[str, Any] = {}
    if lean_strong:
        lean_hits["strong"] = lean_strong
    if lean_ctx_count > 0:
        lean_hits["contextual"] = {"count": lean_ctx_count, "snippets": lean_ctx_snippets}

    other_itp = _find_group_hits(text, OTHER_ITP_PATTERNS, max_snippets=3)
    # Disambiguate bare "Tamarin" in protocol verifiers if needed: keep only if near protocol/formal/proof/verif/security/crypto/prover
    proto_raw = _find_group_hits(text, PROTOCOL_VERIFIER_PATTERNS, max_snippets=3)
    if "tamarin" in proto_raw:
        kept = [
            s
            for s in proto_raw["tamarin"]["snippets"]
            if re.search(
                r"\b(?:prover|protocol|verif\w*|formal|security|crypto|lemma|symbolic|auth\w*|key\s+exchange)\b",
                s,
                re.IGNORECASE,
            )
        ]
        if kept:
            proto_raw["tamarin"]["snippets"] = kept
        else:
            del proto_raw["tamarin"]

    model_checkers = _find_group_hits(text, MODEL_CHECKER_PATTERNS, max_snippets=3)
    smt_sat = _find_group_hits(text, SMT_SAT_PATTERNS, max_snippets=2)

    other_hits: dict[str, Any] = {}
    if other_itp:
        other_hits["itp"] = other_itp
    if model_checkers:
        other_hits["model_checker"] = model_checkers
    if proto_raw:
        other_hits["protocol_verifier"] = proto_raw
    if smt_sat:
        other_hits["smt_sat"] = smt_sat

    urls_set: set[str] = set()
    for u in REPO_URL_RE.findall(text):
        urls_set.add(u.rstrip(".,;:)]}\"'"))
    if extra_urls:
        for u in extra_urls:
            if REPO_URL_RE.match(u):
                urls_set.add(u.rstrip(".,;:)]}\"'"))

    return {
        "has_lean_strong": bool(lean_strong),
        "has_lean_contextual": lean_ctx_count > 0,
        "has_other_itp": bool(other_itp),
        "has_model_checker": bool(model_checkers),
        "has_protocol_verifier": bool(proto_raw),
        "has_smt_sat": bool(smt_sat),
        "lean_hits": lean_hits,
        "other_hits": other_hits,
        "urls": sorted(urls_set),
    }


def strip_lean_comments(code: str) -> str:
    """Remove Lean line (--) and block (/- ... -/) comments for cleaner static red-flag counts."""
    # Remove nested /- ... -/ block comments iteratively
    out: list[str] = []
    i = 0
    n = len(code)
    depth = 0
    while i < n:
        if code[i : i + 2] == "/-":
            depth += 1
            i += 2
        elif depth > 0 and code[i : i + 2] == "-/":
            depth -= 1
            i += 2
        elif depth == 0 and code[i : i + 2] == "--":
            nl = code.find("\n", i)
            if nl == -1:
                break
            out.append("\n")
            i = nl + 1
        elif depth == 0:
            out.append(code[i])
            i += 1
        else:
            if code[i] == "\n":
                out.append("\n")
            i += 1
    return "".join(out)


def scan_lean_source(code: str) -> dict[str, int]:
    """Count static Lean soundness/paradigm indicators in a single .lean file (comments stripped)."""
    cleaned = strip_lean_comments(code)
    counts: dict[str, int] = {}
    for name, pat in LEAN_CODE_PATTERNS.items():
        c = len(pat.findall(cleaned))
        if c:
            counts[name] = c
    # Also detect @[blueprint] inside doc/raw source just in case
    bp = len(LEAN_CODE_PATTERNS["blueprint_attr"].findall(code))
    if bp:
        counts["blueprint_attr"] = bp
    counts["loc_nonempty"] = sum(1 for ln in code.splitlines() if ln.strip())
    return counts


def scan_latex_source(tex: str) -> dict[str, Any]:
    """Scan raw LaTeX source for blueprint macros, theorem counts, and agent tool mentions."""
    out: dict[str, Any] = {}
    for name, pat in LATEX_SIGNAL_PATTERNS.items():
        matches = pat.findall(tex)
        if matches:
            if name == "agent_tools":
                out[name] = sorted(set(matches))
            else:
                out[name] = len(matches)
    return out
