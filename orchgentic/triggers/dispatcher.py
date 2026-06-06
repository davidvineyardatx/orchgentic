from pathlib import Path
from orchgentic.config.loader import load_agent
from orchgentic.providers.factory import create_provider
from orchgentic.agents.assistant import AssistantAgent

def agent_path(name):
    n = name.lower()
    return Path("agents") / (n if n.endswith(".yaml") else f"{n}.yaml")

class TriggerDispatcher:
    async def dispatch(self, event, debug=False):
        cfg = load_agent(agent_path(event.target_agent))
        agent = AssistantAgent(cfg, create_provider(cfg.provider))
        metadata = {
            "trigger_id": event.trigger_id,
            "trigger_type": event.trigger_type,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat()
        }
        return await agent.run(event.task, debug=debug, metadata=metadata)
