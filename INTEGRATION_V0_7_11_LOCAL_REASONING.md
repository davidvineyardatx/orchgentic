# v0.7.11-alpha Integration Notes

This package is aligned to the current Orchgentic layout. The reasoning layer lives in:

```text
orchgentic/core/reasoning/
```

The provider remains the single source of truth for provider/model selection. There is no `fallback_provider` under `reasoning.escalation`.

Run the focused tests with:

```bash
pytest tests/test_reasoning_v0_7_11.py
```

Recommended smoke test:

```bash
orch run Bob --debug
```

Expected behavior:

- Simple safe inputs may be answered locally.
- Tool-like inputs flow through the existing tool runtime.
- Complex or low-confidence inputs escalate to the agent's existing provider.
