# v0.7.12-alpha Team Handoff Compression Hotfix

This hotfix tightens team synthesis quality and reduces token usage during multi-agent team runs.

## Changes

- Team handoffs now forward only each agent's `ANSWER` content.
- Debug-only sections such as `RUN ID`, `PLAN`, `REFLECTION`, `MEMORY`, `KNOWLEDGE`, and `TOOLS` are stripped before passing context to the next team member.
- Team outputs returned in debug mode are compacted to specialist answers instead of full nested transcripts.
- Final team synthesis extracts and sanitizes only the final `ANSWER` block when debug mode is enabled.
- Synthesis instructions now prohibit adding new examples, company names, reports, links, webinars, ebooks, citations, or resources unless they appeared in current team outputs.
- Source labels without URLs are treated as labels, not verified citations.

## Validation

```text
47 passed
```
