import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from orchgentic.core.exceptions import ProviderError
from .base import BaseProvider

load_dotenv()

class LMStudioProvider(BaseProvider):
    def __init__(self, model=None, endpoint=None):
        self.endpoint = endpoint or os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")
        self.model = model or os.getenv("LMSTUDIO_MODEL", "qwen3")
        self.client = AsyncOpenAI(base_url=self.endpoint, api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"))

    async def generate(self, messages):
        try:
            res = await self.client.chat.completions.create(model=self.model, messages=messages)
            return res.choices[0].message.content or ""
        except Exception as exc:
            raise ProviderError(f"LM Studio failed at {self.endpoint}: {exc}") from exc

    def supports_tools(self): return True
    def supports_streaming(self): return True
