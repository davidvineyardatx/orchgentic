from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


SUPPORTED_PROVIDER_TYPES = {"openai", "groq", "lmstudio", "lm_studio"}
SUPPORTED_KNOWLEDGE_STORES = {"local", "zilliz"}
SUPPORTED_MEMORY_STORES = {"sqlite", "local", "disabled"}


@dataclass(frozen=True)
class StabilizationIssue:
    """A single stabilization issue found in an agent/layer config."""

    code: str
    message: str
    severity: str = "error"
    path: str | None = None


@dataclass
class StabilizationReport:
    """Structured result for beta.2 layer stabilization checks."""

    layer: str
    issues: list[StabilizationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def warnings(self) -> list[StabilizationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def errors(self) -> list[StabilizationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    def add_error(self, code: str, message: str, path: str | None = None) -> None:
        self.issues.append(StabilizationIssue(code=code, message=message, severity="error", path=path))

    def add_warning(self, code: str, message: str, path: str | None = None) -> None:
        self.issues.append(StabilizationIssue(code=code, message=message, severity="warning", path=path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "ok": self.ok,
            "errors": [issue.__dict__ for issue in self.errors],
            "warnings": [issue.__dict__ for issue in self.warnings],
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def check_provider_config(config: Mapping[str, Any]) -> StabilizationReport:
    """Validate provider settings without calling an external LLM."""

    report = StabilizationReport(layer="provider")
    provider = _as_mapping(config.get("provider"))

    provider_type = provider.get("type")
    model = provider.get("model")

    if not provider_type:
        report.add_error("provider.type.missing", "Provider type is required.", "provider.type")
        return report

    provider_type_normalized = str(provider_type).strip().lower()

    if provider_type_normalized not in SUPPORTED_PROVIDER_TYPES:
        report.add_error(
            "provider.type.unsupported",
            f"Unsupported provider type: {provider_type!r}.",
            "provider.type",
        )

    if not model:
        report.add_error("provider.model.missing", "Provider model is required.", "provider.model")

    if provider_type_normalized in {"lmstudio", "lm_studio"}:
        base_url = provider.get("base_url") or provider.get("api_base")
        if not base_url:
            report.add_warning(
                "provider.lmstudio.base_url.missing",
                "LM Studio provider has no base_url/api_base configured; default localhost behavior may be used.",
                "provider.base_url",
            )

    fallback = _as_mapping(config.get("fallback_provider"))
    if fallback:
        fallback_type = fallback.get("type")
        fallback_model = fallback.get("model")
        if not fallback_type:
            report.add_error(
                "fallback_provider.type.missing",
                "Fallback provider type is required when fallback_provider is configured.",
                "fallback_provider.type",
            )
        elif str(fallback_type).strip().lower() not in SUPPORTED_PROVIDER_TYPES:
            report.add_error(
                "fallback_provider.type.unsupported",
                f"Unsupported fallback provider type: {fallback_type!r}.",
                "fallback_provider.type",
            )
        if not fallback_model:
            report.add_error(
                "fallback_provider.model.missing",
                "Fallback provider model is required when fallback_provider is configured.",
                "fallback_provider.model",
            )

    return report


def check_memory_config(config: Mapping[str, Any], project_root: str | Path | None = None) -> StabilizationReport:
    """Validate memory settings and common SQLite path issues."""

    report = StabilizationReport(layer="memory")
    memory = _as_mapping(config.get("memory"))

    enabled = memory.get("enabled", False)
    if enabled is False:
        report.add_warning("memory.disabled", "Memory is disabled for this agent.", "memory.enabled")
        return report

    store = str(memory.get("store", "sqlite")).strip().lower()
    if store not in SUPPORTED_MEMORY_STORES:
        report.add_error("memory.store.unsupported", f"Unsupported memory store: {store!r}.", "memory.store")

    db_path = memory.get("db_path")
    if store in {"sqlite", "local"}:
        if not db_path:
            report.add_error("memory.db_path.missing", "Memory db_path is required for local/SQLite memory.", "memory.db_path")
        else:
            path = Path(str(db_path))
            if not path.is_absolute() and project_root is not None:
                path = Path(project_root) / path
            parent = path.parent
            if str(parent) and not parent.exists():
                report.add_warning(
                    "memory.db_path.parent_missing",
                    f"Memory database parent directory does not exist yet: {parent}",
                    "memory.db_path",
                )

    recent_messages = memory.get("recent_messages")
    if recent_messages is not None:
        try:
            if int(recent_messages) < 0:
                report.add_error(
                    "memory.recent_messages.invalid",
                    "memory.recent_messages must be zero or greater.",
                    "memory.recent_messages",
                )
        except (TypeError, ValueError):
            report.add_error(
                "memory.recent_messages.invalid",
                "memory.recent_messages must be an integer.",
                "memory.recent_messages",
            )

    return report


def check_knowledge_config(config: Mapping[str, Any], project_root: str | Path | None = None) -> StabilizationReport:
    """Validate knowledge/RAG settings without requiring embeddings or network access."""

    report = StabilizationReport(layer="knowledge")
    knowledge = _as_mapping(config.get("knowledge"))

    enabled = knowledge.get("enabled", False)
    if enabled is False:
        report.add_warning("knowledge.disabled", "Knowledge/RAG is disabled for this agent.", "knowledge.enabled")
        return report

    store = str(knowledge.get("store", "local")).strip().lower()
    if store not in SUPPORTED_KNOWLEDGE_STORES:
        report.add_error("knowledge.store.unsupported", f"Unsupported knowledge store: {store!r}.", "knowledge.store")

    top_k = knowledge.get("top_k", 5)
    try:
        parsed_top_k = int(top_k)
        if parsed_top_k <= 0:
            report.add_error("knowledge.top_k.invalid", "knowledge.top_k must be greater than zero.", "knowledge.top_k")
        elif parsed_top_k > 25:
            report.add_warning(
                "knowledge.top_k.high",
                "knowledge.top_k is high; this may increase token usage.",
                "knowledge.top_k",
            )
    except (TypeError, ValueError):
        report.add_error("knowledge.top_k.invalid", "knowledge.top_k must be an integer.", "knowledge.top_k")

    if store == "local":
        db_path = knowledge.get("db_path")
        if not db_path:
            report.add_error(
                "knowledge.db_path.missing",
                "Knowledge db_path is required for local knowledge storage.",
                "knowledge.db_path",
            )
        else:
            path = Path(str(db_path))
            if not path.is_absolute() and project_root is not None:
                path = Path(project_root) / path
            parent = path.parent
            if str(parent) and not parent.exists():
                report.add_warning(
                    "knowledge.db_path.parent_missing",
                    f"Knowledge database parent directory does not exist yet: {parent}",
                    "knowledge.db_path",
                )

    if store == "zilliz":
        collection = knowledge.get("collection")
        if not collection:
            report.add_error(
                "knowledge.zilliz.collection.missing",
                "Zilliz knowledge store requires a collection name.",
                "knowledge.collection",
            )

    return report


def check_agent_layer_config(config: Mapping[str, Any], project_root: str | Path | None = None) -> dict[str, Any]:
    """Run all beta.2 layer checks and return a combined doctor-style result."""

    reports = [
        check_provider_config(config),
        check_memory_config(config, project_root=project_root),
        check_knowledge_config(config, project_root=project_root),
    ]

    return {
        "ok": all(report.ok for report in reports),
        "reports": [report.to_dict() for report in reports],
    }
