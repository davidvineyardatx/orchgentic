from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from .models import WorkflowBlueprint, WorkflowStep, WorkflowValidationError
from .registry import WorkflowRegistry


REQUIRED_WORKFLOW_METADATA_KEYS = [
    "workflow_id",
    "workflow_name",
    "workflow_version",
    "workflow_status",
    "workflow_team",
]

RECOMMENDED_WORKFLOW_EVENTS = [
    "run.started",
    "workflow.step.planned",
    "workflow.step.completed",
    "run.completed",
]

TEAM_MEMBER_WARNING_THRESHOLD = 2


def _error(field: str, code: str, message: str) -> dict[str, str]:
    return {"field": field, "code": code, "message": message}


def _warning(field: str, code: str, message: str) -> dict[str, str]:
    return {"field": field, "code": code, "message": message}


def load_workflow_contract(source: WorkflowBlueprint | dict[str, Any] | str | Path) -> WorkflowBlueprint:
    """Load a workflow contract from a blueprint object, dict, or YAML path."""

    if isinstance(source, WorkflowBlueprint):
        return source

    if isinstance(source, (str, Path)):
        path = Path(source)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return WorkflowBlueprint.from_dict(data, path=path)

    return WorkflowBlueprint.from_dict(source)


def validate_workflow_contract(source: WorkflowBlueprint | dict[str, Any] | str | Path) -> dict[str, Any]:
    """Validate the stable workflow contract shape without running a workflow."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    try:
        workflow = load_workflow_contract(source)
    except WorkflowValidationError as exc:
        return {
            "valid": False,
            "status": "invalid",
            "errors": [_error("workflow", "invalid_workflow_shape", str(exc))],
            "warnings": [],
            "runtime_behavior_changed": False,
        }

    if not workflow.id:
        errors.append(_error("workflow.id", "missing_workflow_id", "Workflow id is required."))
    if not workflow.name:
        errors.append(_error("workflow.name", "missing_workflow_name", "Workflow name is required."))
    if not workflow.version:
        warnings.append(_warning("workflow.version", "missing_workflow_version", "Workflow version should be set."))

    team = workflow.team or {}
    team_name = team.get("name") or team.get("id")
    if not team_name:
        errors.append(_error("workflow.team", "missing_team", "Workflow must be team-backed with team.name or team.id."))

    members = team.get("members") or []
    if members and not isinstance(members, list):
        errors.append(_error("workflow.team.members", "invalid_team_members", "Workflow team.members must be a list when provided."))
    elif len(members) == 1:
        errors.append(_error("workflow.team.members", "single_agent_workflow_not_supported", "Workflow should not be modeled as a one-agent team."))
    elif len(members) < TEAM_MEMBER_WARNING_THRESHOLD:
        warnings.append(_warning("workflow.team.members", "team_members_not_declared", "Workflow should declare team members for inspectable team-backed execution."))

    if not workflow.steps:
        errors.append(_error("workflow.steps", "missing_steps", "Workflow must define at least one step."))

    seen_steps: set[str] = set()
    for index, step in enumerate(workflow.steps):
        path = f"workflow.steps[{index}]"
        if step.id in seen_steps:
            errors.append(_error(f"{path}.id", "duplicate_step_id", f"Duplicate workflow step id: {step.id}"))
        seen_steps.add(step.id)

        if not step.actor:
            warnings.append(_warning(f"{path}.actor", "missing_step_actor", f"Step {step.id} should declare an actor."))
        if not step.action:
            warnings.append(_warning(f"{path}.action", "missing_step_action", f"Step {step.id} should declare an action."))
        if not step.execution_tier:
            warnings.append(_warning(f"{path}.execution_tier", "missing_step_execution_tier", f"Step {step.id} should declare an execution tier."))

    metadata = workflow.metadata()
    missing_metadata = [key for key in REQUIRED_WORKFLOW_METADATA_KEYS if key not in metadata]
    for key in missing_metadata:
        errors.append(_error(f"metadata.{key}", "missing_workflow_metadata", f"Workflow metadata missing {key}."))

    trace_contract = workflow_trace_contract(workflow)

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "workflow_id": workflow.id,
        "workflow_name": workflow.name,
        "workflow_version": workflow.version,
        "workflow_status": workflow.status,
        "team_backed": bool(team_name),
        "team_name": team_name,
        "team_member_count": len(members) if isinstance(members, list) else 0,
        "step_count": len(workflow.steps),
        "steps": [step.to_dict() for step in workflow.steps],
        "trace_contract": trace_contract,
        "runtime_behavior_changed": False,
    }


def workflow_trace_contract(workflow: WorkflowBlueprint) -> dict[str, Any]:
    """Return stable trace metadata expectations for a workflow."""

    expected_step_events = [
        {
            "step_id": step.id,
            "planned_event": "workflow.step.planned",
            "completed_event": "workflow.step.completed",
            "execution_tier": step.execution_tier,
            "actor": step.actor,
        }
        for step in workflow.steps
    ]

    return {
        "metadata_keys": REQUIRED_WORKFLOW_METADATA_KEYS,
        "recommended_events": RECOMMENDED_WORKFLOW_EVENTS,
        "expected_step_events": expected_step_events,
        "workflow_id": workflow.id,
        "workflow_name": workflow.name,
        "workflow_version": workflow.version,
        "workflow_team": workflow.team_name,
        "runtime_behavior_changed": False,
    }


def validate_workflow_trace_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate workflow trace metadata shape without reading the observability DB."""

    errors: list[dict[str, str]] = []
    for key in REQUIRED_WORKFLOW_METADATA_KEYS:
        if key not in metadata or metadata.get(key) in {None, ""}:
            errors.append(_error(key, "missing_trace_metadata", f"Trace metadata missing {key}."))

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": [],
        "runtime_behavior_changed": False,
    }


def validate_workflow_directory(workflows_dir: str | Path = "workflows") -> dict[str, Any]:
    """Validate all workflow files in a workflow directory."""

    registry = WorkflowRegistry(workflows_dir)
    results = []
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for path in registry.list_workflow_files():
        result = validate_workflow_contract(path)
        result["path"] = str(path)
        results.append(result)
        for item in result.get("errors", []):
            errors.append({"workflow": result.get("workflow_id") or str(path), **item})
        for item in result.get("warnings", []):
            warnings.append({"workflow": result.get("workflow_id") or str(path), **item})

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "workflow_count": len(results),
        "workflows": results,
        "runtime_behavior_changed": False,
    }
