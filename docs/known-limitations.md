# Known Limitations for v0.9.0-rc.1

Orchgentic v0.9.0-rc.1 is a developer release candidate.

## Not included before v1.0

- Hosted dashboard
- No-code visual builder
- Marketplace
- Enterprise authentication
- Multi-tenant SaaS runtime
- Complex workflow DAGs
- Parallel workflow execution
- Distributed workers
- Full local LLM replacement
- New major provider families
- New major RAG architecture

## Current expectations

- Workflows are YAML-first and stabilization-focused.
- Local reasoner is routing/deterministic-task focused, not a full replacement for an LLM.
- Provider credentials remain developer-managed.
- Gmail tools require Gmail auth setup.
- Some optional commands may require being wired into the root CLI if they were introduced as modular command apps.
