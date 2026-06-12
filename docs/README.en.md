# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

A Python project to build and run Deep Agents using a modern LLM framework.

## 🌟 Project Overview

`nhm-deepagents`is a professional Python project focusing on deep agents. It leverages modern Python features (3.14+) and powerful tools to provide a high-quality development experience for AI agent research and applications.

The project contains two main modules:

-   **`tomorrow`**: Core agent module. The codename is taken from a character in the game "Death Stranding 2: On the Beach"**Tomorrow**(played by Elle Fanning). In the plot, she is the daughter of protagonist Sam Bridges, who was also revealed to be a character in the previous game.**Lou**(BB-28)。
-   **`rainy`**: API service module based on FastAPI. The codename is also taken from a character in Death Stranding 2**Rainy**(played by Shiori Kutsuna). In the game, she has the magical power to cause "Timefall" and the healing "Corefall", and is described as a "Pharmakon" that can both hurt and heal. This module integrates functions such as unified response format and processing time middleware.

This project provides a general smart assistant agent that utilizes`deepagents`The framework analyzes user input and passes`rainy`The module provides external synchronization (`/api/chat`)and**streaming (`/api/chat/stream`）**API interface.

### Core functions

-   **deep agent**: Integrated`deepagents`Framework to support complex task processing and status management.
-   **life cycle management**: introduction`AgentManager`Unified management of the creation and destruction of agent instances ensures graceful initialization of resources.
-   **High performance API**: Built on FastAPI, supports synchronous responses and Server-Sent Events (SSE) streaming output.
-   **Reliability guaranteed**: Forced type hints, Ruff static checking, 100% test coverage requirement.

## ⚙️ CI/CD

The project integrates GitHub Actions workflows, including:

-   **Testing and Coverage**: Automatically run tests and check code coverage.
-   **Document translation**: automatically`README.zh.md`Translated into multiple languages ​​(English, Japanese, Traditional Chinese).
-   **Code specifications**: Automatic execution`ruff`Check and format to ensure consistent code style and high quality.
-   **CI process optimization**: Enhanced workflow trigger path rules, triggering builds only when relevant code or configuration changes, improving efficiency.

## 🛠️ Technology stack

-   **language**:[Python](https://www.python.org/)>= 3.14
-   **Package manager**:[uv](https://github.com/astral-sh/uv)
-   **API framework**:[speedy](https://fastapi.tiangolo.com/)
-   **Web server**:[Uvicorn](https://www.uvicorn.org/)
-   **agent framework**:[deepagents](https://github.com/zongxuheng/deepagents)(Based on LangGraph/LangChain)
-   **LLM provider**:[To be](https://ollama.com/)(pass`langchain-ollama`)
-   **Configuration management**:[Dynaconf](https://www.dynaconf.com/)
-   **Code quality**:[Ruff](https://github.com/astral-sh/ruff)(replaces Black and Isort),`pre-commit`, Strict Type Hinting
-   **Testing and Coverage**:`pytest`,`coverage`

## 📋 Environmental requirements

-   **Python 3.14+**
-   **uv**: A fast Python package installer and parser.
-   **To be**: must be running and accessible.
-   **LLM model**: The model used by default is`qwen3.5:9b`. You can get it using the following command:
    ```bash
    ollama pull qwen3.5:9b
    ```

## 🚀 Quick Start

### Install

1.  **Install`uv`**:
    Please follow[uv official warehouse](https://github.com/astral-sh/uv)Follow the instructions in .

2.  **Clone repository**:
    ```bash
    git clone <repository-url>
    cd nhm-deepagents
    ```

3.  **Synchronize dependencies and create virtual environments**:
    ```bash
    uv sync
    ```

4.  **Install pre-commit hook**:
    ```bash
    uv run pre-commit install
    ```

5.  **Start Ollama and get the model**:
    ```bash
    ollama pull qwen3.5:9b
    ```

### Run application

Run the main entry point:

```bash
uv run python src/main.py
```

## ⚙️ Configuration

This project uses**Dynaconf**Perform configuration management. The settings are respectively defined in`src/tomorrow/settings.py`(Tomorrow) 和`src/rainy/settings.py`(Rainy), you can use environment variables or`.env`file is overwritten.

### environment variables

Environment variables are prefixed by default`TOMORROW_`(core module) or`RAINY_`(API module) at the beginning.

#### Tomorrow configuration (core)

| variable                   | describe                                               | default value                      |
| -------------------------- | ------------------------------------------------------ | ---------------------------------- |
| `TOMORROW_OLLAMA_BASE_URL` | The base address of the Ollama service                 | `http://localhost:11434`           |
| `TOMORROW_DEFAULT_MODEL`   | LLM model used by default                              | `qwen3.5:9b`                       |
| `TOMORROW_APP`             | Application name (used as environment variable prefix) | `tomorrow`                         |
| `TOMORROW_SETTINGS_MODULE` | Set module path                                        | `tomorrow.settings`                |
| `TOMORROW_CHECKPOINT`      | Checkpoint configuration                               | `{"type": CheckpointType.MEMORY}`  |
| `TOMORROW_BACKEND`         | Backend configuration, support`FILESYSTEM`and`DAYTONA` | `{"type": BackendType.FILESYSTEM}` |

#### Rainy configuration (API)

| variable                | describe                                               | default value     |
| ----------------------- | ------------------------------------------------------ | ----------------- |
| `RAINY_HOST`            | API service listening address                          | `localhost`       |
| `RAINY_PORT`            | API service port                                       | `8000`            |
| `RAINY_APP`             | Application name (used as environment variable prefix) | `rainy`           |
| `RAINY_SETTINGS_MODULE` | Set module path                                        | `rainy.settings`  |
| `RAINY_MIDDLEWARE`      | List of enabled middlewares                            | (see settings.py) |

## 📜 Screenplay

Commonly used development scripts:

-   **Check and format code**:
    ```bash
    uv run ruff check . --fix
    uv run ruff format .
    ```

-   **Run the pre-commit hook manually**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 Project structure

-   `src/main.py`: The main entry point of the application. Set up the environment and start the Uvicorn server.
-   `src/tomorrow/`: Core agent package directory.
    -   `core/agent.py`: Define deep agents and their instructions, providing`AgentManager`Lifecycle management, support for Filesystem and Daytona sandbox backends (local mode only).
    -   `core/checkpoints/`: Checkpoint implementation (Memory, SQLite, etc.).
    -   `models/constants/backend.py`: Define backend type constants.
    -   `settings.py`: Default configuration value.
    -   `utils/functional.py`: Function utility.
-   `src/rainy/`: API service package directory.
    -   `app.py`: FastAPI application definition, integrated life cycle management and routing.
    -   `lifespan.py`: Handle the startup and shutdown logic of the application and manage the life cycle of the agent instance.
    -   `api/endpoints/`: API route definition.
        -   `chat.py`: Synchronous and streaming chat interface (using OpenAI-like response format), integrated with deep agent module.
        -   `health.py`: Health check interface.
        -   `urls.py`: Unified routing mounting.
    -   `middleware/`: Custom middleware (processing time, unified response format).
    -   `settings.py`: API module default configuration.
-   `tests/`: Test directory, structure and`src`Be consistent.
-   `docs/`: Multilingual documentation.
-   `pyproject.toml`: Project metadata, dependencies, and tool configuration.
-   `uv.lock`: Lock dependency versions.
-   `LICENSE`: Apache License 2.0。

## 🧪 测试

Project use`pytest`run a test and ask**100%**test coverage.

### Run tests

-   **Run the Tomorrow test**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings uv run pytest tests/tomorrow
    ```

-   **Run Rainy tests**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings uv run pytest tests/rainy
    ```

### Run coverage tests

It is required that test coverage must reach**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings \
RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 License

This project uses**Apache License 2.0**license. For details, please see[LICENSE](LICENSE)document.
