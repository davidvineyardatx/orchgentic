# Routing and Reasoning

Orchgentic v0.7.12 adds routing and reasoning layers that decide how a task should be handled before execution.

## Core flow

```text
User task
→ deterministic local route check
→ local reasoner / confidence scoring
→ workflow router
→ event context router
→ policy router
→ tool execution or LLM escalation
→ final answer
```

## Local reasoning

The local reasoner looks for tasks that do not need an external LLM.

Example:

```bash
orch run Bob --debug
```

Task:

```text
what is the local time?
```

Expected route:

```text
selected_tool: datetime.local
external_llm_used: false
reasoning_level: local_tool
```

This saves latency and tokens by avoiding an unnecessary model call.

## Confidence scoring

Reasoning confidence controls escalation.

Example config:

```yaml
reasoning:
  local_reasoner: true
  confidence_scoring: true
  confidence_high_threshold: 0.78
  confidence_low_threshold: 0.52
  escalation:
    enabled: true
    min_confidence: 0.52
```

If the task is simple and high-confidence, Orchgentic can use a deterministic route or tool.

If confidence is low or the task requires generation, Orchgentic escalates to the configured provider.

## Escalation

Escalation does not choose a separate fallback provider. The agent provider is configured once:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Escalation decides whether this provider should be used.

## Workflow-aware routing

Workflow routing identifies whether a task is likely to be:

- single-step
- multi-step
- tool-driven
- workflow-driven
- team-oriented
- generation-heavy

Example:

```bash
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

Expected workflow judgment:

```text
workflow_type: single_step
required_tools: ['gmail.send']
```

## Event-aware routing

Event context affects safety expectations.

Manual tasks are interactive:

```bash
orch judge-route "send a report email" --agent Bob --event-type manual
```

Webhook or heartbeat tasks may need stricter policy checks:

```bash
orch judge-route "send a report email" --agent Bob --event-type webhook
```

Config:

```yaml
routing:
  event:
    enabled: true
    autonomous_events_require_policy_checks: true
```

## Policy-aware routing

Policy routing can block or hold a task before tool execution or LLM escalation.

Example disabled tool:

```yaml
gmail.delete:
  enabled: false
  require_confirmation: true
```

Route:

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Expected result:

```text
policy.action: block
escalation.escalate: false
external_llm_allowed: false
```

Example confirmation hold:

```yaml
gmail.send:
  enabled: true
  require_confirmation: true
```

Route:

```bash
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

Expected result:

```text
policy.action: hold_for_confirmation
escalation.escalate: false
external_llm_allowed: false
```

## Intent precedence

Action verbs win over object nouns.

Example:

```text
delete gmail message id abcdef123456
```

Correct interpretation:

```text
intent: gmail_delete
required_tools: ['gmail.delete']
```

Even though the phrase contains `message id`, the destructive verb `delete` controls the intent.

## Debug output

Use `--debug` to inspect decisions:

```bash
orch run Bob --debug
```

Debug output may include:

- deterministic routing telemetry
- orchestration judgment
- workflow decision
- event context
- policy action
- escalation decision
- tool calls
- final answer

## Route metrics

Show aggregated routing metrics:

```bash
orch route-metrics
```

Useful for understanding LLM avoidance, local routes, and token savings.


## Execution Policy Awareness

Routing judgments include an advisory `execution_policy` section.

Example:

```text
execution_policy:
  purpose: routing
  recommended_execution_tier: local_llm_candidate
  policy_action: recommend_local_llm
  advisory: true
  enforced: false
```

This is intentionally advisory in alpha.4.

It helps developers see how policy would classify a decision without changing runtime behavior yet.


## Judgment Output Polish

The internal orchestration judgment keeps the full workflow router object for traces and tests.

For CLI display, single-agent routes can show workflow as not applicable:

```text
workflow:
  applicable: false
  reason: Not applicable for single-agent routing.
  workflow_type: null
```

This avoids implying that a workflow was meaningfully considered for simple single-agent jobs.
