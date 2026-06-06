from orchgentic.config.loader import load_team
def test_team_config_load(tmp_path):
    d=tmp_path/'teams'; d.mkdir(); p=d/'contentteam.yaml'
    p.write_text('team:\n  name: ContentTeam\n  orchestrator: Manager\n  members:\n    - Researcher\n    - Writer\n')
    cfg=load_team(p); assert cfg.name=='ContentTeam'; assert cfg.orchestrator=='Manager'
