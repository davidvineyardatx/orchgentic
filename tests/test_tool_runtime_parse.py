from orchgentic.tools.runtime import ToolRuntime

def test_parse_final():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision('{"action":"final","answer":"done"}')
    assert parsed["action"] == "final"
    assert parsed["answer"] == "done"

def test_parse_plain_text_fallback():
    runtime = ToolRuntime(registry=None)
    parsed = runtime.parse_decision("hello")
    assert parsed["action"] == "final"
