from orchgentic.config.schemas import AgentConfig, TeamConfig
from orchgentic.runtime.execution_policy import normalize_execution_policy, normalize_execution_tiers


def test_default_execution_tiers_normalize_to_stable_shape():
    agent = AgentConfig(id="bob", name="Bob")
    tiers = normalize_execution_tiers(agent)

    assert tiers.deterministic_enabled is True
    assert tiers.local_reasoning_enabled is True
    assert tiers.local_llm_enabled is False
    assert tiers.local_llm_provider == "lmstudio"
    assert tiers.local_llm_model is None
    assert "routing" in tiers.local_llm_eligible_for
    assert tiers.external_llm_enabled is True
    assert tiers.premium_model_enabled is True


def test_execution_tiers_alias_takes_precedence_over_execution_policy():
    agent = AgentConfig(
        id="bob",
        name="Bob",
        execution_policy={
            "local_llm": {
                "enabled": False,
                "provider": "lmstudio",
                "model": "ignored",
            }
        },
        execution_tiers={
            "local_llm": {
                "enabled": True,
                "provider": "ollama",
                "model": "llama3.1",
                "eligible_for": ["routing"],
            }
        },
    )

    tiers = normalize_execution_tiers(agent)

    assert tiers.local_llm_enabled is True
    assert tiers.local_llm_provider == "ollama"
    assert tiers.local_llm_model == "llama3.1"
    assert tiers.local_llm_eligible_for == ("routing",)


def test_execution_policy_normalization_reads_provider_and_model():
    tiers = normalize_execution_policy(
        {
            "local_llm": {
                "enabled": True,
                "provider": "lmstudio",
                "model": "qwen3",
                "eligible_for": ["review"],
            }
        }
    )

    assert tiers.local_llm_enabled is True
    assert tiers.local_llm_provider == "lmstudio"
    assert tiers.local_llm_model == "qwen3"
    assert tiers.local_llm_eligible_for == ("review",)


def test_team_config_accepts_execution_tiers_alias():
    team = TeamConfig(
        name="ContentTeam",
        orchestrator="Manager",
        execution_tiers={
            "local_llm": {
                "enabled": True,
                "provider": "ollama",
                "model": "llama3.1",
            }
        },
    )

    tiers = normalize_execution_tiers(team)

    assert tiers.local_llm_enabled is True
    assert tiers.local_llm_provider == "ollama"
    assert tiers.local_llm_model == "llama3.1"
