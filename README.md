# Quickstart

Welcome to Orchgentic — an open-source orchestration platform for building deterministic, autonomous, and scalable AI agent systems.

This Quickstart guide walks through:

* installation
* project initialization
* agent creation
* deterministic routing
* Gmail integration
* telemetry
* route metrics
* running agents

---

# Requirements

* Python 3.12+
* pip
* Windows, Linux, or macOS

---

# Install Orchgentic

Clone the repository:

```bash
git clone https://github.com/your-org/orchgentic.git
cd orchgentic
```

Create and activate a virtual environment.

## Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Orchgentic:

```bash
pip install -e .
```

Verify installation:

```bash
orch --help
```

---

# Initialize a Project

Create a new Orchgentic project:

```bash
orch init
```

This creates:

* agents/
* memory/
* knowledge/
* logs/
* config/

---

# Create an Agent

Create a new agent:

```bash
orch create-agent Bob
```

This generates:

```text
agents/Bob.yaml
```

---

# Example Agent Configuration

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant
  description: Local development assistant powered by Orchgentic.

  instructions: |
    You are Bob, a helpful AI assistant.
    Use memory, knowledge, and tools when relevant.

  timezone: America/Chicago
  locale: en-US

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  capabilities:
    - filesystem.read
    - filesystem.write
    - web.request
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search
    - gmail.search
    - gmail.read
    - gmail.draft
    - gmail.send
    - gmail.reply
    - gmail.delete

  tools:
    - filesystem.read
    - filesystem.write
    - web.request
    - datetime.now
    - datetime.local
    - memory.search
    - knowledge.search
    - gmail.search
    - gmail.read
    - gmail.draft
    - gmail.send
    - gmail.reply
    - gmail.delete

  tool_runtime:
    enabled: true
    max_iterations: 4
    timeout_seconds: 90
    allow_parallel: false
    save_results_to_memory: false

  delegation:
    enabled: false
    allowed_agents: []
    max_depth: 2

  reasoning:
    planner: true
    reflection: true

  memory:
    enabled: true
    recent_messages: 10
    db_path: memory/orchgentic.db

  knowledge:
    enabled: true
    top_k: 5
    store: local
    db_path: memory/orchgentic.db
    collection: orchgentic_knowledge

  gmail:
    connection: assistant

  gmail.send:
    enabled: true
    require_confirmation: true

    send_policy:
      mode: restricted

      allowed_addresses:
        - your@email.com

      allowed_domains: []

      require_confirmation: true

  gmail.reply:
    enabled: true
    require_confirmation: true

  gmail.delete:
    enabled: false
    require_confirmation: true
```

---

# Gmail Integration

## Connect Gmail

Connect a Gmail account:

```bash
orch connect gmail --name assistant
```

Or specify credentials manually:

```bash
orch connect gmail \
  --name assistant \
  --credentials D:/development/gmail-assistant.json
```

After browser authorization completes, Orchgentic stores the authenticated Gmail connection locally.

---

# Important Gmail Configuration

Your agent YAML should define:

```yaml
gmail:
  connection: assistant
```

This ensures the runtime consistently uses the correct Gmail connection.

---

# Test Gmail Integration

## List Gmail Accounts

```bash
orch gmail list
```

## Search Gmail Messages

Before reading or summarizing Gmail messages, first search Gmail to retrieve valid message IDs.

Example:

```bash
orch run Bob --debug
```

Task:

```text
search Gmail "newer_than:7d"
```

This returns recent Gmail messages and their associated `message_id` values.

---

## Run Gmail Tool Directly

```bash
orch tool run gmail.read \
  --agent Bob \
  --arg message_id=<MESSAGE_ID>
```

---

## Deterministic Gmail Read

```bash
orch run Bob --debug
```

Task:

```text
read Gmail message id <MESSAGE_ID>
```

---

## Gmail Read + Summarization

```bash
orch run Bob --debug
```

Task:

```text
read Gmail message id <MESSAGE_ID> and summarize message
```

---

# Deterministic Routing

Orchgentic supports deterministic routing for operational tasks.

This allows Orchgentic to:

* bypass external LLM calls
* reduce token usage
* reduce latency
* improve orchestration predictability

Example:

```bash
orch run Bob --debug
```

Task:

```text
what time is it
```

This executes through deterministic routing without external LLM usage.

---

# Route Telemetry

Every route generates telemetry including:

* route type
* selected tool
* confidence score
* estimated token savings
* execution timing
* provider/model information

Example telemetry:

```json
{
  "timestamp": "2026-06-10T18:24:38.080488+00:00",
  "route_type": "single_tool",
  "external_llm_used": false,
  "selected_tool": "gmail.read",
  "confidence": 0.94,
  "reason": "Direct Gmail read request",
  "estimated_external_tokens_saved": 428,
  "execution_time_ms": 42.5,
  "agent": "Bob",
  "provider": "groq",
  "model": "llama-3.3-70b-versatile"
}
```

---

# Route Metrics

View aggregated route metrics:

```bash
orch route-metrics
```

Metrics include:

* deterministic route count
* LLM escalation count
* estimated token savings
* tool usage frequency
* route type distribution

Metrics are stored in:

```text
logs/route_metrics.json
```

Detailed route events are appended to:

```text
logs/routes.jsonl
```

---

# Inspect Agent Configuration

Inspect normalized runtime configuration:

```bash
orch inspect-agent Bob
```

This validates:

* YAML loading
* provider configuration
* Gmail configuration
* tool registration
* runtime policies
* orchestration behavior

---

# Useful Commands

## List Agents

```bash
orch list-agents
```

## List Tools

```bash
orch list-tools
```

## Search Memory

```bash
orch memory search Bob "weather"
```

## Search Knowledge

```bash
orch knowledge search "orchestration"
```

---

# Current Routing Philosophy

Orchgentic is designed around:

```text
Deterministic execution first.
Reasoning only when necessary.
```

Operational work should be handled by orchestration infrastructure whenever possible.

Reasoning models should be reserved for:

* analysis
* summarization
* planning
* creative generation
* complex reasoning

This dramatically reduces:

* token consumption
* latency
* orchestration unpredictability

while improving scalability and operational reliability.

---

# Current Stable Release

```text
v0.7.10.1-alpha
```

Validated features:

* deterministic routing
* deterministic formatting
* Gmail integration
* dynamic token estimation
* route telemetry
* route metrics
* YAML-driven orchestration behavior

---

# Next Roadmap

## v0.7.11-alpha

* local mini reasoner integration
* confidence scoring
* external LLM escalation logic

## v0.7.12-alpha

* workflow-aware routing
* event-aware routing
* policy-aware escalation

---

# Orchgentic Vision

Orchgentic is building orchestration infrastructure for the autonomous AI era.

The future of AI is not simply “chat.”

The future is intelligent orchestration systems capable of:

* deterministic execution
* scalable autonomy
* efficient reasoning
* dynamic infrastructure coordination
* multi-agent collaboration
* operational observability
