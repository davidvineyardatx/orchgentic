# v0.8.0-beta.1 Observability Stabilization

This beta stabilizes the v0.8.0 observability foundation for broader developer testing.

## Stabilized Areas

```text
observability schema label
core observability CLI commands
dashboard generation/open behavior
dashboard filtering
dashboard search
dashboard pagination
modal run details
copy commands
empty states
metadata panel
export commands
failure diagnostics
retention cleanup
doctor checks
```

## Schema

The observability schema label is frozen for beta testing:

```text
orchgentic.observability.v1
```

## Core Commands

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id>
orch export-runs
orch runs-stats
orch runs-prune
orch run-delete <run_id> --confirm
orch failures
orch dashboard
orch doctor observability
```

## Dashboard Behavior

```bash
orch dashboard
```

generates the dashboard.

```bash
orch dashboard --open
```

opens the existing dashboard without regenerating it.

Filtered workflow:

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

## Beta Validation

Run:

```bash
python -m pytest -q
python -m pytest -q tests/test_observability_v0_8_0.py

orch doctor observability
orch dashboard --limit 500
orch dashboard --open
```

Confirm:

```text
doctor command reports ok/empty/not_initialized clearly
dashboard footer shows schema
dashboard search works
quick filters work
pagination works
Run ID opens modal
copy buttons work
exports still work
cleanup commands still require confirmation
```

## Not Included in beta.1

```text
hosted dashboard
server mode
charts
multi-page generated dashboard files
external telemetry backend
USD cost tracking
```
