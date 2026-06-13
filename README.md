# Orchgentic

Orchgentic is an open-source agent orchestration framework for building, routing, coordinating, and observing AI agents across tools, memory, knowledge, workflows, policies, and teams.

Instead of treating an agent as a single chatbot, Orchgentic gives developers a runtime for deciding how work should move through an agentic system: when to answer locally, when to call a tool, when to escalate to an LLM, when to block or hold an action for confirmation, and when to coordinate multiple specialist agents into a final response.

## What Orchgentic offers in v0.7.12

- **Agent runtime** with YAML-based agent configuration.
- **Provider abstraction** with one provider configured per agent.
- **Local reasoning** to avoid unnecessary LLM calls for simple deterministic tasks.
- **Confidence scoring and escalation** to decide when the configured LLM provider is needed.
- **Workflow-aware routing** for single-step, multi-step, tool-driven, and team-driven tasks.
- **Event-aware routing** for manual, heartbeat, webhook, and autonomous contexts.
- **Policy-aware execution** for blocking disabled tools and holding sensitive actions for confirmation.
- **Tool runtime** with built-in filesystem, web, datetime, memory, knowledge, and Gmail tools.
- **Memory and knowledge layers** for storing conversational history and searchable knowledge.
- **Team orchestration** for Manager / Researcher / Writer / Reviewer style workflows.
- **Compressed team handoffs** to reduce token bloat and improve final synthesis quality.
- **Debug and telemetry output** so routing, policy, tools, and team decisions are inspectable.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows PowerShell

python -m pip install -e ".[dev]"
orch list-agents
orch inspect-agent Bob
orch run Bob --debug
```

When prompted for a task, try:

```text
what is the local time?
```

This should route directly to `datetime.local` without using an external LLM.

## Example routing checks

Preview what Orchgentic would do before execution:

```bash
orch judge-route "what is the local time?" --agent Bob
orch judge-route "delete gmail message id abcdef123456" --agent Bob
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

`judge-route` is inspection-only. It does not execute tools, send email, delete email, or run a workflow.

## Example team run

```bash
orch run-team contentteam --debug
```

When prompted, enter:

```text
Research AI is changing how customers shop and create an Executive Summary
```

Orchgentic will coordinate the team and produce a final synthesized response.

## Documentation

- [Quickstart](docs/QUICKSTART.md)
- [CLI Commands](docs/CLI_COMMANDS.md)
- [Agent Configuration](docs/AGENT_CONFIGURATION.md)
- [Team Configuration](docs/TEAM_CONFIGURATION.md)
- [Tools and Policies](docs/TOOLS_AND_POLICIES.md)
- [Routing and Reasoning](docs/ROUTING_AND_REASONING.md)
- [Examples](docs/EXAMPLES.md)
- [v0.7.12 Release Notes](docs/RELEASE_NOTES_V0_7_12.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)

## Core design rule

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether that provider should be used
```

Agents define one provider. Orchgentic decides whether that provider should be called.
