# Observability Dashboard

The Orchgentic observability dashboard is a local, static HTML dashboard generated from the local observability store.

It is intentionally dependency-free:

```text
no server
no hosted service
no frontend build
no external dashboard dependency
```

## Generate a Dashboard

```bash
orch dashboard
```

Default output:

```text
exports/orchgentic_observability_dashboard.html
```

## Open Existing Dashboard

```bash
orch dashboard --open
```

`--open` opens the existing dashboard file. It does **not** regenerate the dashboard.

This prevents accidental loss of filters.

## Filtered Dashboard Workflow

Generate a filtered dashboard:

```bash
orch dashboard --team ContentTeam
```

Open that exact generated file:

```bash
orch dashboard --open
```

Other filters:

```bash
orch dashboard --agent Bob
orch dashboard --type tool
orch dashboard --status completed
```

Supported aliases:

```bash
orch dashboard --agent-name Bob
orch dashboard --team-name ContentTeam
```

## Loaded Runs and Pagination

The dashboard is a static snapshot. `--limit` controls how many recent runs are loaded into the HTML file:

```bash
orch dashboard --limit 500
```

The browser then paginates the loaded rows.

Dashboard pagination controls:

```text
Page size: 25 / 50 / 100 / All
First
Previous
Next
Last
Showing X–Y of Z matching runs
```

Pagination works with search and quick filters.

## Search and Quick Filters

The dashboard includes client-side search over:

```text
run id
status
type
agent/team
task
```

Quick filters:

```text
All
Completed
Failed
Holds
Tool
Agent
Team
```

## Modal Run Details

Click a Run ID to open a modal with run details and trace events.

The modal can be closed with:

```text
Close button
Esc key
click outside the modal
```

## Copy Buttons

The run detail modal includes copy buttons for:

```text
Copy Run ID
Copy run-info command
Copy trace command
Copy export command
```

Generated commands look like:

```bash
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id> --output exports/run-<short_id>.json
```

## Empty States

The dashboard distinguishes:

```text
no runs loaded
no failed runs
no runs matching current search/filter
```

## Metadata Panel

The dashboard metadata panel shows:

```text
generated_at
database path
active filters
limit
loaded runs
loaded failures
matching/visible runs
success rate
schema label
```

Schema label:

```text
orchgentic.observability.v1
```

## Dashboard Reliability Check

Use the observability doctor before release validation:

```bash
orch doctor observability
```

The dashboard footer also includes the schema label, generated timestamp, and inspection command hints.

## Empty dashboard and first-run guidance

In v0.8.0-beta.2, the dashboard can be generated before any run data exists:

```bash
orch dashboard
```

When there are zero runs, the dashboard shows a fresh workspace guidance panel with the recommended first commands:

```bash
orch tool run datetime.local --agent Bob
orch doctor observability
orch dashboard
orch dashboard --open
```

`orch dashboard --open` intentionally opens the existing dashboard file without regenerating it. If the dashboard file is missing, run `orch dashboard` first.
