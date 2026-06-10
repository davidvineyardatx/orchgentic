from dataclasses import dataclass, field
from typing import Any
import json
import requests

from orchgentic.runtime.router_policy import RouterPolicy

@dataclass
class LocalReasonerDecision:
    matched: bool = False
    intent: str | None = None
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_external_llm: bool = True
    reason: str = ""

class LocalReasoner:
    """
    Optional local mini reasoner for routing/classification only.

    The local reasoner suggests routing decisions. The runtime still validates:
    - tool existence
    - agent capabilities
    - tool policies
    - required args
    """

    def __init__(self, policy: RouterPolicy):
        self.policy = policy

    def enabled(self) -> bool:
        return bool(self.policy.local_reasoner.enabled)

    def decide(self, task: str, available_tools: list[str] | None = None) -> LocalReasonerDecision:
        if not self.enabled():
            return LocalReasonerDecision(
                matched=False,
                requires_external_llm=True,
                reason="Local reasoner disabled",
            )

        if self.policy.local_reasoner.provider != "openai_compatible":
            return LocalReasonerDecision(
                matched=False,
                requires_external_llm=True,
                reason=f"Unsupported local reasoner provider: {self.policy.local_reasoner.provider}",
            )

        return self._decide_openai_compatible(task, available_tools or [])

    def _decide_openai_compatible(self, task: str, available_tools: list[str]) -> LocalReasonerDecision:
        endpoint = self.policy.local_reasoner.endpoint.rstrip("/")
        url = f"{endpoint}/chat/completions"

        system = (
            "You are a low-cost routing classifier for an AI orchestration runtime. "
            "Return ONLY valid JSON. Do not explain. "
            "Choose a tool only when the request can be safely resolved with that tool. "
            "If the task requires summarization, creative writing, analysis, explanation, or ambiguous planning, set requires_external_llm=true."
        )

        user = {
            "task": task,
            "available_tools": available_tools,
            "schema": {
                "matched": "boolean",
                "intent": "string|null",
                "tool": "string|null",
                "arguments": "object",
                "confidence": "number 0..1",
                "requires_external_llm": "boolean",
                "reason": "string",
            },
        }

        payload = {
            "model": self.policy.local_reasoner.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user)},
            ],
            "temperature": self.policy.local_reasoner.temperature,
            "max_tokens": self.policy.local_reasoner.max_tokens,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.policy.local_reasoner.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            parsed = self._parse_json(content)
            return LocalReasonerDecision(
                matched=bool(parsed.get("matched", False)),
                intent=parsed.get("intent"),
                tool=parsed.get("tool"),
                arguments=parsed.get("arguments") or {},
                confidence=float(parsed.get("confidence", 0.0)),
                requires_external_llm=bool(parsed.get("requires_external_llm", True)),
                reason=str(parsed.get("reason", "")),
            )
        except Exception as exc:
            return LocalReasonerDecision(
                matched=False,
                confidence=0.0,
                requires_external_llm=True,
                reason=f"Local reasoner failed: {exc}",
            )

    def _parse_json(self, text: str) -> dict[str, Any]:
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= start:
            text = text[start:end + 1]
        return json.loads(text)
