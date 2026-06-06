from orchgentic.tools.runtime import ToolRuntime

def test_parse_tool_json_with_prose_before():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision(
        'To find out what day it is, I will call the datetime.now tool.\n\n'
        '{"action":"tool","tool":"datetime.now","arguments":{}}'
    )
    assert parsed["action"] == "tool"
    assert parsed["tool"] == "datetime.now"

def test_parse_tool_json_in_markdown_fence():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision(
        '```json\n{"action":"tool","tool":"datetime.now","arguments":{}}\n```'
    )
    assert parsed["action"] == "tool"
    assert parsed["tool"] == "datetime.now"

def test_parse_final_json_with_prose_before():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision(
        'Here is the answer:\n{"action":"final","answer":"Today is Friday."}'
    )
    assert parsed["action"] == "final"
    assert parsed["answer"] == "Today is Friday."

def test_plain_text_fallback_is_final():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision("I cannot help with that.")
    assert parsed["action"] == "final"
