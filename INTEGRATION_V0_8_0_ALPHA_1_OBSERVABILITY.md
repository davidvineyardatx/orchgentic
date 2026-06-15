# v0.8.0-alpha.1 Observability Integration Guide

This patch adds the Orchgentic observability foundation.

## Files Added

```text
orchgentic/observability/__init__.py
orchgentic/observability/models.py
orchgentic/observability/store.py
orchgentic/observability/tracer.py
orchgentic/observability/formatters.py
tests/test_observability_v0_8_0.py
RELEASE_NOTES_V0_8_0_ALPHA_1.md
```

## Files Updated

```text
pyproject.toml
orchgentic/cli.py
orchgentic/agents/assistant.py
orchgentic/agents/manager.py
orchgentic/tools/runtime.py
orchgentic/orchestration/team_runner.py
```

## New Runtime Store

By default, observability data is written to:

```text
logs/orchgentic_observability.db
```

The database contains:

```text
runs
trace_events
```

## New CLI Commands

```bash
orch runs
orch runs --limit 10
orch runs --status failed
orch runs --type team
orch run-info <run_id>
```

`orch run-info` accepts a full run ID or an unambiguous run ID prefix.

## Token Design

The release tracks token usage and token savings only:

```text
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
```

It intentionally does not include USD cost fields.

## Validation

Run:

```bash
python -m pytest -q
```

Expected result from this patch:

```text
57 passed
```
