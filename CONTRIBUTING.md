# Contributing to Orchgentic

Thank you for your interest in contributing.

Orchgentic is currently in developer preview. The highest-value contributions are:

- bug reports
- reproducible test cases
- documentation improvements
- provider adapters
- tool plugins
- runtime reliability improvements
- examples and tutorials

## Development setup

```bash
pip install -e .[dev]
orch init
pytest
```

## Contribution guidelines

- Keep the runtime modular.
- Prefer clear YAML configuration.
- Avoid hardcoded provider assumptions.
- Add tests for runtime behavior changes.
- Do not commit secrets or local runtime databases.
