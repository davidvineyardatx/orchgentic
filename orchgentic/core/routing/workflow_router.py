from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import re


class WorkflowType(str, Enum):
    SINGLE_STEP = "single_step"
    TOOL_CHAIN = "tool_chain"
    RESEARCH_SYNTHESIS = "research_synthesis"
    TEAM_WORKFLOW = "team_workflow"
    MANUAL_REVIEW = "manual_review"


@dataclass(slots=True)
class WorkflowRoute:
    workflow_type: str
    should_use_workflow: bool
    confidence: float
    estimated_steps: int = 1
    required_tools: list[str] = field(default_factory=list)
    required_agents: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WorkflowRouter:
    """Classifies whether a task is a simple request or a workflow.

    This router is intentionally conservative. It does not execute workflow
    decisions by itself; it annotates the route so the runtime can avoid
    treating multi-step work as a single flat prompt.
    """

    TOOL_TERMS: dict[str, list[str]] = {
        "web.request": ["research", "fetch", "browse", "url", "http", "website", "online"],
        "knowledge.search": ["knowledge", "docs", "documentation", "known", "stored"],
        "memory.search": ["memory", "remember", "previous", "earlier"],
        "gmail.search": ["search gmail", "find email", "list email", "unread email"],
        "gmail.delete": ["delete gmail", "delete email", "delete message", "trash gmail", "trash email", "trash message", "remove email", "remove message"],
        "gmail.reply": ["reply to email", "reply to gmail", "respond to email"],
        "gmail.draft": ["draft email", "draft a reply", "draft response"],
        "gmail.send": ["send email", "email to"],
        "gmail.read": ["read gmail", "read email", "message id"],
    }

    MULTI_STEP_CONNECTORS = [" and then ", " then ", " after that ", " before you ", " once you ", ";"]
    TEAM_TERMS = ["team", "delegate", "handoff", "reviewer", "writer", "researcher", "manager"]
    REVIEW_TERMS = ["approval", "approve", "confirmation", "confirm", "review before", "human review"]

    def classify(self, task: str, *, available_tools: list[str] | None = None, team_agents: list[str] | None = None) -> WorkflowRoute:
        text = (task or "").strip().lower()
        available_tools = available_tools or []
        team_agents = team_agents or []

        if not text:
            return WorkflowRoute("single_step", False, 0.0, reasons=["empty_task"])

        required_tools = self._required_tools(text, available_tools)
        reasons: list[str] = []
        estimated_steps = 1

        connector_count = sum(1 for term in self.MULTI_STEP_CONNECTORS if term in text)
        if connector_count:
            estimated_steps += connector_count
            reasons.append("multi_step_language")

        if len(required_tools) > 1:
            estimated_steps = max(estimated_steps, len(required_tools))
            reasons.append("multiple_tools_required")

        has_research_action = any(term in text for term in ["research", "fetch", "browse", "look up", "find sources", "online"])
        has_synthesis_output = any(term in text for term in ["summarize", "summary", "executive summary", "report"])
        has_generation = any(term in text for term in ["write", "draft", "compose", "create", "generate"])
        if has_research_action and (has_generation or has_synthesis_output):
            reasons.append("research_plus_generation")
            estimated_steps = max(estimated_steps, 3)
            return WorkflowRoute(
                WorkflowType.RESEARCH_SYNTHESIS.value,
                True,
                0.88,
                estimated_steps=estimated_steps,
                required_tools=required_tools,
                reasons=reasons,
                metadata={"has_research_action": has_research_action, "has_synthesis_output": has_synthesis_output, "has_generation": has_generation},
            )

        if any(term in text for term in self.TEAM_TERMS) or team_agents:
            required_agents = [agent for agent in team_agents if agent.lower() in text]
            return WorkflowRoute(
                WorkflowType.TEAM_WORKFLOW.value,
                True,
                0.84,
                estimated_steps=max(estimated_steps, 2),
                required_tools=required_tools,
                required_agents=required_agents,
                reasons=reasons + ["team_or_delegation_signal"],
            )

        if any(term in text for term in self.REVIEW_TERMS):
            return WorkflowRoute(
                WorkflowType.MANUAL_REVIEW.value,
                True,
                0.82,
                estimated_steps=max(estimated_steps, 2),
                required_tools=required_tools,
                reasons=reasons + ["manual_review_signal"],
            )

        if estimated_steps > 1 or len(required_tools) > 1:
            return WorkflowRoute(
                WorkflowType.TOOL_CHAIN.value,
                True,
                0.80,
                estimated_steps=estimated_steps,
                required_tools=required_tools,
                reasons=reasons or ["tool_chain_signal"],
            )

        return WorkflowRoute(
            WorkflowType.SINGLE_STEP.value,
            False,
            0.74,
            estimated_steps=1,
            required_tools=required_tools,
            reasons=["single_step_or_generation"],
        )

    def _required_tools(self, text: str, available_tools: list[str]) -> list[str]:
        required: list[str] = []
        available = set(available_tools or [])

        dominant_tool = self._dominant_action_tool(text)
        if dominant_tool and (not available or dominant_tool in available):
            required.append(dominant_tool)

        for tool, terms in self.TOOL_TERMS.items():
            if available and tool not in available:
                continue
            if tool in required:
                continue
            if dominant_tool and tool == "gmail.read":
                # Object identifiers like "message id" may appear in destructive or
                # side-effecting requests. Keep the dominant action as the workflow tool.
                continue
            if any(term in text for term in terms):
                required.append(tool)

        # Preserve explicit tool mentions even if they are not in TOOL_TERMS.
        for tool in available_tools or []:
            if re.search(r"\b" + re.escape(tool.lower()) + r"\b", text) and tool not in required:
                required.append(tool)
        return required

    def _dominant_action_tool(self, text: str) -> str | None:
        has_gmail_object = bool(re.search(r"\b(gmail|email|message)\b", text))
        has_email_address = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text))

        if has_gmail_object and re.search(r"\b(delete|trash|remove)\b", text):
            return "gmail.delete"
        if (has_gmail_object or has_email_address) and re.search(r"\bsend\b", text):
            return "gmail.send"
        if has_gmail_object and re.search(r"\b(reply|respond)\b", text):
            return "gmail.reply"
        if has_gmail_object and re.search(r"\bdraft\b", text):
            return "gmail.draft"
        return None
