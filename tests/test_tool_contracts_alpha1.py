from orchgentic.tools.contracts import (
    get_builtin_tool_contract,
    get_builtin_tool_contracts,
    normalize_tool_contract,
    validate_tool_contract,
)


EXPECTED_BUILTIN_TOOLS = {
    "datetime.now",
    "datetime.local",
    "filesystem.read",
    "filesystem.write",
    "web.request",
    "memory.search",
    "knowledge.search",
    "delegate.agent",
    "gmail.search",
    "gmail.read",
    "gmail.draft",
    "gmail.send",
    "gmail.reply",
    "gmail.delete",
}


def test_builtin_tool_contract_inventory_is_frozen():
    contracts = get_builtin_tool_contracts()
    names = {contract["name"] for contract in contracts}

    assert names == EXPECTED_BUILTIN_TOOLS
    assert len(contracts) == 14


def test_builtin_tool_contracts_have_required_public_fields():
    for contract in get_builtin_tool_contracts():
        assert contract["name"]
        assert contract["description"]
        assert contract["input_schema"]["type"] == "object"
        assert isinstance(contract["input_schema"]["properties"], dict)
        assert isinstance(contract["input_schema"]["required"], list)
        assert "category" in contract
        assert "side_effect" in contract
        assert "destructive" in contract
        assert "supports_confirmation" in contract
        assert "requires_policy_check" in contract
        assert "builtin" in contract
        assert validate_tool_contract(contract)["valid"] is True


def test_gmail_side_effect_contracts_lock_confirmation_and_policy_shape():
    send_contract = get_builtin_tool_contract("gmail.send")
    reply_contract = get_builtin_tool_contract("gmail.reply")
    delete_contract = get_builtin_tool_contract("gmail.delete")

    for contract in [send_contract, reply_contract, delete_contract]:
        assert contract is not None
        assert contract["destructive"] is True
        assert contract["supports_confirmation"] is True
        assert contract["requires_policy_check"] is True
        assert contract["input_schema"]["properties"]["confirm"]["type"] == "boolean"

    assert send_contract["side_effect"] == "send"
    assert reply_contract["side_effect"] == "send"
    assert delete_contract["side_effect"] == "delete"


def test_filesystem_write_contract_locks_current_baseline_without_behavior_change():
    contract = get_builtin_tool_contract("filesystem.write")

    assert contract["destructive"] is True
    assert contract["side_effect"] == "write"
    assert contract["supports_confirmation"] is False
    assert "path" in contract["input_schema"]["required"]
    assert "content" in contract["input_schema"]["required"]


def test_normalize_tool_contract_accepts_definition_dict_with_metadata():
    normalized = normalize_tool_contract(
        {
            "name": "custom.echo",
            "description": "Echo input.",
            "input_schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
        metadata={"category": "custom", "side_effect": "none"},
    )

    assert normalized["name"] == "custom.echo"
    assert normalized["category"] == "custom"
    assert normalized["builtin"] is False
    assert validate_tool_contract(normalized)["valid"] is True
