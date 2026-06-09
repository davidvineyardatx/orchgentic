from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.connectors.gmail.client import search_messages
from orchgentic.runtime.tool_policy import ToolPolicyRuntime
class GmailSearchTool(BaseTool):
    name="gmail.search"; description="Search Gmail messages for a named Gmail connection."
    input_schema={"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer"},"connection":{"type":"string"}},"required":["query"]}
    def __init__(self, agent_config=None): self.agent_config=agent_config; self.policy=ToolPolicyRuntime(agent_config)
    def _connection(self, c=None):
        if c: return c
        g=getattr(self.agent_config,"gmail",None); return g.get("connection","default") if isinstance(g,dict) else "default"
    async def execute(self, query:str, max_results:int=10, connection:str|None=None, **kwargs):
        try:
            self.policy.enforce_enabled(self.name)
            return ToolResult(True,self.name,data={"messages":search_messages(self._connection(connection),query,max_results)})
        except Exception as exc: return ToolResult(False,self.name,error=str(exc))
