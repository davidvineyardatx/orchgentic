# Orchgentic v0.7.8-alpha — Governed Gmail Actions

This release adds governed Gmail send, reply, and delete/trash actions.

## Reconnect Required

v0.7.8 adds Gmail send and modify scopes, so reconnect existing Gmail accounts:

```bash
orch gmail disconnect --name assistant
orch connect gmail --name assistant --credentials gmail-assistant.json
```

## Agent YAML

```yaml
gmail:
  connection: assistant

tools:
  - gmail.search
  - gmail.read
  - gmail.draft
  - gmail.send
  - gmail.reply
  - gmail.delete

capabilities:
  - gmail.search
  - gmail.read
  - gmail.draft
  - gmail.send
  - gmail.reply
  - gmail.delete

tool_policies:
  gmail.send:
    enabled: true
    require_confirmation: true
    send_policy:
      mode: restricted
      allowed_addresses:
        - studio@davidvineyard.com
      allowed_domains: []
      require_confirmation: true

  gmail.reply:
    enabled: true
    require_confirmation: true

  gmail.delete:
    enabled: false
    require_confirmation: true
```

## Test Commands

```bash
orch tool run gmail.send --agent Bob --arg to=you@email.com --arg subject="Governed Send Test" --arg body="This is a governed send test from Orchgentic." --arg confirm=true
orch tool run gmail.reply --agent Bob --arg message_id=MESSAGE_ID --arg body="Thanks, I received this." --arg confirm=true
orch tool run gmail.delete --agent Bob --arg message_id=MESSAGE_ID --arg confirm=true
```

`gmail.delete` moves messages to Trash only. It does not permanently delete messages.
