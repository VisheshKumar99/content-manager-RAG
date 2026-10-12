"""SQLite persistence for script-generation runs and their iterations.

Two tables:
- runs:       one row per prompt submission (the whole refinement job).
- iterations: one row per phase event emitted by the refinement loop
              (generate / critique / refine / final).

The database file lives next to the server package so it is stable
regardless of the working directory the API is started from.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone

# Place the DB at server/data/app.db
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
DB_PATH = os.path.join(_DATA_DIR, "app.db")

# SQLite connections are not safe to share across threads by default.
# We serialize access with a lock and open short-lived connections.
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    os.makedirs(_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with _lock, _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id            TEXT PRIMARY KEY,
                prompt        TEXT NOT NULL,
                config        TEXT NOT NULL,
                status        TEXT NOT NULL,
                best_score    INTEGER,
                final_plan    TEXT,
                error         TEXT,
                created_at    TEXT NOT NULL,
                updated_at    TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS iterations (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id        TEXT NOT NULL,
                iteration     INTEGER NOT NULL,
                phase         TEXT NOT NULL,
                score         INTEGER,
                approved      INTEGER,
                issues        TEXT,
                plan          TEXT,
                message       TEXT,
                created_at    TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );

            CREATE INDEX IF NOT EXISTS idx_iterations_run
                ON iterations(run_id);
            """
        )


def create_run(run_id: str, prompt: str, config: dict) -> None:
    now = _now()
    with _lock, _connect() as conn:
        conn.execute(
            """
            INSERT INTO runs
                (id, prompt, config, status, created_at, updated_at)
            VALUES (?, ?, ?, 'running', ?, ?)
            """,
            (run_id, prompt, json.dumps(config), now, now),
        )


def add_iteration(run_id: str, event: dict) -> int:
    now = _now()
    approved = event.get("approved")
    with _lock, _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO iterations
                (run_id, iteration, phase, score, approved,
                 issues, plan, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                int(event.get("iteration", 0)),
                event.get("phase", "unknown"),
                event.get("score"),
                None if approved is None else int(bool(approved)),
                json.dumps(event.get("issues", [])),
                json.dumps(event.get("plan")) if event.get("plan") else None,
                event.get("message", ""),
                now,
            ),
        )
        conn.execute(
            "UPDATE runs SET updated_at = ? WHERE id = ?", (now, run_id)
        )
        return int(cur.lastrowid)


def finish_run(
    run_id: str,
    status: str,
    best_score: int | None = None,
    final_plan: dict | None = None,
    error: str | None = None,
) -> None:
    now = _now()
    with _lock, _connect() as conn:
        conn.execute(
            """
            UPDATE runs
               SET status = ?, best_score = ?, final_plan = ?,
                   error = ?, updated_at = ?
             WHERE id = ?
            """,
            (
                status,
                best_score,
                json.dumps(final_plan) if final_plan else None,
                error,
                now,
                run_id,
            ),
        )


def _row_to_run(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "prompt": row["prompt"],
        "config": json.loads(row["config"]),
        "status": row["status"],
        "bestScore": row["best_score"],
        "finalPlan": json.loads(row["final_plan"]) if row["final_plan"] else None,
        "error": row["error"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def _row_to_iteration(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "runId": row["run_id"],
        "iteration": row["iteration"],
        "phase": row["phase"],
        "score": row["score"],
        "approved": None if row["approved"] is None else bool(row["approved"]),
        "issues": json.loads(row["issues"]) if row["issues"] else [],
        "plan": json.loads(row["plan"]) if row["plan"] else None,
        "message": row["message"],
        "createdAt": row["created_at"],
    }


def list_runs() -> list[dict]:
    with _lock, _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY created_at DESC"
        ).fetchall()
        return [_row_to_run(r) for r in rows]


def get_run(run_id: str) -> dict | None:
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        run = _row_to_run(row)
        iters = conn.execute(
            "SELECT * FROM iterations WHERE run_id = ? ORDER BY id ASC",
            (run_id,),
        ).fetchall()
        run["iterations"] = [_row_to_iteration(r) for r in iters]
        return run
