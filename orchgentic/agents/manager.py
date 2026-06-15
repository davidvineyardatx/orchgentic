from orchgentic.agents.registry import AgentRegistry
from orchgentic.providers.factory import create_provider
from orchgentic.core.exceptions import ConfigurationError
from orchgentic.runtime.preflight import CapabilityPreflight

class AgentManager:
    def __init__(self, agents_dir: str = "agents"):
        self.registry = AgentRegistry(agents_dir)
        self.preflight = CapabilityPreflight()

    def list_agents(self):
        return self.registry.list_agents()

    def load_agent_config(self, name: str):
        cfg = self.registry.get_agent(name)
        if not cfg:
            raise ConfigurationError(f"Agent not found: {name}")
        return cfg

    def create_agent(self, name: str):
        # Lazy import prevents circular imports with delegation tools.
        from orchgentic.agents.assistant import AssistantAgent

        cfg = self.load_agent_config(name)
        provider = create_provider(cfg.provider)
        return AssistantAgent(cfg, provider)

    async def run_agent(self, name: str, task: str, *, debug: bool = False, metadata: dict | None = None, preflight: bool = True, tracer=None):
        cfg = self.load_agent_config(name)

        if preflight:
            issues = self.preflight.check_agent_task(cfg, task)
            self.preflight.raise_or_notify(issues, context={"agent": cfg.name, "task": task})

        agent = self.create_agent(name)
        return await agent.run(task, debug=debug, metadata=metadata, tracer=tracer)
