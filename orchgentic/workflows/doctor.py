from __future__ import annotations


def format_workflow_doctor(payload: dict) -> str:
    """Format workflow doctor output without importing the CLI module."""

    lines = ["WORKFLOW DOCTOR"]
    lines.append(f"status: {payload.get('status')}")
    lines.append(f"valid: {payload.get('valid')}")
    lines.append(f"workflow_count: {payload.get('workflow_count', 0)}")
    lines.append(f"runtime_behavior_changed: {payload.get('runtime_behavior_changed')}")

    errors = payload.get("errors") or []
    warnings = payload.get("warnings") or []

    if errors:
        lines.append("errors:")
        for item in errors:
            workflow = item.get("workflow") or item.get("workflow_id") or "-"
            lines.append(f"  - {workflow}: {item.get('code')}: {item.get('message')}")

    if warnings:
        lines.append("warnings:")
        for item in warnings:
            workflow = item.get("workflow") or item.get("workflow_id") or "-"
            lines.append(f"  - {workflow}: {item.get('code')}: {item.get('message')}")

    if not errors and not warnings:
        lines.append("checks: all workflow contracts are valid")

    return "\n".join(lines)


def format_workflow_contract(payload: dict) -> str:
    lines = ["WORKFLOW CONTRACT"]
    lines.append(f"id: {payload.get('workflow_id')}")
    lines.append(f"name: {payload.get('workflow_name')}")
    lines.append(f"version: {payload.get('workflow_version')}")
    lines.append(f"status: {payload.get('status')}")
    lines.append(f"team: {payload.get('team_name')}")
    lines.append(f"team_backed: {payload.get('team_backed')}")
    lines.append(f"steps: {payload.get('step_count')}")
    lines.append(f"runtime_behavior_changed: {payload.get('runtime_behavior_changed')}")
    return "\n".join(lines)
