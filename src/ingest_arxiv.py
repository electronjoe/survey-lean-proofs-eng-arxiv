"""Step 1: Ingest arXiv metadata for target categories & date window into SQLite.

Supports two official arXiv metadata sources:
- `oai` (recommended): OAI-PMH bulk harvester (`oaipmh.arxiv.org/oai`, `metadataPrefix=arXivRaw`),
  fast, reliable, and polite (1,000 records/page), filtered strictly by v1 `submitted_date` in [since, until].
- `atom`: arXiv Atom API (`export.arxiv.org/api/query`), paginated by 200 records.
"""

from __future__ import annotations

import argparse
import email.utils
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.db import DEFAULT_DB_PATH, connect, upsert_paper
from src.patterns import scan_text

DEFAULT_CATEGORIES = ["cs.DC", "cs.NI", "cs.IT", "eess.SY", "cs.CR", "cs.RO"]
ARXIV_API = "https://export.arxiv.org/api/query"
OAI_API = "https://oaipmh.arxiv.org/oai"
USER_AGENT = "survey-lean-proofs-eng-arxiv/0.2 (academic research survey; polite rate limit)"
NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "os": "http://a9.com/-/spec/opensearch/1.1/",
}
OAI_NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "raw": "http://arxiv.org/OAI/arXivRaw/",
}
ARXIV_ID_RE = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})(?:v(\d+))?")


def _fmt_arxiv_date(date_str: str, end_of_day: bool = False) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y%m%d") + ("2359" if end_of_day else "0000")


def _cat_to_oai_set(cat: str) -> str:
    if "." in cat:
        archive, sub = cat.split(".", 1)
        return f"{archive}:{archive}:{sub}"
    return cat


def _http_get_with_retry(url: str, timeout: int = 45, max_attempts: int = 5) -> bytes:
    for attempt in range(max_attempts):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            wait = 5 * (attempt + 1)
            print(f"  [retry {attempt+1}/{max_attempts}] error={exc}; sleeping {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch URL: {url}")


def _parse_rfc2822_iso(date_str: str) -> str:
    dt = email.utils.parsedate_to_datetime(date_str.strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _split_raw_authors(authors_text: str) -> list[str]:
    clean = " ".join(authors_text.split())
    parts = [p.strip() for p in re.split(r",\s*|\s+and\s+", clean) if p.strip()]
    return parts


def ingest_oai(
    categories: list[str],
    since: str,
    until: str,
    db_path: Path = DEFAULT_DB_PATH,
    delay_sec: float = 3.1,
) -> dict[str, int]:
    conn = connect(db_path)
    target_set = set(categories)
    # Pad OAI `until` by +3 days to catch announcement datestamp lag, then filter strictly on v1 date
    until_dt = datetime.strptime(until, "%Y-%m-%d") + timedelta(days=3)
    oai_until = min(until_dt.date(), datetime.now(timezone.utc).date()).isoformat()

    seen_ids: dict[str, dict] = {}
    per_cat_counts: dict[str, int] = {}

    for cat in categories:
        oai_set = _cat_to_oai_set(cat)
        resumption: str | None = None
        kept = 0
        scanned = 0
        while True:
            if resumption:
                params = urllib.parse.urlencode({"verb": "ListRecords", "resumptionToken": resumption})
            else:
                params = urllib.parse.urlencode(
                    {
                        "verb": "ListRecords",
                        "metadataPrefix": "arXivRaw",
                        "set": oai_set,
                        "from": since,
                        "until": oai_until,
                    }
                )
            raw = _http_get_with_retry(f"{OAI_API}?{params}")
            root = ET.fromstring(raw)
            err = root.find("oai:error", OAI_NS)
            if err is not None:
                code = err.attrib.get("code", "")
                if code == "noRecordsMatch":
                    print(f"[{cat}] noRecordsMatch", flush=True)
                    break
                raise RuntimeError(f"OAI-PMH error ({code}): {err.text}")

            records = root.findall(".//oai:record", OAI_NS)
            for rec in records:
                header = rec.find("oai:header", OAI_NS)
                if header is not None and header.attrib.get("status") == "deleted":
                    continue
                md = rec.find("oai:metadata/raw:arXivRaw", OAI_NS)
                if md is None:
                    continue
                scanned += 1
                arxiv_id = (md.findtext("raw:id", default="", namespaces=OAI_NS) or "").strip()
                if not arxiv_id:
                    continue
                versions = md.findall("raw:version", OAI_NS)
                if not versions:
                    continue
                v1_date_raw = versions[0].findtext("raw:date", default="", namespaces=OAI_NS)
                vn_date_raw = versions[-1].findtext("raw:date", default="", namespaces=OAI_NS)
                try:
                    submitted_iso = _parse_rfc2822_iso(v1_date_raw)
                    updated_iso = _parse_rfc2822_iso(vn_date_raw)
                except Exception:
                    continue
                sub_day = submitted_iso[:10]
                if not (since <= sub_day <= until):
                    continue

                ver_attr = versions[-1].attrib.get("version", "v1")
                m_ver = re.search(r"(\d+)", ver_attr)
                version = int(m_ver.group(1)) if m_ver else len(versions)

                cats_text = (md.findtext("raw:categories", default="", namespaces=OAI_NS) or "").strip()
                all_cats = cats_text.split() if cats_text else [cat]
                primary_cat = all_cats[0]
                matched_targets = sorted((set(all_cats) & target_set) | {cat})

                title = " ".join((md.findtext("raw:title", default="", namespaces=OAI_NS) or "").split())
                abstract = " ".join((md.findtext("raw:abstract", default="", namespaces=OAI_NS) or "").split())
                authors = _split_raw_authors(md.findtext("raw:authors", default="", namespaces=OAI_NS) or "")
                comment = md.findtext("raw:comments", default=None, namespaces=OAI_NS)
                comment = " ".join(comment.split()) if comment else None
                journal_ref = md.findtext("raw:journal-ref", default=None, namespaces=OAI_NS)
                journal_ref = " ".join(journal_ref.split()) if journal_ref else None
                doi = md.findtext("raw:doi", default=None, namespaces=OAI_NS)
                doi = doi.strip() if doi else None

                kept += 1
                if arxiv_id in seen_ids:
                    prev = seen_ids[arxiv_id]
                    prev["matched_target_cats"] = sorted(
                        set(prev["matched_target_cats"]) | set(matched_targets)
                    )
                else:
                    seen_ids[arxiv_id] = {
                        "arxiv_id": arxiv_id,
                        "version": version,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "primary_category": primary_cat,
                        "all_categories": sorted(set(all_cats)),
                        "matched_target_cats": matched_targets,
                        "submitted_date": submitted_iso,
                        "updated_date": updated_iso,
                        "comment": comment,
                        "journal_ref": journal_ref,
                        "doi": doi,
                    }

            rt_el = root.find(".//oai:resumptionToken", OAI_NS)
            resumption = rt_el.text.strip() if (rt_el is not None and rt_el.text and rt_el.text.strip()) else None
            print(f"  [{cat}] scanned={scanned}, in_window={kept}, has_more={bool(resumption)}", flush=True)
            if not resumption:
                break
            time.sleep(delay_sec)

        per_cat_counts[cat] = kept
        time.sleep(delay_sec)

    _persist_and_preview(conn, seen_ids, categories, since, until)
    conn.close()
    return per_cat_counts


def ingest_atom(
    categories: list[str],
    since: str,
    until: str,
    db_path: Path = DEFAULT_DB_PATH,
    page_size: int = 200,
    delay_sec: float = 3.1,
) -> dict[str, int]:
    conn = connect(db_path)
    since_q = _fmt_arxiv_date(since, end_of_day=False)
    until_q = _fmt_arxiv_date(until, end_of_day=True)
    target_set = set(categories)

    seen_ids: dict[str, dict] = {}
    per_cat_counts: dict[str, int] = {}

    for cat in categories:
        q = f"cat:{cat}+AND+submittedDate:[{since_q}+TO+{until_q}]"
        start = 0
        cat_total = None
        fetched = 0
        while True:
            params = urllib.parse.urlencode(
                {
                    "search_query": q,
                    "start": start,
                    "max_results": page_size,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
                safe=":+[]()",
            )
            raw = _http_get_with_retry(f"{ARXIV_API}?{params}")
            root = ET.fromstring(raw)
            if cat_total is None:
                cat_total = int(root.find("os:totalResults", NS).text)
                print(f"[{cat}] totalResults={cat_total}", flush=True)
            entries = root.findall("a:entry", NS)
            if not entries:
                break
            for e in entries:
                id_url = e.find("a:id", NS).text.strip()
                m = ARXIV_ID_RE.search(id_url)
                if not m:
                    continue
                arxiv_id = m.group(1)
                version = int(m.group(2) or 1)
                all_cats = [c.attrib["term"] for c in e.findall("a:category", NS)]
                pc = e.find("arxiv:primary_category", NS)
                primary_cat = pc.attrib["term"] if pc is not None else (all_cats[0] if all_cats else cat)
                title = " ".join((e.find("a:title", NS).text or "").split())
                abstract = " ".join((e.find("a:summary", NS).text or "").split())
                authors = [
                    " ".join((a.find("a:name", NS).text or "").split())
                    for a in e.findall("a:author", NS)
                ]
                submitted = (e.find("a:published", NS).text or "").strip()
                updated = (e.find("a:updated", NS).text or "").strip()
                comm_el = e.find("arxiv:comment", NS)
                jref_el = e.find("arxiv:journal_ref", NS)
                doi_el = e.find("arxiv:doi", NS)

                matched_targets = sorted(set(all_cats) & target_set | {cat})
                if arxiv_id in seen_ids:
                    prev = seen_ids[arxiv_id]
                    prev["matched_target_cats"] = sorted(
                        set(prev["matched_target_cats"]) | set(matched_targets)
                    )
                else:
                    seen_ids[arxiv_id] = {
                        "arxiv_id": arxiv_id,
                        "version": version,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "primary_category": primary_cat,
                        "all_categories": sorted(set(all_cats)),
                        "matched_target_cats": matched_targets,
                        "submitted_date": submitted,
                        "updated_date": updated,
                        "comment": comm_el.text.strip() if comm_el is not None and comm_el.text else None,
                        "journal_ref": jref_el.text.strip() if jref_el is not None and jref_el.text else None,
                        "doi": doi_el.text.strip() if doi_el is not None and doi_el.text else None,
                    }
            fetched += len(entries)
            start += len(entries)
            print(f"  [{cat}] fetched {fetched}/{cat_total}", flush=True)
            if start >= cat_total or len(entries) < page_size:
                break
            time.sleep(delay_sec)
        per_cat_counts[cat] = fetched
        time.sleep(delay_sec)

    _persist_and_preview(conn, seen_ids, categories, since, until)
    conn.close()
    return per_cat_counts


def _persist_and_preview(
    conn,
    seen_ids: dict[str, dict],
    categories: list[str],
    since: str,
    until: str,
) -> None:
    meta_lean_strong = 0
    meta_lean_ctx = 0
    meta_other_itp = 0
    meta_mc = 0
    meta_proto = 0
    meta_smt = 0

    with conn:
        for p in seen_ids.values():
            upsert_paper(conn, p)
            blob = f"{p['title']}\n{p['abstract']}\n{p.get('comment') or ''}"
            s = scan_text(blob)
            meta_lean_strong += int(s["has_lean_strong"])
            meta_lean_ctx += int(s["has_lean_contextual"])
            meta_other_itp += int(s["has_other_itp"])
            meta_mc += int(s["has_model_checker"])
            meta_proto += int(s["has_protocol_verifier"])
            meta_smt += int(s["has_smt_sat"])

    print(f"\nIngested {len(seen_ids)} unique papers across {categories} ({since}..{until}).")
    print(
        f"Metadata-only quick hits: lean_strong={meta_lean_strong}, lean_ctx={meta_lean_ctx}, "
        f"other_itp={meta_other_itp}, model_checker={meta_mc}, proto_verifier={meta_proto}, smt_sat={meta_smt}"
    )


def main() -> None:
    today = datetime.now(timezone.utc).date()
    default_since = (today - timedelta(days=21)).isoformat()
    default_until = today.isoformat()

    ap = argparse.ArgumentParser(description="Ingest recent arXiv metadata into SQLite.")
    ap.add_argument("--since", default=default_since, help="Start date YYYY-MM-DD (inclusive)")
    ap.add_argument("--until", default=default_until, help="End date YYYY-MM-DD (inclusive)")
    ap.add_argument("--categories", nargs="+", default=DEFAULT_CATEGORIES)
    ap.add_argument("--source", choices=["oai", "atom"], default="oai")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--delay", type=float, default=3.1)
    args = ap.parse_args()

    if args.source == "oai":
        ingest_oai(
            categories=args.categories,
            since=args.since,
            until=args.until,
            db_path=args.db,
            delay_sec=args.delay,
        )
    else:
        ingest_atom(
            categories=args.categories,
            since=args.since,
            until=args.until,
            db_path=args.db,
            delay_sec=args.delay,
        )


if __name__ == "__main__":
    main()
