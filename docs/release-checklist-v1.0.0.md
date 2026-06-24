# v1.0.0 Release Checklist

## Scope

- [ ] No new runtime features.
- [ ] No workflow expansion.
- [ ] No new RAG architecture.
- [ ] No new provider families.
- [ ] No hosted dashboard/no-code builder work.
- [ ] Release-only packaging and validation.

## Required validation

```bash
python -m pytest -q
```

## Clean install validation

Run from a fresh clone or clean workspace:

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

## Documentation validation

Confirm these docs exist and are current:

- [ ] `docs/quickstart.md`
- [ ] `docs/cli-guide.md`
- [ ] `docs/configuration-guide.md`
- [ ] `docs/troubleshooting.md`
- [ ] `docs/clean-install-check.md`
- [ ] `docs/examples-index.md`
- [ ] `docs/known-limitations.md`
- [ ] `RELEASE_NOTES_v1.0.0.md`
- [ ] `CHANGELOG_v1.0.0.md`

## User-facing naming

- [ ] Public CLI references use `orch`.
- [ ] Public product references use `Orchgentic`.
- [ ] Old `agent-core` wording is removed from user-facing commands unless strictly historical or internal.

## Release files

- [ ] `RELEASE_NOTES_v1.0.0.md`
- [ ] `CHANGELOG_v1.0.0.md`
- [ ] `README_V1_SNIPPET.md`
- [ ] `docs/release-checklist-v1.0.0.md`
- [ ] `manifest.json`

## Final commit and tag

```bash
git status
git add .
git commit -m "Release v1.0.0 stable developer release"
git tag v1.0.0
git push origin main --tags
```

## Acceptance

v1.0.0 is ready when:

- [ ] full tests pass
- [ ] clean install path works
- [ ] docs match actual commands
- [ ] examples are current
- [ ] release notes are complete
- [ ] known limitations are documented
- [ ] no scope creep was introduced
