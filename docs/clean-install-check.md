# v0.9.0-rc.1 Clean Install Check

Use this checklist from a fresh clone.

## Environment

```bash
python --version
pip --version
```

Expected:

- Python 3.12 or newer

## Install

```bash
pip install -e .
```

## CLI

```bash
orch --help
orch init
orch list-tools
```

## Agent

```bash
orch create-agent Bob
orch list-agents
orch run Bob "What time is it locally?" --debug
```

## Team

If `ContentTeam` example exists:

```bash
orch run-team ContentTeam "Create a brief content outline for Orchgentic." --debug
```

## Workflows

```bash
orch workflow list
orch workflow doctor examples/workflows/daily-research-summary.yaml
```

## Stabilization checks

If wired:

```bash
orch doctor agent agents/bob.yaml
```

## Tests

```bash
python -m pytest -q
```

## Acceptance

- [ ] Install succeeds.
- [ ] CLI help works.
- [ ] Project init works.
- [ ] Agent creation works.
- [ ] Tool list works.
- [ ] Agent run works.
- [ ] Workflow list works.
- [ ] Workflow doctor works.
- [ ] Full tests pass.
- [ ] Docs match actual commands.
