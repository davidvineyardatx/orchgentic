from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .models import RunRecord, TraceEvent
from .store import ObservabilityStore


TOKEN_PROOF_EVENT_TYPES = {
    "routing.bypassed",
    "routing.completed",
    "reasoning.completed",
    "llm.started",
    "llm.completed",
    "llm.failed",
}


def _pct(part: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{round((part / total) * 100, 1)}%"


def _target(run: RunRecord) -> str:
    return run.team_name or run.agent_name or run.team_id or run.agent_id or "-"


def _is_local_reasoning_event(event: TraceEvent) -> bool:
    value = " ".join(
        str(item or "")
        for item in [event.event_type, event.component, event.name, event.message]
    ).lower()
    data = event.data or {}
    if data.get("local_reasoner_confidence") is not None:
        return True
    if data.get("reasoning_level") in {"local_tool", "local", "deterministic"}:
        return True
    return "local_reason" in value or "local reason" in value or event.event_type == "reasoning.completed"


def _is_deterministic_route_event(event: TraceEvent) -> bool:
    if event.event_type == "routing.bypassed":
        return True
    data = event.data or {}
    route_type = str(data.get("route_type") or event.name or "").lower()
    reasoning_level = str(data.get("reasoning_level") or "").lower()
    return event.event_type == "routing.completed" and (
        route_type in {"single_tool", "multi_tool", "direct_tool"}
        or reasoning_level in {"local_tool", "deterministic"}
    )



def _token_event_reason(event: TraceEvent) -> str:
    data = event.data or {}
    explicit_reason = data.get("token_work_reason") or data.get("reason")
    if explicit_reason:
        reason = explicit_reason
    elif event.message:
        reason = event.message
    elif event.event_type.startswith("llm."):
        purpose = data.get("llm_purpose") or event.name or "LLM call"
        actor = data.get("agent_name") or data.get("agent_id") or "agent"
        team = data.get("team")
        role = data.get("team_role") or data.get("role")
        scope = actor
        if team:
            scope += f" / team={team}"
        if role:
            scope += f" / role={role}"
        reason = f"LLM tokens used by {scope} for {purpose}."
    elif event.estimated_tokens_saved:
        reason = data.get("savings_reason") or data.get("reason") or "Estimated tokens saved by local/direct routing."
    else:
        reason = data.get("reason") or data.get("llm_purpose") or "Trace event included for token proof context."

    source_reason = data.get("token_count_source_reason")
    if source_reason and int(event.total_tokens or 0):
        reason = f"{reason} Count source: {source_reason}."
    return reason


def _token_event_meaning(event: TraceEvent) -> str:
    if int(event.total_tokens or 0):
        return "tokens_used"
    if int(event.estimated_tokens_saved or 0):
        return "tokens_saved"
    return "proof_context"


def _event_local_llm_eligible(event: TraceEvent) -> bool:
    data = event.data or {}
    if data.get("local_llm_eligible") is not None:
        return bool(data.get("local_llm_eligible"))
    if not int(event.total_tokens or 0):
        return False
    purpose = str(data.get("llm_purpose") or event.name or "").lower()
    role = str(data.get("team_role") or data.get("role") or "").lower()
    agent = str(data.get("agent_name") or data.get("agent_id") or "").lower()
    if purpose in {"tool_decision", "routing", "planning", "quality_review"}:
        return True
    if role in {"member", "researcher", "writer", "reviewer"}:
        return True
    if any(marker in agent for marker in ["research", "writer", "review"]):
        return True
    return False


def _execution_tier(event: TraceEvent) -> str:
    if int(event.estimated_tokens_saved or 0):
        return "deterministic_saved"
    if not int(event.total_tokens or 0):
        return "proof_context"
    data = event.data or {}
    explicit = data.get("execution_tier") or data.get("recommended_execution_tier")
    if explicit:
        return str(explicit)
    role = str(data.get("team_role") or data.get("role") or "").lower()
    purpose = str(data.get("llm_purpose") or event.name or "").lower()
    if role == "synthesis" or "synthesis" in purpose:
        return "premium_external_candidate"
    if _event_local_llm_eligible(event):
        return "local_llm_candidate"
    return "external_llm"


def _optimization_opportunity(event: TraceEvent) -> str:
    data = event.data or {}
    if data.get("optimization_opportunity"):
        return str(data.get("optimization_opportunity"))
    tier = _execution_tier(event)
    if tier == "deterministic_saved":
        return "already_avoided_external_llm"
    if tier == "local_llm_candidate":
        return "move_to_local_llm"
    if tier == "premium_external_candidate":
        return "keep_external_or_make_configurable"
    if tier == "proof_context":
        return "none"
    return "monitor"

def build_token_intelligence_report(
    store: ObservabilityStore,
    *,
    limit: int = 100,
    status: str | None = None,
    run_type: str | None = None,
    agent: str | None = None,
    team: str | None = None,
) -> dict[str, Any]:
    """Build a dashboard/CLI-ready proof summary for local reasoning and token savings.

    This report intentionally uses token counts only. Estimated token savings are
    operational estimates of avoided LLM routing/execution overhead, not billing claims.
    """
    limit = max(1, min(int(limit or 100), 1000))
    runs = store.list_runs(limit=limit, status=status, run_type=run_type, agent=agent, team=team)
    stats = store.get_stats(status=status, run_type=run_type, agent=agent, team=team)

    total_runs = len(runs)
    external_llm_runs = sum(1 for run in runs if run.external_llm_used)
    local_runs = total_runs - external_llm_runs
    runs_with_savings = sum(1 for run in runs if int(run.estimated_tokens_saved or 0) > 0)
    direct_tool_runs = sum(1 for run in runs if run.run_type == "tool" and not run.external_llm_used)
    total_tokens = sum(int(run.total_tokens or 0) for run in runs)
    estimated_tokens_saved = sum(int(run.estimated_tokens_saved or 0) for run in runs)
    token_work_total = total_tokens + estimated_tokens_saved

    proof_events: list[dict[str, Any]] = []
    route_counter: Counter[str] = Counter()
    event_counter: Counter[str] = Counter()
    savings_by_target: defaultdict[str, int] = defaultdict(int)
    savings_by_type: defaultdict[str, int] = defaultdict(int)
    direct_bypasses = 0
    deterministic_routes = 0
    local_reasoning_events = 0
    llm_events = 0
    external_tokens_local_candidate = 0
    external_tokens_premium_candidate = 0
    external_tokens_other = 0
    deterministic_tokens_saved = 0

    top_savings_run: RunRecord | None = None
    for run in runs:
        savings = int(run.estimated_tokens_saved or 0)
        savings_by_target[_target(run)] += savings
        savings_by_type[run.run_type or "unknown"] += savings
        if savings and (top_savings_run is None or savings > int(top_savings_run.estimated_tokens_saved or 0)):
            top_savings_run = run

        try:
            events = store.list_events(run.run_id)
        except Exception:  # pragma: no cover - defensive report fallback
            events = []
        for event in events:
            event_counter[event.event_type] += 1
            if event.event_type == "routing.bypassed":
                direct_bypasses += 1
            if event.event_type.startswith("llm."):
                llm_events += 1
            if _is_local_reasoning_event(event):
                local_reasoning_events += 1
            if _is_deterministic_route_event(event):
                deterministic_routes += 1
            if event.event_type in TOKEN_PROOF_EVENT_TYPES or event.estimated_tokens_saved or event.total_tokens:
                data = event.data or {}
                route_name = data.get("route_type") or event.name or event.event_type
                if event.event_type.startswith("routing."):
                    route_counter[str(route_name)] += 1
                event_total_tokens = int(event.total_tokens or 0)
                event_saved_tokens = int(event.estimated_tokens_saved or 0)
                event_execution_tier = _execution_tier(event)
                event_local_llm_eligible = _event_local_llm_eligible(event)
                event_optimization_opportunity = _optimization_opportunity(event)
                if event_execution_tier == "local_llm_candidate":
                    external_tokens_local_candidate += event_total_tokens
                elif event_execution_tier == "premium_external_candidate":
                    external_tokens_premium_candidate += event_total_tokens
                elif event_total_tokens:
                    external_tokens_other += event_total_tokens
                if event_saved_tokens:
                    deterministic_tokens_saved += event_saved_tokens
                proof_events.append(
                    {
                        "run_id": run.run_id,
                        "run_short_id": run.run_id[:8],
                        "run_type": run.run_type,
                        "target": _target(run),
                        "task": run.task,
                        "event_type": event.event_type,
                        "component": event.component,
                        "name": event.name,
                        "status": event.status,
                        "message": event.message,
                        "total_tokens": event_total_tokens,
                        "estimated_tokens_saved": event_saved_tokens,
                        "token_source": event.token_source,
                        "execution_tier": event_execution_tier,
                        "local_llm_eligible": event_local_llm_eligible,
                        "optimization_opportunity": event_optimization_opportunity,
                        "reason": _token_event_reason(event),
                        "token_meaning": _token_event_meaning(event),
                        "llm_purpose": data.get("llm_purpose"),
                        "agent_name": data.get("agent_name") or run.agent_name,
                        "team_role": data.get("team_role") or data.get("role"),
                        "token_count_source_reason": data.get("token_count_source_reason"),
                        "route_type": data.get("route_type") or event.name,
                    }
                )

    proof_events.sort(
        key=lambda item: (int(item.get("estimated_tokens_saved") or 0), int(item.get("total_tokens") or 0)),
        reverse=True,
    )

    return {
        "filters": {"limit": limit, "status": status, "run_type": run_type, "agent": agent, "team": team},
        "filter_summary": ", ".join(
            f"{key}={value}"
            for key, value in {"limit": limit, "status": status, "type": run_type, "agent": agent, "team": team}.items()
            if value is not None
        ),
        "loaded_runs": total_runs,
        "has_runs": total_runs > 0,
        "has_savings": estimated_tokens_saved > 0,
        "store_total_runs": int(stats.get("total_runs", 0) or 0),
        "local_runs": local_runs,
        "external_llm_runs": external_llm_runs,
        "local_run_rate": _pct(local_runs, total_runs),
        "external_llm_rate": _pct(external_llm_runs, total_runs),
        "runs_with_savings": runs_with_savings,
        "runs_with_savings_rate": _pct(runs_with_savings, total_runs),
        "direct_tool_runs": direct_tool_runs,
        "direct_bypasses": direct_bypasses,
        "deterministic_routes": deterministic_routes,
        "local_reasoning_events": local_reasoning_events,
        "llm_events": llm_events,
        "total_tokens": total_tokens,
        "estimated_tokens_saved": estimated_tokens_saved,
        "token_work_total": token_work_total,
        "local_or_deterministic_token_rate": _pct(estimated_tokens_saved, token_work_total),
        "external_llm_token_rate": _pct(total_tokens, token_work_total),
        "deterministic_tokens_saved": deterministic_tokens_saved,
        "external_tokens_used": total_tokens,
        "external_tokens_local_candidate": external_tokens_local_candidate,
        "external_tokens_premium_candidate": external_tokens_premium_candidate,
        "external_tokens_other": external_tokens_other,
        "external_tokens_optimization_rate": _pct(external_tokens_local_candidate, total_tokens),
        "token_source_note": "estimated token savings are operational estimates of avoided LLM routing/execution overhead, not billing claims",
        "route_counts": dict(route_counter),
        "event_counts": dict(event_counter),
        "savings_by_target": dict(sorted(savings_by_target.items(), key=lambda item: item[1], reverse=True)),
        "savings_by_type": dict(sorted(savings_by_type.items(), key=lambda item: item[1], reverse=True)),
        "top_savings_run": None if top_savings_run is None else {
            "run_id": top_savings_run.run_id,
            "run_short_id": top_savings_run.run_id[:8],
            "run_type": top_savings_run.run_type,
            "target": _target(top_savings_run),
            "task": top_savings_run.task,
            "estimated_tokens_saved": int(top_savings_run.estimated_tokens_saved or 0),
            "external_llm_used": bool(top_savings_run.external_llm_used),
            "token_source": top_savings_run.token_source,
        },
        "proof_events": proof_events[:25],
    }


def format_token_intelligence_report(report: dict[str, Any]) -> str:
    lines = ["TOKEN INTELLIGENCE"]
    filters = {k: v for k, v in (report.get("filters") or {}).items() if v is not None}
    if filters:
        lines.append("filters: " + ", ".join(f"{key}={value}" for key, value in filters.items()))
    lines.append(f"loaded_runs: {report.get('loaded_runs', 0)}")
    lines.append(f"token_work_total: {report.get('token_work_total', 0)}")
    lines.append(
        "local_or_deterministic_token_rate: "
        f"{report.get('local_or_deterministic_token_rate', '0%')} "
        f"({report.get('estimated_tokens_saved', 0)} saved/avoided)"
    )
    lines.append(
        "external_llm_token_rate: "
        f"{report.get('external_llm_token_rate', '0%')} "
        f"({report.get('total_tokens', 0)} used)"
    )
    lines.append(f"direct_tool_runs: {report.get('direct_tool_runs', 0)}")
    lines.append(f"direct_bypasses: {report.get('direct_bypasses', 0)}")
    lines.append(f"deterministic_routes: {report.get('deterministic_routes', 0)}")
    lines.append(f"local_reasoning_events: {report.get('local_reasoning_events', 0)}")
    lines.append(f"llm_events: {report.get('llm_events', 0)}")
    lines.append(f"total_tokens: {report.get('total_tokens', 0)}")
    lines.append(f"estimated_tokens_saved: {report.get('estimated_tokens_saved', 0)}")
    lines.append(f"external_tokens_local_candidate: {report.get('external_tokens_local_candidate', 0)} ({report.get('external_tokens_optimization_rate', '0%')})")
    lines.append(f"external_tokens_premium_candidate: {report.get('external_tokens_premium_candidate', 0)}")
    lines.append(f"token_source_note: {report.get('token_source_note')}")

    top = report.get("top_savings_run")
    if top:
        lines.append("")
        lines.append("top_savings_run:")
        lines.append(f"  run: {top.get('run_short_id')} ({top.get('run_type')})")
        lines.append(f"  target: {top.get('target')}")
        lines.append(f"  saved≈{top.get('estimated_tokens_saved', 0)}, source={top.get('token_source')}")
        lines.append(f"  external_llm_used: {top.get('external_llm_used')}")
        lines.append(f"  task: {top.get('task')}")

    proof_events = report.get("proof_events") or []
    if proof_events:
        lines.append("")
        lines.append("proof_events:")
        for event in proof_events[:10]:
            token_bits = []
            if event.get("estimated_tokens_saved"):
                token_bits.append(f"saved≈{event.get('estimated_tokens_saved')}")
            if event.get("total_tokens"):
                token_bits.append(f"tokens={event.get('total_tokens')}")
            token_bits.append(f"source={event.get('token_source')}")
            reason = event.get("reason") or ""
            suffix = f" - {reason}" if reason else ""
            tier = event.get("execution_tier") or "-"
            opportunity = event.get("optimization_opportunity") or "-"
            lines.append(
                f"  - {event.get('run_short_id')} {event.get('event_type')} "
                f"({event.get('component')}/{event.get('name') or '-'}) "
                f"{', '.join(token_bits)} tier={tier} opportunity={opportunity}{suffix}"
            )
    else:
        lines.append("")
        lines.append("proof_events: none yet")
        lines.append("hint: run `orch tool run datetime.local --agent Bob` to create a direct-tool token-savings proof.")

    return "\n".join(lines)
