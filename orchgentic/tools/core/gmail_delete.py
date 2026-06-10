from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.connectors.gmail.client import trash_message
from orchgentic.connectors.gmail.oauth import GmailConnectionError
from orchgentic.runtime.tool_policy import ToolPolicyRuntime, ToolPolicyError

class GmailDeleteTool(BaseTool):
    name = "gmail.delete"
    description = "Move a Gmail message to Trash through a named Gmail connection with confirmation enforcement."
    input_schema = {
        "type": "object",
        "properties": {
            "message_id": {"type": "string"},
            "confirm": {"type": "boolean"},
            "connection": {"type": "string"}
        },
        "required": ["message_id"]
    }

    def __init__(self, agent_config=None):
        self.agent_config = agent_config
        self.policy = ToolPolicyRuntime(agent_config)

    def _connection(self, explicit=None):
        gmail_cfg = getattr(self.agent_config, "gmail", None)

        # Agent configuration ALWAYS wins over model-provided arguments.
        # This prevents an LLM from inventing credential names such as
        # "primary", "default", or "user" and overriding the agent YAML.
        if isinstance(gmail_cfg, dict):
            configured = gmail_cfg.get("connection")
            if configured:
                return configured

        if gmail_cfg is not None:
            configured = getattr(gmail_cfg, "connection", None)
            if configured:
                return configured

        # Explicit runtime argument is only honored when the agent has no
        # configured Gmail connection.
        if explicit:
            return explicit

        return "default"


    async def execute(self, message_id: str, confirm: bool = False, connection: str | None = None, **kwargs):
        try:
            self.policy.enforce_action(self.name, confirm)
            trashed = trash_message(self._connection(connection), message_id)
            return ToolResult(True, self.name, data={"message_id": trashed.get("id"), "thread_id": trashed.get("threadId"), "status": "moved_to_trash"})
        except (GmailConnectionError, ToolPolicyError, Exception) as exc:
            return ToolResult(False, self.name, error=str(exc))
