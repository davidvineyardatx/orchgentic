from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import time

from .models import (
    RunRecord,
    TraceEvent,
    TOKEN_SOURCE_ACTUAL,
    TOKEN_SOURCE_ESTIMATED,
    TOKEN_SOURCE_NOT_APPLICABLE,
    TOKEN_SOURCE_UNKNOWN,
    VALID_TOKEN_SOURCES,
    utc_now_iso,
)
from .store import ObservabilityStore, DEFAULT_OBSERVABILITY_DB


def _duration_ms(started_at_iso: str, ended_at_iso: str | None = None) -> float | None:
    try:
        start = datetime.fromisoformat(started_at_iso)
        end = datetime.fromisoformat(ended_at_iso or utc_now_iso())
        return round((end - start).total_seconds() * 1000, 2)
    except Exception:
        return None


def normalize_token_source(value: str | None, *, has_tokens: bool = False, saved_tokens: int = 0) -> str:
    if value in VALID_TOKEN_SOURCES:
        return value
    if has_tokens or saved_tokens:
        return TOKEN_SOURCE_ESTIMATED
    return TOKEN_SOURCE_NOT_APPLICABLE


class TraceCollector:
    """Collects and persists structured run and trace events.

    The collector writes through immediately so CLI runs have durable history even when a
    later step fails. Token fields are token-only in v0.8.0; no USD cost fields are stored.
    """

    def __init__(self, store: ObservabilityStore | None = None, enabled: bool = True):
        self.store = store or ObservabilityStore(DEFAULT_OBSERVABILITY_DB)
        self.enabled = enabled
        self.run: RunRecord | None = None

    @property
    def run_id(self) -> str | None:
        return self.run.run_id if self.run else None

    def start_run(
        self,
        *,
        run_type: str,
        task: str,
        agent_id: str | None = None,
        agent_name: str | None = None,
        team_id: str | None = None,
        team_name: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RunRecord:
        self.run = RunRecord(
            run_type=run_type,
            task=task,
            agent_id=agent_id,
            agent_name=agent_name,
            team_id=team_id,
            team_name=team_name,
            provider=provider,
            model=model,
            metadata=metadata or {},
        )
        if self.enabled:
            self.store.create_run(self.run)
            self.event(
                "run.started",
                component="run",
                name=run_type,
                status="started",
                message="Run started.",
                data={"run_type": run_type, "metadata": metadata or {}},
            )
        return self.run

    def event(
        self,
        event_type: str,
        *,
        component: str,
        name: str | None = None,
        status: str = "completed",
        message: str | None = None,
        data: dict[str, Any] | None = None,
        duration_ms: float | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int | None = None,
        estimated_tokens_saved: int = 0,
        token_source: str | None = None,
        parent_event_id: str | None = None,
    ) -> TraceEvent | None:
        if not self.enabled or not self.run:
            return None
        input_tokens = int(input_tokens or 0)
        output_tokens = int(output_tokens or 0)
        total_tokens = int(total_tokens if total_tokens is not None else input_tokens + output_tokens)
        estimated_tokens_saved = int(estimated_tokens_saved or 0)
        source = normalize_token_source(
            token_source,
            has_tokens=bool(total_tokens),
            saved_tokens=estimated_tokens_saved,
        )
        event = TraceEvent(
            run_id=self.run.run_id,
            parent_event_id=parent_event_id,
            event_type=event_type,
            component=component,
            name=name,
            status=status,
            message=message,
            data=data or {},
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_tokens_saved=estimated_tokens_saved,
            token_source=source,
        )
        self.store.add_event(event)
        self._rollup_tokens(event)
        return event

    def _rollup_tokens(self, event: TraceEvent) -> None:
        if not self.run:
            return
        if event.total_tokens:
            self.run.input_tokens += int(event.input_tokens or 0)
            self.run.output_tokens += int(event.output_tokens or 0)
            self.run.total_tokens += int(event.total_tokens or 0)
            self.run.token_source = event.token_source
        if event.estimated_tokens_saved:
            self.run.estimated_tokens_saved += int(event.estimated_tokens_saved or 0)
            if self.run.token_source == TOKEN_SOURCE_NOT_APPLICABLE:
                self.run.token_source = TOKEN_SOURCE_ESTIMATED
        if event.event_type.startswith("llm.") and event.status in {"completed", "failed", "started"}:
            self.run.external_llm_used = True
        self.store.update_run(self.run)

    def complete_run(self, *, status: str = "completed", message: str | None = None, data: dict[str, Any] | None = None) -> RunRecord | None:
        if not self.run:
            return None
        self.run.status = status
        self.run.ended_at = utc_now_iso()
        self.run.duration_ms = _duration_ms(self.run.started_at, self.run.ended_at)
        if self.enabled:
            self.event(
                "run.completed" if status == "completed" else f"run.{status}",
                component="run",
                name=self.run.run_type,
                status=status,
                message=message or f"Run {status}.",
                data=data or {},
                duration_ms=self.run.duration_ms,
            )
            self.store.update_run(self.run)
        return self.run

    def fail_run(self, exc: BaseException | str, *, error_type: str | None = None) -> RunRecord | None:
        if not self.run:
            return None
        self.run.status = "failed"
        self.run.ended_at = utc_now_iso()
        self.run.duration_ms = _duration_ms(self.run.started_at, self.run.ended_at)
        self.run.error_type = error_type or (type(exc).__name__ if not isinstance(exc, str) else "RuntimeError")
        self.run.error_message = str(exc)
        if self.enabled:
            self.event(
                "run.failed",
                component="run",
                name=self.run.run_type,
                status="failed",
                message=str(exc),
                data={"error_type": self.run.error_type},
                duration_ms=self.run.duration_ms,
            )
            self.store.update_run(self.run)
        return self.run
