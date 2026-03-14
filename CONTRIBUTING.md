# Contributing to the AI-Powered Medical Form Assistant

First off, thank you for considering contributing! Projects like this thrive on community collaboration, especially in the intersection of AI and healthcare.

## Contents

- [Contributing to the AI-Powered Medical Form Assistant](#contributing-to-the-ai-powered-medical-form-assistant)
  - [Contents](#contents)
  - [Development Workflow](#development-workflow)
    - [1. Fork](#1-fork)
    - [2. Dependencies](#2-dependencies)
    - [3. Local Testing](#3-local-testing)
  - [Coding Standards](#coding-standards)
  - [Docker Guidelines](#docker-guidelines)
  - [💬 Pull Request Process](#-pull-request-process)

## Development Workflow

We use **uv** for a fast dependency management and **Docker** for environment parity.

### 1. Fork

Fork the repo and create your branch from `main`.

### 2. Dependencies

Install dependencies:

```bash
uv sync
```

### 3. Local Testing

- Run `python src/build_database.py` to test RAG ingestion.
- Run `streamlit run src/app.py` to test the UI.

## Coding Standards

- **Prompt Engineering**: All system prompts live in `src/prompts.py`. Do not hardcode Lithuanian text in the backend logic.
- **LLM Independence**: Always use `LiteLLM` wrappers. Avoid provider-specific SDKs (like `openai-python`) to ensure we can switch models easily.
- **Vector Search**: When adding new codes to the CSVs, include a `symptoms` column to improve semantic retrieval.

## Docker Guidelines

Before submitting a Pull Request, ensure the build passes:

```bash
docker compose build
```

The application must run as a non-root user (`appuser`). Do not change the security context in the `Dockerfile` without a security review.

## 💬 Pull Request Process

1. Update the `README.md` if you changed the RAG logic or environment variables.
2. Ensure any new dependencies are added via `uv add <package>`.
3. Submit your PR with a clear description of the "Problem" and your "AI Solution."

---

*By contributing, you agree that your contributions will be licensed under the project's MIT License.*
