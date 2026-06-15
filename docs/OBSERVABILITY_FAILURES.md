# Failure Diagnostics

Orchgentic v0.8.0-alpha.6 adds failure-focused observability commands.

Use these commands when you want to quickly understand what failed without inspecting every run manually.

---

## Show Recent Failures

```bash
orch failures
```

Example:

```text
FAILURES
abc12345  tool     Bob                ToolExecutionError       gmail.send failed: Missing confirmation
def67890  agent    Bob                ProviderError            Groq request failed
```

---

## Limit Failures

```bash
orch failures --limit 10
```

---

## Filter Failures

```bash
orch failures --type tool
orch failures --type agent
orch failures --type team
orch failures --agent Bob
orch failures --team ContentTeam
```

---

## Group by Error Type

```bash
orch failures --group-by error_type
```

Example:

```text
FAILURES BY ERROR TYPE

ToolExecutionError: 3
  - abc12345 tool Bob - gmail.send failed: Missing confirmation

ProviderError: 1
  - def67890 agent Bob - Groq request failed
```

---

## JSON Output

```bash
orch failures --json
```

The JSON payload includes:

```text
failures
stats
```

---

## Inspect a Failed Run

```bash
orch run-info <run_id>
orch trace <run_id>
```

Use `run-info` for the full run summary and trace events.

Use `trace` when you want to filter specific components:

```bash
orch trace <run_id> --component tool
orch trace <run_id> --component provider
orch trace <run_id> --type tool.failed
orch trace <run_id> --type llm.failed
```

---

## Notes

- `orch failures` reads existing observability data.
- It does not execute or retry failed runs.
- Failure diagnostics depend on error information recorded by the runtime and trace events.
