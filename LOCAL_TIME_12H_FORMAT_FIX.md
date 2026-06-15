# Local Time 12-Hour Format Fix

This patch keeps deterministic local-time routing on the no-LLM path and formats the user-facing answer with a 12-hour AM/PM clock for `en-US` style output.

## Changes

- `orchgentic/runtime/time_context.py` now includes `time_12h` in datetime tool data.
- `orchgentic/runtime/deterministic_formatter.py` prefers `time_12h` and falls back by converting `HH:MM:SS` to `h:MM:SS AM/PM`.
- Added focused tests for deterministic formatter output and time context data.

## Expected debug answer

```text
The current local time is 6:31:45 PM (America/Chicago). Today is Thursday, 2026-06-11.
```

Routing should still show:

```text
external_llm_used: False
selected_tool: datetime.local
reasoning_level: local_tool
```
