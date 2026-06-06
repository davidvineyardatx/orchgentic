from pathlib import Path
import yaml
from .schemas import AgentConfig, TriggerConfig, TeamConfig
from orchgentic.core.exceptions import ConfigurationError

def load_agent(path):
    path = Path(path)
    if not path.exists(): raise ConfigurationError(f"Agent config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if 'agent' not in data: raise ConfigurationError(f"Invalid agent config. Missing 'agent' key: {path}")
    return AgentConfig(**data['agent'])

def load_trigger(path):
    path = Path(path)
    if not path.exists(): raise ConfigurationError(f"Trigger config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if 'trigger' not in data: raise ConfigurationError(f"Invalid trigger config. Missing 'trigger' key: {path}")
    return TriggerConfig(**data['trigger'])

def load_all_triggers(directory='triggers'):
    d = Path(directory)
    if not d.exists(): return []
    return [load_trigger(p) for p in sorted(d.glob('*.yaml'))]

def load_team(path):
    path = Path(path)
    if not path.exists(): raise ConfigurationError(f"Team config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if 'team' not in data: raise ConfigurationError(f"Invalid team config. Missing 'team' key: {path}")
    return TeamConfig(**data['team'])

def load_all_teams(directory='teams'):
    d = Path(directory)
    if not d.exists(): return []
    return [load_team(p) for p in sorted(d.glob('*.yaml'))]
