# Observability Examples

## Inspect recent runs

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
```

## Show token-relevant events

```bash
orch trace <run_id> --tokens
```

## Export run data

```bash
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

## Show observability stats

```bash
orch runs-stats
orch runs-stats --json
```

## Preview cleanup

```bash
orch runs-prune --older-than 30d --dry-run
```

## Failure diagnostics

```bash
orch failures
orch failures --group-by error_type
orch failures --json
```

## Generate dashboard

```bash
orch dashboard
```

## Generate and open dashboard

```bash
orch dashboard --open
```

## Generate filtered dashboard

```bash
orch dashboard --type tool --limit 50
orch dashboard --agent Bob
orch dashboard --team ContentTeam
```

## Dashboard drill-down

After generating the dashboard, click a Run ID to jump to that run’s embedded detail section.

The detail section includes:

```text
run metadata
task
token summary
trace event timeline
event messages
```

Use `Close`, click outside the modal, or press `Esc` to return to the dashboard summary.
