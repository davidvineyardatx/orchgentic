from orchgentic.orchestration.synthesis_guardrails import (
    build_member_task,
    build_synthesis_task,
    sanitize_final_answer,
)


def test_synthesis_prompt_prefers_current_team_outputs_and_blocks_placeholders():
    prompt = build_synthesis_task("Research AI shopping", "Researcher -> team: findings")

    assert "Use the current team outputs" in prompt
    assert "Do not rely on unrelated prior memory" in prompt
    assert "Do not invent citations" in prompt
    assert "Do not include placeholder links" in prompt


def test_researcher_prompt_requires_actual_research_not_status():
    prompt = build_member_task("Research AI shopping", "Manager -> team: assignments", "Researcher")

    assert "Provide actual findings" in prompt
    assert "Do not merely say that research has been completed" in prompt


def test_sanitize_final_answer_removes_placeholder_resources_section():
    answer = """### Final Team Response
Useful final content.

#### Additional Resources
* **AI in Retail Report**: A comprehensive report on AI in retail.
* [link to article or resource]
"""

    result = sanitize_final_answer(answer)

    assert "Useful final content" in result.answer
    assert "Additional Resources" not in result.answer
    assert "AI in Retail Report" not in result.answer
    assert "[link to article" not in result.answer
    assert result.removed_placeholder_sections is True
    assert result.removed_placeholder_lines >= 1


def test_sanitize_final_answer_preserves_real_resource_url_section():
    answer = """### Final Team Response
Useful final content.

#### Additional Resources
* Research report: https://example.com/report
"""

    result = sanitize_final_answer(answer)

    assert "Additional Resources" in result.answer
    assert "https://example.com/report" in result.answer
    assert result.removed_placeholder_sections is False


def test_sanitize_final_answer_removes_inline_placeholder_link():
    answer = "Read more here: [link to article or resource]\nKeep this line."

    result = sanitize_final_answer(answer)

    assert "[link to article" not in result.answer
    assert "Keep this line" in result.answer

from orchgentic.orchestration.synthesis_guardrails import (
    extract_answer_for_handoff,
    format_team_outputs_for_prompt,
)


def test_extract_answer_for_handoff_strips_debug_transcript():
    debug_output = """RUN ID
abc

PLAN
Goal: do work

ANSWER
Only this answer should be forwarded.
Second line.

REFLECTION
success=True"""

    assert extract_answer_for_handoff(debug_output) == "Only this answer should be forwarded.\nSecond line."


def test_format_team_outputs_for_prompt_uses_compact_answers_only():
    messages = [
        {
            "sender": "Researcher",
            "recipient": "team",
            "content": "RUN ID\nabc\n\nPLAN\nGoal\n\nANSWER\nFinding one.\n\nREFLECTION\nsuccess=True",
        },
        {
            "sender": "Writer",
            "recipient": "team",
            "content": "Draft summary.",
        },
    ]

    prompt_context = format_team_outputs_for_prompt(messages)

    assert "Researcher -> team: Finding one." in prompt_context
    assert "Writer -> team: Draft summary." in prompt_context
    assert "RUN ID" not in prompt_context
    assert "REFLECTION" not in prompt_context
    assert "PLAN" not in prompt_context


def test_synthesis_prompt_blocks_new_examples_and_distinguishes_source_labels():
    prompt = build_synthesis_task("Research AI shopping", "Researcher -> team: findings")

    assert "company names" in prompt
    assert "source labels, not verified citations" in prompt
    assert "not present in current outputs" in prompt


def test_sanitize_final_answer_removes_internal_synthesis_note():
    answer = """Executive Summary
AI is changing shopping.

Note: While the Writer's draft mentioned visual search, more specific data is not available in the current team outputs.
"""

    result = sanitize_final_answer(answer)

    assert "Executive Summary" in result.answer
    assert "Writer's draft" not in result.answer
    assert "current team outputs" not in result.answer
    assert "internal" not in result.answer.lower()


def test_sanitize_final_answer_softens_unverified_source_phrasing_without_url():
    answer = (
        "Chatbots are expected to be widely adopted, according to a survey by Oracle (Oracle, 2020). "
        "Analytics users outperform peers, as found by a study by McKinsey (McKinsey, 2019). "
        "Supply chain impact is high, as reported by Accenture (Accenture, 2020)."
    )

    result = sanitize_final_answer(answer)

    assert "according to a survey" not in result.answer.lower()
    assert "as found by a study" not in result.answer.lower()
    assert "as reported by" not in result.answer.lower()
    assert "with a source label of Oracle (Oracle, 2020)" in result.answer
    assert "with a source label of McKinsey (McKinsey, 2019)" in result.answer
    assert "with a source label of Accenture (Accenture, 2020)" in result.answer
    assert "softened_unverified_source_phrasing" in (result.notes or [])


def test_sanitize_final_answer_preserves_verified_source_phrasing_with_url():
    answer = "According to a survey by Oracle (Oracle, 2020), adoption is rising. https://example.com/oracle"

    result = sanitize_final_answer(answer)

    assert "According to a survey by Oracle" in result.answer
    assert "https://example.com/oracle" in result.answer


def test_extract_answer_for_handoff_unwraps_structured_final_json():
    output = '{"action":"final","answer":"Executive Summary\\nPlain answer."}'

    assert extract_answer_for_handoff(output) == "Executive Summary\nPlain answer."


def test_extract_answer_for_handoff_unwraps_structured_json_inside_debug_answer():
    debug_output = '''RUN ID
abc

ANSWER
{"action":"final","answer":"Only the plain answer."}

REFLECTION
success=True'''

    assert extract_answer_for_handoff(debug_output) == "Only the plain answer."


def test_sanitize_final_answer_softens_leading_source_claim_without_json_or_splice():
    answer = (
        "A survey by Accenture found that 91% of consumers prefer relevant offers. "
        "Additionally, AI-powered customer service can lead to fewer complaints, as reported by Harvard Business Review. "
        "Augmented reality (AR) and virtual reality (VR) are providing immersive shopping experiences."
    )

    result = sanitize_final_answer(answer)

    assert "A survey by Accenture found" not in result.answer
    assert "as reported by Harvard Business Review" not in result.answer
    assert "source-labeled research cites Accenture" in result.answer
    assert "with a source label of Harvard Business Review" in result.answer
    assert "(AR) and virtual reality (VR)" in result.answer
    assert "team's source-labeled research (AR)" not in result.answer


def test_team_quality_trace_data_uses_notes_without_warnings_attribute():
    from orchgentic.orchestration.team_runner import build_team_quality_trace_data

    quality = sanitize_final_answer("Final answer with [link to article or resource]\nKeep this.")
    data = build_team_quality_trace_data(3, quality)

    assert data["members"] == 3
    assert data["quality_notes"] == quality.notes
    assert data["quality_warnings"] == quality.notes
    assert data["quality"]["removed_placeholder_lines"] >= 1


def test_deterministic_team_plan_assigns_known_roles_without_llm():
    from orchgentic.orchestration.team_runner import build_deterministic_team_plan

    class Team:
        name = "ContentTeam"
        orchestrator = "Manager"
        members = ["Researcher", "Writer", "Reviewer"]

    plan = build_deterministic_team_plan(Team(), "Research data centers")

    assert "Deterministic team plan for ContentTeam" in plan
    assert "Researcher: gather and verify" in plan
    assert "Writer: draft" in plan
    assert "Reviewer: review" in plan
    assert "Synthesis:" in plan


def test_team_member_tool_decision_policy_skips_researcher_writer_and_reviewer():
    from orchgentic.orchestration.team_runner import tool_decision_policy_for_team_member

    researcher = tool_decision_policy_for_team_member("Researcher")
    assert researcher["tool_decision_policy"] == "skip"
    assert researcher["tool_decision_policy_event_name"] == "deterministic_researcher_tool_routing"
    assert researcher["estimated_tool_decision_iterations_saved"] == 3
    assert "deterministic research role contract" in researcher["tool_decision_policy_reason"]

    assert tool_decision_policy_for_team_member("Writer")["tool_decision_policy"] == "skip"
    assert tool_decision_policy_for_team_member("Reviewer")["tool_decision_policy"] == "skip"
