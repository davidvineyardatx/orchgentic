"""Default routing configuration for Orchgentic v0.7.12-alpha."""

DEFAULT_ROUTING_CONFIG = {
    "workflow": {
        "enabled": True,
        "multi_step_threshold": 0.80,
    },
    "event": {
        "enabled": True,
        "autonomous_events_require_policy_checks": True,
    },
    "policy": {
        "enabled": True,
        "block_disabled_tools_before_llm": True,
        "hold_confirmation_tools_before_llm": True,
    },
}
