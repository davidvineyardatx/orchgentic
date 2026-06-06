from orchgentic.agents.manager import AgentManager
from orchgentic.core.exceptions import PermissionError, OrchestrationError
class DelegationRuntime:
    def __init__(self, agent_manager=None):
        self.agent_manager = agent_manager or AgentManager()
    async def delegate(self, source_agent_config, target_agent, task, context=None, depth=0):
        delegation = source_agent_config.delegation
        if not delegation.enabled: raise PermissionError(f'Delegation is not enabled for {source_agent_config.name}')
        allowed = [a.lower() for a in delegation.allowed_agents]
        if allowed and target_agent.lower() not in allowed: raise PermissionError(f'{source_agent_config.name} is not allowed to delegate to {target_agent}')
        if depth >= delegation.max_depth: raise OrchestrationError(f'Delegation depth exceeded for {source_agent_config.name}')
        return await self.agent_manager.run_agent(target_agent, task, debug=False, metadata={'delegated_by': source_agent_config.name, 'delegation_depth': depth+1, 'context': context or {}})
