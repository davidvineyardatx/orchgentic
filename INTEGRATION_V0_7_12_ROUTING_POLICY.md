# Integration Notes — v0.7.12-alpha

## What Changed

The route judgment now returns these sections:

```text
local_reasoner
workflow
event_context
policy
escalation
final_decision
```

Example:

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Expected behavior when `gmail.delete` is disabled:

```text
final_decision.action = block
external_llm_allowed = false
```

## CLI Runtime Behavior

`orch run Bob --debug` now evaluates the full judgment path after deterministic routing and before the LLM provider call.

If the final decision is:

```text
block
hold_for_confirmation
```

Orchgentic prints the reason and stops before calling the provider.

## Event Context

Manual CLI runs use:

```text
event_type = manual
source = cli
```

The event router also supports:

```text
heartbeat
webhook
scheduled
unknown
```

Autonomous events require stricter policy checks for side-effecting tools such as:

```text
gmail.send
gmail.reply
gmail.delete
filesystem.write
```

## YAML

`routing:` is optional because defaults are provided through the schema. A full agent config can include:

```yaml
routing:
  workflow:
    enabled: true
    multi_step_threshold: 0.80
  event:
    enabled: true
    autonomous_events_require_policy_checks: true
  policy:
    enabled: true
    block_disabled_tools_before_llm: true
    hold_confirmation_tools_before_llm: true
```

Provider config remains only at the agent level.
