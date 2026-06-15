# Orchgentic v0.7.12-alpha Team Synthesis Quality Hotfix

This hotfix tightens team synthesis behavior after testing ContentTeam with a research + executive summary task.

## Fixes

- Prevents unrelated historical memory from contaminating team orchestration prompts.
- Strengthens team member prompts so researchers provide actual findings rather than status-only summaries.
- Adds synthesis guardrails that prefer current team outputs over prior memory.
- Prevents placeholder links/resources from appearing in final team responses.
- Adds post-synthesis cleanup for obvious placeholder resource sections and fake resource bullets.
- Preserves real resource sections when they include actual URLs.

## Design rule

Team final synthesis should be grounded in the current team run:

```text
current team outputs > directly relevant knowledge > historical memory
```

Historical memory is disabled by default for team role prompts and final synthesis because the team runner already provides explicit shared context.

## Validation

```text
44 passed
```
