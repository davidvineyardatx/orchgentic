from __future__ import annotations

from typing import Any


def preview_tool_policy_decision(tool_name: str, arguments: dict[str, Any] | None, agent_config: Any) -> dict[str, Any]:
    """Return an explainable policy preview for direct tool execution.

    This helper does not replace tool-level enforcement. It gives observability a
    first-class `policy.checked` event before a direct tool run executes or is
    held/blocked.
    """
    arguments = arguments or {}
    policies = getattr(agent_config, "tool_policies", {}) or {}
    policy = policies.get(tool_name, {}) if isinstance(policies, dict) else {}

    if policy.get("enabled") is False:
        return {
            "action": "block",
            "allowed": False,
            "reason": f"Tool '{tool_name}' is disabled by policy.",
            "affected_tools": [tool_name],
            "require_confirmation": False,
            "external_llm_allowed": False,
            "metadata": {"policy": policy},
        }

    require_confirmation = bool((policy or {}).get("require_confirmation", False))

    if tool_name == "gmail.send":
        send_policy = (policy or {}).get("send_policy", {}) or {}
        mode = send_policy.get("mode", "disabled")
        if mode == "disabled":
            return {
                "action": "block",
                "allowed": False,
                "reason": "gmail.send is disabled by send policy.",
                "affected_tools": [tool_name],
                "require_confirmation": False,
                "external_llm_allowed": False,
                "metadata": {"policy": policy},
            }
        require_confirmation = require_confirmation or bool(send_policy.get("require_confirmation", False))

        if mode != "unrestricted":
            allowed_addresses = {str(a).lower() for a in send_policy.get("allowed_addresses", []) or []}
            allowed_domains = {str(d).lower().lstrip("@") for d in send_policy.get("allowed_domains", []) or []}
            recipients = [addr.strip().lower() for addr in str(arguments.get("to", "")).split(",") if addr.strip()]
            for recipient in recipients:
                domain = recipient.split("@")[-1] if "@" in recipient else ""
                if recipient not in allowed_addresses and domain not in allowed_domains:
                    return {
                        "action": "block",
                        "allowed": False,
                        "reason": f"Recipient '{recipient}' is not allowed by gmail.send policy.",
                        "affected_tools": [tool_name],
                        "require_confirmation": False,
                        "external_llm_allowed": False,
                        "metadata": {"recipient": recipient, "policy": policy},
                    }

    confirm_supplied = arguments.get("confirm") is True
    if require_confirmation and not confirm_supplied:
        return {
            "action": "hold_for_confirmation",
            "allowed": False,
            "reason": f"Tool '{tool_name}' requires explicit confirmation.",
            "affected_tools": [tool_name],
            "require_confirmation": True,
            "external_llm_allowed": False,
            "metadata": {"policy": policy},
        }

    return {
        "action": "allow",
        "allowed": True,
        "reason": "Tool policy allows execution." if policy else "No restricted tool policy applies.",
        "affected_tools": [tool_name] if policy else [],
        "require_confirmation": False,
        "external_llm_allowed": True,
        "metadata": {"policy": policy} if policy else {},
    }
