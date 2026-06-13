# Quickstart

This guide walks through getting Orchgentic running locally, inspecting the included example agent, running a task, checking routes, and running a team workflow.

## 1. Create and activate a virtual environment

From the project root:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Git Bash / macOS / Linux:

```bash
source .venv/bin/activate
```

## 2. Install Orchgentic in editable mode

```bash
python -m pip install -e ".[dev]"
```

The `dev` extra installs the test dependencies used by the project, including `pytest` and `pytest-asyncio`.

## 3. Configure environment variables

Create a `.env` file in the project root.

For Groq:

```env
GROQ_API_KEY=your_groq_api_key_here
```

For OpenAI, if using an OpenAI provider config:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Gmail tools require a Gmail OAuth connection. See [Tools and Policies](TOOLS_AND_POLICIES.md).

## 4. Validate the install

```bash
python -m pytest -q
```

Expected result should look similar to:

```text
53 passed
```

The exact number may change as tests are added.

## 5. List available agents

```bash
orch list-agents
```

Example output:

```text
Bob (bob) - General Assistant
Manager (manager) - Team Manager
Researcher (researcher) - Research Specialist
Writer (writer) - Writing Specialist
Reviewer (reviewer) - Review Specialist
```

## 6. Inspect Bob

```bash
orch inspect-agent Bob
```

This shows Bob's provider, capabilities, tools, and delegation settings.

## 7. Run Bob

```bash
orch run Bob --debug
```

When prompted:

```text
Task: what is the local time?
```

Expected behavior:

- Orchgentic routes directly to `datetime.local`.
- `external_llm_used` is `false`.
- The answer uses Bob's configured timezone and locale.

## 8. Preview routing without executing

```bash
orch judge-route "delete gmail message id abcdef123456" --agent Bob
```

Expected behavior with the sample Bob policy:

```text
policy.action: block
reason: Tool 'gmail.delete' is disabled by policy.
external_llm_allowed: false
```

## 9. Run a direct tool call

```bash
orch tool run datetime.local --agent Bob
```

For a Gmail send with confirmation:

```bash
orch tool run gmail.send \
  --agent Bob \
  --arg to=studio@example.com \
  --arg subject="Hello from Orchgentic" \
  --arg body="This is a confirmed tool execution." \
  --arg confirm=true
```

## 10. Run ContentTeam

```bash
orch run-team contentteam --debug
```

When prompted:

```text
Research AI is changing how customers shop and create an Executive Summary
```

Expected behavior:

- Manager assigns work.
- Researcher provides findings.
- Writer drafts the executive summary.
- Reviewer gives improvement guidance.
- Orchgentic synthesizes a final answer.
- Debug output shows compressed team handoffs instead of nested run transcripts.
