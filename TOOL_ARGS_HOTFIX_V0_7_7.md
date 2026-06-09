# Orchgentic v0.7.7-alpha Tool Args Hotfix

Adds generic key/value argument support to `orch tool run`.

## New syntax

```bash
orch tool run TOOL_NAME --agent AgentName --arg key=value
```

Arguments can be repeated:

```bash
orch tool run gmail.search --agent Bob --arg query="newer_than:7d" --arg max_results=10
```

The existing JSON syntax still works:

```bash
orch tool run gmail.search --agent Bob --args '{"query":"newer_than:7d"}'
```

## Gmail examples

```bash
orch tool run gmail.search --agent Bob --arg query="newer_than:7d"
orch tool run gmail.read --agent Bob --arg message_id=MESSAGE_ID
orch tool run gmail.draft --agent Bob --arg to=test@example.com --arg subject="Test Draft" --arg body="Hello from Orchgentic."
```
