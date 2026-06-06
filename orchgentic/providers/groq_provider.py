import os

from groq import AsyncGroq
from dotenv import load_dotenv

from orchgentic.providers.base import BaseProvider
from orchgentic.core.exceptions import ProviderError

load_dotenv()


class GroqProvider(BaseProvider):
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ProviderError(
                "GROQ_API_KEY is not configured."
            )

        self.client = AsyncGroq(api_key=api_key)

    async def generate(self, messages):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            return response.choices[0].message.content or ""

        except Exception as exc:
            raise ProviderError(
                f"Groq provider failed: {exc}"
            ) from exc

    def supports_tools(self):
        return True

    def supports_json_mode(self):
        return True

    def supports_streaming(self):
        return True