from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult
from orchgentic.connectors.gmail.client import send_message
from orchgentic.connectors.gmail.oauth import GmailConnectionError
from orchgentic.runtime.tool_policy import ToolPolicyRuntime, ToolPolicyError

class GmailSendTool(BaseTool):
    name = "gmail.send"
    description = "Send a Gmail message through a named Gmail connection with policy enforcement."
    input_schema = {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
            "confirm": {"type": "boolean"},
            "connection": {"type": "string"}
        },
        "required": ["to", "subject", "body"]
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


    async def execute(self, to: str, subject: str, body: str, confirm: bool = False, connection: str | None = None, **kwargs):
        try:
            self.policy.enforce_gmail_send(to, confirm=confirm)
            sent = send_message(self._connection(connection), to, subject, body)
            return ToolResult(True, self.name, data={"message_id": sent.get("id"), "thread_id": sent.get("threadId"), "status": "sent"})
        except (GmailConnectionError, ToolPolicyError, Exception) as exc:
            return ToolResult(False, self.name, error=str(exc))
