"""Reasoning defaults for Orchgentic v0.7.11-alpha."""

DEFAULT_REASONING_CONFIG = {
    "planner": True,
    "reflection": True,
    "local_reasoner": True,
    "confidence_scoring": True,
    "confidence_high_threshold": 0.78,
    "confidence_low_threshold": 0.52,
    "escalation": {
        "enabled": True,
        "min_confidence": 0.52,
        "fallback_provider": None,
    },
}
