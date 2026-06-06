from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
@dataclass(slots=True)
class TriggerEvent:
    trigger_id: str
    trigger_type: str
    target_agent: str
    task: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
