from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .beta2_checks import (
    StabilizationReport,
    check_knowledge_config,
    check_memory_config,
    check_provider_config,
)


@dataclass(frozen=True)
class Beta2DoctorResult:
    """Doctor-style result for existing RAG, memory, and provider layers."""

    agent_name: str
    agent_path: str | None
    reports: tuple[StabilizationReport, ...]

    @property
    def ok(self) -> bool:
        return all(report.ok for report in self.reports)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_path": self.agent_path,
            "ok": self.ok,
            "reports": [report.to_dict() for report in self.reports],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def _load_yaml(path: str | Path) -> Mapping[str, Any]:
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, Mapping) else {}


def doctor_agent_layers(
    config_or_path: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path | None = None,
    agent_name: str | None = None,
) -> Beta2DoctorResult:
    """Run beta.2 stabilization checks against an agent config."""

    agent_path: str | None = None

    if isinstance(config_or_path, (str, Path)):
        agent_path = str(config_or_path)
        config = _load_yaml(config_or_path)
        if project_root is None:
            project_root = Path(config_or_path).parent.parent
    else:
        config = config_or_path

    resolved_name = (
        agent_name
        or str(config.get("name") or config.get("id") or "unknown-agent")
    )

    reports = (
        check_provider_config(config),
        check_memory_config(config, project_root=project_root),
        check_knowledge_config(config, project_root=project_root),
    )

    return Beta2DoctorResult(
        agent_name=resolved_name,
        agent_path=agent_path,
        reports=reports,
    )


def format_beta2_doctor_text(result: Beta2DoctorResult) -> str:
    """Format beta.2 doctor output for human-readable CLI display."""

    status = "OK" if result.ok else "FAILED"
    lines = [
        f"Agent: {result.agent_name}",
        f"Status: {status}",
    ]

    if result.agent_path:
        lines.append(f"Path: {result.agent_path}")

    lines.append("")
    lines.append("Layer checks:")

    for report in result.reports:
        layer_status = "OK" if report.ok else "FAILED"
        lines.append(f"  {report.layer}: {layer_status}")

        for issue in report.errors:
            location = f" ({issue.path})" if issue.path else ""
            lines.append(f"    ERROR {issue.code}{location}: {issue.message}")

        for issue in report.warnings:
            location = f" ({issue.path})" if issue.path else ""
            lines.append(f"    WARNING {issue.code}{location}: {issue.message}")

    return "\\n".join(lines)
