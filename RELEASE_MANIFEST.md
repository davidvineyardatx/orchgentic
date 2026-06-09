# Orchgentic v0.7.0 Full Cumulative Release Manifest

Source Package: `orchgentic-v0.7.8`

Sprint 7

## Missing Sprint 6 Files
None

## Added Sprint 7 Files
- orchgentic/agents/manager.py
- orchgentic/agents/registry.py
- orchgentic/orchestration/__init__.py
- orchgentic/orchestration/context.py
- orchgentic/orchestration/delegation.py
- orchgentic/orchestration/messages.py
- orchgentic/orchestration/team_runner.py
- orchgentic/teams/__init__.py
- orchgentic/teams/registry.py
- orchgentic/tools/core/delegate_agent.py
- tests/test_agent_registry.py
- tests/test_team_registry.py

## Added

- `gmail.send`
- `gmail.reply`
- `gmail.delete`
- runtime confirmation enforcement
- Gmail recipient allowlist/domain policy enforcement
- Gmail send/modify OAuth scopes
- delete behavior moves messages to Trash only

## Governance

Gmail actions require runtime policy approval and can require explicit `confirm=true`.

## Reconnect Required

Existing Gmail tokens should be reconnected to include send/modify scopes.
