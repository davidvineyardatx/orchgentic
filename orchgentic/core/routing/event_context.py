from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class EventType(str, Enum):
    MANUAL = "manual"
    HEARTBEAT = "heartbeat"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class EventContext:
    event_type: str = EventType.MANUAL.value
    source: str = "cli"
    task: str | None = None
    target_agent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EventRoute:
    event_type: str
    autonomy: str
    require_extra_policy_checks: bool
    confidence: float
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventContextRouter:
    """Adds event awareness to route decisions.

    Manual CLI work can be interactive. Heartbeat and webhook events are
    autonomous, so they should be more conservative about sends, deletes,
    external side effects, and confirmation-dependent tools.
    """

    def classify(self, context: EventContext | dict[str, Any] | None = None) -> EventRoute:
        if context is None:
            context = EventContext()
        elif isinstance(context, dict):
            context = EventContext(**context)

        event_type = (context.event_type or EventType.UNKNOWN.value).lower()

        if event_type == EventType.MANUAL.value:
            return EventRoute(event_type, "interactive", False, 0.95, ["manual_interactive_run"], context.metadata)

        if event_type == EventType.HEARTBEAT.value:
            return EventRoute(event_type, "autonomous_scheduled", True, 0.90, ["heartbeat_autonomous_run"], context.metadata)

        if event_type == EventType.WEBHOOK.value:
            return EventRoute(event_type, "autonomous_external_event", True, 0.88, ["webhook_external_event"], context.metadata)

        if event_type == EventType.SCHEDULED.value:
            return EventRoute(event_type, "autonomous_scheduled", True, 0.88, ["scheduled_autonomous_run"], context.metadata)

        return EventRoute(event_type or EventType.UNKNOWN.value, "unknown", True, 0.50, ["unknown_event_context"], context.metadata)
