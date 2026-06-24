# Troubleshooting

## `Unsupported provider`

Check your agent YAML:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Supported provider types in v0.9.0-rc.1 stabilization checks:

- `groq`
- `openai`
- `lmstudio`
- `lm_studio`

## `Provider model is required`

Add a model:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

## LM Studio says no models are loaded

Open LM Studio and load a model before running the agent. For LM Studio, ensure your provider config includes the expected local base URL when needed.

## Memory DB path missing

Local/SQLite memory requires:

```yaml
memory:
  enabled: true
  store: sqlite
  db_path: memory/agent_core.db
```

## Knowledge DB path missing

Local knowledge requires:

```yaml
knowledge:
  enabled: true
  store: local
  db_path: memory/knowledge.db
```

## Invalid `top_k`

`top_k` must be an integer greater than zero.

```yaml
knowledge:
  top_k: 5
```

## Gmail tools require auth

Gmail tools require a configured Gmail connection. Sending or deleting email should require explicit confirmation.

## Workflow doctor fails

Check:

- required workflow fields
- duplicate step IDs
- unsupported trigger type
- unsupported step type
- missing agent/team/tool reference
- invalid output reference

## `judge-route` selected a destructive tool

`judge-route` is analysis only. It should not execute destructive actions. Use execution commands with explicit confirmation where required.

## Windows path issues

Prefer relative project paths in YAML, such as:

```yaml
memory:
  db_path: memory/agent_core.db
```

Avoid hardcoding machine-specific absolute paths in committed examples.
