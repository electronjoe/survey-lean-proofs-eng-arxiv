"""Prepare Phase 2 Layer-A audit bundles for cloned engineering_math_proof papers.

Fetches lightweight arXiv HTML5 pages (preserving exact LaTeX equations from <math alttext="...">),
falling back to PDF text extraction when HTML5 is unavailable, for confirmed `engineering_math_proof`
papers with locally cloned/extracted Lean repos (GitHub, GitLab, or Zenodo).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import httpx
from pypdf import PdfReader

from src.db import DEFAULT_DB_PATH, connect

USER_AGENT = "survey-lean-proofs-eng-arxiv/0.2 (academic research survey; phase2 audit prep)"


class _MathPreservingHTMLParser(HTMLParser):
    """Extract clean readable text while preserving LaTeX equations from <math alttext='...'>."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._math_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag in ("script", "style", "svg", "nav", "footer"):
            self._skip_depth += 1
        elif tag == "math":
            if self._math_depth == 0:
                alt = (attr_map.get("alttext") or "").strip()
                if alt:
                    self.chunks.append(f" ${alt}$ ")
            self._math_depth += 1
        elif tag in ("h1", "h2", "h3", "h4"):
            self.chunks.append("\n\n## ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "svg", "nav", "footer") and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "math" and self._math_depth > 0:
            self._math_depth -= 1
        elif tag in ("p", "div", "section", "li", "h1", "h2", "h3", "h4", "br", "tr"):
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and self._math_depth == 0:
            self.chunks.append(data)


def html_to_math_markdown(raw_html: str) -> str:
    p = _MathPreservingHTMLParser()
    p.feed(raw_html)
    txt = "".join(p.chunks)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


def pdf_to_markdown(raw_pdf: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_pdf))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        txt = page.extract_text() or ""
        parts.append(f"<!-- Page {i} -->\n{txt}")
    return "\n\n".join(parts)


def prepare(
    db_path: Path = DEFAULT_DB_PATH,
    clone_root: Path = Path("data/repos"),
    papers_dir: Path = Path("data/phase2_papers"),
    out_path: Path = Path("data/phase2_inputs.json"),
    unaudited_only: bool = False,
    only_ids: list[str] | None = None,
) -> None:
    conn = connect(db_path)
    audited_ids = {r["arxiv_id"] for r in conn.execute("SELECT arxiv_id FROM layer_a_audits").fetchall()}
    rows = conn.execute(
        """
        SELECT p.*, a.repos_json, c.raw_json AS cls_json
        FROM papers p
        JOIN artifact_profiles a ON p.arxiv_id = a.arxiv_id
        JOIN classifications c ON p.arxiv_id = c.arxiv_id
        WHERE c.track = 'lean_candidate' AND c.lean_usage_status = 'lean_contributed'
        ORDER BY p.submitted_date DESC
        """
    ).fetchall()

    papers_dir.mkdir(parents=True, exist_ok=True)
    targets = []
    total_bytes = 0
    only_id_set = set(only_ids) if only_ids else None

    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=45.0) as client:
        for r in rows:
            aid = r["arxiv_id"]
            if only_id_set is not None and aid not in only_id_set:
                continue
            if unaudited_only and aid in audited_ids and only_id_set is None:
                continue
            cls = json.loads(r["cls_json"])
            if cls.get("paper_domain_role") != "engineering_math_proof" and only_id_set is None:
                continue
            repos = json.loads(r["repos_json"] or "[]")
            cloned_repos = []
            for rp in repos:
                if rp.get("lean_file_count", 0) > 0 and not rp.get("clone_skipped"):
                    if rp.get("local_dir") and Path(rp["local_dir"]).exists():
                        d = Path(rp["local_dir"]).resolve()
                    else:
                        slug = rp["repo"].replace("/", "__")
                        d = (clone_root / slug).resolve()
                    if d.exists():
                        cloned_repos.append(
                            {
                                "repo": rp["repo"],
                                "host": rp.get("host", "github"),
                                "local_dir": str(d),
                                "lean_file_count": rp.get("lean_file_count"),
                                "loc_nonempty": rp.get("lean_static_counts", {}).get("loc_nonempty", 0),
                                "lean_toolchain": rp.get("lean_toolchain"),
                                "static_counts": rp.get("lean_static_counts", {}),
                            }
                        )
            if not cloned_repos:
                continue

            ver = r["version"]
            md_path = (papers_dir / f"{aid}.md").resolve()
            if not md_path.exists():
                url = f"https://arxiv.org/html/{aid}v{ver}"
                resp = client.get(url, follow_redirects=True)
                total_bytes += len(resp.content)
                if resp.status_code == 200 and "html" in resp.headers.get("content-type", "").lower() and "No HTML for" not in resp.text[:1000]:
                    md_text = html_to_math_markdown(resp.text)
                    md_path.write_text(md_text)
                    print(f"  Fetched {aid} HTML: {len(resp.content)/1024:.1f} KB -> {len(md_text)} chars", flush=True)
                else:
                    pdf_url = f"https://arxiv.org/pdf/{aid}v{ver}"
                    r_pdf = client.get(pdf_url, follow_redirects=True)
                    total_bytes += len(r_pdf.content)
                    if r_pdf.status_code == 200 and r_pdf.content[:4] == b"%PDF":
                        md_text = pdf_to_markdown(r_pdf.content)
                        md_path.write_text(md_text)
                        print(f"  Fetched {aid} PDF fallback: {len(r_pdf.content)/1024:.1f} KB -> {len(md_text)} chars", flush=True)
                    else:
                        print(f"  WARN: {aid} HTML={resp.status_code} PDF={r_pdf.status_code}", flush=True)
                        md_path.write_text(f"# {r['title']}\n\n{r['abstract']}\n")
                time.sleep(0.5)
            else:
                print(f"  Cached {aid}: {md_path}", flush=True)

            targets.append(
                {
                    "arxiv_id": aid,
                    "title": r["title"],
                    "primary_category": r["primary_category"],
                    "matched_target_cats": json.loads(r["matched_target_cats_json"]),
                    "submitted_date": r["submitted_date"][:10],
                    "abstract": r["abstract"],
                    "phase1_paradigm": cls.get("authoring_paradigm"),
                    "phase1_tier": cls.get("verification_tier_observed"),
                    "phase1_summary": cls.get("one_line_summary"),
                    "paper_markdown_path": str(md_path),
                    "cloned_repos": cloned_repos,
                }
            )

    out_path.write_text(json.dumps({"targets": targets}, indent=2))
    conn.close()
    print(f"\nPrepared {len(targets)} engineering_math_proof targets for Phase 2 audit (total downloaded: {total_bytes/1024/1024:.2f} MB).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Prepare Phase 2 Layer-A audit bundles.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--clone-root", type=Path, default=Path("data/repos"))
    ap.add_argument("--papers-dir", type=Path, default=Path("data/phase2_papers"))
    ap.add_argument("--out", type=Path, default=Path("data/phase2_inputs.json"))
    ap.add_argument("--unaudited-only", action="store_true")
    ap.add_argument("--only-ids", nargs="+", default=None)
    args = ap.parse_args()
    prepare(
        db_path=args.db,
        clone_root=args.clone_root,
        papers_dir=args.papers_dir,
        out_path=args.out,
        unaudited_only=args.unaudited_only,
        only_ids=args.only_ids,
    )


if __name__ == "__main__":
    main()
