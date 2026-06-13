# Orchgentic Roadmap

Orchgentic is an open-source agent orchestration framework for building, routing, coordinating, and observing AI agents across tools, memory, knowledge, workflows, events, policies, and teams.

This roadmap reflects the current direction of Orchgentic after the v0.7.12 release series, which added local reasoning, confidence scoring, workflow-aware routing, policy-aware escalation, and improved team synthesis.

---

## Where Orchgentic Is Today

Orchgentic has moved beyond a basic agent runner. It now provides the foundation for governed, inspectable, multi-agent orchestration.

The current platform can:

* Run configurable agents from YAML
* Use pluggable LLM providers
* Route simple tasks directly to tools
* Avoid unnecessary LLM calls with local reasoning
* Score confidence before escalation
* Use memory and knowledge when relevant
* Execute tools through a registry
* Enforce tool policies before execution
* Require confirmation for sensitive actions
* Block disabled tools before LLM escalation
* Coordinate teams of specialized agents
* Compress team handoffs to reduce token usage
* Synthesize final team responses
* Provide debug output for routing, tools, plans, reflection, and policy decisions

The v0.7.x release line established Orchgentic’s core orchestration foundation.

---

## Completed in v0.7.x

### Multi-Agent Orchestration

Orchgentic now supports team-based workflows where multiple agents contribute to a shared task.

Examples include:

* Manager
* Researcher
* Writer
* Reviewer
* Final synthesis

This enables coordinated work across multiple specialized agents instead of relying on a single general-purpose agent for every task.

### Local Reasoning

Orchgentic now includes a local reasoning layer that can inspect a task before calling an external LLM.

Local reasoning can determine whether a task should:

* Be answered locally
* Use a deterministic tool route
* Run through a workflow
* Escalate to the configured LLM provider
* Stop because of policy restrictions

Example:

```text
"What is the local time?"
→ routed directly to datetime.local
→ external_llm_used: false
```

### Confidence Scoring and Escalation

The reasoning layer now scores confidence before deciding whether to escalate.

This allows Orchgentic to avoid unnecessary LLM calls for simple tasks while still using the configured provider for generation, analysis, or complex reasoning.

Design rule:

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether the provider should be used
```

### Workflow-Aware Routing

Orchgentic can now judge whether a task is likely:

* Single-step
* Multi-step
* Tool-driven
* Workflow-driven
* Team-oriented
* LLM-required

This provides a stronger foundation for future workflow execution and planning.

### Event-Aware Routing

The routing layer now understands execution context, including:

* Manual interactive runs
* Heartbeat-triggered runs
* Webhook-triggered runs
* Autonomous execution contexts

This allows stricter checks when tasks run autonomously.

### Policy-Aware Escalation

Policies are now evaluated before tool execution or external LLM escalation.

This supports safer handling of sensitive actions such as email sending, replying, and deletion.

Examples:

```text
delete gmail message id abcdef123456
→ gmail.delete detected
→ blocked because gmail.delete is disabled
→ external_llm_allowed: false
```

```text
send an email to studio@example.com saying hello
→ gmail.send detected
→ held for confirmation
→ external_llm_allowed: false until confirmed
```

### Team Synthesis Improvements

Team outputs are now cleaner and more efficient.

Improvements include:

* Current-run-only context
* Reduced memory contamination
* Compressed team handoffs
* Structured output unwrapping
* Placeholder resource suppression
* Cleaner final synthesis
* Lower token usage during team workflows

---

## Current Documentation Priority

The immediate priority is making Orchgentic easy to install, configure, run, and understand.

Documentation should focus on step-by-step usage.

Planned documentation includes:

* Main README
* Quickstart guide
* CLI command reference
* Agent YAML configuration guide
* Team YAML configuration guide
* Tools and policy guide
* Routing and reasoning guide
* Examples guide
* Known limitations
* Release notes

The documentation should make it easy for a new user to understand:

* What Orchgentic is
* What problem it solves
* How to configure an agent
* How to run an agent
* How to inspect a route
* How tool policies work
* How confirmation works
* How teams work
* How local reasoning saves cost and latency

---

## Next Engineering Milestone: v0.8.0 Observability

The next major engineering focus should be observability.

As Orchgentic becomes more capable, users need to see what happened inside each run.

Planned v0.8.0 work:

* Run history
* Routing traces
* Tool call traces
* Policy decision logs
* Team handoff traces
* Escalation logs
* Token estimate tracking
* Local reasoning savings estimates
* Error classification visibility
* Dashboard-ready event records

Users should be able to answer:

* Which agent handled the task?
* Which route was selected?
* Was an external LLM used?
* Which tools were called?
* Was anything blocked by policy?
* Was confirmation required?
* What did each team member contribute?
* How much context was passed?
* How many tokens were likely saved?

This is a natural next step because Orchgentic’s value is not only executing agents, but making agent execution inspectable and governable.

---

## Future Milestone: Local LLM Provider Support

True local LLM support is planned, but it is intentionally separate from local reasoning.

Important distinction:

```text
Local reasoning decides whether an LLM is needed.
A local LLM provider generates the response when an LLM is needed.
```

Future local provider support may include:

* LM Studio
* Ollama
* llama.cpp-compatible endpoints
* Other OpenAI-compatible local endpoints

Planned capabilities:

* Local model provider configuration
* Provider health checks
* Model availability checks
* Better local provider errors
* Local-first generation options
* Fallback behavior through normal provider configuration

---

## Future Milestone: Dashboard and UI

Once observability data is available, Orchgentic can support a dashboard or UI layer.

Dashboard goals:

* View agent runs
* View team runs
* Inspect routing decisions
* Inspect local reasoning decisions
* Inspect tool calls
* Inspect policy decisions
* Review memory and knowledge usage
* Review errors and warnings
* Track estimated token savings
* Manage agent and team configurations

---

## Future Milestone: No-Code / Low-Code Builder

A long-term goal is to make Orchgentic usable by non-developers through a no-code or low-code interface.

Builder goals:

* Create agents visually
* Configure providers
* Configure tools
* Configure memory and knowledge
* Configure policies
* Build teams
* Build workflows
* Configure triggers
* Test routes before execution
* Review run history and outputs

This would allow users to build agentic workflows without directly editing YAML.

---

## Future Milestone: Plugin and Connector Ecosystem

Orchgentic should eventually support a broader plugin model for tools and connectors.

Potential plugin categories:

* Email
* Calendar
* CRM
* Files
* Databases
* Web search
* Internal APIs
* Project management
* Messaging
* E-commerce
* Analytics

Plugin goals:

* Standard plugin interface
* Tool manifest format
* Connector registration
* Safer permission boundaries
* Community-contributed tools
* Optional marketplace-style discovery

---

## Future Milestone: Production Hardening

Before a stable 1.0 release, Orchgentic will need additional production-focused work.

Production goals:

* Stronger error handling
* Retry policies
* Rate-limit handling
* Secrets management guidance
* Provider failure handling
* Test coverage expansion
* Security review
* Policy enforcement review
* Documentation completeness
* Packaging and install polish

---

## Version Direction

```text
v0.7.x
→ orchestration foundation, local reasoning, routing, policy, teams

v0.8.x
→ observability, run history, dashboard-ready logs

v0.9.x
→ local provider support, dashboard groundwork, production hardening

v1.0
→ stable open-source agent orchestration framework
```

---

## Core Product Principle

Orchgentic is not just an agent runner.

It is the orchestration layer that decides:

* What should handle the task
* Whether tools are needed
* Whether memory or knowledge should be used
* Whether the task can stay local
* Whether an LLM should be called
* Whether policy allows execution
* Whether human confirmation is required
* Whether a team should collaborate
* How the final answer should be synthesized
* How the run should be inspected afterward

The long-term goal is to help developers build agentic systems that are safer, more efficient, easier to debug, and easier to trust.
