import os

from dotenv import load_dotenv

from orchgentic.core.exceptions import ProviderError
from orchgentic.providers.base import BaseProvider

load_dotenv()


class AnthropicProvider(BaseProvider):
    """Provider adapter for Anthropic Claude models.

    The anthropic package is an optional dependency. It is imported lazily so
    Orchgentic can still run with OpenAI-compatible providers when Anthropic is
    not installed.
    """

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderError("Anthropic provider requires ANTHROPIC_API_KEY in environment or .env file.")

        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise ProviderError(
                "Anthropic provider requires the optional dependency 'anthropic'. "
                "Install it with: pip install anthropic"
            ) from exc

        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(self, messages):
        system_parts = []
        converted_messages = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                if content:
                    system_parts.append(str(content))
                continue

            if role == "assistant":
                converted_role = "assistant"
            else:
                converted_role = "user"

            converted_messages.append(
                {
                    "role": converted_role,
                    "content": str(content),
                }
            )

        if not converted_messages:
            converted_messages.append({"role": "user", "content": ""})

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "1024")),
                system="\n\n".join(system_parts) if system_parts else None,
                messages=converted_messages,
            )

            parts = []
            for block in response.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "\n".join(parts)

        except Exception as exc:
            raise ProviderError(f"Anthropic provider failed: {exc}") from exc

    def supports_tools(self):
        return False

    def supports_json_mode(self):
        return False

    def supports_streaming(self):
        return False
