# Orchgentic v0.7.10-alpha Hotfix — Gmail Connection Precedence

This hotfix prevents LLM-generated Gmail connection arguments from overriding the agent's configured Gmail connection.

## Fixed

When an agent YAML contains:

```yaml
gmail:
  connection: assistant
```

Gmail tools now always use `assistant`, even if the LLM attempts to call a tool with:

```json
{"connection": "primary"}
```

or:

```json
{"connection": "default"}
```

## Connection Precedence

```text
1. Agent YAML gmail.connection
2. Explicit runtime/CLI connection argument
3. default
```

## Why This Matters

Gmail connection names are credential-routing configuration and should not be controlled by LLM-generated tool arguments.

This preserves governed runtime behavior and prevents hallucinated connection names such as `primary`, `default`, or `user` from overriding Bob's configured connection.

## Validate

```bash
orch connect gmail --name assistant
orch tool run gmail.read --agent Bob --arg message_id=19eada2f053bc231
orch run Bob --debug
```

Task:

```text
read Gmail message id 19eada2f053bc231
```

Expected: Gmail read succeeds using Bob's configured `assistant` connection.
