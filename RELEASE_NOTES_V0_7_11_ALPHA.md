# Orchgentic v0.7.11-alpha — Local Reasoning + Confidence + Escalation

This corrected package uses the current Orchgentic layout and places reasoning code under:

```text
orchgentic/core/reasoning/
```

## Added

- Local mini reasoner for deterministic preflight decisions.
- Confidence scorer with high/medium/low bands.
- Escalation policy that decides whether to use the agent's configured provider.
- Runtime hook: `preflight_reasoning(...)`.
- Agent schema fields for local reasoning and confidence scoring.

## Configuration rule

Provider/model are defined exactly once:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Escalation does not define a fallback provider. It only decides whether to call the configured provider:

```yaml
reasoning:
  planner: true
  reflection: true
  local_reasoner: true
  confidence_scoring: true
  confidence_high_threshold: 0.78
  confidence_low_threshold: 0.52
  escalation:
    enabled: true
    min_confidence: 0.52
```
