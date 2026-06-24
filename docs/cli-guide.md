# Orchgentic CLI Guide

This guide lists the expected v0.9.0-rc.1 CLI surface.

## Project

```bash
orch init
```

Creates a new Orchgentic project structure.

## Agents

```bash
orch create-agent Bob
orch list-agents
orch run Bob "What time is it locally?"
orch run Bob "Write a short summary of Orchgentic." --debug
```

## Teams

```bash
orch run-team ContentTeam "Create a useful content outline for Orchgentic workflows." --debug
```

## Tools

```bash
orch list-tools
orch tool run datetime.local --agent Bob
orch tool run gmail.send --agent Bob --arg to=someone@example.com --arg subject="Test" --arg body="Hello" --arg confirm=true
```

Destructive or externally mutating tools should require explicit confirmation.

## Reasoning

```bash
orch judge-route "what time is it locally?" --agent Bob
orch judge-route "send an email to David" --agent Bob
```

`judge-route` is analysis only. It should not execute destructive tools.

## Workflows

```bash
orch workflow list
orch workflow show daily-research-summary
orch workflow doctor examples/workflows/daily-research-summary.yaml
orch workflow run daily-research-summary --input topic="agentic orchestration"
orch workflow trace daily-research-summary --latest
```

## Doctor checks

If the beta.2 doctor command is wired into the root CLI:

```bash
orch doctor agent agents/bob.yaml
orch doctor agent agents/bob.yaml --json
```

## Release candidate expectation

Every command shown in this guide should either:

- work as written, or
- clearly state its prerequisite in the docs.
