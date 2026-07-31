# Development Guide

[Simplified Chinese](/docs/DEVELOPMENT.zh.md)\|[English](/docs/DEVELOPMENT.en.md)\|[Japanese](/docs/DEVELOPMENT.ja.md)\|[Traditional Chinese](/docs/DEVELOPMENT.zh-TW.md)

This document is intended for project developers and contributors and introduces the development environment, code structure, quality inspection and testing methods. For project background, installation, operation, and configuration instructions, see[README](README.zh.md)。

## 🛠️ Technology stack

-   **language**:[Python](https://www.python.org/)>= 3.14
-   **Package manager**:[uv](https://github.com/astral-sh/uv)
-   **API framework**:[speedy](https://fastapi.tiangolo.com/)
-   **Web server**:[Uvicorn](https://www.uvicorn.org/)
-   **agent framework**:[deepagents](https://github.com/zongxuheng/deepagents)(Based on LangGraph/LangChain)
-   **LLM provider**:[To be](https://ollama.com/)、[HuggingFace](https://huggingface.co/)and[Anthropic](https://www.anthropic.com/)
-   **code execution**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)QuickJS middleware provided
-   **Terminal interaction**:`asyncclick`、`prompt-toolkit`and`Rich`
-   **Configuration management**:[Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
-   **Code quality**:[Ruff](https://github.com/astral-sh/ruff)、`pre-commit`and mandatory type hints
-   **Testing and Coverage**:`pytest`、`coverage`

## ⚙️ CI/CD

The project integrates GitHub Actions workflows, including:

-   **Testing and Coverage**: Automatically run tests and check code coverage.
-   **Document translation**: automatically`README.zh.md`and`DEVELOPMENT.zh.md`Translated into English, Japanese and Traditional Chinese.
-   **Code specifications**: Automatic execution`ruff`Check and format to ensure consistent code style.
-   **CI process optimization**: Trigger builds based on relevant code or configuration changes to reduce unnecessary build tasks.

## 📜 Development script

Synchronize dependencies and create a virtual environment:

```bash
uv sync
```

Check and format the code:

```bash
uv run ruff check . --fix
uv run ruff format .
```

Run manually`pre-commit`hook:

```bash
uv run pre-commit run --all-files
```

## 📂 Project structure

-   `src/main.py`: The main entry point of the Rainy API service.
-   `src/fragile/`: Asynchronous command line client containing interactive sessions, slash commands, display and input handling.
-   `src/tomorrow/`: Core agent that implements graph, model, backend, checkpoint, storage and life cycle management.
-   `src/rainy/`: API service to implement application life cycle, chat interface, health check and middleware.
-   `tests/`: Test directory, structure and`src`Be consistent.
-   `docs/`: Multilingual documentation.
-   `pyproject.toml`: Project metadata, dependencies, and tool configuration.
-   `langgraph.json`:`langgraph-cli`graph and environment configuration.
-   `uv.lock`: Lock dependency versions.

## 🧪 Test

Project use`pytest`Conduct testing and require test coverage to reach**100%**。

Run each module test:

```bash
PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
```

Run full coverage tests:

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest -q && uv run coverage report --rcfile=pyproject.toml
```

Test documentation should be in accordance with`src/`module paths are organized and used with`Test`The test class at the beginning wraps the test method.
