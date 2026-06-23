# Team Configuration

Teams are configured with YAML files in the `teams/` folder. A team defines an orchestrator, members, shared context behavior, and a default task prompt.

## Minimal team YAML
The bare minimum should be:
```yaml
team:
  id: marketingteam
  name: MarketingTeam
  orchestrator: Manager

  members:
    - Researcher
    - Writer
    - Reviewer

  task_prompt: |
    Produce a clear, useful response using the team's specialists.

Optional:

shared_context: true
max_rounds: 3
```

## Example `teams/contentteam.yaml`

```yaml
team:
  name: ContentTeam
  description: Research, write, and review content with specialist agents.
  orchestrator: Manager
  members:
    - Researcher
    - Writer
    - Reviewer
  shared_context: true
  max_rounds: 3
  task: |
    Produce a clear, useful content response using the team's specialists.
```

## How team execution works

A typical ContentTeam run follows this flow:

```text
User task
→ Manager decides team assignments
→ Researcher contributes findings
→ Writer drafts the requested output
→ Reviewer gives improvement feedback
→ Orchgentic synthesizes the final response
```

Run the team:

```bash
orch run-team contentteam
```

Run with debug output:

```bash
orch run-team contentteam --debug
```

Example task:

```text
Research AI is changing how customers shop and create an Executive Summary
```

## Team fields

### `name`

The team name used by the CLI.

```yaml
name: ContentTeam
```

You can usually call it case-insensitively:

```bash
orch run-team contentteam
```

### `description`

A human-readable description of the team.

```yaml
description: Research, write, and review content with specialist agents.
```

### `orchestrator`

The manager agent responsible for assigning work.

```yaml
orchestrator: Manager
```

The named agent must exist in `agents/manager.yaml`.

### `members`

The worker agents that contribute to the task.

```yaml
members:
  - Researcher
  - Writer
  - Reviewer
```

Each member should have a matching YAML file in `agents/`.

### `shared_context`

Controls whether each team member receives prior team outputs from the current run.

```yaml
shared_context: true
```

In v0.7.12, team handoffs are compressed. Instead of passing full debug transcripts, Orchgentic passes only the useful answer content from prior team members.

This reduces token usage and improves context quality.

### `max_rounds`

Maximum number of coordination rounds.

```yaml
max_rounds: 3
```

### `task`

The default prompt shown when running the team.

```yaml
task: |
  Produce a clear, useful content response using the team's specialists.
```

You can accept this default or type a custom task when prompted.

## Inspecting teams

List teams:

```bash
orch list-teams
```

Inspect a team:

```bash
orch inspect-team contentteam
```

Preflight a team task:

```bash
orch preflight-team contentteam --task "Research AI shopping trends and create an executive summary"
```

## Team output quality guardrails

v0.7.12 includes several team synthesis improvements:

- Current team outputs are the primary source of truth.
- Unrelated prior memory is not used by default for team synthesis.
- Team handoffs are compressed to reduce token usage.
- Structured JSON-style outputs are unwrapped before synthesis.
- Placeholder links, fake reports, fake webinars, and invented resources are suppressed.
- Source labels are preserved, but they are not treated as verified citations unless source URLs or retrieved documents exist.

## Human review recommendation

Team outputs are intended to be useful drafts. For business, marketing, legal, financial, or public-facing use, a human should review and adjust the final content before publication.
