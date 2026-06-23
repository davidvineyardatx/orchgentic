import os

import pytest

from orchgentic.config.schemas import ProviderConfig
from orchgentic.core.exceptions import ConfigurationError, ProviderError
from orchgentic.providers.factory import create_provider, supported_provider_names
from orchgentic.providers.openai_compatible_provider import OpenAICompatibleProvider


def test_supported_provider_names_include_onboarding_targets():
    names = supported_provider_names()

    assert "openai" in names
    assert "xai" in names
    assert "anthropic" in names
    assert "claude" in names
    assert "groq" in names
    assert "lmstudio" in names
    assert "openai-compatible" in names


def test_xai_uses_openai_compatible_provider(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    provider = create_provider(ProviderConfig(type="xai", model="grok-test"))

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.provider_name == "xAI"
    assert provider.model == "grok-test"
    assert provider.base_url == "https://api.x.ai/v1"


def test_lmstudio_uses_openai_compatible_provider_without_real_key(monkeypatch):
    monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
    monkeypatch.setenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")

    provider = create_provider(ProviderConfig(type="lmstudio", model="local-model"))

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.provider_name == "LM Studio"
    assert provider.model == "local-model"
    assert provider.base_url == "http://localhost:1234/v1"


def test_openai_compatible_requires_base_url(monkeypatch):
    monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)

    with pytest.raises(ConfigurationError) as exc:
        create_provider(ProviderConfig(type="openai-compatible", model="model"))

    assert "OPENAI_COMPATIBLE_BASE_URL" in str(exc.value)


def test_unknown_provider_error_lists_supported_providers():
    with pytest.raises(ConfigurationError) as exc:
        create_provider(ProviderConfig(type="unknown-provider", model="model"))

    message = str(exc.value)
    assert "Unsupported provider: unknown-provider" in message
    assert "openai" in message
    assert "xai" in message
    assert "anthropic" in message


def test_anthropic_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ProviderError) as exc:
        create_provider(ProviderConfig(type="anthropic", model="claude-test"))

    assert "ANTHROPIC_API_KEY" in str(exc.value)
