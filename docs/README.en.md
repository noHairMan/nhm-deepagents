# nhm-deepagents

A Python project for deep agents.

## Overview

`nhm-deepagents`is a Python project focusing on deep agents. It uses modern Python features and tools to provide a robust development experience.

## Environmental requirements

-   **Python**: >= 3.14
-   **包管理器**:[uv](https://github.com/astral-sh/uv)

## Installation and setup

Please follow these steps to start developing:

1.  **Install`uv`**:
    如果您还没有安装 `uv`, you can follow its[官方仓库](https://github.com/astral-sh/uv)Follow the instructions in .

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

## Development script

This project uses`black`and`isort`Format it and use`pre-commit`Conduct quality checks.

-   **格式化代码**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **Run the pre-commit hook manually**:
    ```bash
    uv run pre-commit run --all-files
    ```

## Project structure

-   `src/tomorrow/`: Core package directory.
-   `pyproject.toml`: Project configuration and dependency management.
-   `.pre-commit-config.yaml`: pre-commit hook configuration.
-   `LICENSE`: Apache License 2.0。

## environment variables

-   TODO: Record any required environment variables here.

## test

-   TODO: Add tests and document how to run them (e.g.`uv run pytest`）。

## license

This project uses**Apache License 2.0** 许可证。有关详情，请参阅 [LICENSE](../LICENSE)document.
