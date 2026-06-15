from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment
from orchgentic.runtime.metrics import record_route_metric
from orchgentic.runtime.token_estimator import estimate_route_savings
import time
from orchgentic.runtime.deterministic_formatter import DeterministicFormatter
from orchgentic.runtime.deterministic_router import DeterministicRouter
from orchgentic.runtime.cost_tracker import build_route_telemetry, append_route_log
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import re
import typer
import uvicorn
import webbrowser
from orchgentic.connectors.gmail.oauth import connect_gmail
from orchgentic.connectors.gmail.storage import list_connections, read_account, delete_connection
from orchgentic.scaffold import create_agent_file, create_team_file, create_trigger_file
from orchgentic.workspace import init_workspace
from orchgentic.config.loader import load_agent, load_trigger, load_all_triggers
from orchgentic.providers.factory import create_provider
from orchgentic.agents.assistant import AssistantAgent
from orchgentic.agents.registry import AgentRegistry
from orchgentic.capabilities.registry import CapabilityRegistry
from orchgentic.memory.manager import MemoryManager
from orchgentic.knowledge.manager import KnowledgeManager
from orchgentic.triggers.models import TriggerEvent
from orchgentic.triggers.dispatcher import TriggerDispatcher
from orchgentic.triggers.heartbeat import HeartbeatTriggerRunner
from orchgentic.triggers.webhook_server import create_webhook_app
from orchgentic.tools.registry import default_tool_registry
from orchgentic.teams.registry import TeamRegistry
from orchgentic.orchestration.team_runner import TeamRunner
from orchgentic.runtime.preflight import CapabilityPreflight
from orchgentic.observability import ObservabilityStore, TraceCollector
from orchgentic.observability.policy_preview import preview_tool_policy_decision
from orchgentic.observability.formatters import (
    format_run_list,
    format_run_detail,
    format_run_summary,
    format_event_list,
    format_run_json,
    format_runs_json,
    format_events_json,
)
from orchgentic.observability.exporters import (
    export_run_detail,
    export_runs_jsonl,
    write_export_text,
)
from orchgentic.observability.dashboard import (
    DEFAULT_DASHBOARD_PATH,
    build_dashboard_html,
    write_dashboard_html,
)

app = typer.Typer()
connect_app = typer.Typer(help="Connect external accounts.")
gmail_app = typer.Typer(help="Manage Gmail connections.")
create_app = typer.Typer(help="Create Orchgentic configuration files.")
memory_app = typer.Typer()
create_app = typer.Typer(help="Create Orchgentic configuration files.")
trigger_app = typer.Typer()
create_app = typer.Typer(help="Create Orchgentic configuration files.")
knowledge_app = typer.Typer()
create_app = typer.Typer(help="Create Orchgentic configuration files.")
tool_app = typer.Typer()
create_app = typer.Typer(help="Create Orchgentic configuration files.")

app.add_typer(memory_app, name="memory")
app.add_typer(trigger_app, name="trigger")
app.add_typer(knowledge_app, name="knowledge")
app.add_typer(tool_app, name="tool")
app.add_typer(create_app, name="create")
app.add_typer(connect_app, name="connect")
app.add_typer(gmail_app, name="gmail")

def _agent_path(name):
    return Path("agents") / (name.lower() if name.lower().endswith(".yaml") else f"{name.lower()}.yaml")

def _trigger_path(name):
    return Path("triggers") / (name.lower() if name.lower().endswith(".yaml") else f"{name.lower()}.yaml")



def _parse_tool_args(arg_items):
    parsed = {}
    for item in arg_items or []:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --arg value '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise typer.BadParameter("Invalid --arg value. Key cannot be empty.")

        lowered = value.lower()
        if lowered == "true":
            parsed[key] = True
        elif lowered == "false":
            parsed[key] = False
        elif lowered in {"none", "null"}:
            parsed[key] = None
        else:
            try:
                parsed[key] = int(value)
            except ValueError:
                try:
                    parsed[key] = float(value)
                except ValueError:
                    parsed[key] = value
    return parsed



def _parse_retention_window(value: str | None) -> str | None:
    """Convert a simple retention window like 30d, 12h, or 2w to a UTC ISO cutoff."""
    if not value:
        return None
    raw = value.strip().lower()
    match = re.match(r"^(\d+)([dhw])$", raw)
    if not match:
        raise typer.BadParameter("Expected --older-than in the form 30d, 12h, or 2w.")
    amount = int(match.group(1))
    unit = match.group(2)
    if amount <= 0:
        raise typer.BadParameter("--older-than must be greater than zero.")
    if unit == "h":
        delta = timedelta(hours=amount)
    elif unit == "d":
        delta = timedelta(days=amount)
    elif unit == "w":
        delta = timedelta(weeks=amount)
    else:
        raise typer.BadParameter("Unsupported retention unit.")
    return (datetime.now(timezone.utc) - delta).isoformat()


def _format_stats(stats: dict) -> str:
    lines = ["RUN STATS"]
    filters = {k: v for k, v in (stats.get("filters") or {}).items() if v}
    if filters:
        lines.append("filters: " + ", ".join(f"{k}={v}" for k, v in filters.items()))
    lines.append(f"total_runs: {stats.get('total_runs', 0)}")
    lines.append(f"external_llm_runs: {stats.get('external_llm_runs', 0)}")
    lines.append(f"total_tokens: {stats.get('total_tokens', 0)}")
    lines.append(f"input_tokens: {stats.get('input_tokens', 0)}")
    lines.append(f"output_tokens: {stats.get('output_tokens', 0)}")
    lines.append(f"estimated_tokens_saved: {stats.get('estimated_tokens_saved', 0)}")
    lines.append(f"avg_duration_ms: {stats.get('avg_duration_ms', 0)}")
    if stats.get("first_run_at"):
        lines.append(f"first_run_at: {stats.get('first_run_at')}")
    if stats.get("last_run_at"):
        lines.append(f"last_run_at: {stats.get('last_run_at')}")

    by_status = stats.get("by_status") or {}
    if by_status:
        lines.append("")
        lines.append("by_status:")
        for key, value in by_status.items():
            lines.append(f"  {key}: {value}")

    by_type = stats.get("by_type") or {}
    if by_type:
        lines.append("")
        lines.append("by_type:")
        for key, value in by_type.items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)



async def _try_deterministic_route(task, cfg, registry, debug=False, tracer=None):
    route_start = time.perf_counter()
    router = DeterministicRouter()
    decision = router.route(task, agent_config=cfg)

    if not decision.matched or decision.requires_llm:
        return None

    provider_cfg = getattr(cfg, "provider", None)
    provider_type = getattr(provider_cfg, "type", None) if provider_cfg is not None else None
    provider_model = getattr(provider_cfg, "model", None) if provider_cfg is not None else None
    token_estimate = estimate_route_savings(
        system_prompt=getattr(cfg, "instructions", ""),
        tool_context={"selected_tool": getattr(decision, "tool", None), "arguments": getattr(decision, "arguments", {})},
        task=task,
        expected_completion_tokens=300,
    )

    formatter = DeterministicFormatter()
    selected_tool = decision.tool or (decision.steps[0].tool if decision.steps else None)

    telemetry = build_route_telemetry(
        route_type=getattr(decision, "route_type", "single_tool"),
        external_llm_used=False,
        selected_tool=selected_tool,
        confidence=decision.confidence,
        reason=decision.reason,
        estimated_external_tokens_saved=token_estimate.total,
        execution_time_ms=round((time.perf_counter() - route_start) * 1000, 2),
        agent=getattr(cfg, "name", None),
        provider=provider_type,
        model=provider_model,
        token_estimate=token_estimate.to_dict(),
        local_reasoner_confidence=decision.confidence,
        escalation_reason="not_required",
        reasoning_level="local_tool",
    )

    # Deterministic routes still execute inside an agent run when invoked through
    # `orch run <agent>`. Validate the selected tool route before emitting
    # agent-level events so fallback-to-LLM paths do not leave orphaned spans.
    if getattr(decision, "route_type", "single_tool") == "multi_tool":
        for step in decision.steps:
            if not registry.get(step.tool):
                return None
    else:
        if not registry.get(decision.tool):
            return None

    agent_started_at = time.perf_counter()

    def _emit_agent_completed(status: str = "completed", message: str = "Agent deterministic route completed."):
        if tracer:
            tracer.event(
                "agent.completed" if status == "completed" else "agent.failed",
                component="agent",
                name=getattr(cfg, "name", None),
                status=status,
                message=message,
                duration_ms=round((time.perf_counter() - agent_started_at) * 1000, 2),
                data={"deterministic_route": True, "selected_tool": selected_tool},
            )

    if tracer:
        tracer.event(
            "agent.started",
            component="agent",
            name=getattr(cfg, "name", None),
            status="started",
            message="Agent deterministic route started.",
            data={"agent_id": getattr(cfg, "id", None), "deterministic_route": True},
        )
        tracer.event(
            "routing.completed",
            component="routing",
            name=getattr(decision, "route_type", "single_tool"),
            status="completed",
            message=decision.reason,
            duration_ms=telemetry.get("execution_time_ms"),
            estimated_tokens_saved=token_estimate.total,
            token_source="estimated",
            data=telemetry,
        )

    try:
        append_route_log("logs/routes.jsonl", telemetry)
        record_route_metric(telemetry)
    except Exception:
        pass

    tool_events = []

    if getattr(decision, "route_type", "single_tool") == "multi_tool":
        context = {}
        final_data = {}

        for step in decision.steps:
            tool = registry.get(step.tool)
            if not tool:
                return None

            # Resolve simple reference pattern: $search.messages[].id
            if step.arguments.get("message_id") == "$search.messages[].id":
                messages = ((context.get("search") or {}).get("messages") or [])
                read_messages = []
                for item in messages:
                    message_id = item.get("id")
                    if not message_id:
                        continue
                    if tracer:
                        tracer.event("tool.started", component="tool", name=step.tool, status="started", data={"arguments": {"message_id": message_id}})
                    result = await tool.execute(message_id=message_id)
                    if tracer:
                        tracer.event("tool.completed" if getattr(result, "success", False) else "tool.failed", component="tool", name=step.tool, status="completed" if getattr(result, "success", False) else "failed", message=getattr(result, "error", None), data={"arguments": {"message_id": message_id}, "success": getattr(result, "success", None)})
                    tool_events.append({
                        "tool": step.tool,
                        "arguments": {"message_id": message_id},
                        "success": getattr(result, "success", None),
                        "error": getattr(result, "error", None),
                    })
                    if getattr(result, "success", False):
                        read_messages.append(getattr(result, "data", {}))
                context[step.result_key or step.tool] = read_messages
                final_data["messages"] = read_messages
                continue

            if tracer:
                tracer.event("tool.started", component="tool", name=step.tool, status="started", data={"arguments": step.arguments})
            result = await tool.execute(**step.arguments)
            if tracer:
                tracer.event("tool.completed" if getattr(result, "success", False) else "tool.failed", component="tool", name=step.tool, status="completed" if getattr(result, "success", False) else "failed", message=getattr(result, "error", None), data={"arguments": step.arguments, "success": getattr(result, "success", None)})
            tool_events.append({
                "tool": step.tool,
                "arguments": step.arguments,
                "success": getattr(result, "success", None),
                "error": getattr(result, "error", None),
            })

            if not getattr(result, "success", False):
                if debug:
                    typer.echo("ROUTING")
                    typer.echo(telemetry)
                    typer.echo("")
                    typer.echo("TOOLS")
                    typer.echo(tool_events)
                    typer.echo("")
                _emit_agent_completed(status="failed", message=getattr(result, "error", None) or "Deterministic route tool failed.")
                return result

            context[step.result_key or step.tool] = getattr(result, "data", {})
            final_data[step.result_key or step.tool] = getattr(result, "data", {})

        if debug:
            typer.echo("ROUTING")
            typer.echo(telemetry)
            typer.echo("")
            typer.echo("TOOLS")
            typer.echo(tool_events)
            typer.echo("")

        class FormattedResult:
            success = True
            error = None
            data = formatter.format(decision.formatter, final_data)

        _emit_agent_completed()
        return FormattedResult()

    tool = registry.get(decision.tool)
    if not tool:
        return None

    if tracer:
        tracer.event("tool.started", component="tool", name=decision.tool, status="started", data={"arguments": decision.arguments})
    result = await tool.execute(**decision.arguments)
    if tracer:
        tracer.event("tool.completed" if getattr(result, "success", False) else "tool.failed", component="tool", name=decision.tool, status="completed" if getattr(result, "success", False) else "failed", message=getattr(result, "error", None), data={"arguments": decision.arguments, "success": getattr(result, "success", None)})
    tool_events.append({
        "tool": decision.tool,
        "arguments": decision.arguments,
        "success": getattr(result, "success", None),
        "error": getattr(result, "error", None),
    })

    if debug:
        typer.echo("ROUTING")
        typer.echo(telemetry)
        typer.echo("")
        typer.echo("TOOLS")
        typer.echo(tool_events)
        typer.echo("")

    if getattr(result, "success", False):
        class FormattedResult:
            success = True
            error = None
            data = formatter.format(decision.formatter, result)
        _emit_agent_completed()
        return FormattedResult()

    _emit_agent_completed(status="failed", message=getattr(result, "error", None) or "Deterministic route tool failed.")
    return result


@connect_app.command("gmail")
def connect_gmail_command(
    name: str = typer.Option("default", "--name", help="Named Gmail connection, such as assistant, bob, support, sales, or founder."),
    credentials: str = typer.Option(None, "--credentials", help="Optional path to Google OAuth credentials JSON."),
):
    """Connect a named Gmail account using browser OAuth."""
    try:
        info = connect_gmail(name=name, credentials_file=credentials)
    except Exception as exc:
        typer.echo(f"Gmail connection failed: {exc}")
        raise typer.Exit(1)

    typer.echo("Gmail connected:")
    typer.echo(f"name: {info.get('name')}")
    typer.echo(f"email: {info.get('email') or 'unknown'}")


@gmail_app.command("list")
def gmail_list():
    """List named Gmail connections."""
    connections = list_connections()
    if not connections:
        typer.echo("No Gmail connections found.")
        return

    for item in connections:
        account = read_account(item) or {}
        typer.echo(f"{item}: {account.get('email', 'unknown')}")


@gmail_app.command("status")
def gmail_status(
    name: str = typer.Option(None, "--name", help="Optional named Gmail connection."),
):
    """Show Gmail connection status."""
    if name:
        account = read_account(name)
        if not account:
            typer.echo(f"Gmail connection not found: {name}")
            raise typer.Exit(1)
        typer.echo(f"{name}: {account.get('email', 'unknown')}")
        return

    connections = list_connections()
    if not connections:
        typer.echo("No Gmail connections found.")
        return

    for item in connections:
        account = read_account(item) or {}
        typer.echo(f"{item}: {account.get('email', 'unknown')}")


@gmail_app.command("disconnect")
def gmail_disconnect(
    name: str = typer.Option("default", "--name", help="Named Gmail connection to remove."),
):
    """Disconnect and remove a named Gmail connection token."""
    if delete_connection(name):
        typer.echo(f"Removed Gmail connection: {name}")
    else:
        typer.echo(f"Gmail connection not found: {name}")


@app.command()
def init(path: str = "."):
    init_workspace(path)
    typer.echo(f"Workspace initialized at {Path(path).resolve()}")



@app.command("judge-route")
def judge_route(
    task: str = typer.Argument(...),
    agent_name: str = typer.Option("Bob", "--agent"),
    event_type: str = typer.Option("manual", "--event-type", help="manual, heartbeat, webhook, scheduled, or unknown."),
):
    """Evaluate local reasoner, workflow, event, policy, and escalation judgment for a task."""
    cfg = load_agent(_agent_path(agent_name))
    provider = create_provider(cfg.provider)
    memory = MemoryManager(cfg.memory.db_path)
    knowledge = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
    registry = default_tool_registry(memory, knowledge, source_agent_config=cfg)
    typer.echo(evaluate_orchestration_judgment(task, cfg=cfg, registry=registry, event_context={"event_type": event_type, "source": "cli"}))


@app.command("route-metrics")
def route_metrics():
    """Show aggregated route metrics."""
    from orchgentic.runtime.metrics import load_metrics
    metrics = load_metrics()
    typer.echo(metrics.summary())



def _resolve_run(store: ObservabilityStore, run_id: str):
    run = store.get_run(run_id)
    if run is not None:
        return run
    matches = [item for item in store.list_runs(limit=500) if item.run_id.startswith(run_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        typer.echo(f"Run prefix is ambiguous: {run_id}")
        for item in matches[:20]:
            typer.echo(f"- {item.run_id} {item.status} {item.run_type} {item.task}")
        raise typer.Exit(1)
    typer.echo(f"Run not found: {run_id}")
    raise typer.Exit(1)


def _failure_target(run) -> str:
    return run.team_name or run.agent_name or run.team_id or run.agent_id or "-"


def _failure_summary_from_events(run, events) -> tuple[str, str, str | None, str | None]:
    failed_events = [
        event for event in events
        if event.status == "failed" or event.event_type.endswith(".failed")
    ]
    last_failed = failed_events[-1] if failed_events else None
    error_type = run.error_type or (last_failed.event_type if last_failed else "unknown")
    error_message = run.error_message or (last_failed.message if last_failed else None)
    failed_event_type = last_failed.event_type if last_failed else None
    failed_component = last_failed.component if last_failed else None
    summary = error_message or "Run failed. Inspect trace events for details."
    summary = str(summary).replace("\n", " ").strip()
    if len(summary) > 100:
        summary = summary[:97] + "..."
    return error_type, summary, failed_event_type, failed_component


def _failure_items(store: ObservabilityStore, runs) -> list[dict]:
    items = []
    for run in runs:
        events = store.list_events(run.run_id)
        error_type, summary, failed_event_type, failed_component = _failure_summary_from_events(run, events)
        items.append({
            "run_id": run.run_id,
            "short_run_id": run.run_id[:8],
            "run_type": run.run_type,
            "status": run.status,
            "target": _failure_target(run),
            "agent_id": run.agent_id,
            "agent_name": run.agent_name,
            "team_id": run.team_id,
            "team_name": run.team_name,
            "started_at": run.started_at,
            "duration_ms": run.duration_ms,
            "error_type": error_type,
            "summary": summary,
            "failed_event_type": failed_event_type,
            "failed_component": failed_component,
            "task": run.task,
        })
    return items


def _format_failures(items: list[dict], *, group_by: str | None = None) -> str:
    if not items:
        return "No failures found."

    if group_by == "error_type":
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(item["error_type"] or "unknown", []).append(item)

        lines = ["FAILURES BY ERROR TYPE"]
        for error_type, group in sorted(grouped.items(), key=lambda pair: len(pair[1]), reverse=True):
            lines.append("")
            lines.append(f"{error_type}: {len(group)}")
            for item in group:
                lines.append(
                    f"  - {item['short_run_id']} {item['run_type']} {item['target']} - {item['summary']}"
                )
        return "\n".join(lines)

    lines = ["FAILURES"]
    for item in items:
        lines.append(
            f"{item['short_run_id']}  {item['run_type']:<8} {item['target']:<18} "
            f"{item['error_type']:<24} {item['summary']}"
        )
    return "\n".join(lines)


@app.command("runs")
def runs(
    limit: int = typer.Option(20, "--limit", help="Number of recent runs to show."),
    status: str = typer.Option(None, "--status", help="Optional status filter, such as completed, failed, blocked, or hold_for_confirmation."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    json_output: bool = typer.Option(False, "--json", help="Output run list as JSON."),
):
    """List recent Orchgentic runs from the observability store."""
    store = ObservabilityStore()
    items = store.list_runs(limit=limit, status=status, run_type=run_type, agent=agent, team=team)
    typer.echo(format_runs_json(items) if json_output else format_run_list(items))


@app.command("run-info")
def run_info(
    run_id: str,
    json_output: bool = typer.Option(False, "--json", help="Output run and events as JSON."),
    events_only: bool = typer.Option(False, "--events-only", help="Show trace events only."),
    summary_only: bool = typer.Option(False, "--summary-only", help="Show run summary only."),
):
    """Show one run and its trace events."""
    if events_only and summary_only:
        typer.echo("Use either --events-only or --summary-only, not both.")
        raise typer.Exit(1)
    store = ObservabilityStore()
    run = _resolve_run(store, run_id)
    events = store.list_events(run.run_id)
    if json_output:
        if events_only:
            typer.echo(format_events_json(events))
        elif summary_only:
            typer.echo(format_run_json(run))
        else:
            typer.echo(format_run_json(run, events))
        return
    if events_only:
        typer.echo(format_event_list(events))
    elif summary_only:
        typer.echo(format_run_summary(run))
    else:
        typer.echo(format_run_detail(run, events))


@app.command("trace")
def trace(
    run_id: str,
    json_output: bool = typer.Option(False, "--json", help="Output trace events as JSON."),
    event_type: str = typer.Option(None, "--type", help="Optional event type filter, such as tool.completed."),
    component: str = typer.Option(None, "--component", help="Optional component filter, such as tool, policy, routing, provider, agent, team."),
    tokens: bool = typer.Option(False, "--tokens", help="Only show events with token usage or estimated token savings."),
):
    """Show trace events for one run."""
    store = ObservabilityStore()
    run = _resolve_run(store, run_id)
    events = store.list_events(run.run_id, event_type=event_type, component=component, tokens_only=tokens)
    typer.echo(format_events_json(events) if json_output else format_event_list(events))


@app.command("export-run")
def export_run(
    run_id: str,
    output: Path = typer.Option(None, "--output", "-o", help="Optional path to write the run export JSON."),
    compact: bool = typer.Option(False, "--compact", help="Emit compact JSON instead of pretty JSON."),
):
    """Export one run and its events as dashboard-ready JSON."""
    store = ObservabilityStore()
    run = _resolve_run(store, run_id)
    text = export_run_detail(store, run.run_id, pretty=not compact)
    if output:
        write_export_text(text, output)
        typer.echo(f"Exported run {run.run_id} to {output}")
    else:
        typer.echo(text)


@app.command("export-runs")
def export_runs(
    limit: int = typer.Option(100, "--limit", help="Number of recent runs to export."),
    status: str = typer.Option(None, "--status", help="Optional status filter, such as completed, failed, blocked, or hold_for_confirmation."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    output: Path = typer.Option(None, "--output", "-o", help="Optional path to write JSONL run history export."),
):
    """Export run history as dashboard-ready JSONL."""
    store = ObservabilityStore()
    text = export_runs_jsonl(store, limit=limit, status=status, run_type=run_type, agent=agent, team=team)
    if output:
        write_export_text(text, output)
        typer.echo(f"Exported run history to {output}")
    else:
        typer.echo(text)




@app.command("dashboard")
def dashboard(
    output: Path = typer.Option(DEFAULT_DASHBOARD_PATH, "--output", "-o", help="Path to write the static HTML dashboard."),
    limit: int = typer.Option(100, "--limit", help="Number of recent runs to include."),
    status: str = typer.Option(None, "--status", help="Optional status filter."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    open_browser: bool = typer.Option(False, "--open", help="Open the generated dashboard in the default browser."),
):
    """Generate a static local observability dashboard HTML file."""
    store = ObservabilityStore()
    html = build_dashboard_html(
        store,
        limit=limit,
        status=status,
        run_type=run_type,
        agent=agent,
        team=team,
    )
    path = write_dashboard_html(html, output)
    typer.echo(f"Generated observability dashboard: {path}")
    if open_browser:
        webbrowser.open(path.resolve().as_uri())

@app.command("failures")
def failures(
    limit: int = typer.Option(20, "--limit", help="Number of failed runs to show."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    group_by: str = typer.Option(None, "--group-by", help="Optional grouping. Supported: error_type."),
    json_output: bool = typer.Option(False, "--json", help="Output failures as JSON."),
):
    """Show failed runs with concise diagnostics."""
    if group_by and group_by != "error_type":
        typer.echo("Unsupported --group-by value. Supported: error_type.")
        raise typer.Exit(1)

    store = ObservabilityStore()
    runs = store.list_failures(limit=limit, run_type=run_type, agent=agent, team=team)
    items = _failure_items(store, runs)

    if json_output:
        payload = {
            "failures": items,
            "stats": store.get_failure_stats(run_type=run_type, agent=agent, team=team),
        }
        typer.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return

    typer.echo(_format_failures(items, group_by=group_by))

@app.command("runs-stats")
def runs_stats(
    status: str = typer.Option(None, "--status", help="Optional status filter."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    json_output: bool = typer.Option(False, "--json", help="Output stats as JSON."),
):
    """Show observability run statistics."""
    store = ObservabilityStore()
    stats = store.get_stats(status=status, run_type=run_type, agent=agent, team=team)
    typer.echo(json.dumps(stats, indent=2, sort_keys=True, default=str) if json_output else _format_stats(stats))


@app.command("runs-prune")
def runs_prune(
    older_than: str = typer.Option(None, "--older-than", help="Only match runs older than this window, such as 30d, 12h, or 2w."),
    status: str = typer.Option(None, "--status", help="Optional status filter."),
    run_type: str = typer.Option(None, "--type", help="Optional run type filter, such as agent, team, or tool."),
    agent: str = typer.Option(None, "--agent", help="Optional agent name or id filter."),
    team: str = typer.Option(None, "--team", help="Optional team name or id filter."),
    limit: int = typer.Option(None, "--limit", help="Optional maximum number of matching runs to delete."),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Preview matching runs without deleting. Enabled by default."),
    confirm: bool = typer.Option(False, "--confirm", help="Required to actually delete runs."),
):
    """Prune old or filtered observability run records safely."""
    cutoff = _parse_retention_window(older_than)
    store = ObservabilityStore()

    if not dry_run and not confirm:
        typer.echo("Refusing to delete runs without --confirm. Use --dry-run first, then --no-dry-run --confirm.")
        raise typer.Exit(1)

    result = store.prune_runs(
        status=status,
        run_type=run_type,
        agent=agent,
        team=team,
        older_than_iso=cutoff,
        limit=limit,
        dry_run=dry_run,
    )

    mode = "DRY RUN" if dry_run else "PRUNE"
    typer.echo(f"{mode}: matched {result['matched']} run(s), deleted {result['deleted']} run(s).")
    if result["run_ids"]:
        typer.echo("run_ids:")
        for run_id in result["run_ids"][:50]:
            typer.echo(f"- {run_id}")
        if len(result["run_ids"]) > 50:
            typer.echo(f"... {len(result['run_ids']) - 50} more")


@app.command("run-delete")
def run_delete(
    run_id: str,
    confirm: bool = typer.Option(False, "--confirm", help="Required to delete the run and its trace events."),
):
    """Delete one observability run and its trace events."""
    if not confirm:
        typer.echo("Refusing to delete run without --confirm.")
        raise typer.Exit(1)
    store = ObservabilityStore()
    run = _resolve_run(store, run_id)
    deleted = store.delete_run(run.run_id)
    if deleted:
        typer.echo(f"Deleted run {run.run_id}.")
    else:
        typer.echo(f"Run not found: {run_id}")
        raise typer.Exit(1)

@app.command("list-agents")
def list_agents():
    registry = AgentRegistry()
    agents = registry.list_agents()
    if not agents:
        typer.echo("No agents found.")
        return
    for cfg in agents:
        typer.echo(f"{cfg.name} ({cfg.id}) - {cfg.role}")

@app.command("inspect-agent")
def inspect_agent(agent_name: str):
    cfg = AgentRegistry().get_agent(agent_name)
    if not cfg:
        typer.echo(f"Agent not found: {agent_name}")
        raise typer.Exit(1)
    typer.echo(f"Name: {cfg.name}")
    typer.echo(f"ID: {cfg.id}")
    typer.echo(f"Role: {cfg.role}")
    typer.echo(f"Provider: {cfg.provider.type}/{cfg.provider.model}")
    typer.echo(f"Capabilities: {', '.join(cfg.capabilities)}")
    typer.echo(f"Tools: {', '.join(cfg.tools)}")
    typer.echo(f"Delegation enabled: {cfg.delegation.enabled}")
    typer.echo(f"Allowed agents: {', '.join(cfg.delegation.allowed_agents)}")

@app.command("preflight-agent")
def preflight_agent(agent_name: str, task: str = typer.Option(..., "--task")):
    cfg = AgentRegistry().get_agent(agent_name)
    if not cfg:
        typer.echo(f"Agent not found: {agent_name}")
        raise typer.Exit(1)

    issues = CapabilityPreflight().check_agent_task(cfg, task)
    if not issues:
        typer.echo("Preflight passed.")
        return

    for issue in issues:
        typer.echo(issue.to_text())
    raise typer.Exit(1)

@app.command("list-teams")
def list_teams():
    teams = TeamRegistry().list_teams()
    if not teams:
        typer.echo("No teams found.")
        return
    for team in teams:
        typer.echo(f"{team.name}: orchestrator={team.orchestrator}, members={', '.join(team.members)}")

@app.command("inspect-team")
def inspect_team(team_name: str):
    team = TeamRegistry().get_team(team_name)
    if not team:
        typer.echo(f"Team not found: {team_name}")
        raise typer.Exit(1)

    typer.echo(f"Name: {team.name}")
    typer.echo(f"Description: {team.description}")
    typer.echo(f"Orchestrator: {team.orchestrator}")
    typer.echo(f"Members: {', '.join(team.members)}")
    typer.echo(f"Shared context: {team.shared_context}")
    typer.echo(f"Max rounds: {team.max_rounds}")

    typer.echo("\nTeam tool availability:")
    registry = AgentRegistry()
    agent_names = [team.orchestrator] + [m for m in team.members if m != team.orchestrator]
    for name in agent_names:
        cfg = registry.get_agent(name)
        if cfg:
            tools = sorted(set((cfg.tools or []) + [cap for cap in cfg.capabilities if "." in cap]))
            typer.echo(f"- {cfg.name}: {', '.join(tools) if tools else 'No tools configured'}")

@app.command("preflight-team")
def preflight_team(team_name: str, task: str = typer.Option(..., "--task")):
    team = TeamRegistry().get_team(team_name)
    if not team:
        typer.echo(f"Team not found: {team_name}")
        raise typer.Exit(1)

    registry = AgentRegistry()
    agent_names = [team.orchestrator] + [m for m in team.members if m != team.orchestrator]
    agent_configs = [registry.get_agent(name) for name in agent_names]
    agent_configs = [cfg for cfg in agent_configs if cfg]

    issues = CapabilityPreflight().check_team_task(team, agent_configs, task)
    if not issues:
        typer.echo("Preflight passed.")
        return

    for issue in issues:
        typer.echo(issue.to_text())
        typer.echo("")
    if any(issue.severity.value in ["severe", "critical"] for issue in issues):
        raise typer.Exit(1)

@app.command("run-team")
def run_team(
    team_name: str,
    debug: bool = typer.Option(False, "--debug"),
    no_preflight: bool = typer.Option(False, "--no-preflight")
):
    async def _run():
        team = TeamRegistry().get_team(team_name)
        if not team:
            typer.echo(f"Team not found: {team_name}")
            raise typer.Exit(1)
        task = typer.prompt("Team task", default=team.task)
        tracer = TraceCollector()
        tracer.start_run(run_type="team", task=task, team_id=getattr(team, "id", None), team_name=team.name, metadata={"source": "cli", "debug": debug})
        try:
            result = await TeamRunner().run_team(team, task=task, debug=debug, preflight=not no_preflight, tracer=tracer)
            tracer.complete_run(status="completed", message="Team run completed.")
        except RuntimeError as exc:
            tracer.fail_run(exc)
            typer.echo(str(exc))
            raise typer.Exit(1)
        except Exception as exc:
            tracer.fail_run(exc)
            raise

        typer.echo("TEAM FINAL")
        typer.echo(result["final"])
        if debug:
            typer.echo("\nTEAM OUTPUTS")
            typer.echo(result["outputs"])
    asyncio.run(_run())

@app.command("list-capabilities")
def list_capabilities():
    registry = CapabilityRegistry()
    for capability in registry.list():
        typer.echo(f"{capability}: {', '.join(registry.resolve(capability))}")

@app.command("list-tools")
def list_tools(agent_name: str = typer.Option("Bob", "--agent")):
    cfg = load_agent(_agent_path(agent_name))
    provider = create_provider(cfg.provider)
    memory = MemoryManager(cfg.memory.db_path)
    knowledge = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
    registry = default_tool_registry(memory, knowledge, source_agent_config=cfg)
    allowed = sorted(set((cfg.tools or []) + [cap for cap in cfg.capabilities if "." in cap]))

    for definition in registry.definitions(allowed or None):
        typer.echo(f"{definition['name']}: {definition['description']}")

@app.command("list-triggers")
def list_triggers():
    triggers = load_all_triggers("triggers")

    if not triggers:
        typer.echo("No triggers found.")
        return

    for trigger in triggers:
        detail = f"every {trigger.interval_seconds}s" if trigger.type == "heartbeat" else (trigger.path or "")
        typer.echo(f"{trigger.id}: {trigger.type} -> {trigger.target_agent} {detail} enabled={trigger.enabled}")

@app.command()
def run(
    agent_name: str,
    debug: bool = typer.Option(False, "--debug"),
    show_plan: bool = typer.Option(False, "--show-plan"),
    no_reflection: bool = typer.Option(False, "--no-reflection"),
    no_preflight: bool = typer.Option(False, "--no-preflight")
):
    async def _run():
        cfg = load_agent(_agent_path(agent_name))

        if not no_preflight:
            task = typer.prompt("Task")
            issues = CapabilityPreflight().check_agent_task(cfg, task)
            if issues:
                for issue in issues:
                    typer.echo(issue.to_text())
                    typer.echo("")
                if any(issue.severity.value in ["severe", "critical"] for issue in issues):
                    raise typer.Exit(1)
        else:
            task = typer.prompt("Task")

        provider = create_provider(cfg.provider)
        memory = MemoryManager(cfg.memory.db_path)
        knowledge = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
        registry = default_tool_registry(memory, knowledge, source_agent_config=cfg)

        tracer = TraceCollector()
        tracer.start_run(
            run_type="agent",
            task=task,
            agent_id=cfg.id,
            agent_name=cfg.name,
            provider=getattr(cfg.provider, "type", None),
            model=getattr(cfg.provider, "model", None),
            metadata={"source": "cli", "debug": debug},
        )

        try:
            deterministic_result = await _try_deterministic_route(task, cfg, registry, debug=debug, tracer=tracer)
            if deterministic_result is not None:
                if getattr(deterministic_result, "success", True):
                    tracer.complete_run(status="completed", message="Deterministic local route completed.")
                else:
                    tracer.complete_run(status="failed", message=getattr(deterministic_result, "error", "Deterministic route failed."))
                typer.echo("ANSWER")
                if getattr(deterministic_result, "data", None) is not None:
                    typer.echo(deterministic_result.data)
                elif getattr(deterministic_result, "error", None):
                    typer.echo(deterministic_result.error)
                else:
                    typer.echo(deterministic_result)
                return
        except Exception as exc:
            tracer.fail_run(exc)
            raise

        judgment = evaluate_orchestration_judgment(
            task,
            cfg=cfg,
            registry=registry,
            event_context={"event_type": "manual", "source": "cli"},
        )

        tracer.event("routing.completed", component="routing", name="orchestration_judgment", status="completed", data=judgment)
        policy_decision = judgment.get("policy", {}) or {}
        policy_action = policy_decision.get("action", "unknown")
        tracer.event(
            "policy.checked",
            component="policy",
            name=policy_action,
            status=policy_action if policy_action in {"allow", "block", "hold_for_confirmation"} else "completed",
            message=policy_decision.get("reason"),
            data=policy_decision,
        )

        if debug:
            typer.echo("ORCHESTRATION_JUDGMENT")
            typer.echo(judgment)
            typer.echo("")

        final_decision = judgment.get("final_decision", {}) or {}
        if final_decision.get("action") in {"block", "hold_for_confirmation"}:
            action = final_decision.get("action")
            tracer.complete_run(status=action, message=final_decision.get("reason") or "Routing stopped by policy.")
            typer.echo("ANSWER")
            typer.echo(final_decision.get("reason") or "Routing stopped by policy.")
            return

        agent = AssistantAgent(cfg, provider)
        try:
            output = await agent.run(
                task,
                debug=debug,
                show_plan=show_plan,
                reflection=not no_reflection,
                tracer=tracer,
            )
            tracer.complete_run(status="completed", message="Agent run completed.")
            typer.echo(output)
        except Exception as exc:
            tracer.fail_run(exc)
            raise

    asyncio.run(_run())

def _parse_key_value_args(arg_items):
    parsed = {}
    for item in arg_items or []:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --arg value '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise typer.BadParameter("Invalid --arg value. Key cannot be empty.")

        lowered = value.lower()
        if lowered == "true":
            parsed[key] = True
        elif lowered == "false":
            parsed[key] = False
        elif lowered in {"none", "null"}:
            parsed[key] = None
        else:
            try:
                parsed[key] = int(value)
            except ValueError:
                try:
                    parsed[key] = float(value)
                except ValueError:
                    parsed[key] = value
    return parsed



@tool_app.command("run")
def tool_run(
    tool_name: str,
    args: str = typer.Option("{}", "--args", help="JSON object of tool arguments."),
    arg: list[str] = typer.Option([], "--arg", help="Tool argument in key=value format. Repeat for multiple arguments."),
    agent_name: str = typer.Option("Bob", "--agent")
):
    async def _run():
        cfg = load_agent(_agent_path(agent_name))
        provider = create_provider(cfg.provider)
        memory = MemoryManager(cfg.memory.db_path)
        knowledge = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
        registry = default_tool_registry(memory, knowledge, source_agent_config=cfg)

        tool = registry.get(tool_name)
        if not tool:
            typer.echo(f"Tool not found: {tool_name}")
            raise typer.Exit(1)

        try:
            parsed_args = json.loads(args)
            if not isinstance(parsed_args, dict):
                raise ValueError("--args must be a JSON object")
        except Exception as exc:
            typer.echo(f"Invalid JSON for --args: {exc}")
            raise typer.Exit(1)

        try:
            parsed_args.update(_parse_key_value_args(arg))
        except typer.BadParameter as exc:
            typer.echo(str(exc))
            raise typer.Exit(1)

        tracer = TraceCollector()
        tracer.start_run(run_type="tool", task=f"{tool_name} {parsed_args}", agent_id=cfg.id, agent_name=cfg.name, provider=getattr(cfg.provider, "type", None), model=getattr(cfg.provider, "model", None), metadata={"source": "cli", "tool": tool_name})
        try:
            # Direct tool execution intentionally bypasses natural-language LLM/tool-selection
            # routing. Record that bypass as estimated token savings so `orch run-info`
            # reflects the real cost advantage of explicit tool commands. This is an
            # estimate only; no provider call is made and no USD cost is recorded.
            direct_tool_task = f"{tool_name} {parsed_args}"
            token_estimate = estimate_route_savings(
                system_prompt=getattr(cfg, "instructions", ""),
                tool_context={
                    "selected_tool": tool_name,
                    "arguments": parsed_args,
                    "execution_mode": "direct_tool",
                },
                task=direct_tool_task,
                expected_completion_tokens=300,
            )
            tracer.event(
                "routing.bypassed",
                component="routing",
                name="direct_tool",
                status="completed",
                message="Direct tool execution bypassed LLM routing.",
                estimated_tokens_saved=token_estimate.total,
                token_source="estimated",
                data={
                    "savings_reason": "direct_tool_execution_bypassed_llm_routing",
                    "selected_tool": tool_name,
                    "arguments": parsed_args,
                    "token_estimate": token_estimate.to_dict(),
                },
            )

            policy_decision = preview_tool_policy_decision(tool_name, parsed_args, cfg)
            policy_action = policy_decision.get("action", "unknown")
            tracer.event(
                "policy.checked",
                component="policy",
                name=policy_action,
                status=policy_action if policy_action in {"allow", "block", "hold_for_confirmation"} else "completed",
                message=policy_decision.get("reason"),
                data=policy_decision,
            )
            if policy_action in {"block", "hold_for_confirmation"}:
                tracer.complete_run(status=policy_action, message=policy_decision.get("reason") or "Tool execution stopped by policy.")
                typer.echo(policy_decision.get("reason") or "Tool execution stopped by policy.")
                return

            tracer.event("tool.started", component="tool", name=tool_name, status="started", data={"arguments": parsed_args})
            result = await tool.execute(**parsed_args)
            tracer.event("tool.completed" if getattr(result, "success", False) else "tool.failed", component="tool", name=tool_name, status="completed" if getattr(result, "success", False) else "failed", message=getattr(result, "error", None), data={"success": getattr(result, "success", None), "arguments": parsed_args})
            tracer.complete_run(status="completed" if getattr(result, "success", False) else "failed", message=getattr(result, "error", None))
        except Exception as exc:
            tracer.fail_run(exc)
            raise
        typer.echo(result)

    asyncio.run(_run())

@trigger_app.command("run")
def trigger_run(trigger_id: str, debug: bool = typer.Option(False, "--debug")):
    async def _run():
        trigger = load_trigger(_trigger_path(trigger_id))
        event = TriggerEvent(trigger.id, trigger.type, trigger.target_agent, trigger.task, {"source": "manual_trigger_run"})
        typer.echo(await TriggerDispatcher().dispatch(event, debug=debug))

    asyncio.run(_run())

@trigger_app.command("heartbeat")
def trigger_heartbeat(trigger_id: str, debug: bool = typer.Option(False, "--debug")):
    async def _run():
        trigger = load_trigger(_trigger_path(trigger_id))
        typer.echo(f"Starting heartbeat trigger {trigger.id} every {trigger.interval_seconds}s. Press Ctrl+C to stop.")
        await HeartbeatTriggerRunner(trigger).run_forever(debug=debug)

    asyncio.run(_run())

@app.command("serve-webhooks")
def serve_webhooks(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(create_webhook_app(), host=host, port=port)

@memory_app.command("recent")
def memory_recent(agent_name: str = typer.Option("Bob", "--agent"), limit: int = typer.Option(10, "--limit")):
    cfg = load_agent(_agent_path(agent_name))
    rows = MemoryManager(cfg.memory.db_path).list_recent(cfg.id, limit)

    if not rows:
        typer.echo("No recent memory found.")
        return

    for _id, aid, role, content, ts in rows:
        typer.echo(f"[{ts}] {aid}/{role}: {content}")

@memory_app.command("list")
def memory_list(agent_name: str = typer.Option("Bob", "--agent"), limit: int = typer.Option(50, "--limit")):
    cfg = load_agent(_agent_path(agent_name))
    rows = MemoryManager(cfg.memory.db_path).list_recent(cfg.id, limit)

    if not rows:
        typer.echo("No memory found.")
        return

    for _id, aid, role, content, ts in rows:
        typer.echo(f"{_id}. [{ts}] {aid}/{role}: {content}")

@memory_app.command("episodes")
def memory_episodes(agent_name: str = typer.Option("Bob", "--agent"), limit: int = typer.Option(25, "--limit")):
    cfg = load_agent(_agent_path(agent_name))
    rows = MemoryManager(cfg.memory.db_path).list_episodes(cfg.id, limit)

    if not rows:
        typer.echo("No episodes found.")
        return

    for _id, aid, task, response, status, ts in rows:
        typer.echo(f"{_id}. [{ts}] {aid}/{status}\nTask: {task}\nResponse: {response}\n")

@memory_app.command("search")
def memory_search(query: str, agent_name: str = typer.Option("Bob", "--agent"), limit: int = typer.Option(25, "--limit")):
    cfg = load_agent(_agent_path(agent_name))
    rows = MemoryManager(cfg.memory.db_path).search(query, cfg.id, limit)

    if not rows:
        typer.echo("No matching memory found.")
        return

    for _id, aid, role, content, ts in rows:
        typer.echo(f"{_id}. [{ts}] {aid}/{role}: {content}")

@memory_app.command("clear")
def memory_clear(agent_name: str = typer.Option("Bob", "--agent"), yes: bool = typer.Option(False, "--yes")):
    cfg = load_agent(_agent_path(agent_name))

    if not yes and not typer.confirm(f"Clear memory for {cfg.name}?"):
        return

    MemoryManager(cfg.memory.db_path).clear(cfg.id)
    typer.echo(f"Memory cleared for {cfg.name}.")

@knowledge_app.command("ingest")
def knowledge_ingest(path: str, agent_name: str = typer.Option("Bob", "--agent")):
    async def _run():
        cfg = load_agent(_agent_path(agent_name))
        provider = create_provider(cfg.provider)
        manager = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
        count = await manager.ingest_file(path)
        typer.echo(f"Ingested {count} chunks from {path}")

    asyncio.run(_run())

@knowledge_app.command("search")
def knowledge_search(query: str, agent_name: str = typer.Option("Bob", "--agent"), limit: int = typer.Option(5, "--limit")):
    async def _run():
        cfg = load_agent(_agent_path(agent_name))
        provider = create_provider(cfg.provider)
        manager = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
        results = await manager.search(query, limit)

        if not results:
            typer.echo("No knowledge found.")
            return

        for score, row in results:
            _id, source, chunk, _embedding, _metadata, _timestamp = row
            typer.echo(f"Score: {score:.3f}\nSource: {source}\n{chunk}\n---")

    asyncio.run(_run())

@knowledge_app.command("list")
def knowledge_list(agent_name: str = typer.Option("Bob", "--agent")):
    cfg = load_agent(_agent_path(agent_name))
    provider = create_provider(cfg.provider)
    manager = KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection)
    rows = manager.list_sources()

    if not rows:
        typer.echo("No knowledge sources found.")
        return

    for source, count in rows:
        typer.echo(f"{source}: {count} chunks")

@knowledge_app.command("clear")
def knowledge_clear(agent_name: str = typer.Option("Bob", "--agent"), yes: bool = typer.Option(False, "--yes")):
    cfg = load_agent(_agent_path(agent_name))
    provider = create_provider(cfg.provider)

    if not yes and not typer.confirm("Clear all knowledge chunks?"):
        return

    KnowledgeManager(provider, cfg.knowledge.store, cfg.knowledge.db_path, cfg.knowledge.collection).clear()
    typer.echo("Knowledge cleared.")

if __name__ == "__main__":
    app()
