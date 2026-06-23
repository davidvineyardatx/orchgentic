from pathlib import Path

from typer.testing import CliRunner

from orchgentic.cli import app


def test_create_team_cli_creates_default_team(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["create-team", "MarketingTeam"])

    assert result.exit_code == 0
    team_file = tmp_path / "teams" / "marketingteam.yaml"
    assert team_file.exists()

    text = team_file.read_text(encoding="utf-8")
    assert "id: marketingteam" in text
    assert "name: MarketingTeam" in text
    assert "orchestrator: Manager" in text
    assert "- Researcher" in text
    assert "- Writer" in text
    assert "- Reviewer" in text


def test_create_team_cli_accepts_custom_members(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "create-team",
            "ITTeam",
            "--orchestrator",
            "Lead",
            "--members",
            "Architect,Engineer,Reviewer",
        ],
    )

    assert result.exit_code == 0
    team_file = tmp_path / "teams" / "itteam.yaml"
    text = team_file.read_text(encoding="utf-8")

    assert "id: itteam" in text
    assert "name: ITTeam" in text
    assert "orchestrator: Lead" in text
    assert "- Architect" in text
    assert "- Engineer" in text
    assert "- Reviewer" in text


def test_create_team_cli_refuses_existing_file_without_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    first = runner.invoke(app, ["create-team", "MarketingTeam"])
    second = runner.invoke(app, ["create-team", "MarketingTeam"])

    assert first.exit_code == 0
    assert second.exit_code == 1
    assert "Use --overwrite" in second.output
