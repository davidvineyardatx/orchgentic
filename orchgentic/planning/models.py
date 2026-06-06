from dataclasses import dataclass
@dataclass(slots=True)
class PlanStep:
    id: str
    description: str
    completed: bool = False
@dataclass(slots=True)
class Plan:
    goal: str
    steps: list[PlanStep]
    def to_text(self):
        return "\n".join([f"Goal: {self.goal}", ""] + [f"{i}. [{'done' if s.completed else 'pending'}] {s.description}" for i, s in enumerate(self.steps, 1)])
