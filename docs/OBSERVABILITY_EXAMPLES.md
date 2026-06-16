# Observability Examples

## Inspect Recent Runs

```bash
orch runs --limit 10
```

## Inspect a Run

```bash
orch run-info <run_id>
```

## Inspect Trace Events

```bash
orch trace <run_id>
orch trace <run_id> --tokens
orch trace <run_id> --component tool
orch trace <run_id> --type policy.checked
```

## Export One Run

```bash
orch export-run <run_id> --output exports/run.json
```

## Export Run History

```bash
orch export-runs --limit 100 --output exports/runs.jsonl
```

## Generate and Open Dashboard

```bash
orch dashboard
orch dashboard --open
```

## Generate a Team Dashboard

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

## Generate an Agent Dashboard

```bash
orch dashboard --agent Bob
orch dashboard --open
```

## Generate a Larger Dashboard for Pagination

```bash
orch dashboard --limit 500
orch dashboard --open
```

Then use browser-side controls:

```text
Page size
First / Previous / Next / Last
Search
Quick filters
```

## Search Example

Use the dashboard search box to find:

```text
bob
ContentTeam
failed
tool
gmail
datetime.local
```

## Modal Follow-Up Workflow

Click a Run ID, then copy one of:

```bash
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id> --output exports/run-<short_id>.json
```

## Empty State Example

If a search hides all loaded rows, the dashboard shows:

```text
No runs match the current search or quick filter.
```

Clear the search box or choose `All` to restore loaded rows.
