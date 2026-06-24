from orchgentic.tools.contracts import (
    get_builtin_runtime_confirmation_consistency,
    get_runtime_confirmation_consistency,
)


GMAIL_CONFIRMATION_TOOLS = {
    "gmail.draft",
    "gmail.send",
    "gmail.reply",
    "gmail.delete",
}


def test_runtime_confirmation_consistency_inventory_is_stable():
    results = get_builtin_runtime_confirmation_consistency()

    assert len(results) == 14

    for item in results:
        assert "contract_supports_confirmation" in item
        assert "runtime_supports_confirmation" in item
        assert "runtime_confirm_argument" in item
        assert "consistent" in item
        assert item["runtime_behavior_changed"] is False


def test_gmail_confirmation_runtime_matches_frozen_contract():
    for tool_name in GMAIL_CONFIRMATION_TOOLS:
        item = get_runtime_confirmation_consistency(tool_name)

        assert item["contract_supports_confirmation"] is True
        assert item["contract_requires_confirm_input"] is True
        assert item["runtime_supports_confirmation"] is True
        assert item["runtime_confirm_argument"] is True
        assert item["consistent"] is True
        assert item["runtime_behavior_changed"] is False


def test_read_only_tools_remain_without_confirmation_runtime():
    for tool_name in ["datetime.now", "datetime.local", "filesystem.read", "memory.search", "knowledge.search"]:
        item = get_runtime_confirmation_consistency(tool_name)

        assert item["contract_supports_confirmation"] is False
        assert item["runtime_supports_confirmation"] is False
        assert item["runtime_confirm_argument"] is False
        assert item["consistent"] is True
        assert item["runtime_behavior_changed"] is False


def test_filesystem_write_current_runtime_baseline_is_documented_not_changed():
    item = get_runtime_confirmation_consistency("filesystem.write")

    assert item["contract_supports_confirmation"] is False
    assert item["runtime_supports_confirmation"] is False
    assert item["runtime_behavior_changed"] is False
    assert any("destructive without confirmation" in note for note in item["notes"])


def test_delegate_agent_policy_check_baseline_does_not_claim_confirmation_runtime():
    item = get_runtime_confirmation_consistency("delegate.agent")

    assert item["contract_supports_confirmation"] is False
    assert item["runtime_supports_confirmation"] is False
    assert item["contract_requires_policy_check"] is True
    assert item["runtime_behavior_changed"] is False
