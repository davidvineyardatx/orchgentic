from __future__ import annotations

import pytest

from agent_core.stabilization.beta2_runtime import (
    AgentLayerStabilizationError,
    assert_agent_layers_ready,
    build_runtime_failure_message,
)
from agent_core.runtime.stabilization_gate import validate_agent_runtime_layers
from agent_core.stabilization.beta2_doctor import doctor_agent_layers


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


def test_assert_agent_layers_ready_returns_result_for_valid_config() -> None:
    result = assert_agent_layers_ready(_valid_config(), project_root=".")

    assert result.ok
    assert result.agent_name == "Bob"


def test_assert_agent_layers_ready_raises_for_invalid_provider() -> None:
    with pytest.raises(AgentLayerStabilizationError) as exc:
        assert_agent_layers_ready(
            {
                "id": "broken",
                "provider": {
                    "type": "bad-provider",
                    "model": "test-model",
                },
                "memory": {
                    "enabled": True,
                    "store": "sqlite",
                    "db_path": "memory/agent_core.db",
                },
                "knowledge": {
                    "enabled": True,
                    "store": "local",
                    "db_path": "memory/knowledge.db",
                    "top_k": 5,
                },
            },
            project_root=".",
        )

    message = str(exc.value)

    assert "Agent layer stabilization failed for broken." in message
    assert "provider.type.unsupported" in message


def test_runtime_failure_message_lists_only_errors_not_warnings() -> None:
    result = doctor_agent_layers(
        {
            "id": "mixed",
            "provider": {"type": "bad-provider"},
            "memory": {"enabled": False},
            "knowledge": {
                "enabled": True,
                "store": "local",
                "top_k": 0,
            },
        },
        project_root=".",
    )

    message = build_runtime_failure_message(result)

    assert "provider.type.unsupported" in message
    assert "provider.model.missing" in message
    assert "knowledge.top_k.invalid" in message
    assert "knowledge.db_path.missing" in message
    assert "memory.disabled" not in message


def test_runtime_gate_accepts_valid_config() -> None:
    validate_agent_runtime_layers(_valid_config(), project_root=".")


def test_runtime_gate_raises_same_stabilization_error() -> None:
    with pytest.raises(AgentLayerStabilizationError):
        validate_agent_runtime_layers(
            {
                "id": "bad-memory",
                "provider": {
                    "type": "groq",
                    "model": "llama-3.3-70b-versatile",
                },
                "memory": {
                    "enabled": True,
                    "store": "sqlite",
                },
                "knowledge": {
                    "enabled": True,
                    "store": "local",
                    "db_path": "memory/knowledge.db",
                    "top_k": 5,
                },
            },
            project_root=".",
        )
