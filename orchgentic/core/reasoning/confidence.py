"""Confidence scoring primitives for Orchgentic v0.7.11-alpha."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class ConfidenceBand(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class ConfidenceScore:
    score: float
    band: ConfidenceBand
    reasons: list[str] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)

    @property
    def should_escalate(self) -> bool:
        return self.band == ConfidenceBand.LOW


class ConfidenceScorer:
    """Combines runtime signals into a normalized confidence score."""

    def __init__(self, *, high_threshold: float = 0.78, low_threshold: float = 0.52) -> None:
        if not 0 < low_threshold < high_threshold < 1:
            raise ValueError("thresholds must satisfy 0 < low < high < 1")
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def score(
        self,
        *,
        local_confidence: float | None = None,
        tool_success_rate: float | None = None,
        tool_errors: Sequence[str] | None = None,
        missing_tools: Sequence[str] | None = None,
        reflection_flags: Sequence[str] | None = None,
        provider_error: str | None = None,
        task_complexity: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ConfidenceScore:
        value = self._clamp(local_confidence if local_confidence is not None else 0.65)
        reasons: list[str] = []
        signals: dict[str, Any] = dict(metadata or {})

        errors = list(tool_errors or [])
        missing = list(missing_tools or [])
        flags = list(reflection_flags or [])

        if tool_success_rate is not None:
            rate = self._clamp(tool_success_rate)
            signals["tool_success_rate"] = rate
            if rate < 0.5:
                value -= 0.22
                reasons.append("low_tool_success_rate")
            elif rate < 0.85:
                value -= 0.08
                reasons.append("partial_tool_success_rate")
            else:
                value += 0.05
                reasons.append("high_tool_success_rate")

        if errors:
            value -= min(0.25, 0.07 * len(errors))
            reasons.append("tool_errors_present")
            signals["tool_errors"] = errors

        if missing:
            value -= min(0.35, 0.12 * len(missing))
            reasons.append("missing_tools_present")
            signals["missing_tools"] = missing

        if flags:
            value -= min(0.20, 0.05 * len(flags))
            reasons.append("reflection_flags_present")
            signals["reflection_flags"] = flags

        if provider_error:
            value -= 0.25
            reasons.append("provider_error_present")
            signals["provider_error"] = provider_error

        if task_complexity == "complex":
            value -= 0.10
            reasons.append("complex_task")
        elif task_complexity == "high_risk":
            value -= 0.18
            reasons.append("high_risk_task")
        elif task_complexity == "simple":
            value += 0.05
            reasons.append("simple_task")

        value = self._clamp(value)
        if value >= self.high_threshold:
            band = ConfidenceBand.HIGH
        elif value < self.low_threshold:
            band = ConfidenceBand.LOW
        else:
            band = ConfidenceBand.MEDIUM

        return ConfidenceScore(score=value, band=band, reasons=reasons, signals=signals)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
