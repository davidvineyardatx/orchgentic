# Providers

Orchgentic providers define **who answers when an LLM is needed**.

Routing, policy, and reasoning decide **whether** a provider should be used.

```text
provider = who answers when an LLM is needed
reasoning / routing / policy = whether the provider should be used
```

## Supported Provider Types

```text
openai
xai
anthropic
claude
groq
lmstudio
lm-studio
openai-compatible
```

## Environment Variables

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

XAI_API_KEY=
XAI_MODEL=grok-3-mini
XAI_BASE_URL=https://api.x.ai/v1

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_MAX_TOKENS=1024

GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

LMSTUDIO_ENDPOINT=http://localhost:1234/v1
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=qwen3
LMSTUDIO_API_KEY=lm-studio

OPENAI_COMPATIBLE_BASE_URL=
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_API_KEY_ENV=OPENAI_COMPATIBLE_API_KEY
```

## OpenAI

```yaml
provider:
  type: openai
  model: gpt-4.1-mini
```

Requires:

```env
OPENAI_API_KEY=
```

## xAI

xAI exposes an OpenAI-compatible chat completions API, so Orchgentic uses the OpenAI-compatible adapter for xAI.

```yaml
provider:
  type: xai
  model: grok-3-mini
```

Requires:

```env
XAI_API_KEY=
```

Optional:

```env
XAI_BASE_URL=https://api.x.ai/v1
```

## Anthropic Claude

```yaml
provider:
  type: anthropic
  model: claude-3-5-sonnet-latest
```

or:

```yaml
provider:
  type: claude
  model: claude-3-5-sonnet-latest
```

Requires:

```env
ANTHROPIC_API_KEY=
```

Anthropic support uses the optional `anthropic` package. Install it with:

```bash
pip install anthropic
```

or install the optional provider dependencies if your package manager supports extras:

```bash
pip install -e ".[providers]"
```

## Groq

```yaml
provider:
  type: groq
  model: llama-3.3-70b-versatile
```

Requires:

```env
GROQ_API_KEY=
```

## LM Studio

```yaml
provider:
  type: lmstudio
  model: qwen3
```

Requires LM Studio running an OpenAI-compatible local server.

Common default:

```env
LMSTUDIO_ENDPOINT=http://localhost:1234/v1
LMSTUDIO_MODEL=qwen3
```

## Generic OpenAI-Compatible Provider

Use this when a provider exposes `/v1/chat/completions` with OpenAI-compatible request/response shape.

```yaml
provider:
  type: openai-compatible
  model: your-model-name
```

Requires:

```env
OPENAI_COMPATIBLE_BASE_URL=https://provider.example.com/v1
OPENAI_COMPATIBLE_API_KEY=your_key
```

Advanced key env override:

```env
OPENAI_COMPATIBLE_API_KEY_ENV=MY_PROVIDER_API_KEY
MY_PROVIDER_API_KEY=your_key
```

## Adding a Provider

The preferred path is:

1. If the provider is OpenAI-compatible, use `OpenAICompatibleProvider`.
2. Add an alias in `orchgentic/providers/factory.py`.
3. Add provider docs.
4. Add a factory test.
5. Avoid changing orchestration logic.

Provider adapters should stay thin. They should translate Orchgentic's internal `messages` format into provider-specific API calls and return plain text.

## Design Rules

- Provider adapters should not decide routing.
- Provider adapters should not decide whether a task should use an LLM.
- Provider adapters should raise clear configuration errors when credentials are missing.
- Provider onboarding should be one adapter or one factory entry whenever possible.
- Token Intelligence should distinguish configured provider from provider actually used.

## Official API Notes

OpenAI provides a Python SDK and current API docs for text generation. xAI documents OpenAI-compatible REST APIs under `/v1/chat/completions`. Anthropic provides an official Python SDK for Claude and a Messages API. See each provider's official docs for current model names and SDK details.
