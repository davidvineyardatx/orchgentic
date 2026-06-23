from orchgentic.config.schemas import AgentConfig
from orchgentic.runtime.execution_policy import (
    apply_safe_execution_policy_enforcement,
    classify_routing_execution_policy,
    summarize_execution_policy_enforcement,
)
from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment


def test_deterministic_route_includes_enforcement_summary():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    summary = judgment["execution_policy"]["enforcement_summary"]

    assert judgment["execution_policy"]["enforced"] is False
    assert judgment["execution_policy"]["safe_enforcement"]["enforced"] is True
    assert summary["mode"] == "safe_deterministic_only"
    assert summary["status"] == "safely_enforced"
    assert summary["safe_enforcement_applied"] is True
    assert summary["full_policy_enforced"] is False


def test_generation_route_enforcement_summary_remains_advisory():
    judgment = evaluate_orchestration_judgment(
        "Write a short summary of Orchgentic",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    summary = judgment["execution_policy"]["enforcement_summary"]

    assert judgment["execution_policy"]["safe_enforcement"]["enforced"] is False
    assert summary["mode"] == "observe_only"
    assert summary["status"] == "advisory"
    assert summary["safe_enforcement_applied"] is False
    assert summary["full_policy_enforced"] is False


def test_summary_helper_is_idempotent_for_existing_policy_dict():
    decision = {
        "policy_action": "deterministic_allowed",
        "safe_enforcement": {
            "enforced": True,
            "scope": "deterministic_local_only",
        },
    }

    summarized = summarize_execution_policy_enforcement(decision)
    summarized_again = summarize_execution_policy_enforcement(summarized)

    assert summarized_again["enforcement_summary"]["mode"] == "safe_deterministic_only"


def test_local_llm_candidate_still_not_safe_enforced():
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
    assert decision["safe_enforcement"]["enforced"] is False
    assert decision["enforcement_summary"]["mode"] == "observe_only"
