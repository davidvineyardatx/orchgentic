# Tools and Policies

Tools let an agent interact with the outside world. Policies control whether sensitive tools are allowed, blocked, or held for confirmation.

## Tool categories

Common built-in tools include:

```text
filesystem.read
filesystem.write
web.request
datetime.now
datetime.local
memory.search
knowledge.search
gmail.search
gmail.read
gmail.draft
gmail.send
gmail.reply
gmail.delete
```

List tools available to an agent:

```bash
orch list-tools --agent Bob
```

Run a tool directly:

```bash
orch tool run datetime.local --agent Bob
```

## Tool arguments

You can pass arguments with repeated `--arg key=value` entries:

```bash
orch tool run filesystem.write \
  --agent Bob \
  --arg path=notes/hello.txt \
  --arg content="Hello from Orchgentic"
```

Or with a JSON object:

```bash
orch tool run filesystem.read \
  --agent Bob \
  --args '{"path":"notes/hello.txt"}'
```

## Gmail setup

Connect a Gmail account:

```bash
orch connect gmail --name assistant
```

Use a specific credentials file:

```bash
orch connect gmail --name assistant --credentials credentials.json
```

List Gmail connections:

```bash
orch gmail list
```

Check a connection:

```bash
orch gmail status --name assistant
```

Disconnect:

```bash
orch gmail disconnect --name assistant
```

In `bob.yaml`, map Bob to the named connection:

```yaml
gmail:
  connection: assistant
```

## Gmail policies

Sensitive Gmail tools should be controlled with policies.

Example:

```yaml
tool_policies:
  gmail.send:
    enabled: true
    require_confirmation: true
    send_policy:
      mode: restricted
      allowed_addresses:
        - studio@example.com
      allowed_domains: []
      require_confirmation: true

  gmail.reply:
    enabled: true
    require_confirmation: true

  gmail.delete:
    enabled: false
    require_confirmation: true
```

## Policy behavior rules

```text
enabled: false
→ always block
→ confirmation cannot override

enabled: true + require_confirmation: true
→ hold until confirmed

enabled: true + require_confirmation: true + confirmed
→ allow

enabled: true + require_confirmation: false
→ allow
```

## Previewing policy behavior

Use `judge-route` to inspect what Orchgentic would do.

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Expected behavior if `gmail.delete.enabled` is false:

```text
policy.action: block
external_llm_allowed: false
```

Send route preview:

```bash
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

Expected behavior if `gmail.send.require_confirmation` is true:

```text
policy.action: hold_for_confirmation
external_llm_allowed: false
```

## Confirmed direct send

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Hello from Bob" \
  --arg body="This email was sent by Orchgentic with confirmation." \
  --arg confirm=true
```

## Restricted send policy

This policy only allows exact addresses in `allowed_addresses`:

```yaml
send_policy:
  mode: restricted
  allowed_addresses:
    - studio@example.com
  allowed_domains: []
```

To allow an entire domain, add it to `allowed_domains` if supported by your current tool implementation:

```yaml
allowed_domains:
  - example.com
```

## Safety design

Policy checks happen before external LLM escalation when configured:

```yaml
routing:
  policy:
    block_disabled_tools_before_llm: true
    hold_confirmation_tools_before_llm: true
```

This prevents unnecessary provider calls for tasks that are already blocked or require confirmation.
