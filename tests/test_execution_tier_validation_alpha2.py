from orchgentic.config.schemas import AgentConfig
from orchgentic.runtime.execution_policy import validate_execution_tiers


def test_default_execution_tiers_validate_without_errors():
    result = validate_execution_tiers(AgentConfig(id="bob", name="Bob"))

    assert result["valid"] is True
    assert result["status"] == "valid"
    assert result["errors"] == []
    assert result["routing_behavior_changed"] is False


def test_enabled_local_llm_without_model_warns_but_does_not_error():
    result = validate_execution_tiers(
        AgentConfig(
            id="bob",
            name="Bob",
            execution_tiers={
                "local_llm": {
                    "enabled": True,
                    "provider": "lmstudio",
                    "model": None,
                }
            },
        )
    )

    assert result["valid"] is True
    assert result["errors"] == []
    assert any(item["code"] == "missing_local_llm_model" for item in result["warnings"])
    assert result["routing_behavior_changed"] is False


def test_enabled_local_llm_without_provider_errors():
    result = validate_execution_tiers(
        AgentConfig(
            id="bob",
            name="Bob",
            execution_tiers={
                "local_llm": {
                    "enabled": True,
                    "provider": "",
                    "model": "qwen3",
                }
            },
        )
    )

    assert result["valid"] is False
    assert result["status"] == "invalid"
    assert any(item["code"] == "missing_local_llm_provider" for item in result["errors"])
    assert result["routing_behavior_changed"] is False


def test_unknown_local_llm_provider_warns():
    result = validate_execution_tiers(
        AgentConfig(
            id="bob",
            name="Bob",
            execution_tiers={
                "local_llm": {
                    "enabled": True,
                    "provider": "custom-provider",
                    "model": "custom-model",
                }
            },
        )
    )

    assert result["valid"] is True
    assert any(item["code"] == "unknown_local_llm_provider" for item in result["warnings"])


def test_disabled_deterministic_and_external_llm_warn():
    result = validate_execution_tiers(
        {
            "deterministic": {"enabled": False},
            "external_llm": {"enabled": False},
        }
    )

    warning_codes = {item["code"] for item in result["warnings"]}

    assert result["valid"] is True
    assert "deterministic_disabled" in warning_codes
    assert "external_llm_disabled" in warning_codes
