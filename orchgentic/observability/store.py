from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Iterable

from .models import RunRecord, TraceEvent


DEFAULT_OBSERVABILITY_DB = Path("logs") / "orchgentic_observability.db"


class ObservabilityStore:
    """SQLite-backed run history and trace event store."""

    def __init__(self, db_path: str | Path = DEFAULT_OBSERVABILITY_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    run_type TEXT NOT NULL,
                    task TEXT,
                    status TEXT NOT NULL,
                    agent_id TEXT,
                    agent_name TEXT,
                    team_id TEXT,
                    team_name TEXT,
                    provider TEXT,
                    model TEXT,
                    external_llm_used INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_ms REAL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    estimated_tokens_saved INTEGER NOT NULL DEFAULT 0,
                    token_source TEXT NOT NULL DEFAULT 'not_applicable',
                    error_type TEXT,
                    error_message TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trace_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    parent_event_id TEXT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    name TEXT,
                    status TEXT NOT NULL,
                    message TEXT,
                    data TEXT NOT NULL DEFAULT '{}',
                    duration_ms REAL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    estimated_tokens_saved INTEGER NOT NULL DEFAULT 0,
                    token_source TEXT NOT NULL DEFAULT 'not_applicable',
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_events_run_id ON trace_events(run_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_events_type ON trace_events(event_type)")

    def create_run(self, run: RunRecord) -> RunRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, run_type, task, status, agent_id, agent_name, team_id, team_name,
                    provider, model, external_llm_used, started_at, ended_at, duration_ms,
                    input_tokens, output_tokens, total_tokens, estimated_tokens_saved,
                    token_source, error_type, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                run.to_row(),
            )
        return run

    def update_run(self, run: RunRecord) -> RunRecord:
        return self.create_run(run)

    def add_event(self, event: TraceEvent) -> TraceEvent:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO trace_events (
                    event_id, run_id, parent_event_id, timestamp, event_type, component,
                    name, status, message, data, duration_ms, input_tokens, output_tokens,
                    total_tokens, estimated_tokens_saved, token_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                event.to_row(),
            )
        return event

    def list_runs(self, limit: int = 20, status: str | None = None, run_type: str | None = None) -> list[RunRecord]:
        limit = max(1, min(int(limit or 20), 500))
        where = []
        params: list[object] = []
        if status:
            where.append("status = ?")
            params.append(status)
        if run_type:
            where.append("run_type = ?")
            params.append(run_type)
        sql = "SELECT * FROM runs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [RunRecord.from_row(row) for row in rows]

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return RunRecord.from_row(row) if row else None

    def list_events(self, run_id: str) -> list[TraceEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM trace_events WHERE run_id = ? ORDER BY timestamp ASC",
                (run_id,),
            ).fetchall()
        return [TraceEvent.from_row(row) for row in rows]

    def add_events(self, events: Iterable[TraceEvent]) -> list[TraceEvent]:
        saved = []
        for event in events:
            saved.append(self.add_event(event))
        return saved

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM trace_events")
            conn.execute("DELETE FROM runs")
