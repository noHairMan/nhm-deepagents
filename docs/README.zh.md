# nhm-deepagents

[简体中文](/docs/README.zh.md) | [English](/docs/README.en.md) | [日本語](/docs/README.ja.md) | [繁体中文](/docs/README.zh-TW.md)

一个使用现代 LLM 框架构建和运行“深度智能体”（Deep Agents）的 Python 项目。

## 🌟 项目概览

`nhm-deepagents` 是一个专注于深度智能体的专业 Python 项目。它利用现代 Python 特性 (3.14+) 和强大的工具，为 AI 智能体研究和应用提供高质量的开发体验。

该项目目前包含一个心理专家智能体，可以使用 `deepagents` 框架分析用户输入并提供建议。

## 🛠️ 技术栈

- **语言**: [Python](https://www.python.org/) >= 3.14
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **智能体框架**: [deepagents](https://github.com/zongxuheng/deepagents) (基于 LangGraph/LangChain)
- **LLM 提供商**: [Ollama](https://ollama.com/) (通过 `langchain-ollama`)
- **配置管理**: [Dynaconf](https://www.dynaconf.com/)
- **代码质量**: `black`, `isort`, `pre-commit`

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

### 运行应用

运行主入口点：
```bash
uv run python src/main.py
```

## ⚙️ 配置

该项目使用 **Dynaconf** 进行配置管理。设置定义在 `src/tomorrow/settings.py` 中，可以通过环境变量或 `.env` 文件进行覆盖。

### 环境变量

环境变量默认以前缀 `TOMORROW_` 开头。

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `TOMORROW_OLLAMA_BASE_URL` | Ollama 服务的基地址 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL` | 默认使用的 LLM 模型 | `qwen3.5:9b` |
| `TOMORROW_APP` | 应用名称（用作环境变量前缀） | `tomorrow` |
| `TOMORROW_SETTINGS_MODULE` | 设置模块的路径 | `tomorrow.settings` |

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

- `src/main.py`: 应用的主入口点。设置环境并调用智能体。
- `src/tomorrow/`: 核心包目录。
  - `core/agent.py`: 定义深度智能体及其指令。
  - `settings.py`: 默认配置值。
  - `utils/conf.py`: Dynaconf 初始化逻辑。
  - `utils/functional.py`: 功能实用程序（例如 `SimpleLazyObject`）。
- `docs/`: 多语言文档。
- `pyproject.toml`: 项目元数据、依赖项和工具配置。
- `uv.lock`: 锁定依赖版本。
- `LICENSE`: Apache License 2.0。

## 🧪 测试

- TODO: 使用 `pytest` 实现单元测试和集成测试。
- TODO: 添加用于自动测试的 CI 流程。

运行测试（实现后）：
```bash
uv run pytest
```

## 📄 许可证

本项目采用 **Apache License 2.0** 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
