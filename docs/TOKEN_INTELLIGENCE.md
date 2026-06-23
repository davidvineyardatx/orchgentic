# Token Intelligence

Token Intelligence shows where token-relevant work happened, what Orchgentic avoided, and what could be optimized next.

It turns agent orchestration from:

```text
black-box LLM usage
```

into:

```text
deterministic savings
local LLM candidates
premium model candidates
proof events
```

## Purpose

Token Intelligence answers:

- What used an external LLM?
- What avoided an external LLM?
- What was deterministic?
- What could move to a local LLM?
- What should remain premium or configurable?
- Why did each token-relevant decision happen?

## Core Command

```bash
orch token-report
```

Useful filters:

```bash
orch token-report --json
orch token-report --type workflow
orch token-report --type team
orch token-report --status completed
orch token-report --agent Bob
orch token-report --team ContentTeam
orch token-report --limit 500
```

## Key Metrics

### token_work_total

Total token-relevant work.

```text
token_work_total = total_tokens_used + estimated_tokens_saved
```

This is not a billing total. It is an operational view of work that either used tokens or avoided likely token usage.

### local_or_deterministic_token_rate

The share of token-relevant work handled locally or deterministically.

```text
local_or_deterministic_token_rate = estimated_tokens_saved / token_work_total
```

Example:

```text
local_or_deterministic_token_rate: 51.0% (31,405 saved/avoided)
```

### external_llm_token_rate

The share of token-relevant work that used an external LLM.

```text
external_llm_token_rate = total_tokens_used / token_work_total
```

Example:

```text
external_llm_token_rate: 49.0% (30,140 used)
```

### estimated_tokens_saved

Operational estimate of external tokens avoided through deterministic routing, direct tool execution, skipped tool-decision loops, or local reasoning.

Example:

```text
saved≈349, source=estimated
```

Estimated savings are not billing claims. They are operational estimates of avoided LLM routing/execution overhead.

### total_tokens

Estimated or actual tokens used by external LLM calls.

When provider usage metadata is unavailable, Orchgentic may estimate token usage.

### token_count_source

Explains where the usage count came from.

Valid values:

```text
actual
estimated
not_applicable
unknown
```

Important distinction:

```text
token_count_source = source of tokens used
estimated_tokens_saved = estimated avoided external token work
```

A run can use an external LLM and still have:

```text
token_count_source = estimated
```

That means usage was estimated because exact provider metadata was unavailable.

### external_tokens_local_candidate

External LLM tokens that appear eligible to move to a local LLM or cheaper execution tier.

Example:

```text
external_tokens_local_candidate: 17,134 (56.8%)
```

### external_tokens_premium_candidate

External LLM tokens that should likely remain premium-model work or become configurable.

Example:

```text
external_tokens_premium_candidate: 13,006
```

## Execution Tiers

Token Intelligence classifies events into execution tiers.

Common tiers:

```text
deterministic_saved
local_llm_candidate
premium_external_candidate
external_llm
proof_context
```

### deterministic_saved

Work avoided through deterministic routing, direct tool execution, or skipped LLM planning.

Optimization:

```text
already_avoided_external_llm
```

### local_llm_candidate

External LLM work that may be safe to move to a local LLM.

Optimization:

```text
move_to_local_llm
```

### premium_external_candidate

External LLM work that should likely stay on a premium model or become configurable.

Optimization:

```text
keep_external_or_make_configurable
```

## Optimization Opportunities

Token Intelligence should make optimization visible, not hidden.

Common values:

```text
already_avoided_external_llm
move_to_local_llm
keep_external_or_make_configurable
```

## Proof Events

Proof events are the reason Token Intelligence is credible.

Example proof events:

```text
routing.bypassed
llm.completed
tool.completed
```

A proof event should show:

```text
event
component
name
token meaning
tokens used
saved
count source
reason
execution tier
optimization
```

Example CLI line:

```text
routing.bypassed (routing/deterministic_team_role_routing) saved≈340, source=estimated tier=deterministic_saved opportunity=already_avoided_external_llm - Known team roles were assigned from team configuration without asking an external LLM to plan basic orchestration.
```

## Human-Readable Token Work Reasons

Reason strings should explain why the work happened in plain English.

Examples:

```text
Known team roles were assigned from team configuration without asking an external LLM to plan basic orchestration.
```

```text
Researcher should follow the deterministic research role contract instead of repeatedly asking an external LLM whether research tools are needed.
```

```text
Writer should draft from current team handoff context; basic tool-decision LLM calls are skipped by default.
```

```text
Reviewer should review current team handoff context; basic tool-decision LLM calls are skipped by default.
```

```text
Manager used the LLM during team synthesis to combine member outputs into the final response.
```

## Dashboard Interpretation

The Token Intelligence dashboard should help users quickly see:

- local/deterministic share
- external LLM share
- total tokens used
- estimated tokens saved
- deterministic routes
- direct bypasses
- local LLM candidate tokens
- premium candidate tokens
- top savings run
- proof events

A strong Token Intelligence story looks like:

```text
Orchgentic avoided deterministic orchestration spend,
identified remaining local LLM candidates,
and separated premium/configurable model usage.
```

## Example Report

```text
TOKEN INTELLIGENCE
filters: limit=100
loaded_runs: 2
token_work_total: 61545
local_or_deterministic_token_rate: 51.0% (31405 saved/avoided)
external_llm_token_rate: 49.0% (30140 used)
direct_tool_runs: 0
direct_bypasses: 10
deterministic_routes: 10
local_reasoning_events: 8
llm_events: 16
total_tokens: 30140
estimated_tokens_saved: 31405
external_tokens_local_candidate: 17134 (56.8%)
external_tokens_premium_candidate: 13006
```

## Recommended Product Message

```text
Orchgentic does not just orchestrate agents.
It identifies which orchestration decisions should never have required an external LLM in the first place.
```

## Design Rules

- Never present estimated savings as exact billing savings.
- Always distinguish tokens used from tokens saved.
- Always distinguish actual usage from estimated usage.
- Prefer readable reasons over internal-only labels.
- Tie optimization claims to proof events.
- Treat local LLM migration as an execution-tier decision, not merely a provider swap.

## Related Docs

- `OBSERVABILITY.md`
- `ROUTING_AND_REASONING.md`
- `WORKFLOWS.md`
