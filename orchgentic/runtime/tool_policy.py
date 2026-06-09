from dataclasses import dataclass, field
from typing import Any

class ToolPolicyError(Exception):
    pass

@dataclass
class SendPolicy:
    mode: str = "disabled"
    allowed_addresses: list[str] = field(default_factory=list)
    allowed_domains: list[str] = field(default_factory=list)
    require_confirmation: bool = True

@dataclass
class ToolPolicy:
    enabled: bool = True
    require_confirmation: bool = False
    send_policy: SendPolicy | None = None

class ToolPolicyRuntime:
    def __init__(self, agent_config=None):
        self.agent_config = agent_config

    def get_policy(self, tool_name: str) -> dict[str, Any]:
        policies = getattr(self.agent_config, "tool_policies", None)
        if isinstance(policies, dict):
            return policies.get(tool_name, {}) or {}
        return {}

    def enforce_enabled(self, tool_name: str) -> None:
        policy = self.get_policy(tool_name)
        if policy and policy.get("enabled") is False:
            raise ToolPolicyError(f"Tool '{tool_name}' is disabled by policy.")

    def enforce_confirmation(self, tool_name: str, confirm: bool = False) -> None:
        policy = self.get_policy(tool_name)
        if bool((policy or {}).get("require_confirmation", False)) and confirm is not True:
            raise ToolPolicyError(f"Tool '{tool_name}' requires explicit confirmation. Pass confirm=true.")

    def enforce_action(self, tool_name: str, confirm: bool = False) -> None:
        self.enforce_enabled(tool_name)
        self.enforce_confirmation(tool_name, confirm)

    def enforce_gmail_send(self, to: str, confirm: bool = False) -> None:
        self.enforce_action("gmail.send", confirm)
        policy = self.get_policy("gmail.send")
        send_policy = (policy or {}).get("send_policy", {}) or {}
        mode = send_policy.get("mode", "disabled")

        if mode == "disabled":
            raise ToolPolicyError("gmail.send is disabled by send policy.")
        if mode == "unrestricted":
            return

        allowed_addresses = {a.lower() for a in send_policy.get("allowed_addresses", [])}
        allowed_domains = {d.lower().lstrip("@") for d in send_policy.get("allowed_domains", [])}

        recipients = [addr.strip().lower() for addr in to.split(",") if addr.strip()]
        if not recipients:
            raise ToolPolicyError("gmail.send requires at least one recipient.")

        for addr in recipients:
            domain = addr.split("@")[-1] if "@" in addr else ""
            if addr not in allowed_addresses and domain not in allowed_domains:
                raise ToolPolicyError(f"Recipient '{addr}' is not allowed by gmail.send policy.")
