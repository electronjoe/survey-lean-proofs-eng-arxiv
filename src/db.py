"""SQLite storage for idempotent, resumable, re-runnable arXiv formal-proof surveys."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("data/survey.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    arxiv_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    primary_category TEXT NOT NULL,
    all_categories_json TEXT NOT NULL,
    matched_target_cats_json TEXT NOT NULL,
    submitted_date TEXT NOT NULL,
    updated_date TEXT NOT NULL,
    comment TEXT,
    journal_ref TEXT,
    doi TEXT,
    ingested_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screen_results (
    arxiv_id TEXT PRIMARY KEY REFERENCES papers(arxiv_id),
    version INTEGER NOT NULL,
    fetch_source TEXT NOT NULL,        -- 'html', 'pdf', 'meta_only', 'failed'
    http_status INTEGER,
    error_msg TEXT,
    text_chars INTEGER NOT NULL DEFAULT 0,
    has_lean_strong INTEGER NOT NULL DEFAULT 0,
    has_lean_contextual INTEGER NOT NULL DEFAULT 0,
    has_other_itp INTEGER NOT NULL DEFAULT 0,
    has_model_checker INTEGER NOT NULL DEFAULT 0,
    has_protocol_verifier INTEGER NOT NULL DEFAULT 0,
    has_smt_sat INTEGER NOT NULL DEFAULT 0,
    lean_hits_json TEXT NOT NULL DEFAULT '{}',
    other_hits_json TEXT NOT NULL DEFAULT '{}',
    urls_json TEXT NOT NULL DEFAULT '[]',
    meta_hits_json TEXT NOT NULL DEFAULT '{}',
    screened_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact_profiles (
    arxiv_id TEXT PRIMARY KEY REFERENCES papers(arxiv_id),
    latex_fetched INTEGER NOT NULL DEFAULT 0,
    latex_signals_json TEXT NOT NULL DEFAULT '{}',
    repos_json TEXT NOT NULL DEFAULT '[]',
    profiled_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS classifications (
    arxiv_id TEXT PRIMARY KEY REFERENCES papers(arxiv_id),
    track TEXT NOT NULL,               -- 'lean_candidate' or 'beyond_lean'
    model_tier TEXT NOT NULL,
    lean_usage_status TEXT NOT NULL,
    authoring_paradigm TEXT NOT NULL,
    paradigm_confidence TEXT,
    verification_tier TEXT,
    ai_agent_assisted TEXT,
    artifact_availability TEXT,
    other_formal_tools_json TEXT NOT NULL DEFAULT '[]',
    static_risk_flags_json TEXT NOT NULL DEFAULT '[]',
    raw_json TEXT NOT NULL,
    classified_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_papers_submitted ON papers(submitted_date);
CREATE INDEX IF NOT EXISTS idx_papers_primary_cat ON papers(primary_category);
CREATE INDEX IF NOT EXISTS idx_screen_lean ON screen_results(has_lean_strong, has_lean_contextual);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA)
    return conn


def upsert_paper(conn: sqlite3.Connection, paper: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO papers (
            arxiv_id, version, title, abstract, authors_json,
            primary_category, all_categories_json, matched_target_cats_json,
            submitted_date, updated_date, comment, journal_ref, doi, ingested_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            version = excluded.version,
            title = excluded.title,
            abstract = excluded.abstract,
            authors_json = excluded.authors_json,
            primary_category = excluded.primary_category,
            all_categories_json = excluded.all_categories_json,
            matched_target_cats_json = excluded.matched_target_cats_json,
            submitted_date = excluded.submitted_date,
            updated_date = excluded.updated_date,
            comment = excluded.comment,
            journal_ref = excluded.journal_ref,
            doi = excluded.doi,
            ingested_at = excluded.ingested_at
        """,
        (
            paper["arxiv_id"],
            paper["version"],
            paper["title"],
            paper["abstract"],
            json.dumps(paper["authors"]),
            paper["primary_category"],
            json.dumps(paper["all_categories"]),
            json.dumps(paper["matched_target_cats"]),
            paper["submitted_date"],
            paper["updated_date"],
            paper.get("comment"),
            paper.get("journal_ref"),
            paper.get("doi"),
            utc_now(),
        ),
    )


def upsert_screen_result(conn: sqlite3.Connection, res: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO screen_results (
            arxiv_id, version, fetch_source, http_status, error_msg, text_chars,
            has_lean_strong, has_lean_contextual, has_other_itp,
            has_model_checker, has_protocol_verifier, has_smt_sat,
            lean_hits_json, other_hits_json, urls_json, meta_hits_json, screened_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            version = excluded.version,
            fetch_source = excluded.fetch_source,
            http_status = excluded.http_status,
            error_msg = excluded.error_msg,
            text_chars = excluded.text_chars,
            has_lean_strong = excluded.has_lean_strong,
            has_lean_contextual = excluded.has_lean_contextual,
            has_other_itp = excluded.has_other_itp,
            has_model_checker = excluded.has_model_checker,
            has_protocol_verifier = excluded.has_protocol_verifier,
            has_smt_sat = excluded.has_smt_sat,
            lean_hits_json = excluded.lean_hits_json,
            other_hits_json = excluded.other_hits_json,
            urls_json = excluded.urls_json,
            meta_hits_json = excluded.meta_hits_json,
            screened_at = excluded.screened_at
        """,
        (
            res["arxiv_id"],
            res["version"],
            res["fetch_source"],
            res.get("http_status"),
            res.get("error_msg"),
            res.get("text_chars", 0),
            int(res.get("has_lean_strong", False)),
            int(res.get("has_lean_contextual", False)),
            int(res.get("has_other_itp", False)),
            int(res.get("has_model_checker", False)),
            int(res.get("has_protocol_verifier", False)),
            int(res.get("has_smt_sat", False)),
            json.dumps(res.get("lean_hits", {})),
            json.dumps(res.get("other_hits", {})),
            json.dumps(res.get("urls", [])),
            json.dumps(res.get("meta_hits", {})),
            utc_now(),
        ),
    )


def upsert_artifact_profile(
    conn: sqlite3.Connection,
    arxiv_id: str,
    latex_fetched: bool,
    latex_signals: dict[str, Any],
    repos: list[dict[str, Any]],
) -> None:
    conn.execute(
        """
        INSERT INTO artifact_profiles (
            arxiv_id, latex_fetched, latex_signals_json, repos_json, profiled_at
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            latex_fetched = excluded.latex_fetched,
            latex_signals_json = excluded.latex_signals_json,
            repos_json = excluded.repos_json,
            profiled_at = excluded.profiled_at
        """,
        (
            arxiv_id,
            int(latex_fetched),
            json.dumps(latex_signals),
            json.dumps(repos),
            utc_now(),
        ),
    )


def upsert_classification(
    conn: sqlite3.Connection,
    arxiv_id: str,
    track: str,
    model_tier: str,
    result: dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO classifications (
            arxiv_id, track, model_tier, lean_usage_status, authoring_paradigm,
            paradigm_confidence, verification_tier, ai_agent_assisted,
            artifact_availability, other_formal_tools_json, static_risk_flags_json,
            raw_json, classified_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            track = excluded.track,
            model_tier = excluded.model_tier,
            lean_usage_status = excluded.lean_usage_status,
            authoring_paradigm = excluded.authoring_paradigm,
            paradigm_confidence = excluded.paradigm_confidence,
            verification_tier = excluded.verification_tier,
            ai_agent_assisted = excluded.ai_agent_assisted,
            artifact_availability = excluded.artifact_availability,
            other_formal_tools_json = excluded.other_formal_tools_json,
            static_risk_flags_json = excluded.static_risk_flags_json,
            raw_json = excluded.raw_json,
            classified_at = excluded.classified_at
        """,
        (
            arxiv_id,
            track,
            model_tier,
            result.get("lean_usage_status", "N/A"),
            result.get("authoring_paradigm", "N/A"),
            result.get("paradigm_confidence"),
            result.get("verification_tier_observed"),
            result.get("ai_agent_assisted"),
            result.get("artifact_availability"),
            json.dumps(result.get("other_formal_tools_contributed", [])),
            json.dumps(result.get("static_risk_flags", [])),
            json.dumps(result),
            utc_now(),
        ),
    )
