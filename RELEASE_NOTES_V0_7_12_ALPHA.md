# Orchgentic v0.7.12-alpha — Workflow, Event, and Policy-Aware Routing

This release extends the v0.7.11 local reasoning layer with routing awareness that happens before provider escalation.

## Added

- Workflow-aware routing
  - Detects single-step tasks, tool-chain tasks, research+synthesis workflows, team/delegation signals, and manual-review signals.
  - Adds estimated steps, required tools, and workflow reasons to routing judgment.

- Event-aware routing
  - Adds explicit event context for manual, heartbeat, webhook, scheduled, and unknown runs.
  - Marks heartbeat/webhook/scheduled routes as autonomous so policy checks can be more conservative.

- Policy-aware escalation
  - Checks tool policies before sending policy-sensitive work to an LLM.
  - Blocks disabled tools before provider escalation.
  - Holds confirmation-required tools before provider escalation.
  - Applies Gmail send allow-list policy during routing judgment.

## Important Design Rule

The provider remains configured exactly once:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Routing, reasoning, and policy decide whether that provider should be used. They do not redefine a fallback provider.

## New Files

```text
orchgentic/core/routing/
├─ __init__.py
├─ routing_decision.py
├─ workflow_router.py
├─ event_context.py
└─ policy_router.py

orchgentic/config/routing_defaults.py
tests/test_routing_v0_7_12.py
```

## Updated Files

```text
orchgentic/runtime/router_judgment.py
orchgentic/cli.py
orchgentic/config/schemas.py
agents/bob.yaml
agents/sample_reasoning.yaml
```

## Validation

```bash
python -m pytest -q
```

Expected result from this package:

```text
34 passed
```
