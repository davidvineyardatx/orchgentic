from __future__ import annotations

from agent_core.stabilization.beta2_checks import (
    check_agent_layer_config,
    check_knowledge_config,
    check_memory_config,
    check_provider_config,
)


def test_provider_config_accepts_groq_model() -> None:
    report = check_provider_config(
        {
            "provider": {
                "type": "groq",
                "model": "llama-3.3-70b-versatile",
            }
        }
    )

    assert report.ok
    assert report.errors == []


def test_provider_config_rejects_unknown_provider() -> None:
    report = check_provider_config(
        {
            "provider": {
                "type": "unknown-provider",
                "model": "test-model",
            }
        }
    )

    assert not report.ok
    assert report.errors[0].code == "provider.type.unsupported"


def test_provider_config_requires_model() -> None:
    report = check_provider_config({"provider": {"type": "openai"}})

    assert not report.ok
    assert any(issue.code == "provider.model.missing" for issue in report.errors)


def test_memory_config_warns_when_disabled() -> None:
    report = check_memory_config({"memory": {"enabled": False}})

    assert report.ok
    assert report.warnings[0].code == "memory.disabled"


def test_memory_config_requires_db_path_when_enabled() -> None:
    report = check_memory_config({"memory": {"enabled": True, "store": "sqlite"}})

    assert not report.ok
    assert any(issue.code == "memory.db_path.missing" for issue in report.errors)


def test_memory_config_rejects_negative_recent_messages() -> None:
    report = check_memory_config(
        {
            "memory": {
                "enabled": True,
                "store": "sqlite",
                "db_path": "memory/agent_core.db",
                "recent_messages": -1,
            }
        }
    )

    assert not report.ok
    assert any(issue.code == "memory.recent_messages.invalid" for issue in report.errors)


def test_knowledge_config_requires_local_db_path() -> None:
    report = check_knowledge_config(
        {
            "knowledge": {
                "enabled": True,
                "store": "local",
                "top_k": 5,
            }
        }
    )

    assert not report.ok
    assert any(issue.code == "knowledge.db_path.missing" for issue in report.errors)


def test_knowledge_config_rejects_invalid_top_k() -> None:
    report = check_knowledge_config(
        {
            "knowledge": {
                "enabled": True,
                "store": "local",
                "db_path": "memory/knowledge.db",
                "top_k": 0,
            }
        }
    )

    assert not report.ok
    assert any(issue.code == "knowledge.top_k.invalid" for issue in report.errors)


def test_knowledge_config_warns_on_high_top_k() -> None:
    report = check_knowledge_config(
        {
            "knowledge": {
                "enabled": True,
                "store": "local",
                "db_path": "memory/knowledge.db",
                "top_k": 50,
            }
        }
    )

    assert report.ok
    assert any(issue.code == "knowledge.top_k.high" for issue in report.warnings)


def test_combined_agent_layer_config_reports_all_layers() -> None:
    result = check_agent_layer_config(
        {
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
    )

    assert result["ok"] is True
    assert [report["layer"] for report in result["reports"]] == ["provider", "memory", "knowledge"]
