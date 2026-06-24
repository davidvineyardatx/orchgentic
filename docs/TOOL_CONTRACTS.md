# Tool Contracts

`v0.8.0-beta.6-alpha.1` freezes the current built-in tool contract baseline.

This is documentation and schema baseline work only.

It does **not** add new tools, change tool execution, add a plugin loader, or introduce a marketplace/plugin system.


## Registry-First Contract Flow

The tool registry is the source of truth.

A user should only need to add a tool to the registry for Orchgentic to include it in contract validation.

Recommended built-in tool flow:

```text
create tool class
register tool in the tool registry
run orch doctor tool-contracts
fix any missing metadata warnings/errors
```

Orchgentic derives contracts from registered tool definitions with:

```text
get_tool_contracts_from_registry(...)
validate_tool_registry_contracts(...)
```

A tool class can optionally declare metadata directly:

```python
category = "slack"
side_effect = "send"
destructive = True
supports_confirmation = True
requires_policy_check = True
```

If metadata is not declared, Orchgentic infers safe defaults from the tool name and input schema.

This avoids maintaining a second manual registry of contracts.

## Contract Shape

Each tool contract exposes this stable shape:

```text
name
description
input_schema
category
side_effect
destructive
supports_confirmation
requires_policy_check
builtin
notes
```

The `input_schema` field follows the current Orchgentic object-schema convention:

```yaml
input_schema:
  type: object
  properties: {}
  required: []
```

## Built-in Tool Inventory

```text
datetime.now
datetime.local
filesystem.read
filesystem.write
web.request
memory.search
knowledge.search
delegate.agent
gmail.search
gmail.read
gmail.draft
gmail.send
gmail.reply
gmail.delete
```

## Confirmation and Policy Baseline

The current baseline distinguishes these fields:

```text
supports_confirmation
requires_policy_check
destructive
side_effect
```

Gmail side-effect tools expose a `confirm` input and are policy-aware:

```text
gmail.draft
gmail.send
gmail.reply
gmail.delete
```

The current filesystem write baseline is intentionally documented as-is:

```text
filesystem.write
  destructive: true
  side_effect: write
  supports_confirmation: false
```

That does not mean this is the final v1.0 behavior. It means beta.6 starts by freezing the current behavior before changing it.

## Runtime Boundary

This patch does not change runtime behavior.

Future beta.6 work can use this baseline to stabilize:

```text
tool schema requirements
confirmation behavior
plugin tool contract shape
tool policy expectations
```


## Confirmation Contract Baseline

`v0.8.0-beta.6-alpha.2` freezes the confirmation metadata baseline.

This baseline is metadata-only and does not change runtime behavior.

Confirmation metadata shape:

```text
name
supports_confirmation
requires_confirm_input
confirm_input_type
destructive
side_effect
requires_policy_check
confirmation_required_by_contract
confirmation_recommended
runtime_behavior_changed
```

Current confirmation-supporting built-ins:

```text
gmail.draft
gmail.send
gmail.reply
gmail.delete
```

Current destructive built-ins:

```text
filesystem.write
gmail.send
gmail.reply
gmail.delete
```

Known current baseline:

```text
filesystem.write
  destructive: true
  side_effect: write
  supports_confirmation: false
```

This is intentionally documented as the current baseline. It is not a v1.0 recommendation.

Future beta.6 work may tighten confirmation behavior, but alpha.2 only freezes and validates the current shape.


## Runtime Confirmation Consistency

`v0.8.0-beta.6-alpha.3` compares the frozen confirmation contract metadata to the current runtime baseline.

This is inspection-only.

It does not change tool execution behavior.

Current runtime confirmation tools:

```text
gmail.draft
gmail.send
gmail.reply
gmail.delete
```

Current known runtime baseline:

```text
Gmail write/send/delete tools expose a boolean confirm argument and use Gmail tool policy.
Read-only tools do not require confirmation.
filesystem.write is currently destructive but does not support confirmation enforcement.
```

The consistency helper reports:

```text
contract_supports_confirmation
contract_requires_confirm_input
runtime_supports_confirmation
runtime_confirm_argument
contract_requires_policy_check
runtime_requires_policy_check
consistent
runtime_behavior_changed
notes
```

`runtime_behavior_changed` must remain `false` for this alpha.


## Plugin Tool Contract Shape

`v0.8.0-beta.6-alpha.4` freezes the expected shape for future plugin tool contracts.

This is contract-shape work only.

It does **not** add:

```text
plugin loading
dynamic tool discovery
external package loading
marketplace support
plugin execution
```

A plugin tool contract must still follow the base tool contract shape:

```text
name
description
input_schema
category
side_effect
destructive
supports_confirmation
requires_policy_check
builtin
```

Additional plugin metadata:

```text
plugin.name
plugin.version
plugin.author
plugin.source
```

Example:

```yaml
name: acme.crm.lookup_contact
description: Look up a contact in Acme CRM.
input_schema:
  type: object
  properties:
    email:
      type: string
  required:
    - email
category: crm
side_effect: read
destructive: false
supports_confirmation: false
requires_policy_check: true
builtin: false
plugin:
  name: acme-crm
  version: 0.1.0
  author: Acme
  source: local
```

Contract helpers:

```text
normalize_plugin_tool_contract(...)
validate_plugin_tool_contract(...)
```

Both helpers are validation/normalization only and report:

```text
plugin_loader_added: false
runtime_behavior_changed: false
```


## Tool Contract Doctor Checks

`v0.8.0-beta.6` finalizes the tool/plugin contract stabilization track with doctor checks.

```bash
orch doctor tool-contracts
orch doctor tool-contracts --json
```

The doctor command validates:

```text
built-in tool contract shape
confirmation contract shape
runtime confirmation consistency metadata
future plugin contract shape helpers
```

The command reports:

```text
status
valid
tool_count
errors
warnings
plugin_loader_added
runtime_behavior_changed
```

This is inspection-only. It does not load plugins, register plugin tools, execute tools, or change confirmation/runtime behavior.
