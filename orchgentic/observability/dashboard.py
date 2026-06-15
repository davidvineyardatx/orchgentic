from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Iterable

from .models import RunRecord
from .store import ObservabilityStore


DEFAULT_DASHBOARD_PATH = Path("exports") / "orchgentic_observability_dashboard.html"


def _safe(value) -> str:
    if value is None:
        return "-"
    return escape(str(value))


def _short_id(run_id: str | None) -> str:
    return (run_id or "-")[:8]


def _anchor_id(run_id: str | None) -> str:
    safe = "".join(ch for ch in (run_id or "unknown") if ch.isalnum() or ch in {"-", "_"})
    return f"run-{safe}"


def _target(run: RunRecord) -> str:
    return run.team_name or run.agent_name or run.team_id or run.agent_id or "-"


def _tokens_label(run: RunRecord) -> str:
    if run.total_tokens:
        return f"tokens={run.total_tokens}, source={run.token_source}"
    if run.estimated_tokens_saved:
        return f"saved≈{run.estimated_tokens_saved}, source={run.token_source}"
    return f"source={run.token_source}"


def _status_class(status: str | None) -> str:
    value = (status or "unknown").lower()
    if value == "completed":
        return "status-completed"
    if value == "failed":
        return "status-failed"
    if value in {"blocked", "hold_for_confirmation"}:
        return "status-hold"
    return "status-unknown"


def _metric_card(label: str, value, detail: str = "") -> str:
    return f"""
      <section class="card metric">
        <div class="metric-label">{escape(label)}</div>
        <div class="metric-value">{_safe(value)}</div>
        <div class="metric-detail">{_safe(detail)}</div>
      </section>
    """


def _run_rows(runs: Iterable[RunRecord]) -> str:
    rows = []
    for run in runs:
        rows.append(
            f"""
            <tr>
              <td><a class="run-link" href="#{_safe(_anchor_id(run.run_id))}"><code>{_safe(_short_id(run.run_id))}</code></a></td>
              <td><span class="pill {_status_class(run.status)}">{_safe(run.status)}</span></td>
              <td>{_safe(run.run_type)}</td>
              <td>{_safe(_target(run))}</td>
              <td>{_safe(_tokens_label(run))}</td>
              <td>{_safe(run.task)}</td>
              <td>{_safe(run.started_at)}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7" class="empty">No runs found.</td></tr>'


def _failure_rows(failures: Iterable[RunRecord]) -> str:
    rows = []
    for run in failures:
        error_type = run.error_type or "unknown"
        summary = run.error_message or "Inspect trace events for details."
        rows.append(
            f"""
            <tr>
              <td><a class="run-link" href="#{_safe(_anchor_id(run.run_id))}"><code>{_safe(_short_id(run.run_id))}</code></a></td>
              <td>{_safe(run.run_type)}</td>
              <td>{_safe(_target(run))}</td>
              <td>{_safe(error_type)}</td>
              <td>{_safe(summary)}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5" class="empty">No failed runs found.</td></tr>'



def _event_rows(events) -> str:
    rows = []
    for event in events:
        rows.append(
            f"""
            <tr>
              <td>{_safe(event.timestamp)}</td>
              <td>{_safe(event.event_type)}</td>
              <td>{_safe(event.component)}</td>
              <td>{_safe(event.status)}</td>
              <td>{_safe(event.name)}</td>
              <td>{_safe(event.message)}</td>
              <td>{_safe(_tokens_event_label(event))}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7" class="empty">No trace events found.</td></tr>'


def _tokens_event_label(event) -> str:
    if getattr(event, "total_tokens", 0):
        return f"tokens={event.total_tokens}, source={event.token_source}"
    if getattr(event, "estimated_tokens_saved", 0):
        return f"saved≈{event.estimated_tokens_saved}, source={event.token_source}"
    return getattr(event, "token_source", None) or "-"


def _run_detail_sections(store: ObservabilityStore, runs: Iterable[RunRecord]) -> str:
    sections = []
    for run in runs:
        events = store.list_events(run.run_id)
        sections.append(
            f"""
            <section class="card section run-detail" id="{_safe(_anchor_id(run.run_id))}">
              <div class="section-head">
                <div>
                  <h2>Run Details: <code>{_safe(_short_id(run.run_id))}</code></h2>
                  <div class="detail-subtitle">{_safe(run.run_id)}</div>
                </div>
                <a class="top-link" href="#top">↑ Minimize</a>
              </div>

              <div class="detail-grid">
                <div><span>status</span><strong>{_safe(run.status)}</strong></div>
                <div><span>type</span><strong>{_safe(run.run_type)}</strong></div>
                <div><span>agent/team</span><strong>{_safe(_target(run))}</strong></div>
                <div><span>provider</span><strong>{_safe(run.provider)}</strong></div>
                <div><span>model</span><strong>{_safe(run.model)}</strong></div>
                <div><span>duration_ms</span><strong>{_safe(run.duration_ms)}</strong></div>
                <div><span>tokens</span><strong>{_safe(_tokens_label(run))}</strong></div>
                <div><span>external_llm_used</span><strong>{_safe(bool(run.external_llm_used))}</strong></div>
              </div>

              <div class="task-box">
                <span>task</span>
                <p>{_safe(run.task)}</p>
              </div>

              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Event</th>
                    <th>Component</th>
                    <th>Status</th>
                    <th>Name</th>
                    <th>Message</th>
                    <th>Tokens</th>
                  </tr>
                </thead>
                <tbody>
                  {_event_rows(events)}
                </tbody>
              </table>
            </section>
            """
        )
    return "\n".join(sections) if sections else ""

def build_dashboard_html(
    store: ObservabilityStore,
    *,
    limit: int = 100,
    status: str | None = None,
    run_type: str | None = None,
    agent: str | None = None,
    team: str | None = None,
) -> str:
    """Build a static, dependency-free HTML dashboard from the observability store."""
    limit = max(1, min(int(limit or 100), 500))
    runs = store.list_runs(limit=limit, status=status, run_type=run_type, agent=agent, team=team)
    failures = store.list_failures(limit=25, run_type=run_type, agent=agent, team=team)
    stats = store.get_stats(status=status, run_type=run_type, agent=agent, team=team)
    failure_stats = store.get_failure_stats(run_type=run_type, agent=agent, team=team)

    filters = {
        "status": status,
        "type": run_type,
        "agent": agent,
        "team": team,
        "limit": limit,
    }
    active_filters = ", ".join(f"{k}={v}" for k, v in filters.items() if v) or "none"

    completed = stats.get("by_status", {}).get("completed", 0)
    failed = stats.get("by_status", {}).get("failed", 0)
    total = stats.get("total_runs", 0)
    success_rate = f"{round((completed / total) * 100, 1)}%" if total else "0%"

    generated_at = datetime.now(timezone.utc).isoformat()

    by_status = stats.get("by_status") or {}
    status_chips = " ".join(
        f'<span class="chip">{_safe(key)}: <strong>{_safe(value)}</strong></span>'
        for key, value in by_status.items()
    ) or '<span class="chip">No status data</span>'

    by_type = stats.get("by_type") or {}
    type_chips = " ".join(
        f'<span class="chip">{_safe(key)}: <strong>{_safe(value)}</strong></span>'
        for key, value in by_type.items()
    ) or '<span class="chip">No type data</span>'

    failure_types = failure_stats.get("by_error_type") or {}
    failure_chips = " ".join(
        f'<span class="chip danger">{_safe(key)}: <strong>{_safe(value)}</strong></span>'
        for key, value in failure_types.items()
    ) or '<span class="chip">No failures</span>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Orchgentic Observability Dashboard</title>
  <style>
    :root {{
      --bg: #090b10;
      --panel: #121620;
      --panel-2: #171d29;
      --text: #f5f7fb;
      --muted: #9aa4b2;
      --line: #2a3242;
      --orange: #ff8a1f;
      --orange-soft: rgba(255, 138, 31, 0.16);
      --green: #43d17a;
      --red: #ff5a68;
      --yellow: #ffd166;
      --blue: #6ca8ff;
    }}
    * {{ box-sizing: border-box; }}

    a {{ color: inherit; }}
    .run-link {{ text-decoration: none; }}
    .run-link code {{ transition: border-color .15s ease, background .15s ease; border: 1px solid rgba(255, 138, 31, .16); }}
    .run-link:hover code {{ border-color: rgba(255, 138, 31, .72); background: rgba(255, 138, 31, .24); }}
    .top-link {{ color: var(--orange); text-decoration: none; font-size: 13px; font-weight: 700; }}
    .top-link:hover {{ text-decoration: underline; }}
    .detail-subtitle {{ color: var(--muted); margin-top: 6px; font-size: 12px; }}
    .run-detail {{ scroll-margin-top: 18px; }}
    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }}
    .detail-grid div {{
      background: rgba(255,255,255,.035);
      border: 1px solid rgba(42, 50, 66, .8);
      border-radius: 12px;
      padding: 10px;
    }}
    .detail-grid span,
    .task-box span {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin-bottom: 5px;
    }}
    .detail-grid strong {{ color: var(--text); font-size: 13px; overflow-wrap: anywhere; }}
    .task-box {{
      background: rgba(255,255,255,.025);
      border: 1px solid rgba(42, 50, 66, .8);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 14px;
    }}
    .task-box p {{ margin: 0; color: #d7dce5; overflow-wrap: anywhere; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top right, rgba(255, 138, 31, 0.16), transparent 28rem),
        radial-gradient(circle at bottom left, rgba(108, 168, 255, 0.10), transparent 26rem),
        var(--bg);
      color: var(--text);
    }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 34px; }}
    header {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-start;
      margin-bottom: 28px;
    }}
    h1 {{ margin: 0; font-size: 34px; letter-spacing: -0.03em; }}
    .subtitle {{ color: var(--muted); margin-top: 8px; font-size: 15px; }}
    .brand {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--orange);
      font-weight: 700;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-size: 12px;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--orange);
      box-shadow: 0 0 24px var(--orange);
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
      text-align: right;
      line-height: 1.7;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 18px;
    }}
    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,.015)), var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 18px 50px rgba(0,0,0,.25);
    }}
    .metric {{ padding: 18px; }}
    .metric-label {{ color: var(--muted); font-size: 13px; }}
    .metric-value {{ margin-top: 8px; font-size: 30px; font-weight: 800; letter-spacing: -0.02em; }}
    .metric-detail {{ color: var(--muted); margin-top: 4px; font-size: 12px; min-height: 18px; }}
    .section {{ padding: 18px; margin-top: 16px; }}
    .section-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 14px;
    }}
    h2 {{ margin: 0; font-size: 18px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{
      display: inline-flex;
      gap: 5px;
      align-items: center;
      padding: 6px 10px;
      background: var(--panel-2);
      border: 1px solid var(--line);
      color: var(--muted);
      border-radius: 999px;
      font-size: 12px;
    }}
    .chip.danger {{ color: #ffc2c8; border-color: rgba(255, 90, 104, .35); background: rgba(255, 90, 104, .09); }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-align: left;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
    }}
    td {{
      padding: 12px 10px;
      border-bottom: 1px solid rgba(42, 50, 66, .75);
      color: #d7dce5;
      font-size: 13px;
      vertical-align: top;
    }}
    code {{
      color: #ffd6ad;
      background: var(--orange-soft);
      padding: 3px 6px;
      border-radius: 7px;
    }}
    .pill {{
      display: inline-flex;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .status-completed {{ color: #b8ffd0; background: rgba(67, 209, 122, .13); }}
    .status-failed {{ color: #ffc2c8; background: rgba(255, 90, 104, .13); }}
    .status-hold {{ color: #ffe6a3; background: rgba(255, 209, 102, .13); }}
    .status-unknown {{ color: #d3dcff; background: rgba(108, 168, 255, .13); }}
    .empty {{ color: var(--muted); text-align: center; padding: 26px; }}
    .two-col {{ display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; }}
    footer {{ color: var(--muted); font-size: 12px; margin-top: 18px; text-align: center; }}
    @media (max-width: 900px) {{
      .grid, .two-col {{ grid-template-columns: 1fr; }}
      header {{ flex-direction: column; }}
      .meta {{ text-align: left; }}
    }}
  </style>
</head>
<body>
  <div class="wrap" id="top">
    <header>
      <div>
        <div class="brand"><span class="dot"></span> Orchgentic Observability</div>
        <h1>RUN DASHBOARD</h1>
        <div class="subtitle">Summary of runs, failures, token usage, and estimated savings.</div>
      </div>
      <div class="meta">
        generated_at: {_safe(generated_at)}<br />
        active_filters: {_safe(active_filters)}<br />
        schema: orchgentic.observability.dashboard.v1
      </div>
    </header>

    <main>
      <div class="grid">
        {_metric_card("Total Runs", stats.get("total_runs", 0), f"Success rate {success_rate}")}
        {_metric_card("Failures", failed, f"{failure_stats.get("total_failures", 0)} failed run(s)")}
        {_metric_card("Total Tokens", stats.get("total_tokens", 0), "provider-reported or estimated")}
        {_metric_card("Estimated Tokens Saved", stats.get("estimated_tokens_saved", 0), "operational estimate")}
      </div>

      <div class="two-col">
        <section class="card section">
          <div class="section-head">
            <h2>Run Breakdown</h2>
          </div>
          <div class="chips">{status_chips}</div>
          <div style="height: 10px"></div>
          <div class="chips">{type_chips}</div>
        </section>

        <section class="card section">
          <div class="section-head">
            <h2>Failure Types</h2>
          </div>
          <div class="chips">{failure_chips}</div>
        </section>
      </div>

      <section class="card section">
        <div class="section-head">
          <h2>Recent Runs</h2>
          <span class="chip">limit: <strong>{_safe(limit)}</strong></span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Status</th>
              <th>Type</th>
              <th>Agent / Team</th>
              <th>Tokens</th>
              <th>Task</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            {_run_rows(runs)}
          </tbody>
        </table>
      </section>

      <section class="card section">
        <div class="section-head">
          <h2>Recent Failures</h2>
          <span class="chip danger">diagnostics</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Type</th>
              <th>Agent / Team</th>
              <th>Error Type</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {_failure_rows(failures)}
          </tbody>
        </table>
      </section>

      {_run_detail_sections(store, runs)}
    </main>

    <footer>
      Exported by Orchgentic. Use <code>orch run-info &lt;run_id&gt;</code> and <code>orch trace &lt;run_id&gt;</code> for full trace inspection.
    </footer>
  </div>
</body>
</html>
"""


def write_dashboard_html(html: str, output: str | Path = DEFAULT_DASHBOARD_PATH) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
