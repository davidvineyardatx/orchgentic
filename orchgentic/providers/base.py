from abc import ABC, abstractmethod
from typing import Any
import hashlib
import math

class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, messages):
        raise NotImplementedError

    async def generate_structured(self, messages, schema=None):
        return await self.generate(messages)

    async def generate_tool_decision(self, messages, tools: list[dict[str, Any]], max_iterations: int = 4) -> str:
        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(
                f"- {tool.get('name')}: {tool.get('description')} schema={tool.get('input_schema', {})}"
            )

        tool_prompt = (
            "You are operating inside Orchgentic's tool runtime.\n"
            "You may call a tool if useful.\nFor user-facing local date/time/day questions, prefer datetime.local when available. Use datetime.now only when UTC is specifically requested.\n\n"
            "IMPORTANT OUTPUT RULES:\n"
            "1. If calling a tool, output only one JSON object and no prose:\n"
            '{"action":"tool","tool":"tool.name","arguments":{}}\n'
            "2. If ready to answer, output only one JSON object and no prose:\n"
            '{"action":"final","answer":"your answer"}\n'
            "3. Do not wrap JSON in markdown unless unavoidable.\n\n"
            "Available tools:\n" + "\n".join(tool_descriptions)
        )

        return await self.generate([
            {"role": "system", "content": tool_prompt},
            *messages,
        ])

    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [byte / 255.0 for byte in digest]
        while len(values) < 64:
            values.extend(values)
        vector = values[:64]
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def supports_tools(self):
        return False

    def supports_json_mode(self):
        return False

    def supports_streaming(self):
        return False
