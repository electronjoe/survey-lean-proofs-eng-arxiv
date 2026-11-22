"""Step 2: Polite full-text fetch (arXiv HTML5 -> PDF fallback) and deterministic pre-screen."""

from __future__ import annotations

import argparse
import io
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx
from pypdf import PdfReader

from src.db import DEFAULT_DB_PATH, connect, upsert_screen_result
from src.patterns import scan_text

USER_AGENT = "survey-lean-proofs-eng-arxiv/0.1 (academic research survey; polite fetcher)"


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.chunks: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "svg", "math"):
            self._skip_depth += 1
        elif tag == "a":
            for k, v in attrs:
                if k == "href" and v and v.startswith("http"):
                    self.hrefs.append(v)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "svg", "math") and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in ("p", "div", "section", "li", "h1", "h2", "h3", "h4", "br", "tr"):
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self.chunks.append(data)


def extract_html_text_and_links(raw_html: str) -> tuple[str, list[str]]:
    parser = _HTMLTextExtractor()
    parser.feed(raw_html)
    text = "".join(parser.chunks)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, parser.hrefs


def extract_pdf_text_and_links(raw_pdf: bytes) -> tuple[str, list[str]]:
    reader = PdfReader(io.BytesIO(raw_pdf))
    parts: list[str] = []
    links: list[str] = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
            if txt:
                parts.append(txt)
        except Exception:
            pass
        try:
            annots = page.get("/Annots") or []
            for annot_ref in annots:
                annot = annot_ref.get_object()
                action = annot.get("/A")
                if action and "/URI" in action:
                    uri = str(action["/URI"])
                    if uri.startswith("http"):
                        links.append(uri)
        except Exception:
            pass
    return "\n".join(parts), links


class _RateLimiter:
    """Thread-safe polite global rate limiter with backoff on 429/503."""

    def __init__(self, min_interval: float) -> None:
        self._lock = threading.Lock()
        self._min_interval = min_interval
        self._next_ok = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_ok:
                sleep_for = self._next_ok - now
                self._next_ok = self._next_ok + self._min_interval
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


def screen_one(
    client: httpx.Client,
    limiter: _RateLimiter,
    row: dict[str, Any],
) -> dict[str, Any]:
    arxiv_id = row["arxiv_id"]
    version = row["version"]
    meta_blob = f"{row['title']}\n{row['abstract']}\n{row['comment'] or ''}"
    meta_scan = scan_text(meta_blob)

    html_url = f"https://arxiv.org/html/{arxiv_id}v{version}"
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}v{version}"

    fetch_source = "failed"
    http_status: int | None = None
    error_msg: str | None = None
    full_text = ""
    extra_urls: list[str] = []

    try:
        r = _polite_get(client, limiter, html_url)
        http_status = r.status_code
        ctype = r.headers.get("content-type", "").lower()
        if r.status_code == 200 and "html" in ctype and len(r.text) > 1500 and "No HTML for" not in r.text[:1000]:
            full_text, extra_urls = extract_html_text_and_links(r.text)
            if len(full_text) >= 1000:
                fetch_source = "html"
    except Exception as exc:
        error_msg = f"html:{exc}"

    if fetch_source != "html":
        try:
            r_pdf = _polite_get(client, limiter, pdf_url)
            http_status = r_pdf.status_code
            ctype = r_pdf.headers.get("content-type", "").lower()
            if r_pdf.status_code == 200 and ("pdf" in ctype or r_pdf.content[:4] == b"%PDF"):
                full_text, extra_urls = extract_pdf_text_and_links(r_pdf.content)
                fetch_source = "pdf"
                error_msg = None
            else:
                error_msg = f"pdf_status={r_pdf.status_code}"
        except Exception as exc:
            error_msg = f"pdf:{exc}"

    combined_text = meta_blob + "\n\n" + full_text if full_text else meta_blob
    scan = scan_text(combined_text, extra_urls=extra_urls)

    return {
        "arxiv_id": arxiv_id,
        "version": version,
        "fetch_source": fetch_source,
        "http_status": http_status,
        "error_msg": error_msg,
        "text_chars": len(full_text),
        "has_lean_strong": scan["has_lean_strong"],
        "has_lean_contextual": scan["has_lean_contextual"],
        "has_other_itp": scan["has_other_itp"],
        "has_model_checker": scan["has_model_checker"],
        "has_protocol_verifier": scan["has_protocol_verifier"],
        "has_smt_sat": scan["has_smt_sat"],
        "lean_hits": scan["lean_hits"],
        "other_hits": scan["other_hits"],
        "urls": scan["urls"],
        "meta_hits": {
            "has_lean_strong": meta_scan["has_lean_strong"],
            "has_lean_contextual": meta_scan["has_lean_contextual"],
            "has_other_itp": meta_scan["has_other_itp"],
            "has_model_checker": meta_scan["has_model_checker"],
            "has_protocol_verifier": meta_scan["has_protocol_verifier"],
            "has_smt_sat": meta_scan["has_smt_sat"],
        },
    }


def run_screen(
    db_path: Path = DEFAULT_DB_PATH,
    workers: int = 3,
    min_interval: float = 0.4,
    limit: int | None = None,
    retry_failed: bool = False,
) -> None:
    conn = connect(db_path)
    if retry_failed:
        sql = """
            SELECT p.arxiv_id, p.version, p.title, p.abstract, p.comment
            FROM papers p
            LEFT JOIN screen_results s ON p.arxiv_id = s.arxiv_id
            WHERE s.arxiv_id IS NULL OR s.fetch_source = 'failed'
            ORDER BY p.submitted_date DESC
        """
    else:
        sql = """
            SELECT p.arxiv_id, p.version, p.title, p.abstract, p.comment
            FROM papers p
            LEFT JOIN screen_results s ON p.arxiv_id = s.arxiv_id
            WHERE s.arxiv_id IS NULL
            ORDER BY p.submitted_date DESC
        """
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    if limit is not None:
        rows = rows[:limit]

    total = len(rows)
    if total == 0:
        print("All papers already screened.")
        conn.close()
        return

    print(f"Screening {total} papers (workers={workers}, min_interval={min_interval}s)...", flush=True)
    limiter = _RateLimiter(min_interval=min_interval)
    t0 = time.monotonic()

    counts = {"html": 0, "pdf": 0, "failed": 0, "lean_strong": 0, "lean_ctx": 0, "other_itp": 0, "mc": 0, "proto": 0, "smt": 0}
    done = 0

    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(30.0, connect=15.0),
        limits=httpx.Limits(max_connections=workers + 2, max_keepalive_connections=workers),
    ) as client:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(screen_one, client, limiter, r) for r in rows]
            for fut in as_completed(futs):
                res = fut.result()
                with conn:
                    upsert_screen_result(conn, res)
                done += 1
                counts[res["fetch_source"]] = counts.get(res["fetch_source"], 0) + 1
                counts["lean_strong"] += int(res["has_lean_strong"])
                counts["lean_ctx"] += int(res["has_lean_contextual"])
                counts["other_itp"] += int(res["has_other_itp"])
                counts["mc"] += int(res["has_model_checker"])
                counts["proto"] += int(res["has_protocol_verifier"])
                counts["smt"] += int(res["has_smt_sat"])

                if res["has_lean_strong"]:
                    print(f"  [LEAN STRONG] {res['arxiv_id']} ({res['fetch_source']}) urls={res['urls'][:2]}", flush=True)

                if done % 100 == 0 or done == total:
                    elapsed = time.monotonic() - t0
                    rate = done / max(elapsed, 0.1)
                    eta = (total - done) / max(rate, 0.01) / 60.0
                    print(
                        f"Progress {done}/{total} ({rate:.2f}/s, ETA {eta:.1f}m) | "
                        f"html={counts['html']} pdf={counts['pdf']} fail={counts['failed']} | "
                        f"lean_strong={counts['lean_strong']} lean_ctx={counts['lean_ctx']} "
                        f"itp={counts['other_itp']} mc={counts['mc']} proto={counts['proto']} smt={counts['smt']}",
                        flush=True,
                    )

    conn.close()
    print(f"Finished screening {total} papers in {(time.monotonic()-t0)/60.0:.1f} min.", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch full text and run deterministic formal-proof pre-screen.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--min-interval", type=float, default=0.4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--retry-failed", action="store_true")
    args = ap.parse_args()
    run_screen(
        db_path=args.db,
        workers=args.workers,
        min_interval=args.min_interval,
        limit=args.limit,
        retry_failed=args.retry_failed,
    )


if __name__ == "__main__":
    main()
