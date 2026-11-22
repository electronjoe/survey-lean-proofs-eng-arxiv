"""Prepare low-bandwidth Phase 2 Layer-A audit bundles for cloned engineering_math_proof papers.

Fetches ONLY lightweight arXiv HTML5 pages (preserving exact LaTeX equations from <math alttext="...">)
for the 8 engineering_math_proof papers that already have cloned public Lean repos in data/repos/.
"""

from __future__ import annotations

import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import httpx

from src.db import DEFAULT_DB_PATH, connect

USER_AGENT = "survey-lean-proofs-eng-arxiv/0.1 (academic research survey; low-bandwidth phase2)"


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


def prepare(
    db_path: Path = DEFAULT_DB_PATH,
    clone_root: Path = Path("data/repos"),
    papers_dir: Path = Path("data/phase2_papers"),
    out_path: Path = Path("data/phase2_inputs.json"),
) -> None:
    conn = connect(db_path)
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

    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
        for r in rows:
            cls = json.loads(r["cls_json"])
            if cls.get("paper_domain_role") != "engineering_math_proof":
                continue
            repos = json.loads(r["repos_json"] or "[]")
            cloned_repos = []
            for rp in repos:
                if rp.get("lean_file_count", 0) > 0 and not rp.get("clone_skipped"):
                    slug = rp["repo"].replace("/", "__")
                    d = (clone_root / slug).resolve()
                    if d.exists():
                        cloned_repos.append(
                            {
                                "repo": rp["repo"],
                                "local_dir": str(d),
                                "lean_file_count": rp.get("lean_file_count"),
                                "loc_nonempty": rp.get("lean_static_counts", {}).get("loc_nonempty", 0),
                                "lean_toolchain": rp.get("lean_toolchain"),
                                "static_counts": rp.get("lean_static_counts", {}),
                            }
                        )
            if not cloned_repos:
                continue

            aid = r["arxiv_id"]
            ver = r["version"]
            md_path = (papers_dir / f"{aid}.md").resolve()
            if not md_path.exists():
                url = f"https://arxiv.org/html/{aid}v{ver}"
                resp = client.get(url, follow_redirects=True)
                total_bytes += len(resp.content)
                if resp.status_code == 200 and "html" in resp.headers.get("content-type", "").lower():
                    md_text = html_to_math_markdown(resp.text)
                    md_path.write_text(md_text)
                    print(f"  Fetched {aid} HTML: {len(resp.content)/1024:.1f} KB -> {len(md_text)} chars", flush=True)
                else:
                    print(f"  WARN: {aid} HTML status={resp.status_code}", flush=True)
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


if __name__ == "__main__":
    prepare()
