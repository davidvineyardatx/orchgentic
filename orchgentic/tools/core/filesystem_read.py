from pathlib import Path
from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class FileSystemReadTool(BaseTool):
    name = "filesystem.read"
    description = "Read a text file from the local workspace."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file."}
        },
        "required": ["path"]
    }

    async def execute(self, path: str, **kwargs) -> ToolResult:
        p = Path(path)
        if not p.exists():
            return ToolResult(False, self.name, error=f"File not found: {path}")
        if not p.is_file():
            return ToolResult(False, self.name, error=f"Path is not a file: {path}")
        return ToolResult(True, self.name, data=p.read_text(encoding="utf-8", errors="ignore"))
