# Orchgentic v0.7.12-alpha Team Synthesis Structured Output Hotfix

## Fixes

- Unwraps structured final JSON envelopes such as `{\"action\":\"final\",\"answer\":\"...\"}` during team handoff and final rendering.
- Ensures `TEAM FINAL` renders as plain text instead of raw JSON.
- Ensures Writer/Reviewer structured outputs are normalized before being passed into later team steps.
- Tightens source-label phrasing without malformed sentence splices.
- Preserves AR/VR parentheticals while avoiding unsupported source-verification language.
- Updates synthesis prompt to explicitly request plain text, not JSON.

## Validation

```text
53 passed
```
