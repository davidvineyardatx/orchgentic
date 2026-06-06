# v0.7.5 Time Context Resolver

This release fully adds timezone-aware local time support.

## Added

- `orchgentic/runtime/time_context.py`
- `orchgentic/tools/core/datetime_local.py`
- `datetime.local` registered in the tool registry
- `timezone` and `locale` fields on `AgentConfig`
- Provider prompt guidance to prefer `datetime.local` for user-facing time questions

## Runtime rule

- `datetime.now` returns UTC.
- `datetime.local` returns time resolved from Orchgentic time context.

## Timezone resolution order

1. `runtime_context.timezone`
2. `trigger.timezone`
3. `user.timezone`
4. `workspace.timezone`
5. `agent.timezone`
6. UTC fallback

## Agent YAML

```yaml
timezone: America/Chicago
locale: en-US

capabilities:
  - datetime.now
  - datetime.local

tools:
  - datetime.now
  - datetime.local
```

## Test

```bash
orch tool run datetime.local --agent Bob
orch run Bob --debug
```

Prompt:

```text
What time is it?
```
