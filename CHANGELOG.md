# Changelog

All notable changes to Orchgentic are documented here.

## v1.1.2 — Quickstart CLI Compatibility

- Added optional prompt arguments to `orch run` and `orch run-team` so quoted quickstart tasks execute without interactive prompting.
- Restored the documented `orch create-agent` command for clone-first developer onboarding.
- Added `orch workflow doctor` for direct workflow YAML file diagnostics and workflow id diagnostics.
- Added flat workflow example validation for `examples/workflows/*.yaml` while preserving existing team-backed workflow contract validation.
- Updated `docs/CLI_COMMANDS.md` to reflect the current CLI surface.
- Added regression coverage for quickstart CLI compatibility and workflow doctor examples.

### Developer dependency documentation

- Clarified that test execution requires the `dev` extra: `python -m pip install -e ".[dev]"`.
- Updated Quickstart and clean-install docs so new developers do not hit `No module named pytest` after a runtime-only install.

## v1.0.0 — Stable Developer Release

- Promoted Orchgentic to a stable developer release.
- Finalized the core positioning as a local-first, token-aware AI operations layer.
- Stabilized the `orch` CLI for agents, teams, tools, workflows, policy inspection, observability, and doctor checks.
- Stabilized YAML-first configuration for agents, teams, tools, providers, execution tiers, memory, knowledge, and policy.
- Stabilized multi-agent orchestration and team-backed execution.
- Stabilized deterministic routing, local reasoning, policy-aware escalation, and token-savings telemetry.
- Stabilized observability traces, dashboard-ready exports, retention cleanup, and failure diagnostics.
- Stabilized registry-first tool contracts so registered tools can be normalized and validated automatically.
- Stabilized workflow contracts, workflow validation, and workflow documentation for team-backed workflows.
- Stabilized documentation, examples, release notes, clean install guidance, and v1.0 onboarding.

## v0.9.0-rc.1 — Release Candidate

- Completed release-candidate documentation and examples.
- Cleaned the repository for clone-first developer onboarding.
- Verified required docs, release notes, and validation files.
- Finalized v1.0 release checklist.
- Confirmed clean install flow from clone to first agent/team run.
- Confirmed test coverage for core runtime, routing, tools, policy, workflows, observability, and provider setup.

## v0.9.0-beta.2 — RAG, Memory, and Provider Stabilization

- Stabilized memory and knowledge search behavior.
- Stabilized local semantic knowledge store behavior.
- Improved provider onboarding and provider validation.
- Clarified provider responsibilities: providers answer only when an LLM is needed.
- Preserved the separation between routing/policy decisions and provider execution.
- Improved provider docs for OpenAI-compatible, Groq, LM Studio, and local-ready setups.

## v0.9.0-beta.1 — Workflow Stabilization

- Added workflow contract validation.
- Added workflow doctor checks.
- Stabilized workflow inspect, validate, and run behavior.
- Stabilized workflow trace metadata.
- Enforced the product boundary that workflows are for coordinated, multi-step, team-backed execution.
- Improved workflow error messages and validation output.
- Added clean workflow examples and workflow documentation.

## v0.8.0-beta.6 — Registry-First Tool Contract Stabilization

- Added registry-first tool contract validation.
- Made the tool registry the source of truth for tool contracts.
- Added automatic contract normalization from registered tool definitions.
- Added optional tool-class metadata for category, side effects, destructive behavior, confirmation support, and policy checks.
- Added built-in tool contract inventory as a regression snapshot.
- Added confirmation contract metadata.
- Added runtime confirmation consistency checks.
- Added future plugin tool contract shape validation.
- Added `orch doctor tool-contracts`.
- Added JSON output for tool contract doctor checks.
- Preserved the boundary that no plugin loader, dynamic discovery, external package loading, marketplace, or plugin execution is included in beta.6.

## v0.8.0-beta.5 — Execution Tier Readiness

- Added execution-tier configuration normalization.
- Added `execution_tiers` support as an alias over execution policy.
- Added deterministic, local reasoning, local LLM, external LLM, and premium model execution tier metadata.
- Added local LLM readiness fields without enabling local LLM execution.
- Added execution-tier validation.
- Added execution-tier doctor checks.
- Added `orch doctor execution-tiers`.
- Added execution-tier examples and default configurations.
- Preserved the boundary that beta.5 does not change routing behavior or execute local LLMs.

## v0.8.0-beta.4 — Decision Policy Stabilization

- Added execution policy foundation for agents and teams.
- Added deterministic policy classification.
- Added policy-aware routing decisions.
- Added safe advisory policy enforcement.
- Added safe enforcement trace coverage.
- Added clearer policy enforcement output.
- Added policy report route summaries.
- Added `orch policy-report`.
- Added `orch judge-route --summary`.
- Improved deterministic policy output formatting.
- Stabilized policy trace metadata for allow, block, and confirmation-held decisions.

## v0.8.0-beta.3 — Token Intelligence and Local Reasoning Proof

- Added token intelligence reporting.
- Added deterministic token-savings proof for direct tool execution and local reasoning paths.
- Added token-count source metadata.
- Added token-savings explanations and reason fields.
- Added dashboard-ready token intelligence output.
- Added token report filtering improvements.
- Added workflow execution proof for token-aware workflows.
- Improved local LLM eligibility classification metadata without enabling local LLM execution.
- Clarified that token savings are operational estimates, not billing claims.

## v0.8.0-beta.2 — Clean Install and Developer Polish

- Improved clean install flow for new developers.
- Added clean test-data cleanup command support.
- Improved trace formatting.
- Improved README and roadmap positioning.
- Improved first-run onboarding docs.
- Reduced sample/test clutter for cloned repositories.
- Improved release notes and release description polish.

## v0.8.0-beta.1 — Observability Stabilization

- Added observability foundation.
- Added trace inspection CLI support.
- Added trace coverage hardening.
- Added dashboard-ready export format.
- Added static dashboard preview.
- Added observability retention cleanup.
- Added failure diagnostics.
- Added observability doctor checks.
- Added dashboard filtering, pagination, empty states, and token intelligence sections.
- Improved dashboard run details, modal behavior, and filtered token intelligence views.

## v0.7.12-alpha

- Added workflow-aware routing classification.
- Added event-aware routing context for manual, heartbeat, webhook, and scheduled runs.
- Added policy-aware escalation gates that block disabled tools and hold confirmation-required tools before LLM calls.
- Expanded `ORCHESTRATION_JUDGMENT` output with workflow, event, policy, and final decision sections.
- Preserved the single-provider configuration rule. No fallback provider is defined under routing or escalation.
- Improved team synthesis quality and handoff compression.
- Improved structured team output.
- Added intent precedence fixes for routing and policy decisions.

## v0.7.11-alpha

- Added advisory local reasoner layer.
- Added local confidence scoring.
- Added escalation decision engine.
- Added orchestration judgment debug output.
- Added `orch judge-route`.
- Added Gmail toolset integration for search, read, draft, send, reply, and delete.
- Added telemetry improvements for local reasoning and escalation metadata.
- Improved local-time routing behavior.
- Added 12-hour local time formatting support.

## v0.7.10.1-alpha

- Added dynamic token-savings estimation.
- Added execution timing for route telemetry.
- Added route metrics aggregation.
- Added `orch route-metrics`.

## v0.7.10-alpha

- Added editable router policy config and fallback terms for LLM-required requests.
- Added deterministic argument extraction.
- Added deterministic multi-tool chaining for Gmail subject-line retrieval.
- Added deterministic formatting layer.
- Added route telemetry logging.
- Added estimated token savings metadata.

## v0.7.9-alpha

- Added deterministic router.
- Added no-LLM routing for date/time.
- Added no-LLM routing for Gmail search/read.
- Added exact-field no-LLM routing for Gmail draft/send.
- Added route telemetry helper.

## v0.7.8-alpha

- Added `gmail.send`.
- Added `gmail.reply`.
- Added `gmail.delete`.
- Added runtime confirmation enforcement.
- Added Gmail recipient policy enforcement.
- Added Gmail send/modify OAuth scopes.
- Gmail delete moves messages to Trash only.

## v0.7.7-alpha

- Added named Gmail connections.
- Added Gmail connector CLI commands.
- Added `gmail.search`, `gmail.read`, and `gmail.draft`.
- Added tool policy governance foundation.

## v0.7.6-alpha

- Added `orch create agent`.
- Added `orch create team`.
- Added `orch create trigger`.

## v0.7.5-alpha — Developer Preview

Initial public developer preview release.

Includes:

- Branded Orchgentic package and `orch` CLI.
- Multi-agent orchestration.
- Team execution.
- Delegation.
- Tool runtime.
- Tool parser continuation fixes.
- Capability preflight.
- Memory and semantic knowledge.
- Triggers and webhooks.
- Groq and OpenAI provider support.
- Time context resolver.
- `datetime.local`.
- `tzdata` dependency for Windows timezone support.
