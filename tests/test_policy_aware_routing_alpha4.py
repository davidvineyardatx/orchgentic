from orchgentic.config.schemas import AgentConfig, TeamConfig
from orchgentic.runtime.execution_policy import classify_routing_execution_policy
from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment


def test_routing_judgment_includes_execution_policy():
    agent = AgentConfig(id="bob", name="Bob")
    judgment = evaluate_orchestration_judgment("what is the local time?", cfg=agent)

    assert "execution_policy" in judgment
    assert judgment["execution_policy"]["advisory"] is True
    assert judgment["execution_policy"]["enforced"] is False
    assert judgment["execution_policy"]["allowed"] is True
    assert judgment["execution_policy"]["policy_source"] == "execution_policy"


def test_policy_decision_recommends_local_llm_when_enabled():
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

    assert decision["purpose"] == "routing"
    assert decision["recommended_execution_tier"] == "local_llm_candidate"
    assert decision["policy_action"] == "recommend_local_llm"


def test_policy_decision_keeps_team_work_premium_or_configurable():
    team = TeamConfig(name="ContentTeam", orchestrator="Manager")
    decision = classify_routing_execution_policy(
        "research a topic and write an executive summary",
        team,
        route_type="team",
    )

    assert decision["advisory"] is True
    assert decision["enforced"] is False
    assert decision["allowed"] is True
    assert decision["recommended_execution_tier"] == "premium_external_candidate"
