# Orchgentic Quickstart

This guide validates the v0.9.0-rc.1 developer experience from a clean install.

## Requirements

- Python 3.12 or newer
- Git
- A configured provider in `.env`, such as Groq, OpenAI, or LM Studio

## 1. Install

From the project root:

```bash
pip install -e .
```

## 2. Initialize a project

```bash
orch init
```

Expected result:

- project folders are created
- example config is available
- the `orch` CLI is available

## 3. Create an agent

```bash
orch create-agent Bob
```

Expected result:

- an agent YAML file is created
- Bob appears in the agent list

```bash
orch list-agents
```

## 4. Confirm tools

```bash
orch list-tools
```

Expected result:

- registered tools are listed
- built-in tools appear without manual Python registration

## 5. Run a basic agent task

```bash
orch run Bob "What time is it locally?" --debug
```

Expected result:

- deterministic/local routing should handle local time when configured
- debug output should show routing details
- no unnecessary provider call should be needed for deterministic local time tasks

## 6. Validate memory, knowledge, and provider config

If the optional beta.2 doctor command is wired into the root CLI:

```bash
orch doctor agent agents/bob.yaml
orch doctor agent agents/bob.yaml --json
```

Expected result:

- provider checks are clear
- memory checks are clear
- knowledge/RAG checks are clear
- warnings do not block execution unless they are errors

## 7. Validate workflows

```bash
orch workflow list
orch workflow doctor examples/workflows/daily-research-summary.yaml
```

Expected result:

- workflows are discoverable
- examples validate against the current workflow contract

## 8. Run tests

```bash
python -m pytest -q
```

Expected result:

- all tests pass

## Clean install acceptance standard

A new developer should be able to follow this guide without hidden setup beyond provider credentials and any optional tool-specific auth such as Gmail.
