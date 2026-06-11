# Orchgentic v0.7.10.1-alpha — Dynamic Telemetry + Route Metrics

This release refines deterministic routing telemetry without changing routing, Gmail, or agent execution behavior.

## Added

- dynamic token-savings estimation
- normalized route telemetry schema
- execution timing in milliseconds
- route metrics aggregation
- lightweight `orch route-metrics` command
- token-estimation config section

## Changed

The placeholder value `estimated_external_tokens_saved: 1500` has been replaced with dynamic estimation based on agent instructions, tool context, user task, and expected completion budget.

## Logs

- route events: `logs/routes.jsonl`
- aggregate metrics: `logs/route_metrics.json`

## Validate

```bash
orch run Bob --debug
# Task: what time is it

orch route-metrics
```
