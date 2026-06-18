# Observability Dashboard

The Orchgentic observability dashboard is a local static HTML dashboard generated from local run history and trace data.

Generate:

```bash
orch dashboard
```

Open the existing dashboard:

```bash
orch dashboard --open
```

Generate with a larger run set:

```bash
orch dashboard --limit 500
```

Generate with a team filter:

```bash
orch dashboard --team ContentTeam
```

## Panel Order

The dashboard prioritizes triage first:

1. Recent Failures
2. Recent Runs
3. Token Intelligence

Each major section is collapsible.

## Token Intelligence

The Token Intelligence panel shows:

- local/deterministic share
- external LLM share
- token work total
- direct bypasses
- deterministic routes
- local reasoning events
- LLM events
- estimated tokens saved
- local LLM candidate tokens
- premium candidate tokens
- top savings run
- token proof events

## Filter Behavior

Dashboard filters apply consistently to Recent Runs and Token Intelligence.

When a user filters by status, type, team, agent, or search text, Token Intelligence recalculates from the filtered run set.

## Token Proof Rows

Token proof rows include:

- Run
- Proof Event
- Component
- Meaning
- Tokens Used
- Saved
- Source
- Execution Tier
- Optimization
- Reason

Reason text is shown on its own row so long explanations remain readable.
