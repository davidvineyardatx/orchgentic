from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:
    yaml = None

DEFAULT_FALLBACK_TO_LLM_TERMS = [
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
    "write a response",
    "draft a response",
    "draft content creatively",
    "summarize body",
    "summarize body content",
    "summarize email",
    "summarize message",
]

DEFAULT_SAFE_TERMS = [
    "what time",
    "current time",
    "what day",
    "current date",
    "search gmail",
    "read gmail message",
    "count gmail",
    "show subject lines",
]

@dataclass
class RouterPolicy:
    enabled: bool = True
    fallback_to_llm_terms: list[str] = field(default_factory=lambda: list(DEFAULT_FALLBACK_TO_LLM_TERMS))
    deterministic_safe_terms: list[str] = field(default_factory=lambda: list(DEFAULT_SAFE_TERMS))
    deterministic_min_confidence: float = 0.90
    local_reasoner_min_confidence: float = 0.70
    allow_tool_prefetch_before_llm: bool = False
    log_routes: bool = True

def load_router_policy(path: str | Path = "config/router.yaml") -> RouterPolicy:
    policy_path = Path(path)
    if not policy_path.exists() or yaml is None:
        return RouterPolicy()

    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return RouterPolicy()

    cfg: dict[str, Any] = raw.get("deterministic_router", {}) or {}
    thresholds: dict[str, Any] = cfg.get("thresholds", {}) or {}
    behavior: dict[str, Any] = cfg.get("behavior", {}) or {}

    return RouterPolicy(
        enabled=bool(cfg.get("enabled", True)),
        fallback_to_llm_terms=list(cfg.get("fallback_to_llm_terms", DEFAULT_FALLBACK_TO_LLM_TERMS) or []),
        deterministic_safe_terms=list(cfg.get("deterministic_safe_terms", DEFAULT_SAFE_TERMS) or []),
        deterministic_min_confidence=float(thresholds.get("deterministic_min_confidence", 0.90)),
        local_reasoner_min_confidence=float(thresholds.get("local_reasoner_min_confidence", 0.70)),
        allow_tool_prefetch_before_llm=bool(behavior.get("allow_tool_prefetch_before_llm", False)),
        log_routes=bool(behavior.get("log_routes", True)),
    )
