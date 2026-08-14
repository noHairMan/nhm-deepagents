---
name: configuration-management
description: 配置项、设置模块或环境变量任务的专项规范。
---

# 配置管理

## 触发条件

任务涉及应用配置、环境变量、设置加载或 `settings.py` 时读取本技能。

## 执行规范

- 使用 Pydantic Settings 管理配置。
- 默认配置文件分别为 `src/tomorrow/settings.py`、`src/rainy/settings.py` 和 `src/fragile/settings.py`。
- 三个应用前缀分别为 `TOMORROW_APP`、`RAINY_APP` 和 `FRAGILE_APP`；修改配置项时同步检查对应设置模块。
- 遵循环境变量优先级，不把本地 `.env` 内容或密钥写入仓库。

## 验证

确认设置模块、前缀和优先级与现有实现一致，并运行受影响的配置或应用测试。
