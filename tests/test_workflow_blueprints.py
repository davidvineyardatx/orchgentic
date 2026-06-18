from orchgentic.observability import ObservabilityStore, TraceCollector
from orchgentic.observability.formatters import format_run_summary, format_event_list
from orchgentic.workflows.registry import WorkflowRegistry


def test_workflow_registry_loads_content_intelligence_blueprint(tmp_path):
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    workflow_file = workflows_dir / "content_intelligence_summary.workflow.yaml"
    workflow_file.write_text(
        """
workflow:
  id: content_intelligence_summary
  name: Content Intelligence Summary
  version: 0.1.0
  team:
    name: ContentTeam
  steps:
    - id: deterministic_team_plan
      name: Deterministic team plan
      actor: Manager
      execution_tier: deterministic
      action: assign_roles_from_team_config
""".strip(),
        encoding="utf-8",
    )

    workflow = WorkflowRegistry(workflows_dir).get_workflow("content_intelligence_summary")

    assert workflow is not None
    assert workflow.id == "content_intelligence_summary"
    assert workflow.team_name == "ContentTeam"
    assert workflow.steps[0].id == "deterministic_team_plan"
    assert workflow.metadata()["workflow_id"] == "content_intelligence_summary"


def test_workflow_metadata_is_visible_in_run_summary_and_trace(tmp_path):
    store = ObservabilityStore(tmp_path / "observability.db")
    tracer = TraceCollector(store=store)
    run = tracer.start_run(
        run_type="workflow",
        task="Research Cedar Creek water table.",
        team_name="ContentTeam",
        metadata={
            "workflow_id": "content_intelligence_summary",
            "workflow_name": "Content Intelligence Summary",
            "workflow_version": "0.1.0",
        },
    )
    tracer.event(
        "workflow.step.planned",
        component="workflow",
        name="deterministic_team_plan",
        status="planned",
        message="Deterministic team plan",
        data={"workflow_step": "deterministic_team_plan", "execution_tier": "deterministic"},
    )
    tracer.complete_run()

    loaded = store.get_run(run.run_id)
    events = store.list_events(run.run_id)
    summary = format_run_summary(loaded)
    event_text = format_event_list(events)

    assert "type: workflow" in summary
    assert "workflow: content_intelligence_summary" in summary
    assert "workflow.step.planned" in event_text
    assert "deterministic_team_plan" in event_text
