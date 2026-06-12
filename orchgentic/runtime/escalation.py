from dataclasses import dataclass, field
from typing import Any

@dataclass
class EscalationPolicy:
    local_confidence_threshold: float = 0.70
    deterministic_confidence_threshold: float = 0.90
    external_llm_on_generation: bool = True
    external_llm_on_analysis: bool = True
    external_llm_on_low_confidence: bool = True
    preferred_external_provider: str | None = None
    preferred_external_model: str | None = None

@dataclass
class EscalationDecision:
    escalate: bool
    reason: str
    selected_provider: str | None = None
    selected_model: str | None = None
    reasoning_depth: str = "standard"
    metadata: dict[str, Any] = field(default_factory=dict)

class EscalationEngine:
    """
    Advisory escalation engine for v0.7.11-alpha.
    """

    def __init__(self, policy: EscalationPolicy | None = None):
        self.policy = policy or EscalationPolicy()

    def decide(self, local_decision, provider_config=None) -> EscalationDecision:
        provider = getattr(provider_config, "type", None) if provider_config is not None else None
        model = getattr(provider_config, "model", None) if provider_config is not None else None
        selected_provider = self.policy.preferred_external_provider or provider
        selected_model = self.policy.preferred_external_model or model

        signals = getattr(local_decision, "signals", {}) or {}
        confidence = float(getattr(local_decision, "confidence", 0.0) or 0.0)
        reason = getattr(local_decision, "escalation_reason", "") or ""

        if signals.get("has_generation") and self.policy.external_llm_on_generation:
            return EscalationDecision(True, reason or "Generation requires external LLM", selected_provider, selected_model, "creative", {"confidence": confidence, "signals": signals})

        if signals.get("has_analysis") and self.policy.external_llm_on_analysis:
            return EscalationDecision(True, reason or "Analysis requires external LLM", selected_provider, selected_model, "analytical", {"confidence": confidence, "signals": signals})

        if confidence < self.policy.local_confidence_threshold and self.policy.external_llm_on_low_confidence:
            return EscalationDecision(True, reason or "Confidence below threshold", selected_provider, selected_model, "standard", {"confidence": confidence, "signals": signals})

        return EscalationDecision(False, reason or "No escalation required", None, None, "none", {"confidence": confidence, "signals": signals})

def default_escalation_policy() -> EscalationPolicy:
    return EscalationPolicy()
