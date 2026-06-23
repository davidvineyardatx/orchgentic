import os

from orchgentic.core.exceptions import ConfigurationError
from orchgentic.providers.anthropic_provider import AnthropicProvider
from orchgentic.providers.groq_provider import GroqProvider
from orchgentic.providers.openai_compatible_provider import OpenAICompatibleProvider
from orchgentic.providers.openai_provider import OpenAIProvider

SUPPORTED_PROVIDERS = {
    "openai": "OpenAI API using OPENAI_API_KEY",
    "xai": "xAI OpenAI-compatible API using XAI_API_KEY",
    "anthropic": "Anthropic Claude API using ANTHROPIC_API_KEY",
    "claude": "Alias for anthropic",
    "groq": "Groq API using GROQ_API_KEY",
    "lmstudio": "LM Studio local OpenAI-compatible API",
    "lm-studio": "Alias for lmstudio",
    "openai-compatible": "Generic OpenAI-compatible API",
}


def supported_provider_names() -> list[str]:
    return sorted(SUPPORTED_PROVIDERS.keys())


def create_provider(config):
    provider_type = (config.type or "").lower().strip()
    model = config.model

    if provider_type == "openai":
        return OpenAIProvider(model=model)

    if provider_type == "xai":
        return OpenAICompatibleProvider(
            provider_name="xAI",
            model=model or os.getenv("XAI_MODEL", "grok-3-mini"),
            api_key_env="XAI_API_KEY",
            base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
        )

    if provider_type in ["anthropic", "claude"]:
        return AnthropicProvider(model=model)

    if provider_type == "groq":
        return GroqProvider(model=model)

    if provider_type in ["lmstudio", "lm-studio"]:
        return OpenAICompatibleProvider(
            provider_name="LM Studio",
            model=model or os.getenv("LMSTUDIO_MODEL", "qwen3"),
            api_key_env="LMSTUDIO_API_KEY",
            default_api_key="lm-studio",
            base_url=os.getenv(
                "LMSTUDIO_ENDPOINT",
                os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            ),
        )

    if provider_type == "openai-compatible":
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        api_key_env = os.getenv("OPENAI_COMPATIBLE_API_KEY_ENV", "OPENAI_COMPATIBLE_API_KEY")
        if not base_url:
            raise ConfigurationError(
                "Provider type 'openai-compatible' requires OPENAI_COMPATIBLE_BASE_URL."
            )
        return OpenAICompatibleProvider(
            provider_name="OpenAI-compatible",
            model=model,
            api_key_env=api_key_env,
            base_url=base_url,
        )

    supported = ", ".join(supported_provider_names())
    raise ConfigurationError(
        f"Unsupported provider: {config.type}. Supported providers: {supported}."
    )
