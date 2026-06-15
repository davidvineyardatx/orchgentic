# Observability CLI Examples

This guide contains copy/paste examples for the Orchgentic v0.8.0 observability CLI.

---

## 1. View Recent Runs

```bash
orch runs
```

Example output:

```text
RUNS
fb995dfd  completed  tool     Bob                saved≈349, source=estimated      datetime.local {}
f0b54593  completed  agent    Bob                saved≈343, source=estimated      what is the current time
c739c029  completed  agent    Bob                tokens=1678, source=estimated    Write a short summary of what Orchgentic is.
```

---

## 2. Inspect One Run

```bash
orch run-info fb995dfd
```

Example output:

```text
RUN
id: fb995dfd-38fe-4fab-96b2-d7919493d65e
type: tool
status: completed
agent: Bob
external_llm_used: False
input_tokens: 0
output_tokens: 0
total_tokens: 0
estimated_tokens_saved: 349
token_source: estimated
task: datetime.local {}

TRACE EVENTS
- run.started
- routing.bypassed
- policy.checked
- tool.started
- tool.completed
- run.completed
```

---

## 3. Inspect a Run as JSON

```bash
orch run-info fb995dfd --json
```

Use this when you want the full machine-readable trace.

---

## 4. Show Only Trace Events

```bash
orch run-info fb995dfd --events-only
```

---

## 5. Show Only the Summary

```bash
orch run-info fb995dfd --summary-only
```

---

## 6. Trace Only Tool Events

```bash
orch trace fb995dfd --component tool
```

Expected event types:

```text
tool.started
tool.completed
```

---

## 7. Trace Only Policy Events

```bash
orch trace fb995dfd --component policy
```

Expected event type:

```text
policy.checked
```

---

## 8. Trace Token-Relevant Events

```bash
orch trace fb995dfd --tokens
```

Expected for a direct tool run:

```text
routing.bypassed ... saved≈349, source=estimated
```

---

## 9. Test Local Reasoning Token Savings

Run an agent task that should stay local:

```bash
orch run Bob --debug
```

Task:

```text
what is the current time
```

Then inspect it:

```bash
orch runs --agent Bob --limit 5
orch run-info <run_id>
```

Expected:

```text
external_llm_used: False
estimated_tokens_saved: > 0
token_source: estimated
routing.completed
tool.started
tool.completed
```

---

## 10. Test Direct Tool Token Savings

```bash
orch tool run datetime.local --agent Bob
```

Then inspect:

```bash
orch runs --type tool --limit 5
orch run-info <run_id>
orch run-info <run_id> --json
```

Expected:

```text
routing.bypassed
estimated_tokens_saved: > 0
token_source: estimated
```

In JSON, the `routing.bypassed` event should include:

```json
{
  "savings_reason": "direct_tool_execution_bypassed_llm_routing",
  "token_estimate": {
    "system_prompt_tokens": 24,
    "memory_context_tokens": 0,
    "tool_context_tokens": 21,
    "task_tokens": 4,
    "expected_completion_tokens": 300,
    "total": 349
  }
}
```

---

## 11. Test an LLM-Backed Run

Run an agent task that needs generation:

```bash
orch run Bob --debug
```

Task:

```text
Write a short summary of what Orchgentic is.
```

Then inspect:

```bash
orch runs --agent Bob --limit 5
orch run-info <run_id>
orch trace <run_id> --component provider
```

Expected:

```text
external_llm_used: True
llm.started
llm.completed
total_tokens: > 0
```

---

## 12. Test Gmail Send Confirmation Hold

Do not include `confirm=true`:

```bash
orch tool run gmail.send   --agent Bob   --arg to=studio@example.com   --arg subject="Test"   --arg body="Hello"
```

Expected:

```text
hold_for_confirmation
```

Inspect:

```bash
orch runs --status hold_for_confirmation
orch run-info <run_id>
```

Expected trace:

```text
run.started
routing.bypassed
policy.checked status=hold_for_confirmation
run.completed status=hold_for_confirmation
```

The tool should not execute.

---

## 13. Test Confirmed Gmail Send

Use a safe test address configured in `bob.yaml`.

```bash
orch tool run gmail.send   --agent Bob   --arg to=studio@example.com   --arg subject="Observability test"   --arg body="Testing Orchgentic observability."   --arg confirm=true
```

Inspect:

```bash
orch runs --type tool --limit 5
orch run-info <run_id>
```

Expected trace:

```text
run.started
routing.bypassed
policy.checked status=allow
tool.started
tool.completed
run.completed
```

---

## 14. Export One Run

```bash
orch export-run <run_id>
```

Expected shape:

```json
{
  "schema_version": "orchgentic.observability.v1",
  "exported_at": "...",
  "export_type": "run_detail",
  "run": {},
  "events": []
}
```

---

## 15. Export One Run to a File

```bash
orch export-run <run_id> --output exports/run.json
```

Expected:

```text
Exported run <full-run-id> to exports/run.json
```

On Windows, the path may display with backslashes:

```text
exports\run.json
```

---

## 16. Export Recent Runs as JSONL

```bash
orch export-runs --limit 5
```

Expected:

```text
{"schema_version":"orchgentic.observability.v1","export_type":"run_summary",...}
{"schema_version":"orchgentic.observability.v1","export_type":"run_summary",...}
{"schema_version":"orchgentic.observability.v1","export_type":"run_summary",...}
```

Each line is one run summary.

---

## 17. Export Recent Runs to a File

```bash
orch export-runs --limit 100 --output exports/runs.jsonl
```

Expected:

```text
Exported 100 runs to exports/runs.jsonl
```

---

## 18. Export Failed Runs

```bash
orch export-runs --status failed --output exports/failed-runs.jsonl
```

---

## 19. Export Team Runs

```bash
orch export-runs --type team --output exports/team-runs.jsonl
```

---

## 20. Export Bob Runs

```bash
orch export-runs --agent Bob --output exports/bob-runs.jsonl
```

---

## Recommended Manual Validation Sequence

After applying v0.8.0 observability patches, run:

```bash
python -m pytest -q
python -m pytest -q tests/test_observability_v0_8_0.py
```

Then:

```bash
orch tool run datetime.local --agent Bob
orch runs --type tool --limit 5
orch run-info <run_id>
orch run-info <run_id> --json
orch trace <run_id> --tokens
orch export-run <run_id> --output exports/run.json
orch export-runs --limit 5 --output exports/runs.jsonl
```

Acceptance criteria:

```text
tests pass
orch runs works
orch run-info works
orch trace works
export-run works
export-runs works
direct tool run shows routing.bypassed
token savings are estimated and labeled
no USD cost fields appear
schema_version is orchgentic.observability.v1
```
