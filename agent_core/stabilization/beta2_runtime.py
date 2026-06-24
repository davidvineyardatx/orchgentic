from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .beta2_doctor import Beta2DoctorResult, doctor_agent_layers


class AgentLayerStabilizationError(RuntimeError):
    """Raised when existing provider, memory, or knowledge config is not runtime-ready."""

    def __init__(self, result: Beta2DoctorResult):
        self.result = result
        super().__init__(build_runtime_failure_message(result))


def build_runtime_failure_message(result: Beta2DoctorResult) -> str:
    """Build a concise runtime-facing failure message."""

    lines = [
        f"Agent layer stabilization failed for {result.agent_name}.",
        "Fix the following configuration errors before running the agent:",
    ]

    for report in result.reports:
        for issue in report.errors:
            location = f" at {issue.path}" if issue.path else ""
            lines.append(f"- [{report.layer}] {issue.code}{location}: {issue.message}")

    return "\n".join(lines)


def assert_agent_layers_ready(
    config_or_path: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path | None = None,
    agent_name: str | None = None,
) -> Beta2DoctorResult:
    """Fail fast when existing RAG, memory, or provider layers are not ready."""

    result = doctor_agent_layers(
        config_or_path,
        project_root=project_root,
        agent_name=agent_name,
    )

    if not result.ok:
        raise AgentLayerStabilizationError(result)

    return result
