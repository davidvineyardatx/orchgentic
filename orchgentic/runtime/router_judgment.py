from dataclasses import asdict
from typing import Any

from orchgentic.runtime.local_reasoner import LocalReasoner
from orchgentic.runtime.escalation import EscalationDecision, EscalationEngine, default_escalation_policy
from orchgentic.core.routing import (
    EventContext,
    EventContextRouter,
    PolicyRouter,
    RoutingAction,
    RoutingDecision,
    WorkflowRouter,
)


def _registry_tools(registry=None) -> list[str]:
    if registry is None:
        return []
    for attr in ("items", "tools", "_tools"):
        try:
            value = getattr(registry, attr)
            if isinstance(value, dict):
                return list(value.keys())
        except Exception:
            pass
    try:
        return list(registry.list())
    except Exception:
        return []


def evaluate_orchestration_judgment(task: str, cfg=None, registry=None, event_context: dict[str, Any] | EventContext | None = None) -> dict:
    available_tools = _registry_tools(registry)

    reasoner = LocalReasoner()
    local_decision = reasoner.classify(task, available_tools=available_tools)

    workflow_route = WorkflowRouter().classify(task, available_tools=available_tools)
    event_route = EventContextRouter().classify(event_context)

    candidate_tools = list(workflow_route.required_tools or [])
    if local_decision.intent == "datetime":
        candidate_tools.append("datetime.local")

    policy_route = PolicyRouter().evaluate(
        task,
        agent_config=cfg,
        candidate_tools=candidate_tools,
        event_route=event_route,
    )

    provider_cfg = getattr(cfg, "provider", None) if cfg is not None else None
    escalation = EscalationEngine(default_escalation_policy()).decide(local_decision, provider_config=provider_cfg)
    escalation = _apply_policy_to_escalation(escalation, policy_route)

    final = _final_decision(
        local_decision=local_decision,
        escalation=escalation,
        workflow_route=workflow_route,
        event_route=event_route,
        policy_route=policy_route,
    )

    return {
        "local_reasoner": {
            "intent": local_decision.intent,
            "reasoning_level": local_decision.reasoning_level.value,
            "complexity": local_decision.complexity.value,
            "confidence": local_decision.confidence,
            "should_escalate": local_decision.should_escalate,
            "escalation_reason": local_decision.escalation_reason,
            "signals": local_decision.signals,
        },
        "workflow": workflow_route.to_dict(),
        "event_context": event_route.to_dict(),
        "policy": policy_route.to_dict(),
        "escalation": asdict(escalation),
        "final_decision": final.to_dict(),
    }


def _apply_policy_to_escalation(escalation, policy_route) -> EscalationDecision:
    """Make escalation telemetry obey policy routing.

    Policy decisions are authoritative. If a tool is blocked or waiting on
    confirmation, the judgment should not imply that an external provider will
    still be called. This keeps debug output aligned with the final decision.
    """
    if getattr(policy_route, "action", None) == "block":
        return EscalationDecision(
            False,
            "Policy blocked execution before escalation.",
            selected_provider=None,
            selected_model=None,
            reasoning_depth="none",
            metadata={
                "suppressed_by_policy": True,
                "policy_action": policy_route.action,
                "affected_tools": list(getattr(policy_route, "affected_tools", []) or []),
            },
        )

    if getattr(policy_route, "action", None) == "hold_for_confirmation":
        return EscalationDecision(
            False,
            "Policy requires confirmation before escalation.",
            selected_provider=None,
            selected_model=None,
            reasoning_depth="none",
            metadata={
                "suppressed_by_policy": True,
                "policy_action": policy_route.action,
                "affected_tools": list(getattr(policy_route, "affected_tools", []) or []),
                "require_confirmation": True,
            },
        )

    return escalation


def _final_decision(*, local_decision, escalation, workflow_route, event_route, policy_route) -> RoutingDecision:
    if policy_route.action == "block":
        return RoutingDecision(
            RoutingAction.BLOCK,
            policy_route.reason,
            confidence=policy_route.confidence,
            workflow_type=workflow_route.workflow_type,
            event_type=event_route.event_type,
            external_llm_allowed=False,
            metadata={"affected_tools": policy_route.affected_tools},
        )

    if policy_route.action == "hold_for_confirmation":
        return RoutingDecision(
            RoutingAction.HOLD_FOR_CONFIRMATION,
            policy_route.reason,
            confidence=policy_route.confidence,
            workflow_type=workflow_route.workflow_type,
            event_type=event_route.event_type,
            external_llm_allowed=False,
            metadata={"affected_tools": policy_route.affected_tools},
        )

    if workflow_route.should_use_workflow and escalation.escalate:
        return RoutingDecision(
            RoutingAction.RUN_WORKFLOW,
            "Workflow-aware routing selected a multi-step path with LLM assistance.",
            confidence=min(workflow_route.confidence, 0.92),
            workflow_type=workflow_route.workflow_type,
            event_type=event_route.event_type,
            external_llm_allowed=True,
            metadata={"estimated_steps": workflow_route.estimated_steps, "required_tools": workflow_route.required_tools},
        )

    if escalation.escalate:
        return RoutingDecision(
            RoutingAction.CALL_LLM,
            escalation.reason,
            confidence=float((escalation.metadata or {}).get("confidence", 0.0)),
            workflow_type=workflow_route.workflow_type,
            event_type=event_route.event_type,
            external_llm_allowed=True,
        )

    return RoutingDecision(
        RoutingAction.ANSWER_LOCALLY,
        "Local/deterministic path sufficient.",
        confidence=float(getattr(local_decision, "confidence", 0.0) or 0.0),
        workflow_type=workflow_route.workflow_type,
        event_type=event_route.event_type,
        external_llm_allowed=False,
    )
