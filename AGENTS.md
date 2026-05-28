# 智能体开发指南 (AGENTS.md)

## 1. 环境与配置
- **包管理**: 使用 `uv`。执行 `uv sync` 安装依赖。
- **配置管理**: 基于 `Dynaconf`。
  - `TOMORROW_APP` / `RAINY_APP`: 应用名/环境变量前缀。
  - `TOMORROW_SETTINGS_MODULE` / `RAINY_SETTINGS_MODULE`: 设置模块路径。
- **运行时依赖**: 必须运行 Ollama，默认模型 `qwen3.5:9b`。

## 2. 测试规范
- **框架**: `pytest`。
- **目录结构**: `tests/` 与 `src/` 严格对应（路径与文件名一致）。
- **编写规范**: 必须使用以 `Test` 开头的测试类包裹测试方法。
- **运行测试**:
  ```bash
  PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings uv run pytest
  ```

## 3. 编码规范
- **格式化**: Black (line-length = 120)。
- **排序**: Isort (与 Black 兼容)。
- **核心文件**:
  - `src/tomorrow/core/agent.py`: Deep Agent 定义。
  - `src/tomorrow/conf/config.py`: 配置加载实现。
  - `src/tomorrow/settings.py`: `tomorrow` 默认配置。
  - `src/rainy/settings.py`: `rainy` 默认配置。
- **注意事项**: 修改配置项需同步更新 `settings.py`；环境变量优先级最高。

## 4. 智能体指令
- **文档维护**: 本文档 (`AGENTS.md`) 是为代码编辑智能体设计的，仅包含智能体执行任务所需的关键技术信息。
- **修改原则**: 修改此文档时，应保持其简洁性，确保只保留必要的环境配置、测试规范和编码约束。
