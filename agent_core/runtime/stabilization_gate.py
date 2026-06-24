from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from agent_core.stabilization.beta2_runtime import assert_agent_layers_ready


def validate_agent_runtime_layers(
    agent_config: Mapping[str, Any] | str | Path,
    *,
    project_root: str | Path | None = None,
    agent_name: str | None = None,
) -> None:
    """Validate existing provider, memory, and knowledge layers before runtime execution."""

    assert_agent_layers_ready(
        agent_config,
        project_root=project_root,
        agent_name=agent_name,
    )
