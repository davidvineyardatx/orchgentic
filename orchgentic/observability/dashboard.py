from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from typing import Iterable

from .models import RunRecord
from .store import ObservabilityStore
from .token_intelligence import build_token_intelligence_report


DEFAULT_DASHBOARD_PATH = Path("exports") / "orchgentic_observability_dashboard.html"
OBSERVABILITY_SCHEMA_VERSION = "orchgentic.observability.v1"


def _safe(value) -> str:
    if value is None:
        return "-"
    return escape(str(value))


def _pct(part: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{round((int(part or 0) / int(total or 0)) * 100, 1)}%"


def _short_id(run_id: str | None) -> str:
    return (run_id or "-")[:8]


def _anchor_id(run_id: str | None) -> str:
    safe = "".join(ch for ch in (run_id or "unknown") if ch.isalnum() or ch in {"-", "_"})
    return f"run-{safe}"


def _target(run: RunRecord) -> str:
    return run.team_name or run.agent_name or run.team_id or run.agent_id or "-"


def _tokens_label(run: RunRecord) -> str:
    if run.total_tokens:
        source = run.token_source or "unknown"
        prefix = "estimated tokens used" if source == "estimated" else "actual tokens used" if source == "actual" else "tokens used"
        return f"{prefix}={run.total_tokens}, source={source}"
    if run.estimated_tokens_saved:
        return f"estimated tokens saved≈{run.estimated_tokens_saved}, source={run.token_source}"
    return f"source={run.token_source}"


def _provider_used_label(run: RunRecord) -> str:
    if getattr(run, "external_llm_used", False) is False:
        return "N/A — no LLM used"
    if run.provider and run.model:
        return f"{run.provider} / {run.model}"
    return run.provider or "-"


def _configured_provider_label(run: RunRecord) -> str:
    if run.provider and run.model:
        return f"{run.provider} / {run.model}"
    return run.provider or run.model or "-"


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


def _token_intelligence_section(report: dict) -> str:
    top = report.get("top_savings_run") or {}
    proof_events = report.get("proof_events") or []
    if proof_events:
        proof_rows = "".join(
            f"""
            <tr data-token-proof-row="true" data-token-run-id="{_safe(event.get('run_id'))}" data-token-run-type="{_safe(event.get('run_type'))}" data-token-target="{_safe(event.get('target'))}" data-token-search="{_safe((event.get('run_id') or '') + ' ' + (event.get('run_type') or '') + ' ' + (event.get('target') or '') + ' ' + (event.get('task') or '') + ' ' + (event.get('reason') or ''))}" data-token-total="{_safe(event.get('total_tokens'))}" data-token-saved="{_safe(event.get('estimated_tokens_saved'))}" data-token-tier="{_safe(event.get('execution_tier'))}" data-token-optimization="{_safe(event.get('optimization_opportunity'))}" data-token-event-type="{_safe(event.get('event_type'))}">
              <td rowspan="2"><button class="run-link run-link-button" type="button" data-token-run-target="{_safe('token-' + _anchor_id(event.get('run_id')))}"><code>{_safe(event.get('run_short_id'))}</code></button></td>
              <td>{_safe(event.get('event_type'))}</td>
              <td>{_safe(event.get('component'))}</td>
              <td>{_safe(event.get('token_meaning'))}</td>
              <td>{_safe(event.get('total_tokens'))}</td>
              <td>{_safe(event.get('estimated_tokens_saved'))}</td>
              <td>{_safe(event.get('token_source'))}</td>
              <td>{_safe(event.get('execution_tier'))}</td>
              <td>{_safe(event.get('optimization_opportunity'))}</td>
            </tr>
            <tr class="token-reason-row" data-token-proof-reason-row="true" data-token-run-id="{_safe(event.get('run_id'))}">
              <td colspan="8" class="token-reason-cell"><span>Reason:</span> {_safe(event.get('reason'))}</td>
            </tr>
            """
            for event in proof_events[:8]
        )
    else:
        proof_rows = '<tr><td colspan="9" class="empty">No token proof events yet. Run <code>orch tool run datetime.local --agent Bob</code> to create a direct-tool proof.</td></tr>'

    top_summary = "No saved-token run yet."
    if top:
        top_summary = (
            f"run <button class=\"run-link run-link-button\" type=\"button\" data-token-run-target=\"{_safe('token-' + _anchor_id(top.get('run_id')))}\"><code>{_safe(top.get('run_short_id'))}</code></button> · "
            f"{_safe(top.get('target'))} · saved≈{_safe(top.get('estimated_tokens_saved'))} · "
            f"external_llm_used={_safe(top.get('external_llm_used'))}"
        )

    return f"""
      <details open class="card section collapsible-section token-intelligence" id="token-intelligence-panel">
        <summary class="section-head">
          <h2>Token Intelligence</h2>
          <span class="chip">local reasoning proof</span>
        </summary>
        <div class="section-body">
        <p class="muted-block">Shows when Orchgentic avoided external LLM calls, routed locally, and produced estimated token-savings evidence.</p>
        <div class="metadata-grid">
          <div class="metadata-item"><span>local/deterministic share</span><strong id="token-local-deterministic-share">{_safe(report.get('local_or_deterministic_token_rate', '0%'))}</strong></div>
          <div class="metadata-item"><span>external LLM share</span><strong id="token-external-llm-share">{_safe(report.get('external_llm_token_rate', '0%'))}</strong></div>
          <div class="metadata-item"><span>token_work_total</span><strong id="token-work-total">{_safe(report.get('token_work_total', 0))}</strong></div>
          <div class="metadata-item"><span>direct_bypasses</span><strong id="token-direct-bypasses">{_safe(report.get('direct_bypasses', 0))}</strong></div>
          <div class="metadata-item"><span>deterministic_routes</span><strong id="token-deterministic-routes">{_safe(report.get('deterministic_routes', 0))}</strong></div>
          <div class="metadata-item"><span>local_reasoning_events</span><strong id="token-local-reasoning-events">{_safe(report.get('local_reasoning_events', 0))}</strong></div>
          <div class="metadata-item"><span>llm_events</span><strong id="token-llm-events">{_safe(report.get('llm_events', 0))}</strong></div>
          <div class="metadata-item"><span>estimated_tokens_saved</span><strong id="token-estimated-saved">{_safe(report.get('estimated_tokens_saved', 0))}</strong></div>
          <div class="metadata-item"><span>local_llm_candidate_tokens</span><strong id="token-local-llm-candidate">{_safe(report.get('external_tokens_local_candidate', 0))} ({_safe(report.get('external_tokens_optimization_rate', '0%'))})</strong></div>
          <div class="metadata-item"><span>premium_candidate_tokens</span><strong id="token-premium-candidate">{_safe(report.get('external_tokens_premium_candidate', 0))}</strong></div>
          <div class="metadata-item"><span>top_savings_run</span><strong id="token-top-savings-run">{top_summary}</strong></div>
        </div>
        <p class="muted-block"><strong>Note:</strong> {_safe(report.get('token_source_note'))}.</p>
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Proof Event</th>
              <th>Component</th>
              <th>Meaning</th>
              <th>Tokens Used</th>
              <th>Saved</th>
              <th>Source</th>
              <th>Execution Tier</th>
              <th>Optimization</th>
            </tr>
          </thead>
          <tbody>
            {proof_rows}
            <tr id="token-empty-filtered" style="display:none"><td colspan="9" class="dynamic-empty">No token intelligence events match the current run filters.</td></tr>
          </tbody>
        </table>
        </div>
      </details>
    """


def _run_rows(runs: Iterable[RunRecord]) -> str:
    rows = []
    for run in runs:
        rows.append(
            f"""
            <tr data-dashboard-row="run" data-run-id="{_safe(run.run_id)}" data-status="{_safe(run.status)}" data-type="{_safe(run.run_type)}" data-search="{_safe((run.run_id or '') + ' ' + (run.status or '') + ' ' + (run.run_type or '') + ' ' + _target(run) + ' ' + (run.task or ''))}">
              <td><button class="run-link run-link-button" type="button" data-run-target="{_safe(_anchor_id(run.run_id))}"><code>{_safe(_short_id(run.run_id))}</code></button></td>
              <td><span class="pill {_status_class(run.status)}">{_safe(run.status)}</span></td>
              <td>{_safe(run.run_type)}</td>
              <td>{_safe(_target(run))}</td>
              <td>{_safe(_tokens_label(run))}</td>
              <td>{_safe(run.task)}</td>
              <td>{_safe(run.started_at)}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr id="runs-empty-base"><td colspan="7" class="empty">No runs found. Generate an agent, tool, or team run and refresh the dashboard.</td></tr>'


def _failure_rows(failures: Iterable[RunRecord]) -> str:
    rows = []
    for run in failures:
        error_type = run.error_type or "unknown"
        summary = run.error_message or "Inspect trace events for details."
        rows.append(
            f"""
            <tr data-dashboard-row="failure" data-status="{_safe(run.status)}" data-type="{_safe(run.run_type)}" data-search="{_safe((run.run_id or '') + ' ' + (run.run_type or '') + ' ' + _target(run) + ' ' + error_type + ' ' + summary)}">
              <td><button class="run-link run-link-button" type="button" data-run-target="{_safe(_anchor_id(run.run_id))}"><code>{_safe(_short_id(run.run_id))}</code></button></td>
              <td>{_safe(run.run_type)}</td>
              <td>{_safe(_target(run))}</td>
              <td>{_safe(error_type)}</td>
              <td>{_safe(summary)}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr id="failures-empty-base"><td colspan="5" class="empty">No failures found. That is a good sign — failed runs will appear here when diagnostics are available.</td></tr>'


def _first_run_guidance(total_runs: int, loaded_runs: int) -> str:
    if total_runs or loaded_runs:
        return ""
    return """
      <section class="card section first-run-guidance">
        <div class="section-head">
          <h2>Fresh Workspace Guidance</h2>
          <span class="chip">clean install</span>
        </div>
        <p class="muted-block">No observability runs exist yet. This dashboard is ready; generate a simple trace and refresh it.</p>
        <div class="metadata-grid">
          <div class="metadata-item"><span>1. Create a trace</span><strong><code>orch tool run datetime.local --agent Bob</code></strong></div>
          <div class="metadata-item"><span>2. Check health</span><strong><code>orch doctor observability</code></strong></div>
          <div class="metadata-item"><span>3. Refresh dashboard</span><strong><code>orch dashboard</code></strong></div>
          <div class="metadata-item"><span>4. Open dashboard</span><strong><code>orch dashboard --open</code></strong></div>
        </div>
      </section>
    """



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
        source = getattr(event, "token_source", None) or "unknown"
        prefix = "estimated tokens used" if source == "estimated" else "actual tokens used" if source == "actual" else "tokens used"
        return f"{prefix}={event.total_tokens}, source={source}"
    if getattr(event, "estimated_tokens_saved", 0):
        return f"estimated tokens saved≈{event.estimated_tokens_saved}, source={event.token_source}"
    return getattr(event, "token_source", None) or "-"


def _is_token_proof_event(event) -> bool:
    event_type = getattr(event, "event_type", "") or ""
    if event_type in {"routing.bypassed", "routing.completed", "reasoning.completed", "llm.started", "llm.completed", "llm.failed"}:
        return True
    return bool(getattr(event, "total_tokens", 0) or getattr(event, "estimated_tokens_saved", 0))


def _token_event_meaning(event) -> str:
    if getattr(event, "total_tokens", 0):
        return "tokens used"
    if getattr(event, "estimated_tokens_saved", 0):
        return "tokens saved"
    return "proof/context"


def _event_local_llm_eligible(event) -> bool:
    data = getattr(event, "data", None) or {}
    if data.get("local_llm_eligible") is not None:
        return bool(data.get("local_llm_eligible"))
    if not int(getattr(event, "total_tokens", 0) or 0):
        return False
    purpose = str(data.get("llm_purpose") or getattr(event, "name", None) or "").lower()
    role = str(data.get("team_role") or data.get("role") or "").lower()
    agent = str(data.get("agent_name") or data.get("agent_id") or "").lower()
    if purpose in {"tool_decision", "routing", "planning", "quality_review"}:
        return True
    if role in {"member", "researcher", "writer", "reviewer"}:
        return True
    if any(marker in agent for marker in ["research", "writer", "review"]):
        return True
    return False


def _token_execution_tier(event) -> str:
    if int(getattr(event, "estimated_tokens_saved", 0) or 0):
        return "deterministic saved"
    if not int(getattr(event, "total_tokens", 0) or 0):
        return "proof/context"
    data = getattr(event, "data", None) or {}
    explicit = data.get("execution_tier") or data.get("recommended_execution_tier")
    if explicit:
        return str(explicit).replace("_", " ")
    role = str(data.get("team_role") or data.get("role") or "").lower()
    purpose = str(data.get("llm_purpose") or getattr(event, "name", None) or "").lower()
    if role == "synthesis" or "synthesis" in purpose:
        return "premium external candidate"
    if _event_local_llm_eligible(event):
        return "local LLM candidate"
    return "external LLM"


def _token_optimization_opportunity(event) -> str:
    data = getattr(event, "data", None) or {}
    if data.get("optimization_opportunity"):
        return str(data.get("optimization_opportunity")).replace("_", " ")
    tier = _token_execution_tier(event)
    if tier == "deterministic saved":
        return "already avoided external LLM"
    if tier == "local LLM candidate":
        return "move to local LLM"
    if tier == "premium external candidate":
        return "keep external or make configurable"
    if tier == "proof/context":
        return "none"
    return "monitor"


def _token_event_reason(event) -> str:
    data = getattr(event, "data", None) or {}
    explicit_reason = data.get("token_work_reason") or data.get("reason")
    if explicit_reason:
        reason = explicit_reason
    elif getattr(event, "message", None):
        reason = event.message
    elif str(getattr(event, "event_type", "") or "").startswith("llm."):
        purpose = data.get("llm_purpose") or getattr(event, "name", None) or "LLM call"
        actor = data.get("agent_name") or data.get("agent_id") or "agent"
        team = data.get("team")
        role = data.get("team_role") or data.get("role")
        scope = actor
        if team:
            scope += f" / team={team}"
        if role:
            scope += f" / role={role}"
        reason = f"LLM tokens used by {scope} for {purpose}."
    elif getattr(event, "estimated_tokens_saved", 0):
        reason = data.get("savings_reason") or data.get("reason") or "Estimated tokens saved by local/direct routing."
    else:
        reason = data.get("reason") or data.get("llm_purpose") or "Trace event included for token proof context."

    source_reason = data.get("token_count_source_reason")
    if source_reason and getattr(event, "total_tokens", 0):
        reason = f"{reason} Count source: {source_reason}."
    return reason


def _token_modal_note(run: RunRecord) -> str:
    if int(run.estimated_tokens_saved or 0) > 0:
        return "Estimated token savings are operational estimates of avoided LLM routing/execution overhead, not billing claims."
    if int(run.total_tokens or 0) > 0 and (run.token_source or "") == "estimated":
        return "Token usage is estimated because exact provider usage metadata was not available for one or more LLM calls in this runtime path."
    if int(run.total_tokens or 0) > 0:
        return "Token usage reflects provider-reported or runtime-recorded token counts for this run."
    return "No external LLM tokens were recorded for this run."


def _token_proof_event_rows(events) -> str:
    rows = []
    for event in events:
        if not _is_token_proof_event(event):
            continue
        rows.append(
            f"""
            <tr>
              <td rowspan="2">{_safe(event.event_type)}</td>
              <td>{_safe(event.component)}</td>
              <td>{_safe(event.name)}</td>
              <td>{_safe(_token_event_meaning(event))}</td>
              <td>{_safe(event.total_tokens or 0)}</td>
              <td>{_safe(event.estimated_tokens_saved or 0)}</td>
              <td>{_safe(event.token_source)}</td>
              <td>{_safe(_token_execution_tier(event))}</td>
              <td>{_safe(_token_optimization_opportunity(event))}</td>
            </tr>
            <tr class="token-reason-row">
              <td colspan="8" class="token-reason-cell"><span>Reason:</span> {_safe(_token_event_reason(event))}</td>
            </tr>
            """
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9" class="empty">No token proof events found for this run.</td></tr>'


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
                <div><span>provider used</span><strong>{_safe(_provider_used_label(run))}</strong></div>
                <div><span>configured provider</span><strong>{_safe(_configured_provider_label(run))}</strong></div>
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


def _modal_run_detail_templates(store: ObservabilityStore, runs: Iterable[RunRecord]) -> str:
    templates = []
    for run in runs:
        events = store.list_events(run.run_id)
        templates.append(
            f"""
            <template id="{_safe(_anchor_id(run.run_id))}">
              <div class="modal-detail">
                <div class="detail-grid">
                  <div><span>status</span><strong>{_safe(run.status)}</strong></div>
                  <div><span>type</span><strong>{_safe(run.run_type)}</strong></div>
                  <div><span>agent/team</span><strong>{_safe(_target(run))}</strong></div>
                  <div><span>provider used</span><strong>{_safe(_provider_used_label(run))}</strong></div>
                  <div><span>configured provider</span><strong>{_safe(_configured_provider_label(run))}</strong></div>
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
              </div>
            </template>
            """
        )
    return "\n".join(templates)


def _modal_token_detail_templates(store: ObservabilityStore, runs: Iterable[RunRecord]) -> str:
    templates = []
    for run in runs:
        events = store.list_events(run.run_id)
        token_proof_count = sum(1 for event in events if _is_token_proof_event(event))
        local_candidate_tokens = sum(int(getattr(event, "total_tokens", 0) or 0) for event in events if _token_optimization_opportunity(event) == "move to local LLM")
        premium_candidate_tokens = sum(int(getattr(event, "total_tokens", 0) or 0) for event in events if _token_execution_tier(event) == "premium external candidate")
        token_work_total = int(run.total_tokens or 0) + int(run.estimated_tokens_saved or 0)
        local_or_deterministic_rate = _pct(int(run.estimated_tokens_saved or 0), token_work_total)
        external_llm_rate = _pct(int(run.total_tokens or 0), token_work_total)
        local_execution = not bool(run.external_llm_used)
        templates.append(
            f"""
            <template id="{_safe('token-' + _anchor_id(run.run_id))}">
              <div class="modal-detail token-modal-detail">
                <div class="detail-grid">
                  <div><span>run_id</span><strong>{_safe(run.run_id)}</strong></div>
                  <div><span>external_llm_used</span><strong>{_safe(bool(run.external_llm_used))}</strong></div>
                  <div><span>local_execution</span><strong>{_safe(local_execution)}</strong></div>
                  <div><span>local/deterministic share</span><strong>{_safe(local_or_deterministic_rate)}</strong></div>
                  <div><span>external LLM share</span><strong>{_safe(external_llm_rate)}</strong></div>
                  <div><span>token_work_total</span><strong>{_safe(token_work_total)}</strong></div>
                  <div><span>provider used</span><strong>{_safe(_provider_used_label(run))}</strong></div>
                  <div><span>configured provider</span><strong>{_safe(_configured_provider_label(run))}</strong></div>
                  <div><span>input_tokens</span><strong>{_safe(run.input_tokens or 0)}</strong></div>
                  <div><span>output_tokens</span><strong>{_safe(run.output_tokens or 0)}</strong></div>
                  <div><span>total_tokens</span><strong>{_safe(run.total_tokens or 0)}</strong></div>
                  <div><span>estimated_tokens_saved</span><strong>{_safe(run.estimated_tokens_saved or 0)}</strong></div>
                  <div><span>token_count_source</span><strong>{_safe(run.token_source)}</strong></div>
                  <div><span>local_llm_candidate_tokens</span><strong>{_safe(local_candidate_tokens)}</strong></div>
                  <div><span>premium_candidate_tokens</span><strong>{_safe(premium_candidate_tokens)}</strong></div>
                  <div><span>token_proof_events</span><strong>{_safe(token_proof_count)}</strong></div>
                </div>

                <p class="muted-block"><strong>Note:</strong> {_safe(_token_modal_note(run))}</p>

                <table>
                  <thead>
                    <tr>
                      <th>Proof Event</th>
                      <th>Component</th>
                      <th>Name</th>
                      <th>Token Meaning</th>
                      <th>Tokens Used</th>
                      <th>Saved</th>
                      <th>Count Source</th>
                      <th>Execution Tier</th>
                      <th>Optimization</th>
                            </tr>
                  </thead>
                  <tbody>
                    {_token_proof_event_rows(events)}
                  </tbody>
                </table>
              </div>
            </template>
            """
        )
    return "\n".join(templates)


def _run_detail_metadata_script(runs: Iterable[RunRecord]) -> str:
    items = []
    for run in runs:
        items.append({
            "id": _anchor_id(run.run_id),
            "short_id": _short_id(run.run_id),
            "run_id": run.run_id or "",
            "target": _target(run),
            "status": run.status or "",
            "run_type": run.run_type or "",
            "tokens": _tokens_label(run),
            "task": run.task or "",
            "run_info_command": f"orch run-info {run.run_id}",
            "trace_command": f"orch trace {run.run_id}",
            "export_command": f"orch export-run {run.run_id} --output exports/run-{_short_id(run.run_id)}.json",
        })
    return json.dumps(items)


def _token_detail_metadata_script(store: ObservabilityStore, runs: Iterable[RunRecord]) -> str:
    items = []
    for run in runs:
        try:
            events = store.list_events(run.run_id)
        except Exception:  # pragma: no cover - defensive dashboard fallback
            events = []
        local_candidate_tokens = sum(int(getattr(event, "total_tokens", 0) or 0) for event in events if _token_optimization_opportunity(event) == "move to local LLM")
        premium_candidate_tokens = sum(int(getattr(event, "total_tokens", 0) or 0) for event in events if _token_execution_tier(event) == "premium external candidate")
        search_text = " ".join([run.run_id or "", run.status or "", run.run_type or "", _target(run), run.task or ""]).lower()
        items.append({
            "id": "token-" + _anchor_id(run.run_id),
            "short_id": _short_id(run.run_id),
            "run_id": run.run_id or "",
            "target": _target(run),
            "status": run.status or "",
            "run_type": run.run_type or "",
            "search": search_text,
            "tokens": _tokens_label(run),
            "external_llm_used": bool(run.external_llm_used),
            "estimated_tokens_saved": int(run.estimated_tokens_saved or 0),
            "total_tokens": int(run.total_tokens or 0),
            "local_candidate_tokens": local_candidate_tokens,
            "premium_candidate_tokens": premium_candidate_tokens,
            "token_source": run.token_source or "",
            "run_info_command": f"orch run-info {run.run_id}",
            "trace_command": f"orch trace {run.run_id}",
            "export_command": f"orch export-run {run.run_id} --output exports/run-{_short_id(run.run_id)}.json",
        })
    return json.dumps(items)


def _modal_script(store: ObservabilityStore, runs: Iterable[RunRecord]) -> str:
    run_details = _run_detail_metadata_script(runs)
    token_details = _token_detail_metadata_script(store, runs)
    script = """
  <script>
    (function () {
      var runDetails = __RUN_DETAILS__;
      var tokenDetails = __TOKEN_DETAILS__;
      var runDetailById = {};
      var tokenDetailById = {};
      runDetails.forEach(function (item) {
        runDetailById[item.id] = item;
      });
      tokenDetails.forEach(function (item) {
        tokenDetailById[item.id] = item;
      });

      var modal = document.getElementById("run-detail-modal");
      var modalTitle = document.getElementById("run-detail-modal-title");
      var modalSubtitle = document.getElementById("run-detail-modal-subtitle");
      var modalBody = document.getElementById("run-detail-modal-body");
      var modalClose = document.getElementById("run-detail-modal-close");
      var copyStatus = document.getElementById("copy-status");
      var currentRunMetadata = null;

      function openRunModal(id) {
        var template = document.getElementById(id);
        var metadata = runDetailById[id];

        if (!template || !modal || !modalBody || !metadata) return;

        modalTitle.innerHTML = "Run Details: <code>" + metadata.short_id + "</code>";
        modalSubtitle.textContent = metadata.run_id + " · " + metadata.target + " · " + metadata.status + " · " + metadata.tokens;
        modalBody.innerHTML = "";
        currentRunMetadata = metadata;
        if (copyStatus) copyStatus.textContent = "";
        modalBody.appendChild(template.content.cloneNode(true));

        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        history.replaceState(null, "", "#" + id);
        modalClose.focus();
      }

      function openTokenModal(id) {
        var template = document.getElementById(id);
        var metadata = tokenDetailById[id];

        if (!template || !modal || !modalBody || !metadata) return;

        modalTitle.innerHTML = "Token Details: <code>" + metadata.short_id + "</code>";
        modalSubtitle.textContent = metadata.run_id + " · external_llm_used=" + metadata.external_llm_used + " · " + metadata.tokens;
        modalBody.innerHTML = "";
        currentRunMetadata = metadata;
        if (copyStatus) copyStatus.textContent = "";
        modalBody.appendChild(template.content.cloneNode(true));

        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        history.replaceState(null, "", "#" + id);
        modalClose.focus();
      }

      function closeRunModal() {
        if (!modal) return;
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        if (modalBody) modalBody.innerHTML = "";
        currentRunMetadata = null;
        if (copyStatus) copyStatus.textContent = "";
        history.replaceState(null, "", window.location.pathname + window.location.search);
      }


      function copyText(value, label) {
        if (!value) return;
        function copied() {
          if (copyStatus) {
            copyStatus.textContent = "Copied " + label;
            setTimeout(function () { copyStatus.textContent = ""; }, 1800);
          }
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(value).then(copied).catch(function () {
            fallbackCopy(value);
            copied();
          });
        } else {
          fallbackCopy(value);
          copied();
        }
      }

      function fallbackCopy(value) {
        var textArea = document.createElement("textarea");
        textArea.value = value;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try { document.execCommand("copy"); } catch (error) {}
        document.body.removeChild(textArea);
      }

      document.querySelectorAll("[data-copy-action]").forEach(function (button) {
        button.addEventListener("click", function () {
          if (!currentRunMetadata) return;
          var action = button.getAttribute("data-copy-action");
          if (action === "run_id") copyText(currentRunMetadata.run_id, "Run ID");
          if (action === "run_info") copyText(currentRunMetadata.run_info_command, "run-info command");
          if (action === "trace") copyText(currentRunMetadata.trace_command, "trace command");
          if (action === "export") copyText(currentRunMetadata.export_command, "export command");
        });
      });

      var dashboardSearch = document.getElementById("dashboard-search");
      var filterButtons = document.querySelectorAll("[data-filter-kind]");
      var visibleRunCount = document.getElementById("visible-run-count");
      var metadataVisibleRunCount = document.getElementById("metadata-visible-run-count");
      var filteredEmptyRow = document.getElementById("runs-empty-filtered");
      var tokenEmptyFilteredRow = document.getElementById("token-empty-filtered");
      var pageSizeSelect = document.getElementById("page-size-select");
      var pageFirst = document.getElementById("page-first");
      var pagePrev = document.getElementById("page-prev");
      var pageNext = document.getElementById("page-next");
      var pageLast = document.getElementById("page-last");
      var pageLabel = document.getElementById("page-label");
      var paginationRange = document.getElementById("pagination-range");
      var activeFilter = { kind: "all", value: "all" };
      var currentPage = 1;

      function selectedPageSize() {
        if (!pageSizeSelect || pageSizeSelect.value === "all") return Infinity;
        var parsed = parseInt(pageSizeSelect.value, 10);
        return isNaN(parsed) || parsed <= 0 ? 50 : parsed;
      }

      function percent(part, total) {
        if (!total) return "0%";
        return (Math.round((part / total) * 1000) / 10).toFixed(1).replace(".0", ".0") + "%";
      }

      function setText(id, value) {
        var element = document.getElementById(id);
        if (element) element.textContent = String(value);
      }

      function runMatchesCurrentFilters(row, query) {
        var searchText = (row.getAttribute("data-search") || "").toLowerCase();
        var status = row.getAttribute("data-status") || "";
        var type = row.getAttribute("data-type") || "";
        var matchesSearch = !query || searchText.indexOf(query) !== -1;
        var matchesQuickFilter =
          activeFilter.kind === "all" ||
          (activeFilter.kind === "status" && status === activeFilter.value) ||
          (activeFilter.kind === "type" && type === activeFilter.value);
        return matchesSearch && matchesQuickFilter;
      }

      function applyTokenIntelligenceFilters(matchingRows) {
        var matchingIds = {};
        matchingRows.forEach(function (row) {
          var runId = row.getAttribute("data-run-id") || "";
          if (runId) matchingIds[runId] = true;
        });

        var filteredTokenDetails = tokenDetails.filter(function (item) {
          return !!matchingIds[item.run_id];
        });

        var totalTokens = 0;
        var estimatedSaved = 0;
        var localCandidate = 0;
        var premiumCandidate = 0;
        var topSavings = null;

        filteredTokenDetails.forEach(function (item) {
          var tokens = Number(item.total_tokens || 0);
          var saved = Number(item.estimated_tokens_saved || 0);
          totalTokens += tokens;
          estimatedSaved += saved;
          localCandidate += Number(item.local_candidate_tokens || 0);
          premiumCandidate += Number(item.premium_candidate_tokens || 0);
          if (saved > 0 && (!topSavings || saved > Number(topSavings.estimated_tokens_saved || 0))) {
            topSavings = item;
          }
        });

        var tokenWorkTotal = totalTokens + estimatedSaved;
        setText("token-local-deterministic-share", percent(estimatedSaved, tokenWorkTotal));
        setText("token-external-llm-share", percent(totalTokens, tokenWorkTotal));
        setText("token-work-total", tokenWorkTotal);
        setText("token-estimated-saved", estimatedSaved);
        setText("token-local-llm-candidate", localCandidate + " (" + percent(localCandidate, totalTokens) + ")");
        setText("token-premium-candidate", premiumCandidate);

        if (topSavings) {
          var topElement = document.getElementById("token-top-savings-run");
          if (topElement) {
            topElement.textContent = "";
            topElement.appendChild(document.createTextNode("run "));

            var runButton = document.createElement("button");
            runButton.className = "run-link run-link-button";
            runButton.type = "button";
            runButton.setAttribute("data-token-run-target", topSavings.id);
            runButton.addEventListener("click", function () { openTokenModal(topSavings.id); });

            var code = document.createElement("code");
            code.textContent = topSavings.short_id || "";
            runButton.appendChild(code);
            topElement.appendChild(runButton);

            topElement.appendChild(document.createTextNode(
              " · " + (topSavings.target || "") +
              " · saved≈" + (topSavings.estimated_tokens_saved || 0) +
              " · external_llm_used=" + topSavings.external_llm_used
            ));
          }
        } else {
          setText("token-top-savings-run", "No saved-token run for current filters.");
        }

        var visibleTokenRows = 0;
        var directBypasses = 0;
        var deterministicRoutes = 0;
        var llmEvents = 0;
        var localReasoningEvents = 0;
        document.querySelectorAll("[data-token-proof-row]").forEach(function (row) {
          var runId = row.getAttribute("data-token-run-id") || "";
          var shouldShow = !!matchingIds[runId];
          row.style.display = shouldShow ? "" : "none";
          if (!shouldShow) return;
          visibleTokenRows += 1;
          var eventType = row.getAttribute("data-token-event-type") || "";
          var tier = row.getAttribute("data-token-tier") || "";
          if (eventType === "routing.bypassed") directBypasses += 1;
          if (tier === "deterministic_saved") deterministicRoutes += 1;
          if (eventType.indexOf("llm.") === 0) llmEvents += 1;
          if (eventType === "reasoning.completed") localReasoningEvents += 1;
        });

        document.querySelectorAll("[data-token-proof-reason-row]").forEach(function (row) {
          var runId = row.getAttribute("data-token-run-id") || "";
          row.style.display = matchingIds[runId] ? "" : "none";
        });

        setText("token-direct-bypasses", directBypasses);
        setText("token-deterministic-routes", deterministicRoutes);
        setText("token-local-reasoning-events", localReasoningEvents);
        setText("token-llm-events", llmEvents);

        if (tokenEmptyFilteredRow) {
          tokenEmptyFilteredRow.style.display = visibleTokenRows === 0 ? "" : "none";
        }
      }

      function applyDashboardFilters() {
        var query = dashboardSearch ? dashboardSearch.value.toLowerCase().trim() : "";
        var matchingRows = [];
        var allRows = Array.prototype.slice.call(document.querySelectorAll("[data-dashboard-row='run']"));

        allRows.forEach(function (row) {
          if (runMatchesCurrentFilters(row, query)) matchingRows.push(row);
        });

        var matchingCount = matchingRows.length;
        var pageSize = selectedPageSize();
        var totalPages = pageSize === Infinity ? 1 : Math.max(1, Math.ceil(matchingCount / pageSize));
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        var startIndex = pageSize === Infinity ? 0 : (currentPage - 1) * pageSize;
        var endIndex = pageSize === Infinity ? matchingCount : Math.min(startIndex + pageSize, matchingCount);

        allRows.forEach(function (row) { row.style.display = "none"; });
        matchingRows.slice(startIndex, endIndex).forEach(function (row) { row.style.display = ""; });

        if (visibleRunCount) visibleRunCount.textContent = matchingCount;
        if (metadataVisibleRunCount) metadataVisibleRunCount.textContent = matchingCount;

        if (filteredEmptyRow) {
          var hasLoadedRows = allRows.length > 0;
          filteredEmptyRow.style.display = hasLoadedRows && matchingCount === 0 ? "" : "none";
        }

        if (paginationRange) {
          var first = matchingCount === 0 ? 0 : startIndex + 1;
          var last = matchingCount === 0 ? 0 : endIndex;
          paginationRange.textContent = "Showing " + first + "–" + last + " of " + matchingCount + " matching runs";
        }

        if (pageLabel) pageLabel.textContent = "Page " + currentPage + " of " + totalPages;

        var disableBack = currentPage <= 1 || matchingCount === 0;
        var disableForward = currentPage >= totalPages || matchingCount === 0;
        if (pageFirst) pageFirst.disabled = disableBack;
        if (pagePrev) pagePrev.disabled = disableBack;
        if (pageNext) pageNext.disabled = disableForward;
        if (pageLast) pageLast.disabled = disableForward;

        applyTokenIntelligenceFilters(matchingRows);
      }

      if (dashboardSearch) {
        dashboardSearch.addEventListener("input", function () {
          currentPage = 1;
          applyDashboardFilters();
        });
      }
      if (pageSizeSelect) {
        pageSizeSelect.addEventListener("change", function () {
          currentPage = 1;
          applyDashboardFilters();
        });
      }
      if (pageFirst) {
        pageFirst.addEventListener("click", function () {
          currentPage = 1;
          applyDashboardFilters();
        });
      }
      if (pagePrev) {
        pagePrev.addEventListener("click", function () {
          currentPage -= 1;
          applyDashboardFilters();
        });
      }
      if (pageNext) {
        pageNext.addEventListener("click", function () {
          currentPage += 1;
          applyDashboardFilters();
        });
      }
      if (pageLast) {
        pageLast.addEventListener("click", function () {
          var pageSize = selectedPageSize();
          var query = dashboardSearch ? dashboardSearch.value.toLowerCase().trim() : "";
          var allRows = Array.prototype.slice.call(document.querySelectorAll("[data-dashboard-row='run']"));
          var filteredCount = allRows.filter(function (row) { return runMatchesCurrentFilters(row, query); }).length;
          currentPage = pageSize === Infinity ? 1 : Math.max(1, Math.ceil(filteredCount / pageSize));
          applyDashboardFilters();
        });
      }

      filterButtons.forEach(function (button) {
        button.addEventListener("click", function () {
          filterButtons.forEach(function (item) { item.classList.remove("active"); });
          button.classList.add("active");
          activeFilter = {
            kind: button.getAttribute("data-filter-kind"),
            value: button.getAttribute("data-filter-value")
          };
          currentPage = 1;
          applyDashboardFilters();
        });
      });

      applyDashboardFilters();

      document.querySelectorAll("[data-run-target]").forEach(function (control) {
        control.addEventListener("click", function () {
          var id = control.getAttribute("data-run-target");
          openRunModal(id);
        });
      });

      document.querySelectorAll("[data-token-run-target]").forEach(function (control) {
        control.addEventListener("click", function () {
          var id = control.getAttribute("data-token-run-target");
          openTokenModal(id);
        });
      });

      if (modalClose) {
        modalClose.addEventListener("click", closeRunModal);
      }

      if (modal) {
        modal.addEventListener("click", function (event) {
          if (event.target === modal) closeRunModal();
        });
      }

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeRunModal();
      });

      if (window.location.hash) {
        var id = window.location.hash.slice(1);
        if (document.getElementById(id)) {
          if (id.indexOf("token-run-") === 0) {
            openTokenModal(id);
          } else {
            openRunModal(id);
          }
        }
      }
    })();
  </script>
"""
    return script.replace("__RUN_DETAILS__", run_details).replace("__TOKEN_DETAILS__", token_details)



def _tokens_event_label(event) -> str:
    if getattr(event, "total_tokens", 0):
        source = getattr(event, "token_source", None) or "unknown"
        prefix = "estimated tokens used" if source == "estimated" else "actual tokens used" if source == "actual" else "tokens used"
        return f"{prefix}={event.total_tokens}, source={source}"
    if getattr(event, "estimated_tokens_saved", 0):
        return f"estimated tokens saved≈{event.estimated_tokens_saved}, source={event.token_source}"
    return getattr(event, "token_source", None) or "-"


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
    token_report = build_token_intelligence_report(store, limit=limit, status=status, run_type=run_type, agent=agent, team=team)

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
    db_path = getattr(store, "db_path", None) or getattr(store, "path", None) or "-"
    loaded_runs_count = len(runs)
    loaded_failures_count = len(failures)
    schema_label = OBSERVABILITY_SCHEMA_VERSION
    first_run_guidance = _first_run_guidance(total, loaded_runs_count)

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
    .muted-block {{ color: var(--muted); margin: 0 0 14px; line-height: 1.5; }}
    .first-run-guidance {{ border-color: rgba(255, 138, 31, .42); background: linear-gradient(180deg, rgba(255, 138, 31, .08), rgba(18, 22, 32, .96)); }}
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
    details.section {{ padding: 0; }}
    details.section > summary.section-head {{
      cursor: pointer;
      list-style: none;
      padding: 18px;
      margin-bottom: 0;
      border-radius: 18px 18px 0 0;
    }}
    details.section > summary.section-head::-webkit-details-marker {{ display: none; }}
    details.section > summary.section-head::after {{
      content: "Collapse";
      color: var(--muted);
      border: 1px solid var(--line);
      background: var(--panel-2);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 700;
      margin-left: auto;
    }}
    details.section:not([open]) > summary.section-head::after {{ content: "Expand"; }}
    details.section > summary.section-head:hover::after {{
      color: var(--orange);
      border-color: rgba(255, 138, 31, .55);
      background: rgba(255, 138, 31, .10);
    }}
    .section-body {{ padding: 0 18px 18px; }}
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

    .token-reason-row td {{
      padding-top: 0;
      border-top: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }}
    .token-reason-cell {{
      background: rgba(255,255,255,.018);
      border-left: 2px solid rgba(255, 138, 31, .35);
      overflow-wrap: anywhere;
    }}
    .token-reason-cell span {{
      color: #ffd6ad;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .05em;
      margin-right: 6px;
      font-size: 11px;
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

    .run-link-button {{
      border: 0;
      background: transparent;
      padding: 0;
      cursor: pointer;
      font: inherit;
    }}
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 28px;
      background: rgba(0, 0, 0, .72);
      backdrop-filter: blur(8px);
      z-index: 1000;
    }}
    .modal-backdrop.open {{
      display: flex;
    }}
    .modal-panel {{
      width: min(1120px, 96vw);
      max-height: 88vh;
      overflow: auto;
      background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.02)), var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      box-shadow: 0 30px 90px rgba(0,0,0,.55);
    }}
    .modal-head {{
      position: sticky;
      top: 0;
      z-index: 1;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
      background: rgba(18, 22, 32, .96);
      border-bottom: 1px solid var(--line);
    }}
    .modal-title {{
      margin: 0;
      font-size: 20px;
      letter-spacing: -0.02em;
    }}
    .modal-subtitle {{
      color: var(--muted);
      margin-top: 6px;
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .modal-close {{
      border: 1px solid rgba(255, 138, 31, .35);
      background: rgba(255, 138, 31, .10);
      color: var(--orange);
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
      font-weight: 800;
      font-family: inherit;
    }}
    .modal-close:hover {{
      background: rgba(255, 138, 31, .20);
    }}
    .modal-body {{
      padding: 18px 20px 22px;
    }}
    .modal-detail table {{
      margin-top: 14px;
    }}



    .metadata-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }}
    .metadata-item {{
      background: rgba(255,255,255,.025);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px;
    }}
    .metadata-item span {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: 5px;
    }}
    .metadata-item strong {{
      display: block;
      overflow-wrap: anywhere;
      font-size: 13px;
      font-weight: 800;
    }}
    .dynamic-empty {{
      color: var(--muted);
      text-align: center;
      padding: 22px;
      border-top: 1px solid var(--line);
    }}


    .pagination-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .pagination-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .page-button {{
      color: var(--muted);
      background: rgba(255,255,255,.035);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 11px;
      cursor: pointer;
      font-family: inherit;
      font-weight: 700;
      font-size: 12px;
    }}
    .page-button:hover:not(:disabled) {{
      color: var(--orange);
      border-color: rgba(255, 138, 31, .55);
      background: rgba(255, 138, 31, .10);
    }}
    .page-button:disabled {{
      opacity: .45;
      cursor: not-allowed;
    }}
    .page-size-select {{
      color: var(--text);
      background: rgba(255,255,255,.035);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 10px;
      font: inherit;
      font-size: 12px;
      font-weight: 700;
    }}

    .dashboard-controls {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 14px;
    }}
    .dashboard-search {{
      width: 100%;
      color: var(--text);
      background: rgba(255,255,255,.035);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 11px 12px;
      font: inherit;
      outline: none;
    }}
    .dashboard-search:focus {{
      border-color: rgba(255, 138, 31, .7);
      box-shadow: 0 0 0 3px rgba(255, 138, 31, .10);
    }}
    .quick-filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .filter-button,
    .copy-button {{
      color: var(--muted);
      background: rgba(255,255,255,.035);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 11px;
      cursor: pointer;
      font-family: inherit;
      font-weight: 700;
      font-size: 12px;
    }}
    .filter-button.active,
    .filter-button:hover,
    .copy-button:hover {{
      color: var(--orange);
      border-color: rgba(255, 138, 31, .55);
      background: rgba(255, 138, 31, .10);
    }}
    .row-count {{
      color: var(--muted);
      font-size: 12px;
    }}
    .modal-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0 0 14px;
    }}
    .copy-status {{
      color: var(--green);
      font-size: 12px;
      margin-left: 4px;
      align-self: center;
    }}

    @media (max-width: 900px) {{
      .grid, .two-col, .dashboard-controls, .metadata-grid {{ grid-template-columns: 1fr; }}
      .quick-filters {{ justify-content: flex-start; }}
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
        <h1>DASHBOARD</h1>
        <div class="subtitle">Summary of runs, failures, token usage, and estimated savings.</div>
      </div>
      <div class="meta">
        generated_at: {_safe(generated_at)}<br />
        active_filters: {_safe(active_filters)}<br />
        schema: {_safe(schema_label)}
      </div>
    </header>

    <main>
      <div class="grid">
        {_metric_card("Total Runs", stats.get("total_runs", 0), f"Success rate {success_rate}")}
        {_metric_card("Local Runs", token_report.get("local_runs", 0), f"{token_report.get('local_run_rate', '0%')} avoided external LLM usage")}
        {_metric_card("External LLM Runs", token_report.get("external_llm_runs", 0), f"{token_report.get('external_llm_rate', '0%')} used an LLM")}
        {_metric_card("Estimated Tokens Saved", stats.get("estimated_tokens_saved", 0), "operational estimate")}
        {_metric_card("Total Tokens", stats.get("total_tokens", 0), "provider-reported or estimated")}
        {_metric_card("Failures", failed, f"{failure_stats.get("total_failures", 0)} failed run(s)")}
      </div>

      <details open class="card section collapsible-section" id="recent-failures-panel">
        <summary class="section-head">
          <h2>Recent Failures</h2>
          <span class="chip danger">diagnostics</span>
        </summary>
        <div class="section-body">
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
        </div>
      </details>

      <details open class="card section collapsible-section" id="recent-runs-panel">
        <summary class="section-head">
          <h2>Recent Runs</h2>
          <div class="chips">
            <span class="chip">visible: <strong id="visible-run-count">{_safe(len(runs))}</strong></span>
            <span class="chip">limit: <strong>{_safe(limit)}</strong></span>
          </div>
        </summary>
        <div class="section-body">
          <div class="dashboard-controls" aria-label="Dashboard table controls">
            <input id="dashboard-search" class="dashboard-search" type="search" placeholder="Search runs by id, status, type, agent/team, or task..." />
            <div class="quick-filters" aria-label="Quick filters">
              <button class="filter-button active" type="button" data-filter-kind="all" data-filter-value="all">All</button>
              <button class="filter-button" type="button" data-filter-kind="status" data-filter-value="completed">Completed</button>
              <button class="filter-button" type="button" data-filter-kind="status" data-filter-value="failed">Failed</button>
              <button class="filter-button" type="button" data-filter-kind="status" data-filter-value="hold_for_confirmation">Holds</button>
              <button class="filter-button" type="button" data-filter-kind="type" data-filter-value="tool">Tool</button>
              <button class="filter-button" type="button" data-filter-kind="type" data-filter-value="agent">Agent</button>
              <button class="filter-button" type="button" data-filter-kind="type" data-filter-value="team">Team</button>
            </div>
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
              <tr id="runs-empty-filtered" style="display:none"><td colspan="7" class="dynamic-empty">No runs match the current search or quick filter. Clear the search box or choose All to show loaded runs again.</td></tr>
            </tbody>
          </table>
          <div class="pagination-controls">
            <div>
              <strong id="pagination-range">Showing 0–0 of 0 matching runs</strong>
              <span class="row-count"> · loaded {_safe(loaded_runs_count)} run(s)</span>
            </div>
            <div class="pagination-actions">
              <label for="page-size-select">Page size</label>
              <select id="page-size-select" class="page-size-select">
                <option value="25">25</option>
                <option value="50" selected>50</option>
                <option value="100">100</option>
                <option value="all">All</option>
              </select>
              <button class="page-button" type="button" id="page-first">First</button>
              <button class="page-button" type="button" id="page-prev">Previous</button>
              <span id="page-label">Page 1 of 1</span>
              <button class="page-button" type="button" id="page-next">Next</button>
              <button class="page-button" type="button" id="page-last">Last</button>
            </div>
          </div>
        </div>
      </details>

      {_token_intelligence_section(token_report)}

      {first_run_guidance}

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
          <h2>Dashboard Metadata</h2>
          <span class="chip">schema: <strong>{_safe(schema_label)}</strong></span>
        </div>
        <div class="metadata-grid">
          <div class="metadata-item"><span>generated_at</span><strong>{_safe(generated_at)}</strong></div>
          <div class="metadata-item"><span>database</span><strong>{_safe(db_path)}</strong></div>
          <div class="metadata-item"><span>active_filters</span><strong>{_safe(active_filters)}</strong></div>
          <div class="metadata-item"><span>limit</span><strong>{_safe(limit)}</strong></div>
          <div class="metadata-item"><span>loaded_runs</span><strong>{_safe(loaded_runs_count)}</strong></div>
          <div class="metadata-item"><span>loaded_failures</span><strong>{_safe(loaded_failures_count)}</strong></div>
          <div class="metadata-item"><span>matching_runs</span><strong id="metadata-visible-run-count">{_safe(loaded_runs_count)}</strong></div>
          <div class="metadata-item"><span>success_rate</span><strong>{_safe(success_rate)}</strong></div>
        </div>
      </section>

      <div id="run-detail-templates" hidden>
        {_modal_run_detail_templates(store, runs)}
        {_modal_token_detail_templates(store, runs)}
      </div>

      <div class="modal-backdrop" id="run-detail-modal" aria-hidden="true">
        <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="run-detail-modal-title">
          <div class="modal-head">
            <div>
              <h2 class="modal-title" id="run-detail-modal-title">Run Details</h2>
              <div class="modal-subtitle" id="run-detail-modal-subtitle"></div>
            </div>
            <button class="modal-close" id="run-detail-modal-close" type="button">Close</button>
          </div>
          <div class="modal-body">
            <div class="modal-actions">
              <button class="copy-button" type="button" data-copy-action="run_id">Copy Run ID</button>
              <button class="copy-button" type="button" data-copy-action="run_info">Copy run-info command</button>
              <button class="copy-button" type="button" data-copy-action="trace">Copy trace command</button>
              <button class="copy-button" type="button" data-copy-action="export">Copy export command</button>
              <span class="copy-status" id="copy-status" aria-live="polite"></span>
            </div>
            <div id="run-detail-modal-body"></div>
          </div>
        </div>
      </div>

    </main>

    <footer>
      <strong>Orchgentic Observability Dashboard</strong>
      <span>schema: <code>orchgentic.observability.v1</code></span>
      <span>dashboard_template: <code>orchgentic.observability.dashboard.v1</code></span>
      <span>generated_at: <code>{_safe(generated_at)}</code></span>
      <span>Use <code>orch doctor observability</code>, <code>orch run-info &lt;run_id&gt;</code>, and <code>orch trace &lt;run_id&gt;</code> for inspection.</span>
    </footer>
  </div>

  {_modal_script(store, runs)}

</body>
</html>
"""


def write_dashboard_html(html: str, output: str | Path = DEFAULT_DASHBOARD_PATH) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
