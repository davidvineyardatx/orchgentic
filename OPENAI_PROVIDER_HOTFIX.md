# v0.7.3 OpenAI Provider Hotfix

This hotfix restores support for:

```yaml
provider:
  type: openai
  model: gpt-4o-mini
```

Required `.env` values:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Optional embedding model:

```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

The package still supports LM Studio:

```yaml
provider:
  type: lmstudio
  model: qwen3
```
