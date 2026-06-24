from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agent_core.runtime.stabilization_gate import validate_agent_runtime_layers
from agent_core.stabilization.beta2_regressions import (
    Beta2RegressionResult,
    check_empty_search_result,
    check_provider_factory_result,
    normalize_search_result,
)
from agent_core.stabilization.beta2_runtime import AgentLayerStabilizationError


class FakeProvider:
    def complete(self, prompt: str) -> str:
        return f"completed: {prompt}"


class BadProvider:
    pass


def _valid_config(tmp_path: Path) -> dict:
    memory_path = tmp_path / "memory" / "agent_core.db"
    knowledge_path = tmp_path / "memory" / "knowledge.db"
    memory_path.parent.mkdir(parents=True, exist_ok=True)

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
            "db_path": str(memory_path),
            "recent_messages": 10,
        },
        "knowledge": {
            "enabled": True,
            "store": "local",
            "db_path": str(knowledge_path),
            "top_k": 5,
        },
    }


def test_normalize_search_result_accepts_none_as_empty() -> None:
    assert normalize_search_result(None) == []


def test_normalize_search_result_accepts_list() -> None:
    assert normalize_search_result(["a", "b"]) == ["a", "b"]


def test_normalize_search_result_accepts_tuple() -> None:
    assert normalize_search_result(("a", "b")) == ["a", "b"]


def test_normalize_search_result_accepts_common_mapping_shapes() -> None:
    assert normalize_search_result({"results": ["one"]}) == ["one"]
    assert normalize_search_result({"items": ("two",)}) == ["two"]
    assert normalize_search_result({"matches": []}) == []


def test_empty_memory_search_result_is_safe() -> None:
    result = check_empty_search_result([], layer="memory")

    assert isinstance(result, Beta2RegressionResult)
    assert result.ok
    assert result.name == "memory.empty_search"
    assert result.details == {"count": 0}


def test_empty_knowledge_search_result_is_safe() -> None:
    result = check_empty_search_result({"results": []}, layer="knowledge")

    assert result.ok
    assert result.name == "knowledge.empty_search"
    assert "safe empty result" in result.message


def test_provider_factory_result_accepts_runtime_callable() -> None:
    result = check_provider_factory_result(FakeProvider(), provider_type="groq")

    assert result.ok
    assert result.details == {"provider_type": "groq", "methods": ["complete"]}


def test_provider_factory_result_rejects_none() -> None:
    result = check_provider_factory_result(None, provider_type="groq")

    assert not result.ok
    assert "returned None" in result.message


def test_provider_factory_result_rejects_object_without_runtime_method() -> None:
    result = check_provider_factory_result(BadProvider(), provider_type="groq")

    assert not result.ok
    assert "no recognized callable runtime method" in result.message


def test_runtime_gate_accepts_valid_config_with_real_temp_paths(tmp_path: Path) -> None:
    validate_agent_runtime_layers(_valid_config(tmp_path), project_root=tmp_path)


def test_runtime_gate_fails_before_memory_initialization_when_db_path_missing(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)
    del config["memory"]["db_path"]

    with pytest.raises(AgentLayerStabilizationError) as exc:
        validate_agent_runtime_layers(config, project_root=tmp_path)

    assert "memory.db_path.missing" in str(exc.value)


def test_runtime_gate_fails_before_knowledge_search_when_top_k_invalid(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)
    config["knowledge"]["top_k"] = 0

    with pytest.raises(AgentLayerStabilizationError) as exc:
        validate_agent_runtime_layers(config, project_root=tmp_path)

    assert "knowledge.top_k.invalid" in str(exc.value)


def test_runtime_gate_allows_disabled_memory_without_blocking_agent(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)
    config["memory"] = {"enabled": False}

    validate_agent_runtime_layers(config, project_root=tmp_path)


def test_runtime_gate_allows_disabled_knowledge_without_blocking_agent(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)
    config["knowledge"] = {"enabled": False}

    validate_agent_runtime_layers(config, project_root=tmp_path)


def test_sqlite_memory_path_can_be_created_after_config_validation(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)

    validate_agent_runtime_layers(config, project_root=tmp_path)

    db_path = Path(config["memory"]["db_path"])
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memory_test (id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("INSERT INTO memory_test (text) VALUES (?)", ("hello memory",))
        rows = conn.execute("SELECT text FROM memory_test").fetchall()

    assert rows == [("hello memory",)]


def test_local_knowledge_path_can_be_created_after_config_validation(tmp_path: Path) -> None:
    config = _valid_config(tmp_path)

    validate_agent_runtime_layers(config, project_root=tmp_path)

    db_path = Path(config["knowledge"]["db_path"])
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS knowledge_test (id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("INSERT INTO knowledge_test (text) VALUES (?)", ("hello knowledge",))
        rows = conn.execute("SELECT text FROM knowledge_test").fetchall()

    assert rows == [("hello knowledge",)]
