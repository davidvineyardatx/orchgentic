from dataclasses import dataclass, field
from typing import Any
import re

@dataclass
class PrefetchStep:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    result_key: str | None = None

@dataclass
class PrefetchPlan:
    matched: bool
    reason: str = ""
    steps: list[PrefetchStep] = field(default_factory=list)

class ToolPrefetchPlanner:
    """
    Detects safe deterministic data-fetch operations that should run before LLM reasoning.

    This is intentionally conservative. It should only prefetch data when:
    - a clear tool is requested
    - required arguments are explicit
    - the follow-up request requires LLM reasoning
    """

    LLM_REQUIRED_TERMS = [
        "summarize",
        "summary",
        "analyse",
        "analyze",
        "explain",
        "rewrite",
        "classify",
        "recommend",
        "compare",
        "interpret",
        "generate",
    ]

    def plan(self, task: str) -> PrefetchPlan:
        original = (task or "").strip()
        text = original.lower()

        if not text:
            return PrefetchPlan(False, "Empty task")

        if not any(term in text for term in self.LLM_REQUIRED_TERMS):
            return PrefetchPlan(False, "No LLM-required term detected")

        gmail_read = self._gmail_read(original, text)
        if gmail_read:
            return gmail_read

        return PrefetchPlan(False, "No prefetchable tool found")

    def _gmail_read(self, original: str, text: str) -> PrefetchPlan | None:
        if "gmail" not in text and "email" not in text and "message" not in text:
            return None
        if "read" not in text and "open" not in text and "show" not in text:
            return None

        match = re.search(r'\b(?:message_id|message id|id)\s*[=:]?\s*([A-Za-z0-9_-]{8,})', original, re.IGNORECASE)
        if not match:
            match = re.search(r'\b([a-fA-F0-9]{12,})\b', original)

        if not match:
            return None

        return PrefetchPlan(
            matched=True,
            reason="Prefetch Gmail message before LLM reasoning",
            steps=[
                PrefetchStep(
                    tool="gmail.read",
                    arguments={"message_id": match.group(1)},
                    result_key="gmail_message",
                )
            ],
        )

def build_prefetch_context(task: str, results: dict[str, Any]) -> str:
    lines = [
        "The user asked:",
        task,
        "",
        "Relevant tool results were fetched before reasoning.",
        "Use ONLY the fetched tool result content below for factual claims about the fetched data.",
        "",
    ]

    for key, value in results.items():
        lines.append(f"## Tool Result: {key}")
        lines.append(str(value))
        lines.append("")

    lines.append("Now answer the user's request using the fetched tool result.")
    return "\\n".join(lines)
