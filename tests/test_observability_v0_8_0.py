from orchgentic.observability import ObservabilityStore, TraceCollector
from orchgentic.observability.models import TOKEN_SOURCE_ESTIMATED, TOKEN_SOURCE_NOT_APPLICABLE
from orchgentic.observability.formatters import format_run_detail, format_run_list


def test_observability_store_persists_run_and_events(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)

    run = tracer.start_run(
        run_type="agent",
        task="what is the local time?",
        agent_id="bob",
        agent_name="Bob",
        provider="groq",
        model="llama-3.3-70b-versatile",
    )
    tracer.event(
        "reasoning.completed",
        component="reasoning",
        name="local_reasoner",
        estimated_tokens_saved=343,
        token_source="estimated",
        data={"confidence": 0.98},
    )
    tracer.event("tool.started", component="tool", name="datetime.local", status="started")
    tracer.event("tool.completed", component="tool", name="datetime.local", status="completed")
    tracer.complete_run()

    loaded = store.get_run(run.run_id)
    assert loaded is not None
    assert loaded.status == "completed"
    assert loaded.agent_name == "Bob"
    assert loaded.estimated_tokens_saved == 343
    assert loaded.token_source == TOKEN_SOURCE_ESTIMATED

    events = store.list_events(run.run_id)
    assert [event.event_type for event in events] == [
        "run.started",
        "reasoning.completed",
        "tool.started",
        "tool.completed",
        "run.completed",
    ]


def test_observability_tracks_agent_and_team_event_levels(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="team", task="write a summary", team_name="ContentTeam")

    tracer.event("team.started", component="team", name="ContentTeam", status="started")
    tracer.event("team.member.started", component="team", name="Writer", status="started")
    tracer.event("agent.started", component="agent", name="Writer", status="started")
    tracer.event("agent.completed", component="agent", name="Writer", status="completed")
    tracer.event("team.member.completed", component="team", name="Writer", status="completed")
    tracer.event("team.synthesis.started", component="team", name="Manager", status="started")
    tracer.event("team.synthesis.completed", component="team", name="Manager", status="completed")
    tracer.event("team.completed", component="team", name="ContentTeam", status="completed")
    tracer.complete_run()

    event_types = [event.event_type for event in store.list_events(run.run_id)]
    assert "team.member.started" in event_types
    assert "agent.started" in event_types
    assert "team.synthesis.completed" in event_types


def test_observability_token_fields_do_not_include_usd_cost(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="agent", task="write a summary", agent_id="bob")
    tracer.event(
        "llm.completed",
        component="provider",
        name="groq",
        input_tokens=100,
        output_tokens=25,
        token_source="estimated",
    )
    tracer.complete_run()

    loaded = store.get_run(run.run_id)
    event = store.list_events(run.run_id)[1]
    assert loaded.total_tokens == 125
    assert event.total_tokens == 125
    assert "cost" not in loaded.to_dict()
    assert "cost" not in event.to_dict()


def test_observability_formatters_show_runs_and_trace(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="agent", task="hello", agent_id="bob", agent_name="Bob")
    tracer.event("agent.started", component="agent", name="Bob", status="started")
    tracer.complete_run()

    runs_text = format_run_list(store.list_runs())
    detail_text = format_run_detail(store.get_run(run.run_id), store.list_events(run.run_id))
    assert "RUNS" in runs_text
    assert "Bob" in runs_text
    assert "TRACE EVENTS" in detail_text
    assert "agent.started" in detail_text


def test_observability_run_filters_agent_team_and_type(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    tracer.start_run(run_type="agent", task="hello", agent_id="bob", agent_name="Bob")
    tracer.complete_run()

    tracer = TraceCollector(store=store)
    tracer.start_run(run_type="team", task="summary", team_id="contentteam", team_name="ContentTeam")
    tracer.complete_run()

    assert len(store.list_runs(agent="Bob")) == 1
    assert store.list_runs(agent="Bob")[0].agent_name == "Bob"
    assert len(store.list_runs(team="ContentTeam")) == 1
    assert store.list_runs(team="ContentTeam")[0].team_name == "ContentTeam"
    assert len(store.list_runs(run_type="team")) == 1


def test_observability_event_filters_component_type_and_tokens(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="agent", task="hello", agent_id="bob")
    tracer.event("routing.completed", component="routing", name="single_tool", estimated_tokens_saved=100, token_source="estimated")
    tracer.event("tool.started", component="tool", name="datetime.local", status="started")
    tracer.event("tool.completed", component="tool", name="datetime.local")
    tracer.event("llm.completed", component="provider", name="groq", input_tokens=10, output_tokens=5, token_source="estimated")
    tracer.complete_run()

    assert [event.component for event in store.list_events(run.run_id, component="tool")] == ["tool", "tool"]
    assert [event.event_type for event in store.list_events(run.run_id, event_type="llm.completed")] == ["llm.completed"]
    token_events = store.list_events(run.run_id, tokens_only=True)
    assert [event.event_type for event in token_events] == ["routing.completed", "llm.completed"]


def test_observability_records_policy_checked_event_shape(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="tool", task="gmail.send", agent_id="bob", agent_name="Bob")
    tracer.event(
        "policy.checked",
        component="policy",
        name="hold_for_confirmation",
        status="hold_for_confirmation",
        message="Tool 'gmail.send' requires explicit confirmation.",
        data={"action": "hold_for_confirmation", "affected_tools": ["gmail.send"]},
    )
    tracer.complete_run(status="hold_for_confirmation")

    events = store.list_events(run.run_id, component="policy")
    assert len(events) == 1
    assert events[0].event_type == "policy.checked"
    assert events[0].status == "hold_for_confirmation"


def test_observability_records_failure_event_shapes(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="team", task="team failure", team_name="ContentTeam")
    tracer.event("team.started", component="team", name="ContentTeam", status="started")
    tracer.event("team.member.started", component="team", name="Researcher", status="started")
    tracer.event("agent.failed", component="agent", name="Researcher", status="failed", message="provider unavailable")
    tracer.event("team.member.failed", component="team", name="Researcher", status="failed", message="provider unavailable")
    tracer.event("team.failed", component="team", name="ContentTeam", status="failed", message="provider unavailable")
    tracer.fail_run(RuntimeError("provider unavailable"))

    loaded = store.get_run(run.run_id)
    event_types = [event.event_type for event in store.list_events(run.run_id)]
    assert loaded.status == "failed"
    assert "agent.failed" in event_types
    assert "team.member.failed" in event_types
    assert "team.failed" in event_types


def test_direct_tool_policy_preview_blocks_disabled_tool():
    from orchgentic.observability.policy_preview import preview_tool_policy_decision

    class Cfg:
        tool_policies = {"gmail.delete": {"enabled": False, "require_confirmation": True}}

    decision = preview_tool_policy_decision("gmail.delete", {"message_id": "abc"}, Cfg())
    assert decision["action"] == "block"
    assert decision["allowed"] is False
    assert decision["external_llm_allowed"] is False


def test_direct_tool_policy_preview_holds_confirmation():
    from orchgentic.observability.policy_preview import preview_tool_policy_decision

    class Cfg:
        tool_policies = {"gmail.send": {"enabled": True, "require_confirmation": True, "send_policy": {"mode": "restricted", "allowed_addresses": ["studio@example.com"], "allowed_domains": [], "require_confirmation": True}}}

    decision = preview_tool_policy_decision("gmail.send", {"to": "studio@example.com"}, Cfg())
    assert decision["action"] == "hold_for_confirmation"
    assert decision["require_confirmation"] is True

    confirmed = preview_tool_policy_decision("gmail.send", {"to": "studio@example.com", "confirm": True}, Cfg())
    assert confirmed["action"] == "allow"


def test_direct_tool_runs_can_record_estimated_token_savings(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="tool", task="gmail.send", agent_id="bob", agent_name="Bob")
    tracer.event(
        "routing.bypassed",
        component="routing",
        name="direct_tool",
        status="completed",
        message="Direct tool execution bypassed LLM routing.",
        estimated_tokens_saved=321,
        token_source="estimated",
        data={"savings_reason": "direct_tool_execution_bypassed_llm_routing"},
    )
    tracer.event("policy.checked", component="policy", name="allow", status="allow")
    tracer.event("tool.started", component="tool", name="gmail.send", status="started")
    tracer.event("tool.completed", component="tool", name="gmail.send", status="completed")
    tracer.complete_run()

    loaded = store.get_run(run.run_id)
    events = store.list_events(run.run_id)
    assert loaded.estimated_tokens_saved == 321
    assert loaded.token_source == TOKEN_SOURCE_ESTIMATED
    assert [event.event_type for event in events][1] == "routing.bypassed"
    assert events[1].estimated_tokens_saved == 321
    assert events[1].data["savings_reason"] == "direct_tool_execution_bypassed_llm_routing"



def test_observability_export_run_detail_has_stable_schema(tmp_path):
    import json
    from orchgentic.observability.exporters import SCHEMA_VERSION, export_run_detail

    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(run_type="agent", task="hello", agent_id="bob", agent_name="Bob")
    tracer.event("agent.started", component="agent", name="Bob", status="started")
    tracer.event("agent.completed", component="agent", name="Bob", status="completed")
    tracer.complete_run()

    payload = json.loads(export_run_detail(store, run.run_id))
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["export_type"] == "run_detail"
    assert payload["run"]["run_id"] == run.run_id
    assert [event["event_type"] for event in payload["events"]] == [
        "run.started",
        "agent.started",
        "agent.completed",
        "run.completed",
    ]
    assert "estimated_cost_usd" not in payload["run"]


def test_observability_export_runs_jsonl_filters_history(tmp_path):
    import json
    from orchgentic.observability.exporters import SCHEMA_VERSION, export_runs_jsonl

    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    tracer.start_run(run_type="agent", task="hello", agent_id="bob", agent_name="Bob")
    tracer.complete_run()

    tracer = TraceCollector(store=store)
    tracer.start_run(run_type="team", task="summary", team_id="contentteam", team_name="ContentTeam")
    tracer.complete_run()

    lines = [line for line in export_runs_jsonl(store, run_type="team").splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["export_type"] == "run_summary"
    assert payload["run"]["run_type"] == "team"
    assert payload["run"]["team_name"] == "ContentTeam"


def test_observability_export_writer_creates_parent_directories(tmp_path):
    from orchgentic.observability.exporters import write_export_text

    output = tmp_path / "exports" / "run.json"
    write_export_text("{}", output)
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "{}"


def test_observability_store_stats_and_delete_run(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)

    run = tracer.start_run(run_type="tool", task="datetime.local {}", agent_id="bob", agent_name="Bob")
    tracer.event("routing.bypassed", component="routing", name="direct_tool", estimated_tokens_saved=349, token_source="estimated")
    tracer.complete_run()

    stats = store.get_stats()
    assert stats["total_runs"] == 1
    assert stats["estimated_tokens_saved"] == 349
    assert stats["by_type"]["tool"] == 1
    assert stats["by_status"]["completed"] == 1

    assert store.delete_run(run.run_id) is True
    assert store.get_run(run.run_id) is None
    assert store.list_events(run.run_id) == []


def test_observability_store_prune_runs_dry_run_and_confirm(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)

    run1 = tracer.start_run(run_type="tool", task="old failed tool", agent_id="bob")
    run1.started_at = "2020-01-01T00:00:00+00:00"
    run1.status = "failed"
    store.update_run(run1)
    tracer.complete_run(status="failed", message="failed")

    tracer2 = TraceCollector(store=store)
    run2 = tracer2.start_run(run_type="agent", task="recent agent", agent_id="bob")
    tracer2.complete_run()

    dry = store.prune_runs(status="failed", older_than_iso="2021-01-01T00:00:00+00:00", dry_run=True)
    assert dry["matched"] == 1
    assert dry["deleted"] == 0
    assert store.get_run(run1.run_id) is not None

    confirmed = store.prune_runs(status="failed", older_than_iso="2021-01-01T00:00:00+00:00", dry_run=False)
    assert confirmed["matched"] == 1
    assert confirmed["deleted"] == 1
    assert store.get_run(run1.run_id) is None
    assert store.get_run(run2.run_id) is not None


def test_observability_store_lists_failures_and_failure_stats(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)

    run = tracer.start_run(run_type="tool", task="gmail.send", agent_id="bob", agent_name="Bob")
    tracer.event("tool.failed", component="tool", name="gmail.send", status="failed", message="Missing confirmation")
    tracer.run.error_type = "ToolExecutionError"
    tracer.run.error_message = "gmail.send failed: Missing confirmation"
    tracer.complete_run(status="failed", message="gmail.send failed")

    failures = store.list_failures()
    assert len(failures) == 1
    assert failures[0].run_id == run.run_id

    stats = store.get_failure_stats()
    assert stats["total_failures"] == 1
    assert stats["by_error_type"]["ToolExecutionError"] == 1
    assert stats["by_type"]["tool"] == 1


def test_observability_dashboard_html_export(tmp_path):
    from orchgentic.observability.dashboard import build_dashboard_html, write_dashboard_html

    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    tracer.start_run(run_type="tool", task="datetime.local {}", agent_id="bob", agent_name="Bob")
    tracer.event("routing.bypassed", component="routing", name="direct_tool", estimated_tokens_saved=349, token_source="estimated")
    tracer.complete_run()

    html = build_dashboard_html(store, limit=10)
    assert "Orchgentic Observability" in html
    assert "RUN DASHBOARD" in html
    assert "datetime.local" in html
    assert "saved≈349" in html
    assert "Run Details:" in html
    assert "data-run-target=" in html
    assert "data-run-target=" in html
    assert "run-detail-modal" in html
    assert "function openRunModal" in html
    assert "var runDetails = [" in html or "var runDetails = []" in html
    assert "Close" in html
    assert "a { color: inherit; }" in html
    assert ".run-link" in html

    output = write_dashboard_html(html, tmp_path / "dashboard.html")
    assert output.exists()
    assert "orchgentic.observability.dashboard.v1" in output.read_text(encoding="utf-8")
