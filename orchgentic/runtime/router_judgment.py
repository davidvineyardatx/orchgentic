from dataclasses import asdict
from typing import Any

from orchgentic.runtime.local_reasoner import LocalReasoner
from orchgentic.runtime.escalation import EscalationDecision, EscalationEngine, default_escalation_policy
from orchgentic.runtime.execution_policy import classify_routing_execution_policy, apply_safe_execution_policy_enforcement
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

    execution_policy = classify_routing_execution_policy(
        task,
        cfg,
        local_decision=local_decision,
        escalation=escalation,
        final_decision=final,
    )
    execution_policy = apply_safe_execution_policy_enforcement(
        execution_policy,
        final_decision=final,
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
        "execution_policy": execution_policy,
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


def format_orchestration_judgment_for_cli(judgment: dict) -> dict:
    """Return a human-oriented view of orchestration judgment output.

    The internal judgment keeps the full workflow router object for traces and
    tests. CLI output can be clearer for single-agent runs where workflow
    orchestration is not applicable.
    """

    formatted = dict(judgment)
    workflow = judgment.get("workflow")

    if isinstance(workflow, dict) and workflow.get("should_use_workflow") is False:
        formatted["workflow"] = {
            "applicable": False,
            "reason": "Not applicable for single-agent routing.",
            "workflow_type": None,
        }

    return formatted


def summarize_orchestration_judgment(judgment: dict) -> dict:
    """Return a compact policy/routing summary for CLI and report output."""

    local_reasoner = judgment.get("local_reasoner", {}) or {}
    workflow = judgment.get("workflow", {}) or {}
    policy = judgment.get("policy", {}) or {}
    execution_policy = judgment.get("execution_policy", {}) or {}
    safe_enforcement = execution_policy.get("safe_enforcement", {}) or {}
    enforcement_summary = execution_policy.get("enforcement_summary", {}) or {}
    escalation = judgment.get("escalation", {}) or {}
    final_decision = judgment.get("final_decision", {}) or {}

    workflow_applicable = bool(workflow.get("should_use_workflow")) if isinstance(workflow, dict) else False
    if isinstance(workflow, dict) and "applicable" in workflow:
        workflow_applicable = bool(workflow.get("applicable"))

    return {
        "route": {
            "final_action": final_decision.get("action"),
            "intent": local_reasoner.get("intent"),
            "confidence": final_decision.get("confidence", local_reasoner.get("confidence")),
            "external_llm_allowed": final_decision.get("external_llm_allowed"),
            "external_llm_escalated": bool(escalation.get("escalate")),
        },
        "workflow": {
            "applicable": workflow_applicable,
            "workflow_type": workflow.get("workflow_type") if isinstance(workflow, dict) else None,
            "reason": workflow.get("reason") if isinstance(workflow, dict) else None,
        },
        "tool_policy": {
            "action": policy.get("action"),
            "allowed": policy.get("allowed"),
            "reason": policy.get("reason"),
            "affected_tools": list(policy.get("affected_tools") or []),
            "require_confirmation": bool(policy.get("require_confirmation")),
        },
        "execution_policy": {
            "purpose": execution_policy.get("purpose"),
            "recommended_execution_tier": execution_policy.get("recommended_execution_tier"),
            "policy_action": execution_policy.get("policy_action"),
            "advisory": execution_policy.get("advisory"),
            "full_policy_enforced": enforcement_summary.get("full_policy_enforced", execution_policy.get("enforced")),
            "safe_enforcement_applied": enforcement_summary.get("safe_enforcement_applied", safe_enforcement.get("enforced")),
            "safe_enforcement_scope": safe_enforcement.get("scope"),
            "enforcement_mode": enforcement_summary.get("mode"),
            "enforcement_status": enforcement_summary.get("status"),
            "reason": execution_policy.get("reason"),
        },
    }


def format_orchestration_summary_text(summary: dict) -> str:
    """Format a compact human-readable route/policy summary."""

    route = summary.get("route", {}) or {}
    workflow = summary.get("workflow", {}) or {}
    tool_policy = summary.get("tool_policy", {}) or {}
    execution_policy = summary.get("execution_policy", {}) or {}

    lines = [
        "ROUTE SUMMARY",
        f"- Final action: {route.get('final_action')}",
        f"- Intent: {route.get('intent')}",
        f"- Confidence: {route.get('confidence')}",
        f"- External LLM escalated: {route.get('external_llm_escalated')}",
        "",
        "WORKFLOW",
        f"- Applicable: {workflow.get('applicable')}",
        f"- Type: {workflow.get('workflow_type')}",
    ]
    if workflow.get("reason"):
        lines.append(f"- Reason: {workflow.get('reason')}")

    lines.extend(
        [
            "",
            "TOOL POLICY",
            f"- Action: {tool_policy.get('action')}",
            f"- Allowed: {tool_policy.get('allowed')}",
            f"- Requires confirmation: {tool_policy.get('require_confirmation')}",
        ]
    )
    affected_tools = tool_policy.get("affected_tools") or []
    if affected_tools:
        lines.append(f"- Affected tools: {', '.join(affected_tools)}")
    if tool_policy.get("reason"):
        lines.append(f"- Reason: {tool_policy.get('reason')}")

    lines.extend(
        [
            "",
            "EXECUTION POLICY",
            f"- Purpose: {execution_policy.get('purpose')}",
            f"- Recommended tier: {execution_policy.get('recommended_execution_tier')}",
            f"- Policy action: {execution_policy.get('policy_action')}",
            f"- Enforcement mode: {execution_policy.get('enforcement_mode')}",
            f"- Enforcement status: {execution_policy.get('enforcement_status')}",
            f"- Safe enforcement applied: {execution_policy.get('safe_enforcement_applied')}",
            f"- Full policy enforced: {execution_policy.get('full_policy_enforced')}",
        ]
    )
    if execution_policy.get("safe_enforcement_scope"):
        lines.append(f"- Safe enforcement scope: {execution_policy.get('safe_enforcement_scope')}")
    if execution_policy.get("reason"):
        lines.append(f"- Reason: {execution_policy.get('reason')}")

    return "\n".join(lines)
