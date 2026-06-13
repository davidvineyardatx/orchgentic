# CLI Commands

This document explains the main Orchgentic CLI commands, when to use them, and gives examples.

## Workspace

### `orch init`

Initializes an Orchgentic workspace.

```bash
orch init
```

Initialize a specific path:

```bash
orch init ./my-orchgentic-app
```

Use this when creating a new local workspace.

---

## Agents

### `orch list-agents`

Lists configured agents from the `agents/` folder.

```bash
orch list-agents
```

Use this to confirm that Orchgentic can discover your agent YAML files.

### `orch inspect-agent <AgentName>`

Shows an agent's identity, provider, capabilities, tools, and delegation settings.

```bash
orch inspect-agent Bob
```

Use this when validating changes to an agent YAML file.

### `orch preflight-agent <AgentName> --task "..."`

Checks whether an agent appears configured to handle a task before execution.

```bash
orch preflight-agent Bob --task "what is the local time?"
```

Use this to catch missing capabilities or severe configuration problems before running.

### `orch run <AgentName>`

Runs an agent. The CLI prompts for the task.

```bash
orch run Bob
```

With debug output:

```bash
orch run Bob --debug
```

With plan output:

```bash
orch run Bob --show-plan
```

Skip reflection:

```bash
orch run Bob --no-reflection
```

Skip preflight:

```bash
orch run Bob --no-preflight
```

Example task:

```text
Task: what is the local time?
```

Expected behavior:

```text
selected_tool: datetime.local
external_llm_used: false
```

---

## Routing and judgment

### `orch judge-route "task" --agent <AgentName>`

Previews routing, reasoning, workflow, event, policy, and escalation decisions without executing the task.

```bash
orch judge-route "what is the local time?" --agent Bob
```

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Important: `judge-route` is inspection-only. It does not execute tools, send email, delete email, or run the full workflow.

### `orch judge-route "task" --agent <AgentName> --event-type <type>`

Evaluates a route as if it came from a specific event context.

```bash
orch judge-route "send a report email" --agent Bob --event-type webhook
```

Supported event types include:

```text
manual
heartbeat
webhook
scheduled
unknown
```

### `orch route-metrics`

Shows aggregated routing metrics.

```bash
orch route-metrics
```

Use this to inspect token-saving and routing telemetry after running tasks.

---

## Tools

### `orch list-tools --agent <AgentName>`

Lists tools available to an agent.

```bash
orch list-tools --agent Bob
```

Use this to verify that a tool is configured before running a task.

### `orch tool run <tool.name> --agent <AgentName>`

Runs a specific tool directly.

```bash
orch tool run datetime.local --agent Bob
```

Pass arguments as repeated `--arg key=value` values:

```bash
orch tool run filesystem.write \
  --agent Bob \
  --arg path=notes/hello.txt \
  --arg content="Hello from Orchgentic"
```

Pass JSON with `--args`:

```bash
orch tool run filesystem.read --agent Bob --args '{"path":"notes/hello.txt"}'
```

Confirmed Gmail send:

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Hello" \
  --arg body="Hello from Bob" \
  --arg confirm=true
```

Use direct tool execution when you already know the exact tool and arguments.

---

## Teams

### `orch list-teams`

Lists configured teams from the `teams/` folder.

```bash
orch list-teams
```

### `orch inspect-team <TeamName>`

Shows a team's orchestrator, members, shared context setting, max rounds, and tool availability.

```bash
orch inspect-team contentteam
```

### `orch preflight-team <TeamName> --task "..."`

Checks whether a team appears configured for a task.

```bash
orch preflight-team contentteam --task "Research AI shopping trends and create an executive summary"
```

### `orch run-team <TeamName>`

Runs a team workflow. The CLI prompts for the team task.

```bash
orch run-team contentteam
```

With debug output:

```bash
orch run-team contentteam --debug
```

Example task:

```text
Research AI is changing how customers shop and create an Executive Summary
```

Expected behavior:

- Manager assigns work.
- Researcher contributes findings.
- Writer creates a draft.
- Reviewer gives revision feedback.
- Orchgentic synthesizes the final response.

---

## Capabilities

### `orch list-capabilities`

Lists high-level capabilities and the tools they resolve to.

```bash
orch list-capabilities
```

Use this when deciding which capabilities to add to an agent YAML file.

---

## Triggers

### `orch list-triggers`

Lists configured triggers from the `triggers/` folder.

```bash
orch list-triggers
```

### `orch trigger run <trigger_id>`

Runs a trigger once.

```bash
orch trigger run bob_heartbeat --debug
```

### `orch trigger heartbeat <trigger_id>`

Starts a heartbeat trigger loop.

```bash
orch trigger heartbeat bob_heartbeat --debug
```

Stop it with `Ctrl+C`.

### `orch serve-webhooks`

Starts the webhook server.

```bash
orch serve-webhooks
```

Custom host and port:

```bash
orch serve-webhooks --host 0.0.0.0 --port 8000
```

---

## Memory

### `orch memory recent --agent <AgentName>`

Shows recent memory entries.

```bash
orch memory recent --agent Bob --limit 10
```

### `orch memory list --agent <AgentName>`

Lists memory entries.

```bash
orch memory list --agent Bob --limit 50
```

### `orch memory episodes --agent <AgentName>`

Lists task/response episodes.

```bash
orch memory episodes --agent Bob --limit 25
```

### `orch memory search "query" --agent <AgentName>`

Searches memory.

```bash
orch memory search "Gmail security alert" --agent Bob
```

### `orch memory clear --agent <AgentName> --yes`

Clears memory for an agent.

```bash
orch memory clear --agent Bob --yes
```

---

## Knowledge

### `orch knowledge ingest <path> --agent <AgentName>`

Ingests a file into the knowledge store.

```bash
orch knowledge ingest knowledge/example.txt --agent Bob
```

### `orch knowledge search "query" --agent <AgentName>`

Searches the knowledge store.

```bash
orch knowledge search "What is Orchgentic?" --agent Bob
```

### `orch knowledge list --agent <AgentName>`

Lists ingested knowledge sources.

```bash
orch knowledge list --agent Bob
```

### `orch knowledge clear --agent <AgentName> --yes`

Clears the knowledge store.

```bash
orch knowledge clear --agent Bob --yes
```

---

## Gmail connections

### `orch connect gmail --name <connection>`

Connects a named Gmail account using browser OAuth.

```bash
orch connect gmail --name assistant
```

With a specific credentials file:

```bash
orch connect gmail --name assistant --credentials credentials.json
```

### `orch gmail list`

Lists named Gmail connections.

```bash
orch gmail list
```

### `orch gmail status --name <connection>`

Shows the status of a Gmail connection.

```bash
orch gmail status --name assistant
```

### `orch gmail disconnect --name <connection>`

Disconnects a Gmail connection.

```bash
orch gmail disconnect --name assistant
```

---

## Create commands

The `orch create` command group creates configuration files. Use `orch create --help` to see the available subcommands in your installed version.

Typical generated files include:

```text
agents/<name>.yaml
teams/<name>.yaml
triggers/<name>.yaml
```
