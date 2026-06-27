from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from orchgentic.workflows.contracts import validate_workflow_contract

SUPPORTED_TRIGGER_TYPES = {"manual", "heartbeat", "webhook"}
SUPPORTED_RUNTIME_MODES = {"sequential"}
SUPPORTED_STEP_TYPES = {"agent", "team", "tool"}
BUILTIN_TOOL_NAMES = {
    "datetime.now",
    "datetime.local",
    "filesystem.read",
    "filesystem.write",
    "web.request",
    "memory.search",
    "knowledge.search",
    "delegate.agent",
    "gmail.search",
    "gmail.read",
    "gmail.draft",
    "gmail.send",
    "gmail.reply",
    "gmail.delete",
}


def _issue(field: str, code: str, message: str) -> dict[str, str]:
    return {"field": field, "code": code, "message": message}


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Workflow file must be a YAML mapping.")
    return data


def _names_from_yaml_dir(directory: str | Path) -> set[str]:
    base = Path(directory)
    names: set[str] = set()
    if not base.exists():
        return names
    for path in base.glob("*.yaml"):
        names.add(path.stem.lower())
        try:
            data = _read_yaml(path)
        except Exception:
            continue
        for key in ("id", "name"):
            value = data.get(key)
            if value:
                names.add(str(value).lower())
    return names


def _check_required(data: dict[str, Any], errors: list[dict[str, str]], checks: dict[str, str]) -> None:
    required = {"id", "name", "version", "trigger", "runtime", "steps"}
    missing = sorted(required - set(data))
    if missing:
        checks["required_fields"] = "error"
        errors.append(_issue("workflow", "missing_required_fields", f"Missing required fields: {', '.join(missing)}"))
    else:
        checks["required_fields"] = "ok"


def validate_runtime_workflow_file(
    path: str | Path,
    *,
    agents_dir: str | Path = "agents",
    teams_dir: str | Path = "teams",
    tool_names: set[str] | None = None,
) -> dict[str, Any]:
    """Validate the user-facing flat workflow YAML contract used by examples/workflows.

    This intentionally does not execute a workflow. It validates the file shape,
    common references, and quickstart-level mistakes before runtime.
    """

    workflow_path = Path(path)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    checks: dict[str, str] = {
        "file": "pending",
        "yaml": "pending",
        "required_fields": "pending",
        "trigger_contract": "pending",
        "runtime_contract": "pending",
        "step_ids": "pending",
        "step_contracts": "pending",
        "references": "pending",
        "outputs": "pending",
    }

    if not workflow_path.exists():
        checks["file"] = "error"
        errors.append(_issue("path", "workflow_file_not_found", f"Workflow file not found: {workflow_path}"))
        return _runtime_doctor_payload(workflow_path, {}, errors, warnings, checks)

    checks["file"] = "ok"

    try:
        data = _read_yaml(workflow_path)
    except Exception as exc:
        checks["yaml"] = "error"
        errors.append(_issue("yaml", "invalid_yaml", str(exc)))
        return _runtime_doctor_payload(workflow_path, {}, errors, warnings, checks)

    checks["yaml"] = "ok"

    # Support the newer nested blueprint contract too, so `workflow doctor` can
    # validate both `workflows/*.workflow.yaml` and `examples/workflows/*.yaml`.
    if isinstance(data.get("workflow"), dict):
        nested = validate_workflow_contract(workflow_path)
        checks.update({key: "ok" for key in checks if checks[key] == "pending"})
        for item in nested.get("errors", []):
            errors.append(_issue(item.get("field", "workflow"), item.get("code", "invalid_workflow"), item.get("message", "Invalid workflow.")))
        for item in nested.get("warnings", []):
            warnings.append(_issue(item.get("field", "workflow"), item.get("code", "workflow_warning"), item.get("message", "Workflow warning.")))
        return _runtime_doctor_payload(workflow_path, data.get("workflow") or {}, errors, warnings, checks)

    _check_required(data, errors, checks)

    trigger = data.get("trigger") or {}
    if not isinstance(trigger, dict):
        checks["trigger_contract"] = "error"
        errors.append(_issue("trigger", "invalid_trigger_contract", "trigger must be a mapping."))
    elif trigger.get("type") not in SUPPORTED_TRIGGER_TYPES:
        checks["trigger_contract"] = "error"
        errors.append(_issue("trigger.type", "unsupported_trigger_type", f"Unsupported trigger type: {trigger.get('type')!r}"))
    else:
        checks["trigger_contract"] = "ok"

    runtime = data.get("runtime") or {}
    if not isinstance(runtime, dict):
        checks["runtime_contract"] = "error"
        errors.append(_issue("runtime", "invalid_runtime_contract", "runtime must be a mapping."))
    elif runtime.get("mode") not in SUPPORTED_RUNTIME_MODES:
        checks["runtime_contract"] = "error"
        errors.append(_issue("runtime.mode", "unsupported_runtime_mode", f"Unsupported runtime mode: {runtime.get('mode')!r}"))
    else:
        checks["runtime_contract"] = "ok"
        if runtime.get("save_trace") is not True:
            warnings.append(_issue("runtime.save_trace", "trace_not_enabled", "runtime.save_trace should be true for observable workflow runs."))
        if runtime.get("fail_fast") is not True:
            warnings.append(_issue("runtime.fail_fast", "fail_fast_not_enabled", "runtime.fail_fast should be true while validating workflows."))

    steps = data.get("steps") or []
    if not isinstance(steps, list) or not steps:
        checks["step_ids"] = "error"
        checks["step_contracts"] = "error"
        errors.append(_issue("steps", "missing_or_invalid_steps", "steps must be a non-empty list."))
    else:
        step_ids: list[str] = []
        step_contract_error = False
        reference_error = False
        agent_names = _names_from_yaml_dir(agents_dir)
        team_names = _names_from_yaml_dir(teams_dir)
        tools = tool_names or BUILTIN_TOOL_NAMES

        for index, step in enumerate(steps):
            field = f"steps[{index}]"
            if not isinstance(step, dict):
                step_contract_error = True
                errors.append(_issue(field, "invalid_step_contract", "Each step must be a mapping."))
                continue

            step_id = step.get("id")
            if not step_id:
                step_contract_error = True
                errors.append(_issue(f"{field}.id", "missing_step_id", "Each step must include id."))
            else:
                step_ids.append(str(step_id))

            step_type = step.get("type")
            if step_type not in SUPPORTED_STEP_TYPES:
                step_contract_error = True
                errors.append(_issue(f"{field}.type", "unsupported_step_type", f"Unsupported step type: {step_type!r}"))
                continue

            if step_type == "agent":
                agent = step.get("agent")
                if not agent:
                    step_contract_error = True
                    errors.append(_issue(f"{field}.agent", "missing_agent_reference", "Agent step must include agent."))
                elif str(agent).lower() not in agent_names:
                    reference_error = True
                    errors.append(_issue(f"{field}.agent", "unknown_agent", f"Referenced agent not found: {agent}"))
                if not step.get("prompt"):
                    warnings.append(_issue(f"{field}.prompt", "missing_agent_prompt", "Agent step should include prompt."))

            if step_type == "team":
                team = step.get("team")
                if not team:
                    step_contract_error = True
                    errors.append(_issue(f"{field}.team", "missing_team_reference", "Team step must include team."))
                elif str(team).lower() not in team_names:
                    reference_error = True
                    errors.append(_issue(f"{field}.team", "unknown_team", f"Referenced team not found: {team}"))
                if not step.get("prompt"):
                    warnings.append(_issue(f"{field}.prompt", "missing_team_prompt", "Team step should include prompt."))

            if step_type == "tool":
                tool = step.get("tool")
                if not tool:
                    step_contract_error = True
                    errors.append(_issue(f"{field}.tool", "missing_tool_reference", "Tool step must include tool."))
                elif str(tool) not in tools:
                    reference_error = True
                    errors.append(_issue(f"{field}.tool", "unknown_tool", f"Referenced tool not found: {tool}"))
                if "with" not in step:
                    warnings.append(_issue(f"{field}.with", "missing_tool_inputs", "Tool step should include with inputs."))
                if tool in {"gmail.send", "gmail.delete"}:
                    with_args = step.get("with") or {}
                    if not isinstance(with_args, dict) or with_args.get("confirm") is not True:
                        errors.append(_issue(f"{field}.with.confirm", "destructive_tool_requires_confirm", f"{tool} requires confirm: true."))

        duplicates = sorted({item for item in step_ids if step_ids.count(item) > 1})
        if duplicates:
            checks["step_ids"] = "error"
            errors.append(_issue("steps.id", "duplicate_step_ids", f"Duplicate step ids: {', '.join(duplicates)}"))
        else:
            checks["step_ids"] = "ok"

        checks["step_contracts"] = "error" if step_contract_error else "ok"
        checks["references"] = "error" if reference_error else "ok"

    outputs = data.get("outputs") or {}
    final_output = outputs.get("final") if isinstance(outputs, dict) else None
    if not isinstance(outputs, dict) or not isinstance(final_output, dict) or not final_output.get("from"):
        checks["outputs"] = "warning"
        warnings.append(_issue("outputs.final.from", "missing_final_output", "Workflow should define outputs.final.from."))
    else:
        checks["outputs"] = "ok"

    for key, value in list(checks.items()):
        if value == "pending":
            checks[key] = "ok"

    return _runtime_doctor_payload(workflow_path, data, errors, warnings, checks)


def _runtime_doctor_payload(path: Path, data: dict[str, Any], errors: list[dict[str, str]], warnings: list[dict[str, str]], checks: dict[str, str]) -> dict[str, Any]:
    return {
        "workflow_id": data.get("id"),
        "workflow_name": data.get("name"),
        "path": str(path),
        "status": "error" if errors else "ok",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "runtime_behavior_changed": False,
    }


def format_runtime_workflow_doctor(payload: dict[str, Any]) -> str:
    name = payload.get("workflow_name") or payload.get("workflow_id") or payload.get("path")
    lines = [f"Workflow: {name}", f"Path: {payload.get('path')}", f"Status: {'OK' if payload.get('valid') else 'ERROR'}", "", "Checks:"]
    for key, value in (payload.get("checks") or {}).items():
        marker = "✓" if value == "ok" else ("!" if value == "warning" else "✗")
        lines.append(f"  {marker} {key}: {value}")

    errors = payload.get("errors") or []
    warnings = payload.get("warnings") or []
    if errors:
        lines.extend(["", "Errors:"])
        for item in errors:
            lines.append(f"  - {item.get('field')}: {item.get('code')}: {item.get('message')}")
    if warnings:
        lines.extend(["", "Warnings:"])
        for item in warnings:
            lines.append(f"  - {item.get('field')}: {item.get('code')}: {item.get('message')}")
    return "\n".join(lines)
