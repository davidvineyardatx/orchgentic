from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.connectors.gmail.client import read_message, extract_headers
from orchgentic.runtime.tool_policy import ToolPolicyRuntime
class GmailReadTool(BaseTool):
    name="gmail.read"; description="Read a Gmail message by message ID for a named Gmail connection."
    input_schema={"type":"object","properties":{"message_id":{"type":"string"},"connection":{"type":"string"}},"required":["message_id"]}
    def __init__(self, agent_config=None): self.agent_config=agent_config; self.policy=ToolPolicyRuntime(agent_config)
    def _connection(self, c=None):
        if c: return c
        g=getattr(self.agent_config,"gmail",None); return g.get("connection","default") if isinstance(g,dict) else "default"
    async def execute(self, message_id:str, connection:str|None=None, **kwargs):
        try:
            self.policy.enforce_enabled(self.name); m=read_message(self._connection(connection),message_id)
            return ToolResult(True,self.name,data={"id":m.get("id"),"thread_id":m.get("threadId"),"snippet":m.get("snippet"),"headers":extract_headers(m)})
        except Exception as exc: return ToolResult(False,self.name,error=str(exc))
