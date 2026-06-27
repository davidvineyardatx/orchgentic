# v1.1.2 Clean Install Check

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
pip install -e ".[dev]"
```

This installs the CLI/runtime and developer test dependencies. Use `pip install -e .` only when you do not plan to run the test suite.

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
orch run-team ContentTeam "Create a brief content outline for growing tomatoes in central texas." --debug
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

If pytest is missing, reinstall with the developer extra first:

```bash
python -m pip install -e ".[dev]"
```

Then run:

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
