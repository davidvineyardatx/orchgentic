from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class MemorySearchTool(BaseTool):
    name = "memory.search"
    description = "Search this agent's conversation memory."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "agent_id": {"type": "string"},
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["query", "agent_id"]
    }

    def __init__(self, memory=None):
        self.memory = memory

    async def execute(self, query: str, agent_id: str, limit: int = 5, **kwargs) -> ToolResult:
        if self.memory is None:
            return ToolResult(False, self.name, error="Memory manager is not attached.")
        rows = self.memory.search(query, agent_id, limit)
        data = [
            {"id": row[0], "agent_id": row[1], "role": row[2], "content": row[3], "timestamp": row[4]}
            for row in rows
        ]
        return ToolResult(True, self.name, data=data)
