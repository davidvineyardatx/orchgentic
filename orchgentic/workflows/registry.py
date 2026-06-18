from __future__ import annotations

from pathlib import Path
import yaml

from .models import WorkflowBlueprint, WorkflowValidationError


class WorkflowRegistry:
    """Loads workflow blueprint YAML files from the workspace workflows folder."""

    def __init__(self, workflows_dir: str | Path = "workflows"):
        self.workflows_dir = Path(workflows_dir)

    def list_workflow_files(self) -> list[Path]:
        if not self.workflows_dir.exists():
            return []
        return sorted(self.workflows_dir.glob("*.workflow.yaml")) + sorted(self.workflows_dir.glob("*.workflow.yml"))

    def load_workflow(self, path: str | Path) -> WorkflowBlueprint:
        path = Path(path)
        if not path.exists():
            raise WorkflowValidationError(f"Workflow config not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return WorkflowBlueprint.from_dict(data, path=path)

    def list_workflows(self) -> list[WorkflowBlueprint]:
        return [self.load_workflow(path) for path in self.list_workflow_files()]

    def get_workflow_path(self, workflow_id: str) -> Path | None:
        normalized = workflow_id.strip().lower()
        direct_names = [
            f"{normalized}.workflow.yaml",
            f"{normalized}.workflow.yml",
            f"{normalized}.yaml",
            f"{normalized}.yml",
        ]
        for name in direct_names:
            candidate = self.workflows_dir / name
            if candidate.exists():
                return candidate
        for path in self.list_workflow_files():
            workflow = self.load_workflow(path)
            if workflow.id.lower() == normalized or workflow.name.lower() == normalized:
                return path
        return None

    def get_workflow(self, workflow_id: str) -> WorkflowBlueprint | None:
        path = self.get_workflow_path(workflow_id)
        return self.load_workflow(path) if path else None
