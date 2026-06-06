from pathlib import Path
from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class FileSystemWriteTool(BaseTool):
    name = "filesystem.write"
    description = "Write text content to a local workspace file."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["path", "content"]
    }

    async def execute(self, path: str, content: str, **kwargs) -> ToolResult:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return ToolResult(True, self.name, data=f"Wrote {len(content)} characters to {path}")
