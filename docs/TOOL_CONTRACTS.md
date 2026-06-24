# Tool Contracts

`v0.8.0-beta.6-alpha.1` freezes the current built-in tool contract baseline.

This is documentation and schema baseline work only.

It does **not** add new tools, change tool execution, add a plugin loader, or introduce a marketplace/plugin system.

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
