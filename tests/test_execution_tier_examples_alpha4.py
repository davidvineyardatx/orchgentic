from pathlib import Path


def test_execution_tier_examples_file_exists():
    path = Path("docs/examples/execution_tiers.yaml")

    assert path.exists()


def test_execution_tier_examples_include_supported_readiness_profiles():
    text = Path("docs/examples/execution_tiers.yaml").read_text(encoding="utf-8")

    assert "default_disabled:" in text
    assert "lmstudio_ready:" in text
    assert "ollama_ready:" in text
    assert "openai_compatible_ready:" in text
    assert "provider: lmstudio" in text
    assert "provider: ollama" in text
    assert "provider: openai_compatible" in text


def test_execution_tier_examples_state_no_runtime_behavior_change():
    text = Path("docs/examples/execution_tiers.yaml").read_text(encoding="utf-8")
    docs = Path("docs/EXECUTION_POLICY.md").read_text(encoding="utf-8")

    assert "do not enable local LLM execution" in text
    assert "do not change routing behavior" in docs
