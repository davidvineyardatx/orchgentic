# Orchgentic Roadmap

## Current Track: v0.8.0-beta.5 — Execution Tier Configuration and Local LLM Readiness

Goal:

```text
Use the stabilized policy layer from beta.4 to prepare clear execution-tier configuration for deterministic, local LLM, external LLM, and premium/model-configurable work.
```

Planned beta.5 milestones:

```text
v0.8.0-beta.5-alpha.1 — Execution Tier Config Normalization
```

Scope boundary:

```text
No local LLM execution yet.
No routing behavior changes.
No new dashboard/report features.
```

## Completed: v0.8.0-beta.4 — Runtime Cost Hardening and Decision Policy Stabilization

Status: feature-complete after `v0.8.0-beta.4-alpha.9`.

Completed beta.4 milestones:

```text
v0.8.0-beta.4-alpha.3 — Execution Policy Foundation
v0.8.0-beta.4-alpha.4 — Policy-Aware Routing Decisions
v0.8.0-beta.4-alpha.5 — Deterministic Policy Classification and Judgment Output Polish
v0.8.0-beta.4-alpha.6 — Safe Advisory Policy Enforcement
v0.8.0-beta.4-alpha.7 — Safe Enforcement Trace Coverage
v0.8.0-beta.4-alpha.8 — Policy Enforcement Clarity
v0.8.0-beta.4-alpha.9 — Policy Report and Route Summary
```

Beta.4 added policy-aware route judgment, safe deterministic enforcement metadata, trace/report coverage, and compact CLI policy inspection through `orch judge-route --summary` and `orch policy-report`.

No additional beta.4 feature work is planned.


## Historical v0.8.0 Observability Track

## Current Track: v0.8.0 Observability

Goal:

```text
Make every Orchgentic run inspectable, traceable, and dashboard-ready.
```

Completed:

```text
v0.8.0-alpha.1 — Observability foundation
v0.8.0-alpha.2 — CLI trace inspection
v0.8.0-alpha.3 — Trace coverage hardening and direct-tool token savings
v0.8.0-alpha.4 — Dashboard-ready exports
v0.8.0-alpha.5 — Retention and cleanup
v0.8.0-alpha.6 — Failure diagnostics
v0.8.0-alpha.7 — Static dashboard preview
v0.8.0-alpha.8 — Dashboard filter/open UX, developer controls, empty states, metadata
v0.8.0-alpha.9 — Dashboard pagination
```

## Dashboard Direction

The dashboard remains local-first and static:

```text
no server required
no hosted service required
no frontend build required
```

Current dashboard capabilities:

```text
run metrics
failure metrics
token usage
estimated token savings
filters
search
client-side pagination
modal run details
copy commands
empty states
metadata panel
```

## Upcoming Considerations

Potential next areas:

```text
dashboard polish
export/import workflows
trace diffing
saved dashboard views
severe-error notifications
hosted dashboard option
```


## v0.8.0-alpha.10 — Observability Reliability and Release Readiness

Scope:

```text
orch doctor observability
dashboard schema/version footer
store/status checks
clear empty/not-initialized hints
release validation documentation
```

After alpha.10, the next target is:

```text
v0.8.0-beta.1 — Observability Stabilization
```

## v0.8.0-beta.2 — Observability hardening and clean-install polish

Status: in progress / validation-ready.

Focus:

- Clean-install doctor behavior
- Zero-run dashboard generation
- Clear dashboard open behavior
- First-run guidance
- Fresh workspace validation


## v0.8.0-beta.2 release hygiene

- Added `orch clean-testdata` to safely remove generated logs, exports, memory stores, pytest cache, Python bytecode caches, and other local runtime/test artifacts before publishing.
- The command is dry-run by default and requires `--no-dry-run --confirm` before deleting anything.
- Configuration and source files are preserved.
