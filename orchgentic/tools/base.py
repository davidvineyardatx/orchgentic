from abc import ABC, abstractmethod
from orchgentic.tools.schemas import ToolDefinition, ToolResult

class BaseTool(ABC):
    name: str = "tool"
    description: str = "Base tool"
    input_schema: dict = {"type": "object", "properties": {}}

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
        )

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError
