from pathlib import Path
import re

def _slug(name: str) -> str:
    value = (name or "").strip()
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value)
    return value.lower().strip("-") or "item"

def _display(name: str) -> str:
    return (name or "").strip() or "Item"

def create_agent_file(name: str, provider_type="groq", model="llama-3.3-70b-versatile", role="General Assistant", timezone="America/Chicago", locale="en-US", overwrite=False) -> Path:
    agent_id = _slug(name)
    agent_name = _display(name)
    path = Path("agents") / f"{agent_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Agent already exists: {path}")
    path.write_text(f'''agent:
  id: {agent_id}
  name: {agent_name}
  role: {role}
  description: {agent_name} agent created by Orchgentic.
  instructions: |
    You are {agent_name}, a helpful AI agent. Use tools, memory, and knowledge when relevant.

  timezone: {timezone}
  locale: {locale}

  provider:
    type: {provider_type}
    model: {model}

  capabilities:
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search

  tools:
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search

  tool_runtime:
    enabled: true
    max_iterations: 4
    timeout_seconds: 90
    allow_parallel: false
    save_results_to_memory: false

  delegation:
    enabled: false
    allowed_agents: []
    max_depth: 2

  reasoning:
    planner: true
    reflection: true

  memory:
    enabled: true
    recent_messages: 10
    db_path: memory/orchgentic.db

  knowledge:
    enabled: true
    top_k: 5
    store: local
    db_path: memory/orchgentic.db
    collection: orchgentic_knowledge
''', encoding="utf-8")
    return path

def create_team_file(name: str, orchestrator="Manager", members=None, overwrite=False) -> Path:
    team_id = _slug(name)
    team_name = _display(name)
    path = Path("teams") / f"{team_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Team already exists: {path}")
    members = members or ["Researcher", "Writer", "Reviewer"]
    member_lines = "\n".join(f"    - {m}" for m in members)
    path.write_text(f'''team:
  id: {team_id}
  name: {team_name}
  description: {team_name} team created by Orchgentic.

  orchestrator: {orchestrator}

  members:
{member_lines}

  shared_context: true
  max_rounds: 3

  task: |
    Coordinate the team to complete the requested task.
''', encoding="utf-8")
    return path

def create_trigger_file(name: str, target_agent="Bob", interval_seconds=3600, overwrite=False) -> Path:
    trigger_id = _slug(name)
    path = Path("triggers") / f"{trigger_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Trigger already exists: {path}")
    path.write_text(f'''trigger:
  id: {trigger_id}
  type: heartbeat
  target_agent: {target_agent}
  interval_seconds: {interval_seconds}
  enabled: true
  task: |
    Run the scheduled task for this trigger.
''', encoding="utf-8")
    return path
