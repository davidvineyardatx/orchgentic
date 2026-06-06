import httpx
from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class WebRequestTool(BaseTool):
    name = "web.request"
    description = "Make a simple HTTP request."
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "method": {"type": "string", "default": "GET"},
            "body": {"type": "object"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str, method: str = "GET", body: dict | None = None, **kwargs) -> ToolResult:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method.upper(), url, json=body)
            return ToolResult(True, self.name, data={
                "status_code": response.status_code,
                "body": response.text[:5000],
            })
