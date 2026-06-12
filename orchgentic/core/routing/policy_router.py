from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import re


class PolicyAction(str, Enum):
    ALLOW = "allow"
    CALL_LLM = "call_llm"
    HOLD_FOR_CONFIRMATION = "hold_for_confirmation"
    BLOCK = "block"


@dataclass(slots=True)
class PolicyRoute:
    action: str
    allowed: bool
    confidence: float
    reason: str
    affected_tools: list[str] = field(default_factory=list)
    require_confirmation: bool = False
    external_llm_allowed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PolicyRouter:
    """Evaluates tool policy before escalation or execution.

    This router does not replace tool-level enforcement. It provides an early,
    explainable routing decision so restricted or disabled actions do not get
    sent to an LLM first just to discover a policy block later.
    """

    TOOL_SIGNAL_TERMS: dict[str, list[str]] = {
        "gmail.send": ["send email", "send gmail", "email to", "send a message"],
        "gmail.reply": ["reply to email", "reply to gmail", "respond to email"],
        "gmail.delete": ["delete email", "delete gmail", "trash email", "trash gmail", "remove email"],
        "gmail.draft": ["draft email", "draft gmail", "draft a reply"],
        "gmail.read": ["read email", "read gmail", "message id"],
        "gmail.search": ["search email", "search gmail", "find email", "find gmail", "unread email"],
    }

    SIDE_EFFECT_TOOLS = {"gmail.send", "gmail.reply", "gmail.delete", "filesystem.write"}

    def evaluate(
        self,
        task: str,
        *,
        agent_config: Any = None,
        candidate_tools: list[str] | None = None,
        event_route: Any = None,
    ) -> PolicyRoute:
        text = (task or "").strip().lower()
        candidate_tools = list(candidate_tools or [])
        detected_tools = self._detect_tools(text)
        affected_tools = self._unique(candidate_tools + detected_tools)

        if not affected_tools:
            return PolicyRoute(PolicyAction.ALLOW.value, True, 0.72, "No restricted tool policy applies")

        policies = getattr(agent_config, "tool_policies", {}) if agent_config is not None else {}
        if not isinstance(policies, dict):
            policies = {}

        autonomous = bool(getattr(event_route, "require_extra_policy_checks", False))
        confirm_supplied = self._confirmation_supplied(text)

        for tool in affected_tools:
            policy = policies.get(tool, {}) or {}
            if policy.get("enabled") is False:
                return PolicyRoute(
                    PolicyAction.BLOCK.value,
                    False,
                    0.98,
                    f"Tool '{tool}' is disabled by policy.",
                    affected_tools=[tool],
                    external_llm_allowed=False,
                    metadata={"policy": policy},
                )

            requires_confirmation = bool(policy.get("require_confirmation", False))
            if tool == "gmail.send":
                send_policy = (policy.get("send_policy", {}) or {}) if isinstance(policy, dict) else {}
                if send_policy.get("mode", "disabled") == "disabled":
                    return PolicyRoute(
                        PolicyAction.BLOCK.value,
                        False,
                        0.98,
                        "gmail.send is disabled by send policy.",
                        affected_tools=[tool],
                        external_llm_allowed=False,
                        metadata={"policy": policy},
                    )
                requires_confirmation = requires_confirmation or bool(send_policy.get("require_confirmation", False))

                recipient = self._extract_email(task)
                if recipient:
                    allowed, recipient_reason = self._recipient_allowed(recipient, send_policy)
                    if not allowed:
                        return PolicyRoute(
                            PolicyAction.BLOCK.value,
                            False,
                            0.97,
                            recipient_reason,
                            affected_tools=[tool],
                            external_llm_allowed=False,
                            metadata={"recipient": recipient, "policy": policy},
                        )

            if autonomous and tool in self.SIDE_EFFECT_TOOLS and requires_confirmation:
                return PolicyRoute(
                    PolicyAction.HOLD_FOR_CONFIRMATION.value,
                    False,
                    0.95,
                    f"Tool '{tool}' requires confirmation and the event is autonomous.",
                    affected_tools=[tool],
                    require_confirmation=True,
                    external_llm_allowed=False,
                    metadata={"autonomous_event": True, "policy": policy},
                )

            if requires_confirmation and not confirm_supplied:
                return PolicyRoute(
                    PolicyAction.HOLD_FOR_CONFIRMATION.value,
                    False,
                    0.94,
                    f"Tool '{tool}' requires explicit confirmation.",
                    affected_tools=[tool],
                    require_confirmation=True,
                    external_llm_allowed=False,
                    metadata={"policy": policy},
                )

        return PolicyRoute(
            PolicyAction.ALLOW.value,
            True,
            0.90,
            "Tool policy allows routing to continue.",
            affected_tools=affected_tools,
        )

    def _detect_tools(self, text: str) -> list[str]:
        tools = []
        for tool, terms in self.TOOL_SIGNAL_TERMS.items():
            if any(term in text for term in terms):
                tools.append(tool)
        return tools

    def _confirmation_supplied(self, text: str) -> bool:
        return any(term in text for term in ["confirm=true", "confirmed", "i confirm", "with confirmation", "yes send", "go ahead and send"])

    def _extract_email(self, text: str) -> str | None:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text or "")
        return match.group(0).lower() if match else None

    def _recipient_allowed(self, recipient: str, send_policy: dict[str, Any]) -> tuple[bool, str]:
        mode = send_policy.get("mode", "disabled")
        if mode == "unrestricted":
            return True, "recipient allowed by unrestricted send policy"
        allowed_addresses = {a.lower() for a in send_policy.get("allowed_addresses", []) or []}
        allowed_domains = {d.lower().lstrip("@") for d in send_policy.get("allowed_domains", []) or []}
        domain = recipient.split("@")[-1] if "@" in recipient else ""
        if recipient in allowed_addresses or domain in allowed_domains:
            return True, "recipient allowed by send policy"
        return False, f"Recipient '{recipient}' is not allowed by gmail.send policy."

    def _unique(self, values: list[str]) -> list[str]:
        seen = set()
        unique = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                unique.append(value)
        return unique
