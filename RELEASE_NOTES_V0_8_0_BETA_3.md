# v0.8.0-beta.3 — Token Intelligence and Local Reasoning Proof

## Summary

v0.8.0-beta.3 introduces Orchgentic's Token Intelligence layer: a cost-aware observability system that shows when Orchgentic avoided external LLM calls, routed work locally or deterministically, and produced estimated token-savings evidence.

This release turns observability into an optimization map. The dashboard and CLI now show not only where external tokens were used, but also which orchestration decisions were already avoided and which remaining external LLM calls are candidates for local LLM offload.

## Highlights

- Added `orch token-report`
- Added Token Intelligence dashboard section
- Added token-scoped Run ID modal
- Added local/deterministic share vs external LLM share metrics
- Added token work total metric
- Added estimated token savings proof rows
- Added local LLM candidate token classification
- Added premium/external candidate token classification
- Added deterministic team role routing
- Added deterministic Researcher routing
- Added deterministic Writer, Reviewer, and Synthesis tool-decision bypasses
- Added human-readable token work reasons
- Added filtered Token Intelligence dashboard recalculation
- Reordered dashboard sections:
  1. Recent Failures
  2. Recent Runs
  3. Token Intelligence
- Added collapsible dashboard panels
- Improved Token Intelligence table readability by moving Reason text into a dedicated follow-up row
- Updated dashboard title from `RUN DASHBOARD` to `DASHBOARD`
- Added token-report filters and JSON output improvements

## Why This Matters

Most agent orchestration platforms can coordinate agents. Orchgentic now shows which orchestration decisions should not have required an external LLM in the first place.

This release demonstrates that Orchgentic can:

- avoid external LLM calls for basic team role routing
- avoid external LLM calls for repetitive tool-decision steps
- identify local LLM offload candidates
- keep premium/external LLM usage focused on high-value generation and synthesis
- show proof in the dashboard and trace events

## Token Intelligence Metrics

Token Intelligence now reports:

- local/deterministic share
- external LLM share
- token work total
- direct bypasses
- deterministic routes
- local reasoning events
- LLM events
- estimated tokens saved
- local LLM candidate tokens
- premium candidate tokens
- top savings run
- token proof events

## Execution Tiers

Token proof events can now classify work as:

- `deterministic_saved`
- `local_llm_candidate`
- `premium_external_candidate`
- `external_llm`
- `proof_context`

## Optimization Labels

Token proof events can now identify whether work was:

- already avoided externally
- eligible to move to a local LLM
- worth keeping external or configurable
- proof/context only

## Dashboard Improvements

The dashboard now prioritizes operational triage:

1. Recent Failures
2. Recent Runs
3. Token Intelligence

Each major panel is collapsible.

Dashboard filters now affect Token Intelligence, so filtering by team, agent, status, type, or search text recalculates the token metrics and proof rows from the same filtered run set.

## Validation

Recommended validation:

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q

orch run-team contentteam --debug
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

Final cleanup before release:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```
