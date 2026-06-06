from orchgentic.agents.manager import AgentManager
from orchgentic.agents.registry import AgentRegistry
from orchgentic.orchestration.context import SharedContext
from orchgentic.core.exceptions import TeamError
from orchgentic.runtime.preflight import CapabilityPreflight

class TeamRunner:
    def __init__(self, agent_manager: AgentManager | None = None):
        self.agent_manager = agent_manager or AgentManager()
        self.agent_registry = AgentRegistry()
        self.preflight = CapabilityPreflight()

    def _load_team_agent_configs(self, team_config):
        names = []
        if team_config.orchestrator:
            names.append(team_config.orchestrator)
        for member in team_config.members:
            if member not in names:
                names.append(member)

        configs = []
        for name in names:
            cfg = self.agent_registry.get_agent(name)
            if cfg:
                configs.append(cfg)
        return configs

    async def run_team(self, team_config, task: str | None = None, debug: bool = False, preflight: bool = True):
        team_task = task or team_config.task

        agent_configs = self._load_team_agent_configs(team_config)

        if preflight:
            issues = self.preflight.check_team_task(team_config, agent_configs, team_task)
            self.preflight.raise_or_notify(issues, context={"team": team_config.name, "task": team_task})

        shared = SharedContext()
        outputs = []

        if team_config.orchestrator not in team_config.members:
            members = [team_config.orchestrator, *team_config.members]
        else:
            members = list(team_config.members)

        if not members:
            raise TeamError(f"Team {team_config.name} has no members.")

        orchestrator_prompt = (
            f"You are orchestrating team {team_config.name}.\n"
            f"Team members: {', '.join(team_config.members)}\n"
            f"Task: {team_task}\n"
            "Decide what each team member should contribute."
        )

        orchestrator_output = await self.agent_manager.run_agent(
            team_config.orchestrator,
            orchestrator_prompt,
            debug=debug,
            metadata={"team": team_config.name, "role": "orchestrator"},
            preflight=False,
        )
        shared.add_message(team_config.orchestrator, "team", orchestrator_output)
        outputs.append({
            "agent": team_config.orchestrator,
            "role": "orchestrator",
            "output": orchestrator_output,
        })

        for member in team_config.members:
            if member == team_config.orchestrator:
                continue

            member_task = (
                f"Team task: {team_task}\n\n"
                f"Shared context so far:\n{shared.to_text()}\n\n"
                f"Provide your specialist contribution as {member}."
            )

            result = await self.agent_manager.run_agent(
                member,
                member_task,
                debug=debug,
                metadata={"team": team_config.name, "role": "member"},
                preflight=False,
            )
            shared.add_message(member, "team", result)
            outputs.append({
                "agent": member,
                "role": "member",
                "output": result,
            })

        synthesis_task = (
            f"Create a final team response for this task:\n{team_task}\n\n"
            f"Team outputs:\n{shared.to_text()}"
        )
        final = await self.agent_manager.run_agent(
            team_config.orchestrator,
            synthesis_task,
            debug=debug,
            metadata={"team": team_config.name, "role": "synthesis"},
            preflight=False,
        )

        return {
            "team": team_config.name,
            "task": team_task,
            "outputs": outputs,
            "final": final,
        }
