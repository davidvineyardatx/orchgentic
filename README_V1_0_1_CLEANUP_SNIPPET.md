## v1.0.1 Cleanup

v1.0.1 removes release-only artifacts and local generated state so users get a clean repo after cloning.

Preview:

```bash
python scripts/cleanup_release_artifacts.py --dry-run
```

Apply:

```bash
python scripts/cleanup_release_artifacts.py
```

Validate:

```bash
python -m pytest -q
orch --help
orch init
```
