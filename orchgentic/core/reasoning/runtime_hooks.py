"""Runtime hook helpers for Orchgentic v0.7.11-alpha."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .confidence import ConfidenceScore, ConfidenceScorer
from .escalation import EscalationDecision, EscalationPolicy
from .local_reasoner import LocalDecision, LocalMiniReasoner, LocalReasoningResult


@dataclass(frozen=True)
class PreflightReasoning:
    local_result: LocalReasoningResult
    confidence: ConfidenceScore
    escalation: EscalationDecision


def preflight_reasoning(
    user_input: str,
    *,
    agent_config: Mapping[str, Any],
    available_tools: Sequence[str] | None = None,
    missing_tools: Sequence[str] | None = None,
    reflection_flags: Sequence[str] | None = None,
    severe_errors: Sequence[str] | None = None,
) -> PreflightReasoning:
    reasoning_cfg = agent_config.get("reasoning") or {}
    local_enabled = bool(reasoning_cfg.get("local_reasoner", True))
    confidence_enabled = bool(reasoning_cfg.get("confidence_scoring", True))

    local_reasoner = LocalMiniReasoner()
    if local_enabled:
        local_result = local_reasoner.evaluate(
            user_input,
            agent_config=agent_config,
            available_tools=available_tools,
        )
    else:
        local_result = LocalReasoningResult(
            decision=LocalDecision.ESCALATE_TO_LLM,
            confidence=0.50,
            reasons=["local_reasoner_disabled"],
        )

    scorer = ConfidenceScorer(
        high_threshold=float(reasoning_cfg.get("confidence_high_threshold", 0.78)),
        low_threshold=float(reasoning_cfg.get("confidence_low_threshold", 0.52)),
    )
    if confidence_enabled:
        confidence = scorer.score(
            local_confidence=local_result.confidence,
            missing_tools=missing_tools,
            reflection_flags=reflection_flags,
            task_complexity=_estimate_task_complexity(user_input),
        )
    else:
        confidence = scorer.score(local_confidence=0.75)

    escalation = EscalationPolicy().decide(
        local_result=local_result,
        confidence=confidence,
        agent_config=agent_config,
        severe_errors=severe_errors,
    )

    return PreflightReasoning(local_result=local_result, confidence=confidence, escalation=escalation)


def _estimate_task_complexity(user_input: str) -> str:
    text = (user_input or "").strip().lower()
    if any(term in text for term in ("legal", "medical", "financial", "security", "policy")):
        return "high_risk"
    if len(text.split()) > 40 or any(term in text for term in ("build", "implement", "debug", "research", "compare", "analyze")):
        return "complex"
    return "simple"
