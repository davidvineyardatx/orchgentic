from dataclasses import dataclass, field
from typing import Any
from orchgentic.orchestration.synthesis_guardrails import extract_answer_for_handoff, format_team_outputs_for_prompt
@dataclass(slots=True)
class SharedContext:
    values: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    def add_message(self, sender, recipient, content):
        self.messages.append({'sender': sender, 'recipient': recipient, 'content': extract_answer_for_handoff(content)})
    def to_text(self):
        lines = [format_team_outputs_for_prompt(self.messages)] if self.messages else []
        lines += [f'{k}: {v}' for k, v in self.values.items()]
        return '\n'.join(line for line in lines if line)
