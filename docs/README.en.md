# nhm-deepagents

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

A Python project to build and run Deep Agents using a modern LLM framework.

## 🌟 Project Overview

`nhm-deepagents`is a professional Python project focusing on deep agents. It leverages modern Python features (3.14+) and powerful tools to provide a high-quality development experience for AI agent research and applications.

The project currently contains a psychological expert agent that can be used`deepagents`The framework analyzes user input and provides recommendations.

## 🛠️ Technology stack

-   **language**:[Python](https://www.python.org/)>= 3.14
-   **Package manager**:[uv](https://github.com/astral-sh/uv)
-   **agent framework**:[deepagents](https://github.com/zongxuheng/deepagents)(Based on LangGraph/LangChain)
-   **LLM provider**:[To be](https://ollama.com/)(pass`langchain-ollama`)
-   **Configuration management**:[Dynaconf](https://www.dynaconf.com/)
-   **Code quality**:`black`,`isort`,`pre-commit`

## 📋 环境要求

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

### Run application

运行主入口点：

```bash
uv run python src/main.py
```

## ⚙️ Configuration

This project uses**Dynaconf**Perform configuration management. Settings are defined in`src/tomorrow/settings.py`, which can be passed through environment variables or`.env`file is overwritten.

### environment variables

Environment variables are prefixed by default`TOMORROW_`beginning.

| variable                   | describe                                               | default value            |
| -------------------------- | ------------------------------------------------------ | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | The base address of the Ollama service                 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | LLM model used by default                              | `qwen3.5:9b`             |
| `TOMORROW_APP`             | Application name (used as environment variable prefix) | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | Set module path                                        | `tomorrow.settings`      |

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

-   `src/main.py`: The main entry point of the application. Set up the environment and invoke the agent.
-   `src/tomorrow/`: Core package directory.
    -   `core/agent.py`: Define deep agents and their instructions.
    -   `settings.py`: Default configuration value.
    -   `utils/conf.py`: Dynaconf 初始化逻辑。
    -   `utils/functional.py`: Functional utility (e.g.`SimpleLazyObject`）。
-   `docs/`: Multilingual documentation.
-   `pyproject.toml`: Project metadata, dependencies, and tool configuration.
-   `uv.lock`: Lock dependency versions.
-   `LICENSE`: Apache License 2.0。

## 🧪 Test

-   TODO: use`pytest`Implement unit testing and integration testing.
-   TODO: Add CI process for automated testing.

Running the test (after implementation):

```bash
uv run pytest
```

## 📄 License

This project uses**Apache License 2.0**license. For details, please see[LICENSE](LICENSE)document.
