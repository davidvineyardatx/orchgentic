# v0.7.12-alpha Intent Precedence Hotfix

This hotfix resolves Gmail routing ambiguity where object phrases like `message id` caused destructive actions to also be interpreted as read actions.

## Fixes

- `delete gmail message id ...` now produces:
  - `local_reasoner.intent: gmail_delete`
  - `local_reasoner.signals.simple_intents: ["gmail_delete"]`
  - `workflow.required_tools: ["gmail.delete"]`
- Action verbs now take precedence over object nouns:
  - delete/trash/remove + gmail/email/message -> `gmail.delete`
  - send + email/gmail/message/address -> `gmail.send`
  - reply/respond + email/gmail/message -> `gmail.reply`
  - draft + email/gmail/reply/message -> `gmail.draft`

## Validation

```bash
python -m pytest -q
# 39 passed
```
