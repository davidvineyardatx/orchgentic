# Content Intelligence Summary Workflow

```text
workflows/content_intelligence_summary.workflow.yaml
```

## Purpose

The Content Intelligence Summary workflow is a token-aware research, drafting, review, and synthesis workflow.

It is designed to produce executive summaries while avoiding unnecessary external LLM calls for basic orchestration decisions.

## What It Proves

This workflow is intended to prove that Orchgentic can:

- assign known team roles without external LLM planning
- route Researcher behavior deterministically
- skip Writer and Reviewer tool-decision LLM calls
- classify Writer and Reviewer generation as local LLM candidates
- reserve final synthesis as premium/configurable external model work
- show all of this in Token Intelligence

## Execution Shape

```text
Manager
  deterministic team plan

Researcher
  deterministic research route
  research-oriented generation

Writer
  draft from handoff context

Reviewer
  review clarity, structure, completeness

Manager
  final synthesis
```

## Expected Token Intelligence Story

A successful run should show:

- deterministic savings for manager planning
- deterministic savings for researcher tool-decision
- deterministic savings for writer tool-decision
- deterministic savings for reviewer tool-decision
- deterministic savings for synthesis tool-decision
- local LLM candidate tokens for drafting/review work
- premium candidate tokens for final synthesis

## Current Command Flow

```bash
orch run-team contentteam --debug
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

## Workflow Status

This is currently a workflow blueprint.

It should become executable as part of the v0.9 workflow layer.
