# Observability Examples

## Prove Deterministic Tool Savings

```bash
orch tool run datetime.local --agent Bob
orch token-report
orch dashboard --open
```

Expected story:

```text
No external LLM was needed.
The tool was routed directly.
Estimated external LLM routing overhead was avoided.
The trace contains proof.
```

## Prove Team Routing Savings

```bash
orch run-team contentteam --debug
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

Expected story:

```text
Basic team role routing was deterministic.
Manager planning did not require an external LLM.
Researcher tool-decision loops were bypassed.
Writer, Reviewer, and Synthesis tool-decision calls were bypassed.
External LLM usage was focused on content generation, review, or synthesis.
```

## Read the Token Intelligence Split

Example interpretation:

```text
local/deterministic share: 50.6%
external LLM share: 49.4%
estimated tokens saved: 15,850
local LLM candidate tokens: 8,670
premium candidate tokens: 6,829
```

Meaning:

```text
Orchgentic already avoided 15,850 estimated external tokens.
8,670 remaining external tokens may be local LLM candidates.
6,829 remaining external tokens are premium/configurable candidates.
```
