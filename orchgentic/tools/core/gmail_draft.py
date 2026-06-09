from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.connectors.gmail.client import create_draft
from orchgentic.runtime.tool_policy import ToolPolicyRuntime
class GmailDraftTool(BaseTool):
    name="gmail.draft"; description="Create a Gmail draft for a named Gmail connection. Does not send."
    input_schema={"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"},"connection":{"type":"string"}},"required":["to","subject","body"]}
    def __init__(self, agent_config=None): self.agent_config=agent_config; self.policy=ToolPolicyRuntime(agent_config)
    def _connection(self, c=None):
        if c: return c
        g=getattr(self.agent_config,"gmail",None); return g.get("connection","default") if isinstance(g,dict) else "default"
    async def execute(self,to:str,subject:str,body:str,connection:str|None=None,**kwargs):
        try:
            self.policy.enforce_enabled(self.name); d=create_draft(self._connection(connection),to,subject,body)
            return ToolResult(True,self.name,data={"draft_id":d.get("id"),"message_id":(d.get("message") or {}).get("id"),"status":"draft_created"})
        except Exception as exc: return ToolResult(False,self.name,error=str(exc))
