# Observability

Orchgentic observability makes agent, team, tool, workflow, routing, and LLM activity inspectable.

The core goal is:

```text
Every meaningful runtime decision should leave a trace.
```

Observability is not only for debugging. It is the proof layer for Orchgentic's local-first, token-aware execution model.

## What Observability Tracks

Orchgentic tracks:

- runs
- run status
- run type
- target agent or team
- task
- start time
- completion time
- failures
- routing decisions
- tool execution
- LLM usage
- estimated token savings
- workflow metadata when a workflow is used

Common run types include:

```text
agent
team
workflow
tool
```

## Core Commands

### Show recent runs

```bash
orch runs
```

Useful filters:

```bash
orch runs --type workflow
orch runs --type team
orch runs --status completed
orch runs --status failed
```

### Inspect a run

```bash
orch run-info <run_id>
```

Use this to inspect one run's events, routing decisions, tool activity, token fields, and workflow metadata.

For workflow runs, useful proof fields include:

```text
workflow_id
workflow_name
workflow_version
workflow_source
workflow_step
```

### Generate the dashboard

```bash
orch dashboard --limit 500
```

### Open the existing dashboard

```bash
orch dashboard --open
```

`--open` opens the latest generated dashboard without rebuilding it.

### Check observability health

```bash
orch doctor observability
```

The doctor command checks whether the observability store, run data, event data, dashboard export path, and related runtime assumptions are healthy.

### Clean generated test/runtime data

Dry run:

```bash
orch clean-testdata
```

Verbose dry run:

```bash
orch clean-testdata --verbose
```

JSON dry run:

```bash
orch clean-testdata --json
```

Actual cleanup:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
```

PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; orch clean-testdata --no-dry-run --confirm
```

Cleanup is intended to remove generated runtime/test artifacts such as:

```text
logs/
exports/
memory/
.pytest_cache/
__pycache__/
*.pyc
```

It should preserve source code, docs, agent configs, team configs, triggers, provider credentials, and `.env`.

## Dashboard

The observability dashboard is a static HTML report generated from local run data.

Recommended command:

```bash
orch dashboard --limit 500
orch dashboard --open
```

The dashboard is organized around the most useful operational questions:

1. What failed recently?
2. What ran recently?
3. Where did tokens go?
4. What did Orchgentic avoid deterministically?
5. What could move to a local LLM?
6. What should remain premium/configurable?

Current major dashboard sections:

```text
Recent Failures
Recent Runs
Token Intelligence
```

Each major section should be collapsible so users can focus on the signal they need.

## Recent Failures

Recent Failures should help a developer quickly answer:

- what failed
- which run failed
- which agent/team/workflow failed
- what the likely cause was
- where to inspect details next

Failure diagnostics should prefer actionable language over raw trace dumps.

## Recent Runs

Recent Runs shows completed and failed activity across agents, teams, tools, and workflows.

Useful fields:

```text
Run
Status
Type
Agent / Team
Tokens
Task
Started
```

For workflow execution proof, a workflow run should appear with:

```text
Type = workflow
Agent / Team = <mapped team>
```

Example:

```text
Run        Status      Type       Agent / Team   Tokens
1626c34d   completed   workflow   ContentTeam    estimated tokens used=13749, source=estimated
```

## Run Detail

Run detail views should expose:

- run metadata
- task
- target
- provider used
- configured provider
- external LLM usage
- tool events
- routing decisions
- token usage
- estimated token savings
- proof events
- failure details, if any

For direct or deterministic runs, provider display should distinguish:

```text
provider used: N/A — no LLM used
configured provider: groq / llama-3.3-70b-versatile
external_llm_used: False
```

## Retention

Observability data is local runtime data. Retention should be simple and predictable.

The current cleanup path is:

```bash
orch clean-testdata --no-dry-run --confirm
```

Future retention policy should support:

- max runs
- max age
- dashboard export cleanup
- trace/event cleanup
- safe dry-run reporting

## Workflow Observability

Workflows are for coordinated, multi-step, team-backed execution.

Simple one-agent or one-tool tasks should use agents and direct tools, not workflows.

When a workflow is executed, observability should show:

```text
type = workflow
workflow_id = <workflow_id>
workflow_name = <workflow_name>
workflow_version = <version>
target = <team>
```

Workflow execution should also preserve the team-backed execution trace so Token Intelligence can still classify routing, tool decisions, and LLM usage.

## Observability Design Rules

- Do not hide whether an LLM was used.
- Do not hide why an LLM was used.
- Do not mix configured provider with provider actually used.
- Do not present estimated token savings as billing claims.
- Prefer concise reason strings that are readable in the CLI and dashboard.
- Every optimization claim should be traceable to an event.

## Related Docs

- `TOKEN_INTELLIGENCE.md`
- `WORKFLOWS.md`
- `ROUTING_AND_REASONING.md`
- `RELEASE_VALIDATION.md`
