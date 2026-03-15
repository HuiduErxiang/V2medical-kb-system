---
name: medical-writing
description: 医学写作类目 — 稳定可复用的医学写作能力
---

# Medical Writing Skill

## 定位

本 Skill 是医学写作**类目层**，不再承担广义总入口职责。

它只接受两类请求：
1. **显式直写请求** — 用户已明确要直接成稿，且写作目标、素材或下游输入已基本齐备
2. **模板内下游调用** — 由 `medical-content-router` 或既定模板显式转入写作类目

---

## Triggers

### 显式直写请求

只有当以下条件**至少满足 2 项**时，才允许直达本 Skill：

| 字段 | 说明 |
|------|------|
| `source_packet` | 用户已提供素材、明确证据包，或 query/opinion/review/planning 的结构化结果 |
| `prototype_hint` | 已指定文章原型（如证据解读稿、患教稿、观点社论稿） |
| `target_audience` | 已明确目标受众（专科医师、患者、大众等） |
| `rewrite_target` | 已明确改写目标（基于审核结果改写） |

**触发示例**：
- "基于这些证据写一篇 R3 级专科医师稿"（有素材 + 受众）
- "按证据解读稿原型写出这篇文章"（有原型 + 素材）
- "根据审核报告改写这篇稿件"（有改写目标）

### 模板内下游调用

本 Skill 也接受以下模板的下游调用：
- `query_to_write` — 来自 `medical-database-query` 的查询结果
- `opinion_to_write` — 来自 `medical-opinion-generator` 的观点产出
- `review_then_rewrite` — 来自 `medical-article-reviewer` 的审核结果
- `planning_to_write` — 来自策划模式的原型建议

---

## 入口分流规则

**模糊/组合/多步请求**：请调用 `medical-content-router`

包括但不限于：
- 用户只说"写一篇医学文章"而未提供素材、原型、受众或改写目标
- 用户要求先查询/先形成观点/先审核再写作
- 用户要求多项能力组合执行

**单一能力请求**：
- 仅需观点产出（不写文章）→ 调用 `medical-opinion-generator`
- 仅需审核（不写作）→ 调用 `medical-article-reviewer`
- 仅需查询（不写作）→ 调用 `medical-database-query`

---

## 文章原型（MVP 三原型）

本类目当前支持以下 3 种文章原型。原型决定文章的结构、语感和审核标准。

### 证据解读稿

| 要素 | 定义 |
|------|------|
| **适用场景** | 新研究解读、会议数据呈现、关键临床试验结果传播 |
| **默认结构** | 研究问题 → 核心结果 → 局限与边界 → 临床启示 |
| **证据密度要求** | 高（需 R1-R3 级证据支撑，数据来源可追溯） |
| **结尾动作** | 结论 + 风险边界提示（如"需进一步验证"、"仅适用于..."） |
| **最小输入要求** | `source_packet`（研究证据/数据）+ `prototype_hint`（指定本原型） |

**写作策略**：
- 开篇：点明研究问题与临床意义
- 中段：精准呈现数据，标注来源与证据等级
- 边界段：明确研究局限、适用人群、对比基准
- 结尾：可落地的临床启示，附带风险提示

### 患者教育稿

| 要素 | 定义 |
|------|------|
| **适用场景** | 患者教育、照护者指导、基层医务人员培训、大众科普 |
| **默认结构** | 问题解释 → 影响说明 → 应对建议 |
| **证据密度要求** | 中（需 R2-R4 级，允许简化表述，但不得误导） |
| **结尾动作** | 可执行的行动建议 + 风险提示 |
| **最小输入要求** | `source_packet` 或 `target_audience=患者/照护者/大众` |

**写作策略**：
- 开篇：用日常语言定义问题，避免术语堆砌
- 中段：解释影响时结合生活场景，使用比喻或类比
- 建议段：具体可执行，如"每天运动 X 分钟"、"出现 Y 症状需就医"
- 结尾：强调患者可做什么，附带"不确定时咨询医生"

**禁止事项**：
- 不得过度承诺疗效
- 不得用绝对化用语
- 不得省略风险与限制提示

### 观点社论稿

| 要素 | 定义 |
|------|------|
| **适用场景** | 行业趋势判断、证据立场表达、学术观点输出、政策评论 |
| **默认结构** | 核心立场 → 证据支撑 → 反例/边界 → 判断收束 |
| **证据密度要求** | 中高（需证据闭环，主张必须有支撑） |
| **结尾动作** | 立场收束（明确判断，开放讨论空间） |
| **最小输入要求** | `source_packet`（支撑素材）+ `prototype_hint` 或 `target_audience=行业从业者` |

**写作策略**：
- 开篇：明确亮出立场，一句话核心主张
- 中段：证据链支撑，每项主张对应至少一条证据
- 边界段：主动呈现反例、局限、不确定领域
- 结尾：重申立场，点明后续可探索方向

**强制约束**：
- 一文一主张：全文只围绕一个核心论点展开
- 证据闭环：每个支撑点必须有证据映射
- 边界透明：必须声明主张的适用范围与局限

---

## 原型选择规则

### 优先级判定

1. **显式指定**：`prototype_hint` 已明确 → 按指定原型执行
2. **受众推断**：无 `prototype_hint` 但有 `target_audience`：
   - 患者/照护者/大众 → 患者教育稿
   - 专科医师 + 研究数据 → 证据解读稿
   - 行业从业者/政策评论 → 观点社论稿
3. **素材推断**：无原型信号但有 `source_packet`：
   - 临床试验/研究数据 → 证据解读稿
   - 产品动态/政策/行业分析 → 观点社论稿
   - 疾病科普/指南解读 → 患者教育稿
4. **无法判定**：无任何原型信号 → 进入策划模式，向用户确认原型

### 策划模式

当原型无法自动判定时，进入策划模式：
- 分析素材类型与受众
- 提供 2-3 个候选原型
- 说明各原型的结构与适用场景
- 等待用户选择后进入成稿模式

---

## 控制握手（下游继承模式）

**当本 Skill 是模板内下游调用时**：
- 只继承 `control_context` 和 `log_context`
- 不重复读取控制面
- 不重复初始化日志
- 不重复做启动确认

**当本 Skill 是显式直写请求时**：
- 执行完整控制握手（见下文）

---

## 加载后必须执行（显式直写时）

**第一步：读取运行时规则**

立即读取以下文件：
```
D:/汇度编辑部1/写作知识库/项目规范/必看/系统运行.md
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

---

## 接收的 Handoff 字段

当由 `medical-content-router` 调用时，本 Skill 接收：

### 公共字段
```json
{
  "route_template_id": "query_to_write | opinion_to_write | ...",
  "handoff_source": "medical-content-router",
  "control_context": { "已读取控制面": true },
  "log_context": { "日志路径": "...", "会话ID": "..." }
}
```

### 写作必需字段
```json
{
  "task_goal": "用户目标描述",
  "source_packet": { "素材或证据包" },
  "constraints_context": { "约束条件" },
  "prototype_hint": "建议原型（可选）",
  "target_audience": "目标受众（可选）"
}
```

**说明**：至少提供一个写作落点信号（`prototype_hint` / `target_audience`）。

### 改稿控制字段（新增）

当从 `review_then_rewrite` 模板进入时，本 Skill 还接收以下改稿控制字段：

**完整字段定义参见**：`medical_kb_system_v2/docs/contracts/改稿控制协议_v1.md`

```json
{
  "rewrite_mode": "expand_patch | dedupe_patch | deepen_patch | mixed_patch",
  "locked_spans": [
    { "section_id": "intro", "action": "keep_verbatim", "reason": "用户明确要求不改引言" }
  ],
  "must_keep_claims": [
    "PACC突变领域目前无获批药物"
  ],
  "must_delete_or_compress": [
    {
      "issue_id": "dup-001",
      "location": "Part 2 第3段",
      "instruction": "压缩为一句总结，保留关键数据",
      "preserve_info": ["ORR 60%", "PFS 9.7个月"]
    }
  ],
  "expand_targets": [
    {
      "location": "Part 1",
      "dimension": "mechanism",
      "instruction": "补充空间位阻为何导致传统TKI难以稳定结合",
      "forbidden_additions": ["空泛过渡语", "抽象口号"]
    }
  ],
  "dedupe_map": {
    "dup-001": { "merge_into": "Part 1 第2段", "action": "merge" }
  },
  "evidence_gap_list": [
    {
      "location": "Part 1",
      "missing_item": "ELCC官方 ORR/PFS 数据",
      "status": "pending",
      "action_if_missing": "标注'数据待补充'"
    }
  ],
  "style_guard": {
    "forbidden_phrases": ["更深一层来看", "源头创新不是口号"],
    "tone_requirement": "冷静洞察，不喊口号",
    "register": "R3"
  },
  "word_budget": {
    "total_delta": { "min": -100, "max": +200 },
    "section_budgets": {
      "intro": { "action": "locked", "delta": 0 },
      "part1": { "action": "expand", "delta": "+50~+100" }
    }
  }
}
```

**说明**：分段预算 `section_budgets` 嵌套在 `word_budget` 内，与 reviewer 输出结构一致。

---

## 改稿模式执行规则

当接收到 `rewrite_mode` 字段时，必须按以下规则执行：

### expand_patch（增补模式）

**允许新增**：
- 数据（数值、百分比、P值）
- 机制解释（原理、路径、靶点作用）
- 对比基准（与标准治疗、历史数据对比）
- 案例或场景（临床案例、患者场景）
- 适用边界（人群限制、条件限制）
- 推导链条（从证据到结论的逻辑链）

**禁止新增**：
- ❌ 空泛过渡语（"进一步来说"、"更深层地看"）
- ❌ 抽象口号（"源头创新不是口号"、"改变未来"）
- ❌ 同义复述（不产生新信息的换说法）

**输出要求**：新增信息量 > 新增字数的 80%

### dedupe_patch（去重模式）

**目标**：压缩重复表达，保留信息量

**执行规则**：
1. 识别 `must_delete_or_compress` 中的重复内容
2. 按 `preserve_info` 保留关键信息点
3. 将重复内容合并到目标位置
4. 输出合并说明

**禁止做法**：
- ❌ 直接删段导致信息丢失
- ❌ 简单删字而不说明保留了什么

**输出要求**：信息量守恒，删除前后的信息点列表对比

### deepen_patch（深化模式）

**必须按指定维度深化**：
- `mechanism_deepen` — 机制深化（更具体的原理、路径）
- `evidence_deepen` — 证据深化（更多数据、更细致的对比）
- `comparison_deepen` — 对比深化（与竞品/标准治疗的对比）
- `boundary_deepen` — 边界深化（适用条件、限制因素）
- `clinical_deepen` — 临床推导深化（实际应用场景、决策路径）

**禁止做法**：
- ❌ 更宏大的总结（把具体问题升华为泛泛而谈）
- ❌ 更抽象的判断（用概念替换数据）
- ❌ 更多修辞（堆砌形容词和比喻）

### mixed_patch（混合模式）

按各段落标记的模式分别执行，每个段落遵循对应模式的规则。

---

## 段落锁定规则

当 `locked_spans` 中某段落标记为 `keep_verbatim` 时：

1. **不得修改** 该段落的任何内容
2. **不得插入** 新内容到该段落内
3. **不得删除** 该段落
4. 如需改动，返回错误并要求重新冻结 brief

**示例**：
```json
{
  "locked_spans": [
    { "section_id": "intro", "action": "keep_verbatim", "reason": "用户明确要求不改引言" }
  ]
}
```

则 writer 输出时，intro 段落必须与原文逐字一致。

---

## 字数预算规则

当接收到 `word_budget` 时：

1. 总字数变化必须在 `total_delta` 范围内
2. 各段落字数变化必须在 `section_budgets` 对应段落范围内
3. `locked` 状态的段落字数变化必须为 0

---

## 能力范围

本 Skill 触发后，通过知识库获取以下能力：

| 模块 | 说明 | 知识库位置 |
|------|------|-----------|
| 硬约束层 | 证据先于判断、合规边界、语域控制、中文表达底线 | 系统运行.md |
| 文章原型层 | 3 类 MVP 原型（证据解读、患教、观点社论） | 本 Skill 定义 |
| 写作策略层 | 开篇方式、证据组织、风险段位置、结尾动作 | 知识库 |
| 风格变体层 | Style-RAG | 知识库 |

**禁止**：本 Skill 内部不定义具体规则，所有规则以知识库和运行文档为准。

---

## 改稿前 Gate 校验

当进入 `review_then_rewrite` 模板时，必须先执行 Gate 校验。

### 五项必查

| 序号 | 检查项 | 必需条件 | 不满足时的动作 |
|------|--------|----------|----------------|
| 1 | 冻结 brief | 已生成且状态为 `frozen` | 回到 brief 冻结步骤 |
| 2 | 改稿模式 | 已明确 `rewrite_mode` | 回到策略策划步骤 |
| 3 | 锁定段落 | 已列出 `locked_spans`（可为空列表） | 确认无锁定后继续 |
| 4 | 必留信息点 | 已列出 `must_keep_claims` | 回到 brief 冻结步骤 |
| 5 | 证据缺口 | 已列出 `evidence_gap_list`（可为空列表） | 确认无缺口后继续 |

### Gate 输出格式

```json
{
  "gate_status": "pass | blocked",
  "checks": [
    { "item": "frozen_brief", "status": "pass", "brief_id": "proj-001-v3" },
    { "item": "rewrite_mode", "status": "pass", "mode": "expand_patch" },
    { "item": "locked_spans", "status": "pass", "count": 2 },
    { "item": "must_keep_points", "status": "pass", "count": 5 },
    { "item": "evidence_gaps", "status": "pass", "count": 1 }
  ],
  "blocked_reason": null,
  "proceed_to": "writer"
}
```

### Gate 阻断处理

当 `gate_status` 为 `blocked` 时：

1. **不允许进入写作**
2. 输出阻断原因
3. 指引用户回到对应步骤

**示例**：
```json
{
  "gate_status": "blocked",
  "checks": [
    { "item": "frozen_brief", "status": "fail", "reason": "未找到冻结 brief" },
    { "item": "rewrite_mode", "status": "pending", "reason": "等待 brief 冻结后确定" }
  ],
  "blocked_reason": "缺少冻结 brief",
  "action_required": "请先生成并确认冻结 brief"
}
```

---

## 工作流

### 显式直写模式
```
用户触发本 Skill（满足直写阈值）
    ↓
读取系统运行.md（铁律、workflow-gate、文档地图、项目日志机制）
    ↓
按 DOC-017 准备日志记录位置
    ↓
向用户确认已理解规则
    ↓
判定原型（显式指定 / 受众推断 / 素材推断 / 策划模式）
    ↓
执行写作任务
    ↓
交付结果
```

### 模板内下游调用模式
```
medical-content-router 调用本 Skill
    ↓
继承 control_context 和 log_context
    ↓
基于 handoff payload 判定原型
    ↓
执行写作
    ↓
交付结果
```

### 改稿模式（review_then_rewrite）
```
medical-article-reviewer 完成审核
    ↓
输出 patch 控制字段（rewrite_mode, locked_spans, etc.）
    ↓
【Gate 校验】检查五项必查
    ↓
Gate 通过？
    ├─ 是 → 进入受控改稿
    │       ↓
    │   按 rewrite_mode 执行
    │       ├─ expand_patch: 只增有效信息
    │       ├─ dedupe_patch: 压缩但守恒信息
    │       └─ deepen_patch: 按维度深化
    │       ↓
    │   检查 locked_spans（锁定段落不得改动）
    │       ↓
    │   检查 word_budget（字数预算）
    │       ↓
    │   交付结果 + 改稿报告
    │
    └─ 否 → 阻断，返回上一步骤
```

---

## 与其他 Skill 的关系

| Skill | 关系 | 说明 |
|-------|------|------|
| `medical-content-router` | 上游入口 | 处理模糊/组合请求后，将明确写作任务移交给本 Skill |
| `medical-opinion-generator` | 上游子模块 | 可作为 `opinion_to_write` 模板的前序步骤 |
| `medical-article-reviewer` | 上游子模块 | 可作为 `review_then_rewrite` 模板的前序步骤 |
| `medical-database-query` | 上游子模块 | 可作为 `query_to_write` 模板的前序步骤 |

---

## 与知识库的关系

- **本 Skill**: 只负责"什么时候触发写作"
- **知识库**: 负责"触发后做什么" + "所有规则定义"

如果知识库规则与 Skill 内部任何描述矛盾，**以知识库为准**。

---

# End of Skill