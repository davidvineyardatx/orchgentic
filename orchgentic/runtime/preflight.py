from orchgentic.runtime.requirements import RequirementDetector
from orchgentic.runtime.error_policy import RuntimeIssue, ErrorSeverity
from orchgentic.notifications.manager import NotificationManager

class CapabilityPreflight:
    def __init__(self, notifier: NotificationManager | None = None):
        self.detector = RequirementDetector()
        self.notifier = notifier or NotificationManager()

    def _agent_tools(self, agent_config) -> set[str]:
        explicit = set(agent_config.tools or [])
        capabilities = {cap for cap in (agent_config.capabilities or []) if "." in cap}
        return {tool.lower() for tool in explicit.union(capabilities)}

    def check_agent_task(self, agent_config, task: str) -> list[RuntimeIssue]:
        requirements = self.detector.detect(task)
        if not requirements.required_tools:
            return []

        available = self._agent_tools(agent_config)
        missing = sorted(tool for tool in requirements.required_tools if tool.lower() not in available)

        if not missing:
            return []

        suggestions = []
        for tool in missing:
            suggestions.append(
                f"Add '{tool}' to both tools and capabilities in agents/{agent_config.id}.yaml or the relevant agent YAML file."
            )

        return [
            RuntimeIssue(
                code="MISSING_REQUIRED_TOOL",
                severity=ErrorSeverity.SEVERE,
                message=f"Agent '{agent_config.name}' is missing required tool(s): {', '.join(missing)}",
                details={
                    "agent": agent_config.name,
                    "required_tools": missing,
                    "available_tools": sorted(available),
                    "reasons": requirements.reasons,
                },
                fix_suggestions=suggestions,
            )
        ]

    def check_team_task(self, team_config, agent_configs: list, task: str) -> list[RuntimeIssue]:
        requirements = self.detector.detect(task)
        if not requirements.required_tools:
            return []

        team_tool_map = {}
        for agent in agent_configs:
            team_tool_map[agent.name] = sorted(self._agent_tools(agent))

        team_available = set()
        for tools in team_tool_map.values():
            team_available.update(tool.lower() for tool in tools)

        missing_from_team = sorted(tool for tool in requirements.required_tools if tool.lower() not in team_available)

        # For team runs, we intentionally do NOT auto-route to some unrelated capable agent.
        # Users must configure the correct agent roles/tools explicitly.
        issues = []

        if missing_from_team:
            suggestions = [
                f"Add '{tool}' to the appropriate team member YAML, usually the role responsible for this task."
                for tool in missing_from_team
            ]

            issues.append(RuntimeIssue(
                code="TEAM_MISSING_REQUIRED_TOOL",
                severity=ErrorSeverity.SEVERE,
                message=f"Team '{team_config.name}' cannot complete this task because required tool(s) are missing: {', '.join(missing_from_team)}",
                details={
                    "team": team_config.name,
                    "required_tools": missing_from_team,
                    "team_tools": team_tool_map,
                    "reasons": requirements.reasons,
                },
                fix_suggestions=suggestions,
            ))

        # Role alignment check: Researcher-like agents should have web.request for live web/current data tasks.
        task_lower = (task or "").lower()
        needs_web = "web.request" in {tool.lower() for tool in requirements.required_tools}
        if needs_web:
            for agent in agent_configs:
                role_text = f"{agent.name} {agent.role} {agent.description}".lower()
                looks_like_researcher = any(word in role_text for word in ["research", "researcher", "analyst"])
                has_web = "web.request" in self._agent_tools(agent)

                if looks_like_researcher and not has_web:
                    issues.append(RuntimeIssue(
                        code="ROLE_TOOL_ALIGNMENT_WARNING",
                        severity=ErrorSeverity.WARNING,
                        message=f"Agent '{agent.name}' appears to be a research-oriented role but lacks web.request.",
                        details={
                            "agent": agent.name,
                            "role": agent.role,
                            "missing_tool": "web.request",
                        },
                        fix_suggestions=[
                            f"Add 'web.request' to tools and capabilities in agents/{agent.id}.yaml if this agent should perform live web research."
                        ],
                    ))

        return issues

    def raise_or_notify(self, issues: list[RuntimeIssue], *, context: dict | None = None) -> None:
        if not issues:
            return

        for issue in issues:
            self.notifier.handle_issue(issue, context=context or {})

        severe_issues = [issue for issue in issues if issue.severity in [ErrorSeverity.SEVERE, ErrorSeverity.CRITICAL]]
        if severe_issues:
            message = "\n\n".join(issue.to_text() for issue in severe_issues)
            raise RuntimeError(message)
