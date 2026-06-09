# Orchgentic

**Orchgentic is an open-source orchestration runtime for autonomous and multi-agent AI systems.**

Developer Preview: `v0.7.8-alpha`

Orchgentic helps developers configure and run AI agents with:

- YAML-first agent configuration
- provider abstraction
- tool runtime
- planning and reflection
- memory
- semantic knowledge
- triggers and webhooks
- multi-agent teams
- delegation
- timezone-aware runtime tools
- capability preflight checks
- CLI-first workflows

> Status: Developer Preview. Orchgentic is usable for experimentation, demos, and early developer feedback, but it is not yet a production-stable enterprise platform.

---

## Quickstart

```bash
pip install -e .
orch init
orch list-agents
orch list-tools --agent Bob
orch run Bob --debug
```

Test local time support:

```bash
orch tool run datetime.local --agent Bob
```

Run a team:

```bash
orch list-teams
orch run-team ContentTeam --debug
```

---

## Provider Setup

Create a `.env` file from `.env.example`.

### Groq

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Agent YAML:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

### OpenAI

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Agent YAML:

```yaml
provider:
  type: openai
  model: gpt-4o-mini
```

---

## Example agent timezone

```yaml
timezone: America/Chicago
locale: en-US

tools:
  - datetime.now
  - datetime.local
```

`datetime.now` returns UTC.  
`datetime.local` returns local time based on the resolved Orchgentic time context.

---

## Current limitations

- Developer preview quality
- No full DAG workflow engine yet
- Email/webhook notification providers are scaffolded but not fully implemented
- No hosted dashboard/UI yet
- No enterprise RBAC yet
- Provider API keys are required for hosted models

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).
