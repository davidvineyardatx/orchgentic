# README Workflow Snippet

Add this section to README.md when ready.

## Workflow Blueprint

Orchgentic now includes its first token-aware workflow blueprint:

```text
workflows/content_intelligence_summary.workflow.yaml
```

This workflow captures the cost-aware team pattern proven in v0.8.0-beta.3:

- deterministic team role routing
- deterministic Researcher routing
- Writer and Reviewer tool-decision bypass
- local LLM candidate classification
- premium/configurable final synthesis
- Token Intelligence proof

Current runtime equivalent:

```bash
orch run-team contentteam --debug
orch token-report
orch dashboard --limit 500
orch dashboard --open
```
