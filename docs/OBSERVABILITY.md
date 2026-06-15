# Observability

Orchgentic includes a native observability foundation for inspecting agent runs, tool runs, team runs, routing decisions, policy checks, provider calls, token usage, estimated token savings, failures, exports, and dashboard views.

---

## Core Commands

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
```

---

## Export Commands

```bash
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

---

## Retention and Cleanup

```bash
orch runs-stats
orch runs-prune --older-than 30d --dry-run
orch runs-prune --older-than 30d --no-dry-run --confirm
orch run-delete <run_id> --confirm
```

---

## Failure Diagnostics

```bash
orch failures
orch failures --group-by error_type
orch failures --json
```

---

## Static Dashboard

```bash
orch dashboard
orch dashboard --open
orch dashboard --output exports/dashboard.html
```

The dashboard provides a local static UI for:

```text
run summaries
failure summaries
token usage
estimated token savings
clickable Run IDs
modal run details
trace event timelines
```

---

## Token Fields

```text
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
```

Valid `token_source` values:

```text
actual
estimated
not_applicable
unknown
```

Token savings are operational estimates, not billing claims. USD cost fields are intentionally omitted.

---

## Schema Labels

```text
orchgentic.observability.v1
orchgentic.observability.dashboard.v1
```
