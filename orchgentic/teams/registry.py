from pathlib import Path
from orchgentic.config.loader import load_team
class TeamRegistry:
    def __init__(self, teams_dir='teams'):
        self.teams_dir = Path(teams_dir)
    def list_team_files(self): return sorted(self.teams_dir.glob('*.yaml')) if self.teams_dir.exists() else []
    def list_teams(self): return [load_team(p) for p in self.list_team_files()]
    def get_team_path(self, name):
        normalized = name.lower()
        direct = self.teams_dir / (normalized if normalized.endswith('.yaml') else f'{normalized}.yaml')
        if direct.exists(): return direct
        for p in self.list_team_files():
            cfg = load_team(p)
            if cfg.name.lower() == normalized: return p
        return None
    def get_team(self, name):
        p = self.get_team_path(name)
        return load_team(p) if p else None
