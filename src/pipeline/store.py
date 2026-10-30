"""W4 REFERENCE — src/pipeline/store.py

Extends the W2 SQLite store with two new columns:
  • cost_usd  REAL    — actual per-call cost from response.usage × rates
  • model     TEXT    — which model produced the answer

Adds ensure_schema() that runs idempotent ALTER TABLE migrations so a cohort
member can rerun without breaking an existing answers.db.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
import time

# ─── Schema (idempotent) ────────────────────────────────────────────────────
_BASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    content         TEXT NOT NULL,
    retries         INTEGER DEFAULT 0,
    cost_usd        REAL DEFAULT 0.0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS eval_runs;

CREATE TABLE eval_runs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 run_id       INTEGER NOT NULL,                          -- groups one eval run
 golden_id TEXT NOT NULL,
 question TEXT NOT NULL,
 candidate_answer TEXT NOT NULL,
 accuracy INTEGER NOT NULL,
 groundedness INTEGER NOT NULL,
 format INTEGER NOT NULL,
 reasoning TEXT NOT NULL,
 eval_run_label TEXT DEFAULT 'eval-run-001',
 created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

"""

# Columns added in W4. Each entry: (column_name, column_def).
# Applied via ALTER TABLE only if missing — so the migration is safe to rerun.
_W4_NEW_COLUMNS = [
    ("model",          "TEXT"),
    ("confidence",     "REAL"),
    ("sources_json",   "TEXT"),  # list[str] stored as JSON
    ("schema_version", "TEXT DEFAULT 'v1'"),
]


def ensure_schema(db_path: str | Path) -> None:
    """Create answers table if missing, then add any missing W4 columns.

    Safe to call on an empty file, on a W2/W3 db, or on a fully-migrated db.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_BASE_SCHEMA)
        # Read current columns.
        cur = conn.execute("PRAGMA table_info(answers)")
        existing = {row[1] for row in cur.fetchall()}
        for col_name, col_def in _W4_NEW_COLUMNS:
            if col_name not in existing:
                conn.execute(f"ALTER TABLE answers ADD COLUMN {col_name} {col_def}")
        conn.commit()
    finally:
        conn.close()


@contextmanager
def connect(db_path: str | Path== "data/answers.db") -> Iterator[sqlite3.Connection]:
    """Open a connection with the W4 schema guaranteed in place."""
    ensure_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def save_answer(
    conn: sqlite3.Connection,
    *,
    question: str,
    content: str,
    retries: int,
    cost_usd: float,
    model: str,
    confidence: float,
    sources: list[str],
    schema_version: str = "v1",
) -> int:
    """Insert one row and return its rowid."""
    cur = conn.execute(
        """
        INSERT INTO answers (
            question, content, retries, cost_usd, model,
            confidence, sources_json, schema_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question, content, retries, cost_usd, model,
            confidence, json.dumps(sources), schema_version,
        ),
    )
    return cur.lastrowid


def query_results(conn: sqlite3.Connection, model: str | None = None) -> list[dict]:
    """Read back rows, optionally filtered by model. Useful in Step 3."""
    if model is None:
        cur = conn.execute("SELECT * FROM answers ORDER BY id")
    else:
        cur = conn.execute("SELECT * FROM answers WHERE model = ? ORDER BY id", (model,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

def write_eval_run(
    conn: sqlite3.Connection,
    run_id: int,
    golden_id: str,
    question: str,
    candidate_answer: str,
    scores: dict
) -> None:
    """Insert one judged answer into `eval_runs` (Week 5)."""
    # try:
    # with conn as conn1:
    conn.execute(
                "INSERT INTO eval_runs (run_id, golden_id, question, candidate_answer,"
                "                       accuracy, groundedness, format, reasoning, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, golden_id, question, candidate_answer,
                scores.get("accuracy"), scores.get("groundedness"),
                scores.get("format"), scores.get("reasoning"), time.time()),
            )
    conn.commit()
    # except AttributeError as e:
    #     print(e)


def write_rag_run(
    con: sqlite3.Connection,
    run_id: int,
    golden_id: str,
    question: str,
    answer: str,
    sources: list[str],
    hit: int,
    latency_ms: float,
    cost_usd: float,
) -> None:
    """Insert one RAG answer over the golden set into `rag_runs` (Week 6)."""
    import json
    conn.execute(
        "INSERT INTO rag_runs (run_id, golden_id, question, answer, sources_json, "
        "                      hit, latency_ms, cost_usd, ts) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, golden_id, question, answer, json.dumps(sources),
         hit, latency_ms, cost_usd, time.time()),
    )
    conn.commit()