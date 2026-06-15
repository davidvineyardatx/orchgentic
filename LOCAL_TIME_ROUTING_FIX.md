# v0.7.11-alpha Local Time Routing Fix

Fixes a deterministic routing miss where prompts such as `what is the local time?` escalated to the external LLM instead of routing directly to `datetime.local`.

Changes:

- Expanded deterministic router date/time phrase coverage.
- Expanded local orchestration reasoner datetime phrase coverage.
- Fixed orchestration judgment tool discovery for the current `Registry.items` layout.
- Added regression tests for local time routing variants and registry tool count telemetry.

Expected behavior:

```text
Task: what is the local time?
→ selected_tool: datetime.local
→ external_llm_used: False
→ local_reasoner_confidence: 0.98
→ escalation_reason: not_required
→ reasoning_level: local_tool
```
