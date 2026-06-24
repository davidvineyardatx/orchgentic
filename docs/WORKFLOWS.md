# Orchgentic Workflows

Workflows are declarative YAML definitions that coordinate agents, tools, triggers, routing rules, and trace behavior.

The goal of v0.9.0-beta.1 is to keep workflows simple enough for users to add by configuration, while still giving the runtime enough structure to validate, route, trace, and explain workflow execution.

## What a workflow does

A workflow answers four questions:

1. **When should this run?**
2. **Which agent or team should handle it?**
3. **Which steps should run, and in what order?**
4. **What should be recorded in the trace?**

Workflows are intentionally YAML-first. A user should not need to edit Python code to add a normal workflow.

## Basic shape

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

inputs:
  topic:
    type: string
    required: true
    description: Topic to research and summarize.

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
      Create a clear summary using the retrieved knowledge results.
      Topic: {{ inputs.topic }}

outputs:
  final:
    from: summarize.response
```

## Required fields

| Field | Required | Purpose |
| --- | --- | --- |
| `id` | Yes | Stable workflow identifier. Use lowercase kebab-case. |
| `name` | Yes | Human-readable workflow name. |
| `version` | Yes | Workflow contract or release version. |
| `trigger.type` | Yes | `manual`, `heartbeat`, or `webhook`. |
| `runtime.mode` | Yes | `sequential` in beta.1. |
| `steps` | Yes | Ordered list of workflow steps. |
| `outputs` | Recommended | Defines what result the user sees. |

## Step types

### Agent step

Use an agent step when the workflow needs reasoning, writing, summarization, planning, or tool-aware execution.

```yaml
- id: draft_response
  type: agent
  agent: Bob
  prompt: >
    Draft a concise response to this request:
    {{ inputs.request }}
```

### Team step

Use a team step when multiple specialists should contribute.

```yaml
- id: content_team_response
  type: team
  team: ContentTeam
  prompt: >
    Produce a useful content strategy response for:
    {{ inputs.topic }}
```

### Tool step

Use a tool step for deterministic tool execution.

```yaml
- id: local_time
  type: tool
  tool: datetime.local
  with:
    timezone: America/Chicago
```

### Conditional step

Use `when` to keep the workflow declarative while avoiding unnecessary work.

```yaml
- id: send_email
  type: tool
  tool: gmail.send
  when: "{{ inputs.confirm_send == true }}"
  with:
    to: "{{ inputs.to }}"
    subject: "{{ steps.draft.subject }}"
    body: "{{ steps.draft.body }}"
    confirm: true
```

## Trigger examples

### Manual

```yaml
trigger:
  type: manual
```

### Heartbeat

```yaml
trigger:
  type: heartbeat
  schedule:
    every: 1 day
```

### Webhook

```yaml
trigger:
  type: webhook
  path: /webhooks/content-request
  method: POST
```

## Runtime behavior

Beta.1 workflows should be predictable and easy to debug.

```yaml
runtime:
  mode: sequential
  max_steps: 6
  timeout_seconds: 240
  save_trace: true
  fail_fast: true
```

Recommended defaults:

- `mode: sequential`
- `save_trace: true`
- `fail_fast: true`
- Keep `max_steps` small until the workflow is proven stable.

## Trace consistency

A workflow trace should include:

- workflow id
- workflow version
- trigger type
- step id
- step type
- selected agent, team, or tool
- status
- start and end timestamps
- final output reference
- error classification when a step fails

This makes workflow runs inspectable and gives the doctor command enough information to explain failures.

## Design rule

For beta.1, users should only need to add workflow YAML to the workflow registry or workflow directory. The runtime should discover, validate, and expose the workflow without custom Python registration.
