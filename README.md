# Orchgentic

> Stop letting agents become black boxes that eat tokens in the dark.

Orchgentic is a **local-first AI operations layer** for developers and technical teams who need agents, tools, policies, memory, and observability to work together under clear, version-controlled contracts — without burning tokens just to figure out what to do next.

---

## What Is Orchgentic?

Most agent frameworks hand control to an LLM and hope for the best. Orchgentic takes a different approach: it reasons about *whether* and *how* to use an LLM before spending a single token.

At every step, Orchgentic decides:

- Which agent should handle a task
- Whether a tool can be run directly — without an LLM
- Whether memory or knowledge needs to be searched
- Whether the task can be handled locally
- Which external provider (if any) to call
- Whether a workflow or agent team should be used
- Whether policy allows the action
- Whether human confirmation is required

Every decision is recorded, inspectable, and token-aware.

---

## Why Orchgentic?

### The Problem With Other Frameworks

Most agent frameworks assume the LLM is always the right tool. The result: agents burn tokens routing tasks they don't need to route, lose context across tool calls, operate as opaque black boxes, and ignore the cost of every decision.

### The Orchgentic Difference

| Concern | Most Frameworks | Orchgentic |
|---|---|---|
| **Token usage** | LLM decides everything, always | Deterministic routing bypasses LLM when possible |
| **Observability** | Log files, if you're lucky | Built-in run history, trace events, and a local dashboard |
| **Policy control** | Application-layer hacks | First-class policy engine with per-tool rules |
| **Local execution** | Rarely considered | Core feature — local reasoning proven and recorded |
| **Multi-agent teams** | Manual wiring | Native team orchestration with handoff compression |
| **Configuration** | Code-first | YAML-based agent contracts, version-controllable |
| **Provider flexibility** | Locked to one model/vendor | Pluggable: Groq, OpenAI, LM Studio, local LLMs |
| **Cost awareness** | Invisible | Token Intelligence reports with estimated savings |

Orchgentic is built for teams that need agents to be **observable, policy-safe, token-aware, and trustworthy** — not just functional.

---

## Key Features

**Routing & Reasoning**
- Deterministic tool routing — bypass the LLM when you don't need it
- Local reasoning with confidence scoring
- Workflow-aware and event-aware routing
- Policy-aware escalation with per-tool rules

**Execution**
- YAML-based agent configuration
- Pluggable provider support (Groq, OpenAI, LM Studio, local LLMs)
- Tool registry with direct and confirmation-required execution
- Multi-agent team orchestration with handoff compression
- Memory and knowledge search integration
- Planning and reflection

**Observability**
- Run history and trace events stored locally
- Token Intelligence reports with estimated savings tracking
- Local static dashboard with search, filters, and run inspection
- Export commands (JSON / JSONL)
- Observability doctor for health checks

**Policy & Safety**
- Gmail tool policies
- Disabled-tool blocking
- Human confirmation gates
- Team synthesis guardrails

---

## Quick Install

**Requirements:** Python 3.9+, Git

```bash
# Clone the repository
git clone https://github.com/davidvineyardatx/orchgentic.git
cd orchgentic

# Create and activate a virtual environment
python -m venv .venv

# Git Bash / macOS / Linux
source .venv/Scripts/activate

# PowerShell (Windows)
# .\.venv\Scripts\Activate.ps1

# Install in editable mode
pip install -e .

# Initialize your workspace
orch init

# Verify the CLI
orch --help
```

---

## First Run

```bash
# See what's available
orch list-agents
orch list-tools

# Run an agent
orch run Bob

# Run a tool directly (no LLM used)
orch tool run datetime.local --agent Bob

# Inspect what happened
orch runs
orch run-info <run_id>
orch trace <run_id>
```

---

## Token Intelligence in 60 Seconds

Run a deterministic tool and inspect where tokens went — or didn't go:

```bash
orch tool run datetime.local --agent Bob
orch token-report
```

Example output:

```text
TOKEN INTELLIGENCE
local_runs:          1 (100.0%)
external_llm_runs:   0 (0.0%)
direct_tool_runs:    1
total_tokens:        0
estimated_tokens_saved: 349
```

Orchgentic proved the task didn't need an LLM, routed directly to the tool, and recorded the savings. Every run is inspectable.

Filter reports by agent, team, status, or run type:

```bash
orch token-report --agent Bob
orch token-report --team ContentTeam
orch token-report --status completed
orch token-report --json
```

---

## Observability Dashboard

Generate a local static HTML dashboard from your run history:

```bash
orch dashboard
orch dashboard --open
orch dashboard --team ContentTeam --limit 500
```

The dashboard runs entirely locally — no hosted service required. It includes run summaries, failure analysis, Token Intelligence, search, filters, and modal run details.

---

## Provider Setup

Agents only call an external provider when a task actually escalates to one. Direct tool runs and local reasoning paths spend zero external tokens.

```env
# Groq
GROQ_API_KEY=your_groq_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Local (LM Studio or compatible)
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

---

## Preview Routing Without Executing

```bash
# See how Orchgentic would route a task
orch judge-route "what is the local time?" --agent Bob

# Check a policy-controlled action
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

---

## Current Status

Orchgentic is in **developer preview alpha**. The core runtime is functional and available now. The following are planned for future releases:

- Hosted dashboard and SaaS control plane
- No-code workflow builder
- Stable workflow YAML contract
- Plugin marketplace
- Enterprise RBAC
- Distributed workers

The current focus is a stable, hardened local-first runtime that teams can build on confidently.

---

## Roadmap to v1.0

Near-term priorities:

- Token Intelligence polish and local reasoning proof
- Runtime hardening and error consistency
- Configuration and tool/plugin contract freeze
- Workflow execution foundation
- RAG, memory, and knowledge stabilization
- SDK and local API foundation
- Dashboard and workbench improvements

At v1.0, Orchgentic will be: **CLI-first · SDK-supported · local API-enabled · dashboard-observable · workflow-capable · RAG-aware · local LLM-ready · builder-ready**

---

## Documentation

| Document | Description |
|---|---|
| `docs/QUICKSTART.md` | Get up and running fast |
| `docs/CLI_COMMANDS.md` | Full CLI reference |
| `docs/AGENT_CONFIGURATION.md` | YAML agent schema |
| `docs/TEAM_CONFIGURATION.md` | Multi-agent team setup |
| `docs/TOOLS_AND_POLICIES.md` | Tool registry and policy rules |
| `docs/ROUTING_AND_REASONING.md` | How routing decisions are made |
| `docs/OBSERVABILITY.md` | Run history and trace events |
| `docs/OBSERVABILITY_DASHBOARD.md` | Dashboard generation and usage |
| `ROADMAP.md` | What's coming |

---

## Vision

The autonomous AI era is only beginning. Orchgentic is being built to be the orchestration runtime that makes multi-agent systems observable, governable, and cost-aware — from a single developer's laptop to production-scale deployments.

---

*Orchgentic is open-core. The runtime is free and open-source. Enterprise features are on the roadmap.*
