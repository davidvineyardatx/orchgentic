# Orchgentic Quickstart

Get Orchgentic running locally in under 5 minutes.

---

# Requirements

Before installing Orchgentic, ensure you have:

* Python 3.11+
* Git
* A supported AI provider API key

Supported providers:

* Groq
* OpenAI

---

# 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/orchgentic.git
cd orchgentic
```

---

# 2. Create Virtual Environment

## Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 3. Install Orchgentic

```bash
pip install -e .
```

This installs:

* the `orch` CLI
* Orchgentic runtime
* providers
* tools
* orchestration runtime
* timezone support (`tzdata`)

---

# 4. Configure Environment Variables

Create a `.env` file in the project root.

---

## Groq Example

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## OpenAI Example

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

---

# 5. Initialize Orchgentic Workspace

```bash
orch init
```

This creates:

* agents/
* teams/
* memory/
* knowledge/
* triggers/
* logs/

---

# 6. Create Your First Agent

```bash
orch create agent Bob
```

Expected output:

```text
Created agent:
agents/bob.yaml
```

---

# 7. Configure the Agent

Open:

```text
agents/bob.yaml
```

Example configuration:

```yaml
agent:
  id: bob
  name: Bob
  role: General Assistant

  timezone: America/Chicago
  locale: en-US

  provider:
    type: groq
    model: llama-3.3-70b-versatile

  capabilities:
    - web.request
    - datetime.local
    - memory.search
    - knowledge.search

  tools:
    - web.request
    - datetime.local
    - memory.search
    - knowledge.search

  reasoning:
    planner: true
    reflection: true

  memory:
    enabled: true
```

---

# 8. List Agents

```bash
orch list-agents
```

---

# 9. Run Your First Agent

```bash
orch run Bob --debug
```

Example prompt:

```text
Summarize the latest trends in Product Marketing.
```

---

# 10. Test the Tool Runtime

```bash
orch tool run datetime.local --agent Bob
```

Expected output:

```text
timezone='America/Chicago'
weekday='Saturday'
time='08:48:28'
```

---

# 11. Create Your First Team

```bash
orch create team ContentTeam
```

---

# 12. List Teams

```bash
orch list-teams
```

---

# 13. Run a Team

```bash
orch run-team ContentTeam --debug
```

Example orchestration flow:

```text
ManagerAgent
    ↓
ResearchAgent
    ↓
WriterAgent
    ↓
ReviewerAgent
    ↓
Final Output
```

---

# Common Commands

## Workspace

```bash
orch init
```

---

## Agents

```bash
orch create agent Bob
orch list-agents
orch run Bob
```

---

## Teams

```bash
orch create team ContentTeam
orch list-teams
orch run-team ContentTeam
```

---

## Tools

```bash
orch list-tools --agent Bob
orch tool run datetime.local --agent Bob
```

---

## Memory

```bash
orch memory search "Product Marketing"
```

---

## Knowledge

```bash
orch knowledge ingest docs/
orch knowledge search "marketing trends"
```

---

# Recommended First Demo Flow

For first-time users:

1. `orch init`
2. `orch create agent Bob`
3. `orch list-agents`
4. `orch run Bob --debug`
5. `orch tool run datetime.local --agent Bob`
6. `orch create team ContentTeam`
7. `orch list-teams`
8. `orch run-team ContentTeam --debug`

This demonstrates:

* runtime initialization
* provider integration
* agent execution
* tool runtime
* orchestration
* delegation
* team execution

---

# Troubleshooting

## Missing API Key

Example error:

```text
ProviderError: Missing GROQ_API_KEY
```

Solution:

* verify `.env`
* restart terminal session
* confirm provider configuration

---

## Tool Not Found

Example error:

```text
Tool not found: datetime.local
```

Solution:

* verify tool exists in `tools`
* confirm tool included in agent YAML
* reinstall package:

```bash
pip install -e .
```

---

## Invalid Timezone

Example error:

```text
Unknown timezone 'America/Chicago'
```

Solution:

* ensure `tzdata` installed
* use valid IANA timezone names

---

# Current Status

Developer Preview:
`v0.7.5-alpha`

Current focus:

* runtime stabilization
* orchestration reliability
* observability foundations
* provider maturity
* workflow orchestration

---

# Next Steps

After completing Quickstart:

* review `EXAMPLES.md`
* explore orchestration flows
* create specialized agents
* build multi-agent teams
* test triggers and webhooks
* experiment with delegation and memory

---

# Orchgentic

### Coordinate. Scale. Observe. Autonomous AI Systems.
