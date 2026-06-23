from orchgentic.config.schemas import AgentConfig
from orchgentic.runtime.execution_policy import (
    apply_safe_execution_policy_enforcement,
    classify_routing_execution_policy,
)
from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment


def test_deterministic_local_route_gets_safe_enforcement_metadata():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    enforcement = judgment["execution_policy"]["safe_enforcement"]

    assert judgment["execution_policy"]["recommended_execution_tier"] == "deterministic_saved"
    assert judgment["execution_policy"]["policy_action"] == "deterministic_allowed"
    assert enforcement["enforced"] is True
    assert enforcement["scope"] == "deterministic_local_only"
    assert enforcement["action"] == "enforce_local_execution"
    assert enforcement["external_llm_allowed"] is False


def test_generation_route_remains_observe_only():
    judgment = evaluate_orchestration_judgment(
        "Write a short summary of Orchgentic",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    enforcement = judgment["execution_policy"]["safe_enforcement"]

    assert judgment["final_decision"]["action"] == "call_llm"
    assert enforcement["enforced"] is False
    assert enforcement["scope"] == "observe_only"
    assert enforcement["action"] == "no_enforcement"


def test_local_llm_candidate_remains_advisory_not_enforced():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        execution_policy={
            "local_llm": {
                "enabled": True,
                "eligible_for": ["routing"],
            }
        },
    )
    decision = classify_routing_execution_policy(
        "what is the local time?",
        agent,
        route_type="single_tool",
    )

    decision = apply_safe_execution_policy_enforcement(
        decision,
        final_decision={"action": "answer_locally"},
    )

    assert decision["recommended_execution_tier"] == "local_llm_candidate"
    assert decision["policy_action"] == "recommend_local_llm"
    assert decision["safe_enforcement"]["enforced"] is False
    assert decision["safe_enforcement"]["scope"] == "observe_only"


def test_alpha4_advisory_fields_remain_stable():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    assert judgment["execution_policy"]["advisory"] is True
    assert judgment["execution_policy"]["enforced"] is False
    assert judgment["execution_policy"]["allowed"] is True
