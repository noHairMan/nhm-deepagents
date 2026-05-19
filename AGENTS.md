# 开发者指南 (AGENTS.md)

本文档旨在为开发人员提供关于 `nhm-deepagents` 项目的构建、测试及开发的详细信息。

## 1. 构建与配置说明

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理和环境管理工具。

### 环境设置
1.  **安装依赖**:
    使用 `uv sync` 命令来同步依赖并创建虚拟环境。
    ```bash
    uv sync
    ```
2.  **配置环境**:
    项目使用 `Dynaconf` 进行配置管理，通过环境变量控制加载行为。
    - `TOMORROW_APP`: 定义应用名称（同时作为环境变量前缀，默认值为 `tomorrow`）。
    - `TOMORROW_SETTINGS_MODULE`: 定义设置文件的模块路径或文件路径。

### 运行时依赖
- **Ollama**: 必须安装并运行 Ollama 服务。
- **模型**: 默认需要 `qwen3.5:9b`。
  ```bash
  ollama pull qwen3.5:9b
  ```

## 2. 测试指南

项目使用 `pytest` 作为测试框架。

### 运行测试
由于源代码位于 `src` 目录，且配置加载依赖于环境变量，在项目根目录下运行测试时建议使用以下命令：
```bash
PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=src.tomorrow.settings uv run pytest
```

### 添加新测试
- 测试文件应存放在 `tests/` 目录下，并以 `test_*.py` 命名。
- 若需要测试涉及 LLM 的异步逻辑，建议使用 `pytest-asyncio`。

### 测试示例
以下是一个验证配置加载和模型实例化的简单示例（已验证通过）：

```python
from tomorrow.core.agent import get_model
from langchain_ollama import ChatOllama

def test_get_model_initialization():
    """验证模型实例是否能根据给定名称正确创建"""
    model_name = "test-model"
    model = get_model(model_name)
    assert isinstance(model, ChatOllama)
    assert model.model == model_name
```

## 3. 额外开发信息

### 代码规范
- **格式化**: 项目遵循 Black 格式化规范，行宽设置为 **120**。
- **导入排序**: 使用 Isort 进行导入排序，配置与 Black 兼容。
- **静态检查**: 建议安装 `pre-commit` 钩子。
  ```bash
  uv run pre-commit install
  ```

### 项目核心结构
- `src/tomorrow/core/agent.py`: 包含深度智能体（Deep Agent）的定义。
- `src/tomorrow/utils/conf.py`: 封装了基于 Dynaconf 的配置加载逻辑。
- `src/tomorrow/settings.py`: 存储项目的默认配置项。

### 开发注意事项
- 修改配置项后，请务必更新 `src/tomorrow/settings.py`。
- 环境变量加载具有高优先级，默认前缀为 `TOMORROW_`。
