from orchgentic.runtime.execution_policy import validate_execution_tiers


def test_doctor_execution_tiers_command_is_registered():
    source = open("orchgentic/cli.py", encoding="utf-8").read()

    assert '@doctor_app.command("execution-tiers")' in source
    assert "def doctor_execution_tiers" in source
    assert "validate_execution_tiers" in source
    assert "format_execution_tier_doctor" in source


def test_execution_tier_doctor_formatter_outputs_key_fields():
    from orchgentic.runtime.execution_tier_doctor import format_execution_tier_doctor

    payload = {
        "agent": "Bob",
        "status": "valid",
        "valid": True,
        "routing_behavior_changed": False,
        "execution_tiers": {
            "local_llm": {
                "enabled": False,
                "provider": "lmstudio",
                "model": None,
                "eligible_for": ["routing", "review"],
            }
        },
        "errors": [],
        "warnings": [],
    }

    text = format_execution_tier_doctor(payload)

    assert "EXECUTION TIER DOCTOR" in text
    assert "agent: Bob" in text
    assert "status: valid" in text
    assert "routing_behavior_changed: False" in text
    assert "provider: lmstudio" in text
    assert "eligible_for: routing, review" in text


def test_execution_tier_doctor_formatter_shows_warnings_and_errors():
    from orchgentic.runtime.execution_tier_doctor import format_execution_tier_doctor

    payload = {
        "agent": "Bob",
        "status": "invalid",
        "valid": False,
        "routing_behavior_changed": False,
        "execution_tiers": {"local_llm": {"enabled": True, "provider": "", "model": None, "eligible_for": []}},
        "errors": [{"code": "missing_local_llm_provider", "message": "provider missing"}],
        "warnings": [{"code": "missing_local_llm_model", "message": "model missing"}],
    }

    text = format_execution_tier_doctor(payload)

    assert "errors:" in text
    assert "missing_local_llm_provider: provider missing" in text
    assert "warnings:" in text
    assert "missing_local_llm_model: model missing" in text


def test_execution_tier_validation_still_does_not_change_routing_behavior():
    result = validate_execution_tiers(
        {
            "local_llm": {
                "enabled": True,
                "provider": "lmstudio",
                "model": None,
            }
        }
    )

    assert result["routing_behavior_changed"] is False
