from orchgentic.runtime.error_policy import ErrorSeverity
from orchgentic.notifications.channels import ConsoleNotifier, EmailNotifier, WebhookNotifier

class NotificationManager:
    def __init__(self):
        self.console = ConsoleNotifier()
        self.email = EmailNotifier()
        self.webhook = WebhookNotifier()

    def handle_issue(self, issue, context: dict | None = None):
        # For v0.7.2, always console/log surface.
        self.console.notify(issue, context=context)

        # Real email/webhook sending is intentionally deferred.
        # Severe and critical issues are routed to stubs to keep the interface stable.
        if issue.severity in [ErrorSeverity.SEVERE, ErrorSeverity.CRITICAL]:
            self.email.notify(issue, context=context)
            self.webhook.notify(issue, context=context)
