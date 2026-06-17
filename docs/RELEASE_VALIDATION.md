# Release Validation

Recommended release validation flow.

## Clean Test Run

```bash
python -m pytest -q
python -m pytest -q tests/test_observability_v0_8_0.py
```

## Observability Doctor

```bash
orch doctor observability
```

A clean release workspace may show:

```text
status: empty
runs: 0
events: 0
```

That is acceptable after cleaning runtime artifacts.

## Dashboard Smoke Test

Create a small run:

```bash
orch tool run datetime.local --agent Bob
```

Generate and open the dashboard:

```bash
orch dashboard --limit 100
orch dashboard --open
```

Confirm:

```text
dashboard opens
metadata panel is present
pagination controls are present
Run ID opens modal
copy buttons work
footer shows schema
```

## Clean Runtime Artifacts Before Release

Remove generated local artifacts while preserving configuration:

```bash
orch clean-testdata
orch clean-testdata --verbose
orch clean-testdata --no-dry-run --confirm
```

The cleanup command removes generated runtime/test artifacts such as `logs/`, `exports/`, `memory/`, `.pytest_cache/`, `__pycache__/`, and `*.pyc` files. Default output is grouped for readability; use `--verbose` to list every matched cache/file path. It preserves configuration and source files such as `agents/`, `teams/`, `triggers/`, `docs/`, `.env`, provider credentials, and source code.


## Beta.1 Stabilization Checklist

```bash
python -m pytest -q
python -m pytest -q tests/test_observability_v0_8_0.py
orch doctor observability
orch dashboard --limit 500
orch dashboard --open
```

Confirm:

```text
schema label is orchgentic.observability.v1
observability CLI commands still work
dashboard opens without regenerating when using --open
filtered dashboard workflow works
dashboard pagination works
modal copy commands work
docs are aligned
runtime artifacts can be cleaned before release
```

## v0.8.0-beta.2 clean-install validation

Run these checks from a clean workspace or after clearing local runtime artifacts:

```bash
python -m pytest -q
python -m pytest -q tests/test_observability_v0_8_0.py
orch doctor observability
orch doctor observability --json
orch dashboard
orch dashboard --open
orch tool run datetime.local --agent Bob
orch doctor observability
orch dashboard --limit 500
orch dashboard --open
```

Expected clean-state behavior:

- `orch doctor observability` reports `empty` or `not_initialized` with actionable next steps.
- `orch dashboard` creates a valid dashboard even with zero runs.
- `orch dashboard --open` opens the existing dashboard only.
- After the first run, doctor reports run/event counts and dashboard refresh works.

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
