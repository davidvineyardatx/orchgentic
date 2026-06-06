from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid
@dataclass(slots=True)
class AgentMessage:
    sender: str
    recipient: str
    task: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
