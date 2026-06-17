# Orchgentic

**Orchgentic** is an open-source, local-first AI agent orchestration framework for building, routing, coordinating, observing, and optimizing agents across tools, memory, knowledge, workflows, events, policies, providers, and teams.

Orchgentic is designed around a YAML-first operational architecture so agent behavior, tools, policies, routing, observability, and token usage can be configured, versioned, inspected, and trusted.

> Stop letting agents become black boxes that eat tokens in the dark.

## What Orchgentic Is

Orchgentic is not just an agent runner.

It is a local-first AI operations layer that helps determine:

- which agent should handle a task
- whether a tool should be used
- whether memory or knowledge should be searched
- whether the task can be handled locally
- whether an external LLM should be called
- whether a workflow or team should be used
- whether policy allows the action
- whether human confirmation is required
- how many tokens were used or estimated to be saved
- how the run should be inspected afterward

Orchgentic is built for developers and technical teams who need agents, tools, teams, workflows, policies, memory, knowledge, providers, and observability to work together under clear, version-controlled contracts.

---

## Why Orchgentic Exists

AI agents are powerful, but they can easily become black boxes that spend tokens just to figure out:

- what role they are supposed to play
- which tools they have
- which provider they should use
- what policies apply
- what context is available
- whether memory or knowledge is needed
- whether the task even requires an LLM

Orchgentic helps make agent systems:

- observable
- token-aware
- policy-safe
- locally efficient
- provider-flexible
- workflow-ready
- easier to debug
- easier to trust

---

## Key Features

Current capabilities include:

- YAML-based agent configuration
- pluggable provider configuration
- tool registry and tool execution
- memory support
- knowledge search support
- planning and reflection
- local reasoning
- confidence scoring
- deterministic tool routing
- workflow-aware routing
- event-aware routing
- policy-aware escalation
- Gmail tool policies
- confirmation-required tool execution
- disabled-tool blocking
- multi-agent team orchestration
- team handoff compression
- structured output unwrapping
- team synthesis guardrails
- observability store
- run history
- trace events
- run inspection
- trace inspection
- export commands
- static local dashboard
- dashboard search, filters, pagination, and modals
- Token Intelligence reporting
- estimated token savings tracking
- local execution proof events
- observability doctor command
- clean test data / release cleanup command

---

## Quick Install

Clone the repository:

```bash
git clone https://github.com/davidvineyardatx/orchgentic.git
cd orchgentic
```

Create and activate a virtual environment.

Git Bash / Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install Orchgentic in editable mode:

```bash
pip install -e .
```

Initialize the workspace:

```bash
orch init
```

Verify the CLI:

```bash
orch --help
```

---

## First Run

List available agents:

```bash
orch list-agents
```

List available tools:

```bash
orch list-tools
```

Run Bob:

```bash
orch run Bob
```

Run a deterministic tool through Bob:

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

---

## Token Intelligence Demo

The fastest way to see the Orchgentic token-savings story is to run a deterministic tool and then inspect the Token Intelligence report.

Run:

```bash
orch tool run datetime.local --agent Bob
```

Then:

```bash
orch token-report
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

This demonstrates:

```text
Bob has a provider configured.
The task did not need the provider.
Orchgentic bypassed LLM routing.
The tool ran directly.
The run spent 0 external LLM tokens.
The estimated savings were recorded and can be inspected.
```

Filter token reports:

```bash
orch token-report --status completed
orch token-report --type tool
orch token-report --agent Bob
orch token-report --team ContentTeam
orch token-report --limit 500
orch token-report --json
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

- run summaries
- failure summaries
- search
- quick filters
- client-side pagination
- modal run details
- Token Intelligence section
- token-scoped Run ID modal
- copy commands
- empty states
- generated metadata panel
- local static HTML output

The dashboard is local and does not require a hosted service.

---

## Observability Commands

Orchgentic records run and trace data locally.

Schema:

```text
orchgentic.observability.v1
```

Useful commands:

| Command | Purpose |
|---|---|
| `orch runs` | List recorded runs |
| `orch run-info <run_id>` | Inspect a run and its trace |
| `orch trace <run_id>` | Inspect trace events |
| `orch failures` | Show failed runs |
| `orch export-run <run_id>` | Export one run as JSON |
| `orch export-runs` | Export multiple runs as JSONL |
| `orch runs-stats` | Show observability stats |
| `orch doctor observability` | Check observability health |
| `orch token-report` | Show token intelligence summary |
| `orch dashboard` | Generate dashboard |
| `orch clean-testdata` | Preview cleanup of generated data |

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

- schema version
- store status
- run count
- event count
- dashboard output path
- directory health
- estimated tokens saved
- next steps

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

## Provider Setup

Agents only need valid provider configuration when a run actually escalates to an external LLM.

For Groq:

```env
GROQ_API_KEY=your_groq_api_key
```

For OpenAI:

```env
OPENAI_API_KEY=your_openai_api_key
```

For local OpenAI-compatible runtimes such as LM Studio:

```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

Direct tool runs, deterministic routes, and some local reasoning paths may avoid external LLM calls entirely.

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

- `logs/`
- `exports/`
- `memory/`
- `.pytest_cache/`
- `__pycache__/`
- `*.pyc`

It preserves:

- `agents/`
- `teams/`
- `triggers/`
- `docs/`
- `.env`
- provider credentials
- source code

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

## What Is Not Stable Yet

Orchgentic is still in developer preview.

The current release does not yet claim:

- hosted dashboard
- hosted SaaS control plane
- full no-code builder
- stable workflow YAML contract
- stable plugin marketplace
- enterprise RBAC
- distributed workers

These are future directions. The current focus is building a stable local-first runtime with observable, token-aware execution.

---

## Roadmap Direction

Near-term priorities include:

- Token Intelligence polish
- local reasoning proof
- runtime hardening and error consistency
- configuration contract freeze
- tool/plugin contract stabilization
- workflow execution foundation
- RAG, memory, and knowledge stabilization
- provider and local LLM stabilization
- SDK foundation
- local API foundation
- dashboard/workbench improvements
- builder-ready contracts
- stable v1.0 release

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

- multi-agent coordination
- tool-using agents
- policy-governed execution
- autonomous workflows
- memory and knowledge retrieval
- RAG
- local LLMs
- local reasoning
- provider escalation
- human confirmation
- runtime observability
- Token Intelligence
- dashboard-driven operations
- SDK and API access
- eventually, no-code orchestration

The autonomous AI era is only beginning.

Orchgentic is being built to help orchestrate what comes next.
