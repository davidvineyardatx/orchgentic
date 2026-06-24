from __future__ import annotations

import json
from pathlib import Path

from agent_core.stabilization.beta2_doctor import (
    doctor_agent_layers,
    format_beta2_doctor_text,
)


def _valid_config() -> dict:
    return {
        "id": "bob",
        "name": "Bob",
        "provider": {
            "type": "groq",
            "model": "llama-3.3-70b-versatile",
        },
        "memory": {
            "enabled": True,
            "store": "sqlite",
            "db_path": "memory/agent_core.db",
            "recent_messages": 10,
        },
        "knowledge": {
            "enabled": True,
            "store": "local",
            "db_path": "memory/knowledge.db",
            "top_k": 5,
        },
    }


def test_doctor_agent_layers_accepts_valid_config() -> None:
    result = doctor_agent_layers(_valid_config(), project_root=".")

    assert result.ok
    assert result.agent_name == "Bob"
    assert [report.layer for report in result.reports] == ["provider", "memory", "knowledge"]


def test_doctor_agent_layers_returns_json_shape() -> None:
    result = doctor_agent_layers(_valid_config(), project_root=".")
    parsed = json.loads(result.to_json())

    assert parsed["ok"] is True
    assert parsed["agent_name"] == "Bob"
    assert [report["layer"] for report in parsed["reports"]] == ["provider", "memory", "knowledge"]


def test_doctor_agent_layers_accepts_yaml_path(tmp_path: Path) -> None:
    agent_dir = tmp_path / "agents"
    agent_dir.mkdir()
    agent_path = agent_dir / "bob.yaml"
    agent_path.write_text(
        """
id: bob
name: Bob
provider:
  type: groq
  model: llama-3.3-70b-versatile
memory:
  enabled: true
  store: sqlite
  db_path: memory/agent_core.db
  recent_messages: 10
knowledge:
  enabled: true
  store: local
  db_path: memory/knowledge.db
  top_k: 5
""".strip(),
        encoding="utf-8",
    )

    result = doctor_agent_layers(agent_path)

    assert result.ok
    assert result.agent_path == str(agent_path)


def test_doctor_text_shows_clear_failure_details() -> None:
    result = doctor_agent_layers(
        {
            "id": "broken",
            "provider": {"type": "bad-provider"},
            "memory": {"enabled": True, "store": "sqlite"},
            "knowledge": {"enabled": True, "store": "local", "top_k": 0},
        },
        project_root=".",
    )

    text = format_beta2_doctor_text(result)

    assert not result.ok
    assert "Status: FAILED" in text
    assert "provider.type.unsupported" in text
    assert "provider.model.missing" in text
    assert "memory.db_path.missing" in text
    assert "knowledge.top_k.invalid" in text
    assert "knowledge.db_path.missing" in text


def test_doctor_text_keeps_warnings_non_blocking() -> None:
    result = doctor_agent_layers(
        {
            "id": "warnings-only",
            "provider": {
                "type": "groq",
                "model": "llama-3.3-70b-versatile",
            },
            "memory": {"enabled": False},
            "knowledge": {"enabled": False},
        },
        project_root=".",
    )

    text = format_beta2_doctor_text(result)

    assert result.ok
    assert "Status: OK" in text
    assert "WARNING memory.disabled" in text
    assert "WARNING knowledge.disabled" in text
