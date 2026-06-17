# Orchgentic CLI Commands

This page lists the commonly used Orchgentic CLI commands.

## Core Agent Commands

```bash
orch init
orch create-agent Bob
orch list-agents
orch run Bob
orch run Bob --debug
orch run Bob --show-plan
```

## Tool Commands

Run a tool directly:

```bash
orch tool run datetime.local --agent Bob
```

Run a tool with arguments:

```bash
orch tool run gmail.send --agent Bob --arg to=studio@example.com --arg subject="Hello" --arg body="Testing" --arg confirm=true
```

Direct tool runs are observable and can record estimated token savings when they bypass LLM routing.

## Team Commands

```bash
orch run-team ContentTeam
orch run-team ContentTeam --debug
```

## Routing and Reasoning

Inspect routing without executing:

```bash
orch judge-route "what is the local time?" --agent Bob
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

`judge-route` is analysis-only. Use `orch run` or `orch tool run` for execution.

## Observability Commands

List recent runs:

```bash
orch runs
orch runs --limit 10
orch runs --status completed
orch runs --status failed
orch runs --type tool
orch runs --type agent
orch runs --type team
orch runs --agent Bob
orch runs --team ContentTeam
orch runs --json
```

Inspect one run:

```bash
orch run-info <run_id>
orch run-info <run_id> --json
orch run-info <run_id> --events-only
orch run-info <run_id> --summary-only
```

Inspect a trace:

```bash
orch trace <run_id>
orch trace <run_id> --json
orch trace <run_id> --type tool.completed
orch trace <run_id> --component tool
orch trace <run_id> --component policy
orch trace <run_id> --tokens
```

Export observability data:

```bash
orch export-run <run_id>
orch export-run <run_id> --output exports/run.json

orch export-runs
orch export-runs --limit 100
orch export-runs --status completed
orch export-runs --type agent
orch export-runs --type team
orch export-runs --agent Bob
orch export-runs --team ContentTeam
orch export-runs --output exports/runs.jsonl
```

Run statistics and cleanup:

```bash
orch runs-stats
orch runs-stats --json

orch runs-prune --older-than 30d --dry-run
orch runs-prune --older-than 30d --no-dry-run --confirm
orch runs-prune --status failed --dry-run

orch run-delete <run_id> --confirm
```

Failure diagnostics:

```bash
orch failures
orch failures --limit 20
orch failures --type tool
orch failures --type agent
orch failures --type team
orch failures --agent Bob
orch failures --team ContentTeam
orch failures --group-by error_type
orch failures --json
```

## Dashboard Commands

Generate a dashboard:

```bash
orch dashboard
```

Generate a filtered dashboard:

```bash
orch dashboard --team ContentTeam
orch dashboard --agent Bob
orch dashboard --type tool
orch dashboard --status completed
```

Open the existing dashboard file without regenerating it:

```bash
orch dashboard --open
```

Recommended filtered workflow:

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

`--open` does not rebuild the dashboard. It opens the last generated HTML file.

Generate a larger loaded set for browser-side pagination:

```bash
orch dashboard --limit 500
orch dashboard --open
```

`--limit` controls how many recent runs are loaded into the static HTML file. The dashboard paginates that loaded set in the browser.

## Dashboard Features

The generated dashboard includes:

```text
run summary metrics
failure summary metrics
token usage
estimated token savings
active filters
generated metadata
search
quick filters
client-side pagination
modal run details
copy Run ID
copy run-info command
copy trace command
copy export command
empty states
```

## Doctor Commands

Diagnose observability readiness:

```bash
orch doctor observability
orch doctor observability --json
```

Check a custom dashboard path:

```bash
orch doctor observability --output exports/custom-dashboard.html
```


## Beta.1 Stable Observability Commands

The following command names are considered stable for v0.8.0-beta.1 developer testing:

```text
orch runs
orch run-info
orch trace
orch export-run
orch export-runs
orch runs-stats
orch runs-prune
orch run-delete
orch failures
orch dashboard
orch doctor observability
```

## Observability clean-install commands

```bash
orch doctor observability
orch doctor observability --json
orch dashboard
orch dashboard --open
orch tool run datetime.local --agent Bob
```

On a clean workspace, `orch doctor observability` explains whether the observability store exists, whether the dashboard file exists, whether the exports directory exists, and what to run next. `orch dashboard` can create a dashboard with zero runs. `orch dashboard --open` only opens an existing dashboard and does not regenerate it.

## Clean generated test/runtime data

Use this before committing or publishing a release when you want to remove local runtime artifacts but keep configuration files.

Preview what would be removed. By default, the command shows grouped targets so the output stays readable:

```bash
orch clean-testdata
```

Show every matched path when needed:

```bash
orch clean-testdata --verbose
```

Delete generated data after review:

```bash
orch clean-testdata --no-dry-run --confirm
```

The command removes generated local artifacts such as:

```text
logs/
exports/
memory/
.pytest_cache/
__pycache__/
*.pyc
```

It preserves configuration and source files such as:

```text
agents/
teams/
triggers/
docs/
.env
provider credentials
source code
```

Optional filters:

```bash
orch clean-testdata --no-memory
orch clean-testdata --no-exports
orch clean-testdata --no-logs
orch clean-testdata --no-caches
orch clean-testdata --verbose
orch clean-testdata --json
```

## Final release cleanup and Python bytecode

`orch clean-testdata` removes generated runtime/test artifacts, but running Python or `orch` may recreate `__pycache__/` and `*.pyc` files.

For the final cleanup before publishing a GitHub release, run cleanup as the last command before `git status`.

Git Bash:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```

PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; orch clean-testdata --no-dry-run --confirm
git status
```

After this final cleanup, avoid running `pytest`, `python`, or `orch` again before checking and committing, because those commands can recreate bytecode cache files.

## Token intelligence

```bash
orch token-report
orch token-report --limit 100
orch token-report --status completed
orch token-report --type tool
orch token-report --agent Bob
orch token-report --json
```

`orch token-report` summarizes local runs, external LLM runs, direct tool bypasses, deterministic routes, local reasoning events, LLM events, estimated tokens saved, and proof events. Estimated token savings are operational estimates, not billing claims.
