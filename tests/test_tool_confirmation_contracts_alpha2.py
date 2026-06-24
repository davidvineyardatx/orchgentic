from orchgentic.tools.contracts import (
    get_builtin_confirmation_contracts,
    get_confirmation_contract,
    validate_confirmation_contract,
)


def test_confirmation_contract_inventory_has_stable_shape():
    contracts = get_builtin_confirmation_contracts()

    assert len(contracts) == 14

    for contract in contracts:
        assert "name" in contract
        assert "supports_confirmation" in contract
        assert "requires_confirm_input" in contract
        assert "confirm_input_type" in contract
        assert "destructive" in contract
        assert "side_effect" in contract
        assert "requires_policy_check" in contract
        assert "confirmation_required_by_contract" in contract
        assert "confirmation_recommended" in contract
        assert contract["runtime_behavior_changed"] is False


def test_gmail_confirmation_contracts_require_boolean_confirm_input():
    for tool_name in ["gmail.draft", "gmail.send", "gmail.reply", "gmail.delete"]:
        contract = get_confirmation_contract(tool_name)

        assert contract["supports_confirmation"] is True
        assert contract["requires_confirm_input"] is True
        assert contract["confirm_input_type"] == "boolean"
        assert contract["requires_policy_check"] is True
        assert validate_confirmation_contract(tool_name)["valid"] is True


def test_destructive_gmail_contracts_require_confirmation_by_contract():
    for tool_name in ["gmail.send", "gmail.reply", "gmail.delete"]:
        contract = get_confirmation_contract(tool_name)

        assert contract["destructive"] is True
        assert contract["confirmation_required_by_contract"] is True
        assert contract["confirmation_recommended"] is True


def test_filesystem_write_current_confirmation_baseline_is_locked_without_behavior_change():
    result = validate_confirmation_contract("filesystem.write")
    contract = result["confirmation"]

    assert contract["destructive"] is True
    assert contract["side_effect"] == "write"
    assert contract["supports_confirmation"] is False
    assert contract["confirmation_required_by_contract"] is False
    assert contract["confirmation_recommended"] is True
    assert result["runtime_behavior_changed"] is False
    assert any(item["code"] == "destructive_without_confirmation" for item in result["warnings"])


def test_read_only_tools_do_not_require_confirmation():
    for tool_name in ["datetime.now", "datetime.local", "filesystem.read", "memory.search", "knowledge.search"]:
        contract = get_confirmation_contract(tool_name)

        assert contract["destructive"] is False
        assert contract["supports_confirmation"] is False
        assert contract["confirmation_required_by_contract"] is False
        assert contract["runtime_behavior_changed"] is False
