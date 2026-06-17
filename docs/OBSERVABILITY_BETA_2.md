# v0.8.0-beta.2 — Observability hardening and clean-install polish

This beta hardens the observability experience for fresh workspaces, empty stores, missing dashboard files, and first-run developer flows.

## Focus

- Clean-install observability behavior
- Empty workspace dashboard behavior
- Clear `orch dashboard --open` handling when no dashboard exists yet
- More detailed `orch doctor observability` output
- Fresh workspace guidance inside the static dashboard
- Stable schema/version reporting

## Clean workspace flow

```bash
orch doctor observability
orch dashboard
orch dashboard --open
orch tool run datetime.local --agent Bob
orch doctor observability
orch dashboard
orch dashboard --open
```

Before any runs exist, `orch doctor observability` should clearly report whether the store exists, whether the dashboard exists, whether the exports directory exists, and what command to run next.

## Doctor output additions

`orch doctor observability` now includes additional clean-install metadata:

```text
store_dir
store_dir_exists
dashboard_parent
dashboard_parent_exists
next_steps
checks
```

The JSON form includes the same data:

```bash
orch doctor observability --json
```

## Dashboard zero-run behavior

`orch dashboard` can generate a useful dashboard even when no runs exist. The dashboard includes a fresh workspace guidance panel with commands for creating a first trace, checking health, refreshing the dashboard, and opening the existing dashboard.

## Open behavior

`orch dashboard --open` opens an existing dashboard file only. It does not regenerate the dashboard. If the file does not exist, the CLI now gives clearer guidance:

```text
Run `orch dashboard` first to generate it, then run `orch dashboard --open`.
```

## Acceptance criteria

- Fresh workspace state is understandable.
- Empty observability stores are not treated as failures.
- Dashboard generation works with zero runs.
- Dashboard open behavior is explicit and safe.
- Doctor output gives actionable next steps.
- Tests cover clean-install and zero-run behavior.


## Release cleanup

Before committing or publishing a release, remove generated local runtime/test artifacts while preserving configuration and source files:

```bash
orch clean-testdata
orch clean-testdata --verbose
orch clean-testdata --no-dry-run --confirm
```

`orch clean-testdata` is a dry run by default. It removes generated artifacts such as `logs/`, `exports/`, `memory/`, `.pytest_cache/`, `__pycache__/`, and `*.pyc` files only when `--no-dry-run --confirm` is provided. It preserves `agents/`, `teams/`, `triggers/`, `docs/`, `.env`, provider credentials, and source code.

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
