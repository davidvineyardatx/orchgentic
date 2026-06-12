from dataclasses import dataclass, field
from typing import Any
import re
from orchgentic.runtime.router_policy import load_router_policy

@dataclass
class RouteStep:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    result_key: str | None = None

@dataclass
class RouteDecision:
    matched: bool
    intent: str | None = None
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_llm: bool = True
    reason: str = ""
    route_type: str = "single_tool"
    steps: list[RouteStep] = field(default_factory=list)
    formatter: str | None = None

class DeterministicRouter:
    """
    Conservative deterministic routing for obvious operational requests.

    v0.7.10 expands:
    - Gmail argument extraction
    - basic multi-tool chains
    - deterministic formatter selection
    """

    def route(self, task: str, agent_config=None) -> RouteDecision:
        original = (task or "").strip()
        text = original.lower()
        policy = load_router_policy()

        if not policy.enabled:
            return RouteDecision(False, requires_llm=True, reason="Deterministic router disabled by policy")

        if not text:
            return RouteDecision(False, requires_llm=True, reason="Empty task")

        if self._requires_llm(text, policy):
            return RouteDecision(False, requires_llm=True, reason="Router policy requires LLM/local reasoner fallback")

        route = (
            self._time(text)
            or self._gmail_search_subjects(original, text)
            or self._gmail_search_count(original, text)
            or self._gmail_search(original, text)
            or self._gmail_read(original, text)
            or self._gmail_draft(original, text)
            or self._gmail_send(original, text)
        )

        if route:
            return route

        return RouteDecision(False, requires_llm=True, reason="No deterministic match")

    def _requires_llm(self, text: str, policy) -> bool:
        return any(term.lower() in text for term in (policy.fallback_to_llm_terms or []))

    def _time(self, text: str):
        patterns = [
            r"\bwhat\s+time\s+is\s+it\b",
            r"\bwhat\s+is\s+(?:the\s+)?(?:local\s+)?time\b",
            r"\bwhat(?:'s|\s+is)\s+(?:the\s+)?(?:local\s+)?time\b",
            r"\blocal\s+time\b",
            r"\bcurrent\s+(?:local\s+)?time\b",
            r"\btell\s+me\s+(?:the\s+)?(?:local\s+)?time\b",
            r"\bwhat\s+day\s+is\s+it\b",
            r"\bwhat\s+is\s+today\b",
            r"\bwhat\s+date\s+is\s+it\b",
            r"\bcurrent\s+day\b",
            r"\bcurrent\s+date\b",
        ]
        if any(re.search(p, text) for p in patterns):
            return RouteDecision(
                True,
                "datetime.local",
                "datetime.local",
                {},
                0.98,
                False,
                "Direct date/time request",
                formatter="datetime.local",
            )
        return None

    def _gmail_search_subjects(self, original: str, text: str):
        if not self._mentions_mail(text):
            return None
        if not any(w in text for w in ["subject", "subjects", "subject lines", "headers"]):
            return None
        query = self._build_gmail_query(original, text)
        if not query:
            return None

        max_results = self._extract_limit(text) or 10
        return RouteDecision(
            matched=True,
            intent="gmail.subjects",
            confidence=0.88,
            requires_llm=False,
            reason="Gmail search plus subject-line formatting request",
            route_type="multi_tool",
            steps=[
                RouteStep("gmail.search", {"query": query, "max_results": max_results}, "search"),
                RouteStep("gmail.read", {"message_id": "$search.messages[].id"}, "messages"),
            ],
            formatter="gmail.subjects",
        )

    def _gmail_search_count(self, original: str, text: str):
        if not self._mentions_mail(text):
            return None
        if "count" not in text and "how many" not in text:
            return None
        query = self._build_gmail_query(original, text)
        if not query:
            return None

        max_results = self._extract_limit(text) or 25
        return RouteDecision(
            True,
            "gmail.count",
            "gmail.search",
            {"query": query, "max_results": max_results},
            0.90,
            False,
            "Gmail count request",
            formatter="gmail.count",
        )

    def _gmail_search(self, original: str, text: str):
        if not self._mentions_mail(text):
            return None
        if not any(w in text for w in ["search", "find", "list", "show", "check"]):
            return None

        query = self._build_gmail_query(original, text)
        if query:
            args = {"query": query}
            limit = self._extract_limit(text)
            if limit:
                args["max_results"] = limit

            return RouteDecision(
                True,
                "gmail.search",
                "gmail.search",
                args,
                0.92,
                False,
                "Direct Gmail search request",
                formatter="gmail.search",
            )
        return None

    def _gmail_read(self, original: str, text: str):
        if "read" not in text and "open" not in text and "show" not in text:
            return None
        if "gmail" not in text and "email" not in text and "message" not in text:
            return None

        match = re.search(r'\b(?:message_id|message id|id)\s*[=:]?\s*([A-Za-z0-9_-]{8,})', original, re.IGNORECASE)
        if not match:
            match = re.search(r'\b([a-fA-F0-9]{12,})\b', original)

        if match:
            return RouteDecision(
                True,
                "gmail.read",
                "gmail.read",
                {"message_id": match.group(1)},
                0.94,
                False,
                "Direct Gmail read request",
                formatter="gmail.read",
            )
        return None

    def _gmail_draft(self, original: str, text: str):
        if "draft" not in text or not self._mentions_mail(text):
            return None
        to = self._email(original)
        subject = self._field(original, "subject")
        body = self._field(original, "body") or self._field(original, "message")
        if to and subject and body:
            return RouteDecision(
                True,
                "gmail.draft",
                "gmail.draft",
                {"to": to, "subject": subject, "body": body},
                0.90,
                False,
                "Exact Gmail draft fields provided",
                formatter="gmail.draft",
            )
        return None

    def _gmail_send(self, original: str, text: str):
        if "send" not in text or not self._mentions_mail(text):
            return None
        to = self._email(original)
        subject = self._field(original, "subject")
        body = self._field(original, "body") or self._field(original, "message")
        confirm = "confirm=true" in text or "confirmed" in text or "with confirmation" in text
        if to and subject and body:
            return RouteDecision(
                True,
                "gmail.send",
                "gmail.send",
                {"to": to, "subject": subject, "body": body, "confirm": confirm},
                0.90,
                False,
                "Exact Gmail send fields provided",
                formatter="gmail.send",
            )
        return None

    def _mentions_mail(self, text: str) -> bool:
        return "gmail" in text or "email" in text or "mail" in text or "message" in text

    def _build_gmail_query(self, original: str, text: str) -> str | None:
        quoted = re.search(r'"([^"]+)"', original)
        if quoted:
            return quoted.group(1).strip()

        parts: list[str] = []

        # Preserve explicit Gmail operators.
        ops = re.findall(r'\b(?:newer_than|older_than|from|to|subject|after|before|label|is|has):[^\s]+', original)
        parts.extend(ops)

        # Natural language extraction.
        if "unread" in text and "is:unread" not in parts:
            parts.append("is:unread")

        if "read " in text and "unread" not in text and "is:read" not in parts:
            # Avoid adding is:read for "read gmail message id".
            pass

        sender = self._extract_sender(original, text)
        if sender and not any(p.startswith("from:") for p in parts):
            parts.append(f"from:{sender}")

        subject = self._extract_subject_search(original)
        if subject and not any(p.startswith("subject:") for p in parts):
            parts.append(f'subject:{subject}')

        if not any(p.startswith(("newer_than:", "older_than:", "after:", "before:")) for p in parts):
            if "today" in text:
                parts.append("newer_than:1d")
            elif "yesterday" in text:
                parts.append("newer_than:2d")
            elif "last 30" in text or "30 days" in text or "month" in text:
                parts.append("newer_than:30d")
            elif "last 14" in text or "14 days" in text or "two weeks" in text:
                parts.append("newer_than:14d")
            elif "week" in text or "7 days" in text:
                parts.append("newer_than:7d")

        return " ".join(parts).strip() or None

    def _extract_sender(self, original: str, text: str) -> str | None:
        # from email address
        match = re.search(r'\bfrom\s+([\w\.-]+@[\w\.-]+\.\w+)', original, re.IGNORECASE)
        if match:
            return match.group(1)

        # from Google / Amazon / etc.
        match = re.search(r'\bfrom\s+([A-Za-z0-9_.-]+)\b', original, re.IGNORECASE)
        if match:
            value = match.group(1).strip().lower()
            ignore = {"today", "yesterday", "last", "the", "my", "gmail", "email", "mail"}
            if value not in ignore:
                return value
        return None

    def _extract_subject_search(self, original: str) -> str | None:
        match = re.search(r'\bsubject\s+(?:contains\s+)?["\']?([^"\']+?)["\']?(?:\s+from|\s+newer_than|\s+older_than|\s+unread|\s+today|\s+last|\s*$)', original, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value and not value.startswith("=") and not value.startswith(":"):
                return value.replace(" ", "-")
        return None

    def _extract_limit(self, text: str) -> int | None:
        match = re.search(r'\b(?:limit|top|first|max)\s+(\d{1,3})\b', text)
        if match:
            return min(max(int(match.group(1)), 1), 50)
        return None

    def _email(self, text: str):
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None

    def _field(self, text: str, label: str):
        quoted = re.search(label + r'\s*[=:]\s*"([^"]+)"', text, re.IGNORECASE)
        if quoted:
            return quoted.group(1).strip()

        labels = "subject|body|message|to"
        match = re.search(label + r'\s*[=:]\s*(.+?)(?=\s+(?:' + labels + r')\s*[=:]|\s*$)', text, re.IGNORECASE)
        if match:
            value = match.group(1).strip().strip('"').strip("'")
            return value or None
        return None
