from orchgentic.core.reasoning.confidence import ConfidenceBand, ConfidenceScorer
from orchgentic.core.reasoning.escalation import EscalationAction
from orchgentic.core.reasoning.local_reasoner import LocalDecision, LocalMiniReasoner
from orchgentic.core.reasoning.runtime_hooks import preflight_reasoning


def test_local_reasoner_handles_safe_math_locally():
    result = LocalMiniReasoner().evaluate("what is 67-9?")
    assert result.decision == LocalDecision.ANSWER_LOCALLY
    assert result.local_answer == "58"
    assert result.confidence >= 0.95


def test_confidence_scorer_lowers_score_for_missing_tools():
    score = ConfidenceScorer().score(local_confidence=0.70, missing_tools=["web.request", "memory.search"])
    assert score.score < 0.70
    assert "missing_tools_present" in score.reasons


def test_preflight_uses_configured_provider_path_without_provider_override():
    agent_config = {
        "provider": {"type": "groq", "model": "llama-3.3-70b-versatile"},
        "reasoning": {
            "planner": True,
            "reflection": True,
            "local_reasoner": True,
            "confidence_scoring": True,
            "confidence_high_threshold": 0.78,
            "confidence_low_threshold": 0.52,
            "escalation": {"enabled": True, "min_confidence": 0.52},
        },
    }
    result = preflight_reasoning("Help me build code for a new feature", agent_config=agent_config)
    assert result.escalation.action == EscalationAction.CALL_LLM
    assert not hasattr(result.escalation, "provider_type")
    assert not hasattr(result.escalation, "model")


def test_preflight_can_answer_locally_without_llm():
    agent_config = {"reasoning": {"local_reasoner": True, "confidence_scoring": True, "escalation": {"enabled": True}}}
    result = preflight_reasoning("hello", agent_config=agent_config)
    assert result.local_result.local_answer
    assert result.escalation.action == EscalationAction.NONE


def test_deterministic_router_recognizes_local_time_variants():
    from orchgentic.runtime.deterministic_router import DeterministicRouter

    router = DeterministicRouter()
    variants = [
        "what is the local time?",
        "what is local time?",
        "local time",
        "current local time",
    ]

    for task in variants:
        decision = router.route(task)
        assert decision.matched is True
        assert decision.requires_llm is False
        assert decision.tool == "datetime.local"


def test_orchestration_judgment_counts_registry_items_for_local_time():
    from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment

    class DummyRegistry:
        items = {"datetime.local": object(), "datetime.now": object()}

    judgment = evaluate_orchestration_judgment(
        "what is the local time?",
        registry=DummyRegistry(),
    )

    assert judgment["local_reasoner"]["signals"]["available_tool_count"] > 0
    assert judgment["local_reasoner"]["intent"] == "datetime"
    assert judgment["local_reasoner"]["should_escalate"] is False


def test_deterministic_datetime_formatter_uses_12_hour_clock():
    from orchgentic.runtime.deterministic_formatter import DeterministicFormatter

    formatted = DeterministicFormatter().format(
        "datetime.local",
        {
            "time": "18:31:45",
            "date": "2026-06-11",
            "weekday": "Thursday",
            "timezone": "America/Chicago",
        },
    )

    assert "6:31:45 PM" in formatted
    assert "18:31:45" not in formatted


def test_time_context_includes_12_hour_clock_field():
    from orchgentic.runtime.time_context import TimeContextResolver

    data = TimeContextResolver().now_local("America/Chicago", locale="en-US")

    assert "time_12h" in data
    assert data["time_12h"].endswith(("AM", "PM"))
