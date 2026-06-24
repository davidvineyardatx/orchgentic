# v0.9.0-beta.2 Release Checklist

## Scope confirmation

- [ ] No workflow feature expansion.
- [ ] No new RAG architecture.
- [ ] No new provider families unless already supported.
- [ ] No hosted dashboard work.
- [ ] No no-code builder work.

## Tests

```bash
python -m pytest -q tests/test_stabilization_beta2_checks.py
python -m pytest -q tests/test_stabilization_beta2_doctor.py
python -m pytest -q tests/test_stabilization_beta2_runtime.py
python -m pytest -q tests/test_stabilization_beta2_runtime_regressions.py
python -m pytest -q
```

## Manual sanity checks

```bash
orch list-agents
orch list-tools
orch run Bob --debug
orch judge-route "what time is it locally?" --agent Bob
```

If the optional doctor command is wired into the root CLI:

```bash
orch doctor agent agents/bob.yaml
orch doctor agent agents/bob.yaml --json
```

## Expected result

- Existing provider config failures are clear.
- Existing memory config failures are clear.
- Existing knowledge/RAG config failures are clear.
- Disabled memory/knowledge produces warnings, not blocking errors.
- Runtime boundary fails before provider/memory/knowledge initialization when config is invalid.
- Full test suite passes.

## Tag

```bash
git status
git add .
git commit -m "Release v0.9.0-beta.2 stabilization"
git tag v0.9.0-beta.2
git push origin main --tags
```
