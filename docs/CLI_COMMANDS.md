# CLI Commands

This page lists the primary Orchgentic CLI commands, including the v0.8.0 observability and dashboard commands.

---

## Workspace

Initialize a workspace:

```bash
orch init
```

---

## Agents

Create an agent:

```bash
orch create-agent Bob
```

List agents:

```bash
orch list-agents
```

Inspect an agent:

```bash
orch inspect-agent Bob
```

Preflight an agent task:

```bash
orch preflight-agent Bob --task "what time is it locally?"
```

Run an agent:

```bash
orch run Bob
orch run Bob --debug
orch run Bob --show-plan
```

Judge a route without executing:

```bash
orch judge-route "what time is it locally?" --agent Bob
```

---

## Teams

Create a team:

```bash
orch create-team ContentTeam
```

List teams:

```bash
orch list-teams
```

Inspect a team:

```bash
orch inspect-team ContentTeam
```

Preflight a team task:

```bash
orch preflight-team ContentTeam --task "Produce a content strategy."
```

Run a team:

```bash
orch run-team ContentTeam
orch run-team ContentTeam --debug
```

---

## Tools

List tools:

```bash
orch list-tools
```

Run a tool directly:

```bash
orch tool run datetime.local --agent Bob
```

Run a tool with arguments:

```bash
orch tool run filesystem.write --agent Bob --arg path=notes/example.txt --arg content="Hello"
```

Run a destructive or policy-sensitive tool with confirmation:

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Observability test" \
  --arg body="Testing Orchgentic observability." \
  --arg confirm=true
```

---

## Memory

Search memory:

```bash
orch memory search "routing decision"
```

---

## Knowledge

Ingest knowledge:

```bash
orch knowledge ingest docs/README.md
```

Search knowledge:

```bash
orch knowledge search "observability"
```

---

## Triggers

Create a trigger:

```bash
orch create-trigger heartbeat
```

Run heartbeat triggers:

```bash
orch trigger heartbeat
```

Run webhook server:

```bash
orch trigger webhook
```

---

# Observability Commands

Orchgentic v0.8.0 includes native observability commands for run history, trace inspection, exports, retention cleanup, failure diagnostics, and dashboard generation.

---

## Run History

Show recent runs:

```bash
orch runs
```

Limit results:

```bash
orch runs --limit 10
```

Filter runs:

```bash
orch runs --status completed
orch runs --status failed
orch runs --status hold_for_confirmation
orch runs --type agent
orch runs --type tool
orch runs --type team
orch runs --agent Bob
orch runs --team ContentTeam
```

JSON output:

```bash
orch runs --json
```

---

## Run Details

Inspect one run:

```bash
orch run-info <run_id>
```

JSON output:

```bash
orch run-info <run_id> --json
```

Show only the run summary:

```bash
orch run-info <run_id> --summary-only
```

Show only trace events:

```bash
orch run-info <run_id> --events-only
```

---

## Trace Inspection

Show trace events for a run:

```bash
orch trace <run_id>
```

Filter trace events:

```bash
orch trace <run_id> --component tool
orch trace <run_id> --component policy
orch trace <run_id> --component routing
orch trace <run_id> --component provider
orch trace <run_id> --component agent
orch trace <run_id> --component team
```

Filter by event type:

```bash
orch trace <run_id> --type tool.completed
orch trace <run_id> --type tool.failed
orch trace <run_id> --type llm.failed
orch trace <run_id> --type policy.checked
```

Show token-relevant trace events:

```bash
orch trace <run_id> --tokens
```

JSON output:

```bash
orch trace <run_id> --json
```

---

## Exports

Export one run as dashboard-ready JSON:

```bash
orch export-run <run_id>
```

Export one run to a file:

```bash
orch export-run <run_id> --output exports/run.json
```

Compact JSON:

```bash
orch export-run <run_id> --compact
```

Export run history as JSONL:

```bash
orch export-runs --limit 100
```

Export run history to a file:

```bash
orch export-runs --limit 100 --output exports/runs.jsonl
```

Filter exported run history:

```bash
orch export-runs --status completed
orch export-runs --type tool
orch export-runs --agent Bob
orch export-runs --team ContentTeam
```

---

## Run Statistics

Show observability stats:

```bash
orch runs-stats
```

JSON output:

```bash
orch runs-stats --json
```

Filter stats:

```bash
orch runs-stats --status completed
orch runs-stats --type tool
orch runs-stats --agent Bob
orch runs-stats --team ContentTeam
```

---

## Retention and Cleanup

Preview pruning old runs:

```bash
orch runs-prune --older-than 30d --dry-run
```

Preview pruning failed runs:

```bash
orch runs-prune --status failed --dry-run
```

Preview pruning tool runs:

```bash
orch runs-prune --type tool --older-than 7d --dry-run
```

Delete matching runs after preview:

```bash
orch runs-prune --older-than 30d --no-dry-run --confirm
```

Delete one run:

```bash
orch run-delete <run_id> --confirm
```

Safety notes:

```text
runs-prune defaults to dry-run
actual pruning requires --no-dry-run --confirm
run-delete requires --confirm
deleting a run also deletes its trace events
```

Supported retention windows:

```text
12h
30d
2w
```

---

## Failure Diagnostics

Show failed runs:

```bash
orch failures
```

Limit failures:

```bash
orch failures --limit 20
```

Filter failures:

```bash
orch failures --type tool
orch failures --type agent
orch failures --type team
orch failures --agent Bob
orch failures --team ContentTeam
```

Group by error type:

```bash
orch failures --group-by error_type
```

JSON output:

```bash
orch failures --json
```

---

## Static Observability Dashboard

Generate the local dashboard:

```bash
orch dashboard
```

Default output:

```text
exports/orchgentic_observability_dashboard.html
```

Generate and open the dashboard:

```bash
orch dashboard --open
```

Custom output path:

```bash
orch dashboard --output exports/dashboard.html
```

Filter dashboard data:

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

The dashboard includes:

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
embedded run detail sections
trace event timelines
```

Run IDs in the dashboard are clickable. Clicking a Run ID jumps to an embedded detail section for that run.

Use:

```text
↑ Minimize
```

to return from the run detail section back to the dashboard summary.

---

## Common Observability Workflow

Run something:

```bash
orch run Bob --debug
```

Find the run:

```bash
orch runs --agent Bob --limit 5
```

Inspect the run:

```bash
orch run-info <run_id>
```

Inspect token-relevant events:

```bash
orch trace <run_id> --tokens
```

Generate the dashboard:

```bash
orch dashboard --open
```

Export data for external systems:

```bash
orch export-run <run_id> --output exports/run.json
orch export-runs --limit 100 --output exports/runs.jsonl
```

---

## Token Fields

Observability tracks:

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
