## Observability

Orchgentic includes a native observability foundation for inspecting and explaining agent, tool, and team runs.

Common commands:

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch failures
orch runs-stats
orch dashboard
```

Generate the local dashboard:

```bash
orch dashboard --open
```

The dashboard includes run summaries, failures, token usage, estimated token savings, clickable Run IDs, modal run details, and trace event timelines.

Exports are available for external dashboards:

```bash
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

Schema labels:

```text
orchgentic.observability.v1
orchgentic.observability.dashboard.v1
```
