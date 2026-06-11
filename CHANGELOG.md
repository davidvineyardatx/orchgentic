# Changelog

## v0.7.10.1-alpha

- Added dynamic token-savings estimation
- Added execution timing for route telemetry
- Added route metrics aggregation
- Added `orch route-metrics`


## v0.7.10-alpha

- Added editable router policy config and fallback terms for LLM-required requests.


- Added deterministic argument extraction
- Added deterministic multi-tool chaining for Gmail subject-line retrieval
- Added deterministic formatting layer
- Added route telemetry logging
- Added estimated token savings metadata


## v0.7.9-alpha

- Added deterministic router
- Added no-LLM routing for date/time
- Added no-LLM routing for Gmail search/read
- Added exact-field no-LLM routing for Gmail draft/send
- Added route telemetry helper


## v0.7.8-alpha

- Added `gmail.send`
- Added `gmail.reply`
- Added `gmail.delete`
- Added runtime confirmation enforcement
- Added Gmail recipient policy enforcement
- Added Gmail send/modify OAuth scopes
- Gmail delete moves messages to Trash only


## v0.7.7-alpha

- Added named Gmail connections
- Added Gmail connector CLI commands
- Added gmail.search, gmail.read, gmail.draft
- Added tool policy governance foundation


## v0.7.6-alpha

- Added `orch create agent`
- Added `orch create team`
- Added `orch create trigger`


## v0.7.5-alpha Developer Preview

Initial public developer preview release.

Includes:

- Branded Orchgentic package and `orch` CLI
- Multi-agent orchestration
- Team execution
- Delegation
- Tool runtime
- Tool parser continuation fixes
- Capability preflight
- Memory and semantic knowledge
- Triggers and webhooks
- Groq and OpenAI provider support
- Time context resolver
- `datetime.local`
- `tzdata` dependency for Windows timezone support
