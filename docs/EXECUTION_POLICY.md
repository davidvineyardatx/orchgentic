# Execution Policy

Execution policy defines how Orchgentic should think about deterministic work, local reasoning, local LLM candidates, external LLM calls, and premium-model work.

This is the policy foundation for runtime cost hardening.

## Principle

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether the provider should be used
```

Execution policy belongs to the second half of that rule.

It does not replace providers. It tells Orchgentic which execution tier should be preferred, allowed, recommended, or eventually blocked.

## Current Status

In `v0.8.0-beta.4-alpha.3`, execution policy is schema and helper foundation only.

It adds:

```text
execution_policy YAML schema
default execution policy config
normalization helpers
advisory purpose classification
tests
docs
```

It does **not** yet change routing behavior.

Policy-aware routing enforcement should come in the next patch.

## Default Policy

```yaml
execution_policy:
  enabled: true
  default_mode: external_llm_when_needed

  deterministic:
    enabled: true

  local_reasoning:
    enabled: true

  local_llm:
    enabled: false
    eligible_for:
      - classification
      - routing
      - summarization
      - review

  external_llm:
    enabled: true
    require_for:
      - complex_generation
      - high_uncertainty_reasoning

  premium_model:
    enabled: true
    require_for:
      - final_synthesis
      - executive_output
      - high_quality_final
```

## Agent Example

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  instructions: |
    You are Bob, a helpful AI assistant.

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  execution_policy:
    enabled: true
    default_mode: external_llm_when_needed

    deterministic:
      enabled: true

    local_reasoning:
      enabled: true

    local_llm:
      enabled: false
      eligible_for:
        - classification
        - routing
        - summarization
        - review

    external_llm:
      enabled: true
      require_for:
        - complex_generation
        - high_uncertainty_reasoning

    premium_model:
      enabled: true
      require_for:
        - final_synthesis
        - executive_output
        - high_quality_final
```

## Team Example

```yaml
team:
  id: contentteam
  name: ContentTeam
  orchestrator: Manager
  members:
    - Researcher
    - Writer
    - Reviewer

  execution_policy:
    enabled: true
    default_mode: external_llm_when_needed

    deterministic:
      enabled: true

    local_llm:
      enabled: false
      eligible_for:
        - routing
        - review
        - summarization

    premium_model:
      enabled: true
      require_for:
        - final_synthesis
        - executive_output
```

## Execution Buckets

### deterministic

Work that should not need an LLM.

Examples:

```text
direct tool routing
known team role assignment
simple time/date routing
known policy checks
```

### local_reasoning

Small local logic that can decide whether the task is simple, deterministic, or should escalate.

Examples:

```text
intent classification
confidence scoring
simple tool selection
safe local answer
```

### local_llm

Future local model candidates.

Examples:

```text
classification
routing
summarization
review
```

### external_llm

External LLM work that is allowed when needed.

Examples:

```text
complex_generation
high_uncertainty_reasoning
```

### premium_model

Work that should likely stay on a premium model or become explicitly configurable.

Examples:

```text
final_synthesis
executive_output
high_quality_final
```

## Design Rules

- Execution policy should be readable YAML.
- Defaults should be safe.
- Policy should not silently disable required quality work.
- Policy should not hide when external LLMs are used.
- Token Intelligence should show when policy influenced a decision.
- Provider selection and execution policy should remain separate.

## Planned Next Step

The next patch should apply this policy to routing decisions and traces.

Expected future trace language:

```text
policy.allowed
policy.blocked
policy.recommended_local_llm
policy.escalated_to_external_llm
policy.kept_premium
```

Expected future dashboard language:

```text
This was deterministic and avoided an LLM.
This could move to a local LLM.
This required an external LLM.
This should remain premium/configurable.
This was blocked by policy.
```

## Related Docs

- `CORE_YAML_CONTRACTS.md`
- `PROVIDERS.md`
- `ROUTING_AND_REASONING.md`
- `TOKEN_INTELLIGENCE.md`


## Policy-Aware Routing Decisions

In `v0.8.0-beta.4-alpha.4`, routing and traces become policy-aware in advisory mode.

Advisory mode means:

```text
policy is visible
policy is classified
policy is traced
policy does not yet block or force reroutes
```

New trace event:

```text
execution_policy.classified
```

The event includes:

```text
purpose
recommended_execution_tier
policy_action
reason
advisory
enforced
allowed
policy_source
```

Example policy actions:

```text
recommend_local_llm
keep_premium_or_configurable
allow_external_llm
use_default_mode
policy_disabled
```

This makes routing explain policy influence without changing provider behavior yet.


## Deterministic Policy Classification

In `v0.8.0-beta.4-alpha.5`, local and deterministic routes are classified more directly.

When a route is answered locally or by deterministic tool routing, the advisory policy output reports:

```text
recommended_execution_tier: deterministic_saved
policy_action: deterministic_allowed
```

This does not enforce policy. It makes the judgment output match the actual execution path more clearly.


## Safe Advisory Policy Enforcement

In `v0.8.0-beta.4-alpha.6`, execution policy begins safe enforcement for deterministic/local routes only.

This means:

```text
if the route already resolved locally
and the policy classified it as deterministic_allowed
then Orchgentic marks local execution as safely enforced
and external LLM usage remains disabled for that route
```

The policy decision includes:

```text
safe_enforcement:
  enforced: true
  scope: deterministic_local_only
  action: enforce_local_execution
  external_llm_allowed: false
```

All other execution-policy cases remain advisory:

```text
safe_enforcement:
  enforced: false
  scope: observe_only
  action: no_enforcement
```

This patch does not block tools, force reroutes, or change provider selection for generation, workflow, local-LLM, or premium-model candidates.


## Runtime Trace Coverage

In `v0.8.0-beta.4-alpha.7`, safe enforcement metadata is carried into runtime trace surfaces.

The same `safe_enforcement` object used by `judge-route` is now available in:

```text
agent execution policy trace events
deterministic route telemetry
team execution policy trace events
```

Deterministic/local routes can show:

```text
safe_enforcement:
  enforced: true
  scope: deterministic_local_only
  action: enforce_local_execution
  external_llm_allowed: false
```

Team/workflow routes and generation routes remain observe-only.


## Enforcement Summary

In `v0.8.0-beta.4-alpha.8`, execution-policy output includes an `enforcement_summary` block.

This avoids confusion between:

```text
execution_policy.enforced: false
safe_enforcement.enforced: true
```

The first value means full policy enforcement is not enabled yet. The second value means a narrow deterministic/local-only guardrail was safely applied.

For deterministic/local routes, the summary is:

```text
enforcement_summary:
  mode: safe_deterministic_only
  status: safely_enforced
  safe_enforcement_applied: true
  full_policy_enforced: false
```

For all other routes, the summary is:

```text
enforcement_summary:
  mode: observe_only
  status: advisory
  safe_enforcement_applied: false
  full_policy_enforced: false
```
