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



def infer_tool_contract_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Infer safe contract metadata from a tool definition.

    Registry tools remain the source of truth. This helper fills contract
    metadata from the tool name and input schema when the tool class has not
    declared metadata explicitly.
    """

    name = str(data.get("name") or "").lower()
    input_schema = data.get("input_schema") or {}
    properties = input_schema.get("properties", {}) if isinstance(input_schema, dict) else {}
    category = name.split(".", 1)[0] if "." in name else "general"

    side_effect = "none"
    if name.endswith(".search") or name.endswith(".read") or name in {"datetime.now", "datetime.local"}:
        side_effect = "read"
    if name.endswith(".write") or name.endswith(".draft"):
        side_effect = "write"
    if name.endswith(".send") or name.endswith(".reply"):
        side_effect = "send"
    if name.endswith(".delete"):
        side_effect = "delete"
    if name == "web.request":
        side_effect = "network"
    if name == "delegate.agent":
        side_effect = "delegate"

    destructive = side_effect in {"send", "delete"} or name == "filesystem.write"
    supports_confirmation = "confirm" in properties
    requires_policy_check = name.startswith("gmail.") or name == "delegate.agent" or destructive or supports_confirmation

    return {
        "category": category,
        "side_effect": side_effect,
        "destructive": destructive,
        "supports_confirmation": supports_confirmation,
        "requires_policy_check": requires_policy_check,
    }


def normalize_tool_contract(definition: Any, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a tool definition plus optional metadata into the contract shape.

    Runtime registry definitions are the intended source of truth. Tool classes
    can declare metadata directly as attributes; otherwise safe defaults are
    inferred from the tool name and input schema.
    """

    if hasattr(definition, "to_dict"):
        data = definition.to_dict()
    elif isinstance(definition, dict):
        data = dict(definition)
    else:
        data = {
            "name": getattr(definition, "name", None),
            "description": getattr(definition, "description", None),
            "input_schema": getattr(definition, "input_schema", None),
            "category": getattr(definition, "category", None),
            "side_effect": getattr(definition, "side_effect", None),
            "destructive": getattr(definition, "destructive", None),
            "supports_confirmation": getattr(definition, "supports_confirmation", None),
            "requires_policy_check": getattr(definition, "requires_policy_check", None),
            "builtin": getattr(definition, "builtin", None),
            "notes": getattr(definition, "notes", None),
            "plugin": getattr(definition, "plugin", None),
        }

    extra = dict(metadata or {})
    inferred = infer_tool_contract_metadata(data)

    payload = ToolContract(
        name=str(data.get("name") or ""),
        description=str(data.get("description") or ""),
        input_schema=dict(data.get("input_schema") or _schema()),
        category=str(extra.get("category", data.get("category") or inferred["category"])),
        side_effect=str(extra.get("side_effect", data.get("side_effect") or inferred["side_effect"])),
        destructive=bool(extra.get("destructive", data.get("destructive") if data.get("destructive") is not None else inferred["destructive"])),
        supports_confirmation=bool(extra.get("supports_confirmation", data.get("supports_confirmation") if data.get("supports_confirmation") is not None else inferred["supports_confirmation"])),
        requires_policy_check=bool(extra.get("requires_policy_check", data.get("requires_policy_check") if data.get("requires_policy_check") is not None else inferred["requires_policy_check"])),
        builtin=bool(extra.get("builtin", data.get("builtin") if data.get("builtin") is not None else False)),
        notes=extra.get("notes", data.get("notes")),
    ).to_dict()

    if data.get("plugin") is not None:
        payload["plugin"] = dict(data.get("plugin") or {})
    if "plugin" in extra:
        payload["plugin"] = dict(extra.get("plugin") or {})
    return payload


def get_tool_contracts_from_registry(registry: Any, allowed: list[str] | None = None) -> list[dict[str, Any]]:
    """Normalize contracts from the tool registry.

    This is the user-friendly path: add a tool to the registry, and Orchgentic
    can derive and validate its contract from the registered tool definition.
    """

    tools = []
    if hasattr(registry, "items") and isinstance(getattr(registry, "items"), dict):
        tools = list(registry.items.values())
    elif hasattr(registry, "definitions"):
        return [
            normalize_tool_contract(definition, metadata={"builtin": True})
            for definition in registry.definitions(allowed=allowed)
        ]

    if allowed:
        allowed_set = {name.lower() for name in allowed}
        tools = [tool for tool in tools if str(getattr(tool, "name", "")).lower() in allowed_set]

    return [normalize_tool_contract(tool, metadata={"builtin": True}) for tool in tools]


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


GMAIL_RUNTIME_CONFIRMATION_TOOLS = {
    "gmail.draft",
    "gmail.send",
    "gmail.reply",
    "gmail.delete",
}


def get_runtime_confirmation_consistency(contract_or_name: Any) -> dict[str, Any]:
    """Compare frozen confirmation contract metadata to current runtime baseline.

    This is inspection-only. It does not call or modify tool execution.
    """

    if isinstance(contract_or_name, str):
        contract = get_builtin_tool_contract(contract_or_name)
        if contract is None:
            raise KeyError(f"Unknown tool contract: {contract_or_name}")
    elif isinstance(contract_or_name, dict):
        contract = dict(contract_or_name)
    else:
        contract = normalize_tool_contract(contract_or_name)

    confirmation = get_confirmation_contract(contract["name"] if isinstance(contract, dict) and contract.get("name") in _TOOL_CONTRACTS_BY_NAME else contract)
    name = confirmation["name"]

    known_builtin_runtime = name in _TOOL_CONTRACTS_BY_NAME
    runtime_supports_confirmation = name in GMAIL_RUNTIME_CONFIRMATION_TOOLS
    runtime_requires_policy_check = name.startswith("gmail.")
    runtime_confirm_argument = runtime_supports_confirmation

    if not known_builtin_runtime:
        runtime_supports_confirmation = confirmation["supports_confirmation"]
        runtime_requires_policy_check = confirmation["requires_policy_check"]
        runtime_confirm_argument = confirmation["requires_confirm_input"]

    consistent = (
        confirmation["supports_confirmation"] == runtime_supports_confirmation
        and confirmation["requires_confirm_input"] == runtime_confirm_argument
    )

    notes: list[str] = []
    if name == "filesystem.write":
        notes.append("Current runtime baseline remains destructive without confirmation enforcement.")
    if name in GMAIL_RUNTIME_CONFIRMATION_TOOLS:
        notes.append("Current runtime baseline enforces confirmation through Gmail tool policy.")
    if not known_builtin_runtime:
        notes.append("Runtime confirmation behavior is inferred from the registered tool contract.")

    return {
        "name": name,
        "contract_supports_confirmation": confirmation["supports_confirmation"],
        "contract_requires_confirm_input": confirmation["requires_confirm_input"],
        "runtime_supports_confirmation": runtime_supports_confirmation,
        "runtime_confirm_argument": runtime_confirm_argument,
        "contract_requires_policy_check": confirmation["requires_policy_check"],
        "runtime_requires_policy_check": runtime_requires_policy_check,
        "consistent": consistent,
        "runtime_behavior_changed": False,
        "notes": notes,
    }


def get_builtin_runtime_confirmation_consistency() -> list[dict[str, Any]]:
    """Return runtime confirmation consistency metadata for all built-in tools."""

    return [get_runtime_confirmation_consistency(contract.to_dict()) for contract in BUILTIN_TOOL_CONTRACTS]


PLUGIN_TOOL_CONTRACT_REQUIRED_FIELDS = {
    "name",
    "description",
    "input_schema",
    "plugin",
}


def normalize_plugin_tool_contract(definition: Any, *, plugin: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a future plugin tool contract without loading or executing plugins.

    This is contract-shape work only. It does not discover, import, register, or
    run external plugin tools.
    """

    metadata = {"builtin": False}
    if plugin is not None:
        metadata["plugin"] = dict(plugin)

    contract = normalize_tool_contract(definition, metadata=metadata)

    if "plugin" not in contract:
        contract["plugin"] = {}
    contract["builtin"] = False
    return contract


def validate_plugin_tool_contract(contract: Any) -> dict[str, Any]:
    """Validate future plugin tool contract shape without plugin loading."""

    data = normalize_plugin_tool_contract(contract) if not isinstance(contract, dict) or contract.get("builtin") is not False else dict(contract)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    missing = sorted(field for field in PLUGIN_TOOL_CONTRACT_REQUIRED_FIELDS if field not in data)
    for field in missing:
        errors.append(
            {
                "field": field,
                "code": "missing_plugin_contract_field",
                "message": f"Plugin tool contract is missing required field '{field}'.",
            }
        )

    plugin = data.get("plugin") or {}
    if not isinstance(plugin, dict):
        errors.append(
            {
                "field": "plugin",
                "code": "invalid_plugin_metadata",
                "message": "Plugin metadata must be an object.",
            }
        )
        plugin = {}

    for field in ["name", "version"]:
        if not plugin.get(field):
            errors.append(
                {
                    "field": f"plugin.{field}",
                    "code": "missing_plugin_metadata",
                    "message": f"Plugin metadata is missing '{field}'.",
                }
            )

    if data.get("builtin") is not False:
        errors.append(
            {
                "field": "builtin",
                "code": "plugin_contract_must_not_be_builtin",
                "message": "Plugin tool contracts must set builtin to false.",
            }
        )

    name = str(data.get("name") or "")
    if name and "." not in name:
        warnings.append(
            {
                "field": "name",
                "code": "plugin_tool_name_should_be_namespaced",
                "message": "Plugin tool names should be namespaced, for example vendor.tool_name.",
            }
        )

    base_validation = validate_tool_contract(data)
    for item in base_validation.get("errors", []):
        errors.append(item)
    for item in base_validation.get("warnings", []):
        warnings.append(item)

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "contract": data,
        "plugin_loader_added": False,
        "runtime_behavior_changed": False,
    }


def _collect_contract_validation_payload(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    tool_results = []
    confirmation_results = []
    runtime_results = []

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for contract in contracts:
        name = contract.get("name")
        tool_result = validate_tool_contract(contract)
        confirmation_result = validate_confirmation_contract(contract)
        runtime_result = get_runtime_confirmation_consistency(contract)

        tool_results.append({"name": name, **tool_result})
        confirmation_results.append({"name": name, **confirmation_result})
        runtime_results.append(runtime_result)

        for item in tool_result.get("errors", []):
            if isinstance(item, dict):
                errors.append({"tool": name, **item})
            else:
                errors.append({"tool": name, "field": "contract", "code": "invalid_tool_contract", "message": str(item)})
        for item in confirmation_result.get("errors", []):
            errors.append({"tool": name, **item})
        for item in tool_result.get("warnings", []):
            if isinstance(item, dict):
                warnings.append({"tool": name, **item})
            else:
                warnings.append({"tool": name, "field": "contract", "code": "tool_contract_warning", "message": str(item)})
        for item in confirmation_result.get("warnings", []):
            warnings.append({"tool": name, **item})

        if name in _TOOL_CONTRACTS_BY_NAME and runtime_result.get("consistent") is not True:
            errors.append(
                {
                    "tool": name,
                    "field": "runtime_confirmation",
                    "code": "runtime_confirmation_inconsistent",
                    "message": "Runtime confirmation metadata does not match the frozen built-in contract baseline.",
                }
            )

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "tool_count": len(tool_results),
        "tool_contracts": tool_results,
        "confirmation_contracts": confirmation_results,
        "runtime_confirmation_consistency": runtime_results,
        "plugin_loader_added": False,
        "runtime_behavior_changed": False,
    }


def validate_tool_registry_contracts(registry: Any) -> dict[str, Any]:
    """Validate registered tools as the source of truth."""

    contracts = get_tool_contracts_from_registry(registry)
    payload = _collect_contract_validation_payload(contracts)
    payload["source"] = "registry"
    return payload


def validate_builtin_tool_contracts() -> dict[str, Any]:
    """Validate the static built-in baseline snapshot.

    This remains available for regression tests. Runtime doctor checks should
    prefer validate_tool_registry_contracts(default_tool_registry()).
    """

    payload = _collect_contract_validation_payload(get_builtin_tool_contracts())
    payload["source"] = "builtin_snapshot"
    return payload
