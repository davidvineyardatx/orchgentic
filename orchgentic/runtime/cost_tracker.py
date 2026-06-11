from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class RouteTelemetry:
    timestamp: str
    route_type: str
    external_llm_used: bool
    selected_tool: str | None
    confidence: float
    reason: str
    estimated_external_tokens_saved: int = 0
    execution_time_ms: float | None = None
    agent: str | None = None
    provider: str | None = None
    model: str | None = None
    token_estimate: dict | None = None

def build_route_telemetry(
    route_type: str,
    external_llm_used: bool,
    selected_tool=None,
    confidence=0.0,
    reason="",
    estimated_external_tokens_saved=0,
    execution_time_ms=None,
    agent=None,
    provider=None,
    model=None,
    token_estimate=None,
) -> dict:
    return asdict(RouteTelemetry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        route_type=route_type,
        external_llm_used=external_llm_used,
        selected_tool=selected_tool,
        confidence=float(confidence or 0.0),
        reason=str(reason or ""),
        estimated_external_tokens_saved=int(estimated_external_tokens_saved or 0),
        execution_time_ms=execution_time_ms,
        agent=agent,
        provider=provider,
        model=model,
        token_estimate=token_estimate,
    ))

def append_route_log(path: str | Path, event: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
