from orchgentic.tools.contracts import (
    normalize_plugin_tool_contract,
    validate_plugin_tool_contract,
)


def _plugin_contract():
    return {
        "name": "acme.crm.lookup_contact",
        "description": "Look up a contact in Acme CRM.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
        "category": "crm",
        "side_effect": "read",
        "destructive": False,
        "supports_confirmation": False,
        "requires_policy_check": True,
        "builtin": False,
        "plugin": {
            "name": "acme-crm",
            "version": "0.1.0",
            "author": "Acme",
            "source": "local",
        },
    }


def test_normalize_plugin_tool_contract_sets_builtin_false():
    normalized = normalize_plugin_tool_contract(
        {
            "name": "acme.crm.lookup_contact",
            "description": "Look up a contact.",
            "input_schema": {
                "type": "object",
                "properties": {"email": {"type": "string"}},
                "required": ["email"],
            },
        },
        plugin={"name": "acme-crm", "version": "0.1.0"},
    )

    assert normalized["builtin"] is False
    assert normalized["plugin"]["name"] == "acme-crm"
    assert normalized["plugin"]["version"] == "0.1.0"


def test_valid_plugin_tool_contract_shape_passes_without_loader():
    result = validate_plugin_tool_contract(_plugin_contract())

    assert result["valid"] is True
    assert result["status"] == "valid"
    assert result["plugin_loader_added"] is False
    assert result["runtime_behavior_changed"] is False
    assert result["contract"]["builtin"] is False


def test_plugin_tool_contract_requires_plugin_name_and_version():
    contract = _plugin_contract()
    contract["plugin"] = {"name": "acme-crm"}

    result = validate_plugin_tool_contract(contract)

    assert result["valid"] is False
    assert any(item["field"] == "plugin.version" for item in result["errors"])


def test_plugin_tool_contract_warns_when_tool_name_is_not_namespaced():
    contract = _plugin_contract()
    contract["name"] = "lookup_contact"

    result = validate_plugin_tool_contract(contract)

    assert result["valid"] is True
    assert any(item["code"] == "plugin_tool_name_should_be_namespaced" for item in result["warnings"])


def test_plugin_tool_contract_does_not_add_runtime_behavior():
    result = validate_plugin_tool_contract(_plugin_contract())

    assert result["plugin_loader_added"] is False
    assert result["runtime_behavior_changed"] is False
