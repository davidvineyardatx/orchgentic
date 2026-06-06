from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ErrorSeverity(str, Enum):
    MINOR = "minor"
    WARNING = "warning"
    SEVERE = "severe"
    CRITICAL = "critical"

@dataclass(slots=True)
class RuntimeIssue:
    code: str
    severity: ErrorSeverity
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    fix_suggestions: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        parts = [
            f"{self.severity.value.upper()}: {self.message}",
            f"Code: {self.code}",
        ]

        if self.details:
            parts.append("Details:")
            for key, value in self.details.items():
                parts.append(f"- {key}: {value}")

        if self.fix_suggestions:
            parts.append("Suggested fix:")
            for suggestion in self.fix_suggestions:
                parts.append(f"- {suggestion}")

        return "\n".join(parts)

class RuntimePolicy:
    def __init__(self):
        self.actions = {
            ErrorSeverity.MINOR: ["log"],
            ErrorSeverity.WARNING: ["log", "dashboard"],
            ErrorSeverity.SEVERE: ["log", "dashboard", "notify", "halt"],
            ErrorSeverity.CRITICAL: ["log", "dashboard", "notify", "halt_runtime"],
        }

    def actions_for(self, severity: ErrorSeverity) -> list[str]:
        return self.actions.get(severity, ["log"])

    def should_halt(self, severity: ErrorSeverity) -> bool:
        return "halt" in self.actions_for(severity) or "halt_runtime" in self.actions_for(severity)
