from __future__ import annotations


def format_execution_tier_doctor(payload: dict) -> str:
    """Format execution-tier doctor payload without importing the CLI module."""

    lines = ["EXECUTION TIER DOCTOR"]
    lines.append(f"agent: {payload.get('agent')}")
    lines.append(f"status: {payload.get('status')}")
    lines.append(f"valid: {payload.get('valid')}")
    lines.append(f"routing_behavior_changed: {payload.get('routing_behavior_changed')}")

    tiers = payload.get("execution_tiers") or {}
    local_llm = tiers.get("local_llm") or {}
    lines.append("local_llm:")
    lines.append(f"  enabled: {local_llm.get('enabled')}")
    lines.append(f"  provider: {local_llm.get('provider')}")
    lines.append(f"  model: {local_llm.get('model')}")

    eligible_for = local_llm.get("eligible_for") or []
    lines.append(f"  eligible_for: {', '.join(eligible_for) if eligible_for else '-'}")

    errors = payload.get("errors") or []
    warnings = payload.get("warnings") or []

    if errors:
        lines.append("errors:")
        for item in errors:
            lines.append(f"  - {item.get('code')}: {item.get('message')}")

    if warnings:
        lines.append("warnings:")
        for item in warnings:
            lines.append(f"  - {item.get('code')}: {item.get('message')}")

    if not errors and not warnings:
        lines.append("checks: no execution-tier issues found")

    return "\n".join(lines)
