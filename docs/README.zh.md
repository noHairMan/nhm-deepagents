# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)
[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[简体中文](/docs/README.zh.md) | [English](/docs/README.en.md) | [日本語](/docs/README.ja.md) | [繁体中文](/docs/README.zh-TW.md)

一个使用现代 LLM 框架构建和运行“深度智能体”（Deep Agents）的 Python 项目。

## 🌟 项目概览

`nhm-deepagents` 是一个专注于深度智能体的专业 Python 项目。它利用现代 Python 特性 (3.14+) 和强大的工具，为 AI 智能体研究和应用提供高质量的开发体验。

项目内部包含三个主要模块：
- **`tomorrow`**: 核心智能体模块。代号取自游戏《死亡搁浅 2：冥滩之上》（Death Stranding 2: On the Beach）中的角色 **Tomorrow**（由艾丽·范宁饰演）。在剧情中，她是主角山姆·布里吉斯（Sam Bridges）的女儿，也被揭示为前作中的 **Lou** (BB-28)。
- **`rainy`**: 基于 FastAPI 的 API 服务模块。代号同样取自《死亡搁浅 2》中的角色 **Rainy**（由忽那汐里饰演）。在游戏中，她拥有引发“时间雨”（Timefall）和具有治愈能力的“核心雨”（Corefall）的神奇力量，被描述为既能伤害也能治愈的“药（Pharmakon）”。
- **`fragile`**: 基于 Typer 的命令行客户端，用于直接向 Tomorrow 智能体提问或启动交互式会话。其名称取自同一作品中的角色 **Fragile**。Fragile 是 Fragile Express 的创始人和快递员，因接触时间雨而快速衰老，却始终在危险环境中为他人运送重要物资；这种“脆弱”外表下仍坚持承担连接与传递使命的形象，正是该客户端名称的背景。

该项目提供了一个通用的智能助理智能体，利用 `deepagents` 框架分析用户输入，并通过 `rainy` 模块对外提供同步（`/api/chat`）及**流式（`/api/chat/stream`）** API 接口。

### 核心功能
- **深度智能体**: 集成 `deepagents` 框架，支持复杂任务处理与状态管理。
- **技能模块**: 支持通过 `TOMORROW_SKILLS` 配置技能目录，为智能体加载可扩展的领域能力。
- **子代理**: 支持通过 `TOMORROW_SUBAGENTS` 配置专用子代理及其模型、技能和系统提示词。
- **代码解释器**: 集成 QuickJS 中间件，为智能体提供代码执行能力。
- **递归控制**: 支持通过 `TOMORROW_RECURSION_LIMIT` 限制智能体递归调用深度。
- **生命周期管理**: 引入 `AgentManager` 统一管理智能体实例的创建与销毁，确保资源的优雅初始化。
- **高性能 API**: 基于 FastAPI 构建，支持同步响应与 Server-Sent Events (SSE) 流式输出。
- **可靠性保障**: 强制类型提示、Ruff 静态检查、100% 测试覆盖率要求。

## ⚙️ CI/CD

项目集成了 GitHub Actions 工作流，包括：
- **测试与覆盖率**: 自动运行测试并检查代码覆盖率。
- **文档翻译**: 自动将 `README.zh.md` 翻译为多种语言（English, 日本語, 繁体中文）。
- **代码规范**: 自动执行 `ruff` 检查与格式化，确保代码风格统一且高质量。
- **CI 流程优化**: 增强了工作流触发路径规则，仅在相关代码或配置变动时触发构建，提升效率。

## 🛠️ 技术栈

- **语言**: [Python](https://www.python.org/) >= 3.14
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **API 框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **Web 服务器**: [Uvicorn](https://www.uvicorn.org/)
- **智能体框架**: [deepagents](https://github.com/zongxuheng/deepagents) (基于 LangGraph/LangChain)
- **LLM 提供商**: [Ollama](https://ollama.com/)、[HuggingFace](https://huggingface.co/) 和 [Anthropic](https://www.anthropic.com/)
- **代码执行**: [langchain-quickjs](https://github.com/langchain-ai/langchainjs) 提供的 QuickJS 中间件
- **配置管理**: [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- **异常处理**: 自定义异常体系 (`TomorrowError` 及其子类)，涵盖模型、后端、存储和检查点错误。
- **代码质量**: [Ruff](https://github.com/astral-sh/ruff) (替代 Black 和 Isort)、`pre-commit`、强制类型提示 (Strict Type Hinting)
- **测试与覆盖率**: `pytest`, `coverage`

## 📋 环境要求

- **Python 3.14+**
- **uv**: 一个快速的 Python 包安装和解析器。
- **LLM 提供商**: 当前 `.env` 使用 Anthropic 兼容接口，无需运行 Ollama。
- **LLM 模型**: 当前配置使用 `deepseek-v4-flash`；也可以通过 `TOMORROW_MODEL` 切换到 Ollama 或 HuggingFace。

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

5. **配置 LLM**:
   ```bash
   export TOMORROW_MODEL__TYPE="anthropic"
   export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
   export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
   export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
   ```

### 运行应用

运行主入口点：
```bash
uv run python src/main.py
```

使用 `langgraph-cli` 启动智能体 API 服务：
```bash
uv run langgraph dev
```

CLI 会读取根目录的 `langgraph.json`，并暴露名为 `tomorrow` 的 graph。

使用 `fragile` 命令行客户端进行单次提问：
```bash
uv run fragile "请介绍一下你的能力"
```

启动交互式会话：
```bash
uv run fragile interactive
```

通过 `--thread` 或 `-t` 传入 UUID 可以恢复已有会话；不传入时会自动创建新的线程。

## ⚙️ 配置

该项目使用 **Pydantic Settings** 进行配置管理。设置分别定义在 `src/tomorrow/settings.py` (Tomorrow) 和 `src/rainy/settings.py` (Rainy) 中，可以通过环境变量或 `.env` 文件进行覆盖。环境变量优先级最高，Tomorrow 使用 `TOMORROW_` 前缀，Rainy 使用 `RAINY_` 前缀。

### 环境变量

环境变量默认以前缀 `TOMORROW_` (核心模块) 或 `RAINY_` (API 模块) 开头。

#### Tomorrow 配置 (核心)
| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `TOMORROW_APP` | 应用名称（用作环境变量前缀） | `tomorrow` |
| `TOMORROW_MODEL` | 模型配置，支持 OLLAMA、HUGGINGFACE 和 ANTHROPIC | 当前 `.env` 使用 `anthropic` / `deepseek-v4-flash` |
| `TOMORROW_CHECKPOINT` | 检查点配置，支持 MEMORY 和 SQLITE | `{"type":"memory"}` |
| `TOMORROW_BACKEND` | 后端配置，支持 FILESYSTEM 和 LOCAL_SHELL | `{"type":"filesystem"}` |
| `TOMORROW_STORE` | 存储配置，支持 MEMORY 和 SQLITE | `{"type":"sqlite"}` |
| `TOMORROW_SKILLS` | 技能目录列表 | `["skills/"]` |
| `TOMORROW_SUBAGENTS` | 子代理配置列表 | `[]` |
| `TOMORROW_RECURSION_LIMIT` | 智能体递归调用上限 | `100` |

模型配置通过 `TOMORROW_MODEL` 或嵌套环境变量传入。当前 `.env` 使用 Anthropic 兼容接口和 `deepseek-v4-flash`；使用其他提供商时，请相应配置 `ollama` 或 `huggingface` 对象。例如：

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

具体字段和默认值请参阅 `src/tomorrow/settings.py`。

子代理配置通过 `TOMORROW_SUBAGENTS` 传入，每个子代理至少需要 `name`、`description` 和 `system_prompt` 字段，也可以指定 `model` 与 `skills`，例如：

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### Rainy 配置 (API)

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `RAINY_HOST` | API 服务监听地址 | `localhost` |
| `RAINY_PORT` | API 服务端口 | `8000` |
| `RAINY_APP` | 应用名称（用作环境变量前缀） | `rainy` |
| `RAINY_MIDDLEWARE` | 启用的中间件列表 | (见 settings.py) |

## 📜 脚本

常用的开发脚本：

- **检查与格式化代码**:
  ```bash
  uv run ruff check . --fix
  uv run ruff format .
  ```

- **手动运行 pre-commit 钩子**:
  ```bash
  uv run pre-commit run --all-files
  ```

## 📂 项目结构

- `src/main.py`: Rainy API 服务的主入口点。设置环境并启动 Uvicorn 服务器。
- `src/fragile/`: 命令行客户端包目录。
  - `app.py`: 提供单次提问和交互式会话命令，并支持通过线程 UUID 恢复会话。
- `src/tomorrow/`: 核心智能体包目录。
  - `graph.py`: `langgraph-cli` 使用的 graph 入口。
  - `core/agent.py`: 定义深度智能体及其指令，提供 `AgentManager` 进行生命周期管理。
  - `core/backend/`: 统一后端加载逻辑，支持 `FILESYSTEM` 和 `LOCAL_SHELL`。
  - `core/checkpoint/`: 检查点实现，支持 `MEMORY` 和 `SQLITE`。
  - `core/model/`: 模型加载实现，支持 `OLLAMA`、`HUGGINGFACE` 和 `ANTHROPIC`。
  - `core/store/`: 存储实现，支持 `MEMORY` 和 `SQLITE`。
  - `exceptions.py`: 定义应用特定的异常类体系。
  - `models/constants/`: 定义各类常量（Backend, Checkpoint, Model, Store）。
  - `settings.py`: 默认配置值。
  - `utils/functional.py`: 功能实用程序。
- `src/rainy/`: API 服务包目录。
  - `app.py`: FastAPI 应用定义，集成生命周期管理与路由。
  - `lifespan.py`: 处理应用的启动与关闭逻辑，管理智能体实例生命周期。
  - `api/endpoints/`: API 路由定义。
    - `chat.py`: 同步及流式聊天接口，集成了深度智能体模块（响应由中间件统一包装）。
      - `POST /api/chat`: 同步聊天响应。
      - `POST /api/chat/stream`: SSE 流式响应。
      - `POST /api/chat/stream/event`: 事件流响应。
    - `health.py`: 健康检查接口 (`GET /api/health`)。
    - `urls.py`: 统一路由挂载。
  - `middleware/`: 自定义中间件（处理时间、统一响应格式）。
  - `settings.py`: API 模块默认配置。
- `tests/`: 测试目录，结构与 `src` 保持一致。
- `docs/`: 多语言文档。
- `pyproject.toml`: 项目元数据、依赖项和工具配置。
- `langgraph.json`: `langgraph-cli` 的 graph 与环境配置。
- `uv.lock`: 锁定依赖版本。
- `LICENSE`: Apache License 2.0。

## 🧪 测试

项目使用 `pytest` 进行测试，并要求 **100%** 的测试覆盖率。

### 运行测试

- **运行 Tomorrow 测试**:
  ```bash
  PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
  ```

- **运行 Rainy 测试**:
  ```bash
  PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
  ```

- **运行 Fragile 测试**:
  ```bash
  PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/fragile
  ```

### 运行覆盖率测试

要求测试覆盖率必须达到 **100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 许可证

本项目采用 **Apache License 2.0** 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
