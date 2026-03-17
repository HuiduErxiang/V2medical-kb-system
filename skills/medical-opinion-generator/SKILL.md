---
name: medical-opinion-generator
description: 医学观点产出技能 — 触发后加载知识库规则
---

# Medical Opinion Generator

## Triggers

当用户**仅需要观点产出**，且**不涉及写作和审核**时，加载本技能：

- "产出一个医学观点"
- "帮我提炼一个核心论点"
- "这个数据说明了什么问题"
- "从这篇文献里能得出什么结论"
- "出几个 topic"
- "分析这个临床问题，应该怎么下结论"
- "单独调用观点产出"

**注意**：如果用户同时要求"写文章"、"审核"、"生成完整内容"，请调用 `medical-content-router` skill。

---

## 控制握手（双模式）

**本 Skill 可能以两种模式被调用**：

### 模式一：单独直接调用

当用户直接触发本 Skill（不经过 `medical-content-router`）时，执行完整控制握手：

**第一步：读取运行时规则**

立即读取以下文件：
```
D:/汇度编辑部1/写作知识库/project_standards/must_read/system_operations.md
```

必须确认已读并理解：
- 铁律与约束（SYS-001 ~ SYS-016）
- `workflow-gate` 入口与触发时机
- 文档地图
- 项目日志机制

**第二步：按当前规则创建日志并确认口径**

- 按 DOC-017 执行日志分层保存：
  - 能明确归属到独立项目时，优先写入项目目录下的 `项目日志/`
  - 无法归属到具体项目时，写入 `写作项目运行日志/` 作为摘要索引
- 向用户确认："已读取系统运行并按当前日志机制准备记录，确认理解 SYS-001~016 与关键 DOC 规则。"

### 模式二：作为 Router 下游调用

当由 `medical-content-router` 通过 `opinion_to_write` 等模板调用时，**只继承上下文，不重复握手**：

**接收的 Handoff 字段**：
```json
{
  "route_template_id": "opinion_to_write | ...",
  "handoff_source": "medical-content-router",
  "control_context": { "已读取控制面": true, "owner": "medical-content-router" },
  "log_context": { "日志路径": "...", "会话ID": "..." }
}
```

**禁止再做**：
- ❌ 第二次读取控制面文档
- ❌ 第二次初始化日志
- ❌ 重复启动确认

**只允许**：
- ✅ 继承 `control_context` 和 `log_context`
- ✅ 在既有日志上下文里追加模块级执行记录
- ✅ 基于上游 payload 继续完成观点产出任务

---
## 工作流

### 单独直接调用模式
```
用户直接触发本 Skill
    ↓
读取系统运行.md（铁律、workflow-gate、文档地图、项目日志机制）
    ↓
按 DOC-017 准备日志记录位置
    ↓
向用户确认已理解规则
    ↓
获取原始证据 / 数据
    ↓
解构证据（事实层 → 推断层 → 观点层）
    ↓
生成核心观点 + 支撑点 + 边界标注
    ↓
交付观点产出报告
```

### Router 下游调用模式
```
medical-content-router 调用本 Skill
    ↓
继承 control_context 和 log_context
    ↓
基于 handoff payload 获取证据
    ↓
解构证据（事实层 → 推断层 → 观点层）
    ↓
生成核心观点 + 支撑点 + 边界标注
    ↓
交付观点产出报告（含结构化输出字段）
```

---

---

## 与知识库的关系

- **本 Skill**: 只负责"什么时候触发观点产出"
- **知识库**: 负责"怎么产出" + "证据分级" + "所有规则"

如果知识库规则与 Skill 内部任何描述矛盾，**以知识库为准**。

---

## 输出给下游的结构化字段

当本 Skill 的结果需要传递给 `medical-writing` 进行写作时，必须输出以下字段（`opinion_to_write` 模板契约）：

```json
{
  "thesis": "核心主张（一句话）",
  "support_points": [
    { "point": "支撑点1", "evidence_ref": "证据来源" },
    { "point": "支撑点2", "evidence_ref": "证据来源" }
  ],
  "boundaries": [
    { "boundary": "边界1", "reason": "边界原因" }
  ],
  "evidence_mapping": {
    "主张A": "证据X",
    "主张B": "证据Y"
  }
}
```

**说明**：
- `thesis`：全文核心主张，必须是可被验证的明确判断
- `support_points`：支撑核心主张的分论点，每项需标注证据来源
- `boundaries`：主张的适用范围、局限、不确定领域
- `evidence_mapping`：主张与证据的映射关系

---

# End of Skill