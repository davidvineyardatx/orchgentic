# Observability v0.8.0-beta.3

## Token Intelligence and Local Reasoning Proof

v0.8.0-beta.3 adds Token Intelligence to Orchgentic observability.

Token Intelligence shows:

- when Orchgentic avoided external LLM calls
- when work was routed locally or deterministically
- estimated tokens saved
- external tokens used
- local LLM candidate tokens
- premium/external candidate tokens
- token-relevant proof events
- human-readable reasons for token use or savings

## Key CLI Command

```bash
orch token-report
```

Useful filters:

```bash
orch token-report --status completed
orch token-report --type team
orch token-report --team ContentTeam
orch token-report --agent Bob
orch token-report --limit 500
orch token-report --json
```

## Token Share Metrics

Token Intelligence reports a token-work split instead of only run counts:

```text
local/deterministic share
external LLM share
token_work_total
```

Calculation:

```text
token_work_total = total_tokens_used + estimated_tokens_saved

local/deterministic share =
  estimated_tokens_saved / token_work_total

external LLM share =
  total_tokens_used / token_work_total
```

## Execution Tiers

Token proof events may be classified as:

```text
deterministic_saved
local_llm_candidate
premium_external_candidate
external_llm
proof_context
```

## Optimization Labels

Token proof events may include:

```text
already_avoided_external_llm
move_to_local_llm
keep_external_or_make_configurable
```

## Dashboard Behavior

The dashboard Token Intelligence panel recalculates when run filters change.

Filtering by team, agent, run type, status, or search text updates:

- local/deterministic share
- external LLM share
- token work total
- estimated tokens saved
- local LLM candidate tokens
- premium candidate tokens
- top savings run
- proof rows

## Dashboard Layout

The main dashboard panels now appear in this order:

1. Recent Failures
2. Recent Runs
3. Token Intelligence

Each major panel is collapsible.

## Token Reason Rows

Token Intelligence proof rows now display Reason text on its own follow-up row for readability.

This keeps the metrics table compact while preserving human-readable explanations.
