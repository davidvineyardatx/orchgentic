from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.runtime.time_context import TimeContextResolver, TimeContextError

class DateTimeLocalTool(BaseTool):
    name = "datetime.local"
    description = "Return the current local date and time using the resolved Orchgentic time context."
    input_schema = {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Optional IANA timezone override, for example America/Chicago."
            }
        },
        "required": []
    }

    def __init__(self, agent_config=None):
        self.agent_config = agent_config
        self.resolver = TimeContextResolver()

    async def execute(self, timezone: str | None = None, **kwargs) -> ToolResult:
        try:
            timezone_name = timezone or self.resolver.resolve_timezone(agent_config=self.agent_config)
            locale = self.resolver.resolve_locale(agent_config=self.agent_config)
            data = self.resolver.now_local(timezone_name, locale=locale)
            return ToolResult(True, self.name, data=data)
        except TimeContextError as exc:
            return ToolResult(False, self.name, error=str(exc))
