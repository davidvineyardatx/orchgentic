# Static Observability Dashboard

Orchgentic can generate a local static HTML dashboard from the observability database.

This is the first developer-facing UI for Orchgentic observability. It gives developers a quick visual summary of runs, failures, token usage, estimated token savings, and run-level trace details.

---

## Generate Dashboard

```bash
orch dashboard
```

Default output:

```text
exports/orchgentic_observability_dashboard.html
```

The dashboard header displays:

```text
RUN DASHBOARD
```

Subtitle:

```text
Summary of runs, failures, token usage, and estimated savings.
```

---

## Open in Browser

```bash
orch dashboard --open
```

---

## Custom Output Path

```bash
orch dashboard --output exports/dashboard.html
```

---

## Filter Dashboard Data

```bash
orch dashboard --limit 50
orch dashboard --status completed
orch dashboard --status failed
orch dashboard --type tool
orch dashboard --type agent
orch dashboard --type team
orch dashboard --agent Bob
orch dashboard --team ContentTeam
```

---

## Dashboard Includes

```text
total runs
failure count
total tokens
estimated tokens saved
run breakdown by status
run breakdown by type
failure breakdown by error type
recent runs
recent failures
clickable Run IDs
modal run detail views
trace event timelines
```

---

## Clickable Run IDs

Run IDs in the dashboard are clickable.

Clicking a Run ID jumps to an modal detail view for that run.

Each link and target are generated together:

```text
href="#run-<full_run_id>"
id="run-<full_run_id>"
```

Each run detail section includes:

```text
run metadata
task
token summary
trace events
event messages
```

Use `Close`, click outside the modal, or press `Esc` to return to the dashboard summary.

---

## When to Use CLI vs Dashboard

Use the dashboard for a fast visual overview.

Use the CLI for deeper inspection:

```bash
orch run-info <run_id>
orch trace <run_id>
orch failures
orch export-run <run_id>
orch export-runs --limit 100 --output exports/runs.jsonl
```

---

## Related Commands

```bash
orch runs
orch run-info <run_id>
orch trace <run_id>
orch runs-stats
orch failures
orch dashboard
```

---

## Notes

- The dashboard is a static HTML file.
- No server is required.
- No frontend build step is required.
- It reads local observability data only.
- The dashboard schema label is `orchgentic.observability.dashboard.v1`.

---

## Modal Run Details

Run details open in a modal window.

When a Run ID is selected:

```text
a modal opens
run metadata is shown
task details are shown
trace events are shown
the dashboard remains in place behind the modal
```

Close the modal by selecting `Close`, clicking outside the modal, or pressing `Esc`.
