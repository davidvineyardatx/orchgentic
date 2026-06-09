# Orchgentic v0.7.7-alpha — Gmail Connector + Tool Governance Foundation

This release adds named Gmail connections, safe Gmail tools, and generic CLI tool argument support.

## Validated Gmail Scope

The safe Gmail scope for this release is:

- `gmail.search`
- `gmail.read`
- `gmail.draft`

The following are intentionally deferred:

- `gmail.send`
- `gmail.reply`
- `gmail.delete`

## Named Gmail Connections

Orchgentic supports multiple named Gmail connections so different agents can use different inboxes.

Example:

```bash
orch connect gmail --name assistant --credentials D:/development/orchgentic-v0.7.7-alpha/gmail-assistant.json
```

Status:

```bash
orch gmail list
orch gmail status --name assistant
```

Disconnect:

```bash
orch gmail disconnect --name assistant
```

## Agent YAML

Add the Gmail connection and tools to the agent YAML:

```yaml
gmail:
  connection: assistant

capabilities:
  - gmail.search
  - gmail.read
  - gmail.draft

tools:
  - gmail.search
  - gmail.read
  - gmail.draft

tool_policies:
  gmail.search:
    enabled: true

  gmail.read:
    enabled: true

  gmail.draft:
    enabled: true

  gmail.send:
    enabled: false
    send_policy:
      mode: restricted
      allowed_addresses: []
      allowed_domains: []
      require_confirmation: true
```

## Tool Argument Syntax

`orch tool run` supports repeatable key/value arguments:

```bash
orch tool run TOOL_NAME --agent AgentName --arg key=value
```

## Tested Commands

Search Gmail:

```bash
orch tool run gmail.search --agent Bob --arg query="newer_than:7d"
```

Read a Gmail message:

```bash
orch tool run gmail.read --agent Bob --arg message_id=MESSAGE_ID
```

Create a Gmail draft:

```bash
orch tool run gmail.draft --agent Bob --arg to=studio@davidvineyard.com --arg subject="Orchgentic Gmail Test" --arg body="This is a test draft from Orchgentic."
```

## Demo Prompt

```text
Check unread emails from today.
Summarize anything important.
Draft replies where useful, but do not send anything.
```

## Governance Direction

This release establishes the foundation for governed operational tools.

Future releases can extend the same policy model to:

- Gmail send/reply/delete
- filesystem writes
- shell execution
- calendar actions
- CRM updates
- webhook posting
- database writes
