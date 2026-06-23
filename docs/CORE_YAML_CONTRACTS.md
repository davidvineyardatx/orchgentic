# Core YAML Contracts



## Provider YAML Examples

OpenAI:

```yaml
provider:
  type: openai
  model: gpt-4.1-mini
```

xAI:

```yaml
provider:
  type: xai
  model: grok-3-mini
```

Anthropic Claude:

```yaml
provider:
  type: anthropic
  model: claude-3-5-sonnet-latest
```

Groq:

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

LM Studio:

```yaml
provider:
  type: lmstudio
  model: qwen3
```

Generic OpenAI-compatible provider:

```yaml
provider:
  type: openai-compatible
  model: your-model-name
```

See `PROVIDERS.md` for environment variables and onboarding details.


## Execution Policy YAML

Agents and teams may include an optional execution policy.

```yaml
execution_policy:
  enabled: true
  default_mode: external_llm_when_needed

  deterministic:
    enabled: true

  local_reasoning:
    enabled: true

  local_llm:
    enabled: false
    eligible_for:
      - classification
      - routing
      - summarization
      - review

  external_llm:
    enabled: true
    require_for:
      - complex_generation
      - high_uncertainty_reasoning

  premium_model:
    enabled: true
    require_for:
      - final_synthesis
      - executive_output
      - high_quality_final
```

Execution policy does not choose the provider. It defines whether deterministic, local reasoning, local LLM, external LLM, or premium-model work should be preferred or classified.

See `EXECUTION_POLICY.md`.
