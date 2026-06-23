from pathlib import Path

from orchgentic.config.schemas import AgentConfig, TeamConfig
from orchgentic.runtime.execution_policy import (
    apply_safe_execution_policy_enforcement,
    classify_routing_execution_policy,
)


def test_agent_local_policy_trace_payload_contains_safe_enforcement():
    agent = AgentConfig(id="bob", name="Bob")
    decision = classify_routing_execution_policy(
        "what is the local time?",
        agent,
        final_decision={"action": "answer_locally"},
    )
    decision = apply_safe_execution_policy_enforcement(
        decision,
        final_decision={"action": "answer_locally"},
    )

    assert decision["policy_action"] == "deterministic_allowed"
    assert decision["safe_enforcement"]["enforced"] is True
    assert decision["safe_enforcement"]["external_llm_allowed"] is False


def test_team_policy_trace_payload_remains_observe_only():
    team = TeamConfig(name="ContentTeam", orchestrator="Manager")
    decision = classify_routing_execution_policy(
        "Research a topic and write an executive summary.",
        team,
        route_type="team",
    )
    decision = apply_safe_execution_policy_enforcement(
        decision,
        final_decision={"action": "run_workflow"},
    )

    assert decision["recommended_execution_tier"] == "premium_external_candidate"
    assert decision["safe_enforcement"]["enforced"] is False
    assert decision["safe_enforcement"]["scope"] == "observe_only"


def test_runtime_files_apply_safe_enforcement_to_trace_surfaces():
    root = Path(__file__).resolve().parents[1]

    assistant_source = (root / "orchgentic" / "agents" / "assistant.py").read_text()
    cli_source = (root / "orchgentic" / "cli.py").read_text()
    team_source = (root / "orchgentic" / "orchestration" / "team_runner.py").read_text()

    assert "apply_safe_execution_policy_enforcement" in assistant_source
    assert "apply_safe_execution_policy_enforcement" in cli_source
    assert "apply_safe_execution_policy_enforcement" in team_source

    assert "execution_policy.classified" in assistant_source
    assert "execution_policy.classified" in cli_source
    assert "execution_policy.classified" in team_source
