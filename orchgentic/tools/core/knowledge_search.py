from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class KnowledgeSearchTool(BaseTool):
    name = "knowledge.search"
    description = "Search the agent knowledge base."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    }

    def __init__(self, knowledge=None):
        self.knowledge = knowledge

    async def execute(self, query: str, limit: int = 5, **kwargs) -> ToolResult:
        if self.knowledge is None:
            return ToolResult(False, self.name, error="Knowledge manager is not attached.")

        results = await self.knowledge.search(query, limit)
        data = []
        for score, row in results:
            _id, source, chunk, _embedding, _metadata, _timestamp = row
            data.append({"score": score, "source": source, "chunk": chunk})

        return ToolResult(True, self.name, data=data)
