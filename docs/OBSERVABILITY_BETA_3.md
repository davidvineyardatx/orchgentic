# v0.8.0-beta.3 — Token Intelligence and Local Reasoning Proof

v0.8.0-beta.3 makes Orchgentic's token-savings story more visible and provable.

The goal is to show when Orchgentic avoided unnecessary external LLM calls, used deterministic/local routing, executed direct tools, and produced trace evidence for estimated token savings.

## New command

```bash
orch token-report
```

The report summarizes recent runs and highlights:

```text
loaded_runs
local_runs
external_llm_runs
direct_tool_runs
direct_bypasses
deterministic_routes
local_reasoning_events
llm_events
total_tokens
estimated_tokens_saved
proof_events
```

Example:

```bash
orch token-report --limit 100
orch token-report --status completed
orch token-report --type tool
orch token-report --agent Bob
orch token-report --json
```

## What the report proves

The token report is designed to answer:

```text
Was an external LLM used?
Was the run handled locally?
Was routing deterministic?
Did direct tool execution bypass LLM routing?
How many estimated tokens were avoided?
Which trace event proves that?
What was the reason?
```

For a direct tool run, the proof event should look similar to:

```text
routing.bypassed (routing/direct_tool) saved≈349, source=estimated - Direct tool execution bypassed LLM routing.
```

## Dashboard updates

The static dashboard now includes a **Token Intelligence** section with:

```text
local runs
external LLM runs
direct bypasses
deterministic routes
local reasoning events
LLM events
estimated tokens saved
top savings run
proof events
```

This section helps demonstrate that Orchgentic is not only recording token totals; it is showing why tokens were saved and which execution path produced the savings.

## Token-source note

Estimated token savings are operational estimates of avoided LLM routing/execution overhead. They are not billing claims.

The report and dashboard intentionally keep this clear so Orchgentic can prove avoided work without pretending to know exact provider billing.

## Suggested validation

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q

orch tool run datetime.local --agent Bob
orch token-report
orch token-report --json
orch dashboard --limit 500
orch dashboard --open
```

## Why this matters

This release strengthens Orchgentic's core product story:

```text
Orchgentic turns black-box agent behavior into observable, token-aware AI operations.
```

The runtime can now more clearly prove when it avoided LLM usage and preserved tokens through local reasoning, deterministic routes, and direct tool execution.

## Token Intelligence run modal

Run IDs in the Token Intelligence section open a focused token-only modal.

This keeps dashboard behavior consistent with other run links while limiting the modal content to token intelligence fields for that specific run:

```text
external_llm_used
local_execution
provider used
configured provider
input_tokens
output_tokens
total_tokens
estimated_tokens_saved
token_source
token_proof_events
```

The token modal intentionally excludes the full trace timeline and general run detail fields. Use the regular run table/modal for full run inspection, and use the Token Intelligence modal when validating savings, local execution, and LLM avoidance.


## Dashboard title polish

The main dashboard title is now `DASHBOARD` so the page reads as the overall Orchgentic observability dashboard rather than only a run dashboard.
