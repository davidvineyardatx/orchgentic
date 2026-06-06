import pytest
from orchgentic.runtime.time_context import TimeContextResolver
from orchgentic.config.schemas import AgentConfig
from orchgentic.tools.core.datetime_local import DateTimeLocalTool

def test_agent_timezone_resolution():
    agent = AgentConfig(id="bob", name="Bob", timezone="America/Chicago")
    resolver = TimeContextResolver()
    assert resolver.resolve_timezone(agent_config=agent) == "America/Chicago"

def test_runtime_context_override():
    agent = AgentConfig(id="bob", name="Bob", timezone="America/Chicago")
    resolver = TimeContextResolver()
    assert resolver.resolve_timezone(
        runtime_context={"timezone": "Europe/London"},
        agent_config=agent,
    ) == "Europe/London"

@pytest.mark.asyncio
async def test_datetime_local_tool_uses_agent_timezone():
    agent = AgentConfig(id="bob", name="Bob", timezone="America/Chicago", locale="en-US")
    result = await DateTimeLocalTool(agent_config=agent).execute()
    assert result.success is True
    assert result.tool_name == "datetime.local"
    assert result.data["timezone"] == "America/Chicago"
