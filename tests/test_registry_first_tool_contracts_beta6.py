from orchgentic.registry import Registry
from orchgentic.tools.contracts import (
    get_tool_contracts_from_registry,
    validate_tool_registry_contracts,
)


class EchoTool:
    name = "custom.echo"
    description = "Echo text."
    input_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }


class SlackSendTool:
    name = "slack.send"
    description = "Send a Slack message."
    input_schema = {
        "type": "object",
        "properties": {
            "channel": {"type": "string"},
            "text": {"type": "string"},
            "confirm": {"type": "boolean"},
        },
        "required": ["channel", "text"],
    }
    category = "slack"
    side_effect = "send"
    destructive = True
    supports_confirmation = True
    requires_policy_check = True


def test_registry_is_source_of_truth_for_tool_contracts():
    registry = Registry()
    registry.register(EchoTool.name, EchoTool())

    contracts = get_tool_contracts_from_registry(registry)

    assert len(contracts) == 1
    assert contracts[0]["name"] == "custom.echo"
    assert contracts[0]["builtin"] is True
    assert contracts[0]["input_schema"]["type"] == "object"


def test_registry_tool_metadata_can_be_declared_on_tool_class():
    registry = Registry()
    registry.register(SlackSendTool.name, SlackSendTool())

    contract = get_tool_contracts_from_registry(registry)[0]

    assert contract["name"] == "slack.send"
    assert contract["category"] == "slack"
    assert contract["side_effect"] == "send"
    assert contract["destructive"] is True
    assert contract["supports_confirmation"] is True
    assert contract["requires_policy_check"] is True


def test_registry_contract_validation_validates_registered_tools():
    registry = Registry()
    registry.register(EchoTool.name, EchoTool())
    registry.register(SlackSendTool.name, SlackSendTool())

    result = validate_tool_registry_contracts(registry)

    assert result["source"] == "registry"
    assert result["tool_count"] == 2
    assert result["runtime_behavior_changed"] is False
    assert result["plugin_loader_added"] is False
    assert result["valid"] is True


def test_registry_contract_validation_reports_invalid_registered_tool():
    class BadTool:
        name = "bad.tool"
        description = ""
        input_schema = {"type": "object", "properties": {}, "required": []}

    registry = Registry()
    registry.register(BadTool.name, BadTool())

    result = validate_tool_registry_contracts(registry)

    assert result["source"] == "registry"
    assert result["valid"] is False
    assert any(item["tool"] == "bad.tool" for item in result["errors"])
