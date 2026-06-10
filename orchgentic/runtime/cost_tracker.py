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

def build_route_telemetry(route_type: str, external_llm_used: bool, selected_tool=None, confidence=0.0, reason="", estimated_external_tokens_saved=0) -> dict:
    return asdict(RouteTelemetry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        route_type=route_type,
        external_llm_used=external_llm_used,
        selected_tool=selected_tool,
        confidence=confidence,
        reason=reason,
        estimated_external_tokens_saved=estimated_external_tokens_saved,
    ))

def append_route_log(path: str | Path, event: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\\n")
