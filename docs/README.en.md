# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

![Fragile banner](/docs/images/fragile.png)

A Python project to build and run Deep Agents using a modern LLM framework.

For development environment, project structure, code specifications and testing methods, please refer to[Contribution Guide](CONTRIBUTING.zh.md)。

## 🌟 Project Overview

`nhm-deepagents`is a professional Python project focusing on deep agents. It leverages modern Python features (3.14+) and powerful tools to provide a high-quality development experience for AI agent research and applications.

The project contains three main modules:

-   **`tomorrow`**: Core agent module. The codename is taken from a character in the game "Death Stranding 2: On the Beach"**Tomorrow**(played by Elle Fanning). In the plot, she is the daughter of protagonist Sam Bridges, who was also revealed to be a character in the previous game.**Lou**(BB-28)。
-   **`rainy`**: API service module based on FastAPI. The codename is also taken from a character in Death Stranding 2**Rainy**(played by Shiori Kutsuna). In the game, she has the magical power to cause "Timefall" and the healing "Corefall", and is described as a "Pharmakon" that can both hurt and heal.
-   **`fragile`**: based on`asyncclick`An asynchronous command line client for asking questions directly to the Tomorrow agent or starting interactive sessions. Its name is taken from a character in the same work**Fragile**. Fragile is the founder and courier of Fragile Express. He has aged rapidly due to exposure to the rain of time, but he has always delivered important supplies to others in dangerous environments. This image of a "fragile" appearance that still insists on the mission of connection and delivery is the background of the name of this client.

This project provides a general smart assistant agent that utilizes`deepagents`The framework analyzes user input and passes`rainy`The module provides external synchronization (`/api/chat`)and**streaming (`/api/chat/stream`）**API interface.

### Core functions

-   **deep agent**: Integrated`deepagents`Framework to support complex task processing and status management.
-   **Skill module**: support through`TOMORROW_SKILLS`Configure the skills directory to load scalable domain capabilities for the agent.
-   **subagent**: support through`TOMORROW_SUBAGENTS`Configure dedicated subagents and their models, skills, and system prompts.
-   **recursive control**: support through`TOMORROW_RECURSION_LIMIT`Limit the depth of agent recursive calls.
-   **life cycle management**: introduction`AgentManager`Unified management of the creation and destruction of agent instances ensures graceful initialization of resources.
-   **High performance API**: Built on FastAPI, supports synchronous responses and Server-Sent Events (SSE) streaming output.
-   **Interactive CLI**:`fragile`support`/new`Create new session,`/history`Browse and switch between persisted historical sessions,`/account`Configure external model account,`/quit`Exit, session recovery, input history, slash command completion and multi-line editing.
-   **Account configuration persistence**: Supports saving API credentials for Ollama, Anthropic, and OpenAI via interactive commands and automatically restoring them in subsequent sessions.
-   **Reliability guaranteed**: Forced type hints, Ruff static checking, 100% test coverage requirement.

## 🛠️ Technology stack

-   **language**:[Python](https://www.python.org/)>= 3.14
-   **Package manager**:[uv](https://github.com/astral-sh/uv)
-   **API framework**:[speedy](https://fastapi.tiangolo.com/)
-   **Web server**:[Uvicorn](https://www.uvicorn.org/)
-   **agent framework**:[deepagents](https://github.com/zongxuheng/deepagents)(Based on LangGraph/LangChain)
-   **LLM provider**:[To be](https://ollama.com/)、[Anthropic](https://www.anthropic.com/)and[OpenAI](https://openai.com/)
-   **Terminal interaction**:[asyncclick](https://github.com/python-trio/asyncclick)Provide asynchronous CLI commands, parameter parsing and help information;[prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)Provides asynchronous input, input history, command completion and multi-line editing;[Rich](https://github.com/Textualize/rich)Provides terminal output styles.
-   **Configuration management**:[Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
-   **Exception handling**: Custom exception system (`TomorrowError`and its subclasses), covering model, backend, storage, and checkpoint errors.
-   **Code quality**:[Ruff](https://github.com/astral-sh/ruff)(replaces Black and Isort),`pre-commit`, Strict Type Hinting
-   **Testing and Coverage**:`pytest`,`coverage`

## 📋 Environmental requirements

-   **Python 3.14+**
-   **uv**: A fast Python package installer and parser.
-   **LLM provider**: current`.env`Using the Anthropic-compatible interface, there is no need to run Ollama.
-   **LLM model**: Current configuration uses`deepseek-v4-flash`;can also be passed`TOMORROW_MODEL`Switch to Ollama.

## 🚀 Quick Start

### Install

1.  **Install`uv`**:
    Please follow[uv official warehouse](https://github.com/astral-sh/uv)Follow the instructions in .

2.  **Clone repository**:
    ```bash
    git clone https://github.com/noHairMan/nhm-deepagents.git
    cd nhm-deepagents
    ```

3.  **Synchronize dependencies and create virtual environments**:
    ```bash
    uv sync
    ```

4.  **Install`fragile`Order**:

    ```bash
    uv tool install .
    ```

    After installation is complete, you can use it directly`fragile`command starts the command line client.

### Run application

Run the main entry point:

```bash
uv run python src/main.py
```

This command starts the Rainy API, which listens by default`http://localhost:8000`. You can also use Uvicorn to start directly:

```bash
uv run uvicorn main:app --app-dir src --host localhost --port 8000
```

use`langgraph-cli`Start the agent API service:

```bash
uv run langgraph dev
```

The CLI will read the root directory`langgraph.json`, and expose the name`tomorrow`graph.

The request body of Rainy API contains required`message`fields and optional sessions`thread_id`. The synchronization interface returns the agent's final reply:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"你好"}'
```

When you need to receive replies step by step, you can call`/api/chat/stream` 获取 SSE 数据流；`/api/chat/stream/event`A more complete stream of LangGraph events is returned. The health check interface is`GET /api/health`。

use`fragile`The command line client starts an interactive session:

```bash
fragile
```

If not used yet`uv tool install .`The installation command can also be run in the project environment:

```bash
uv run fragile
```

pass`--thread`or`-t`Passing in the UUID can restore an existing session; if not passed in, a new thread will be automatically created. Input during interaction`/new`To clear the screen and start a new session, enter`/history`To view saved sessions and switch by number or UUID, enter`/quit`Exit; you can also press twice in succession`Ctrl+C`To exit a session in a short time, press`Esc`Press Enter to insert a line feed.

When using another model provider for the first time, you can enter it in an interactive session`/account`, follow the prompts to select a provider and fill in the Base URL and API Key. Other configurations such as model names still pass`TOMORROW_MODEL`Or the corresponding environment variable settings. Credentials will be persisted to the local database for subsequent startups`fragile`Automatically restore when running; if you need to modify the configuration, execute it again`/account`That’s it.

`fragile`CLI entry and`purge`Subcommands all use asynchronous command functions to avoid nested calls in already running event loops`asyncio.run()`. Clean up persisted session records:

```bash
fragile purge
```

## ⚙️ Configuration

This project uses**Pydantic Settings**Perform configuration management. The settings are respectively defined in`src/tomorrow/settings.py`(Tomorrow)、`src/rainy/settings.py`(Rainy) and`src/fragile/settings.py`(Fragile), you can use environment variables or`.env`file is overwritten. Environment variables have the highest priority and are used by the three modules respectively.`TOMORROW_`、`RAINY_`and`FRAGILE_`prefix; can also be passed`TOMORROW_ENV_FILE`、`RAINY_ENV_FILE`or`FRAGILE_ENV_FILE`Specify the configuration file path.

### environment variables

Environment variables are prefixed by default`TOMORROW_`(core module),`RAINY_`(API module) or`FRAGILE_`(CLI module) beginning.

#### Tomorrow configuration (core)

| variable                   | describe                                                   | default value                                   |
| -------------------------- | ---------------------------------------------------------- | ----------------------------------------------- |
| `TOMORROW_APP`             | Application name (used as environment variable prefix)     | `tomorrow`                                      |
| `TOMORROW_MODEL`           | Model configuration, supports OLLAMA, ANTHROPIC and OPENAI | current`.env`use`anthropic`/`deepseek-v4-flash` |
| `TOMORROW_CHECKPOINT`      | Checkpoint configuration, supports MEMORY and SQLITE       | `{"type":"memory"}`                             |
| `TOMORROW_BACKEND`         | Backend configuration, supports FILESYSTEM and LOCAL_SHELL | `{"type":"filesystem"}`                         |
| `TOMORROW_STORE`           | Storage configuration, supports MEMORY and SQLITE          | `{"type":"sqlite"}`                             |
| `TOMORROW_SKILLS`          | Skill Catalog List                                         | `["skills/"]`                                   |
| `TOMORROW_SUBAGENTS`       | Subagent configuration list                                | `[]`                                            |
| `TOMORROW_RECURSION_LIMIT` | The upper limit of agent recursive calls                   | `100`                                           |

Model configuration passed`TOMORROW_MODEL`Or pass in nested environment variables. current`.env`Use Anthropic compatible interfaces and`deepseek-v4-flash`;When using Ollama, please configure accordingly`ollama`object. For example:

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

When selecting OpenAI or an OpenAI API-compatible service, you can configure the model name, API Key, optional Base URL, and temperature using the following nested environment variables:

```bash
export TOMORROW_MODEL__TYPE="openai"
export TOMORROW_MODEL__OPENAI__MODEL="gpt-4o-mini"
export TOMORROW_MODEL__OPENAI__API_KEY="your-api-key"
export TOMORROW_MODEL__OPENAI__BASE_URL="https://api.openai.com/v1"
export TOMORROW_MODEL__OPENAI__TEMPERATURE="0"
```

For specific fields and default values, please refer to`src/tomorrow/settings.py`。

Subagent configuration passed`TOMORROW_SUBAGENTS`Passed in, each subagent requires at least`name`、`description`and`system_prompt`field, you can also specify`model`and`skills`,For example:

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### Rainy configuration (API)

| variable                              | describe                                               | default value                               |
| ------------------------------------- | ------------------------------------------------------ | ------------------------------------------- |
| `RAINY_HOST`                          | API service listening address                          | `localhost`                                 |
| `RAINY_PORT`                          | API service port                                       | `8000`                                      |
| `RAINY_APP`                           | Application name (used as environment variable prefix) | `rainy`                                     |
| `RAINY_MIDDLEWARE`                    | List of enabled middlewares                            | Unified response format and processing time |
| `RAINY_UNIFY_RESPONSE_FORMAT_EXCLUDE` | Path without unified response packaging                | `/docs`、`/redoc`、`/openapi.json`            |
| `RAINY_LOG_LEVEL`                     | Log level                                              | `INFO`                                      |

#### Fragile configuration (CLI)

| variable                           | describe                                                         | default value          |
| ---------------------------------- | ---------------------------------------------------------------- | ---------------------- |
| `FRAGILE_APP`                      | Application name (used as environment variable prefix)           | `fragile`              |
| `FRAGILE_INTERRUPT_EXIT_THRESHOLD` | twice`Ctrl+C`Maximum interval between triggering exits (seconds) | `0.5`                  |
| `FRAGILE_ENABLED_COMMANDS`         | Enabled interactive command classpath list                       | `quit`、`new`、`history` |

Other interactive behavior of Fragile is controlled through command line options and built-in slash commands. Commands are discovered and processed uniformly through the registry, using`FRAGILE_ENABLED_COMMANDS`Adjust enabled commands. Account credentials are provided by`Account`The model is saved in Fragile's database as a singleton, and will be restored to Tomorrow's model configuration when an interactive session is started; environment variables can still be used as a configuration source and have higher priority.

## 📄 License

This project uses**Apache License 2.0**license. For details, please see[LICENSE](/LICENSE)document.
