# Examples Index

## Agents

Recommended examples:

- `agents/bob.yaml`
- General assistant with provider, memory, knowledge, tools, and reasoning enabled.

## Teams

Recommended examples:

- `teams/contentteam.yaml`
- Content specialist team using existing configured agents.

## Workflows

Recommended examples:

- `examples/workflows/daily-research-summary.yaml`
- `examples/workflows/content-team-outline.yaml`
- `examples/workflows/gmail-draft-review.yaml`
- `examples/workflows/heartbeat-status-check.yaml`
- `examples/workflows/webhook-content-request.yaml`

## Knowledge

Recommended commands:

```bash
orch knowledge ingest <path>
orch knowledge search "agentic orchestration"
```

## Memory

Recommended commands:

```bash
orch memory search "previous discussion"
```

## Reasoning

Recommended commands:

```bash
orch judge-route "what time is it locally?" --agent Bob
orch judge-route "send an email to David" --agent Bob
```

## Release candidate rule

Every example should either:

- run directly from a clean install, or
- clearly state its prerequisites.
