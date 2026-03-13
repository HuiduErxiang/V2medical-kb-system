# Skills 目录说明

本目录是医学编辑智能写作系统 V2 的技能定义入口。

---

## 当前状态

**本目录为 V2 默认技能入口。**

当前阶段，V2 技能定义采取以下策略：

1. **核心技能**：通过 OpenCode 配置管理，不在此目录复制
2. **技能发现**：由 OpenCode 自动发现用户安装的技能
3. **历史技能**：V1 技能保留在 `medical_kb_system/skills/`，用于历史追溯

---

## 已安装的技能

以下技能通过 OpenCode 配置管理，可直接使用：

| 技能名称 | 用途 |
|----------|------|
| `medical-article-reviewer` | 医学文章审核 |
| `medical-database-query` | 医学数据库查询 |
| `medical-opinion-generator` | 医学观点生成 |
| `medical-writing` | 医学写作 |
| `code-review-workflow` | 代码审查工作流 |
| `commit-workflow` | 提交工作流 |
| `markitdown-converter` | Markdown 转换器 |
| `pandoc-converter` | 文档格式转换 |
| `scaffold-workflow` | 脚手架工作流 |

---

## V1 技能说明

V1 技能保留在 `medical_kb_system/skills/` 目录，包含：

- `isolation_l1_writing_craft.md`
- `isolation_l2_medical_playbook.md`
- `isolation_knowledge_l3_l4.md`
- `medical_article_generator_v2.md`
- `medical-article-reviewer.md`
- `medical-database-query.md`
- `medical-opinion-generator.md`
- `semantic_review_workflow.md`
- `article-knowledge-base-builder.md`
- `recursive-word-count-validator.md`

> **注意**：V1 已进入只读/归档计划状态，上述技能仅供历史追溯。

---

## 技能使用方式

通过 OpenCode 的 `skill` 工具调用：

```
skill(name="medical-writing")
```

或在对话中请求 AI 使用特定技能。

---

## 维护说明

- **最后更新**: 2026-03-10
- **状态**: V2 默认技能入口