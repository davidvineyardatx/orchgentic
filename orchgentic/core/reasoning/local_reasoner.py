"""Local mini-reasoner for Orchgentic v0.7.11-alpha.

The local reasoner is intentionally lightweight and deterministic. It does not
replace the configured provider. It decides whether a task can be handled
locally, whether tools are likely needed, or whether the normal LLM path should
be used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Mapping, Sequence


class LocalDecision(str, Enum):
    ANSWER_LOCALLY = "answer_locally"
    USE_TOOL_RUNTIME = "use_tool_runtime"
    ESCALATE_TO_LLM = "escalate_to_llm"
    REFUSE_OR_CLARIFY = "refuse_or_clarify"


@dataclass(frozen=True)
class LocalReasoningResult:
    decision: LocalDecision
    confidence: float
    reasons: list[str] = field(default_factory=list)
    suggested_tools: list[str] = field(default_factory=list)
    local_answer: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def should_escalate(self) -> bool:
        return self.decision == LocalDecision.ESCALATE_TO_LLM

    @property
    def should_use_tools(self) -> bool:
        return self.decision == LocalDecision.USE_TOOL_RUNTIME


class LocalMiniReasoner:
    """Small deterministic router used before calling the configured provider.

    Conservative by design: anything complex, ambiguous, open-ended,
    policy-sensitive, or requiring fresh/world knowledge escalates to the
    agent's existing provider path.
    """

    DIRECT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
        (re.compile(r"^\s*(hi|hello|hey|howdy)\s*[!.]?\s*$", re.I), "Hello. How can I help?"),
        (re.compile(r"^\s*(thanks|thank you|appreciate it)\s*[!.]?\s*$", re.I), "You’re welcome."),
        (re.compile(r"^\s*what\s+is\s+(-?\d+)\s*([+\-*/])\s*(-?\d+)\s*\??\s*$", re.I), "__MATH__"),
    )

    TOOL_HINTS: Mapping[str, tuple[str, ...]] = {
        "datetime.local": ("time", "date", "today", "tomorrow", "yesterday", "day is it"),
        "filesystem.read": ("read file", "open file", "load file", "inspect file"),
        "filesystem.write": ("write file", "save file", "create file", "update file"),
        "web.request": ("http", "https", "api", "webhook", "request url", "fetch"),
        "memory.search": ("remember", "memory", "what did i say", "previously"),
        "knowledge.search": ("knowledge", "docs", "documentation", "ingested"),
    }

    ESCALATION_HINTS: tuple[str, ...] = (
        "latest", "current", "news", "research", "compare", "analyze", "strategy",
        "build", "implement", "code", "debug", "why", "how", "plan", "summarize",
        "email", "legal", "medical", "financial", "policy", "security", "create",
        "write", "draft", "explain", "recommend",
    )

    CLARIFY_HINTS: tuple[str, ...] = ("something", "stuff", "thing")

    def evaluate(
        self,
        user_input: str,
        *,
        agent_config: Mapping[str, Any] | None = None,
        available_tools: Sequence[str] | None = None,
    ) -> LocalReasoningResult:
        text = (user_input or "").strip()
        lower = text.lower()
        tools = {tool.lower() for tool in (available_tools or [])}

        if not text:
            return LocalReasoningResult(
                decision=LocalDecision.REFUSE_OR_CLARIFY,
                confidence=0.95,
                reasons=["empty_input"],
                local_answer="Please provide a task or question.",
            )

        for pattern, answer in self.DIRECT_PATTERNS:
            match = pattern.match(text)
            if not match:
                continue
            if answer == "__MATH__":
                return self._simple_math(match)
            return LocalReasoningResult(
                decision=LocalDecision.ANSWER_LOCALLY,
                confidence=0.96,
                reasons=["matched_safe_direct_pattern"],
                local_answer=answer,
            )

        suggested = [tool for tool, hints in self.TOOL_HINTS.items() if any(hint in lower for hint in hints)]
        available_suggested = [tool for tool in suggested if not tools or tool in tools]
        if available_suggested:
            return LocalReasoningResult(
                decision=LocalDecision.USE_TOOL_RUNTIME,
                confidence=0.82,
                reasons=["tool_hint_detected"],
                suggested_tools=available_suggested,
                metadata={"all_tool_hints": suggested},
            )

        if any(hint in lower for hint in self.ESCALATION_HINTS):
            return LocalReasoningResult(
                decision=LocalDecision.ESCALATE_TO_LLM,
                confidence=0.44,
                reasons=["complex_or_open_ended_task"],
            )

        if len(text.split()) <= 4 and any(token in lower.split() for token in self.CLARIFY_HINTS):
            return LocalReasoningResult(
                decision=LocalDecision.REFUSE_OR_CLARIFY,
                confidence=0.70,
                reasons=["ambiguous_short_request"],
                local_answer="Can you clarify what you want me to do?",
            )

        return LocalReasoningResult(
            decision=LocalDecision.ESCALATE_TO_LLM,
            confidence=0.58,
            reasons=["default_to_provider_for_safety"],
        )

    def _simple_math(self, match: re.Match[str]) -> LocalReasoningResult:
        left = int(match.group(1))
        op = match.group(2)
        right = int(match.group(3))
        try:
            if op == "+":
                value = left + right
            elif op == "-":
                value = left - right
            elif op == "*":
                value = left * right
            elif op == "/":
                if right == 0:
                    return LocalReasoningResult(
                        decision=LocalDecision.REFUSE_OR_CLARIFY,
                        confidence=0.98,
                        reasons=["division_by_zero"],
                        local_answer="Division by zero is undefined.",
                    )
                value = left / right
            else:
                raise ValueError(op)
        except Exception as exc:
            return LocalReasoningResult(
                decision=LocalDecision.ESCALATE_TO_LLM,
                confidence=0.30,
                reasons=["simple_math_failed"],
                metadata={"error": str(exc)},
            )

        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return LocalReasoningResult(
            decision=LocalDecision.ANSWER_LOCALLY,
            confidence=0.98,
            reasons=["safe_integer_math"],
            local_answer=str(value),
        )
