# Orchgentic

Orchgentic is an open-source, local-first agent orchestration framework for building, routing, coordinating, observing, and optimizing AI agents across tools, memory, knowledge, workflows, events, policies, providers, and teams.

Orchgentic is designed around a YAML-first operational architecture so agents, teams, tools, routing behavior, memory, knowledge, safety policies, observability, and token usage can be configured clearly and inspected easily.

## Current Status

**Developer Preview — v0.8.0-beta.3**

The current release line focuses on observability, token intelligence, clean runtime inspection, and proving when Orchgentic avoids unnecessary external LLM usage.

v0.8.0-beta.3 introduces the Token Intelligence layer:

* `orch token-report`
* local vs external LLM run summaries
* direct tool bypass metrics
* deterministic route metrics
* estimated token savings summaries
* proof events for local/direct execution
* Token Intelligence dashboard section
* token-scoped Run ID modal
* dashboard title polish

The goal is simple:

> Stop letting agents become black boxes that eat tokens in the dark.

Orchgentic helps prove when an agent had a provider configured, avoided the LLM, ran locally or directly, spent zero external LLM tokens, and recorded the proof in the trace.

---

## Core Positioning

Orchgentic is not just an agent runner.

It is a local-first AI operations layer that helps determine:

* which agent should handle a task
* whether a tool should be used
* whether memory or knowledge should be searched
* whether the task can be handled locally
* whether an external LLM should be called
* whether policy allows the action
* whether human confirmation is required
* how many tokens were used or estimated to be saved
* how the run should be inspected afterward

Orchgentic is built for developers and technical teams who need agents, tools, teams, workflows, policies, memory, knowledge, providers, and observability to work together under clear, version-controlled contracts.

---

## Key Features

Current capabilities include:

* YAML-based agent configuration
* pluggable provider configuration
* tool registry and tool execution
* memory support
* knowledge search support
* planning and reflection
* local reasoning
* confidence scoring
* deterministic tool routing
* workflow-aware routing
* event-aware routing
* policy-aware escalation
* Gmail tool policies
* confirmation-required tool execution
* disabled-tool blocking
* multi-agent team orchestration
* team handoff compression
* structured output unwrapping
* team synthesis guardrails
* observability store
* run history
* trace events
* run inspection
* trace inspection
* export commands
* static local dashboard
* dashboard search, filters, pagination, and modals
* Token Intelligence reporting
* estimated token savings tracking
* local execution proof events
* observability doctor command
* clean test data / release cleanup command

---

## Installation

From the project root:

```bash
pip install -e .
```

Then verify the CLI:

```bash
orch --help
```

---

## Quick Start

Run a low-risk deterministic tool through an agent:

```bash
orch tool run datetime.local --agent Bob
```

Inspect recent runs:

```bash
orch runs
```

Inspect a specific run:

```bash
orch run-info <run_id>
```

Inspect trace events:

```bash
orch trace <run_id>
```

Generate a Token Intelligence report:

```bash
orch token-report
```

Generate the dashboard:

```bash
orch dashboard
```

Open the existing dashboard:

```bash
orch dashboard --open
```

---

## Token Intelligence

Token Intelligence is Orchgentic’s proof layer for local execution and estimated token savings.

Use:

```bash
orch token-report
```

Filter reports:

```bash
orch token-report --status completed
orch token-report --type tool
orch token-report --agent Bob
orch token-report --team ContentTeam
orch token-report --limit 500
orch token-report --json
```

Example output:

```text
TOKEN INTELLIGENCE
filters: limit=100
loaded_runs: 1
local_runs: 1 (100.0%)
external_llm_runs: 0 (0.0%)
direct_tool_runs: 1
direct_bypasses: 1
deterministic_routes: 1
local_reasoning_events: 0
llm_events: 0
total_tokens: 0
estimated_tokens_saved: 349
token_source_note: estimated token savings are operational estimates of avoided LLM routing/execution overhead, not billing claims
```

Example proof event:

```text
routing.bypassed (routing/direct_tool) saved≈349, source=estimated - Direct tool execution bypassed LLM routing.
```

This proves that Orchgentic avoided an unnecessary external LLM call for a deterministic direct-tool path.

---

## Observability

The v0.8.0 observability foundation includes:

* run history
* trace inspection
* exports
* failure diagnostics
* retention cleanup
* local static dashboard
* dashboard pagination
* observability doctor
* Token Intelligence reporting

Schema:

```text
orchgentic.observability.v1
```

Useful commands:

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch failures
orch export-run <run_id>
orch export-runs
orch runs-stats
orch doctor observability
orch token-report
```

---

## Observability Dashboard

Generate a local static dashboard:

```bash
orch dashboard
```

Open the existing dashboard:

```bash
orch dashboard --open
```

Generate a filtered dashboard and then open it:

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

Load more runs into the dashboard:

```bash
orch dashboard --limit 500
```

Dashboard features include:

* search
* quick filters
* client-side pagination
* modal run details
* Token Intelligence section
* token-scoped Run ID modal
* copy commands
* empty states
* generated metadata panel
* local static HTML output

The dashboard is local and does not require a hosted service.

---

## Observability Doctor

Check observability health:

```bash
orch doctor observability
```

JSON output:

```bash
orch doctor observability --json
```

The doctor reports:

* schema version
* store status
* run count
* event count
* dashboard output path
* directory health
* estimated tokens saved
* next steps

Example states:

```text
ok
empty
not_initialized
```

---

## Agent Configuration

A typical agent can define identity, provider, tools, Gmail policies, routing, reasoning, memory, and knowledge.

Example Bob header:

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  description: General-purpose AI assistant.
  instructions: |
    You are Bob, a helpful AI assistant. Use memory, knowledge, reasoning, and tools when relevant.
```

Provider example:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Design rule:

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether the provider should be used
```

A configured provider does not mean a provider was used for every run. Direct tool runs or deterministic routes may report:

```text
external_llm_used: False
provider used: N/A — no LLM used
configured provider: groq / llama-3.3-70b-versatile
```

---

## Tool Execution

Run a direct tool:

```bash
orch tool run datetime.local --agent Bob
```

Run a Gmail send tool with confirmation:

```bash
orch tool run gmail.send --agent Bob --arg to=studio@example.com --arg subject="Hello" --arg body="Hello from Bob" --arg confirm=true
```

Direct tool runs can be observed without using an external LLM.

Expected trace shape:

```text
run.started
routing.bypassed
policy.checked
tool.started
tool.completed
run.completed
```

---

## Team Execution

Run a team:

```bash
orch run-team contentteam --debug
```

Teams allow Orchgentic to coordinate multiple specialized agents and synthesize the final result.

---

## Routing Inspection

Preview routing behavior without executing:

```bash
orch judge-route "what is the local time?" --agent Bob
```

Preview a policy-controlled action:

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Routing helps decide whether work should be handled locally, routed to a tool, escalated to a provider, blocked by policy, held for confirmation, or delegated to a team/workflow.

---

## Release Cleanup

Preview cleanup:

```bash
orch clean-testdata
```

Verbose dry run:

```bash
orch clean-testdata --verbose
```

JSON output:

```bash
orch clean-testdata --json
```

Actually clean generated runtime/test data:

```bash
orch clean-testdata --no-dry-run --confirm
```

The cleanup command removes generated artifacts such as:

* `logs/`
* `exports/`
* `memory/`
* `.pytest_cache/`
* `__pycache__/`
* `*.pyc`

It preserves:

* `agents/`
* `teams/`
* `triggers/`
* `docs/`
* `.env`
* provider credentials
* source code

---

## Final Release Cleanup and Python Bytecode

`orch clean-testdata` removes generated runtime/test artifacts, but running Python or `orch` may recreate `__pycache__/` and `*.pyc` files.

For the final cleanup before publishing a GitHub release, run cleanup as the last command before `git status`.

Git Bash:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```

PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; orch clean-testdata --no-dry-run --confirm
git status
```

After this final cleanup, avoid running `pytest`, `python`, or `orch` again before checking and committing, because those commands can recreate bytecode cache files.

---

## Validation

Recommended validation before release:

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q

orch tool run datetime.local --agent Bob
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

Final cleanup:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```

---

## Documentation

Recommended reading order:

1. `README.md`
2. `docs/QUICKSTART.md`
3. `docs/CLI_COMMANDS.md`
4. `docs/AGENT_CONFIGURATION.md`
5. `docs/TEAM_CONFIGURATION.md`
6. `docs/TOOLS_AND_POLICIES.md`
7. `docs/ROUTING_AND_REASONING.md`
8. `docs/OBSERVABILITY.md`
9. `docs/OBSERVABILITY_DASHBOARD.md`
10. `docs/OBSERVABILITY_EXAMPLES.md`
11. `ROADMAP.md`

---

## Roadmap Direction

Near-term priorities include:

* Token Intelligence polish
* local reasoning proof
* runtime hardening and error consistency
* configuration contract freeze
* tool/plugin contract stabilization
* workflow execution foundation
* RAG, memory, and knowledge stabilization
* provider and local LLM stabilization
* SDK foundation
* local API foundation
* dashboard/workbench improvements
* builder-ready contracts
* stable v1.0 release

For v1.0, Orchgentic should be:

```text
CLI-first
SDK-supported
local API-enabled
dashboard-observable
workflow-capable
RAG-aware
local LLM-ready
builder-ready
```

---

## Long-Term Vision

The long-term vision for Orchgentic is to become a unified orchestration runtime for autonomous and multi-agent AI systems.

Orchgentic is being built to support:

* multi-agent coordination
* tool-using agents
* policy-governed execution
* autonomous workflows
* memory and knowledge retrieval
* RAG
* local LLMs
* local reasoning
* provider escalation
* human confirmation
* runtime observability
* Token Intelligence
* dashboard-driven operations
* SDK and API access
* eventually, no-code orchestration

The autonomous AI era is only beginning.

Orchgentic is being built to help orchestrate what comes next.
