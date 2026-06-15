# Orchgentic v0.8.0-alpha.1 Release Notes

## Observability Foundation

v0.8.0-alpha.1 introduces the first native observability layer for Orchgentic.

The goal of this release is to make every Orchgentic run inspectable, traceable, and dashboard-ready.

## Added

- `orchgentic.observability` package
- `RunRecord` model for top-level run history
- `TraceEvent` model for structured execution traces
- SQLite-backed `ObservabilityStore`
- `TraceCollector` runtime helper
- CLI command: `orch runs`
- CLI command: `orch run-info <run_id>`
- Trace events for agent runs
- Trace events for team runs
- Trace events for team members
- Trace events for team synthesis
- Trace events for tool execution
- Trace events for provider/LLM calls where visible to the runtime
- Trace events for policy block and confirmation-hold outcomes
- Token usage fields without USD cost fields
- Estimated token savings rollups for local deterministic routes

## Event Levels

v0.8.0-alpha.1 separates observability into clear event levels:

```text
run-level events
agent-level events
team-level events
reasoning/routing/policy/tool/provider events
```

Standalone agent runs use:

```text
run.started
agent.started
agent.completed
run.completed
```

Team runs use:

```text
run.started
team.started
team.member.started
agent.started
agent.completed
team.member.completed
team.synthesis.started
team.synthesis.completed
team.completed
run.completed
```

## Token Fields

Run records and trace events now support token fields:

```text
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
```

Supported token source values:

```text
actual
estimated
not_applicable
unknown
```

No USD cost fields are included in this release. That is intentional because provider pricing, discounts, local inference costs, and future pricing changes can make cost estimates misleading.

## New CLI Commands

List recent runs:

```bash
orch runs
```

Inspect a run and its trace events:

```bash
orch run-info <run_id>
```

`run-info` supports full run IDs and unambiguous run ID prefixes.

## Tests

Added focused observability tests:

```text
tests/test_observability_v0_8_0.py
```

Validation:

```text
57 passed
```

## Notes

This is the foundation for future dashboard and export capabilities. The first priority is clean native run history and trace persistence. Dashboard/UI work should come after the trace model has stabilized.
