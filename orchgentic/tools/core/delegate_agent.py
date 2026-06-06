from orchgentic.tools.base import BaseTool
from orchgentic.tools.schemas import ToolResult

class DelegateAgentTool(BaseTool):
    name = "delegate.agent"
    description = "Delegate a task to another configured Orchgentic agent."
    input_schema = {
        "type": "object",
        "properties": {
            "agent": {"type": "string", "description": "Target agent name or id."},
            "task": {"type": "string", "description": "Task to delegate."},
            "context": {"type": "object", "description": "Optional context for the target agent."}
        },
        "required": ["agent", "task"]
    }

    def __init__(self, source_agent_config=None, agent_manager=None):
        self.source_agent_config = source_agent_config
        self.agent_manager = agent_manager

    def _get_agent_manager(self):
        if self.agent_manager is None:
            # Lazy import prevents circular import:
            # assistant -> tools.registry -> delegate_agent -> agents.manager -> assistant
            from orchgentic.agents.manager import AgentManager
            self.agent_manager = AgentManager()
        return self.agent_manager

    async def execute(self, agent: str, task: str, context: dict | None = None, **kwargs) -> ToolResult:
        if self.source_agent_config is not None:
            delegation = self.source_agent_config.delegation

            if not delegation.enabled:
                return ToolResult(False, self.name, error=f"Delegation is not enabled for {self.source_agent_config.name}")

            allowed = [name.lower() for name in delegation.allowed_agents]
            if allowed and agent.lower() not in allowed:
                return ToolResult(False, self.name, error=f"Delegation to {agent} is not allowed.")

        manager = self._get_agent_manager()
        result = await manager.run_agent(
            agent,
            task,
            debug=False,
            metadata={
                "delegated": True,
                "source_agent": self.source_agent_config.name if self.source_agent_config else None,
                "context": context or {},
            }
        )
        return ToolResult(True, self.name, data=result)
