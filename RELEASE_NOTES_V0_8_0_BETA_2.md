# v0.8.0-beta.2 — Observability Clean-Install Polish

This beta hardens Orchgentic observability for clean workspaces, release hygiene, and local development workflows.

## Highlights

- Improved `orch doctor observability` output for empty and clean workspaces.
- Added observability directory metadata, checks, and next-step guidance.
- Improved zero-run dashboard behavior and clean dashboard generation.
- Preserved `orch dashboard --open` as an open-existing operation.
- Fixed trace formatting for estimated token savings messages.
- Corrected observability event counting in doctor output.
- Clarified direct-tool runs where no LLM provider was used.
- Added `orch clean-testdata` for safe release cleanup.

## New cleanup command

Preview generated runtime/test artifacts:

```bash
orch clean-testdata
```

Show every matched path:

```bash
orch clean-testdata --verbose
```

Delete generated artifacts after review:

```bash
orch clean-testdata --no-dry-run --confirm
```

The command removes generated data such as `logs/`, `exports/`, `memory/`, `.pytest_cache/`, `__pycache__/`, and `*.pyc` files. It preserves configuration and source files such as `agents/`, `teams/`, `triggers/`, `docs/`, `.env`, provider credentials, and source code.

## Validation target

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q
orch clean-testdata
orch clean-testdata --verbose
orch clean-testdata --no-dry-run --confirm
orch doctor observability
```

- Documented final release cleanup with `PYTHONDONTWRITEBYTECODE=1` to avoid recreating Python bytecode caches before `git status`.
