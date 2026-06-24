from __future__ import annotations


def format_tool_contract_doctor(payload: dict) -> str:
    """Format tool-contract doctor output without importing the CLI module."""

    lines = ["TOOL CONTRACT DOCTOR"]
    lines.append(f"status: {payload.get('status')}")
    lines.append(f"valid: {payload.get('valid')}")
    lines.append(f"tool_count: {payload.get('tool_count')}")
    lines.append(f"plugin_loader_added: {payload.get('plugin_loader_added')}")
    lines.append(f"runtime_behavior_changed: {payload.get('runtime_behavior_changed')}")

    errors = payload.get("errors") or []
    warnings = payload.get("warnings") or []

    if errors:
        lines.append("errors:")
        for item in errors:
            tool = item.get("tool") or "-"
            lines.append(f"  - {tool}: {item.get('code')}: {item.get('message')}")

    if warnings:
        lines.append("warnings:")
        for item in warnings:
            tool = item.get("tool") or "-"
            lines.append(f"  - {tool}: {item.get('code')}: {item.get('message')}")

    if not errors and not warnings:
        lines.append("checks: all built-in tool contracts match the frozen baseline")

    return "\n".join(lines)
