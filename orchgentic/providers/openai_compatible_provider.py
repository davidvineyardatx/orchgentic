import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from orchgentic.core.exceptions import ProviderError
from orchgentic.providers.base import BaseProvider

load_dotenv()


class OpenAICompatibleProvider(BaseProvider):
    """Provider adapter for OpenAI-compatible chat completion APIs.

    This is used for providers that expose the /v1/chat/completions contract,
    including xAI and local OpenAI-compatible endpoints.
    """

    def __init__(
        self,
        *,
        provider_name: str,
        model: str,
        api_key_env: str,
        base_url: str | None = None,
        base_url_env: str | None = None,
        default_api_key: str | None = None,
    ):
        self.provider_name = provider_name
        self.model = model
        self.api_key_env = api_key_env
        self.base_url = base_url or (os.getenv(base_url_env) if base_url_env else None)

        api_key = os.getenv(api_key_env) or default_api_key
        if not api_key:
            raise ProviderError(
                f"{provider_name} provider requires {api_key_env} in environment or .env file."
            )

        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = AsyncOpenAI(**client_kwargs)

    async def generate(self, messages):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            location = f" at {self.base_url}" if self.base_url else ""
            raise ProviderError(f"{self.provider_name} provider failed{location}: {exc}") from exc

    def supports_tools(self):
        return True

    def supports_json_mode(self):
        return True

    def supports_streaming(self):
        return True
