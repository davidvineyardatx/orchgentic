# Agent Configuration

Agents are configured with YAML files in the `agents/` folder. Each file describes the agent's identity, provider, tools, policies, routing behavior, reasoning settings, memory, and knowledge configuration.

The example below is a full `agents/bob.yaml` for v0.7.12.

## Full `bob.yaml`

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  description: Local development assistant.
  instructions: |
    You are Bob, a helpful AI assistant. Use memory, knowledge, reasoning, and tools when relevant.
  timezone: America/Chicago
  locale: en-US

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  capabilities:
    - filesystem.read
    - filesystem.write
    - web.request
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search
    - gmail.search
    - gmail.read
    - gmail.draft
    - gmail.send
    - gmail.reply
    - gmail.delete

  tools:
    - datetime.now
    - datetime.local
    - filesystem.read
    - filesystem.write
    - web.request
    - memory.search
    - knowledge.search
    - gmail.search
    - gmail.read
    - gmail.draft
    - gmail.send
    - gmail.reply
    - gmail.delete

  gmail:
    connection: assistant

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

  reasoning:
    planner: true
    reflection: true
    local_reasoner: true
    confidence_scoring: true
    confidence_high_threshold: 0.78
    confidence_low_threshold: 0.52
    escalation:
      enabled: true
      min_confidence: 0.52

  memory:
    enabled: true
    recent_messages: 10
    db_path: memory/orchgentic.db

  knowledge:
    enabled: true
    top_k: 5
    store: local
    db_path: memory/orchgentic.db
    collection: orchgentic_knowledge
```

Replace `studio@example.com` with an address you actually want to allow.

## Section-by-section walkthrough

### `agent`

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
```

The top-level `agent` block contains everything about the agent. The `id` is used internally. The `name` is how you usually refer to the agent from the CLI.

Example:

```bash
orch run Bob
```

### `description` and `instructions`

```yaml
description: Local development assistant.
instructions: |
  You are Bob, a helpful AI assistant. Use memory, knowledge, reasoning, and tools when relevant.
```

The description helps humans understand the agent. The instructions are passed to the model when an LLM call is needed.

Keep instructions clear and durable. Avoid provider-specific wording unless the agent is meant to be tied to one provider.

### `timezone` and `locale`

```yaml
timezone: America/Chicago
locale: en-US
```

These fields are used by time-aware tools and deterministic formatting.

For example, with `locale: en-US`, local time responses use 12-hour AM/PM formatting.

### `provider`

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

The provider is the configured LLM backend for the agent.

Important design rule:

```text
Define the provider once at the agent level.
```

Reasoning and routing decide whether this provider should be called. They do not define a second fallback provider.

### `capabilities` and `tools`

```yaml
capabilities:
  - datetime.local
  - memory.search
  - knowledge.search

tools:
  - datetime.local
  - memory.search
  - knowledge.search
```

`capabilities` describe what the agent is allowed to do. `tools` list concrete tools available at runtime.

In v0.7.12, both may appear. Keep them aligned so preflight and runtime behavior are consistent.

### `gmail`

```yaml
gmail:
  connection: assistant
```

This tells Gmail tools which named Gmail connection to use.

Create the connection with:

```bash
orch connect gmail --name assistant
```

### `tool_policies`

Tool policies define safety behavior for sensitive actions.

Example:

```yaml
gmail.send:
  enabled: true
  require_confirmation: true
```

This means `gmail.send` is allowed, but execution must include confirmation.

Disabled tools cannot be overridden by confirmation:

```yaml
gmail.delete:
  enabled: false
  require_confirmation: true
```

This means Gmail delete is blocked even if the user provides confirmation.

### `routing`

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

Routing controls how Orchgentic judges tasks before execution.

- `workflow.enabled`: enables workflow-aware routing.
- `event.enabled`: enables event-aware routing.
- `policy.enabled`: enables policy checks during routing.
- `block_disabled_tools_before_llm`: prevents LLM escalation when a disabled tool is required.
- `hold_confirmation_tools_before_llm`: prevents LLM escalation when a confirmation-required tool is detected but not confirmed.

### `reasoning`

```yaml
reasoning:
  planner: true
  reflection: true
  local_reasoner: true
  confidence_scoring: true
  confidence_high_threshold: 0.78
  confidence_low_threshold: 0.52
  escalation:
    enabled: true
    min_confidence: 0.52
```

Reasoning controls planning, reflection, local routing judgment, confidence scoring, and escalation.

Examples:

```text
what is the local time?
→ local deterministic route
→ no external LLM needed
```

```text
write an executive summary about AI shopping trends
→ generation task
→ escalates to configured provider
```

### `memory`

```yaml
memory:
  enabled: true
  recent_messages: 10
  db_path: memory/orchgentic.db
```

Memory stores recent interactions and episodes for later search or context.

Useful commands:

```bash
orch memory recent --agent Bob
orch memory search "AI shopping" --agent Bob
orch memory clear --agent Bob --yes
```

### `knowledge`

```yaml
knowledge:
  enabled: true
  top_k: 5
  store: local
  db_path: memory/orchgentic.db
  collection: orchgentic_knowledge
```

Knowledge stores searchable content ingested from files.

Useful commands:

```bash
orch knowledge ingest knowledge/example.txt --agent Bob
orch knowledge search "What is Orchgentic?" --agent Bob
orch knowledge list --agent Bob
```

## Common mistakes

### Incorrect indentation

This is wrong because `routing` is indented too far:

```yaml
   routing:
```

It should align under `agent` with `tool_policies`, `reasoning`, `memory`, and `knowledge`:

```yaml
  routing:
```

### Duplicate provider configuration

Do not define a provider inside escalation.

Use this:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile

reasoning:
  escalation:
    enabled: true
    min_confidence: 0.52
```

Do not use this:

```yaml
reasoning:
  escalation:
    fallback_provider:
      type: groq
      model: llama-3.3-70b-versatile
```

### Forgetting confirmation for Gmail send

If `gmail.send.require_confirmation` is `true`, direct tool calls must include:

```bash
--arg confirm=true
```

Example:

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Hello" \
  --arg body="Hello from Bob" \
  --arg confirm=true
```
