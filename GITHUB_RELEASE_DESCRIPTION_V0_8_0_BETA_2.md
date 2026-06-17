# v0.8.0-beta.2 — Observability Clean-Install Polish

This release hardens the Orchgentic observability foundation for clean installs, empty workspaces, release validation, and pre-publish cleanup.

## What changed

- Hardened `orch doctor observability` for clean and empty workspaces.
- Added doctor checks, next steps, store directory metadata, dashboard parent metadata, and clearer clean-install guidance.
- Improved dashboard behavior when there are zero runs.
- Preserved `orch dashboard --open` as an open-existing command that does not regenerate the dashboard.
- Fixed CLI trace formatting for estimated token savings output.
- Corrected doctor event counting so trace event totals reflect stored events.
- Clarified direct-tool runs where a provider is configured but no LLM was used.
- Added `orch clean-testdata` to safely remove generated local runtime/test artifacts before committing or publishing.

## New command

```bash
orch clean-testdata
orch clean-testdata --verbose
orch clean-testdata --no-dry-run --confirm
```

`orch clean-testdata` is dry-run by default. It removes generated artifacts only when `--no-dry-run --confirm` is provided. Config and source files are preserved.

## Validation

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q
```


## Final release cleanup

For a final clean workspace before publishing:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```

Run this as the last cleanup command before checking Git status, because running Python or `orch` can recreate `__pycache__/` and `*.pyc` files.
