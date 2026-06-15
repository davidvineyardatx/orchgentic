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
