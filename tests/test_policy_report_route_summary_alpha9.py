from pathlib import Path

from orchgentic.config.schemas import AgentConfig
from orchgentic.runtime.router_judgment import (
    evaluate_orchestration_judgment,
    format_orchestration_summary_text,
    summarize_orchestration_judgment,
)


def test_route_summary_includes_policy_and_enforcement_fields():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    summary = summarize_orchestration_judgment(judgment)

    assert summary["route"]["final_action"] == "answer_locally"
    assert summary["route"]["intent"] == "datetime"
    assert summary["workflow"]["applicable"] is False
    assert summary["tool_policy"]["action"] == "allow"
    assert summary["execution_policy"]["recommended_execution_tier"] == "deterministic_saved"
    assert summary["execution_policy"]["policy_action"] == "deterministic_allowed"
    assert summary["execution_policy"]["safe_enforcement_applied"] is True
    assert summary["execution_policy"]["full_policy_enforced"] is False
    assert summary["execution_policy"]["enforcement_mode"] == "safe_deterministic_only"


def test_route_summary_text_is_human_readable():
    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    text = format_orchestration_summary_text(summarize_orchestration_judgment(judgment))

    assert "ROUTE SUMMARY" in text
    assert "WORKFLOW" in text
    assert "TOOL POLICY" in text
    assert "EXECUTION POLICY" in text
    assert "Final action: answer_locally" in text
    assert "Recommended tier: deterministic_saved" in text
    assert "Enforcement mode: safe_deterministic_only" in text


def test_generation_summary_remains_observe_only():
    judgment = evaluate_orchestration_judgment(
        "Write a short summary of Orchgentic",
        cfg=AgentConfig(id="bob", name="Bob"),
    )

    summary = summarize_orchestration_judgment(judgment)

    assert summary["route"]["final_action"] == "call_llm"
    assert summary["execution_policy"]["safe_enforcement_applied"] is False
    assert summary["execution_policy"]["enforcement_mode"] == "observe_only"


def test_cli_contains_judge_route_summary_and_policy_report_commands():
    root = Path(__file__).resolve().parents[1]
    cli_source = (root / "orchgentic" / "cli.py").read_text()

    assert '--summary' in cli_source
    assert '@app.command("policy-report")' in cli_source
    assert 'summarize_orchestration_judgment' in cli_source
    assert 'format_orchestration_summary_text' in cli_source
