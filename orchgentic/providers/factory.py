from orchgentic.core.exceptions import ConfigurationError
from orchgentic.providers.groq_provider import GroqProvider
from orchgentic.providers.openai_provider import OpenAIProvider

def create_provider(config):
    provider_type = config.type.lower()

    if provider_type in ["openai", "openai-compatible"]:
        return OpenAIProvider(model=config.model)
    
    if provider_type in ["groq"]:
        return GroqProvider(model=config.model)

    raise ConfigurationError(f"Unsupported provider: {config.type}")
