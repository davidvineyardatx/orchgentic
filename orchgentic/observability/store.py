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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_type ON runs(run_type)")
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

    def _build_run_filters(
        self,
        *,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
        older_than_iso: str | None = None,
    ) -> tuple[list[str], list[object]]:
        where: list[str] = []
        params: list[object] = []
        if status:
            where.append("status = ?")
            params.append(status)
        if run_type:
            where.append("run_type = ?")
            params.append(run_type)
        if agent:
            where.append("(lower(agent_id) = lower(?) OR lower(agent_name) = lower(?))")
            params.extend([agent, agent])
        if team:
            where.append("(lower(team_id) = lower(?) OR lower(team_name) = lower(?))")
            params.extend([team, team])
        if older_than_iso:
            where.append("started_at < ?")
            params.append(older_than_iso)
        return where, params

    def list_runs(
        self,
        limit: int = 20,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
    ) -> list[RunRecord]:
        limit = max(1, min(int(limit or 20), 500))
        where, params = self._build_run_filters(status=status, run_type=run_type, agent=agent, team=team)
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

    def list_events(
        self,
        run_id: str,
        event_type: str | None = None,
        component: str | None = None,
        tokens_only: bool = False,
    ) -> list[TraceEvent]:
        where = ["run_id = ?"]
        params: list[object] = [run_id]
        if event_type:
            where.append("event_type = ?")
            params.append(event_type)
        if component:
            where.append("component = ?")
            params.append(component)
        if tokens_only:
            where.append("(total_tokens > 0 OR estimated_tokens_saved > 0)")
        sql = "SELECT * FROM trace_events WHERE " + " AND ".join(where) + " ORDER BY timestamp ASC"
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [TraceEvent.from_row(row) for row in rows]

    def add_events(self, events: Iterable[TraceEvent]) -> list[TraceEvent]:
        saved = []
        for event in events:
            saved.append(self.add_event(event))
        return saved

    def get_stats(
        self,
        *,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
    ) -> dict:
        where, params = self._build_run_filters(status=status, run_type=run_type, agent=agent, team=team)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        with self._connect() as conn:
            summary = conn.execute(
                f"""
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(total_tokens), 0) AS total_tokens,
                    COALESCE(SUM(input_tokens), 0) AS input_tokens,
                    COALESCE(SUM(output_tokens), 0) AS output_tokens,
                    COALESCE(SUM(estimated_tokens_saved), 0) AS estimated_tokens_saved,
                    COALESCE(SUM(external_llm_used), 0) AS external_llm_runs,
                    MIN(started_at) AS first_run_at,
                    MAX(started_at) AS last_run_at,
                    COALESCE(AVG(duration_ms), 0) AS avg_duration_ms
                FROM runs
                {where_sql}
                """,
                params,
            ).fetchone()

            by_status = conn.execute(
                f"SELECT status, COUNT(*) AS count FROM runs {where_sql} GROUP BY status ORDER BY count DESC",
                params,
            ).fetchall()

            by_type = conn.execute(
                f"SELECT run_type, COUNT(*) AS count FROM runs {where_sql} GROUP BY run_type ORDER BY count DESC",
                params,
            ).fetchall()

        return {
            "filters": {
                "status": status,
                "run_type": run_type,
                "agent": agent,
                "team": team,
            },
            "total_runs": int(summary["total_runs"] or 0),
            "total_tokens": int(summary["total_tokens"] or 0),
            "input_tokens": int(summary["input_tokens"] or 0),
            "output_tokens": int(summary["output_tokens"] or 0),
            "estimated_tokens_saved": int(summary["estimated_tokens_saved"] or 0),
            "external_llm_runs": int(summary["external_llm_runs"] or 0),
            "first_run_at": summary["first_run_at"],
            "last_run_at": summary["last_run_at"],
            "avg_duration_ms": round(float(summary["avg_duration_ms"] or 0), 2),
            "by_status": {row["status"]: int(row["count"]) for row in by_status},
            "by_type": {row["run_type"]: int(row["count"]) for row in by_type},
        }

    def count_runs(
        self,
        *,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
        older_than_iso: str | None = None,
    ) -> int:
        where, params = self._build_run_filters(
            status=status,
            run_type=run_type,
            agent=agent,
            team=team,
            older_than_iso=older_than_iso,
        )
        sql = "SELECT COUNT(*) AS count FROM runs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
        return int(row["count"] or 0)

    def list_run_ids(
        self,
        *,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
        older_than_iso: str | None = None,
        limit: int | None = None,
    ) -> list[str]:
        where, params = self._build_run_filters(
            status=status,
            run_type=run_type,
            agent=agent,
            team=team,
            older_than_iso=older_than_iso,
        )
        sql = "SELECT run_id FROM runs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY started_at ASC"
        if limit:
            sql += " LIMIT ?"
            params.append(max(1, int(limit)))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [row["run_id"] for row in rows]

    def delete_run(self, run_id: str) -> bool:
        with self._connect() as conn:
            existing = conn.execute("SELECT run_id FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if not existing:
                return False
            conn.execute("DELETE FROM trace_events WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
        return True

    def prune_runs(
        self,
        *,
        status: str | None = None,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
        older_than_iso: str | None = None,
        limit: int | None = None,
        dry_run: bool = True,
    ) -> dict:
        run_ids = self.list_run_ids(
            status=status,
            run_type=run_type,
            agent=agent,
            team=team,
            older_than_iso=older_than_iso,
            limit=limit,
        )
        if dry_run:
            return {"matched": len(run_ids), "deleted": 0, "run_ids": run_ids}

        deleted = 0
        for run_id in run_ids:
            if self.delete_run(run_id):
                deleted += 1
        return {"matched": len(run_ids), "deleted": deleted, "run_ids": run_ids}

    def list_failures(
        self,
        limit: int = 20,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
    ) -> list[RunRecord]:
        """List failed runs for diagnostics."""
        return self.list_runs(limit=limit, status="failed", run_type=run_type, agent=agent, team=team)

    def get_failure_stats(
        self,
        *,
        run_type: str | None = None,
        agent: str | None = None,
        team: str | None = None,
    ) -> dict:
        """Return failure counts grouped by error type and run type."""
        where, params = self._build_run_filters(status="failed", run_type=run_type, agent=agent, team=team)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        with self._connect() as conn:
            summary = conn.execute(
                f"""
                SELECT
                    COUNT(*) AS total_failures,
                    MIN(started_at) AS first_failure_at,
                    MAX(started_at) AS last_failure_at
                FROM runs
                {where_sql}
                """,
                params,
            ).fetchone()

            by_error_type = conn.execute(
                f"""
                SELECT COALESCE(error_type, 'unknown') AS error_type, COUNT(*) AS count
                FROM runs
                {where_sql}
                GROUP BY COALESCE(error_type, 'unknown')
                ORDER BY count DESC
                """,
                params,
            ).fetchall()

            by_type = conn.execute(
                f"""
                SELECT run_type, COUNT(*) AS count
                FROM runs
                {where_sql}
                GROUP BY run_type
                ORDER BY count DESC
                """,
                params,
            ).fetchall()

        return {
            "filters": {
                "run_type": run_type,
                "agent": agent,
                "team": team,
            },
            "total_failures": int(summary["total_failures"] or 0),
            "first_failure_at": summary["first_failure_at"],
            "last_failure_at": summary["last_failure_at"],
            "by_error_type": {row["error_type"]: int(row["count"]) for row in by_error_type},
            "by_type": {row["run_type"]: int(row["count"]) for row in by_type},
        }


    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM trace_events")
            conn.execute("DELETE FROM runs")
