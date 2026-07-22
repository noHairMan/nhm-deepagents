# 智能体开发指南

## 1. 环境与配置
- **包管理**: 使用 `uv`。执行 `uv sync` 安装依赖。
- **配置管理**: 基于 `Pydantic Settings`。
  - `TOMORROW_APP` / `RAINY_APP`: 应用名/环境变量前缀。
- **模型配置**: 当前 `.env` 使用 Anthropic 兼容接口和 `deepseek-v4-flash`；Ollama 与 HuggingFace 为可选模型提供商。
- **路径与环境加载**:
  - 如果智能体无法找到某个命令，必须通过当前 Shell 的 **Login Shell** 模式执行，以强制加载完整的用户环境配置（比如说zsh -i -c "uv version"）。

## 2. 测试规范
- **框架**: `pytest`。
- **目录结构**: 测试文件按 `src/` 的模块路径组织，并与被测模块文件名保持一致。
- **命名规范**: 所有测试文件的名称必须与原模块中的文件名完全一致。
- **编写规范**: 必须使用以 `Test` 开头的测试类包裹测试方法。
- **运行测试**:
  - `tomorrow`:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
    ```
  - `rainy`:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
    ```
- **运行覆盖率测试**:
  ```bash
  PYTHONPATH=src \
  TOMORROW_APP=tomorrow \
  RAINY_APP=rainy \
  uv run coverage run --rcfile=pyproject.toml -m pytest
  ```

## 3. 编码规范
- **Lint & 格式化**: Ruff。
- **类型提示**: 必须为所有方法和函数添加明确的类型注释 (Type Hinting)，确保代码的类型安全。
- **核心文件**:
  - `src/tomorrow/core/agent.py`: Deep Agent 定义。
  - `src/tomorrow/conf/config.py`: 配置加载实现。
  - `src/tomorrow/settings.py`: `tomorrow` 默认配置。
  - `src/rainy/settings.py`: `rainy` 默认配置。
- **注意事项**: 修改配置项需同步更新 `settings.py`；环境变量优先级最高。

## 4. 智能体指令
- **测试覆盖率要求**:
  - 每次更改代码后，必须运行上述覆盖率测试命令。
  - 智能体必须确保生成对应的测试代码。
  - 测试覆盖率必须达到 **100%**。
- **文档维护**: 本文档是为代码编辑智能体设计的，仅包含智能体执行任务所需的关键技术信息。
- **修改原则**: 修改此文档时，应保持其简洁性，确保只保留必要的环境配置、测试规范和编码约束。

## 5. 文档更新规范
- **README 更新**:
  - 当需要更新 README 文档时，必须先通过 `git log` 查看自上次 README 修改以来的所有提交记录。
  - 重点关注当前开发者的提交记录（可通过 `git config user.name` 获取），总结功能变更、技术栈更新及项目结构调整。
  - 仅需更新中文文档（`docs/README.zh.md`），其余语言文档由 GitHub Action 自动翻译生成。
  - 更新内容应包括但不限于：模块说明、技术栈、配置参数、项目结构和测试指南。
