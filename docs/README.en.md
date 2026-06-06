# nhm-deepagents

[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://isort.readthedocs.io/)

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

A Python project to build and run Deep Agents using a modern LLM framework.

## 🌟 Project Overview

`nhm-deepagents`is a professional Python project focusing on deep agents. It leverages modern Python features (3.14+) and powerful tools to provide a high-quality development experience for AI agent research and applications.

The project contains two main modules:

-   **`tomorrow`**: Core agent module. The codename is taken from a character in the game "Death Stranding 2: On the Beach"**Tomorrow**(played by Elle Fanning). In the plot, she is the daughter of protagonist Sam Bridges, who was also revealed to be a character in the previous game.**Lou**(BB-28)。
-   **`rainy`**: API service module based on FastAPI. The codename is also taken from a character in Death Stranding 2**Rainy**(played by Shiori Kutsuna). In the game, she has the magical power to cause "Timefall" and the healing "Corefall", and is described as a "Pharmakon" that can both hurt and heal. This module integrates functions such as unified response format and processing time middleware.

The project currently contains a psychological expert agent that can be used`deepagents`The framework analyzes user input and provides suggestions via`rainy`The module provides an API interface to the outside world.

## 🛠️ Technology stack

-   **language**:[Python](https://www.python.org/)>= 3.14
-   **Package manager**:[uv](https://github.com/astral-sh/uv)
-   **API framework**:[speedy](https://fastapi.tiangolo.com/)
-   **Web server**:[Uvicorn](https://www.uvicorn.org/)
-   **agent framework**:[deepagents](https://github.com/zongxuheng/deepagents)(Based on LangGraph/LangChain)
-   **LLM provider**:[To be](https://ollama.com/)(pass`langchain-ollama`)
-   **Configuration management**:[Dynaconf](https://www.dynaconf.com/)
-   **Code quality**:`black`,`isort`,`pre-commit`
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

| variable                   | describe                                               | default value            |
| -------------------------- | ------------------------------------------------------ | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | The base address of the Ollama service                 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | LLM model used by default                              | `qwen3.5:9b`             |
| `TOMORROW_APP`             | Application name (used as environment variable prefix) | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | Set module path                                        | `tomorrow.settings`      |
| `TOMORROW_CHECKPOINT`      | Checkpoint configuration                               | `{"type": "memory"}`     |

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

-   **Format code**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **Run the pre-commit hook manually**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 Project structure

-   `src/main.py`: The main entry point of the application. Set up the environment and start the Uvicorn server.
-   `src/tomorrow/`: Core agent package directory.
    -   `core/agent.py`: Define deep agents and their instructions.
    -   `core/checkpoints/`: Checkpoint implementation (Memory, SQLite, etc.).
    -   `settings.py`: Default configuration value.
    -   `utils/functional.py`: Function utility.
-   `src/rainy/`: API service package directory.
    -   `app.py`: FastAPI application definition.
    -   `api/endpoints/`: API route definition.
        -   `chat.py`: Chat interface, integrated with deep agent module.
    -   `middleware/`: Custom middleware (processing time, unified response format).
    -   `settings.py`: API module default configuration.
-   `tests/`: Test directory, structure and`src`Be consistent.
-   `docs/`: Multilingual documentation.
-   `pyproject.toml`: Project metadata, dependencies, and tool configuration.
-   `uv.lock`: Lock dependency versions.
-   `LICENSE`: Apache License 2.0。

## 🧪 Test

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

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings \
RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 License

This project uses**Apache License 2.0**license. For details, please see[LICENSE](LICENSE)document.
