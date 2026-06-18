from __future__ import annotations

import json
from .models import RunRecord, TraceEvent


def _short(value: str | None, width: int = 8) -> str:
    if not value:
        return ""
    return value[:width]


def _token_summary(run: RunRecord | TraceEvent) -> str:
    total = getattr(run, "total_tokens", 0) or 0
    saved = getattr(run, "estimated_tokens_saved", 0) or 0
    source = getattr(run, "token_source", "unknown") or "unknown"
    parts = []
    if total:
        parts.append(f"tokens={total}")
    if saved:
        parts.append(f"saved≈{saved}")
    if parts:
        parts.append(f"source={source}")
    return ", ".join(parts) if parts else "tokens=n/a"


def run_to_dict(run: RunRecord, events: list[TraceEvent] | None = None) -> dict:
    data = run.to_dict()
    if events is not None:
        data["events"] = [event.to_dict() for event in events]
    return data


def format_run_json(run: RunRecord, events: list[TraceEvent] | None = None) -> str:
    return json.dumps(run_to_dict(run, events), indent=2, sort_keys=True, default=str)


def format_runs_json(runs: list[RunRecord]) -> str:
    return json.dumps([run.to_dict() for run in runs], indent=2, sort_keys=True, default=str)


def format_events_json(events: list[TraceEvent]) -> str:
    return json.dumps([event.to_dict() for event in events], indent=2, sort_keys=True, default=str)


def format_run_list(runs: list[RunRecord]) -> str:
    if not runs:
        return "No runs found."
    lines = []
    lines.append("RUNS")
    for run in runs:
        target = run.team_name or run.agent_name or run.team_id or run.agent_id or "-"
        task = (run.task or "").replace("\n", " ").strip()
        if len(task) > 70:
            task = task[:67] + "..."
        lines.append(
            f"{_short(run.run_id)}  {run.status:<10} {run.run_type:<8} {target:<18} "
            f"{_token_summary(run):<32} {task}"
        )
    return "\n".join(lines)


def _provider_used_label(run: RunRecord) -> str:
    if getattr(run, "external_llm_used", False) is False:
        return "N/A (no LLM used)"
    if run.provider and run.model:
        return f"{run.provider} / {run.model}"
    return run.provider or run.model or "-"


def _configured_provider_label(run: RunRecord) -> str:
    if run.provider and run.model:
        return f"{run.provider} / {run.model}"
    return run.provider or run.model or "-"


def format_run_summary(run: RunRecord) -> str:
    lines = ["RUN"]
    lines.append(f"id: {run.run_id}")
    lines.append(f"type: {run.run_type}")
    lines.append(f"status: {run.status}")
    if run.agent_name or run.agent_id:
        lines.append(f"agent: {run.agent_name or run.agent_id}")
    if run.team_name or run.team_id:
        lines.append(f"team: {run.team_name or run.team_id}")
    metadata = run.metadata or {}
    if metadata.get("workflow_id"):
        lines.append(f"workflow: {metadata.get('workflow_id')} ({metadata.get('workflow_name') or '-' } v{metadata.get('workflow_version') or '-'})")
    lines.append(f"provider_used: {_provider_used_label(run)}")
    if run.provider or run.model:
        lines.append(f"configured_provider: {_configured_provider_label(run)}")
    lines.append(f"external_llm_used: {run.external_llm_used}")
    lines.append(f"started_at: {run.started_at}")
    if run.ended_at:
        lines.append(f"ended_at: {run.ended_at}")
    if run.duration_ms is not None:
        lines.append(f"duration_ms: {run.duration_ms}")
    lines.append(f"input_tokens: {run.input_tokens}")
    lines.append(f"output_tokens: {run.output_tokens}")
    lines.append(f"total_tokens: {run.total_tokens}")
    lines.append(f"estimated_tokens_saved: {run.estimated_tokens_saved}")
    lines.append(f"token_source: {run.token_source}")
    if run.error_message:
        lines.append(f"error: {run.error_type}: {run.error_message}")
    lines.append(f"task: {run.task}")
    return "\n".join(lines)


def format_event_list(events: list[TraceEvent], *, title: str = "TRACE EVENTS") -> str:
    lines = [title]
    if not events:
        lines.append("No trace events found.")
        return "\n".join(lines)
    for event in events:
        token_info = _token_summary(event)
        name = f"/{event.name}" if event.name else ""
        duration = f" duration_ms={event.duration_ms}" if event.duration_ms is not None else ""

        # Build the line in explicit segments so the optional message always has
        # a readable separator. This avoids output like:
        #   source=estimated- Direct tool execution...
        line = (
            f"- [{event.timestamp}] {event.event_type} "
            f"({event.component}{name}) status={event.status}{duration} {token_info}"
        )
        if event.message:
            line += f" - {event.message}"
        lines.append(line)
    return "\n".join(lines)


def format_run_detail(run: RunRecord, events: list[TraceEvent]) -> str:
    return format_run_summary(run) + "\n\n" + format_event_list(events)
