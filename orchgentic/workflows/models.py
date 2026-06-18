from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class WorkflowValidationError(ValueError):
    """Raised when a workflow blueprint is missing required shape."""


@dataclass(slots=True)
class WorkflowStep:
    id: str
    name: str = ""
    actor: str | None = None
    execution_tier: str | None = None
    action: str | None = None
    optimization: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowStep":
        if not isinstance(data, dict):
            raise WorkflowValidationError("Workflow step must be a mapping.")
        step_id = str(data.get("id") or "").strip()
        if not step_id:
            raise WorkflowValidationError("Workflow step is missing required field: id")
        return cls(
            id=step_id,
            name=str(data.get("name") or step_id),
            actor=data.get("actor"),
            execution_tier=data.get("execution_tier"),
            action=data.get("action"),
            optimization=data.get("optimization") or data.get("optimization_opportunity"),
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "actor": self.actor,
            "execution_tier": self.execution_tier,
            "action": self.action,
            "optimization": self.optimization,
            "raw": self.raw,
        }


@dataclass(slots=True)
class WorkflowBlueprint:
    id: str
    name: str
    version: str = "0.1.0"
    status: str = "blueprint"
    description: str = ""
    purpose: str = ""
    team: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)
    execution_policy: dict[str, Any] = field(default_factory=dict)
    steps: list[WorkflowStep] = field(default_factory=list)
    observability: dict[str, Any] = field(default_factory=dict)
    expected_token_story: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    @property
    def team_name(self) -> str | None:
        team = self.team or {}
        return team.get("name") or team.get("id")

    @property
    def default_task(self) -> str | None:
        task_input = (self.inputs or {}).get("task") or {}
        if isinstance(task_input, dict):
            value = task_input.get("default")
            return str(value) if value else None
        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, path: str | Path | None = None) -> "WorkflowBlueprint":
        if not isinstance(data, dict):
            raise WorkflowValidationError("Workflow file must be a mapping.")
        root = data.get("workflow")
        if not isinstance(root, dict):
            raise WorkflowValidationError("Invalid workflow config. Missing 'workflow' key.")

        workflow_id = str(root.get("id") or "").strip()
        if not workflow_id:
            raise WorkflowValidationError("Workflow is missing required field: workflow.id")
        name = str(root.get("name") or workflow_id).strip()
        team = root.get("team") or {}
        if not isinstance(team, dict):
            raise WorkflowValidationError("Workflow team must be a mapping.")
        if not (team.get("name") or team.get("id")):
            raise WorkflowValidationError("Workflow is missing required field: workflow.team.name or workflow.team.id")

        steps_data = root.get("steps") or []
        if not isinstance(steps_data, list):
            raise WorkflowValidationError("Workflow steps must be a list.")
        steps = [WorkflowStep.from_dict(item) for item in steps_data]
        if not steps:
            raise WorkflowValidationError("Workflow must define at least one step.")

        return cls(
            id=workflow_id,
            name=name,
            version=str(root.get("version") or "0.1.0"),
            status=str(root.get("status") or "blueprint"),
            description=str(root.get("description") or ""),
            purpose=str(root.get("purpose") or ""),
            team=team,
            inputs=root.get("inputs") or {},
            execution_policy=root.get("execution_policy") or {},
            steps=steps,
            observability=root.get("observability") or {},
            expected_token_story=root.get("expected_token_story") or {},
            raw=root,
            path=Path(path) if path else None,
        )

    def metadata(self) -> dict[str, Any]:
        return {
            "workflow_id": self.id,
            "workflow_name": self.name,
            "workflow_version": self.version,
            "workflow_status": self.status,
            "workflow_team": self.team_name,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "description": self.description,
            "purpose": self.purpose,
            "team": self.team,
            "inputs": self.inputs,
            "execution_policy": self.execution_policy,
            "steps": [step.to_dict() for step in self.steps],
            "observability": self.observability,
            "expected_token_story": self.expected_token_story,
            "path": str(self.path) if self.path else None,
        }
