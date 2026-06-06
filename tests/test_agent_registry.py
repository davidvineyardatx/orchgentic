from orchgentic.agents.registry import AgentRegistry
def test_agent_registry_empty(tmp_path):
    registry=AgentRegistry(str(tmp_path/'agents')); assert registry.list_agents()==[]
