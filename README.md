# Orchgentic

> Stop letting agents become black boxes that eat tokens in the dark.

Orchgentic is a **local-first AI operations layer** for developers and technical teams who need agents, tools, policies, memory, knowledge, routing, observability, and token usage to work together under clear, version-controlled contracts — without burning tokens just to figure out what to do next.

---

## What Is Orchgentic?

Most agent frameworks hand control to an LLM and hope for the best. Orchgentic takes a different approach: it reasons about *whether* and *how* to use an LLM before spending a single token.

At every step, Orchgentic helps decide:

- Which agent should handle a task
- Whether a tool can be run directly without an LLM
- Whether memory or knowledge needs to be searched
- Whether the task can be handled locally
- Which external provider, if any, should be called
- Whether a workflow or agent team should be used
- Whether policy allows the action
- Whether human confirmation is required
- How the run should be inspected afterward

Every decision is recorded, inspectable, and token-aware.

---

## Why Orchgentic?

### The Problem With Other Frameworks

Most agent frameworks assume the LLM is always the right tool.

The result: agents burn tokens routing tasks they do not need to route, lose context across tool calls, operate as opaque black boxes, and ignore the cost of every decision.

### The Orchgentic Difference

| Concern | Most Frameworks | Orchgentic |
|---|---|---|
| **Token usage** | LLM decides everything, always | Deterministic routing bypasses LLMs when possible |
| **Observability** | Log files, if you are lucky | Built-in run history, trace events, exports, and local dashboard |
| **Policy control** | Application-layer hacks | First-class policy checks with per-tool rules |
| **Local execution** | Rarely central | Core design goal — local/direct execution is recorded and provable |
| **Multi-agent teams** | Manual wiring | Native team orchestration with handoff compression |
| **Configuration** | Often code-first | YAML-based agent and team contracts |
| **Provider flexibility** | Often tied to one model/vendor | Pluggable provider direction: Groq, OpenAI, LM Studio, local LLMs |
| **Cost awareness** | Usually invisible | Token Intelligence reports with estimated savings |

Orchgentic is built for teams that need agents to be **observable, policy-safe, token-aware, and trustworthy** — not just functional.

---

## Key Features

### Routing and Reasoning

- Deterministic tool routing to bypass LLMs when they are not needed
- Local reasoning with confidence scoring
- Workflow-aware and event-aware routing
- Policy-aware escalation with per-tool rules
- Direct tool execution with traceable `routing.bypassed` events

### Execution

- YAML-based agent configuration
- Pluggable provider support
- Tool registry with direct and confirmation-required execution
- Multi-agent team orchestration with handoff compression
- Memory and knowledge search integration
- Planning and reflection

### Observability

- Run history and trace events stored locally
- Token Intelligence reports with estimated savings tracking
- Local static dashboard with search, filters, pagination, and run inspection
- Token-scoped Run ID modal in the Token Intelligence section
- Export commands for JSON / JSONL inspection
- Observability doctor for health checks

### Policy and Safety

- Gmail tool policies
- Disabled-tool blocking
- Human confirmation gates
- Policy checks before sensitive tool execution
- Team synthesis guardrails

---

## Quick Install

**Requirements:** Python 3.12+, Git

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

> Note: On macOS/Linux, the virtual environment activation path is usually `source .venv/bin/activate`. On Windows Git Bash, use `source .venv/Scripts/activate`.

---

## First Run

```bash
# See what is available
orch list-agents
orch list-tools

# Run an agent
orch run Bob

# Run a tool directly through Bob
orch tool run datetime.local --agent Bob

# Inspect what happened
orch runs
orch run-info <run_id>
orch trace <run_id>
```

---

## Token Intelligence in 60 Seconds

Run a deterministic tool and inspect where tokens went — or did not go:

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

Orchgentic proved the task did not need an LLM, routed directly to the tool, and recorded the estimated savings.

Every run is inspectable.

Filter reports by agent, team, status, or run type:

```bash
orch token-report --agent Bob
orch token-report --team ContentTeam
orch token-report --status completed
orch token-report --type tool
orch token-report --json
```

Example proof event:

```text
routing.bypassed (routing/direct_tool) saved≈349, source=estimated - Direct tool execution bypassed LLM routing.
```

Estimated token savings are operational estimates of avoided LLM routing/execution overhead. They are not billing claims.

---

## Observability Dashboard

Generate a local static HTML dashboard from your run history:

```bash
orch dashboard
```

Open the existing dashboard:

```bash
orch dashboard --open
```

Generate a filtered dashboard:

```bash
orch dashboard --team ContentTeam --limit 500
```

The dashboard runs entirely locally — no hosted service required.

Dashboard features include:

- run summaries
- failure summaries
- Token Intelligence
- search
- quick filters
- client-side pagination
- modal run details
- token-scoped Run ID modal
- copy commands
- empty states
- generated metadata panel

---

## Provider Setup

Agents only call an external provider when a task actually escalates to one. Direct tool runs and local reasoning paths can spend zero external LLM tokens.

Configure only the provider your agent needs.

```env
# Groq
GROQ_API_KEY=your_groq_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Local OpenAI-compatible runtime such as LM Studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

Design rule:

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether the provider should be used
```

A configured provider does not mean a provider was used for every run.

For direct tool runs or deterministic routes, Orchgentic may report:

```text
external_llm_used: False
provider used: N/A — no LLM used
configured provider: groq / llama-3.3-70b-versatile
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

## Common CLI Commands

| Command | Purpose |
|---|---|
| `orch init` | Initialize a workspace |
| `orch list-agents` | List configured agents |
| `orch list-tools` | List available tools |
| `orch run Bob` | Run an agent |
| `orch judge-route "<task>" --agent Bob` | Preview routing without executing |
| `orch tool run <tool> --agent Bob` | Run a tool directly |
| `orch run-team contentteam --debug` | Run a configured team |
| `orch runs` | List recorded runs |
| `orch run-info <run_id>` | Inspect a run and its trace |
| `orch trace <run_id>` | Inspect trace events |
| `orch token-report` | Show Token Intelligence summary |
| `orch dashboard` | Generate local dashboard |
| `orch doctor observability` | Check observability health |
| `orch clean-testdata` | Preview cleanup of generated data |

---

## Release Cleanup

Preview cleanup:

```bash
orch clean-testdata
```

Verbose dry run:

```bash
orch clean-testdata --verbose
```

JSON output:

```bash
orch clean-testdata --json
```

Actually clean generated runtime/test data:

```bash
orch clean-testdata --no-dry-run --confirm
```

The cleanup command removes generated artifacts such as:

- `logs/`
- `exports/`
- `memory/`
- `.pytest_cache/`
- `__pycache__/`
- `*.pyc`

It preserves:

- `agents/`
- `teams/`
- `triggers/`
- `docs/`
- `.env`
- provider credentials
- source code

For final release cleanup before publishing:

```bash
PYTHONDONTWRITEBYTECODE=1 orch clean-testdata --no-dry-run --confirm
git status
```

PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; orch clean-testdata --no-dry-run --confirm
git status
```

After final cleanup, avoid running `pytest`, `python`, or `orch` again before checking and committing, because those commands can recreate bytecode cache files.

---

## Validation

Recommended validation before release:

```bash
python -m pytest -q tests/test_observability_v0_8_0.py
python -m pytest -q

orch tool run datetime.local --agent Bob
orch token-report
orch dashboard --limit 500
orch dashboard --open
```

---

## Current Status

Orchgentic is in **developer preview beta**.

The core runtime is functional and available now. The following are planned for future releases:

- hosted dashboard and SaaS control plane
- no-code workflow builder
- stable workflow YAML contract
- plugin marketplace
- enterprise RBAC
- distributed workers

The current focus is a stable, hardened local-first runtime that teams can build on confidently.

---

## Roadmap to v1.0

Near-term priorities:

- Token Intelligence polish and local reasoning proof
- Runtime hardening and error consistency
- Configuration and tool/plugin contract freeze
- Workflow execution foundation
- RAG, memory, and knowledge stabilization
- Provider and local LLM stabilization
- SDK and local API foundation
- Dashboard and workbench improvements

At v1.0, Orchgentic will be:

```text
CLI-first
SDK-supported
local API-enabled
dashboard-observable
workflow-capable
RAG-aware
local LLM-ready
builder-ready
```

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
| `docs/OBSERVABILITY_EXAMPLES.md` | Observability and Token Intelligence examples |
| `ROADMAP.md` | What is coming |

---

## Vision

The autonomous AI era is only beginning.

Orchgentic is being built to be the orchestration runtime that makes multi-agent systems observable, governable, and cost-aware — from a single developer's laptop to production-scale deployments.

---

*Orchgentic is open-source. Future hosted, enterprise, and team collaboration features are on the roadmap.*
