# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

A Python project to build and run Deep Agents using a modern LLM framework.

## 🌟 Project Overview

`nhm-deepagents` 是一个专注于深度智能体的专业 Python 项目。它利用现代 Python 特性 (3.14+) 和强大的工具，为 AI 智能体研究和应用提供高质量的开发体验。

The project contains three main modules:

-   **`tomorrow`**: Core agent module. The codename is taken from a character in the game "Death Stranding 2: On the Beach"**Tomorrow**(played by Elle Fanning). In the plot, she is the daughter of protagonist Sam Bridges, who was also revealed to be a character in the previous game.**Lou**(BB-28)。
-   **`rainy`**: API service module based on FastAPI. The codename is also taken from a character in Death Stranding 2**Rainy**(played by Shiori Kutsuna). In the game, she has the magical power to cause "Timefall" and the healing "Corefall", and is described as a "Pharmakon" that can both hurt and heal.
-   **`fragile`**: A Typer-based command line client for asking questions directly to the Tomorrow agent or starting interactive sessions. Its name is taken from a character in the same work**Fragile**. Fragile is the founder and courier of Fragile Express. He has aged rapidly due to exposure to the rain of time, but he has always delivered important supplies to others in dangerous environments. This image of a "fragile" appearance that still insists on the mission of connection and delivery is the background of the name of this client.

This project provides a general smart assistant agent that utilizes`deepagents`The framework analyzes user input and passes`rainy`The module provides external synchronization (`/api/chat`)and**streaming (`/api/chat/stream`）**API interface.

### Core functions

-   **deep agent**: Integrated`deepagents`Framework to support complex task processing and status management.
-   **Skill module**: support through`TOMORROW_SKILLS`Configure the skills directory to load scalable domain capabilities for the agent.
-   **subagent**: support through`TOMORROW_SUBAGENTS`Configure dedicated subagents and their models, skills, and system prompts.
-   **code interpreter**: Integrate QuickJS middleware to provide code execution capabilities for agents.
-   **recursive control**: support through`TOMORROW_RECURSION_LIMIT`Limit the depth of agent recursive calls.
-   **life cycle management**: introduction`AgentManager`Unified management of the creation and destruction of agent instances ensures graceful initialization of resources.
-   **High performance API**: Built on FastAPI, supports synchronous responses and Server-Sent Events (SSE) streaming output.
-   **Interactive CLI**:`fragile`support`/new`Create new session,`/history`Browse and switch between persisted historical sessions,`/quit`Exit, session recovery, input history, slash command completion and multi-line editing.
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
-   **LLM provider**:[To be](https://ollama.com/)、[HuggingFace](https://huggingface.co/)and[Anthropic](https://www.anthropic.com/)
-   **code execution**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)QuickJS middleware provided
-   **Terminal interaction**:[prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)Provides input history, command completion and multi-line editing,[Rich](https://github.com/Textualize/rich)Provides terminal output styles.
-   **Configuration management**:[Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
-   **Exception handling**: Custom exception system (`TomorrowError`and its subclasses), covering model, backend, storage, and checkpoint errors.
-   **Code quality**:[Ruff](https://github.com/astral-sh/ruff)(replaces Black and Isort),`pre-commit`, Strict Type Hinting
-   **Testing and Coverage**:`pytest`,`coverage`

## 📋 Environmental requirements

-   **Python 3.14+**
-   **uv**: A fast Python package installer and parser.
-   **LLM provider**: current`.env`Using the Anthropic-compatible interface, there is no need to run Ollama.
-   **LLM model**: Current configuration uses`deepseek-v4-flash`;You can also pass`TOMORROW_MODEL`Switch to Ollama or HuggingFace.

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

5.  **Configure LLM**:
    ```bash
    export TOMORROW_MODEL__TYPE="anthropic"
    export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
    export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
    export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
    ```

### Run application

Run the main entry point:

```bash
uv run python src/main.py
```

use`langgraph-cli`Start the agent API service:

```bash
uv run langgraph dev
```

The CLI will read the root directory`langgraph.json`, and expose the name`tomorrow`graph.

use`fragile`The command line client starts an interactive session:

```bash
uv run fragile
```

pass`--thread`or`-t`Passing in the UUID can restore an existing session; if not passed in, a new thread will be automatically created. Input during interaction`/new`To clear the screen and start a new session, enter`/history`To view saved sessions and switch by number or UUID, enter`/quit`Exit; press`Esc`Press Enter to insert a line feed.

## ⚙️ Configuration

This project uses**Pydantic Settings**Perform configuration management. The settings are respectively defined in`src/tomorrow/settings.py`(Tomorrow)、`src/rainy/settings.py`(Rainy) and`src/fragile/settings.py`(Fragile), you can use environment variables or`.env`file is overwritten. Environment variables have the highest priority and are used by the three modules respectively.`TOMORROW_`、`RAINY_`and`FRAGILE_`prefix; can also be passed`TOMORROW_ENV_FILE`、`RAINY_ENV_FILE`or`FRAGILE_ENV_FILE`Specify the configuration file path.

### environment variables

Environment variables are prefixed by default`TOMORROW_`(core module),`RAINY_`(API module) or`FRAGILE_`(CLI module) beginning.

#### Tomorrow configuration (core)

| variable                   | describe                                                        | default value                                   |
| -------------------------- | --------------------------------------------------------------- | ----------------------------------------------- |
| `TOMORROW_APP`             | Application name (used as environment variable prefix)          | `tomorrow`                                      |
| `TOMORROW_MODEL`           | Model configuration, supports OLLAMA, HUGGINGFACE and ANTHROPIC | current`.env`use`anthropic`/`deepseek-v4-flash` |
| `TOMORROW_CHECKPOINT`      | Checkpoint configuration, supports MEMORY and SQLITE            | `{"type":"memory"}`                             |
| `TOMORROW_BACKEND`         | Backend configuration, supports FILESYSTEM and LOCAL_SHELL      | `{"type":"filesystem"}`                         |
| `TOMORROW_STORE`           | Storage configuration, supports MEMORY and SQLITE               | `{"type":"sqlite"}`                             |
| `TOMORROW_SKILLS`          | Skill Catalog List                                              | `["skills/"]`                                   |
| `TOMORROW_SUBAGENTS`       | Subagent configuration list                                     | `[]`                                            |
| `TOMORROW_RECURSION_LIMIT` | The upper limit of agent recursive calls                        | `100`                                           |

Model configuration passed`TOMORROW_MODEL`Or pass in nested environment variables. current`.env`Use Anthropic compatible interfaces and`deepseek-v4-flash`;When using other providers, please configure accordingly`ollama`or`huggingface`object. For example:

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

For specific fields and default values, please refer to`src/tomorrow/settings.py`。

Subagent configuration passed`TOMORROW_SUBAGENTS`Passed in, each subagent requires at least`name`、`description`and`system_prompt`field, you can also specify`model`and`skills`,For example:

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### Rainy configuration (API)

| variable           | describe                                               | default value     |
| ------------------ | ------------------------------------------------------ | ----------------- |
| `RAINY_HOST`       | API service listening address                          | `localhost`       |
| `RAINY_PORT`       | API service port                                       | `8000`            |
| `RAINY_APP`        | Application name (used as environment variable prefix) | `rainy`           |
| `RAINY_MIDDLEWARE` | List of enabled middlewares                            | (see settings.py) |

#### Fragile configuration (CLI)

| variable      | describe                                               | default value |
| ------------- | ------------------------------------------------------ | ------------- |
| `FRAGILE_APP` | Application name (used as environment variable prefix) | `fragile`     |

Other interactive behavior of Fragile is controlled through command line options and built-in slash commands.

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

-   `src/main.py`: The main entry point of the Rainy API service. Set up the environment and start the Uvicorn server.
-   `src/fragile/`: Command line client package directory.
    -   `cli.py`: definition`fragile`Command line entry.
    -   `commands/interactive/`: Interactive session implementation, supporting session recovery, new session, command completion and multi-line input.
        -   `agent.py`: Manages interactions with the Tomorrow agent.
        -   `commands/`: Interactive slash command implementation.
            -   `history.py`: Query and select persisted historical sessions.
            -   `new.py`: Create a new session.
            -   `quit.py`: Exit the interactive session.
        -   `display.py`: Management terminal display.
        -   `input.py`: Manage input history, command completion and multi-line editing.
        -   `session.py`: Manage the flow of interactive sessions.
    -   `settings.py`: CLI module default configuration.
-   `src/tomorrow/`: Core agent package directory.
    -   `graph.py`:`langgraph-cli`The graph entry to use.
    -   `core/agent.py`: Define deep agents and their instructions, providing`AgentManager`Perform life cycle management.
    -   `core/backend/`: Unify backend loading logic, support`FILESYSTEM`and`LOCAL_SHELL`。
    -   `core/checkpoint/`: Checkpoint implementation, support`MEMORY`and`SQLITE`。
    -   `core/model/`: Model loading implementation, support`OLLAMA`、`HUGGINGFACE`and`ANTHROPIC`。
    -   `core/store/`: Storage implementation, support`MEMORY`and`SQLITE`。
    -   `exceptions.py`: Define application-specific exception class system.
    -   `models/constants/`: Define various types of constants (Backend, Checkpoint, Model, Store).
    -   `settings.py`: Default configuration value.
    -   `utils/functional.py`: Function utility.
-   `src/rainy/`: API service package directory.
    -   `app.py`: FastAPI application definition, integrated life cycle management and routing.
    -   `lifespan.py`: Handle the startup and shutdown logic of the application and manage the life cycle of the agent instance.
    -   `api/endpoints/`: API route definition.
        -   `chat.py`: Synchronous and streaming chat interface, integrated with deep agent module (responses are uniformly packaged by middleware).
            -   `POST /api/chat`: Synchronize chat responses.
            -   `POST /api/chat/stream`: SSE streaming response.
            -   `POST /api/chat/stream/event`: Event stream response.
        -   `health.py`: Health check interface (`GET /api/health`)。
        -   `urls.py`: Unified routing mounting.
    -   `middleware/`: Custom middleware (processing time, unified response format).
    -   `settings.py`: API module default configuration.
-   `tests/`: Test directory, structure and`src`Be consistent.
-   `docs/`: Multilingual documentation.
-   `pyproject.toml`: Project metadata, dependencies, and tool configuration.
-   `langgraph.json`:`langgraph-cli`graph and environment configuration.
-   `uv.lock`: Lock dependency versions.
-   `LICENSE`: Apache License 2.0。

## 🧪 Test

Project use`pytest`run a test and ask**100%**test coverage.

### Run tests

-   **Run the Tomorrow test**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
    ```

-   **Run Rainy tests**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
    ```

-   **Run Fragile tests**:
    ```bash
    PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
    ```

### Run coverage tests

It is required that test coverage must reach**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 License

This project uses**Apache License 2.0**license. For details, please see[LICENSE](LICENSE)document.
