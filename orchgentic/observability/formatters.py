from __future__ import annotations

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


def format_run_detail(run: RunRecord, events: list[TraceEvent]) -> str:
    lines = ["RUN"]
    lines.append(f"id: {run.run_id}")
    lines.append(f"type: {run.run_type}")
    lines.append(f"status: {run.status}")
    if run.agent_name or run.agent_id:
        lines.append(f"agent: {run.agent_name or run.agent_id}")
    if run.team_name or run.team_id:
        lines.append(f"team: {run.team_name or run.team_id}")
    if run.provider or run.model:
        lines.append(f"provider: {run.provider or '-'} / {run.model or '-'}")
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
    lines.append("")
    lines.append("TRACE EVENTS")
    if not events:
        lines.append("No trace events found.")
        return "\n".join(lines)
    for event in events:
        token_info = _token_summary(event)
        name = f"/{event.name}" if event.name else ""
        duration = f" duration_ms={event.duration_ms}" if event.duration_ms is not None else ""
        msg = f" - {event.message}" if event.message else ""
        lines.append(
            f"- [{event.timestamp}] {event.event_type} "
            f"({event.component}{name}) status={event.status}{duration} {token_info}{msg}"
        )
    return "\n".join(lines)
