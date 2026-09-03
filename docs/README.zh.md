# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python Version](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)
[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[简体中文](/docs/README.zh.md) | [English](/docs/README.en.md) | [日本語](/docs/README.ja.md) | [繁体中文](/docs/README.zh-TW.md)

![Fragile banner](/docs/images/fragile.png)

一个使用现代 LLM 框架构建和运行“深度智能体”（Deep Agents）的 Python 项目。

开发环境、项目结构、代码规范和测试方法请参阅[贡献指南](CONTRIBUTING.zh.md)。

## 🌟 项目概览

`nhm-deepagents` 是一个专注于深度智能体的专业 Python 项目。它利用 Python 3.14 和强大的工具，为 AI 智能体研究和应用提供高质量的开发体验。

项目内部包含三个主要模块：
- **`tomorrow`**: 核心智能体模块。代号取自游戏《死亡搁浅 2：冥滩之上》（Death Stranding 2: On the Beach）中的角色 **Tomorrow**（由艾丽·范宁饰演）。在剧情中，她是主角山姆·布里吉斯（Sam Bridges）的女儿，也被揭示为前作中的 **Lou** (BB-28)。
- **`rainy`**: 基于 FastAPI 的 API 服务模块。代号同样取自《死亡搁浅 2》中的角色 **Rainy**（由忽那汐里饰演）。在游戏中，她拥有引发“时间雨”（Timefall）和具有治愈能力的“核心雨”（Corefall）的神奇力量，被描述为既能伤害也能治愈的“药（Pharmakon）”。
- **`fragile`**: 基于 `asyncclick` 的异步命令行客户端，用于直接向 Tomorrow 智能体提问或启动交互式会话。其名称取自同一作品中的角色 **Fragile**。Fragile 是 Fragile Express 的创始人和快递员，因接触时间雨而快速衰老，却始终在危险环境中为他人运送重要物资；这种“脆弱”外表下仍坚持承担连接与传递使命的形象，正是该客户端名称的背景。

该项目提供了一个通用的智能助理智能体，利用 `deepagents` 框架分析用户输入，并通过 `rainy` 模块对外提供同步（`/api/chat`）及**流式（`/api/chat/stream`）** API 接口。

### 核心功能
- **深度智能体**: 集成 `deepagents` 框架，支持复杂任务处理与状态管理。
- **技能模块**: 支持通过 `TOMORROW_SKILLS` 配置技能目录，为智能体加载可扩展的领域能力。
- **子代理**: 支持通过 `TOMORROW_SUBAGENTS` 配置专用子代理及其模型、技能和系统提示词。
- **递归控制**: 支持通过 `TOMORROW_RECURSION_LIMIT` 限制智能体递归调用深度。
- **生命周期管理**: 引入 `AgentManager` 统一管理智能体实例的创建与销毁，确保资源的优雅初始化。
- **高性能 API**: 基于 FastAPI 构建，支持同步响应与 Server-Sent Events (SSE) 流式输出。
- **交互式 CLI**: `fragile` 支持 `/new` 创建新会话、`/history` 浏览并切换已持久化的历史会话、`/account` 配置外部模型账户、`/model` 选择模型、`/quit` 退出、会话恢复、输入历史、斜线命令补全和多行编辑，并以追加式时间线显示模型摘要、工具调用、命令结果和最终答案。
- **账户配置持久化**: 支持通过交互式命令保存 Anthropic 和 OpenAI 的 API 凭据，并在后续会话中自动恢复。
- **可靠性保障**: 强制类型提示、Ruff 静态检查、100% 测试覆盖率要求。

## 🛠️ 技术栈

- **语言**: [Python](https://www.python.org/) >= 3.14, < 3.15
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **API 框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **Web 服务器**: [Uvicorn](https://www.uvicorn.org/)
- **智能体框架**: [deepagents](https://github.com/zongxuheng/deepagents) (基于 LangGraph/LangChain)
- **LLM 提供商**: [Anthropic](https://www.anthropic.com/) 和 [OpenAI](https://openai.com/)
- **终端交互**: [asyncclick](https://github.com/python-trio/asyncclick) 提供异步 CLI 命令、参数解析和帮助信息；[prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) 提供异步输入、输入历史、命令补全和多行编辑；[Rich](https://github.com/Textualize/rich) 提供终端输出样式。
- **配置管理**: [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- **异常处理**: 自定义异常体系 (`TomorrowError` 及其子类)，涵盖模型、后端、存储和检查点错误。
- **代码质量**: [Ruff](https://github.com/astral-sh/ruff) (替代 Black 和 Isort)、`pre-commit`、强制类型提示 (Strict Type Hinting)
- **测试与覆盖率**: `pytest`, `coverage`

## 📋 环境要求

- **Python 3.14（不支持 3.15 及更高版本）**
- **uv**: 一个快速的 Python 包安装和解析器。
- **LLM 提供商**: 支持 Anthropic 和 OpenAI 兼容接口，需要通过环境变量或 `.env` 配置 API Key。
- **LLM 模型**: 默认使用 Anthropic 的 `claude-sonnet-5`，也可以通过 `TOMORROW_MODEL__TYPE` 切换到 OpenAI。

## 🚀 快速入门

### 安装

1. **安装 `uv`**:
   请按照 [uv 官方仓库](https://github.com/astral-sh/uv)中的说明进行操作。

2. **克隆仓库**:
   ```bash
   git clone https://github.com/noHairMan/nhm-deepagents.git
   cd nhm-deepagents
   ```

3. **同步依赖并创建虚拟环境**:
   ```bash
   uv sync
   ```

4. **安装 `fragile` 命令**:
   ```bash
   uv tool install .
   ```

   安装完成后，可以直接使用 `fragile` 命令启动命令行客户端。

### 运行应用

运行主入口点：
```bash
uv run python src/main.py
```

该命令启动 Rainy API，默认监听 `http://localhost:8000`。也可以使用 Uvicorn 直接启动：

```bash
uv run uvicorn main:app --app-dir src --host localhost --port 8000
```

使用 `langgraph-cli` 启动智能体 API 服务：
```bash
uv run langgraph dev
```

CLI 会读取根目录的 `langgraph.json`，并暴露名为 `tomorrow` 的 graph。

Rainy API 的请求体包含必填的 `message` 字段和可选的会话 `thread_id`。同步接口返回智能体的最终回复：

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"你好"}'
```

需要逐步接收回复时，可调用 `/api/chat/stream` 获取 SSE 数据流；`/api/chat/stream/event` 会返回更完整的 LangGraph 事件流。健康检查接口为 `GET /api/health`。

使用 `fragile` 命令行客户端启动交互式会话：
```bash
fragile
```

如果尚未使用 `uv tool install .` 安装命令，也可以在项目环境中运行：
```bash
uv run fragile
```

通过 `--thread` 或 `-t` 传入 UUID 可以恢复已有会话；不传入时会自动创建新的线程。交互过程中输入 `/new` 可清屏并开始新会话，输入 `/history` 可查看已保存的会话并按编号或 UUID 切换，输入 `/quit` 退出；也可以连续两次按 `Ctrl+C` 在短时间内退出会话，按 `Esc` 后回车可插入换行。

#### Fragile 输出时间线

每次普通对话都会按执行顺序追加显示以下区块：

- `Thinking (provider summary)`：仅显示模型提供商明确返回的 thinking/reasoning 摘要，不推断或生成私有思维链。
- `Tool`：显示工具名称、脱敏后的参数和运行状态；`execute` 还会突出显示实际命令。
- `Completed` / `Failed`：显示工具结果或失败信息；过长内容会在终端中标记截断。
- `Assistant`：最终答案仍按模型返回的片段连续流式输出。

工具、命令、阶段和模型摘要会与答案一起保存，使用 `/history` 切换会话时按原顺序回放。时间线采用与全屏输入兼容的追加式输出，不使用动态分屏面板；参数、结果和错误中的 API Key、Authorization、密码及 URL 凭据会先脱敏后显示和保存。

首次使用其他模型提供商时，可在交互会话中输入 `/account`，按提示选择提供商并填写 Base URL 和 API Key。模型名称等其他配置仍通过 `TOMORROW_MODEL` 或对应的环境变量设置。凭据会持久化到本地数据库，后续启动 `fragile` 时自动恢复；如需修改配置，再次执行 `/account` 即可。

`fragile` 的 CLI 入口和 `purge` 子命令均使用异步命令函数，避免在已运行的事件循环中嵌套调用 `asyncio.run()`。清理已持久化的会话记录：

```bash
fragile purge
```

## ⚙️ 配置

该项目使用 **Pydantic Settings** 进行配置管理。设置分别定义在 `src/tomorrow/settings.py` (Tomorrow)、`src/rainy/settings.py` (Rainy) 和 `src/fragile/settings.py` (Fragile) 中，可以通过环境变量或 `.env` 文件进行覆盖。环境变量优先级最高，三个模块分别使用 `TOMORROW_`、`RAINY_` 和 `FRAGILE_` 前缀；也可以通过 `TOMORROW_ENV_FILE`、`RAINY_ENV_FILE` 或 `FRAGILE_ENV_FILE` 指定配置文件路径。

### 环境变量

环境变量默认以前缀 `TOMORROW_` (核心模块)、`RAINY_` (API 模块) 或 `FRAGILE_` (CLI 模块) 开头。

#### Tomorrow 配置 (核心)
| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `TOMORROW_APP` | 应用名称（用作环境变量前缀） | `tomorrow` |
| `TOMORROW_MODEL` | 模型配置，支持 `ANTHROPIC` 和 `OPENAI` | `anthropic` / `claude-sonnet-5` |
| `TOMORROW_CHECKPOINT` | 检查点配置，支持 MEMORY 和 SQLITE | `{"type":"memory"}` |
| `TOMORROW_BACKEND` | 后端配置，支持 FILESYSTEM 和 LOCAL_SHELL | `{"type":"filesystem"}` |
| `TOMORROW_STORE` | 存储配置，支持 MEMORY 和 SQLITE | `{"type":"sqlite"}` |
| `TOMORROW_SKILLS` | 技能目录列表 | `[]` |
| `TOMORROW_SUBAGENTS` | 子代理配置列表 | `[]` |
| `TOMORROW_RECURSION_LIMIT` | 智能体递归调用上限 | `100` |
| `TOMORROW_MODEL__ANTHROPIC__THINKING_ENABLED` | 是否请求 Anthropic thinking 输出 | `false` |
| `TOMORROW_MODEL__ANTHROPIC__THINKING_BUDGET_TOKENS` | Anthropic thinking 的 token 预算（启用时必填） | 未设置 |
| `TOMORROW_MODEL__OPENAI__REASONING_EFFORT` | OpenAI reasoning 强度：`low`、`medium` 或 `high` | 未设置 |
| `TOMORROW_MODEL__OPENAI__REASONING_SUMMARY` | OpenAI reasoning 摘要：`auto`、`concise` 或 `detailed` | 未设置 |

模型配置通过 `TOMORROW_MODEL` 或嵌套环境变量传入。默认使用 Anthropic 的 `claude-sonnet-5`，也可以配置 Anthropic 兼容接口。例如：

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://api.anthropic.com"
export TOMORROW_MODEL__ANTHROPIC__MODEL="claude-sonnet-5"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

选择 OpenAI 或兼容 OpenAI API 的服务时，可以使用以下嵌套环境变量配置模型名、API Key、可选的 Base URL 和温度：

```bash
export TOMORROW_MODEL__TYPE="openai"
export TOMORROW_MODEL__OPENAI__MODEL="gpt-4o-mini"
export TOMORROW_MODEL__OPENAI__API_KEY="your-api-key"
export TOMORROW_MODEL__OPENAI__BASE_URL="https://api.openai.com/v1"
export TOMORROW_MODEL__OPENAI__TEMPERATURE="0"
```

thinking/reasoning 默认关闭。需要在 `fragile` CLI 中查看模型明确返回的 thinking 或 reasoning 摘要时，按提供商配置对应参数；该功能可能增加 token 消耗和响应延迟。例如：

```bash
export TOMORROW_MODEL__ANTHROPIC__THINKING_ENABLED="true"
export TOMORROW_MODEL__ANTHROPIC__THINKING_BUDGET_TOKENS="2048"

export TOMORROW_MODEL__OPENAI__REASONING_EFFORT="medium"
export TOMORROW_MODEL__OPENAI__REASONING_SUMMARY="auto"
```

Fragile 只展示提供商返回的 thinking/reasoning 内容，不会生成或推断模型未返回的内部思考；Rainy API 的现有响应协议不受影响。未配置或模型不支持对应能力时，仍只显示最终答案。thinking/reasoning 可能增加 token 消耗和响应延迟，具体内容取决于模型提供商。

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
| `RAINY_MIDDLEWARE` | 启用的中间件列表 | 统一响应格式、处理时间 |
| `RAINY_UNIFY_RESPONSE_FORMAT_EXCLUDE` | 不进行统一响应包装的路径 | `/docs`、`/redoc`、`/openapi.json` |
| `RAINY_LOG_LEVEL` | 日志级别 | `INFO` |

#### Fragile 配置 (CLI)

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `FRAGILE_APP` | 应用名称（用作环境变量前缀） | `fragile` |
| `FRAGILE_INTERRUPT_EXIT_THRESHOLD` | 两次 `Ctrl+C` 触发退出的最大间隔（秒） | `0.5` |
| `FRAGILE_ENABLED_COMMANDS` | 启用的交互式命令类路径列表 | `quit`、`new`、`history`、`account`、`model` |

Fragile 的其他交互行为通过命令行选项和内置斜线命令控制。命令通过注册表统一发现和处理，可使用 `FRAGILE_ENABLED_COMMANDS` 调整启用的命令。账户凭据由 `Account` 模型以单例形式保存于 Fragile 的数据库中，启动交互会话时会恢复到 Tomorrow 的模型配置；环境变量仍可作为配置来源并拥有更高优先级。

## 📄 许可证

本项目采用 **Apache License 2.0** 许可证。详情请参阅 [LICENSE](/LICENSE) 文件。
