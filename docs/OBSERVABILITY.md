# Observability

Orchgentic includes a native observability foundation for inspecting agent runs, tool runs, team runs, routing decisions, policy checks, provider calls, token usage, and estimated token savings.

## What Observability Tracks

Run records include:

```text
run_id
run_type
status
task
agent_id / agent_name
team_id / team_name
provider
model
started_at
completed_at
duration_ms
external_llm_used
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
error_type
error_message
```

Trace events include:

```text
timestamp
event_type
component
name
status
message
token fields
event data
```

## Token Source Values

```text
actual
estimated
not_applicable
unknown
```

Estimated token savings are labeled as estimates. They are useful for understanding avoided LLM routing/execution overhead, not for billing claims.

## Common Commands

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

## Dashboard

Generate a dashboard:

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

`--open` opens the existing dashboard file and does not regenerate it.

## Dashboard Pagination

The dashboard paginates loaded rows in the browser.

```bash
orch dashboard --limit 500
orch dashboard --open
```

`--limit` controls how many recent runs are loaded into the static HTML file. Browser controls paginate that loaded set.

## Dashboard Controls

The dashboard includes:

```text
search box
quick filters
page size selector
First / Previous / Next / Last
visible/matching count
modal run details
copy buttons for CLI follow-up commands
```

## Exports

Single run export:

```bash
orch export-run <run_id> --output exports/run.json
```

Run history export:

```bash
orch export-runs --limit 100 --output exports/runs.jsonl
```

Schema label:

```text
orchgentic.observability.v1
```

## Observability Doctor

Use the doctor command to check store and dashboard readiness:

```bash
orch doctor observability
```

JSON output:

```bash
orch doctor observability --json
```

The doctor reports:

```text
schema
status
store
path
runs
events
latest_run
dashboard_output
dashboard_exists
exports_dir
exports_dir_exists
total_tokens
estimated_tokens_saved
hint
```

Possible statuses:

```text
ok
empty
not_initialized
```


## Beta.1 Schema Stability

For v0.8.0-beta.1, the public observability schema label is:

```text
orchgentic.observability.v1
```

This label is used in dashboard metadata, doctor output, and observability export conventions.

## v0.8.0-beta.2 clean-install behavior

The observability layer is expected to behave clearly before any runs exist. A fresh workspace can run:

```bash
orch doctor observability
orch dashboard
orch dashboard --open
```

`orch doctor observability` reports store, dashboard, exports directory, run count, event count, and actionable next steps. `orch dashboard` can generate a zero-run dashboard with first-run guidance. `orch dashboard --open` opens an existing dashboard only and tells the user to generate one first when the file is missing.
