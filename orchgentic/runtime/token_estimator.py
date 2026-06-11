from dataclasses import dataclass

DEFAULT_CHARS_PER_TOKEN = 4
DEFAULT_COMPLETION_TOKENS = 300

def estimate_tokens(text: object, chars_per_token: int = DEFAULT_CHARS_PER_TOKEN) -> int:
    if text is None:
        return 0
    value = str(text)
    if not value:
        return 0
    chars_per_token = max(int(chars_per_token or DEFAULT_CHARS_PER_TOKEN), 1)
    return max(1, len(value) // chars_per_token)

@dataclass
class TokenSavingsEstimate:
    system_prompt_tokens: int = 0
    memory_context_tokens: int = 0
    tool_context_tokens: int = 0
    task_tokens: int = 0
    expected_completion_tokens: int = DEFAULT_COMPLETION_TOKENS

    @property
    def total(self) -> int:
        return self.system_prompt_tokens + self.memory_context_tokens + self.tool_context_tokens + self.task_tokens + self.expected_completion_tokens

    def to_dict(self) -> dict:
        return {
            "system_prompt_tokens": self.system_prompt_tokens,
            "memory_context_tokens": self.memory_context_tokens,
            "tool_context_tokens": self.tool_context_tokens,
            "task_tokens": self.task_tokens,
            "expected_completion_tokens": self.expected_completion_tokens,
            "total": self.total,
        }

def estimate_route_savings(
    system_prompt: object = "",
    memory_context: object = "",
    tool_context: object = "",
    task: object = "",
    expected_completion_tokens: int = DEFAULT_COMPLETION_TOKENS,
    chars_per_token: int = DEFAULT_CHARS_PER_TOKEN,
) -> TokenSavingsEstimate:
    return TokenSavingsEstimate(
        system_prompt_tokens=estimate_tokens(system_prompt, chars_per_token),
        memory_context_tokens=estimate_tokens(memory_context, chars_per_token),
        tool_context_tokens=estimate_tokens(tool_context, chars_per_token),
        task_tokens=estimate_tokens(task, chars_per_token),
        expected_completion_tokens=max(int(expected_completion_tokens or 0), 0),
    )
