from __future__ import annotations

from pathlib import Path

from orchgentic.workflows.runtime_doctor import validate_runtime_workflow_file


CLI_SOURCE = Path("orchgentic/cli.py")


def test_run_accepts_optional_quickstart_prompt_argument() -> None:
    source = CLI_SOURCE.read_text(encoding="utf-8")

    assert '@app.command()\ndef run(' in source
    assert 'prompt: str | None = typer.Argument(None' in source
    assert 'task = prompt or typer.prompt("Task")' in source


def test_run_team_accepts_optional_quickstart_prompt_argument() -> None:
    source = CLI_SOURCE.read_text(encoding="utf-8")

    assert '@app.command("run-team")\ndef run_team(' in source
    assert 'prompt: str | None = typer.Argument(None' in source
    assert 'task = prompt or typer.prompt("Team task", default=team.task)' in source


def test_create_agent_command_is_registered_for_quickstart() -> None:
    source = CLI_SOURCE.read_text(encoding="utf-8")

    assert '@app.command("create-agent")' in source
    assert 'def create_agent(' in source
    assert 'create_agent_file(' in source


def test_workflow_doctor_command_is_registered_for_quickstart() -> None:
    source = CLI_SOURCE.read_text(encoding="utf-8")

    assert '@workflow_app.command("doctor")' in source
    assert 'def workflow_doctor(' in source
    assert 'validate_runtime_workflow_file' in source


def test_workflow_doctor_accepts_quickstart_example_files() -> None:
    for path in sorted(Path("examples/workflows").glob("*.yaml")):
        payload = validate_runtime_workflow_file(path)
        assert payload["valid"] is True, f"{path} should be valid: {payload['errors']}"
        assert payload["checks"]["required_fields"] == "ok"
        assert payload["checks"]["trigger_contract"] == "ok"
        assert payload["checks"]["runtime_contract"] == "ok"
        assert payload["checks"]["step_ids"] == "ok"
        assert payload["checks"]["references"] == "ok"
        assert payload["checks"]["outputs"] == "ok"


def test_workflow_doctor_reports_unknown_references(tmp_path: Path) -> None:
    workflow = tmp_path / "bad.yaml"
    workflow.write_text(
        """
id: bad-workflow
name: Bad Workflow
version: 0.9.0-beta.1
trigger:
  type: manual
runtime:
  mode: sequential
  save_trace: true
  fail_fast: true
steps:
  - id: missing_agent
    type: agent
    agent: MissingAgent
    prompt: Test
outputs:
  final:
    from: missing_agent.response
""".strip(),
        encoding="utf-8",
    )

    payload = validate_runtime_workflow_file(workflow)

    assert payload["valid"] is False
    assert any(item["code"] == "unknown_agent" for item in payload["errors"])
