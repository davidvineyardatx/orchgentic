# Orchgentic v0.7.11-alpha Hotfix — Tool Prefetch Before LLM

This hotfix adds the missing bridge between deterministic routing and LLM fallback.

## Fixed

Requests such as:

```text
read Gmail message id 19eada2f053bc231 and summarize message
```

now follow this flow:

```text
1. Deterministic router declines because summarization requires reasoning
2. Tool prefetch planner detects explicit gmail.read requirement
3. gmail.read executes using the agent's configured Gmail connection
4. fetched message content is injected into the LLM task context
5. LLM summarizes actual fetched content instead of guessing
```

## Config

Enabled in:

```text
config/router.yaml
```

```yaml
deterministic_router:
  behavior:
    allow_tool_prefetch_before_llm: true
```

## Validate

```bash
orch memory clear --agent Bob --yes
orch run Bob --debug
```

Task:

```text
read Gmail message id 19eada2f053bc231 and summarize message
```

Expected debug output includes:

```text
TOOL_PREFETCH
PREFETCH_TOOLS
gmail.read
```
