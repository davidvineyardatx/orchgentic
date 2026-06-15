# Observability Retention and Cleanup

Orchgentic stores run history and trace events in a local SQLite observability database.

As run history grows, you can inspect, prune, or delete observability records.

---

## Show Run Statistics

```bash
orch runs-stats
```

Example output:

```text
RUN STATS
total_runs: 42
external_llm_runs: 8
total_tokens: 12048
estimated_tokens_saved: 7340

by_status:
  completed: 39
  failed: 2
  hold_for_confirmation: 1

by_type:
  agent: 21
  tool: 17
  team: 4
```

JSON output:

```bash
orch runs-stats --json
```

---

## Preview Cleanup

`runs-prune` defaults to dry-run mode.

```bash
orch runs-prune --older-than 30d --dry-run
```

Other filters:

```bash
orch runs-prune --status failed --dry-run
orch runs-prune --type tool --older-than 7d --dry-run
orch runs-prune --agent Bob --older-than 14d --dry-run
orch runs-prune --team ContentTeam --older-than 14d --dry-run
```

Supported retention windows:

```text
12h
30d
2w
```

---

## Delete Matching Runs

Deletion requires both:

```text
--no-dry-run
--confirm
```

Example:

```bash
orch runs-prune --older-than 30d --no-dry-run --confirm
```

Delete failed runs:

```bash
orch runs-prune --status failed --no-dry-run --confirm
```

---

## Delete One Run

```bash
orch run-delete <run_id> --confirm
```

Deleting a run also deletes its associated trace events.

---

## Safety Notes

- Always run with `--dry-run` first.
- `runs-prune` will refuse deletion without `--confirm`.
- `run-delete` will refuse deletion without `--confirm`.
- Deletion is local to the observability database.
