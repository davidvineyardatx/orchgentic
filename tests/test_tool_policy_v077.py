import pytest
from orchgentic.runtime.tool_policy import ToolPolicyRuntime, ToolPolicyError
class Agent:
    tool_policies = {"gmail.send":{"enabled":True,"send_policy":{"mode":"restricted","allowed_addresses":["owner@example.com"],"allowed_domains":["company.com"]}},"gmail.delete":{"enabled":False}}
def test_disabled_tool_policy():
    with pytest.raises(ToolPolicyError): ToolPolicyRuntime(Agent()).enforce_enabled("gmail.delete")
def test_gmail_send_allowed_address(): ToolPolicyRuntime(Agent()).enforce_gmail_send("owner@example.com")
def test_gmail_send_allowed_domain(): ToolPolicyRuntime(Agent()).enforce_gmail_send("person@company.com")
def test_gmail_send_blocked():
    with pytest.raises(ToolPolicyError): ToolPolicyRuntime(Agent()).enforce_gmail_send("person@other.com")
