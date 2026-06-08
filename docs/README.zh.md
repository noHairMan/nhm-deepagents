# nhm-deepagents

[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://isort.readthedocs.io/)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)

[简体中文](/docs/README.zh.md) | [English](/docs/README.en.md) | [日本語](/docs/README.ja.md) | [繁体中文](/docs/README.zh-TW.md)

一个使用现代 LLM 框架构建和运行“深度智能体”（Deep Agents）的 Python 项目。

## 🌟 项目概览

`nhm-deepagents` 是一个专注于深度智能体的专业 Python 项目。它利用现代 Python 特性 (3.14+) 和强大的工具，为 AI 智能体研究和应用提供高质量的开发体验。

项目内部包含两个主要模块：
- **`tomorrow`**: 核心智能体模块。代号取自游戏《死亡搁浅 2：冥滩之上》（Death Stranding 2: On the Beach）中的角色 **Tomorrow**（由艾丽·范宁饰演）。在剧情中，她是主角山姆·布里吉斯（Sam Bridges）的女儿，也被揭示为前作中的 **Lou** (BB-28)。
- **`rainy`**: 基于 FastAPI 的 API 服务模块。代号同样取自《死亡搁浅 2》中的角色 **Rainy**（由忽那汐里饰演）。在游戏中，她拥有引发“时间雨”（Timefall）和具有治愈能力的“核心雨”（Corefall）的神奇力量，被描述为既能伤害也能治愈的“药（Pharmakon）”。该模块集成了统一响应格式、处理时间中间件等功能。

该项目目前包含一个心理专家智能体，可以使用 `deepagents` 框架分析用户输入并提供建议，并通过 `rainy` 模块对外提供 API 接口。

## 🛠️ 技术栈

- **语言**: [Python](https://www.python.org/) >= 3.14
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **API 框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **Web 服务器**: [Uvicorn](https://www.uvicorn.org/)
- **智能体框架**: [deepagents](https://github.com/zongxuheng/deepagents) (基于 LangGraph/LangChain)
- **LLM 提供商**: [Ollama](https://ollama.com/) (通过 `langchain-ollama`)
- **配置管理**: [Dynaconf](https://www.dynaconf.com/)
- **代码质量**: `black`, `isort`, `pre-commit`
- **测试与覆盖率**: `pytest`, `coverage`

## 📋 环境要求

- **Python 3.14+**
- **uv**: 一个快速的 Python 包安装和解析器。
- **Ollama**: 必须正在运行且可访问。
- **LLM 模型**: 默认使用的模型是 `qwen3.5:9b`。您可以使用以下命令获取：
  ```bash
  ollama pull qwen3.5:9b
  ```

## 🚀 快速入门

### 安装

1. **安装 `uv`**:
   请按照 [uv 官方仓库](https://github.com/astral-sh/uv)中的说明进行操作。

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

5. **启动 Ollama 并获取模型**:
   ```bash
   ollama pull qwen3.5:9b
   ```

### 运行应用

运行主入口点：
```bash
uv run python src/main.py
```

## ⚙️ 配置

该项目使用 **Dynaconf** 进行配置管理。设置分别定义在 `src/tomorrow/settings.py` (Tomorrow) 和 `src/rainy/settings.py` (Rainy) 中，可以通过环境变量或 `.env` 文件进行覆盖。

### 环境变量

环境变量默认以前缀 `TOMORROW_` (核心模块) 或 `RAINY_` (API 模块) 开头。

#### Tomorrow 配置 (核心)

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `TOMORROW_OLLAMA_BASE_URL` | Ollama 服务的基地址 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL` | 默认使用的 LLM 模型 | `qwen3.5:9b` |
| `TOMORROW_APP` | 应用名称（用作环境变量前缀） | `tomorrow` |
| `TOMORROW_SETTINGS_MODULE` | 设置模块的路径 | `tomorrow.settings` |
| `TOMORROW_CHECKPOINT` | 检查点配置 | `{"type": "memory"}` |

#### Rainy 配置 (API)

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `RAINY_HOST` | API 服务监听地址 | `localhost` |
| `RAINY_PORT` | API 服务端口 | `8000` |
| `RAINY_APP` | 应用名称（用作环境变量前缀） | `rainy` |
| `RAINY_SETTINGS_MODULE` | 设置模块的路径 | `rainy.settings` |
| `RAINY_MIDDLEWARE` | 启用的中间件列表 | (见 settings.py) |

## 📜 脚本

常用的开发脚本：

- **格式化代码**:
  ```bash
  uv run black .
  uv run isort .
  ```

- **手动运行 pre-commit 钩子**:
  ```bash
  uv run pre-commit run --all-files
  ```

## 📂 项目结构

- `src/main.py`: 应用的主入口点。设置环境并启动 Uvicorn 服务器。
- `src/tomorrow/`: 核心智能体包目录。
  - `core/agent.py`: 定义深度智能体及其指令。
  - `core/checkpoints/`: 检查点实现（Memory, SQLite 等）。
  - `settings.py`: 默认配置值。
  - `utils/functional.py`: 功能实用程序。
- `src/rainy/`: API 服务包目录。
  - `app.py`: FastAPI 应用定义。
  - `api/endpoints/`: API 路由定义。
    - `chat.py`: 聊天接口，集成了深度智能体模块。
  - `middleware/`: 自定义中间件（处理时间、统一响应格式）。
  - `settings.py`: API 模块默认配置。
- `tests/`: 测试目录，结构与 `src` 保持一致。
- `docs/`: 多语言文档。
- `pyproject.toml`: 项目元数据、依赖项和工具配置。
- `uv.lock`: 锁定依赖版本。
- `LICENSE`: Apache License 2.0。

## 🧪 测试

项目使用 `pytest` 进行测试，并要求 **100%** 的测试覆盖率。

### 运行测试

- **运行 Tomorrow 测试**:
  ```bash
  PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings uv run pytest tests/tomorrow
  ```

- **运行 Rainy 测试**:
  ```bash
  PYTHONPATH=src RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings uv run pytest tests/rainy
  ```

### 运行覆盖率测试

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings \
RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 许可证

本项目采用 **Apache License 2.0** 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
