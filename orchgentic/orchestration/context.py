from dataclasses import dataclass, field
from typing import Any
@dataclass(slots=True)
class SharedContext:
    values: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    def add_message(self, sender, recipient, content):
        self.messages.append({'sender': sender, 'recipient': recipient, 'content': content})
    def to_text(self):
        lines = [f"{m['sender']} -> {m['recipient']}: {m['content']}" for m in self.messages]
        lines += [f'{k}: {v}' for k, v in self.values.items()]
        return '\n'.join(lines)
