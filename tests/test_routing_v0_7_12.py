from orchgentic.config.schemas import AgentConfig
from orchgentic.core.routing import EventContext, EventContextRouter, PolicyRouter, WorkflowRouter
from orchgentic.runtime.router_judgment import evaluate_orchestration_judgment


def test_workflow_router_detects_research_synthesis():
    route = WorkflowRouter().classify(
        "Research how AI is changing shopping and write an executive summary",
        available_tools=["web.request", "knowledge.search"],
    )
    assert route.should_use_workflow is True
    assert route.workflow_type == "research_synthesis"
    assert route.estimated_steps >= 3


def test_event_context_router_marks_heartbeat_as_autonomous():
    route = EventContextRouter().classify(EventContext(event_type="heartbeat", source="trigger"))
    assert route.autonomy == "autonomous_scheduled"
    assert route.require_extra_policy_checks is True


def test_policy_router_blocks_disabled_gmail_delete_before_llm():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        tool_policies={"gmail.delete": {"enabled": False, "require_confirmation": True}},
    )
    route = PolicyRouter().evaluate("delete gmail message id abcdef123456", agent_config=agent)
    assert route.action == "block"
    assert route.allowed is False
    assert route.external_llm_allowed is False


def test_policy_router_holds_gmail_send_without_confirmation():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        tool_policies={
            "gmail.send": {
                "enabled": True,
                "require_confirmation": True,
                "send_policy": {
                    "mode": "restricted",
                    "allowed_addresses": ["studio@davidvineyard.com"],
                    "allowed_domains": [],
                    "require_confirmation": True,
                },
            }
        },
    )
    route = PolicyRouter().evaluate(
        'send email to studio@davidvineyard.com subject="Hi" body="Test"',
        agent_config=agent,
    )
    assert route.action == "hold_for_confirmation"
    assert route.require_confirmation is True
    assert route.external_llm_allowed is False


def test_policy_router_blocks_disallowed_gmail_recipient():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        tool_policies={
            "gmail.send": {
                "enabled": True,
                "send_policy": {
                    "mode": "restricted",
                    "allowed_addresses": ["studio@davidvineyard.com"],
                    "allowed_domains": [],
                    "require_confirmation": True,
                },
            }
        },
    )
    route = PolicyRouter().evaluate(
        'send email to stranger@example.com subject="Hi" body="Test" confirm=true',
        agent_config=agent,
    )
    assert route.action == "block"
    assert "not allowed" in route.reason


def test_orchestration_judgment_includes_workflow_event_policy_and_final_decision():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        tool_policies={"gmail.delete": {"enabled": False, "require_confirmation": True}},
    )
    judgment = evaluate_orchestration_judgment(
        "delete gmail message id abcdef123456",
        cfg=agent,
        event_context={"event_type": "manual", "source": "test"},
    )
    assert "workflow" in judgment
    assert "event_context" in judgment
    assert "policy" in judgment
    assert "final_decision" in judgment
    assert judgment["policy"]["action"] == "block"
    assert judgment["final_decision"]["action"] == "block"


def test_generation_request_still_uses_default_provider_path():
    agent = AgentConfig(id="bob", name="Bob")
    judgment = evaluate_orchestration_judgment(
        "Write a short summary of Orchgentic",
        cfg=agent,
        event_context={"event_type": "manual", "source": "test"},
    )
    assert judgment["final_decision"]["action"] == "call_llm"
    assert judgment["escalation"]["selected_provider"] == agent.provider.type
    assert judgment["escalation"]["selected_model"] == agent.provider.model


def test_local_reasoner_classifies_gmail_delete_before_read():
    judgment = evaluate_orchestration_judgment(
        "delete gmail message id abcdef123456",
        cfg=AgentConfig(
            id="bob",
            name="Bob",
            tool_policies={"gmail.delete": {"enabled": False, "require_confirmation": True}},
        ),
        event_context={"event_type": "manual", "source": "test"},
    )
    assert judgment["local_reasoner"]["intent"] == "gmail_delete"
    assert "gmail_delete" in judgment["local_reasoner"]["signals"]["simple_intents"]


def test_policy_block_suppresses_escalation_telemetry():
    judgment = evaluate_orchestration_judgment(
        "delete gmail message id abcdef123456",
        cfg=AgentConfig(
            id="bob",
            name="Bob",
            tool_policies={"gmail.delete": {"enabled": False, "require_confirmation": True}},
        ),
        event_context={"event_type": "manual", "source": "test"},
    )
    assert judgment["policy"]["action"] == "block"
    assert judgment["escalation"]["escalate"] is False
    assert judgment["escalation"]["selected_provider"] is None
    assert judgment["escalation"]["selected_model"] is None
    assert judgment["escalation"]["metadata"]["suppressed_by_policy"] is True


def test_policy_hold_suppresses_escalation_telemetry():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        tool_policies={
            "gmail.send": {
                "enabled": True,
                "require_confirmation": True,
                "send_policy": {
                    "mode": "restricted",
                    "allowed_addresses": ["studio@davidvineyard.com"],
                    "allowed_domains": [],
                    "require_confirmation": True,
                },
            }
        },
    )
    judgment = evaluate_orchestration_judgment(
        "send an email to studio@davidvineyard.com saying hello",
        cfg=agent,
        event_context={"event_type": "manual", "source": "test"},
    )
    assert judgment["policy"]["action"] == "hold_for_confirmation"
    assert judgment["escalation"]["escalate"] is False
    assert judgment["escalation"]["selected_provider"] is None
    assert judgment["escalation"]["selected_model"] is None
    assert judgment["escalation"]["metadata"]["require_confirmation"] is True


def test_workflow_router_prefers_delete_over_message_id_read():
    route = WorkflowRouter().classify(
        "delete gmail message id abcdef123456",
        available_tools=["gmail.read", "gmail.delete"],
    )
    assert route.required_tools == ["gmail.delete"]


def test_local_reasoner_delete_intent_does_not_include_read():
    judgment = evaluate_orchestration_judgment(
        "delete gmail message id abcdef123456",
        cfg=AgentConfig(
            id="bob",
            name="Bob",
            tool_policies={"gmail.delete": {"enabled": False, "require_confirmation": True}},
        ),
        event_context={"event_type": "manual", "source": "test"},
    )
    assert judgment["local_reasoner"]["intent"] == "gmail_delete"
    assert judgment["local_reasoner"]["signals"]["simple_intents"] == ["gmail_delete"]
    assert judgment["workflow"]["required_tools"] == ["gmail.delete"]
