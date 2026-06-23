from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DEFAULT_LOCAL_LLM_ELIGIBLE_FOR = [
    "classification",
    "routing",
    "summarization",
    "review",
]

DEFAULT_EXTERNAL_REQUIRE_FOR = [
    "complex_generation",
    "high_uncertainty_reasoning",
]

DEFAULT_PREMIUM_REQUIRE_FOR = [
    "final_synthesis",
    "executive_output",
    "high_quality_final",
]


@dataclass(frozen=True)
class NormalizedExecutionPolicy:
    enabled: bool = True
    default_mode: str = "external_llm_when_needed"
    deterministic_enabled: bool = True
    local_reasoning_enabled: bool = True
    local_llm_enabled: bool = False
    local_llm_eligible_for: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_LOCAL_LLM_ELIGIBLE_FOR))
    external_llm_enabled: bool = True
    external_llm_require_for: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_EXTERNAL_REQUIRE_FOR))
    premium_model_enabled: bool = True
    premium_model_require_for: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_PREMIUM_REQUIRE_FOR))

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "default_mode": self.default_mode,
            "deterministic": {
                "enabled": self.deterministic_enabled,
            },
            "local_reasoning": {
                "enabled": self.local_reasoning_enabled,
            },
            "local_llm": {
                "enabled": self.local_llm_enabled,
                "eligible_for": list(self.local_llm_eligible_for),
            },
            "external_llm": {
                "enabled": self.external_llm_enabled,
                "require_for": list(self.external_llm_require_for),
            },
            "premium_model": {
                "enabled": self.premium_model_enabled,
                "require_for": list(self.premium_model_require_for),
            },
        }


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return {
        key: getattr(value, key)
        for key in dir(value)
        if not key.startswith("_") and not callable(getattr(value, key))
    }


def _string_list(value: Any, fallback: list[str]) -> tuple[str, ...]:
    if value is None:
        return tuple(fallback)
    if isinstance(value, str):
        return (value,)
    try:
        return tuple(str(item) for item in value)
    except TypeError:
        return tuple(fallback)


def normalize_execution_policy(config_or_policy: Any = None) -> NormalizedExecutionPolicy:
    """Normalize agent/team execution policy into a stable runtime shape.

    This helper intentionally does not change routing behavior yet. It gives the
    rest of the runtime one safe, predictable object to read when policy-aware
    routing is introduced.
    """

    if config_or_policy is not None and hasattr(config_or_policy, "execution_policy"):
        raw = getattr(config_or_policy, "execution_policy")
    else:
        raw = config_or_policy

    data = _as_dict(raw)

    deterministic = _as_dict(data.get("deterministic"))
    local_reasoning = _as_dict(data.get("local_reasoning"))
    local_llm = _as_dict(data.get("local_llm"))
    external_llm = _as_dict(data.get("external_llm"))
    premium_model = _as_dict(data.get("premium_model"))

    return NormalizedExecutionPolicy(
        enabled=bool(data.get("enabled", True)),
        default_mode=str(data.get("default_mode", "external_llm_when_needed")),
        deterministic_enabled=bool(deterministic.get("enabled", True)),
        local_reasoning_enabled=bool(local_reasoning.get("enabled", True)),
        local_llm_enabled=bool(local_llm.get("enabled", False)),
        local_llm_eligible_for=_string_list(local_llm.get("eligible_for"), DEFAULT_LOCAL_LLM_ELIGIBLE_FOR),
        external_llm_enabled=bool(external_llm.get("enabled", True)),
        external_llm_require_for=_string_list(external_llm.get("require_for"), DEFAULT_EXTERNAL_REQUIRE_FOR),
        premium_model_enabled=bool(premium_model.get("enabled", True)),
        premium_model_require_for=_string_list(premium_model.get("require_for"), DEFAULT_PREMIUM_REQUIRE_FOR),
    )


def classify_execution_purpose(purpose: str, policy: Any = None) -> dict[str, Any]:
    """Classify a purpose against the normalized policy.

    This is advisory in alpha.3. Runtime enforcement comes in the next policy-aware
    routing patch.
    """

    normalized = normalize_execution_policy(policy)
    purpose_value = (purpose or "").strip().lower()

    if not normalized.enabled:
        return {
            "purpose": purpose_value,
            "recommended_execution_tier": "external_llm",
            "policy_action": "policy_disabled",
            "reason": "Execution policy is disabled.",
        }

    if normalized.local_llm_enabled and purpose_value in normalized.local_llm_eligible_for:
        return {
            "purpose": purpose_value,
            "recommended_execution_tier": "local_llm_candidate",
            "policy_action": "recommend_local_llm",
            "reason": f"{purpose_value} is eligible for local LLM execution.",
        }

    if purpose_value in normalized.premium_model_require_for:
        return {
            "purpose": purpose_value,
            "recommended_execution_tier": "premium_external_candidate",
            "policy_action": "keep_premium_or_configurable",
            "reason": f"{purpose_value} is configured as premium-model work.",
        }

    if purpose_value in normalized.external_llm_require_for:
        return {
            "purpose": purpose_value,
            "recommended_execution_tier": "external_llm",
            "policy_action": "allow_external_llm",
            "reason": f"{purpose_value} is configured to require an external LLM.",
        }

    return {
        "purpose": purpose_value,
        "recommended_execution_tier": normalized.default_mode,
        "policy_action": "use_default_mode",
        "reason": f"{purpose_value or 'unknown'} did not match a specific execution policy bucket.",
    }


def infer_execution_purpose(
    task: str = "",
    *,
    local_decision: Any = None,
    escalation: Any = None,
    final_decision: Any = None,
    route_type: str | None = None,
) -> str:
    """Infer a coarse execution purpose for advisory policy classification."""

    action = getattr(final_decision, "action", None)
    action_value = getattr(action, "value", action)

    if action_value == "run_workflow" or route_type in {"team", "workflow"}:
        return "final_synthesis"

    if action_value == "call_llm":
        return "complex_generation"

    if route_type in {"single_tool", "multi_tool"}:
        return "routing"

    if getattr(escalation, "escalate", False) or getattr(escalation, "should_call_llm", False):
        return "complex_generation"

    intent = (getattr(local_decision, "intent", "") or "").lower()
    if intent in {"datetime", "tool", "gmail", "memory", "knowledge"}:
        return "routing"

    text = (task or "").lower()
    if any(term in text for term in ("review", "check quality", "critique")):
        return "review"
    if any(term in text for term in ("summarize", "summary")):
        return "summarization"
    if any(term in text for term in ("classify", "categorize")):
        return "classification"
    if any(term in text for term in ("executive", "final answer", "final synthesis")):
        return "executive_output"
    if any(term in text for term in ("research", "compare", "analyze", "write", "draft", "generate")):
        return "complex_generation"

    return "routing"


def classify_routing_execution_policy(
    task: str = "",
    policy: Any = None,
    *,
    local_decision: Any = None,
    escalation: Any = None,
    final_decision: Any = None,
    route_type: str | None = None,
) -> dict[str, Any]:
    """Build an advisory execution-policy decision for routing/debug/trace output.

    This is advisory only. It exposes policy influence without blocking,
    forcing reroutes, or changing provider behavior.
    """

    purpose = infer_execution_purpose(
        task,
        local_decision=local_decision,
        escalation=escalation,
        final_decision=final_decision,
        route_type=route_type,
    )
    normalized = normalize_execution_policy(policy)

    action = getattr(final_decision, "action", None)
    action_value = getattr(action, "value", action)

    deterministic_route = action_value == "answer_locally" or (
        route_type in {"single_tool", "multi_tool"}
        and not normalized.local_llm_enabled
    )

    if deterministic_route:
        decision = {
            "purpose": purpose,
            "recommended_execution_tier": "deterministic_saved",
            "policy_action": "deterministic_allowed",
            "reason": "This route was satisfied by deterministic/local execution and avoided an external LLM.",
        }
    else:
        decision = classify_execution_purpose(purpose, policy)

    decision.update(
        {
            "advisory": True,
            "enforced": False,
            "allowed": True,
            "policy_source": "execution_policy",
        }
    )
    return decision
