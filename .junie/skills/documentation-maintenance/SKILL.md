---
name: documentation-maintenance
description: README、贡献指南或项目文档维护任务的专项规范。
---

# 文档维护

## 触发条件

任务涉及 `README`、`CONTRIBUTING`、`docs/`、文档链接或文档自动翻译时读取本技能。

## 执行规范

- `CONTRIBUTING.md` 作为开发规范的详细事实来源；常驻入口只引用按需规则，不复制完整贡献文档。
- 仅更新以下中文源文档：`docs/README.zh.md` 和 `docs/CONTRIBUTING.zh.md`；其他多语言文档依赖自动化翻译生成或同步，不手工维护。
- 修改前确认目标文件存在，并保留上述项目既有路径约定。
- 需要了解文档演变时，只查询与目标文件直接相关的 Git 历史，避免无关历史扫描。

## 验证

检查 Markdown 结构、相对链接、路径和规则与 `CONTRIBUTING.md`、`pyproject.toml` 及工作流一致；记录未运行的业务测试。
