from orchgentic.tools.core.gmail_delete import GmailDeleteTool
from orchgentic.tools.core.gmail_reply import GmailReplyTool
from orchgentic.tools.core.gmail_send import GmailSendTool
from orchgentic.tools.core.gmail_search import GmailSearchTool
from orchgentic.tools.core.gmail_read import GmailReadTool
from orchgentic.tools.core.gmail_draft import GmailDraftTool
from orchgentic.registry import Registry
from orchgentic.tools.core.datetime_now import DateTimeNowTool
from orchgentic.tools.core.datetime_local import DateTimeLocalTool
from orchgentic.tools.core.filesystem_read import FileSystemReadTool
from orchgentic.tools.core.filesystem_write import FileSystemWriteTool
from orchgentic.tools.core.web_request import WebRequestTool
from orchgentic.tools.core.memory_search import MemorySearchTool
from orchgentic.tools.core.knowledge_search import KnowledgeSearchTool
from orchgentic.tools.core.delegate_agent import DelegateAgentTool

class ToolRegistry(Registry):
    def definitions(self, allowed: list[str] | None = None):
        tools = list(self.items.values())
        if allowed:
            allowed_set = {name.lower() for name in allowed}
            tools = [tool for tool in tools if tool.name.lower() in allowed_set]
        return [tool.definition().to_dict() for tool in tools]

def default_tool_registry(memory=None, knowledge=None, source_agent_config=None) -> ToolRegistry:
    registry = ToolRegistry()

    for tool in [
        DateTimeNowTool(),
        DateTimeLocalTool(agent_config=source_agent_config),
        FileSystemReadTool(),
        FileSystemWriteTool(),
        WebRequestTool(),
        MemorySearchTool(memory),
        KnowledgeSearchTool(knowledge),
        DelegateAgentTool(source_agent_config=source_agent_config),
        GmailSearchTool(agent_config=source_agent_config),
        GmailReadTool(agent_config=source_agent_config),
        GmailDraftTool(agent_config=source_agent_config),
        GmailSendTool(agent_config=source_agent_config),
        GmailReplyTool(agent_config=source_agent_config),
        GmailDeleteTool(agent_config=source_agent_config),
    ]:
        registry.register(tool.name, tool)

    return registry
