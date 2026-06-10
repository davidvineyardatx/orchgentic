from typing import Any

class DeterministicFormatter:
    def format(self, formatter: str | None, result: Any) -> str:
        if not formatter:
            return str(result)

        data = self._data(result)

        if formatter == "datetime.local":
            return self._datetime(data)

        if formatter == "gmail.search":
            return self._gmail_search(data)

        if formatter == "gmail.read":
            return self._gmail_read(data)

        if formatter == "gmail.count":
            return self._gmail_count(data)

        if formatter == "gmail.subjects":
            return self._gmail_subjects(data)

        if formatter == "gmail.draft":
            return self._gmail_action(data, "Draft created")

        if formatter == "gmail.send":
            return self._gmail_action(data, "Email sent")

        return str(data)

    def _data(self, result: Any) -> Any:
        if hasattr(result, "data"):
            return result.data
        return result

    def _datetime(self, data: dict) -> str:
        if not isinstance(data, dict):
            return str(data)
        time_value = data.get("time", "")
        date = data.get("date", "")
        weekday = data.get("weekday", "")
        timezone = data.get("timezone", "")
        if time_value:
            return f"The current time is {time_value} ({timezone}). Today is {weekday}, {date}."
        return str(data)

    def _gmail_search(self, data: dict) -> str:
        messages = (data or {}).get("messages", []) if isinstance(data, dict) else []
        if not messages:
            return "No Gmail messages found."
        return f"Found {len(messages)} Gmail message(s)."

    def _gmail_count(self, data: dict) -> str:
        messages = (data or {}).get("messages", []) if isinstance(data, dict) else []
        return f"Found {len(messages)} Gmail message(s)."

    def _gmail_read(self, data: dict) -> str:
        if not isinstance(data, dict):
            return str(data)
        headers = data.get("headers", {}) or {}
        subject = headers.get("subject", "(no subject)")
        sender = headers.get("from", "(unknown sender)")
        date = headers.get("date", "")
        snippet = data.get("snippet", "")
        return f"From: {sender}\nSubject: {subject}\nDate: {date}\n\n{snippet}"

    def _gmail_subjects(self, data: dict) -> str:
        messages = data.get("messages", []) if isinstance(data, dict) else []
        if not messages:
            return "No Gmail messages found."

        lines = [f"Found {len(messages)} Gmail message(s):"]
        for idx, message in enumerate(messages, start=1):
            headers = message.get("headers", {}) or {}
            subject = headers.get("subject", "(no subject)")
            sender = headers.get("from", "(unknown sender)")
            lines.append(f"{idx}. {subject} — {sender}")
        return "\\n".join(lines)

    def _gmail_action(self, data: dict, label: str) -> str:
        if not isinstance(data, dict):
            return str(data)
        status = data.get("status", "")
        message_id = data.get("message_id") or data.get("draft_id")
        if message_id:
            return f"{label}. Status: {status}. ID: {message_id}"
        return f"{label}. Status: {status}."
