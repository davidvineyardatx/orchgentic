from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import RunRecord, TraceEvent, utc_now_iso
from .store import ObservabilityStore

SCHEMA_VERSION = "orchgentic.observability.v1"


def _run_payload(run: RunRecord) -> dict[str, Any]:
    """Return the stable dashboard/export representation for a run."""
    return run.to_dict()


def _event_payload(event: TraceEvent) -> dict[str, Any]:
    """Return the stable dashboard/export representation for a trace event."""
    return event.to_dict()


def build_run_export(run: RunRecord, events: list[TraceEvent]) -> dict[str, Any]:
    """Build a dashboard-ready export wrapper for one run.

    The wrapper is intentionally versioned from the first export release so future
    dashboard, JSON, JSONL, OpenTelemetry, or third-party exporter changes have a
    stable compatibility boundary.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at": utc_now_iso(),
        "export_type": "run_detail",
        "run": _run_payload(run),
        "events": [_event_payload(event) for event in events],
    }


def build_run_summary_export(run: RunRecord) -> dict[str, Any]:
    """Build one JSONL row for run-history export."""
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at": utc_now_iso(),
        "export_type": "run_summary",
        "run": _run_payload(run),
    }


def export_run_detail(store: ObservabilityStore, run_id: str, *, pretty: bool = True) -> str:
    """Export one run and its trace events as JSON text."""
    run = store.get_run(run_id)
    if not run:
        raise ValueError(f"Run not found: {run_id}")
    payload = build_run_export(run, store.list_events(run.run_id))
    return json.dumps(payload, indent=2 if pretty else None, sort_keys=True, default=str)


def export_runs_jsonl(
    store: ObservabilityStore,
    *,
    limit: int = 100,
    status: str | None = None,
    run_type: str | None = None,
    agent: str | None = None,
    team: str | None = None,
) -> str:
    """Export run history as newline-delimited JSON.

    JSONL is used for dashboard ingestion and future batch processing because each
    run summary is independently parseable and streams cleanly for large histories.
    """
    runs = store.list_runs(limit=limit, status=status, run_type=run_type, agent=agent, team=team)
    rows = [build_run_summary_export(run) for run in runs]
    return "\n".join(json.dumps(row, sort_keys=True, default=str) for row in rows)


def write_export_text(text: str, output_path: str | Path) -> Path:
    """Write export text to disk, creating parent directories when needed."""
    path = Path(output_path)
    if path.parent and str(path.parent) not in {"", "."}:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
