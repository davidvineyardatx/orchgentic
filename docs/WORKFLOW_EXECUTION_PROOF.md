# Workflow Execution Proof

Orchgentic supports the `workflow` CLI namespace for loading, validating, inspecting, and running workflow blueprints from the `workflows/` folder.

## Commands

```bash
orch workflow list
orch workflow inspect content_intelligence_summary
orch workflow validate content_intelligence_summary
orch workflow run content_intelligence_summary --task "Research water table level in Cedar Creek, TX and provide an executive summary." --debug
```

## What This Proves

A workflow run records explicit workflow metadata in observability:

```text
workflow_id: content_intelligence_summary
workflow_name: Content Intelligence Summary
workflow_version: 0.1.0
workflow_step: deterministic_team_plan
workflow_step: research_route
workflow_step: research_findings
workflow_step: draft_summary
workflow_step: review_summary
workflow_step: final_synthesis
```

This separates two states clearly:

```text
ContentTeam run
  The team executed directly.

Workflow run
  The workflow blueprint was loaded, mapped to ContentTeam, executed, and traced.
```

## Runtime Equivalent

The workflow currently maps to `ContentTeam`, so the team execution behavior remains the same. The difference is observability proof: `orch run-info <run_id>` now shows the workflow metadata and `workflow.step.planned` trace events.

## Recommended Validation

```bash
orch workflow validate content_intelligence_summary
orch workflow inspect content_intelligence_summary
orch workflow run content_intelligence_summary --task "Research water table level in Cedar Creek, TX and provide an executive summary." --debug
orch runs --type workflow
orch run-info <workflow_run_id>
orch token-report --type workflow
orch dashboard --limit 500
```
