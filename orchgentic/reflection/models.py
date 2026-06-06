from dataclasses import dataclass
@dataclass(slots=True)
class ReflectionResult:
    success: bool
    confidence: float
    notes: list[str]
    def to_text(self):
        return f"success={self.success}, confidence={self.confidence:.2f}, notes={'; '.join(self.notes) if self.notes else 'No issues found.'}"
