#!/usr/bin/env python3
"""Audit BibTeX hygiene, LaTeX citation integrity, and (optionally) live arXiv metadata.

Usage:
  # Fast offline CI gate (no network):
  uv run python scripts/audit_bib.py

  # Full live verification against export.arxiv.org API:
  uv run python scripts/audit_bib.py --live
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIB = REPO_ROOT / "papers" / "shared" / "references.bib"
DEFAULT_TEX = REPO_ROOT / "papers" / "arxiv-empirical" / "main.tex"

PLACEHOLDER_AUTHOR_PATTERNS = (
    re.compile(r"\bauthors?\b", re.IGNORECASE),
    re.compile(r"\band\s+others\b", re.IGNORECASE),
    re.compile(r"\bet\s+al\.?\b", re.IGNORECASE),
    re.compile(r"\b(todo|tbd|unknown|anonymous|placeholder)\b", re.IGNORECASE),
)

ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


@dataclass
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]
    line: int


def _extract_balanced(text: str, start: int) -> tuple[str, int]:
    """Extract balanced {...} value starting at index `start` (where text[start] == '{')."""
    assert text[start] == "{"
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise ValueError(f"Unbalanced braces starting at offset {start}")


def parse_bib(text: str) -> tuple[list[BibEntry], list[str]]:
    """Parse a BibTeX file into structured entries and report duplicate keys."""
    entries: list[BibEntry] = []
    errors: list[str] = []
    seen: set[str] = set()
    i = 0
    n = len(text)

    while i < n:
        at = text.find("@", i)
        if at == -1:
            break
        line_no = text.count("\n", 0, at) + 1
        m = re.match(r"@(\w+)\s*\{", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        body_start = at + m.end() - 1
        try:
            body, next_i = _extract_balanced(text, body_start)
        except ValueError as exc:
            errors.append(f"line {line_no}: {exc}")
            break
        i = next_i
        if etype in {"comment", "preamble", "string"}:
            continue

        comma = body.find(",")
        if comma == -1:
            errors.append(f"line {line_no}: malformed entry @{etype} (missing comma)")
            continue
        key = body[:comma].strip()
        if key in seen:
            errors.append(f"line {line_no}: duplicate BibTeX key {key!r}")
        seen.add(key)

        fields: dict[str, str] = {}
        pos = comma + 1
        while pos < len(body):
            fm = re.search(r"([A-Za-z_][A-Za-z0-9_-]*)\s*=\s*", body[pos:])
            if not fm:
                break
            fname = fm.group(1).lower()
            val_start = pos + fm.end()
            while val_start < len(body) and body[val_start].isspace():
                val_start += 1
            if val_start >= len(body):
                break
            if body[val_start] == "{":
                val, end_pos = _extract_balanced(body, val_start)
            elif body[val_start] == '"':
                end_q = body.find('"', val_start + 1)
                if end_q == -1:
                    errors.append(f"line {line_no} ({key}): unclosed quote in field {fname}")
                    break
                val = body[val_start + 1 : end_q]
                end_pos = end_q + 1
            else:
                end_c = body.find(",", val_start)
                if end_c == -1:
                    end_c = len(body)
                val = body[val_start:end_c].strip()
                end_pos = end_c
            fields[fname] = val.strip()
            pos = end_pos
        entries.append(BibEntry(entry_type=etype, key=key, fields=fields, line=line_no))

    return entries, errors


def extract_tex_citations(tex_text: str) -> set[str]:
    """Extract all cited BibTeX keys from LaTeX source (ignoring commented lines)."""
    cleaned = "\n".join(
        re.sub(r"(?<!\\)%.*$", "", line) for line in tex_text.splitlines()
    )
    keys: set[str] = set()
    for m in re.finditer(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}", cleaned):
        for raw_k in m.group(1).split(","):
            k = raw_k.strip()
            if k:
                keys.add(k)
    return keys


def _normalize_text_for_match(s: str) -> str:
    """Normalize LaTeX/arXiv titles and names for tolerant exact comparison."""
    # Unescape common TeX accents and math wrappers
    s = s.replace("--", "-").replace("---", "-")
    s = s.replace(r"{\i}", "i").replace(r"\i", "i").replace("ı", "i").replace("İ", "i")
    s = s.replace(r"{\l}", "l").replace(r"\l", "l").replace("ł", "l").replace("Ł", "l")
    s = s.replace(r"{\o}", "o").replace(r"\o", "o").replace("ø", "o").replace("Ø", "o")
    s = s.replace(r"{\ss}", "ss").replace("ß", "ss")
    s = re.sub(r"\\['\"`^~=.uvHc]\{?([A-Za-z])\}?", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("$", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    return s


def _surname(name: str) -> str:
    norm = _normalize_text_for_match(name)
    parts = norm.split()
    return parts[-1] if parts else ""


def check_offline_hygiene(
    entries: list[BibEntry], tex_paths: list[Path]
) -> list[str]:
    errors: list[str] = []
    keys = {e.key for e in entries}

    for e in entries:
        loc = f"{e.key} (line {e.line})"
        for req in ("author", "title", "year"):
            if not e.fields.get(req):
                errors.append(f"{loc}: missing required field '{req}'")

        author = e.fields.get("author", "")
        for pat in PLACEHOLDER_AUTHOR_PATTERNS:
            if pat.search(author):
                errors.append(f"{loc}: placeholder/truncated author string: {author!r}")

        if any(ord(ch) > 127 for ch in author):
            errors.append(
                f"{loc}: raw non-ASCII characters in author field (use TeX escapes for BibTeX safety): {author!r}"
            )

        if e.fields.get("archiveprefix", "").lower() == "arxiv" or "eprint" in e.fields:
            ep = e.fields.get("eprint", "")
            if not ARXIV_ID_RE.match(ep):
                errors.append(f"{loc}: invalid arXiv eprint ID {ep!r}")
            if not e.fields.get("primaryclass"):
                errors.append(f"{loc}: arXiv entry missing 'primaryClass'")

    if tex_paths:
        cited: set[str] = set()
        for tp in tex_paths:
            cited |= extract_tex_citations(tp.read_text(encoding="utf-8"))
        missing = sorted(cited - keys)
        uncited = sorted(keys - cited)
        if missing:
            errors.append(f"Cited in LaTeX but missing from BibTeX: {missing}")
        if uncited:
            errors.append(f"Present in BibTeX but uncited in LaTeX: {uncited}")

    return errors


def check_live_arxiv(entries: list[BibEntry], batch_size: int = 25) -> list[str]:
    """Query export.arxiv.org API and compare titles, authors, and primaryClass."""
    arxiv_entries = [
        e for e in entries if e.fields.get("eprint") and ARXIV_ID_RE.match(e.fields["eprint"])
    ]
    errors: list[str] = []
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    live_map: dict[str, tuple[str, list[str], str]] = {}
    for start in range(0, len(arxiv_entries), batch_size):
        batch = arxiv_entries[start : start + batch_size]
        ids = [re.sub(r"v\d+$", "", e.fields["eprint"]) for e in batch]
        url = "https://export.arxiv.org/api/query?max_results=" + str(len(ids)) + "&id_list=" + ",".join(ids)
        req = urllib.request.Request(url, headers={"User-Agent": "survey-lean-proofs-bib-audit/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            root = ET.fromstring(resp.read())
        for atom_entry in root.findall("a:entry", ns):
            raw_id = atom_entry.findtext("a:id", "", ns)
            m = re.search(r"/abs/(\d{4}\.\d{4,5})", raw_id)
            if not m:
                continue
            base_id = m.group(1)
            title = " ".join((atom_entry.findtext("a:title", "", ns) or "").split())
            authors = [a.findtext("a:name", "", ns) or "" for a in atom_entry.findall("a:author", ns)]
            pcat_el = atom_entry.find("arxiv:primary_category", ns)
            pcat = pcat_el.attrib.get("term", "") if pcat_el is not None else ""
            live_map[base_id] = (title, authors, pcat)

    for e in arxiv_entries:
        base_id = re.sub(r"v\d+$", "", e.fields["eprint"])
        loc = f"{e.key} ({base_id})"
        if base_id not in live_map:
            errors.append(f"{loc}: eprint not found on live arXiv API")
            continue
        live_title, live_authors, live_pcat = live_map[base_id]

        bib_title_n = _normalize_text_for_match(e.fields.get("title", ""))
        live_title_n = _normalize_text_for_match(live_title)
        if bib_title_n != live_title_n:
            errors.append(
                f"{loc}: title mismatch\n    bib:  {e.fields.get('title')!r}\n    live: {live_title!r}"
            )

        bib_authors = [a.strip() for a in e.fields.get("author", "").split(" and ") if a.strip()]
        if len(bib_authors) != len(live_authors):
            errors.append(
                f"{loc}: author count mismatch (bib={len(bib_authors)} vs live={len(live_authors)})\n"
                f"    bib:  {bib_authors}\n    live: {live_authors}"
            )
        else:
            for ba, la in zip(bib_authors, live_authors):
                if _surname(ba) != _surname(la):
                    errors.append(f"{loc}: author surname mismatch: bib={ba!r} vs live={la!r}")

        bib_pcat = e.fields.get("primaryclass", "")
        if live_pcat and bib_pcat != live_pcat:
            errors.append(f"{loc}: primaryClass mismatch (bib={bib_pcat!r} vs live={live_pcat!r})")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit BibTeX hygiene and optional live arXiv metadata.")
    ap.add_argument("--bib", type=Path, default=DEFAULT_BIB, help="Path to .bib file.")
    ap.add_argument(
        "--tex",
        type=Path,
        nargs="*",
        default=[DEFAULT_TEX],
        help="LaTeX file(s) to cross-check citations against (pass empty to skip).",
    )
    ap.add_argument(
        "--live",
        action="store_true",
        help="Also verify every arXiv eprint against live export.arxiv.org API.",
    )
    args = ap.parse_args()

    bib_text = args.bib.read_text(encoding="utf-8")
    entries, parse_errors = parse_bib(bib_text)
    errors = list(parse_errors)
    errors.extend(check_offline_hygiene(entries, [p for p in args.tex if p.is_file()]))

    arxiv_count = sum(1 for e in entries if e.fields.get("eprint"))
    if args.live:
        errors.extend(check_live_arxiv(entries))

    if errors:
        print(f"BibTeX audit FAILED ({len(errors)} issue(s) across {len(entries)} entries):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    mode = "offline + live arXiv API" if args.live else "offline"
    print(f"BibTeX audit PASSED ({mode}): {len(entries)} entries ({arxiv_count} arXiv eprints), 0 issues.")


if __name__ == "__main__":
    main()
