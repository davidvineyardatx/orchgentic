# v0.7.2 Stabilization Hotfix

## Added

- Capability preflight checks
- Missing-tool detection
- Fail-fast runtime protection before LLM calls
- Severity-based runtime issues
- Notification abstraction
- Console notifier
- Email notifier stub
- Webhook notifier stub
- `preflight-agent` CLI command
- `preflight-team` CLI command
- `--no-preflight` escape hatch for testing

## Example

```bash
orchgentic preflight-team ContentTeam --task "Research the latest AI orchestration tools online"
```

If `web.request` is missing, Orchgentic will fail before invoking the LLM.

## Deferred

Real email notification providers are intentionally deferred to v0.7.3+.

Planned providers:

- SMTP
- SendGrid
- Resend
- AWS SES
- Slack
- Discord
- External webhook notifications
```
