# v0.9.0-rc.1-hotfix.1

## Fix

Adds the missing root-level release notes file expected by `tests/test_rc1_docs_exist.py`:

```text
RELEASE_NOTES_v0.9.0-rc.1.md
```

## Scope

No runtime changes. No docs scope expansion. No workflow changes.

## Validation

```bash
python -m pytest -q tests/test_rc1_docs_exist.py
python -m pytest -q tests/test_rc1_clean_install_commands_documented.py
python -m pytest -q
```
