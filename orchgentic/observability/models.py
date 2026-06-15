from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import json
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    if value is None:
        return "{}"
    try:
        return json.dumps(value, default=str, sort_keys=True)
    except TypeError:
        return json.dumps({"value": str(value)}, sort_keys=True)


def _json_loads(value: str | None) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {"value": value}


TOKEN_SOURCE_ACTUAL = "actual"
TOKEN_SOURCE_ESTIMATED = "estimated"
TOKEN_SOURCE_NOT_APPLICABLE = "not_applicable"
TOKEN_SOURCE_UNKNOWN = "unknown"

VALID_TOKEN_SOURCES = {
    TOKEN_SOURCE_ACTUAL,
    TOKEN_SOURCE_ESTIMATED,
    TOKEN_SOURCE_NOT_APPLICABLE,
    TOKEN_SOURCE_UNKNOWN,
}


@dataclass(slots=True)
class RunRecord:
    """Top-level record for one Orchgentic execution.

    A run is the outer container for an agent run, team run, tool run, trigger dispatch,
    or future workflow execution. Token fields intentionally track tokens only; no USD
    cost is stored in v0.8.0 because pricing data can be provider-specific, discounted,
    local, or unavailable.
    """

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_type: str = "agent"
    task: str = ""
    status: str = "running"
    agent_id: str | None = None
    agent_name: str | None = None
    team_id: str | None = None
    team_name: str | None = None
    provider: str | None = None
    model: str | None = None
    external_llm_used: bool = False
    started_at: str = field(default_factory=utc_now_iso)
    ended_at: str | None = None
    duration_ms: float | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_tokens_saved: int = 0
    token_source: str = TOKEN_SOURCE_NOT_APPLICABLE
    error_type: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["external_llm_used"] = bool(self.external_llm_used)
        return data

    def to_row(self) -> tuple:
        return (
            self.run_id,
            self.run_type,
            self.task,
            self.status,
            self.agent_id,
            self.agent_name,
            self.team_id,
            self.team_name,
            self.provider,
            self.model,
            1 if self.external_llm_used else 0,
            self.started_at,
            self.ended_at,
            self.duration_ms,
            int(self.input_tokens or 0),
            int(self.output_tokens or 0),
            int(self.total_tokens or 0),
            int(self.estimated_tokens_saved or 0),
            self.token_source if self.token_source in VALID_TOKEN_SOURCES else TOKEN_SOURCE_UNKNOWN,
            self.error_type,
            self.error_message,
            _json_dumps(self.metadata),
        )

    @classmethod
    def from_row(cls, row) -> "RunRecord":
        if row is None:
            raise ValueError("Cannot build RunRecord from empty row.")
        return cls(
            run_id=row["run_id"],
            run_type=row["run_type"],
            task=row["task"] or "",
            status=row["status"],
            agent_id=row["agent_id"],
            agent_name=row["agent_name"],
            team_id=row["team_id"],
            team_name=row["team_name"],
            provider=row["provider"],
            model=row["model"],
            external_llm_used=bool(row["external_llm_used"]),
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            duration_ms=row["duration_ms"],
            input_tokens=int(row["input_tokens"] or 0),
            output_tokens=int(row["output_tokens"] or 0),
            total_tokens=int(row["total_tokens"] or 0),
            estimated_tokens_saved=int(row["estimated_tokens_saved"] or 0),
            token_source=row["token_source"] or TOKEN_SOURCE_UNKNOWN,
            error_type=row["error_type"],
            error_message=row["error_message"],
            metadata=_json_loads(row["metadata"]),
        )


@dataclass(slots=True)
class TraceEvent:
    """Structured event describing what happened inside a run."""

    run_id: str
    event_type: str
    component: str
    name: str | None = None
    status: str = "completed"
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_event_id: str | None = None
    timestamp: str = field(default_factory=utc_now_iso)
    duration_ms: float | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_tokens_saved: int = 0
    token_source: str = TOKEN_SOURCE_NOT_APPLICABLE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_row(self) -> tuple:
        return (
            self.event_id,
            self.run_id,
            self.parent_event_id,
            self.timestamp,
            self.event_type,
            self.component,
            self.name,
            self.status,
            self.message,
            _json_dumps(self.data),
            self.duration_ms,
            int(self.input_tokens or 0),
            int(self.output_tokens or 0),
            int(self.total_tokens or 0),
            int(self.estimated_tokens_saved or 0),
            self.token_source if self.token_source in VALID_TOKEN_SOURCES else TOKEN_SOURCE_UNKNOWN,
        )

    @classmethod
    def from_row(cls, row) -> "TraceEvent":
        if row is None:
            raise ValueError("Cannot build TraceEvent from empty row.")
        return cls(
            event_id=row["event_id"],
            run_id=row["run_id"],
            parent_event_id=row["parent_event_id"],
            timestamp=row["timestamp"],
            event_type=row["event_type"],
            component=row["component"],
            name=row["name"],
            status=row["status"],
            message=row["message"],
            data=_json_loads(row["data"]),
            duration_ms=row["duration_ms"],
            input_tokens=int(row["input_tokens"] or 0),
            output_tokens=int(row["output_tokens"] or 0),
            total_tokens=int(row["total_tokens"] or 0),
            estimated_tokens_saved=int(row["estimated_tokens_saved"] or 0),
            token_source=row["token_source"] or TOKEN_SOURCE_UNKNOWN,
        )
