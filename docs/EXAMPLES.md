# Orchgentic Examples

This document contains practical examples for using Orchgentic to build autonomous and multi-agent AI systems.

---

# Example 1 — Create an Agent

## Create a New Agent

```bash
orch create agent Bob
```

Expected result:

```text
Created agent:
agents/bob.yaml
```

---

## List Agents

```bash
orch list-agents
```

---

## Run an Agent

```bash
orch run Bob --debug
```

Example prompt:

```text
Summarize the latest trends in Product Marketing.
```

---

## Example Agent Configuration

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant

  timezone: America/Chicago
  locale: en-US

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  capabilities:
    - web.request
    - datetime.local
    - memory.search
    - knowledge.search

  tools:
    - web.request
    - datetime.local
    - memory.search
    - knowledge.search

  reasoning:
    planner: true
    reflection: true

  memory:
    enabled: true
```

---

# Example 2 — Create a Team

## Create a Team

```bash
orch create team ContentTeam
```

Expected result:

```text
Created team:
teams/contentteam.yaml
```

---

## List Teams

```bash
orch list-teams
```

---

## Run a Team

```bash
orch run-team ContentTeam --debug
```

---

## Example Team Architecture

```text
ManagerAgent
    ↓
ResearchAgent
    ↓
WriterAgent
    ↓
ReviewerAgent
    ↓
Final Output
```

---

## Example Use Case

Prompt:

```text
Create a technical blog post explaining autonomous AI orchestration platforms.
```

Expected orchestration behavior:
- ResearchAgent gathers information
- WriterAgent drafts content
- ReviewerAgent validates quality
- ManagerAgent assembles final output

---

# Example 3 — Tool Runtime

## Run a Tool Directly

```bash
orch tool run datetime.local --agent Bob
```

Expected output:

```text
timezone='America/Chicago'
weekday='Saturday'
time='08:48:28'
```

---

## Example Web Request

```text
Research the latest developments in Product Marketing automation.
```

The agent can dynamically invoke:

```text
web.request
```

during execution.

---

# Example 4 — Delegation

## Example Delegation Flow

```text
ManagerAgent
  └── delegates research to ResearchAgent
  └── delegates writing to WriterAgent
  └── delegates validation to ReviewerAgent
```

This allows:
- specialization
- parallel reasoning
- modular orchestration

---

# Example 5 — Memory Retrieval

## Search Memory

```bash
orch memory search "Product Marketing"
```

Agents can retrieve:
- prior conversations
- prior outputs
- runtime context
- execution history

---

# Example 6 — Semantic Knowledge

## Ingest Knowledge

```bash
orch knowledge ingest docs/
```

---

## Search Knowledge

```bash
orch knowledge search "product marketing trends"
```

Agents can use semantic retrieval during execution.

---

# Example 7 — Scheduled Autonomous Agent

## Heartbeat Trigger

```yaml
trigger:
  type: heartbeat
  interval_seconds: 3600
```

Example behavior:
- run every hour
- gather research
- generate summary
- store results in memory

---

# Example 8 — Webhook-Triggered Workflow

## Webhook Runtime

Example:
- external system sends webhook
- Orchgentic trigger receives event
- orchestration pipeline executes automatically

Example use cases:
- ticket triage
- incident response
- automated reporting
- content generation
- AI workflow automation

---

# Example 9 — Capability Preflight

Before execution, Orchgentic validates:
- required tools
- provider configuration
- team references
- orchestration dependencies

Example failure:

```text
ERROR: Agent requires tool 'web.request' but it is not configured.
```

This prevents:
- wasted LLM calls
- orchestration failures
- silent runtime degradation

---

# Example 10 — Timezone-Aware Runtime

## Example Agent Time Context

```yaml
timezone: America/Chicago
locale: en-US
```

## Example Tool

```bash
orch tool run datetime.local --agent Bob
```

Returns:
- localized time
- timezone
- weekday
- UTC offset

This enables:
- scheduled workflows
- region-aware orchestration
- cloud-safe execution

---

# Example 11 — Long-Running Research Workflow

## Example Scenario

Prompt:

```text
Research current Product Marketing strategies and create an executive summary.
```

Potential orchestration flow:

```text
ManagerAgent
    ↓
ResearchAgent
    ↓
Knowledge Retrieval
    ↓
WriterAgent
    ↓
ReviewerAgent
    ↓
Final Summary
```

Features involved:
- web research
- semantic retrieval
- memory
- delegation
- orchestration
- reflection

---

# Example 12 — Autonomous Reporting System

## Example Goal

Generate daily Product Marketing reports automatically.

Workflow:
1. heartbeat trigger fires
2. research agents gather data
3. writer agent summarizes findings
4. reviewer validates output
5. report stored to filesystem
6. future notification system distributes report

---

# Example 13 — Future Workflow DAG Engine

Planned future orchestration:

```text
START
  ↓
Research
  ↓
Branch:
  ├── Technical Summary
  ├── Executive Summary
  └── Social Content
  ↓
Review
  ↓
Publish
```

This will evolve into:
- visual workflows
- conditional routing
- retries
- persistent workflow state

---

# Recommended Demo Flow

For first-time users:

1. `orch init`
2. `orch create agent Bob`
3. `orch list-agents`
4. `orch run Bob --debug`
5. `orch tool run datetime.local --agent Bob`
6. `orch create team ContentTeam`
7. `orch list-teams`
8. `orch run-team ContentTeam --debug`

This demonstrates:
- runtime initialization
- agent creation
- team creation
- tool runtime
- provider integration
- orchestration
- delegation
- team execution

---

# Current Focus

The current Orchgentic release is focused on:

- runtime stabilization
- orchestration reliability
- provider resilience
- observability foundations
- operational maturity

Developer Preview:
`v0.7.5-alpha`
