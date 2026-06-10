# Orchgentic v0.7.10-alpha — Deterministic Operational Routing

This release expands v0.7.9 deterministic single-tool routing into more capable deterministic operational routing.

## Added

- deterministic Gmail argument extraction
- simple deterministic multi-tool chaining
- deterministic formatting layer
- route telemetry logging to `logs/routes.jsonl`

## Examples

### Natural Gmail Query Extraction

```text
search unread Gmail from Google from the last 30 days
```

Routes to:

```text
gmail.search(query="is:unread from:google newer_than:30d")
```

### Count Gmail Results

```text
count unread Gmail from the last 7 days
```

Routes to:

```text
gmail.search(query="is:unread newer_than:7d")
```

Formats response without external LLM.

### Subject Line Extraction

```text
show subject lines for unread Gmail from the last 7 days
```

Routes to:

```text
gmail.search
→ gmail.read for each result
→ deterministic subject-line formatter
```

### Time Formatting

```text
what time is it?
```

Routes to:

```text
datetime.local
→ deterministic formatter
```

## Logs

Route telemetry is appended to:

```text
logs/routes.jsonl
```

Example fields:

- `route_type`
- `external_llm_used`
- `selected_tool`
- `confidence`
- `reason`
- `estimated_external_tokens_saved`

## Philosophy

The runtime should resolve deterministic operational requests without using external LLM tokens whenever safe and possible.
