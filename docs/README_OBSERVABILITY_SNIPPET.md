# README Observability Snippet

Add this section to `README.md` or link to `docs/OBSERVABILITY.md`.

---

## Observability

Orchgentic includes a native observability foundation for inspecting agent runs, tool runs, team runs, routing decisions, policy checks, provider calls, token usage, and estimated token savings.

Common commands:

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

Observability answers:

```text
What happened?
Where did it happen?
Why did it happen?
What was the outcome?
What did it cost in tokens, if known or safely estimated?
```

Run records and trace events are dashboard-ready and can be exported with the versioned schema:

```text
orchgentic.observability.v1
```

For full details, see:

```text
docs/OBSERVABILITY.md
docs/OBSERVABILITY_EXAMPLES.md
```
