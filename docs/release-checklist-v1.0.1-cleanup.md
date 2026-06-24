# v1.0.1 Cleanup Release Checklist

## Scope

- [ ] No new runtime features.
- [ ] No workflow expansion.
- [ ] No provider changes.
- [ ] No RAG architecture changes.
- [ ] Cleanup-only release.

## Cleanup

Preview:

```bash
python scripts/cleanup_release_artifacts.py --dry-run
```

Apply:

```bash
python scripts/cleanup_release_artifacts.py
```

Or keep release notes/changelogs:

```bash
python scripts/cleanup_release_artifacts.py --keep-release-notes
```

## Confirm clean directories

```text
memory/.gitkeep
knowledge/.gitkeep
```

## Confirm ignored runtime state

`.gitignore` should include:

```text
memory/*
!memory/.gitkeep
knowledge/*
!knowledge/.gitkeep
```

## Validation

```bash
python -m pytest -q
orch --help
orch init
orch create-agent Bob
orch list-agents
orch list-tools
```

## Commit

```bash
git status
git add .
git commit -m "Release v1.0.1 cleanup"
git tag v1.0.1
git push origin main --tags
```
