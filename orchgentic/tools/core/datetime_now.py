from datetime import datetime, timezone
from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class DateTimeNowTool(BaseTool):
    name = "datetime.now"
    description = "Return the current UTC date and time."
    input_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(True, self.name, data=datetime.now(timezone.utc).isoformat())
