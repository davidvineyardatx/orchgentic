# Core YAML Contracts

This document defines the minimum YAML needed to create functioning Orchgentic agents, teams, and workflows.

The goal is to make the open-source developer contract clear:

```text
What is the least YAML I need before Orchgentic can run?
```

Everything beyond these minimum fields should be treated as optional configuration or runtime policy.

## Design Principle

```text
Agents handle simple execution.
Teams coordinate specialists.
Workflows coordinate repeatable, team-backed business processes.
```

Simple one-agent or one-tool tasks should use agents and direct tools, not workflows.

Workflows are for coordinated, multi-step, team-backed execution.

---

## Minimal Agent YAML

A minimal agent needs:

- `id`
- `name`
- `role`
- `instructions`
- `provider.type`
- `provider.model`

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  instructions: |
    You are Bob, a helpful AI assistant.

  provider:
    type: groq
    model: llama-3.3-70b-versatile
```

Recommended starter fields:

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  description: General-purpose AI assistant.
  instructions: |
    You are Bob, a helpful AI assistant. Use memory, knowledge, reasoning, and tools when relevant.

  timezone: America/Chicago
  locale: en-US

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  capabilities:
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search

  tools:
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search
```

Create a starter agent:

```bash
orch create-agent Bob
```

---

## Minimal Team YAML

A minimal team needs:

- `id`
- `name`
- `orchestrator`
- `members`
- a task prompt/default task

```yaml
team:
  id: marketingteam
  name: MarketingTeam
  orchestrator: Manager

  members:
    - Researcher
    - Writer
    - Reviewer

  task: |
    Coordinate the team to complete the requested task.
```

Recommended starter team:

```yaml
team:
  id: marketingteam
  name: MarketingTeam
  description: MarketingTeam team created by Orchgentic.

  orchestrator: Manager

  members:
    - Researcher
    - Writer
    - Reviewer

  shared_context: true
  max_rounds: 3

  task: |
    Coordinate the team to complete the requested task.
```

Create a starter team:

```bash
orch create-team MarketingTeam
```

Create with custom members:

```bash
orch create-team MarketingTeam --members Researcher,Writer,Reviewer
```

or:

```bash
orch create-team MarketingTeam --member Researcher --member Writer --member Reviewer
```

Run the team:

```bash
orch list-teams
orch inspect-team MarketingTeam
orch preflight-team MarketingTeam --task "Test this team setup"
orch run-team MarketingTeam --debug
```

---

## Minimal Workflow YAML

Workflows are team-backed.

A minimal workflow needs:

- `id`
- `name`
- `version`
- `team.id` or `team.name`
- at least one step

```yaml
workflow:
  id: content_summary
  name: Content Summary
  version: 0.1.0

  team:
    id: contentteam
    name: ContentTeam

  steps:
    - id: run_team
      name: Run team
      action: run_team
```

Recommended workflow fields:

```yaml
workflow:
  id: content_intelligence_summary
  name: Content Intelligence Summary
  version: 0.1.0
  status: blueprint
  description: >
    Token-aware research, drafting, review, and synthesis workflow.

  team:
    id: contentteam
    name: ContentTeam
    orchestrator: Manager
    members:
      - Researcher
      - Writer
      - Reviewer

  execution_policy:
    default_mode: external_llm_when_needed

  steps:
    - id: deterministic_team_plan
      name: Deterministic team plan
      actor: Manager
      execution_tier: deterministic
      action: assign_roles_from_team_config

    - id: final_synthesis
      name: Final synthesis
      actor: Manager
      execution_tier: premium_external_candidate
      action: synthesize_final_response
```

Run a workflow:

```bash
orch workflow run content_intelligence_summary --task "Research a topic and produce an executive summary." --debug
```

---

## Provider YAML Examples

OpenAI:

```yaml
provider:
  type: openai
  model: gpt-4.1-mini
```

xAI:

```yaml
provider:
  type: xai
  model: grok-3-mini
```

Anthropic Claude:

```yaml
provider:
  type: anthropic
  model: claude-3-5-sonnet-latest
```

Groq:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

LM Studio:

```yaml
provider:
  type: lmstudio
  model: qwen3
```

Generic OpenAI-compatible provider:

```yaml
provider:
  type: openai-compatible
  model: your-model-name
```

See `PROVIDERS.md` for environment variables and onboarding details.

## Validation Expectations

A valid core YAML file should be:

```text
readable
minimal
safe by default
easy to extend
clear about what executes
```

## Related Docs

- `AGENT_CONFIGURATION.md`
- `TEAM_CONFIGURATION.md`
- `WORKFLOWS.md`
- `PROVIDERS.md`
- `TOOLS_AND_POLICIES.md`
- `CLI_COMMANDS.md`
