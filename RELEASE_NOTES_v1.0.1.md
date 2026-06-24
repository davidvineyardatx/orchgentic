# Orchgentic v1.0.1 Release Notes

## Focus

v1.0.1 is a cleanup release.

The goal is to make the repository cleaner for users who clone it after v1.0.0.

## Added

- Cleanup script for release-only artifacts and generated local state.
- `.gitignore` entries for local memory and knowledge runtime files.
- `.gitkeep` placeholders for clean `memory/` and `knowledge/` directories.
- Cleanup documentation and checklist.

## Removed by cleanup script

- Release-package-only tests:
  - `tests/test_rc1_docs_exist.py`
  - `tests/test_rc1_clean_install_commands_documented.py`
  - `tests/test_v1_release_docs.py`
- Local runtime state:
  - `memory/*`
  - `knowledge/*`
- Build/cache artifacts:
  - `.pytest_cache/`
  - `.mypy_cache/`
  - `.ruff_cache/`
  - `__pycache__/`
  - `dist/`
  - `build/`
  - `*.egg-info/`
- Release packaging snippets/manifests:
  - `manifest.json`
  - `README_RC1_SNIPPET.md`
  - `README_V1_SNIPPET.md`
  - `README_BETA2_SNIPPET.md`

## Not removed

The real product test suite should remain. Do not remove all tests.

## Validation

```bash
python -m pytest -q
orch --help
orch init
orch create-agent Bob
orch list-agents
orch list-tools
```
