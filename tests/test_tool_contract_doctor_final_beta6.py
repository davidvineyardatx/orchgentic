from orchgentic.tools.contracts import validate_builtin_tool_contracts, validate_tool_registry_contracts


def test_validate_builtin_tool_contracts_returns_stable_summary():
    result = validate_builtin_tool_contracts()

    assert result["tool_count"] == 14
    assert result["plugin_loader_added"] is False
    assert result["runtime_behavior_changed"] is False
    assert "tool_contracts" in result
    assert "confirmation_contracts" in result
    assert "runtime_confirmation_consistency" in result


def test_tool_contract_doctor_command_is_registered():
    source = open("orchgentic/cli.py", encoding="utf-8").read()

    assert '@doctor_app.command("tool-contracts")' in source
    assert "def doctor_tool_contracts" in source
    assert "validate_tool_registry_contracts" in source
    assert "format_tool_contract_doctor" in source


def test_tool_contract_doctor_formatter_outputs_summary():
    from orchgentic.tools.contract_doctor import format_tool_contract_doctor

    payload = {
        "status": "valid",
        "valid": True,
        "tool_count": 14,
        "plugin_loader_added": False,
        "runtime_behavior_changed": False,
        "errors": [],
        "warnings": [],
    }

    text = format_tool_contract_doctor(payload)

    assert "TOOL CONTRACT DOCTOR" in text
    assert "status: valid" in text
    assert "tool_count: 14" in text
    assert "plugin_loader_added: False" in text
    assert "runtime_behavior_changed: False" in text


def test_tool_contract_doctor_formatter_shows_warnings():
    from orchgentic.tools.contract_doctor import format_tool_contract_doctor

    payload = {
        "status": "valid",
        "valid": True,
        "tool_count": 14,
        "plugin_loader_added": False,
        "runtime_behavior_changed": False,
        "errors": [],
        "warnings": [
            {
                "tool": "filesystem.write",
                "code": "destructive_without_confirmation",
                "message": "baseline warning",
            }
        ],
    }

    text = format_tool_contract_doctor(payload)

    assert "warnings:" in text
    assert "filesystem.write: destructive_without_confirmation: baseline warning" in text
