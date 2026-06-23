from orchgentic.config.schemas import AgentConfig, TeamConfig
from orchgentic.runtime.execution_policy import (
    classify_execution_purpose,
    normalize_execution_policy,
)


def test_agent_execution_policy_defaults_are_available():
    agent = AgentConfig(id="bob", name="Bob")

    policy = normalize_execution_policy(agent)

    assert policy.enabled is True
    assert policy.default_mode == "external_llm_when_needed"
    assert policy.deterministic_enabled is True
    assert policy.local_reasoning_enabled is True
    assert policy.local_llm_enabled is False
    assert "routing" in policy.local_llm_eligible_for
    assert "final_synthesis" in policy.premium_model_require_for


def test_team_execution_policy_defaults_are_available():
    team = TeamConfig(name="ContentTeam", orchestrator="Manager")

    policy = normalize_execution_policy(team)

    assert policy.enabled is True
    assert policy.external_llm_enabled is True
    assert "complex_generation" in policy.external_llm_require_for


def test_custom_execution_policy_normalizes_from_dict():
    policy = normalize_execution_policy(
        {
            "enabled": True,
            "default_mode": "local_llm_when_safe",
            "local_llm": {
                "enabled": True,
                "eligible_for": ["classification", "routing"],
            },
            "premium_model": {
                "enabled": True,
                "require_for": ["final_synthesis"],
            },
        }
    )

    assert policy.default_mode == "local_llm_when_safe"
    assert policy.local_llm_enabled is True
    assert policy.local_llm_eligible_for == ("classification", "routing")
    assert policy.premium_model_require_for == ("final_synthesis",)


def test_classify_execution_purpose_recommends_local_llm_when_enabled():
    decision = classify_execution_purpose(
        "routing",
        {
            "local_llm": {
                "enabled": True,
                "eligible_for": ["routing"],
            },
        },
    )

    assert decision["recommended_execution_tier"] == "local_llm_candidate"
    assert decision["policy_action"] == "recommend_local_llm"


def test_classify_execution_purpose_keeps_final_synthesis_premium():
    decision = classify_execution_purpose("final_synthesis")

    assert decision["recommended_execution_tier"] == "premium_external_candidate"
    assert decision["policy_action"] == "keep_premium_or_configurable"


def test_classify_execution_purpose_uses_default_for_unknown_purpose():
    decision = classify_execution_purpose("unknown_work")

    assert decision["recommended_execution_tier"] == "external_llm_when_needed"
    assert decision["policy_action"] == "use_default_mode"
