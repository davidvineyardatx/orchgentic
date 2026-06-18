import time

from orchgentic.runtime.token_estimator import estimate_route_savings
from orchgentic.orchestration.context import SharedContext
from orchgentic.core.exceptions import TeamError
from orchgentic.runtime.preflight import CapabilityPreflight
from orchgentic.orchestration.synthesis_guardrails import (
    build_member_task,
    build_synthesis_task,
    sanitize_final_answer,
    extract_answer_for_handoff,
)


def build_team_quality_trace_data(members_count: int, quality) -> dict:
    """Build trace-safe team quality metadata.

    Older team-runner code expected ``SynthesisQualityResult.warnings``, but
    the guardrail result exposes ``notes`` and ``to_dict()``. Keep the legacy
    ``quality_warnings`` key as an alias so existing dashboard/export consumers
    do not break, while avoiding AttributeError during team completion tracing.
    """
    notes = getattr(quality, "warnings", None)
    if notes is None:
        notes = getattr(quality, "notes", None)
    notes = notes or []

    data = {
        "members": members_count,
        "quality_notes": notes,
        "quality_warnings": notes,
    }

    to_dict = getattr(quality, "to_dict", None)
    if callable(to_dict):
        data["quality"] = to_dict()

    return data


def _role_label(name: str) -> str:
    value = (name or "").strip()
    lower = value.lower()
    if "research" in lower:
        return "Researcher"
    if "writer" in lower:
        return "Writer"
    if "review" in lower:
        return "Reviewer"
    if "manager" in lower or "orchestrator" in lower:
        return "Manager"
    return value or "Team member"


def build_deterministic_team_plan(team_config, task: str) -> str:
    """Create a local, deterministic team plan from team configuration.

    This avoids spending an external LLM call just to decide common team-role
    assignments for known teams. Specialist agents can still use an LLM for
    their actual work when needed.
    """
    members = list(getattr(team_config, "members", []) or [])
    lines = [
        f"Deterministic team plan for {team_config.name}.",
        f"Task: {task}",
        "Assignments:",
    ]
    for member in members:
        role = _role_label(member)
        lower = role.lower()
        if lower == "researcher":
            contribution = "gather and verify relevant facts, context, examples, and source-labeled findings."
        elif lower == "writer":
            contribution = "draft the response from the team handoff context and organize it clearly for the requested audience."
        elif lower == "reviewer":
            contribution = "review the draft for clarity, completeness, consistency, and usefulness."
        else:
            contribution = "contribute according to the agent role and the team task."
        lines.append(f"- {member}: {contribution}")
    lines.append("Synthesis: combine member outputs into a clear final response using only current team outputs.")
    return "\n".join(lines)


def build_deterministic_team_routing_trace_data(team_config, task: str, plan: str) -> dict:
    savings = estimate_route_savings(
        system_prompt=f"You are orchestrating team {team_config.name}.",
        task=task,
        tool_context={"members": list(getattr(team_config, "members", []) or [])},
        expected_completion_tokens=300,
    )
    return {
        "routing_mode": "deterministic_team_role_routing",
        "reason": "Known team roles were assigned from team configuration without asking an external LLM to plan basic orchestration.",
        "savings_reason": "deterministic_team_role_routing_bypassed_manager_llm_planning",
        "local_llm_eligible": True,
        "external_llm_avoided": True,
        "team": team_config.name,
        "orchestrator": team_config.orchestrator,
        "members": list(getattr(team_config, "members", []) or []),
        "plan_preview": plan[:500],
        "estimated_savings_breakdown": savings.to_dict(),
    }


def tool_decision_policy_for_team_member(member: str) -> dict:
    role = _role_label(member).lower()
    if role == "researcher":
        return {
            "tool_decision_policy": "skip",
            "tool_decision_policy_event_name": "deterministic_researcher_tool_routing",
            "estimated_tool_decision_iterations_saved": 3,
            "tool_decision_policy_reason": (
                "Researcher should follow the deterministic research role contract instead of repeatedly asking "
                "an external LLM whether research tools are needed. Basic research-planning/tool-decision "
                "LLM calls are skipped by default; the researcher can still use the LLM for research-oriented "
                "generation from current task and handoff context."
            ),
        }
    if role == "writer":
        return {
            "tool_decision_policy": "skip",
            "tool_decision_policy_event_name": "deterministic_tool_decision_policy",
            "estimated_tool_decision_iterations_saved": 1,
            "tool_decision_policy_reason": "Writer should draft from current team handoff context; basic tool-decision LLM calls are skipped by default.",
        }
    if role == "reviewer":
        return {
            "tool_decision_policy": "skip",
            "tool_decision_policy_event_name": "deterministic_tool_decision_policy",
            "estimated_tool_decision_iterations_saved": 1,
            "tool_decision_policy_reason": "Reviewer should review current team handoff context; basic tool-decision LLM calls are skipped by default.",
        }
    return {
        "tool_decision_policy": "allow",
        "tool_decision_policy_reason": "No deterministic team-member policy matched this role.",
    }


class TeamRunner:
    def __init__(self, agent_manager=None):
        # Import AgentManager lazily so tests and pure helper imports do not require
        # optional provider SDKs such as groq/openai until an agent actually runs.
        from orchgentic.agents.manager import AgentManager
        from orchgentic.agents.registry import AgentRegistry

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

    async def run_team(self, team_config, task: str | None = None, debug: bool = False, preflight: bool = True, tracer=None):
        team_task = task or team_config.task
        team_started = time.perf_counter()

        def _team_failed(exc: Exception):
            if tracer:
                tracer.event(
                    "team.failed",
                    component="team",
                    name=team_config.name,
                    status="failed",
                    message=str(exc),
                    duration_ms=round((time.perf_counter() - team_started) * 1000, 2),
                    data={"error_type": type(exc).__name__},
                )

        if tracer:
            tracer.event(
                "team.started",
                component="team",
                name=team_config.name,
                status="started",
                message="Team execution started.",
                data={
                    "team": team_config.name,
                    "orchestrator": team_config.orchestrator,
                    "members": list(team_config.members),
                },
            )

        try:
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

            orchestrator_answer = build_deterministic_team_plan(team_config, team_task)
            routing_data = build_deterministic_team_routing_trace_data(team_config, team_task, orchestrator_answer)
            if tracer:
                tracer.event(
                    "routing.bypassed",
                    component="routing",
                    name="deterministic_team_role_routing",
                    status="completed",
                    message="Deterministic team role routing bypassed external LLM manager planning.",
                    estimated_tokens_saved=routing_data["estimated_savings_breakdown"]["total"],
                    token_source="estimated",
                    data=routing_data,
                )
                tracer.event(
                    "team.member.completed",
                    component="team",
                    name=team_config.orchestrator,
                    status="completed",
                    message="Orchestrator planning completed deterministically from team configuration.",
                    data={"role": "orchestrator", "routing_mode": "deterministic_team_role_routing"},
                )
            shared.add_message(team_config.orchestrator, "team", orchestrator_answer)
            outputs.append({
                "agent": team_config.orchestrator,
                "role": "orchestrator",
                "output": orchestrator_answer,
            })

            for member in team_config.members:
                if member == team_config.orchestrator:
                    continue

                member_task = build_member_task(team_task, shared.to_text(), member)

                member_started = time.perf_counter()
                if tracer:
                    tracer.event("team.member.started", component="team", name=member, status="started", data={"role": "member"})
                try:
                    result = await self.agent_manager.run_agent(
                        member,
                        member_task,
                        debug=debug,
                        metadata={
                            "team": team_config.name,
                            "role": "member",
                            "team_role": _role_label(member).lower(),
                            **tool_decision_policy_for_team_member(member),
                        },
                        preflight=False,
                        tracer=tracer,
                    )
                except Exception as exc:
                    if tracer:
                        tracer.event("team.member.failed", component="team", name=member, status="failed", message=str(exc), duration_ms=round((time.perf_counter() - member_started) * 1000, 2), data={"role": "member", "error_type": type(exc).__name__})
                    raise
                if tracer:
                    tracer.event("team.member.completed", component="team", name=member, status="completed", duration_ms=round((time.perf_counter() - member_started) * 1000, 2), data={"role": "member"})
                member_answer = extract_answer_for_handoff(result)
                shared.add_message(member, "team", member_answer)
                outputs.append({
                    "agent": member,
                    "role": "member",
                    "output": member_answer,
                })

            synthesis_task = build_synthesis_task(team_task, shared.to_text())
            synthesis_started = time.perf_counter()
            if tracer:
                tracer.event("team.synthesis.started", component="team", name=team_config.orchestrator, status="started", data={"role": "synthesis"})
            try:
                final = await self.agent_manager.run_agent(
                    team_config.orchestrator,
                    synthesis_task,
                    debug=debug,
                    metadata={
                        "team": team_config.name,
                        "role": "synthesis",
                        "team_role": "synthesis",
                        "memory_policy": "current_team_outputs_only",
                        "tool_decision_policy": "skip",
                        "tool_decision_policy_reason": "Team synthesis should combine current team outputs directly; basic tool-decision LLM calls are skipped by default.",
                    },
                    preflight=False,
                    tracer=tracer,
                )
            except Exception as exc:
                if tracer:
                    tracer.event("team.synthesis.failed", component="team", name=team_config.orchestrator, status="failed", message=str(exc), duration_ms=round((time.perf_counter() - synthesis_started) * 1000, 2), data={"role": "synthesis", "error_type": type(exc).__name__})
                raise
            if tracer:
                tracer.event("team.synthesis.completed", component="team", name=team_config.orchestrator, status="completed", duration_ms=round((time.perf_counter() - synthesis_started) * 1000, 2), data={"role": "synthesis"})

            final_answer = extract_answer_for_handoff(final)
            quality = sanitize_final_answer(final_answer)
            final = quality.answer

            if tracer:
                tracer.event(
                    "team.completed",
                    component="team",
                    name=team_config.name,
                    status="completed",
                    message="Team execution completed.",
                    duration_ms=round((time.perf_counter() - team_started) * 1000, 2),
                    data=build_team_quality_trace_data(len(outputs), quality),
                )

            return {
                "team": team_config.name,
                "task": team_task,
                "outputs": outputs,
                "final": final,
            }
        except Exception as exc:
            _team_failed(exc)
            raise
