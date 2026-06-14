## Architecture Overview

Orchgentic is organized around a CLI-first, YAML-configured orchestration runtime that connects agents, providers, reasoning, routing, policies, tools, memory, knowledge, triggers, and multi-agent teams.

![Orchgentic Architecture](assets/orchgentic-architecture.svg)

```mermaid
flowchart TD
    CLI["orch CLI"] --> Core["Orchgentic Core Runtime"]

    Config["YAML Configuration<br/>agents • teams • triggers • policies"] --> Core

    Core --> Reasoning["Reasoning Layer<br/>local reasoner • confidence scoring • escalation decisions"]
    Core --> Routing["Routing Layer<br/>workflow-aware • event-aware • policy-aware"]
    Core --> Providers["LLM Providers<br/>Groq • OpenAI • future local providers"]
    Core --> ToolLoop["Tool Runtime<br/>validate • execute • observe"]
    Core --> Orchestration["Team Orchestration<br/>manager • specialists • handoff compression • synthesis"]
    Core --> State["Memory + Knowledge<br/>SQLite memory • semantic knowledge search"]
    Core --> TimeContext["Time Context Resolver<br/>UTC • local timezone • locale-aware formatting"]

    Reasoning --> Routing
    Routing --> Policy["Policy Controls<br/>disabled tools • confirmation holds • restricted actions"]
    Policy --> ToolLoop
    Routing --> Providers

    ToolLoop --> Tools["Tools<br/>filesystem • web • datetime • memory • knowledge • gmail"]
    Tools --> State

    Entry["Manual CLI<br/>Heartbeat<br/>Webhook"] --> Core

    Core -. roadmap .-> Future["Future Layers<br/>observability • run history • dashboard • local LLMs • no-code builder • plugins"]
```

### What the architecture does

Orchgentic is not just an agent runner. It is the orchestration layer that decides how work should move through an agentic system.

At runtime, Orchgentic can:

- Load agents, teams, tools, policies, memory, and knowledge from YAML configuration.
- Use local reasoning to decide whether a task can avoid an external LLM call.
- Score confidence and escalate to the configured provider only when needed.
- Route tasks through deterministic tools, workflows, policies, or teams.
- Block disabled tools before LLM escalation or execution.
- Hold sensitive actions for confirmation.
- Coordinate team members and compress handoffs to reduce token usage.
- Produce debug output that explains routing, policy, tool, and team decisions.

### Current architecture focus

The v0.7.12 architecture focuses on:

- Local reasoning before provider calls
- Workflow-aware routing
- Event-aware routing
- Policy-aware escalation
- Tool safety and confirmation controls
- Team handoff compression
- Clean final team synthesis
- Debug visibility for developers

### Where the architecture is headed

The next major architecture layer is observability. Future versions are expected to add run history, routing traces, tool call traces, policy decision logs, team handoff traces, token savings estimates, and dashboard-ready event records.
