# Orchgentic CLI Command Sheet

## Core

```bash
orch --help
```

```bash
orch init
```

```bash
orch list-agents
```

```bash
orch list-tools
```

```bash
orch inspect-agent Bob
```

---

## Agents

```bash
orch create-agent Bob
```

```bash
orch run Bob
```

```bash
orch run Bob --debug
```

```bash
orch run Bob --show-plan
```

```bash
orch run Bob --no-reflection
```

```bash
orch run Bob --no-preflight
```

---

## Tools

```bash
orch tool run <tool_name>
```

```bash
orch tool run <tool_name> --agent Bob
```

```bash
orch tool run <tool_name> --agent Bob --arg key=value
```

Example:

```bash
orch tool run gmail.read --agent Bob --arg message_id=<MESSAGE_ID>
```

---

## Gmail

```bash
orch connect gmail --name assistant
```

```bash
orch connect gmail --name assistant --credentials D:/development/gmail-assistant.json
```

```bash
orch gmail list
```

```bash
orch gmail status
```

```bash
orch gmail status --name assistant
```

```bash
orch gmail disconnect --name assistant
```

---

## Gmail Tool Examples

```bash
orch tool run gmail.search --agent Bob --arg query="newer_than:7d"
```

```bash
orch tool run gmail.read --agent Bob --arg message_id=<MESSAGE_ID>
```

```bash
orch tool run gmail.draft --agent Bob --arg to=name@example.com --arg subject="Subject" --arg body="Message body"
```

```bash
orch tool run gmail.send --agent Bob --arg to=name@example.com --arg subject="Subject" --arg body="Message body" --arg confirm=true
```

```bash
orch tool run gmail.reply --agent Bob --arg message_id=<MESSAGE_ID> --arg body="Reply body" --arg confirm=true
```

```bash
orch tool run gmail.delete --agent Bob --arg message_id=<MESSAGE_ID> --arg confirm=true
```

---

## Gmail Natural Language Examples

```bash
orch run Bob --debug
```

Task:

```text
search Gmail "newer_than:7d"
```

Task:

```text
read Gmail message id <MESSAGE_ID>
```

Task:

```text
read Gmail message id <MESSAGE_ID> and summarize message
```

---

## Memory

```bash
orch memory search Bob "search term"
```

```bash
orch memory clear --agent Bob --yes
```

---

## Knowledge

```bash
orch knowledge ingest <path>
```

```bash
orch knowledge search "search term"
```

---

## Teams

```bash
orch run-team <TeamName>
```

```bash
orch run-team <TeamName> --debug
```

---

## Triggers

```bash
orch trigger run <trigger_id>
```

```bash
orch trigger run <trigger_id> --debug
```

---

## Route Telemetry

```bash
orch route-metrics
```

Route logs:

```text
logs/routes.jsonl
```

Route metrics:

```text
logs/route_metrics.json
```

---

## Deterministic Routing Test Commands

```bash
orch run Bob --debug
```

Task:

```text
what time is it
```

Expected:

```text
ROUTING
external_llm_used: False
selected_tool: datetime.local
```

```bash
orch run Bob --debug
```

Task:

```text
read Gmail message id <MESSAGE_ID>
```

Expected:

```text
ROUTING
external_llm_used: False
selected_tool: gmail.read
```

---

## Recommended Validation Checklist

```bash
orch inspect-agent Bob
```

```bash
orch connect gmail --name assistant
```

```bash
orch gmail list
```

```bash
orch tool run gmail.read --agent Bob --arg message_id=<MESSAGE_ID>
```

```bash
orch run Bob --debug
```

Task:

```text
read Gmail message id <MESSAGE_ID>
```

```bash
orch run Bob --debug
```

Task:

```text
read Gmail message id <MESSAGE_ID> and summarize message
```

```bash
orch run Bob --debug
```

Task:

```text
what time is it
```

```bash
orch route-metrics
```
