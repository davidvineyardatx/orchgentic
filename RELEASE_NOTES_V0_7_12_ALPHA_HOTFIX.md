# Orchgentic v0.7.12-alpha Hotfix

This hotfix cleans up routing judgment consistency after the initial v0.7.12-alpha policy routing validation.

## Fixes

- Correctly classifies delete requests such as `delete gmail message id ...` as `gmail_delete` instead of `gmail_read`.
- Suppresses escalation telemetry when policy blocks or holds execution.
- Keeps the final decision and escalation object aligned:
  - `block` policy -> `escalation.escalate = False`
  - `hold_for_confirmation` policy -> `escalation.escalate = False`
  - provider/model remain `None` when escalation is suppressed by policy

## Validation

```bash
python -m pytest -q
```

Result:

```text
37 passed
```
