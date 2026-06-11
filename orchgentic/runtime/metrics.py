from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

@dataclass
class RuntimeMetrics:
    total_routes: int = 0
    deterministic_routes: int = 0
    external_llm_routes: int = 0
    local_reasoner_routes: int = 0
    total_estimated_tokens_saved: int = 0
    tool_usage: dict[str, int] = field(default_factory=dict)
    route_type_counts: dict[str, int] = field(default_factory=dict)

    def record_route(self, event: dict) -> None:
        self.total_routes += 1
        route_type = str(event.get("route_type") or "unknown")
        self.route_type_counts[route_type] = self.route_type_counts.get(route_type, 0) + 1
        if route_type.startswith("deterministic") or route_type in {"single_tool", "multi_tool"}:
            self.deterministic_routes += 1
        if event.get("external_llm_used"):
            self.external_llm_routes += 1
        if route_type == "local_reasoner":
            self.local_reasoner_routes += 1
        tool = event.get("selected_tool")
        if tool:
            self.record_tool(str(tool))
        self.total_estimated_tokens_saved += int(event.get("estimated_external_tokens_saved") or 0)

    def record_tool(self, tool_name: str) -> None:
        self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1

    def summary(self) -> dict:
        return asdict(self)

def load_metrics(path: str | Path = "logs/route_metrics.json") -> RuntimeMetrics:
    p = Path(path)
    if not p.exists():
        return RuntimeMetrics()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return RuntimeMetrics(
            total_routes=int(raw.get("total_routes", 0)),
            deterministic_routes=int(raw.get("deterministic_routes", 0)),
            external_llm_routes=int(raw.get("external_llm_routes", 0)),
            local_reasoner_routes=int(raw.get("local_reasoner_routes", 0)),
            total_estimated_tokens_saved=int(raw.get("total_estimated_tokens_saved", 0)),
            tool_usage=dict(raw.get("tool_usage", {}) or {}),
            route_type_counts=dict(raw.get("route_type_counts", {}) or {}),
        )
    except Exception:
        return RuntimeMetrics()

def save_metrics(metrics: RuntimeMetrics, path: str | Path = "logs/route_metrics.json") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(metrics.summary(), indent=2), encoding="utf-8")

def record_route_metric(event: dict, path: str | Path = "logs/route_metrics.json") -> None:
    metrics = load_metrics(path)
    metrics.record_route(event)
    save_metrics(metrics, path)
