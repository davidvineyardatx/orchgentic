from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ToolContract:
    """Stable contract metadata for a tool.

    This contract is intentionally separate from tool execution. It freezes the
    tool-facing shape that agents, planners, docs, tests, and future plugin
    loaders can depend on without changing runtime behavior.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    category: str = "general"
    side_effect: str = "none"
    destructive: bool = False
    supports_confirmation: bool = False
    requires_policy_check: bool = False
    builtin: bool = True
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "category": self.category,
            "side_effect": self.side_effect,
            "destructive": self.destructive,
            "supports_confirmation": self.supports_confirmation,
            "requires_policy_check": self.requires_policy_check,
            "builtin": self.builtin,
        }
        if self.notes:
            payload["notes"] = self.notes
        return payload


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
    }


BUILTIN_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="datetime.now",
        description="Return the current UTC date and time.",
        input_schema=_schema(),
        category="datetime",
    ),
    ToolContract(
        name="datetime.local",
        description="Return the current local date and time using the resolved Orchgentic time context.",
        input_schema=_schema(
            {
                "timezone": {
                    "type": "string",
                    "description": "Optional IANA timezone override, for example America/Chicago.",
                }
            }
        ),
        category="datetime",
    ),
    ToolContract(
        name="filesystem.read",
        description="Read a text file from the local workspace.",
        input_schema=_schema({"path": {"type": "string", "description": "Path to the file."}}, ["path"]),
        category="filesystem",
        side_effect="read",
    ),
    ToolContract(
        name="filesystem.write",
        description="Write text content to a local workspace file.",
        input_schema=_schema({"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
        category="filesystem",
        side_effect="write",
        destructive=True,
        notes="Current baseline does not require a confirm argument for filesystem.write.",
    ),
    ToolContract(
        name="web.request",
        description="Make a simple HTTP request.",
        input_schema=_schema(
            {
                "url": {"type": "string"},
                "method": {"type": "string", "default": "GET"},
                "body": {"type": "object"},
            },
            ["url"],
        ),
        category="network",
        side_effect="network",
    ),
    ToolContract(
        name="memory.search",
        description="Search this agent's conversation memory.",
        input_schema=_schema(
            {
                "query": {"type": "string"},
                "agent_id": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            ["query", "agent_id"],
        ),
        category="memory",
        side_effect="read",
    ),
    ToolContract(
        name="knowledge.search",
        description="Search the agent knowledge base.",
        input_schema=_schema(
            {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            ["query"],
        ),
        category="knowledge",
        side_effect="read",
    ),
    ToolContract(
        name="delegate.agent",
        description="Delegate a task to another configured Orchgentic agent.",
        input_schema=_schema(
            {
                "agent": {"type": "string", "description": "Target agent name or id."},
                "task": {"type": "string", "description": "Task to delegate."},
                "context": {"type": "object", "description": "Optional context for the target agent."},
            },
            ["agent", "task"],
        ),
        category="orchestration",
        side_effect="delegate",
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.search",
        description="Search Gmail messages for a named Gmail connection.",
        input_schema=_schema(
            {
                "query": {"type": "string"},
                "max_results": {"type": "integer"},
                "connection": {"type": "string"},
            },
            ["query"],
        ),
        category="gmail",
        side_effect="read",
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.read",
        description="Read a Gmail message through a named Gmail connection.",
        input_schema=_schema(
            {
                "message_id": {"type": "string"},
                "connection": {"type": "string"},
            },
            ["message_id"],
        ),
        category="gmail",
        side_effect="read",
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.draft",
        description="Create a Gmail draft through a named Gmail connection with confirmation enforcement.",
        input_schema=_schema(
            {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "confirm": {"type": "boolean"},
                "connection": {"type": "string"},
            },
            ["to", "subject", "body"],
        ),
        category="gmail",
        side_effect="write",
        supports_confirmation=True,
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.send",
        description="Send a Gmail message through a named Gmail connection with policy enforcement.",
        input_schema=_schema(
            {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "confirm": {"type": "boolean"},
                "connection": {"type": "string"},
            },
            ["to", "subject", "body"],
        ),
        category="gmail",
        side_effect="send",
        destructive=True,
        supports_confirmation=True,
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.reply",
        description="Reply to a Gmail message thread through a named Gmail connection with confirmation enforcement.",
        input_schema=_schema(
            {
                "message_id": {"type": "string"},
                "body": {"type": "string"},
                "confirm": {"type": "boolean"},
                "connection": {"type": "string"},
            },
            ["message_id", "body"],
        ),
        category="gmail",
        side_effect="send",
        destructive=True,
        supports_confirmation=True,
        requires_policy_check=True,
    ),
    ToolContract(
        name="gmail.delete",
        description="Move a Gmail message to Trash through a named Gmail connection with confirmation enforcement.",
        input_schema=_schema(
            {
                "message_id": {"type": "string"},
                "confirm": {"type": "boolean"},
                "connection": {"type": "string"},
            },
            ["message_id"],
        ),
        category="gmail",
        side_effect="delete",
        destructive=True,
        supports_confirmation=True,
        requires_policy_check=True,
    ),
)


_TOOL_CONTRACTS_BY_NAME = {contract.name: contract for contract in BUILTIN_TOOL_CONTRACTS}


def normalize_tool_contract(definition: Any, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a tool definition plus optional metadata into the contract shape."""

    if hasattr(definition, "to_dict"):
        data = definition.to_dict()
    elif isinstance(definition, dict):
        data = dict(definition)
    else:
        data = {
            "name": getattr(definition, "name", None),
            "description": getattr(definition, "description", None),
            "input_schema": getattr(definition, "input_schema", None),
        }

    extra = dict(metadata or {})
    return ToolContract(
        name=str(data.get("name") or ""),
        description=str(data.get("description") or ""),
        input_schema=dict(data.get("input_schema") or _schema()),
        category=str(extra.get("category", "general")),
        side_effect=str(extra.get("side_effect", "none")),
        destructive=bool(extra.get("destructive", False)),
        supports_confirmation=bool(extra.get("supports_confirmation", False)),
        requires_policy_check=bool(extra.get("requires_policy_check", False)),
        builtin=bool(extra.get("builtin", False)),
        notes=extra.get("notes"),
    ).to_dict()


def get_builtin_tool_contracts(allowed: list[str] | None = None) -> list[dict[str, Any]]:
    """Return stable built-in tool contracts, optionally filtered by tool name."""

    if not allowed:
        return [contract.to_dict() for contract in BUILTIN_TOOL_CONTRACTS]
    allowed_set = {name.lower() for name in allowed}
    return [
        contract.to_dict()
        for contract in BUILTIN_TOOL_CONTRACTS
        if contract.name.lower() in allowed_set
    ]


def get_builtin_tool_contract(name: str) -> dict[str, Any] | None:
    """Return a single built-in tool contract by name."""

    contract = _TOOL_CONTRACTS_BY_NAME.get(name)
    return contract.to_dict() if contract else None


def validate_tool_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Validate the public tool contract shape without executing a tool."""

    errors: list[str] = []
    name = contract.get("name")
    description = contract.get("description")
    input_schema = contract.get("input_schema")

    if not isinstance(name, str) or not name.strip():
        errors.append("name is required")
    if not isinstance(description, str) or not description.strip():
        errors.append("description is required")
    if not isinstance(input_schema, dict):
        errors.append("input_schema must be an object")
    else:
        if input_schema.get("type") != "object":
            errors.append("input_schema.type must be object")
        if not isinstance(input_schema.get("properties", {}), dict):
            errors.append("input_schema.properties must be an object")
        if not isinstance(input_schema.get("required", []), list):
            errors.append("input_schema.required must be a list")

    if contract.get("supports_confirmation"):
        properties = (input_schema or {}).get("properties", {}) if isinstance(input_schema, dict) else {}
        confirm = properties.get("confirm") if isinstance(properties, dict) else None
        if not isinstance(confirm, dict) or confirm.get("type") != "boolean":
            errors.append("supports_confirmation requires a boolean confirm property")

    return {
        "valid": not errors,
        "errors": errors,
    }


CONFIRMATION_SIDE_EFFECTS = {"send", "delete"}
CONFIRMATION_RECOMMENDED_SIDE_EFFECTS = {"write", "send", "delete", "delegate"}


def get_confirmation_contract(contract_or_name: Any) -> dict[str, Any]:
    """Return stable confirmation metadata for a tool contract.

    This is metadata-only and does not change tool execution behavior.
    """

    if isinstance(contract_or_name, str):
        contract = get_builtin_tool_contract(contract_or_name)
        if contract is None:
            raise KeyError(f"Unknown tool contract: {contract_or_name}")
    else:
        contract = normalize_tool_contract(contract_or_name)

    input_schema = contract.get("input_schema") or {}
    properties = input_schema.get("properties") or {}
    confirm_schema = properties.get("confirm") or {}

    supports_confirmation = bool(contract.get("supports_confirmation"))
    destructive = bool(contract.get("destructive"))
    side_effect = str(contract.get("side_effect") or "none")

    requires_confirm_input = supports_confirmation and "confirm" in properties
    confirm_type = confirm_schema.get("type") if isinstance(confirm_schema, dict) else None

    return {
        "name": contract.get("name"),
        "supports_confirmation": supports_confirmation,
        "requires_confirm_input": requires_confirm_input,
        "confirm_input_type": confirm_type,
        "destructive": destructive,
        "side_effect": side_effect,
        "requires_policy_check": bool(contract.get("requires_policy_check")),
        "confirmation_required_by_contract": supports_confirmation and destructive,
        "confirmation_recommended": side_effect in CONFIRMATION_RECOMMENDED_SIDE_EFFECTS or destructive,
        "runtime_behavior_changed": False,
    }


def get_builtin_confirmation_contracts() -> list[dict[str, Any]]:
    """Return confirmation metadata for all built-in tool contracts."""

    return [get_confirmation_contract(contract.to_dict()) for contract in BUILTIN_TOOL_CONTRACTS]


def validate_confirmation_contract(contract_or_name: Any) -> dict[str, Any]:
    """Validate confirmation metadata without enforcing runtime behavior."""

    confirmation = get_confirmation_contract(contract_or_name)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if confirmation["supports_confirmation"]:
        if not confirmation["requires_confirm_input"]:
            errors.append(
                {
                    "field": "input_schema.properties.confirm",
                    "code": "missing_confirm_input",
                    "message": "Tool supports confirmation but does not expose a confirm input.",
                }
            )
        elif confirmation["confirm_input_type"] != "boolean":
            errors.append(
                {
                    "field": "input_schema.properties.confirm.type",
                    "code": "invalid_confirm_input_type",
                    "message": "Tool confirm input must be boolean.",
                }
            )

    if confirmation["destructive"] and not confirmation["supports_confirmation"]:
        warnings.append(
            {
                "field": "supports_confirmation",
                "code": "destructive_without_confirmation",
                "message": "Tool is destructive but current baseline does not support confirmation.",
            }
        )

    if confirmation["side_effect"] in CONFIRMATION_SIDE_EFFECTS and not confirmation["supports_confirmation"]:
        warnings.append(
            {
                "field": "supports_confirmation",
                "code": "side_effect_without_confirmation",
                "message": "Tool has send/delete side effects but does not support confirmation.",
            }
        )

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "confirmation": confirmation,
        "runtime_behavior_changed": False,
    }
