import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from orchgentic.providers.base import BaseProvider
from orchgentic.core.exceptions import ProviderError

load_dotenv()

class OpenAIProvider(BaseProvider):
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is not set in environment or .env file.")
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, messages):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise ProviderError(f"OpenAI provider failed: {exc}") from exc

    async def embed(self, text: str) -> list[float]:
        # Uses OpenAI embeddings when OPENAI_EMBEDDING_MODEL is provided.
        # Falls back to BaseProvider deterministic dev embeddings otherwise.
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
        if not embedding_model:
            return await super().embed(text)

        try:
            response = await self.client.embeddings.create(
                model=embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as exc:
            raise ProviderError(f"OpenAI embedding failed: {exc}") from exc

    def supports_tools(self):
        return True

    def supports_json_mode(self):
        return True

    def supports_streaming(self):
        return True
