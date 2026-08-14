# 贡献指南

[简体中文](/docs/CONTRIBUTING.zh.md) | [English](/docs/CONTRIBUTING.en.md) | [日本語](/docs/CONTRIBUTING.ja.md) | [繁体中文](/docs/CONTRIBUTING.zh-TW.md)

本文档面向项目开发者和贡献者，介绍开发环境、代码结构、质量检查与测试方法。项目的背景、安装、运行和配置说明请参阅 [README](README.zh.md)。

## 🛠️ 技术栈

- **语言**: [Python](https://www.python.org/) >= 3.14
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **API 框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **Web 服务器**: [Uvicorn](https://www.uvicorn.org/)
- **智能体框架**: [deepagents](https://github.com/zongxuheng/deepagents)（基于 LangGraph/LangChain）
- **LLM 提供商**: [Ollama](https://ollama.com/) 和 [Anthropic](https://www.anthropic.com/)
- **代码执行**: [langchain-quickjs](https://github.com/langchain-ai/langchainjs) 提供的 QuickJS 中间件
- **终端交互**: `asyncclick`、`prompt-toolkit` 和 `Rich`
- **配置管理**: [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- **代码质量**: [Ruff](https://github.com/astral-sh/ruff)、`pre-commit` 和强制类型提示
- **测试与覆盖率**: `pytest`、`coverage`

## ⚙️ CI/CD

项目集成了 GitHub Actions 工作流，包括：

- **测试与覆盖率**: 自动运行测试并检查代码覆盖率。
- **文档翻译**: 自动将 `README.zh.md` 和 `CONTRIBUTING.zh.md` 翻译为 English、日本語和繁体中文。
- **代码规范**: 自动执行 `ruff` 检查与格式化，确保代码风格统一。
- **CI 流程优化**: 根据相关代码或配置变更触发构建，减少不必要的构建任务。

## 📜 开发脚本

同步依赖并创建虚拟环境：

```bash
uv sync
```

检查并格式化代码：

```bash
uv run ruff check . --fix
uv run ruff format .
```

手动运行 `pre-commit` 钩子：

```bash
uv run pre-commit run --all-files
```

## 📂 项目结构

- `src/main.py`: Rainy API 服务的主入口点。
- `src/fragile/`: 异步命令行客户端，包含交互式会话、斜线命令、显示和输入处理。
- `src/tomorrow/`: 核心智能体，实现 graph、模型、后端、检查点、存储和生命周期管理。
- `src/rainy/`: API 服务，实现应用生命周期、聊天接口、健康检查和中间件。
- `tests/`: 测试目录，结构与 `src` 保持一致。
- `docs/`: 多语言文档。
- `pyproject.toml`: 项目元数据、依赖项和工具配置。
- `langgraph.json`: `langgraph-cli` 的 graph 与环境配置。
- `uv.lock`: 锁定依赖版本。

## 🧪 测试

项目使用 `pytest` 进行测试，并要求测试覆盖率达到 **100%**。

运行各模块测试：

```bash
PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
```

运行完整覆盖率测试：

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest -q && uv run coverage report --rcfile=pyproject.toml
```

测试文件应按照 `src/` 的模块路径组织，并使用以 `Test` 开头的测试类包裹测试方法。
