# Observability CLI

Orchgentic v0.8.0 adds an observability foundation for inspecting agent runs, tool runs, team runs, routing decisions, policy checks, token usage, and estimated token savings.

The goal of observability in Orchgentic is to answer:

```text
What happened?
Where did it happen?
Why did it happen?
What was the outcome?
What did it cost in tokens, if known or safely estimated?
```

Orchgentic observability is intentionally **run-first** and **orchestration-native**. Instead of only tracing model calls, it records the full execution shape: runs, agents, teams, tools, routing, policies, provider calls, failures, and exports.

---

## Core Concepts

### Run Record

A run is the top-level execution container.

A run may represent:

- A single agent run
- A direct tool run
- A team run
- A future trigger or workflow run

Run records include:

```text
run_id
run_type
status
agent_id / agent_name
team_id / team_name
provider / model
external_llm_used
started_at / ended_at
duration_ms
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
task
metadata
error_type
error_message
```

### Trace Event

A trace event describes something that happened inside a run.

Trace events may include:

```text
run.started
run.completed
run.failed

agent.started
agent.completed
agent.failed

team.started
team.member.started
team.member.completed
team.member.failed
team.synthesis.started
team.synthesis.completed
team.synthesis.failed
team.completed
team.failed

routing.completed
routing.bypassed

policy.checked

tool.started
tool.completed
tool.failed

llm.started
llm.completed
llm.failed

memory.context_loaded
planning.completed
reflection.completed
```

### Token Tracking

Orchgentic tracks tokens, not money.

v0.8.0 intentionally does **not** include USD cost fields because provider pricing can vary by plan, region, discount, local model, or future pricing changes.

Token fields include:

```text
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
```

Valid `token_source` values:

```text
actual
estimated
not_applicable
unknown
```

### Estimated Token Savings

`estimated_tokens_saved` means Orchgentic avoided likely LLM tokens.

Examples:

- A local deterministic route avoided an external LLM call.
- A direct tool command bypassed LLM tool-selection/routing.
- A policy blocked or held a sensitive action before LLM escalation.

The estimate is not a billing claim. It is an operational signal.

Example:

```text
saved≈349, source=estimated
```

The `≈` indicates an estimate.

For direct tool runs, the event data can include a breakdown:

```json
{
  "savings_reason": "direct_tool_execution_bypassed_llm_routing",
  "token_estimate": {
    "system_prompt_tokens": 24,
    "memory_context_tokens": 0,
    "tool_context_tokens": 21,
    "task_tokens": 4,
    "expected_completion_tokens": 300,
    "total": 349
  }
}
```

---

## Commands

### List Recent Runs

```bash
orch runs
```

Shows recent runs.

Example:

```text
RUNS
fb995dfd  completed  tool     Bob                saved≈349, source=estimated      datetime.local {}
f0b54593  completed  agent    Bob                saved≈343, source=estimated      what is the current time
```

---

### Limit Run History

```bash
orch runs --limit 5
```

Shows only the latest five runs.

---

### Filter by Status

```bash
orch runs --status completed
orch runs --status failed
orch runs --status hold_for_confirmation
```

Useful when reviewing failures or confirmation holds.

---

### Filter by Run Type

```bash
orch runs --type agent
orch runs --type tool
orch runs --type team
```

Run types help separate single-agent runs, direct tool calls, and team orchestration runs.

---

### Filter by Agent

```bash
orch runs --agent Bob
```

Shows runs for a specific agent.

---

### Filter by Team

```bash
orch runs --team ContentTeam
```

Shows runs for a specific team.

---

### Output Runs as JSON

```bash
orch runs --json
```

Returns recent run records as JSON.

---

## Inspecting a Run

### Show Run Details

```bash
orch run-info <run_id>
```

The run id can be shortened as long as it uniquely identifies a run.

Example:

```bash
orch run-info fb995dfd
```

Example output:

```text
RUN
id: fb995dfd-38fe-4fab-96b2-d7919493d65e
type: tool
status: completed
agent: Bob
provider: groq / llama-3.3-70b-versatile
external_llm_used: False
duration_ms: 967.74
input_tokens: 0
output_tokens: 0
total_tokens: 0
estimated_tokens_saved: 349
token_source: estimated
task: datetime.local {}

TRACE EVENTS
- run.started
- routing.bypassed
- policy.checked
- tool.started
- tool.completed
- run.completed
```

---

### Show Run Details as JSON

```bash
orch run-info <run_id> --json
```

Use this when you need the full run/event data structure.

---

### Show Only the Run Summary

```bash
orch run-info <run_id> --summary-only
```

Use this when you do not need the full trace event list.

---

### Show Only Events

```bash
orch run-info <run_id> --events-only
```

Use this when you only want the trace timeline.

---

## Trace Inspection

### Show Trace Events

```bash
orch trace <run_id>
```

Shows the event timeline for a run.

---

### Trace as JSON

```bash
orch trace <run_id> --json
```

Useful for external tools, scripts, dashboards, or debugging.

---

### Filter Trace by Event Type

```bash
orch trace <run_id> --type tool.completed
orch trace <run_id> --type routing.bypassed
orch trace <run_id> --type policy.checked
```

---

### Filter Trace by Component

```bash
orch trace <run_id> --component tool
orch trace <run_id> --component policy
orch trace <run_id> --component routing
orch trace <run_id> --component provider
orch trace <run_id> --component team
```

---

### Show Token-Relevant Events

```bash
orch trace <run_id> --tokens
```

Shows events that consumed tokens or estimated token savings.

---

## Export Commands

### Export One Run

```bash
orch export-run <run_id>
```

Outputs a dashboard-ready JSON object.

Shape:

```json
{
  "schema_version": "orchgentic.observability.v1",
  "exported_at": "...",
  "export_type": "run_detail",
  "run": {},
  "events": []
}
```

---

### Export One Run to a File

```bash
orch export-run <run_id> --output exports/run.json
```

Writes the run detail export to disk.

---

### Export Run History as JSONL

```bash
orch export-runs --limit 100
```

Outputs one JSON object per line.

Each line has this shape:

```json
{
  "schema_version": "orchgentic.observability.v1",
  "exported_at": "...",
  "export_type": "run_summary",
  "run": {}
}
```

---

### Export Run History to a File

```bash
orch export-runs --limit 100 --output exports/runs.jsonl
```

Writes one run summary per line.

---

### Filter Exports

The run export command supports the same common filters:

```bash
orch export-runs --status completed
orch export-runs --status failed
orch export-runs --type agent
orch export-runs --type tool
orch export-runs --type team
orch export-runs --agent Bob
orch export-runs --team ContentTeam
```

---

## Common Workflows

### Inspect a Local Reasoning Savings Run

```bash
orch run Bob --debug
# Task: what is the current time

orch runs
orch run-info <run_id>
orch trace <run_id> --tokens
```

Expected:

```text
external_llm_used: False
estimated_tokens_saved: > 0
token_source: estimated
routing.completed
tool.started
tool.completed
```

---

### Inspect a Direct Tool Savings Run

```bash
orch tool run datetime.local --agent Bob

orch runs --type tool --limit 5
orch run-info <run_id>
orch run-info <run_id> --json
```

Expected:

```text
routing.bypassed
policy.checked
tool.started
tool.completed
estimated_tokens_saved: > 0
token_source: estimated
```

---

### Inspect a Policy Hold

```bash
orch tool run gmail.send   --agent Bob   --arg to=studio@example.com   --arg subject="Test"   --arg body="Hello"
```

Expected:

```text
policy.checked status=hold_for_confirmation
run status=hold_for_confirmation
tool.started should not appear
```

Then inspect:

```bash
orch runs --status hold_for_confirmation
orch run-info <run_id>
```

---

### Inspect a Confirmed Tool Run

```bash
orch tool run gmail.send   --agent Bob   --arg to=studio@example.com   --arg subject="Observability test"   --arg body="Testing Orchgentic observability."   --arg confirm=true
```

Expected:

```text
policy.checked status=allow
tool.started
tool.completed
run.completed
```

---

### Export for a Dashboard

```bash
orch export-run <run_id> --output exports/run.json
orch export-runs --limit 100 --output exports/runs.jsonl
```

The first file is useful for a run detail view.

The second file is useful for a dashboard run list.

---

## Interpreting Token Fields

### `total_tokens`

Tokens consumed by LLM/provider calls when known or estimated.

For local tool-only runs, this should usually be:

```text
total_tokens: 0
```

### `estimated_tokens_saved`

Approximate LLM tokens avoided.

Examples:

```text
local deterministic route
→ avoided an LLM call

direct tool run
→ bypassed LLM routing/tool-selection

policy block or confirmation hold
→ prevented unnecessary escalation
```

### `token_source`

```text
actual
→ provider returned usage

estimated
→ Orchgentic estimated usage or savings

not_applicable
→ no token cost applies to this event

unknown
→ token usage may exist but cannot be safely calculated
```

---

## Notes and Limitations

- Token savings are estimates, not exact billing numbers.
- USD cost is intentionally not tracked in v0.8.0.
- Older runs created before observability hotfixes will not have newer trace events retroactively.
- `judge-route` remains inspect-only and does not create run records.
- Export schema is versioned as `orchgentic.observability.v1`.
- The current export format is designed for future dashboards and external tooling.
