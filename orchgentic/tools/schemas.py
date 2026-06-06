from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

@dataclass(slots=True)
class ToolCall:
    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ToolResult:
    success: bool
    tool_name: str
    data: Any = None
    error: str | None = None
