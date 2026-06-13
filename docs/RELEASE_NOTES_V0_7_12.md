# Orchgentic v0.7.12 Release Notes

Orchgentic v0.7.12 is a major stabilization release focused on routing, reasoning, policy, and team orchestration quality.

## What changed

### Workflow-aware routing

Orchgentic can now judge whether a task is single-step, multi-step, tool-driven, workflow-driven, team-oriented, or LLM-required.

### Event-aware routing

Routing can account for event context such as manual CLI runs, heartbeat triggers, webhook triggers, scheduled tasks, and autonomous execution.

### Policy-aware escalation

Policy checks now happen before provider escalation when configured. This means disabled or confirmation-required tools can block or hold execution before spending tokens on an external model.

### Intent precedence

Action verbs now take priority over object nouns.

Example:

```text
delete gmail message id abcdef123456
→ gmail.delete
```

This avoids misclassifying destructive actions as read operations simply because the phrase includes `message id`.

### Local reasoning and confidence scoring

The local reasoner can identify simple deterministic tasks and avoid unnecessary LLM calls.

Example:

```text
what is the local time?
→ datetime.local
→ external_llm_used: false
```

### Provider configuration cleanup

Agents define one provider at the agent level. Escalation decides whether to use that provider; it does not define a duplicate fallback provider.

### Gmail policy safety

Gmail tools now support safer policy behavior:

- block disabled tools
- hold confirmation-required actions
- restrict send recipients
- suppress LLM escalation when policy blocks or holds execution

### Team synthesis quality

Team orchestration now includes:

- current-run-only synthesis context
- reduced memory contamination
- compressed team handoffs
- placeholder resource suppression
- structured output unwrapping
- cleaner final team answers

### Token efficiency

Team handoffs no longer pass repeated nested `RUN ID`, `PLAN`, `ANSWER`, and `REFLECTION` blocks between agents. This reduces context bloat and can lower token usage for client workloads.

## Validation

The final v0.7.12 validation suite passed:

```text
53 passed
```

The exact test count may change as the project grows.

## Known limitations

- Local LLM provider work is deferred.
- Source labels in generated research outputs are not verified citations unless retrieved sources or URLs are provided.
- Human review is recommended before using generated content publicly or commercially.
- Gmail and other external tools require credentials and local setup.
