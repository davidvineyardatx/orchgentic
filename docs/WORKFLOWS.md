# Workflows

Orchgentic workflows are declarative execution contracts that describe how agents, teams, tools, routing, policy, observability, and token intelligence should work together.

In v0.8.x, workflows are introduced as visible YAML blueprints. They are intended to make execution policy and cost-control behavior explicit before the full v0.9 workflow runtime is stabilized.

## Minimal workflow YAML

Since workflows are team-backed, the bare minimum should be:
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

## Why Workflows Matter

A workflow gives Orchgentic a clear contract for:

- which team should run
- what each role is responsible for
- which steps are deterministic
- which steps are local LLM candidates
- which steps should remain external or premium-model eligible
- which tool decisions should be skipped
- which proof events should be recorded
- how Token Intelligence should classify usage and savings

## First Workflow Blueprint

The first workflow blueprint is:

```text
workflows/content_intelligence_summary.workflow.yaml
```

It captures the pattern proven in v0.8.0-beta.3:

```text
deterministic team role routing
deterministic researcher routing
Writer and Reviewer tool-decision bypass
local LLM candidate classification
premium/configurable final synthesis
Token Intelligence proof
```

## Current Runtime Equivalent

Until full workflow execution lands, this workflow can be approximated with:

```bash
orch run-team contentteam --debug
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

## Design Principle

```text
Use deterministic routing first.
Use local reasoning second.
Use local LLMs for low-risk planning and classification.
Use external LLMs only when quality, complexity, or uncertainty requires escalation.
```

## Planned Direction

The v0.9 workflow layer should make workflow YAML executable and should preserve the Token Intelligence fields introduced in v0.8.0-beta.3:

- execution tier
- optimization opportunity
- token work reason
- local/deterministic share
- external LLM share
- local LLM candidate tokens
- premium candidate tokens
- estimated tokens saved
