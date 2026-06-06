from orchgentic.runtime.preflight import CapabilityPreflight
from orchgentic.config.schemas import AgentConfig, TeamConfig

def test_agent_missing_web_request():
    agent = AgentConfig(id="researcher", name="Researcher", role="Research Specialist", tools=["knowledge.search"], capabilities=["knowledge.search"])
    issues = CapabilityPreflight().check_agent_task(agent, "Fetch https://example.com and summarize it")
    assert issues
    assert issues[0].code == "MISSING_REQUIRED_TOOL"
    assert issues[0].severity.value == "severe"

def test_team_missing_web_request():
    team = TeamConfig(name="ContentTeam", orchestrator="Manager", members=["Researcher"])
    agent = AgentConfig(id="researcher", name="Researcher", role="Research Specialist", tools=["knowledge.search"], capabilities=["knowledge.search"])
    issues = CapabilityPreflight().check_team_task(team, [agent], "Research the latest news online")
    assert any(issue.code == "TEAM_MISSING_REQUIRED_TOOL" for issue in issues)
