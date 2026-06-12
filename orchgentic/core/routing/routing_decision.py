from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class RoutingAction(str, Enum):
    ANSWER_LOCALLY = "answer_locally"
    EXECUTE_TOOL = "execute_tool"
    CALL_LLM = "call_llm"
    RUN_WORKFLOW = "run_workflow"
    HOLD_FOR_CONFIRMATION = "hold_for_confirmation"
    BLOCK = "block"


@dataclass(slots=True)
class RoutingDecision:
    action: RoutingAction
    reason: str
    confidence: float = 0.0
    selected_tool: str | None = None
    workflow_type: str | None = None
    event_type: str = "manual"
    external_llm_allowed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["action"] = self.action.value
        return data
