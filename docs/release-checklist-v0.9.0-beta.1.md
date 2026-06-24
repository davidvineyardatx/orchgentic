# v0.9.0-beta.1 Release Checklist

## Tests

```bash
python -m pytest -q
python -m pytest -q tests/test_workflow_examples_beta1.py
```

## Workflow doctor

```bash
orch workflow doctor examples/workflows/daily-research-summary.yaml
orch workflow doctor examples/workflows/content-team-outline.yaml
orch workflow doctor examples/workflows/gmail-draft-review.yaml
orch workflow doctor examples/workflows/heartbeat-status-check.yaml
orch workflow doctor examples/workflows/webhook-content-request.yaml
```

## CLI smoke tests

```bash
orch workflow list
orch workflow run daily-research-summary --input topic="Orchgentic workflows" --debug
orch workflow trace daily-research-summary --latest
```

## Docs

- [ ] README includes workflow snippet or link.
- [ ] `docs/workflows.md` explains the workflow shape.
- [ ] `docs/workflow-doctor.md` explains validation.
- [ ] `examples/workflows/` includes practical examples.
- [ ] Release notes are ready.

## Tag

```bash
git status
git add .
git commit -m "Release v0.9.0-beta.1 workflow beta"
git tag v0.9.0-beta.1
git push origin main --tags
```
