# Configuration Guide

## Agent YAML

Example:

```yaml
id: bob
name: Bob
role: General Assistant
instructions: >
  You are Bob, a helpful AI assistant. Use memory, knowledge, reasoning,
  and tools when relevant.

timezone: America/Chicago
locale: en-US

provider:
  type: groq
  model: llama-3.3-70b-versatile

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
  store: sqlite
  db_path: memory/agent_core.db

knowledge:
  enabled: true
  top_k: 5
  store: local
  db_path: memory/knowledge.db

tools:
  - datetime.now
  - datetime.local
  - filesystem.read
  - filesystem.write
  - memory.search
  - knowledge.search
```

## Provider

Supported provider types expected by the stabilization checks:

- `groq`
- `openai`
- `lmstudio`
- `lm_studio`

Provider config requires:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

## Memory

SQLite/local memory requires a `db_path`.

```yaml
memory:
  enabled: true
  store: sqlite
  db_path: memory/agent_core.db
  recent_messages: 10
```

Disabled memory is allowed:

```yaml
memory:
  enabled: false
```

## Knowledge / RAG

Local knowledge requires a `db_path`.

```yaml
knowledge:
  enabled: true
  store: local
  db_path: memory/knowledge.db
  top_k: 5
```

`top_k` must be greater than zero.

## Team YAML

Example:

```yaml
id: contentteam
name: ContentTeam
description: Team for content strategy and writing.
agents:
  - Bob
```

## Workflow YAML

Example:

```yaml
id: daily-research-summary
name: Daily Research Summary
version: 0.9.0-beta.1

trigger:
  type: manual

runtime:
  mode: sequential
  max_steps: 4
  timeout_seconds: 180
  save_trace: true
  fail_fast: true

inputs:
  topic:
    type: string
    required: true

steps:
  - id: search_knowledge
    type: tool
    tool: knowledge.search
    with:
      query: "{{ inputs.topic }}"
      top_k: 5

  - id: summarize
    type: agent
    agent: Bob
    prompt: >
      Write a clear summary for {{ inputs.topic }}.

outputs:
  final:
    from: summarize.response
```
