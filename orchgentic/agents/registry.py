from pathlib import Path
from orchgentic.config.loader import load_agent
class AgentRegistry:
    def __init__(self, agents_dir='agents'):
        self.agents_dir = Path(agents_dir)
    def list_agent_files(self):
        return sorted(self.agents_dir.glob('*.yaml')) if self.agents_dir.exists() else []
    def list_agents(self):
        return [load_agent(p) for p in self.list_agent_files()]
    def get_agent_path(self, name):
        normalized = name.lower()
        direct = self.agents_dir / (normalized if normalized.endswith('.yaml') else f'{normalized}.yaml')
        if direct.exists(): return direct
        for p in self.list_agent_files():
            cfg = load_agent(p)
            if cfg.name.lower() == normalized or cfg.id.lower() == normalized: return p
        return None
    def get_agent(self, name):
        p = self.get_agent_path(name)
        return load_agent(p) if p else None
