# Orchgentic CLI Commands

This page lists the currently supported Orchgentic CLI commands for the installed `orch` CLI.

## Help

```bash
orch --help
orch <command> --help
```

## Workspace

```bash
orch init
orch init <path>
```

## Agent Commands

```bash
orch create-agent Bob
orch create-agent Bob --provider groq --model llama-3.3-70b-versatile
orch create-agent Bob --timezone America/Chicago --locale en-US
orch create-agent Bob --overwrite

orch list-agents
orch inspect-agent Bob
orch preflight-agent Bob --task "What time is it locally?"

orch run Bob
orch run Bob --debug
orch run Bob --show-plan
orch run Bob "What time is it locally?"
orch run Bob "What time is it locally?" --debug
orch run Bob "Write a short summary of Orchgentic." --debug
orch run Bob "Draft a plan" --no-reflection
orch run Bob "What time is it locally?" --no-preflight
```

`orch run Bob` remains interactive. Passing a quoted prompt runs that task directly, which is the recommended quickstart style for repeatable testing.

## Team Commands

```bash
orch create-team ContentTeam
orch create-team ContentTeam --orchestrator Manager --member Researcher --member Writer --member Reviewer
orch create-team ContentTeam --members Researcher,Writer,Reviewer
orch create-team ContentTeam --overwrite

orch list-teams
orch inspect-team ContentTeam
orch preflight-team ContentTeam --task "Research AI shopping trends and create an executive summary"

orch run-team ContentTeam
orch run-team ContentTeam --debug
orch run-team ContentTeam "Create a brief content outline for Orchgentic." --debug
```

## Routing and Policy Commands

Inspect routing without executing:

```bash
orch judge-route "what is the local time?" --agent Bob
orch judge-route "what is the local time?" --agent Bob --summary
orch judge-route "what is the local time?" --agent Bob --summary --json
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
orch judge-route "send a report email" --agent Bob --event-type webhook
```

Policy and route metrics:

```bash
orch policy-report "what is the local time?" --agent Bob
orch policy-report "what is the local time?" --agent Bob --json
orch route-metrics
```

`judge-route` and `policy-report` are analysis-only. Use `orch run` or `orch tool run` for execution.

## Tool Commands

```bash
orch list-tools
orch list-tools --agent Bob
orch list-capabilities

orch tool run datetime.local --agent Bob
orch tool run filesystem.read --agent Bob --arg path=README.md
orch tool run filesystem.write --agent Bob --arg path=notes/test.txt --arg content="Hello" --arg confirm=true
orch tool run gmail.send --agent Bob --arg to=studio@example.com --arg subject="Hello" --arg body="Testing" --arg confirm=true
orch tool run datetime.local --agent Bob --args '{}'
```

Direct tool runs are observable and can record estimated token savings when they bypass LLM routing.

## Workflow Commands

```bash
orch workflow list
orch workflow list --workflows-dir workflows

orch workflow inspect content_intelligence_summary
orch workflow inspect content_intelligence_summary --json
orch workflow inspect content_intelligence_summary --workflows-dir workflows

orch workflow validate
orch workflow validate --json
orch workflow validate content_intelligence_summary
orch workflow validate content_intelligence_summary --json
orch workflow validate --workflows-dir workflows

orch workflow doctor
orch workflow doctor --json
orch workflow doctor workflows/content_intelligence_summary.workflow.yaml
orch workflow doctor examples/workflows/daily-research-summary.yaml
orch workflow doctor examples/workflows/daily-research-summary.yaml --json
orch workflow doctor content_intelligence_summary
orch workflow doctor content_intelligence_summary --workflows-dir workflows
```

`workflow validate` validates the team-backed workflow blueprint registry. `workflow doctor` is the quickstart-facing diagnostic command and can validate both registered workflow ids and direct YAML file paths.

## Trigger Commands

```bash
orch list-triggers
orch trigger run order_webhook
orch trigger run order_webhook --debug
orch trigger heartbeat bob_heartbeat
orch serve-webhooks
orch serve-webhooks --host 127.0.0.1 --port 8000
```

## Memory Commands

```bash
orch memory recent --agent Bob
orch memory recent --agent Bob --limit 10
orch memory list --agent Bob
orch memory list --agent Bob --limit 50
orch memory episodes --agent Bob
orch memory episodes --agent Bob --limit 25
orch memory search "previous discussion" --agent Bob
orch memory search "previous discussion" --agent Bob --limit 25
orch memory clear --agent Bob --yes
```

## Knowledge Commands

```bash
orch knowledge ingest knowledge/example.txt --agent Bob
orch knowledge search "What is Orchgentic?" --agent Bob
orch knowledge search "What is Orchgentic?" --agent Bob --limit 5
orch knowledge list --agent Bob
orch knowledge clear --agent Bob --yes
```

## Gmail Connection Commands

```bash
orch connect gmail
orch connect gmail --name assistant
orch connect gmail --name assistant --credentials credentials.json

orch gmail list
orch gmail status --name assistant
orch gmail disconnect --name assistant
```

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
orch runs-stats --status completed
orch runs-stats --type agent
orch runs-stats --agent Bob
orch runs-stats --team ContentTeam

orch runs-prune --older-than 30d --dry-run
orch runs-prune --older-than 30d --no-dry-run --confirm
orch runs-prune --status failed --dry-run
orch runs-prune --limit 10 --dry-run

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
orch dashboard --limit 500
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

## Doctor Commands

```bash
orch doctor observability
orch doctor observability --json
orch doctor observability --output exports/custom-dashboard.html

orch doctor tool-contracts
orch doctor tool-contracts --json

orch doctor execution-tiers --agent Bob
orch doctor execution-tiers --agent Bob --json

orch doctor workflows
orch doctor workflows --json
orch doctor workflows --workflows-dir workflows
```

## Clean Generated Test/Runtime Data

Preview what would be removed:

```bash
orch clean-testdata
```

Show every matched path:

```bash
orch clean-testdata --verbose
```

Delete generated data after review:

```bash
orch clean-testdata --no-dry-run --confirm
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

`orch clean-testdata` removes generated local artifacts such as `logs/`, `exports/`, `memory/`, `.pytest_cache/`, `__pycache__/`, and `*.pyc`. It preserves source code, configuration folders, docs, `.env`, and provider credentials.
