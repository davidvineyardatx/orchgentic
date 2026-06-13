# Examples

These examples are designed to show how Orchgentic behaves in real use.

## Example 1: Local time without LLM

Run Bob:

```bash
orch run Bob --debug
```

Task:

```text
what is the local time?
```

Expected behavior:

```text
selected_tool: datetime.local
external_llm_used: false
reasoning_level: local_tool
```

Why it matters:

Orchgentic should not spend tokens on an external LLM when a deterministic tool can safely answer the task.

## Example 2: Preview a blocked Gmail delete

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

With this policy:

```yaml
gmail.delete:
  enabled: false
  require_confirmation: true
```

Expected result:

```text
intent: gmail_delete
required_tools: ['gmail.delete']
policy.action: block
escalation.escalate: false
external_llm_allowed: false
```

Why it matters:

Disabled tools remain blocked. Confirmation cannot override `enabled: false`.

## Example 3: Preview a confirmation-required Gmail send

```bash
orch judge-route "send an email to studio@example.com saying hello" --agent Bob
```

With this policy:

```yaml
gmail.send:
  enabled: true
  require_confirmation: true
```

Expected result:

```text
intent: gmail_send
required_tools: ['gmail.send']
policy.action: hold_for_confirmation
escalation.escalate: false
external_llm_allowed: false
```

Why it matters:

Orchgentic should not call a provider or execute a sensitive tool when the task requires confirmation.

## Example 4: Send email with direct tool confirmation

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Saying Hello" \
  --arg body="Hello. This message was sent by Orchgentic with confirmation." \
  --arg confirm=true
```

Expected result:

```text
ToolResult(success=True, tool_name='gmail.send', data={...}, error=None)
```

Why it matters:

Confirmed direct tool execution is explicit and auditable.

## Example 5: Run ContentTeam

```bash
orch run-team contentteam --debug
```

Task:

```text
Research AI is changing how customers shop and create an Executive Summary
```

Expected behavior:

```text
TEAM FINAL
<polished final response>

TEAM OUTPUTS
Manager -> concise assignment
Researcher -> research findings
Writer -> draft
Reviewer -> review feedback
```

Why it matters:

Team handoffs are compressed in v0.7.12. Orchgentic passes useful answer content forward instead of nested debug transcripts, reducing token usage and improving synthesis quality.

## Example 6: Ingest and search knowledge

Create a file:

```text
knowledge/orchgentic_overview.txt
```

Add content:

```text
Orchgentic is an open-source agent orchestration framework for routing, coordinating, and observing AI agents.
```

Ingest it:

```bash
orch knowledge ingest knowledge/orchgentic_overview.txt --agent Bob
```

Search it:

```bash
orch knowledge search "What is Orchgentic?" --agent Bob
```

Why it matters:

Knowledge gives agents access to durable project or domain information.

## Example 7: Search memory

```bash
orch memory search "AI shopping" --agent Bob
```

Why it matters:

Memory can help an agent recall prior interactions, but team synthesis in v0.7.12 avoids unrelated prior memory by default to reduce contamination.
