import asyncio
from pathlib import Path
import json
import typer
import uvicorn
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

app = typer.Typer()
memory_app = typer.Typer()
trigger_app = typer.Typer()
knowledge_app = typer.Typer()
tool_app = typer.Typer()

app.add_typer(memory_app, name="memory")
app.add_typer(trigger_app, name="trigger")
app.add_typer(knowledge_app, name="knowledge")
app.add_typer(tool_app, name="tool")

def _agent_path(name):
    return Path("agents") / (name.lower() if name.lower().endswith(".yaml") else f"{name.lower()}.yaml")

def _trigger_path(name):
    return Path("triggers") / (name.lower() if name.lower().endswith(".yaml") else f"{name.lower()}.yaml")

@app.command()
def init(path: str = "."):
    init_workspace(path)
    typer.echo(f"Workspace initialized at {Path(path).resolve()}")

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
        try:
            result = await TeamRunner().run_team(team, task=task, debug=debug, preflight=not no_preflight)
        except RuntimeError as exc:
            typer.echo(str(exc))
            raise typer.Exit(1)

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

        agent = AssistantAgent(cfg, create_provider(cfg.provider))
        typer.echo(await agent.run(
            task,
            debug=debug,
            show_plan=show_plan,
            reflection=not no_reflection
        ))

    asyncio.run(_run())

@tool_app.command("run")
def tool_run(
    tool_name: str,
    args: str = typer.Option("{}", "--args"),
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
        except Exception as exc:
            typer.echo(f"Invalid JSON for --args: {exc}")
            raise typer.Exit(1)

        result = await tool.execute(**parsed_args)
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
