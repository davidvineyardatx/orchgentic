# Orchgentic v0.7.7-alpha — Gmail Connector + Tool Governance Foundation

This cumulative release adds the first governed real-world connector to Orchgentic.

## Added

- Named Gmail connections
- `orch connect gmail`
- `orch gmail list`
- `orch gmail status`
- `orch gmail disconnect`
- `gmail.search`
- `gmail.read`
- `gmail.draft`
- Generic `orch tool run --arg key=value` support
- Tool policy governance foundation
- Gmail send policy schema for future send/reply/delete support
- Google Gmail API dependencies
- Groq dependency confirmation

## Validated

The following flows were validated:

```bash
orch connect gmail --name assistant --credentials gmail-assistant.json
orch tool run gmail.search --agent Bob --arg query="newer_than:7d"
orch tool run gmail.read --agent Bob --arg message_id=MESSAGE_ID
orch tool run gmail.draft --agent Bob --arg to=studio@davidvineyard.com --arg subject="Orchgentic Gmail Test" --arg body="This is a test draft from Orchgentic."
```

## Deferred

The following Gmail actions are intentionally deferred until stronger confirmation and governance flows are implemented:

- `gmail.send`
- `gmail.reply`
- `gmail.delete`

## Strategic Direction

This release moves Orchgentic toward governed operational AI runtime behavior: agents can interact with real systems, but within named connections, scoped permissions, and runtime policy boundaries.
