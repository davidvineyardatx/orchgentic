from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re

class ReasoningLevel(str, Enum):
    DETERMINISTIC = "deterministic"
    LOCAL_REASONER = "local_reasoner"
    EXTERNAL_LLM = "external_llm"

class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class LocalReasoningDecision:
    intent: str | None = None
    reasoning_level: ReasoningLevel = ReasoningLevel.EXTERNAL_LLM
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
    confidence: float = 0.0
    should_escalate: bool = True
    escalation_reason: str = ""
    signals: dict[str, Any] = field(default_factory=dict)

class LocalReasoner:
    """
    Lightweight local orchestration reasoner.

    This is not a full assistant. It classifies intent, estimates complexity,
    scores confidence, and recommends whether external LLM escalation is justified.
    """

    GENERATION_TERMS = [
        "write", "draft", "compose", "create content", "generate", "rewrite",
        "polish", "make this sound", "linkedin post", "email response"
    ]

    ANALYSIS_TERMS = [
        "summarize", "summary", "analyze", "analyse", "explain", "compare",
        "recommend", "interpret", "classify", "review", "evaluate"
    ]

    AMBIGUITY_TERMS = [
        "something", "anything", "whatever", "best", "maybe", "should i",
        "what do you think", "help me decide"
    ]

    SIMPLE_OPERATION_PATTERNS = {
        "datetime": [
            r"\bwhat\s+time\b",
            r"\bwhat\s+is\s+(?:the\s+)?(?:local\s+)?time\b",
            r"\blocal\s+time\b",
            r"\bcurrent\s+(?:local\s+)?time\b",
            r"\bwhat day\b",
            r"\bcurrent date\b",
        ],
        "gmail_delete": [
            r"\bdelete\s+(?:gmail\s+)?(?:email\s+)?message\b",
            r"\bdelete\s+(?:an?\s+)?(?:email|gmail)\b",
            r"\btrash\s+(?:an?\s+)?(?:email|gmail)\b",
            r"\bremove\s+(?:an?\s+)?(?:email|gmail)\b",
        ],
        "gmail_send": [
            r"\bsend\s+(?:an?\s+)?email\b",
            r"\bsend\s+(?:a\s+)?gmail\b",
            r"\bemail\s+to\b",
        ],
        "gmail_reply": [r"\breply\s+to\s+(?:an?\s+)?email\b", r"\breply\s+to\s+gmail\b", r"\brespond\s+to\s+(?:an?\s+)?email\b"],
        "gmail_draft": [r"\bdraft\s+(?:an?\s+)?email\b", r"\bdraft\s+(?:a\s+)?gmail\b", r"\bdraft\s+a\s+reply\b"],
        "gmail_search": [r"\bsearch gmail\b", r"\bfind gmail\b", r"\blist gmail\b", r"\bsearch email\b", r"\bfind email\b"],
        "gmail_read": [
            r"\bread\s+(?:gmail\s+)?(?:email\s+)?message\b",
            r"\bread\s+(?:an?\s+)?(?:email|gmail)\b",
            r"(?<!delete\s)\bgmail message id\b",
            r"(?<!delete\s)\bmessage id\b",
        ],
        "memory_search": [r"\bmemory search\b", r"\bsearch memory\b"],
        "knowledge_search": [r"\bknowledge search\b", r"\bsearch knowledge\b"],
    }

    def classify(self, task: str, available_tools: list[str] | None = None) -> LocalReasoningDecision:
        text = (task or "").strip()
        lowered = text.lower()
        available_tools = available_tools or []

        if not lowered:
            return LocalReasoningDecision(
                intent="empty",
                reasoning_level=ReasoningLevel.EXTERNAL_LLM,
                complexity=ComplexityLevel.LOW,
                confidence=0.0,
                should_escalate=True,
                escalation_reason="Empty task",
                signals={"empty": True},
            )

        signals = self._signals(lowered, available_tools)
        confidence = self.score_confidence(signals)
        complexity = self.estimate_complexity(signals)
        intent = self._intent(signals)
        should_escalate, reason = self.should_escalate_decision(signals, confidence, complexity)

        if should_escalate:
            level = ReasoningLevel.EXTERNAL_LLM
        elif signals.get("simple_operation"):
            level = ReasoningLevel.DETERMINISTIC
        else:
            level = ReasoningLevel.LOCAL_REASONER

        return LocalReasoningDecision(
            intent=intent,
            reasoning_level=level,
            complexity=complexity,
            confidence=confidence,
            should_escalate=should_escalate,
            escalation_reason=reason,
            signals=signals,
        )

    def _signals(self, text: str, available_tools: list[str]) -> dict[str, Any]:
        has_generation = any(term in text for term in self.GENERATION_TERMS)
        has_analysis = any(term in text for term in self.ANALYSIS_TERMS)
        has_ambiguity = any(term in text for term in self.AMBIGUITY_TERMS)

        simple_intents = []
        for name, patterns in self.SIMPLE_OPERATION_PATTERNS.items():
            if any(re.search(pattern, text) for pattern in patterns):
                simple_intents.append(name)

        simple_intents = self._apply_intent_precedence(text, simple_intents)

        argument_complete = bool(
            re.search(r"\bmessage id\s+[A-Za-z0-9_-]{8,}\b", text)
            or re.search(r"\b[A-Fa-f0-9]{12,}\b", text)
            or "what time" in text
            or "what is the local time" in text
            or "what is local time" in text
            or "local time" in text
            or "current time" in text
            or "current local time" in text
            or '"' in text
        )

        tool_mentions = [tool for tool in available_tools if tool.lower() in text]
        word_count = len(text.split())

        return {
            "has_generation": has_generation,
            "has_analysis": has_analysis,
            "has_ambiguity": has_ambiguity,
            "simple_operation": bool(simple_intents),
            "simple_intents": simple_intents,
            "argument_complete": argument_complete,
            "tool_mentions": tool_mentions,
            "word_count": word_count,
            "available_tool_count": len(available_tools),
        }

    def _apply_intent_precedence(self, text: str, simple_intents: list[str]) -> list[str]:
        """Resolve overlapping intent signals so action verbs win over object nouns.

        Example: "delete gmail message id ..." contains "message id", but the
        destructive verb should resolve to gmail_delete rather than gmail_read.
        """
        if not simple_intents:
            return simple_intents

        destructive_gmail = bool(re.search(r"\b(delete|trash|remove)\b", text)) and bool(
            re.search(r"\b(gmail|email|message)\b", text)
        )
        if destructive_gmail:
            return [intent for intent in simple_intents if intent != "gmail_read"]

        send_gmail = bool(re.search(r"\bsend\b", text)) and bool(
            re.search(r"\b(email|gmail|message)\b", text) or re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        )
        if send_gmail:
            return [intent for intent in simple_intents if intent != "gmail_read"]

        reply_gmail = bool(re.search(r"\b(reply|respond)\b", text)) and bool(re.search(r"\b(email|gmail|message)\b", text))
        if reply_gmail:
            return [intent for intent in simple_intents if intent != "gmail_read"]

        draft_gmail = bool(re.search(r"\bdraft\b", text)) and bool(re.search(r"\b(email|gmail|reply|message)\b", text))
        if draft_gmail:
            return [intent for intent in simple_intents if intent != "gmail_read"]

        return simple_intents

    def score_confidence(self, signals: dict[str, Any]) -> float:
        score = 0.35
        if signals.get("simple_operation"):
            score += 0.30
        if signals.get("argument_complete"):
            score += 0.20
        if signals.get("tool_mentions"):
            score += 0.10
        if signals.get("has_ambiguity"):
            score -= 0.25
        if signals.get("has_generation"):
            score -= 0.20
        if signals.get("has_analysis"):
            score -= 0.15
        if signals.get("word_count", 0) > 30:
            score -= 0.10
        return max(0.0, min(1.0, round(score, 2)))

    def estimate_complexity(self, signals: dict[str, Any]) -> ComplexityLevel:
        if signals.get("has_generation") or signals.get("has_analysis"):
            return ComplexityLevel.HIGH
        if signals.get("has_ambiguity") or signals.get("word_count", 0) > 30:
            return ComplexityLevel.MEDIUM
        if signals.get("simple_operation"):
            return ComplexityLevel.LOW
        return ComplexityLevel.MEDIUM

    def should_escalate_decision(self, signals: dict[str, Any], confidence: float, complexity: ComplexityLevel) -> tuple[bool, str]:
        if signals.get("has_generation"):
            return True, "Generation request requires external LLM"
        if signals.get("has_analysis"):
            return True, "Analysis or summarization request requires external LLM"
        if complexity == ComplexityLevel.HIGH:
            return True, "High complexity request"
        if confidence < 0.70:
            return True, "Confidence below local threshold"
        return False, "Local/deterministic path sufficient"

    def _intent(self, signals: dict[str, Any]) -> str:
        simple_intents = signals.get("simple_intents") or []
        if simple_intents:
            return simple_intents[0]
        if signals.get("has_generation"):
            return "generation"
        if signals.get("has_analysis"):
            return "analysis"
        if signals.get("has_ambiguity"):
            return "ambiguous"
        return "general"
