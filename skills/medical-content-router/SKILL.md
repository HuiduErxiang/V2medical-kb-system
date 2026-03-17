---
name: medical-content-router
description: 医学内容路由器 — 唯一广义入口，负责意图识别与固定链路模板编排
---

# Medical Content Router

## 定位

本 Skill 是医学内容体系的**唯一广义 live 入口**，负责：

1. **主意图识别** — 判断用户需要查询、观点、写作、审核还是系列策划
2. **固定链路模板选择** — 从预定义模板中选择匹配的执行路径
3. **任务移交** — 将任务上下文移交给下游 `medical-writing` 或各子模块

**禁止事项**：
- 不定义文章原型（原型由 `medical-writing` 类目层负责）
- 不定义证据规则、证据分级规则（由知识库负责）
- 不定义审核标准、P0/P1/P2 分级（由知识库负责）
- 不重述项目控制面规则（控制面由 `系统运行.md` 承接）

---

## Triggers

当用户请求属于以下任一类型时，加载本技能：

### 组合请求
- "观点 + 写作 + 审核"
- "从这些证据形成观点 + 写篇文章"
- "查一下这个病的知识 + 写一篇"
- "帮我审核这篇文章 + 顺便改一改"
- "完整链路"
- "生成医学内容"
- "写一篇医学文章"（泛请求，未指定素材/原型/受众）
- "帮我写个医学内容"
- "写一篇关于 XX 的文章"

### 模糊请求
- "这个素材适合做什么"
- "帮我判断一下这个该怎么处理"
- "我有这些证据，能做什么"

### 先判断再执行的请求
- "先看看证据再决定写什么"
- "帮我规划一下这篇稿子"
- "这个产品适合做什么类型的内容"

---

## 控制握手（会话级 Owner）

**本 Skill 是链路首个 live 入口时，承担一次性控制握手责任。**

### 启动时必须执行

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

**第二步：初始化日志上下文**

按 DOC-017 执行日志分层保存：
- 能明确归属到独立项目时，优先写入项目目录下的 `项目日志/`
- 无法归属到具体项目时，写入 `写作项目运行日志/` 作为摘要索引

**第三步：向用户确认**

向用户确认："已读取系统运行并按当前日志机制准备记录，确认理解 SYS-001~016 与关键 DOC 规则。"

### 下游模块继承规则

下游被模板调用的 skill（如 `medical-writing`、`medical-opinion-generator` 等）：
- **只继承**：`control_context` 和 `log_context`
- **禁止再做**：
  - 第二次读取控制面
  - 第二次初始化日志
  - 重复启动确认

---

## 固定链路模板

本 Skill 只能从以下预定义模板中选择，**不允许临场发明自由工作流**。

### 单步模板

| 模板名 | 触发场景 | 链路 |
|--------|----------|------|
| `query_only` | 只查知识或证据 | `medical-database-query` |
| `opinion_only` | 只形成观点 | `medical-opinion-generator` |
| `review_only` | 只做审核 | `medical-article-reviewer` |
| `write_direct` | 已有素材，直接成稿 | `medical-writing` |

### 两步模板

| 模板名 | 触发场景 | 链路 |
|--------|----------|------|
| `query_to_write` | 先查再写 | `medical-database-query` → `medical-writing` |
| `opinion_to_write` | 先形成观点再写 | `medical-opinion-generator` → `medical-writing` |
| `review_then_rewrite` | 先审再改 | `medical-article-reviewer` → `medical-writing` |
| `planning_to_write` | 先判断原型或系列策划，再决定是否成稿 | `medical-writing`（策划模式）→ 可选进入成稿模式 |

**约束**：
- 每条模板最多 2 到 3 步，不再往上叠加自由节点
- 一旦模板选定，后续执行权移交给下游 live skill

---

## 最小 Handoff 契约

所有跨模块模板必须传递以下公共上下文：

### 公共字段
```json
{
  "route_template_id": "query_to_write | opinion_to_write | ...",
  "handoff_source": "medical-content-router",
  "control_context": { "已读取控制面": true, "owner": "medical-content-router" },
  "log_context": { "日志路径": "...", "会话ID": "..." }
}
```

### medical-writing 接收字段
```json
{
  "task_goal": "用户目标描述",
  "source_packet": { "素材或证据包" },
  "constraints_context": { "约束条件" },
  "prototype_hint": "建议原型（可选）",
  "rewrite_target": "改写目标（可选）",
  "target_audience": "目标受众（可选）"
}
```

**说明**：至少提供一个写作落点信号（`prototype_hint` / `rewrite_target` / `target_audience`）。

### 各模板特有字段

**query_to_write**:
```json
{
  "question": "原始问题",
  "results": [ "查询结果" ],
  "source_summary": "来源摘要",
  "recommended_register": "建议语体等级"
}
```

**opinion_to_write**:
```json
{
  "thesis": "核心主张",
  "support_points": [ "支撑点" ],
  "boundaries": [ "边界标注" ],
  "evidence_mapping": { "证据映射" }
}
```

**review_then_rewrite**:
```json
{
  "draft_ref_or_text": "待审稿件引用或文本",
  "review_findings": { "审核发现" },
  "severity_summary": { "P0": 0, "P1": 2, "P2": 3 },
  "rewrite_mode": "expand_patch | dedupe_patch | deepen_patch | mixed_patch",
  "locked_spans": [],
  "must_keep_claims": [],
  "must_delete_or_compress": [],
  "expand_targets": [],
  "dedupe_map": {},
  "evidence_gap_list": [],
  "style_guard": {},
  "word_budget": {
    "total_delta": { "min": -100, "max": +200 },
    "section_budgets": {}
  }
}
```

**说明**：`review_then_rewrite` 模板的完整字段定义参见 `medical_kb_system_v2/docs/contracts/revision_control_protocol_v1.md`。

**planning_to_write**:
```json
{
  "prototype_recommendation": "原型建议",
  "planning_rationale": "策划理由",
  "required_inputs": [ "所需输入" ],
  "write_decision": "是否进入成稿"
}
```

---

## 显式直写判定规则

以下情况**不允许**直达 `medical-writing`，必须先经过本 Router：

1. 用户只说"写一篇医学文章"而未提供：
   - 素材 (`source_packet`)
   - 原型提示 (`prototype_hint`)
   - 目标受众 (`target_audience`)
   - 改写目标 (`rewrite_target`)

2. 只有当上述 4 项中**至少具备 2 项**时，才允许直达 `medical-writing`

---

## 工作流

```
用户触发本 Skill
    ↓
识别主意图（查询/观点/写作/审核/系列策划）
    ↓
选择固定链路模板
    ↓
执行一次性控制握手（读取控制面、初始化日志、确认）
    ↓
构建 handoff payload（包含公共字段 + 模板特有字段）
    ↓
移交任务给下游 skill
    ↓
下游执行（继承 control_context 和 log_context）
    ↓
交付结果
```

---

## 与其他 Skill 的关系

| Skill | 关系 | 说明 |
|-------|------|------|
| `medical-writing` | 下游类目层 | 本 Router 将明确写作任务移交给它；它不再承担广义入口职责 |
| `medical-opinion-generator` | 下游子模块 | 独立观点产出，或作为 `opinion_to_write` 模板的前序步骤 |
| `medical-article-reviewer` | 下游子模块 | 独立审核，或作为 `review_then_rewrite` 模板的前序步骤 |
| `medical-database-query` | 下游子模块 | 独立查询，或作为 `query_to_write` 模板的前序步骤 |

---

## 注意事项

1. **入口唯一化**：本 Skill 上线后，所有模糊/组合/多步请求只允许命中本 Router
2. **显式直写阈值**：`medical-writing` 的直写入口必须满足素材/原型/受众/改写目标至少 2 项
3. **控制握手单次**：本 Skill 是链路唯一 owner，下游不得重复握手
4. **模板固定**：不得临场发明超出预定义模板的工作流

---

# End of Skill