from dataclasses import dataclass, field
from datetime import datetime
from .enums import RunStatus

@dataclass(slots=True)
class AgentIdentity:
    id: str
    name: str
    role: str = "Assistant"
    description: str = ""

@dataclass(slots=True)
class RunState:
    run_id: str
    status: RunStatus = RunStatus.CREATED
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    planner_steps: int = 0
    reflection_count: int = 0
    def complete(self): self.status = RunStatus.COMPLETED; self.ended_at = datetime.utcnow()
    def fail(self): self.status = RunStatus.FAILED; self.ended_at = datetime.utcnow()
