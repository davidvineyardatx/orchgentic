from dataclasses import dataclass, field

@dataclass(slots=True)
class RequirementResult:
    required_tools: set[str] = field(default_factory=set)
    reasons: list[str] = field(default_factory=list)

    @property
    def has_requirements(self) -> bool:
        return bool(self.required_tools)

class RequirementDetector:
    # Deterministic first-pass detector.
    # This intentionally avoids LLM calls so we can fail fast before spending tokens.
    WEB_KEYWORDS = [
        "web",
        "website",
        "url",
        "http://",
        "https://",
        "fetch",
        "browse",
        "internet",
        "online",
        "current",
        "latest",
        "today",
        "search online",
        "api",
        "endpoint",
    ]

    FILE_READ_KEYWORDS = [
        "read file",
        "open file",
        "load file",
        "inspect file",
    ]

    FILE_WRITE_KEYWORDS = [
        "write file",
        "save file",
        "create file",
        "export file",
    ]

    def detect(self, task: str) -> RequirementResult:
        text = (task or "").lower()
        result = RequirementResult()

        if any(keyword in text for keyword in self.WEB_KEYWORDS):
            result.required_tools.add("web.request")
            result.reasons.append("Task appears to require web or current external data access.")

        if any(keyword in text for keyword in self.FILE_READ_KEYWORDS):
            result.required_tools.add("filesystem.read")
            result.reasons.append("Task appears to require reading a local file.")

        if any(keyword in text for keyword in self.FILE_WRITE_KEYWORDS):
            result.required_tools.add("filesystem.write")
            result.reasons.append("Task appears to require writing a local file.")

        return result
