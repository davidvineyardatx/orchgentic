# Known Limitations

Orchgentic is a developer preview release focused on the core orchestration foundation.

The current release includes agent configuration, tool execution, memory, knowledge search, planning, reflection, local reasoning, routing, policy-aware escalation, Gmail tool safety, and multi-agent team orchestration.

The limitations below are known and are expected to improve in future releases.

---

## Developer Preview Status

Orchgentic is not yet a production-stable 1.0 framework.

The current release is intended for:

* Local development
* Framework testing
* Agent orchestration experiments
* CLI-driven workflows
* Early adopter feedback
* Architecture validation

Production deployment should be done carefully, with human review, logging, and additional safeguards.

---

## Observability Is Still Early

v0.7.12 includes useful debug output, but it does not yet include a full observability system.

Current limitations:

* No persistent run history UI
* No dashboard
* No structured run timeline viewer
* No centralized trace browser
* No built-in run replay
* No long-term analytics layer

Planned v0.8.0 focus:

* Run records
* Routing traces
* Tool call traces
* Policy decision logs
* Team handoff traces
* Escalation traces
* Token savings estimates
* Dashboard-ready event records

---

## Local Reasoning Is Not a Local LLM

v0.7.12 includes local reasoning, but that is not the same thing as local LLM generation.

Local reasoning decides whether an LLM is needed.

A local LLM provider generates the response when an LLM is needed.

Current local reasoning can help with:

* Simple intent detection
* Deterministic tool routing
* Confidence scoring
* Escalation decisions
* Policy-aware blocking or confirmation holds

Current local reasoning does not replace a full language model for:

* Complex writing
* Open-ended analysis
* Deep reasoning
* Large summarization tasks
* Creative generation

Local LLM provider support is planned for a future release.

---

## Local LLM Provider Support Is Deferred

Orchgentic currently supports configured external providers such as Groq and OpenAI-style providers.

True local provider support is planned but not complete in v0.7.12.

Future local provider support may include:

* LM Studio
* Ollama
* llama.cpp-compatible endpoints
* Other OpenAI-compatible local endpoints
* Provider health checks
* Model availability checks
* Better fallback behavior

---

## Team Outputs Still Need Human Review

v0.7.12 improves team synthesis quality through:

* Team handoff compression
* Structured output unwrapping
* Reduced context noise
* Cleaner final synthesis
* Placeholder resource suppression

However, team-generated outputs should still be reviewed before use.

Important notes:

* Generated business content may need editing.
* Source-labeled content should not be treated as verified citation unless the workflow actually retrieved and validated the source.
* Multi-agent outputs can still contain interpretation errors.
* Human review is recommended before publishing, sending, or relying on generated content.

---

## Source Verification Is Not Fully Automated

Orchgentic can use tools, memory, and knowledge search, but v0.7.12 does not yet provide a complete source verification pipeline.

Current limitations:

* Source labels may come from agent-generated context unless explicitly retrieved by a tool.
* The framework does not yet enforce citation validation across all workflows.
* The framework does not yet include built-in source confidence scoring.
* Research workflows should be reviewed before publication.

Future work may include stronger retrieval verification, citation tracking, and source provenance records.

---

## Policy Controls Are Early but Useful

v0.7.12 includes policy-aware routing and tool controls.

Current policy capabilities include:

* Disabled tool blocking
* Confirmation-required actions
* Restricted Gmail send policies
* Pre-LLM policy checks
* Hold-for-confirmation decisions

Current limitations:

* Policy rules are still configuration-driven and relatively simple.
* There is no full policy authoring UI.
* There is no centralized policy audit dashboard.
* More policy types will be needed for production environments.

Confirmation can approve enabled-but-sensitive actions, but it does not override disabled tools.

---

## Gmail Tools Require Careful Configuration

Gmail tools are available in v0.7.12, but they require proper credentials, policies, and confirmation behavior.

Recommended safeguards:

* Keep `gmail.delete` disabled unless explicitly needed.
* Require confirmation for `gmail.send`.
* Require confirmation for `gmail.reply`.
* Use restricted send policies when testing.
* Review generated email content before sending.
* Use `judge-route` before executing sensitive Gmail tasks.

Example safe policy behavior:

```text
gmail.delete disabled
→ delete requests are blocked

gmail.send enabled + confirmation required
→ send requests are held until confirmed
```

---

## Memory Can Introduce Context Noise

Orchgentic supports memory, but memory retrieval can sometimes introduce irrelevant prior context.

v0.7.12 improved team memory filtering, but memory should still be used carefully.

Current limitations:

* Memory relevance is not perfect.
* Old task context may occasionally influence new tasks.
* Team workflows may need stricter memory boundaries depending on the use case.

Future work may include better memory scoping, stronger relevance scoring, and more explicit memory controls.

---

## Knowledge Search Is Basic

Knowledge search is available, but it is still early.

Current limitations:

* Local knowledge storage is basic.
* Advanced source provenance is not complete.
* External vector database support is not yet fully production-hardened.
* Ranking and retrieval quality may vary by content and configuration.

Future work may include stronger ingestion workflows, better retrieval metadata, and improved vector database integrations.

---

## Trigger and Webhook Workflows Need More Hardening

Orchgentic includes trigger concepts such as manual runs, heartbeat intervals, and webhooks.

Current limitations:

* Autonomous trigger workflows should be tested carefully.
* Long-running autonomous execution is not yet production-hardened.
* Operational safeguards need to mature.
* Observability for autonomous runs is still limited.

Event-aware routing is now part of the foundation, but future releases should add stronger monitoring and auditability.

---

## CLI First, No UI Yet

Orchgentic is currently CLI-first and YAML-first.

Current limitations:

* No visual dashboard
* No no-code builder
* No visual team editor
* No visual workflow editor
* No web-based run inspector

This is intentional for the current stage.

The project is first building the runtime foundation. A dashboard and no-code or low-code builder are future milestones.

---

## Error Handling Will Continue to Improve

v0.7.x added error classification and safer routing behavior, but error handling is still evolving.

Current limitations:

* Provider failures may require manual troubleshooting.
* Tool failures may need more detailed diagnostics.
* Retry policies are not fully mature.
* Severe error notification is planned but not fully implemented.
* Dashboard-level error visibility is not yet available.

---

## Not All Workflows Are Fully Declarative Yet

Orchgentic is YAML-first, but not every future workflow capability is fully declarative yet.

Current limitations:

* Workflow DAG execution is not complete.
* Complex workflow branching is still future work.
* Visual workflow editing is not available.
* More schema validation will be needed as workflows expand.

---

## Security Review Is Ongoing

Because Orchgentic can execute tools and interact with external systems, security should be treated seriously.

Recommended precautions:

* Do not enable destructive tools unless needed.
* Use confirmation for sensitive actions.
* Keep credentials out of committed files.
* Use `.env` for secrets.
* Review agent instructions and tool permissions.
* Test policies before autonomous use.
* Avoid broad tool permissions in production-like environments.

A deeper security and policy enforcement review should happen before a stable 1.0 release.

---

## Summary

v0.7.12 is a strong orchestration foundation, but it is still a developer preview.

The most important known gaps are:

* Full observability
* Run history
* Dashboard-ready traces
* Local LLM provider support
* Stronger source verification
* More mature policy management
* Production hardening
* UI and no-code builder support

These limitations are aligned with the roadmap and are expected to guide the v0.8.x and v0.9.x release lines.
