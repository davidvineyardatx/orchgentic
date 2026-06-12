from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

class TimeContextError(Exception):
    pass

class TimeContextResolver:
    def resolve_timezone(
        self,
        runtime_context: dict | None = None,
        trigger_config=None,
        user_context: dict | None = None,
        workspace_config=None,
        agent_config=None,
    ) -> str:
        if runtime_context and runtime_context.get("timezone"):
            return runtime_context["timezone"]

        if trigger_config and getattr(trigger_config, "timezone", None):
            return trigger_config.timezone

        if user_context and user_context.get("timezone"):
            return user_context["timezone"]

        if workspace_config and getattr(workspace_config, "timezone", None):
            return workspace_config.timezone

        if agent_config and getattr(agent_config, "timezone", None):
            return agent_config.timezone

        return "UTC"

    def resolve_locale(
        self,
        runtime_context: dict | None = None,
        user_context: dict | None = None,
        workspace_config=None,
        agent_config=None,
    ) -> str:
        if runtime_context and runtime_context.get("locale"):
            return runtime_context["locale"]

        if user_context and user_context.get("locale"):
            return user_context["locale"]

        if workspace_config and getattr(workspace_config, "locale", None):
            return workspace_config.locale

        if agent_config and getattr(agent_config, "locale", None):
            return agent_config.locale

        return "en-US"

    def now_local(self, timezone_name: str, locale: str = "en-US") -> dict:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise TimeContextError(
                f"Unknown timezone '{timezone_name}'. Use an IANA timezone like 'America/Chicago'."
            ) from exc

        now = datetime.now(tz)

        return {
            "datetime": now.isoformat(),
            "timezone": timezone_name,
            "locale": locale,
            "weekday": now.strftime("%A"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "time_12h": now.strftime("%I:%M:%S %p").lstrip("0"),
            "utc_offset": now.strftime("%z"),
        }

    def now_utc(self) -> dict:
        now = datetime.now(timezone.utc)

        return {
            "datetime": now.isoformat(),
            "timezone": "UTC",
            "weekday": now.strftime("%A"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "time_12h": now.strftime("%I:%M:%S %p").lstrip("0"),
            "utc_offset": "+0000",
        }
