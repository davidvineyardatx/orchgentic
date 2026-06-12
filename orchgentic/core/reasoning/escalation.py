"""Escalation policy for Orchgentic v0.7.11-alpha.

Important design rule: provider/model are configured exactly once, at the
agent provider block. Escalation only decides whether to use that configured
provider; it does not select a second provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .confidence import ConfidenceBand, ConfidenceScore
from .local_reasoner import LocalDecision, LocalReasoningResult


class EscalationAction(str, Enum):
    NONE = "none"
    CALL_LLM = "call_llm"
    STOP_WITH_ERROR = "stop_with_error"


@dataclass(frozen=True)
class EscalationDecision:
    action: EscalationAction
    reason: str
    confidence_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def should_call_llm(self) -> bool:
        return self.action == EscalationAction.CALL_LLM


class EscalationPolicy:
    """Chooses if/when to call the agent's configured provider.

    Expected config shape under agent YAML:

    provider:
      type: groq
      model: llama-3.3-70b-versatile

    reasoning:
      local_reasoner: true
      confidence_scoring: true
      escalation:
        enabled: true
        min_confidence: 0.52
    """

    def decide(
        self,
        *,
        local_result: LocalReasoningResult,
        confidence: ConfidenceScore,
        agent_config: Mapping[str, Any],
        severe_errors: Sequence[str] | None = None,
    ) -> EscalationDecision:
        reasoning_cfg = agent_config.get("reasoning") or {}
        escalation_cfg = reasoning_cfg.get("escalation") or {}
        enabled = bool(escalation_cfg.get("enabled", True))
        min_confidence = float(escalation_cfg.get("min_confidence", 0.52))
        severe_errors = list(severe_errors or [])

        if severe_errors:
            return EscalationDecision(
                action=EscalationAction.STOP_WITH_ERROR,
                reason="severe_errors_present",
                confidence_score=confidence.score,
                metadata={"severe_errors": severe_errors},
            )

        if not enabled:
            return EscalationDecision(
                action=EscalationAction.NONE,
                reason="escalation_disabled",
                confidence_score=confidence.score,
            )

        if local_result.decision == LocalDecision.ANSWER_LOCALLY and confidence.band != ConfidenceBand.LOW:
            return EscalationDecision(
                action=EscalationAction.NONE,
                reason="local_answer_confident_enough",
                confidence_score=confidence.score,
            )

        if local_result.decision == LocalDecision.USE_TOOL_RUNTIME and confidence.band == ConfidenceBand.HIGH:
            return EscalationDecision(
                action=EscalationAction.NONE,
                reason="tool_runtime_confident_enough",
                confidence_score=confidence.score,
            )

        if confidence.score < min_confidence or confidence.band == ConfidenceBand.LOW:
            return EscalationDecision(
                action=EscalationAction.CALL_LLM,
                reason="low_confidence_use_configured_provider",
                confidence_score=confidence.score,
            )

        return EscalationDecision(
            action=EscalationAction.CALL_LLM,
            reason="general_reasoning_required",
            confidence_score=confidence.score,
        )
