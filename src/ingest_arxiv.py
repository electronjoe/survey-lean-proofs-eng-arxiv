"""Step 1: Ingest arXiv metadata for target categories & date window into SQLite."""

from __future__ import annotations

import argparse
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
USER_AGENT = "survey-lean-proofs-eng-arxiv/0.1 (academic research survey; polite rate limit)"
NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "os": "http://a9.com/-/spec/opensearch/1.1/",
}
ARXIV_ID_RE = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})(?:v(\d+))?")


def _fmt_arxiv_date(date_str: str, end_of_day: bool = False) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y%m%d") + ("2359" if end_of_day else "0000")


def _fetch_page(search_query: str, start: int, max_results: int) -> bytes:
    params = urllib.parse.urlencode(
        {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        safe=":+[]()",
    )
    url = f"{ARXIV_API}?{params}"
    for attempt in range(5):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:
            wait = 5 * (attempt + 1)
            print(f"  [retry {attempt+1}/5] error={exc}; sleeping {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch arXiv API page start={start}")


def ingest(
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
            raw = _fetch_page(q, start=start, max_results=page_size)
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

    # Persist to SQLite and print instant metadata-only preview
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

    conn.close()
    print(f"\nIngested {len(seen_ids)} unique papers across {categories} ({since}..{until}).")
    print(
        f"Metadata-only quick hits: lean_strong={meta_lean_strong}, lean_ctx={meta_lean_ctx}, "
        f"other_itp={meta_other_itp}, model_checker={meta_mc}, proto_verifier={meta_proto}, smt_sat={meta_smt}"
    )
    return per_cat_counts


def main() -> None:
    today = datetime.now(timezone.utc).date()
    default_since = (today - timedelta(days=21)).isoformat()
    default_until = today.isoformat()

    ap = argparse.ArgumentParser(description="Ingest recent arXiv metadata into SQLite.")
    ap.add_argument("--since", default=default_since, help="Start date YYYY-MM-DD (inclusive)")
    ap.add_argument("--until", default=default_until, help="End date YYYY-MM-DD (inclusive)")
    ap.add_argument("--categories", nargs="+", default=DEFAULT_CATEGORIES)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--delay", type=float, default=3.1)
    args = ap.parse_args()

    ingest(
        categories=args.categories,
        since=args.since,
        until=args.until,
        db_path=args.db,
        delay_sec=args.delay,
    )


if __name__ == "__main__":
    main()
