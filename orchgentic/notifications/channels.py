class BaseNotifier:
    name = "base"

    def notify(self, issue, context: dict | None = None):
        raise NotImplementedError

class ConsoleNotifier(BaseNotifier):
    name = "console"

    def notify(self, issue, context: dict | None = None):
        print(issue.to_text())

class EmailNotifier(BaseNotifier):
    name = "email"

    def notify(self, issue, context: dict | None = None):
        # Stub only. Real SMTP/SendGrid/Resend/SES support is deferred to v0.7.3+.
        return {
            "status": "deferred",
            "message": "Email notifications are scaffolded but not implemented yet.",
        }

class WebhookNotifier(BaseNotifier):
    name = "webhook"

    def notify(self, issue, context: dict | None = None):
        # Stub only. Real outbound webhook support is deferred to v0.7.3+.
        return {
            "status": "deferred",
            "message": "Webhook notifications are scaffolded but not implemented yet.",
        }
