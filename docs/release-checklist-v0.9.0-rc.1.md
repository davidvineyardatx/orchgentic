# v0.9.0-rc.1 Release Checklist

## Scope

- [ ] No new runtime features.
- [ ] No new workflow expansion.
- [ ] No new provider families.
- [ ] No new hosted dashboard/no-code builder work.
- [ ] Docs, examples, clean install, and release readiness only.

## Docs

- [ ] `docs/quickstart.md`
- [ ] `docs/cli-guide.md`
- [ ] `docs/configuration-guide.md`
- [ ] `docs/troubleshooting.md`
- [ ] `docs/clean-install-check.md`
- [ ] `docs/examples-index.md`
- [ ] `docs/known-limitations.md`

## Clean install

```bash
pip install -e .
orch --help
orch init
orch create-agent Bob
orch list-agents
orch list-tools
orch run Bob "What time is it locally?" --debug
orch workflow list
orch workflow doctor examples/workflows/daily-research-summary.yaml
python -m pytest -q
```

## Stabilization tests

```bash
python -m pytest -q tests/test_stabilization_beta2_checks.py
python -m pytest -q tests/test_stabilization_beta2_doctor.py
python -m pytest -q tests/test_stabilization_beta2_runtime.py
python -m pytest -q tests/test_stabilization_beta2_runtime_regressions.py
```

## Workflow example tests

```bash
python -m pytest -q tests/test_workflow_examples_beta1.py
```

## Final acceptance

- [ ] All tests pass.
- [ ] Clean install works.
- [ ] README points to the right docs.
- [ ] Examples are current.
- [ ] Release notes are complete.
- [ ] Known limitations are documented.
- [ ] Tag as `v0.9.0-rc.1`.

## Tag

```bash
git status
git add .
git commit -m "Release v0.9.0-rc.1"
git tag v0.9.0-rc.1
git push origin main --tags
```
