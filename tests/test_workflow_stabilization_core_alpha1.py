from orchgentic.workflows.contracts import (
    validate_workflow_contract,
    validate_workflow_directory,
    validate_workflow_trace_metadata,
    workflow_trace_contract,
)
from orchgentic.workflows.doctor import format_workflow_contract, format_workflow_doctor


def _workflow():
    return {
        "workflow": {
            "id": "content_intelligence_summary",
            "name": "Content Intelligence Summary",
            "version": "0.1.0",
            "team": {
                "name": "ContentTeam",
                "members": ["Researcher", "Writer", "Reviewer"],
            },
            "steps": [
                {
                    "id": "deterministic_team_plan",
                    "name": "Deterministic team plan",
                    "actor": "Manager",
                    "execution_tier": "deterministic",
                    "action": "assign_roles_from_team_config",
                },
                {
                    "id": "final_synthesis",
                    "name": "Final synthesis",
                    "actor": "Manager",
                    "execution_tier": "premium_external_candidate",
                    "action": "synthesize_final_response",
                },
            ],
        }
    }


def test_workflow_contract_baseline_validates_team_backed_workflow():
    result = validate_workflow_contract(_workflow())

    assert result["valid"] is True
    assert result["status"] == "valid"
    assert result["workflow_id"] == "content_intelligence_summary"
    assert result["team_backed"] is True
    assert result["team_name"] == "ContentTeam"
    assert result["team_member_count"] == 3
    assert result["step_count"] == 2
    assert result["runtime_behavior_changed"] is False


def test_single_agent_workflow_is_rejected():
    workflow = _workflow()
    workflow["workflow"]["team"]["members"] = ["Bob"]

    result = validate_workflow_contract(workflow)

    assert result["valid"] is False
    assert any(item["code"] == "single_agent_workflow_not_supported" for item in result["errors"])


def test_workflow_trace_contract_exposes_metadata_and_step_events():
    result = validate_workflow_contract(_workflow())
    trace = result["trace_contract"]

    assert trace["workflow_id"] == "content_intelligence_summary"
    assert "workflow_id" in trace["metadata_keys"]
    assert "workflow.step.planned" in trace["recommended_events"]
    assert trace["expected_step_events"][0]["step_id"] == "deterministic_team_plan"
    assert trace["runtime_behavior_changed"] is False


def test_validate_workflow_trace_metadata_requires_stable_keys():
    valid = validate_workflow_trace_metadata(
        {
            "workflow_id": "content_intelligence_summary",
            "workflow_name": "Content Intelligence Summary",
            "workflow_version": "0.1.0",
            "workflow_status": "blueprint",
            "workflow_team": "ContentTeam",
        }
    )
    invalid = validate_workflow_trace_metadata({"workflow_id": "content_intelligence_summary"})

    assert valid["valid"] is True
    assert invalid["valid"] is False
    assert any(item["code"] == "missing_trace_metadata" for item in invalid["errors"])


def test_workflow_directory_doctor_validates_all_workflows(tmp_path):
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "content_intelligence_summary.workflow.yaml").write_text(
        """
workflow:
  id: content_intelligence_summary
  name: Content Intelligence Summary
  version: 0.1.0
  team:
    name: ContentTeam
    members:
      - Researcher
      - Writer
      - Reviewer
  steps:
    - id: deterministic_team_plan
      actor: Manager
      execution_tier: deterministic
      action: assign_roles_from_team_config
""".strip(),
        encoding="utf-8",
    )

    result = validate_workflow_directory(workflows_dir)

    assert result["valid"] is True
    assert result["workflow_count"] == 1
    assert result["runtime_behavior_changed"] is False


def test_workflow_doctor_formatter_is_lightweight_and_stable():
    payload = {
        "status": "valid",
        "valid": True,
        "workflow_count": 1,
        "runtime_behavior_changed": False,
        "errors": [],
        "warnings": [],
    }

    text = format_workflow_doctor(payload)

    assert "WORKFLOW DOCTOR" in text
    assert "status: valid" in text
    assert "workflow_count: 1" in text
    assert "runtime_behavior_changed: False" in text


def test_workflow_contract_formatter_outputs_summary():
    result = validate_workflow_contract(_workflow())

    text = format_workflow_contract(result)

    assert "WORKFLOW CONTRACT" in text
    assert "id: content_intelligence_summary" in text
    assert "team: ContentTeam" in text
    assert "steps: 2" in text


def test_cli_registers_workflow_commands_without_importing_cli_module():
    source = open("orchgentic/cli.py", encoding="utf-8").read()

    assert "workflow_app = typer.Typer" in source
    assert 'app.add_typer(workflow_app, name="workflow")' in source
    assert '@workflow_app.command("list")' in source
    assert '@workflow_app.command("inspect")' in source
    assert '@workflow_app.command("validate")' in source
    assert '@doctor_app.command("workflows")' in source
