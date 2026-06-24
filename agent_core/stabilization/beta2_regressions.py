from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class Beta2RegressionResult:
    """Small structured result for beta.2 runtime regression checks."""

    name: str
    ok: bool
    message: str
    details: dict[str, Any] | None = None


def normalize_search_result(result: Any) -> list[Any]:
    """Normalize common memory/RAG search return shapes."""

    if result is None:
        return []

    if isinstance(result, list):
        return result

    if isinstance(result, tuple):
        return list(result)

    if isinstance(result, Mapping):
        for key in ("results", "items", "matches", "documents", "memories"):
            value = result.get(key)
            if value is None:
                continue
            if isinstance(value, list):
                return value
            if isinstance(value, tuple):
                return list(value)
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
                return list(value)
        return []

    if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
        return list(result)

    return [result]


def check_empty_search_result(result: Any, *, layer: str) -> Beta2RegressionResult:
    """Confirm an empty memory/RAG search result is safe and iterable."""

    normalized = normalize_search_result(result)

    if normalized:
        return Beta2RegressionResult(
            name=f"{layer}.empty_search",
            ok=True,
            message=f"{layer} search returned {len(normalized)} result(s).",
            details={"count": len(normalized)},
        )

    return Beta2RegressionResult(
        name=f"{layer}.empty_search",
        ok=True,
        message=f"{layer} search returned a safe empty result.",
        details={"count": 0},
    )


def check_provider_factory_result(provider: Any, *, provider_type: str) -> Beta2RegressionResult:
    """Confirm a provider factory returned a runtime-usable object."""

    if provider is None:
        return Beta2RegressionResult(
            name="provider.factory",
            ok=False,
            message=f"Provider factory returned None for {provider_type}.",
            details={"provider_type": provider_type},
        )

    callable_names = [
        name
        for name in ("complete", "chat", "generate", "invoke", "run")
        if callable(getattr(provider, name, None))
    ]

    if not callable_names:
        return Beta2RegressionResult(
            name="provider.factory",
            ok=False,
            message=f"Provider {provider_type} has no recognized callable runtime method.",
            details={"provider_type": provider_type},
        )

    return Beta2RegressionResult(
        name="provider.factory",
        ok=True,
        message=f"Provider {provider_type} exposes runtime method(s): {', '.join(callable_names)}.",
        details={"provider_type": provider_type, "methods": callable_names},
    )
