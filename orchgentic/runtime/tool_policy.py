class ToolPolicyError(Exception):
    pass

class ToolPolicyRuntime:
    def __init__(self, agent_config=None):
        self.agent_config = agent_config
    def get_policy(self, tool_name: str):
        policies = getattr(self.agent_config, "tool_policies", None) or {}
        return policies.get(tool_name, {}) if isinstance(policies, dict) else {}
    def enforce_enabled(self, tool_name: str):
        policy = self.get_policy(tool_name)
        if policy and policy.get("enabled") is False:
            raise ToolPolicyError(f"Tool '{tool_name}' is disabled by policy.")
    def enforce_gmail_send(self, to: str):
        policy = self.get_policy("gmail.send")
        if policy and policy.get("enabled") is False:
            raise ToolPolicyError("gmail.send is disabled by policy.")
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
