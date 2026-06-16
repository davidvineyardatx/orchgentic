## Observability

Orchgentic includes native observability for runs, trace events, token usage, estimated token savings, failures, exports, and a local static dashboard.

Common commands:

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

Generate a dashboard:

```bash
orch dashboard
```

Open the existing dashboard without regenerating:

```bash
orch dashboard --open
```

Generate a filtered dashboard and then open it:

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

Dashboard features:

```text
search
quick filters
client-side pagination
modal run details
copy CLI commands
empty states
metadata panel
```

Schema:

```text
orchgentic.observability.v1
```
