# nhm-deepagents

一个用于深度智能体（deep agents）的 Python 项目。

## 概览

`nhm-deepagents` 是一个专注于深度智能体的 Python 项目。它使用现代 Python 特性和工具，以提供稳健的开发体验。

## 环境要求

- **Python**: >= 3.14
- **包管理器**: [uv](https://github.com/astral-sh/uv)

## 安装与设置

请按照以下步骤开始开发：

1. **安装 `uv`**:
   如果您还没有安装 `uv`，可以按照其[官方仓库](https://github.com/astral-sh/uv)中的说明进行操作。

2. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd nhm-deepagents
   ```

3. **同步依赖并创建虚拟环境**:
   ```bash
   uv sync
   ```

4. **安装 pre-commit 钩子**:
   ```bash
   uv run pre-commit install
   ```

## 开发脚本

该项目使用 `black` 和 `isort` 进行格式化，并使用 `pre-commit` 进行质量检查。

- **格式化代码**:
  ```bash
  uv run black .
  uv run isort .
  ```

- **手动运行 pre-commit 钩子**:
  ```bash
  uv run pre-commit run --all-files
  ```

## 项目结构

- `src/tomorrow/`: 核心包目录。
- `pyproject.toml`: 项目配置和依赖管理。
- `.pre-commit-config.yaml`: pre-commit 钩子配置。
- `LICENSE`: Apache License 2.0。

## 环境变量

- TODO: 在此处记录任何所需的环境变量。

## 测试

- TODO: 添加测试并记录如何运行它们（例如 `uv run pytest`）。

## 许可证

本项目采用 **Apache License 2.0** 许可证。有关详情，请参阅 [LICENSE](../LICENSE) 文件。
