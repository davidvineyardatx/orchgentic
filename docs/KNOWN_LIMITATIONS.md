# Known Limitations

This document describes known limitations in Orchgentic v0.7.12.

## Local LLM support is deferred

v0.7.12 includes local reasoning, but not a full local LLM provider workflow.

Local reasoning means Orchgentic can make deterministic routing decisions locally, such as routing a time question directly to `datetime.local`.

Local LLM support means running an actual local model through LM Studio, Ollama, llama.cpp, or another local runtime. That is planned for a later provider-focused release.

## Source labels are not source verification

Team outputs may preserve source labels such as:

```text
Source: Accenture
Source: McKinsey
Source: NRF
```

These are useful labels when produced by a team member, but they are not verified citations unless Orchgentic retrieved the source document or URL through a tool.

For public-facing research, users should verify statistics and sources before publishing.

## Human review is expected

Orchgentic can generate useful business drafts and summaries, but generated content should be reviewed by a human before external use.

Human review is especially important for:

- public marketing content
- legal, medical, financial, or compliance-related content
- sales outreach
- customer communications
- research that includes statistics or source claims

## Gmail tools require local credentials

Gmail tools require OAuth setup and a named connection.

Example:

```bash
orch connect gmail --name assistant
```

Agents must reference the connection:

```yaml
gmail:
  connection: assistant
```

## Disabled tools cannot be confirmed

Confirmation can approve enabled-but-sensitive tools. It cannot override disabled tools.

```yaml
gmail.delete:
  enabled: false
  require_confirmation: true
```

This remains blocked even if confirmation is provided.

## `judge-route` does not execute

`judge-route` previews routing and policy decisions only.

It does not:

- call tools
- send emails
- delete emails
- run workflows
- execute a team

Use `orch run`, `orch tool run`, or `orch run-team` for execution.

## Capabilities and tools may currently duplicate entries

Some agent YAML files list the same items under both `capabilities` and `tools`.

This is acceptable in v0.7.12 if the runtime expects both. A future release may simplify this into one source of truth.
