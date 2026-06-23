from orchgentic.config.schemas import AgentConfig
from orchgentic.runtime.execution_policy import classify_routing_execution_policy
from orchgentic.runtime.router_judgment import (
    evaluate_orchestration_judgment,
    format_orchestration_judgment_for_cli,
)


def test_local_answer_policy_classifies_as_deterministic_saved():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    assert judgment["final_decision"]["action"] == "answer_locally"
    assert judgment["execution_policy"]["recommended_execution_tier"] == "deterministic_saved"
    assert judgment["execution_policy"]["policy_action"] == "deterministic_allowed"


def test_direct_tool_policy_classifies_as_deterministic_saved_when_local_llm_disabled():
    decision = classify_routing_execution_policy(
        "what is the local time?",
        AgentConfig(id="bob", name="Bob"),
        route_type="single_tool",
    )

    assert decision["recommended_execution_tier"] == "deterministic_saved"
    assert decision["policy_action"] == "deterministic_allowed"


def test_local_llm_policy_still_recommends_local_llm_when_enabled():
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

    assert decision["recommended_execution_tier"] == "local_llm_candidate"
    assert decision["policy_action"] == "recommend_local_llm"


def test_cli_judgment_formats_workflow_as_not_applicable_for_single_agent_routes():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    formatted = format_orchestration_judgment_for_cli(judgment)

    assert isinstance(judgment["workflow"], dict)
    assert judgment["workflow"]["should_use_workflow"] is False
    assert formatted["workflow"]["applicable"] is False
    assert formatted["workflow"]["reason"] == "Not applicable for single-agent routing."
    assert formatted["workflow"]["workflow_type"] is None
