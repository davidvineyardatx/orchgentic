# Workflow Doctor

`orch workflow doctor` validates workflow configuration before runtime execution.

The doctor should catch the most common workflow mistakes:

- missing required fields
- duplicate step ids
- unsupported trigger types
- unsupported step types
- referenced agents that do not exist
- referenced teams that do not exist
- referenced tools that are not registered
- unresolved output references
- unsafe destructive tool steps without explicit confirmation

## Example

```bash
orch workflow doctor workflows/daily-research-summary.yaml
```

Expected output:

```text
Workflow: Daily Research Summary
Status: OK

Checks:
  ✓ required fields
  ✓ trigger contract
  ✓ runtime contract
  ✓ step ids
  ✓ tool references
  ✓ agent references
  ✓ output references
```

## JSON output

```bash
orch workflow doctor workflows/daily-research-summary.yaml --json
```

Expected shape:

```json
{
  "workflow_id": "daily-research-summary",
  "status": "ok",
  "errors": [],
  "warnings": [],
  "checks": {
    "required_fields": "ok",
    "trigger_contract": "ok",
    "runtime_contract": "ok",
    "step_ids": "ok",
    "references": "ok",
    "outputs": "ok"
  }
}
```

## Severity guidance

### Error

Errors should block execution.

Examples:

- unknown tool
- unknown agent
- duplicate step id
- invalid trigger type
- missing required input
- missing output source

### Warning

Warnings should not block execution.

Examples:

- missing workflow description
- high timeout value
- no final output mapping
- no trace persistence
- large number of steps
