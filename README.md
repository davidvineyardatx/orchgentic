# Orchgentic


## Observability Dashboard

Generate a local static dashboard:

```bash
orch dashboard
```

Open the existing dashboard:

```bash
orch dashboard --open
```

Generate a filtered dashboard and then open it:

```bash
orch dashboard --team ContentTeam
orch dashboard --open
```

Dashboard features include search, quick filters, client-side pagination, modal run details, copy commands, empty states, and a generated metadata panel.


## v0.8.0-beta.1 Observability

The v0.8.0 observability foundation includes run history, trace inspection, exports, failure diagnostics, retention cleanup, a local static dashboard, dashboard pagination, and `orch doctor observability`.

Schema:

```text
orchgentic.observability.v1
```

## v0.8.0-beta.2 observability polish

This beta hardens clean-install observability behavior. A fresh workspace can run `orch doctor observability`, generate a zero-run dashboard with `orch dashboard`, and open the existing dashboard with `orch dashboard --open` after generation.


## Release cleanup

```bash
orch clean-testdata
orch clean-testdata --no-dry-run --confirm
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
