# revision_control_protocol v1.0

> **日期**: 2026-03-13
> **状态**: 已生效
> **适用范围**: V2 写作系统中所有长文改稿场景

---

## 1. 协议目的

本协议解决 V2 写作系统在长文改稿场景下的以下问题：

1. **增补灌水** — 系统增补内容时靠过渡句、抽象升华、同义复述扩字数
2. **去重丢信息** — 系统去重时直接删段导致信息量下降
3. **深化空泛** — 系统深化时写成更宏观的空泛表达
4. **锁段失效** — 用户明确锁定的内容被后续轮次改坏

---

## 2. 冻结 Brief 机制

### 2.1 定义

**冻结 brief** 是当前轮写作/改稿的唯一执行真相源。它必须在进入写作或改稿前先生成并确认。

### 2.2 必需字段

```json
{
  "project_id": "项目唯一标识",
  "audience": "目标受众",
  "article_goal": "文章目标",
  "prototype_hint": "文章原型（证据解读稿/患者教育稿/观点社论稿）",
  "locked_sections": [
    { "section_id": "intro", "reason": "用户要求不改引言" }
  ],
  "must_keep_points": [
    "PACC突变领域目前无获批药物",
    "exon20ins 是 EGFR 罕见突变中先发优势最明确的亚型"
  ],
  "must_delete_points": [
    "过时的临床数据（已被新研究替代）"
  ],
  "forbidden_topics": [
    "竞品直接比较（无头对头数据）"
  ],
  "word_count_target": { "min": 1800, "max": 2200 },
  "evidence_gaps": [
    { "location": "Part 1", "missing": "ELCC官方 ORR/PFS 数据", "status": "pending" }
  ],
  "current_source_of_truth": "项目执行卡或需求文档的路径"
}
```

### 2.3 冻结规则

1. **未冻结不写作** — 未生成冻结 brief 前，不允许进入成稿或改稿
2. **冲突先解决** — 若项目执行卡、需求文档、项目日志存在冲突，必须先解决冲突，再生成冻结 brief
3. **一轮一 brief** — 一轮冻结 brief 生效后，本轮只服从这份 brief，不再并行服从其他控制文档
4. **冻结后不改** — 冻结 brief 一旦确认，本轮内不得单方面修改；如需修改，必须重新冻结

---

## 3. 改稿模式定义

系统必须根据改稿目标选择以下三种模式之一，不允许使用泛化的 `rewrite_target`。

### 3.1 增补模式 `expand_patch`

**目标**：新增有效信息，禁止灌水。

**允许新增**：
- 数据（数值、百分比、P值等）
- 机制解释（原理、路径、靶点作用）
- 对比基准（与标准治疗、历史数据的对比）
- 案例或场景（临床案例、患者场景）
- 适用边界（人群限制、条件限制）
- 推导链条（从证据到结论的逻辑链）

**禁止新增**：
- 空泛过渡语（"进一步来说"、"更深层地看"）
- 抽象口号（"源头创新不是口号"、"改变未来"）
- 同义复述（不产生新信息的换说法）

**输出要求**：
```json
{
  "added_items": [
    { "type": "mechanism", "content": "空间位阻导致传统TKI难以稳定结合", "location": "Part 1" }
  ],
  "word_delta": "+150",
  "new_info_check": "新增信息量大于新增字数的 80%"
}
```

### 3.2 去重模式 `dedupe_patch`

**目标**：压缩重复表达，保留信息量。

**禁止做法**：
- 直接删段导致信息丢失
- 简单删字而不说明保留了什么

**输出要求**：
```json
{
  "dedupe_actions": [
    {
      "source_location": "Part 2 第3段",
      "target_location": "Part 1 第2段（已合并至此）",
      "action": "merge",
      "deleted_content": "重复的 exon20ins 先发优势描述",
      "retained_info": "关键数据点：ORR 60%，PFS 9.7个月",
      "info_preserved": true
    }
  ],
  "word_delta": "-80",
  "info_preservation_check": "信息量守恒"
}
```

**信息守恒校验**：
- 删除前信息点列表 vs 删除后信息点列表
- 如有信息丢失，必须说明原因并获得确认

### 3.3 深化模式 `deepen_patch`

**目标**：增加论证深度，禁止抽象升华。

**必须先指定维度**：
- `mechanism_deepen` — 机制深化（更具体的原理、路径）
- `evidence_deepen` — 证据深化（更多数据、更细致的对比）
- `comparison_deepen` — 对比深化（与竞品/标准治疗的对比）
- `boundary_deepen` — 边界深化（适用条件、限制因素）
- `clinical_deepen` — 临床推导深化（实际应用场景、决策路径）

**禁止做法**：
- 更宏大的总结（把具体问题升华为泛泛而谈）
- 更抽象的判断（用概念替换数据）
- 更多修辞（堆砌形容词和比喻）

**输出要求**：
```json
{
  "deepen_dimension": "mechanism",
  "deepen_actions": [
    {
      "location": "Part 1",
      "before": "空间位阻影响药物结合",
      "after": "Exon20ins 插入突变导致 EGFR C 螺旋位移，使 ATP 结合口袋构象改变，传统 TKI 因分子结构刚性无法适应新构象，结合能下降 40%",
      "depth_type": "mechanism"
    }
  ],
  "word_delta": "+60",
  "abstraction_check": "未出现抽象升华"
}
```

---

## 4. Reviewer → Writer Patch 契约

### 4.1 Reviewer 输出字段

`medical-article-reviewer` 输出必须包含以下 patch 控制字段：

```json
{
  "draft_ref_or_text": "待审稿件引用或文本",
  
  "review_findings": {
    "P0_issues": [],
    "P1_issues": [],
    "P2_issues": []
  },
  
  "severity_summary": { "P0": 0, "P1": 2, "P2": 3 },
  
  "rewrite_mode": "expand_patch | dedupe_patch | deepen_patch | mixed_patch",
  
  "locked_spans": [
    { "section_id": "intro", "action": "keep_verbatim", "reason": "用户明确要求不改引言" }
  ],
  
  "must_keep_claims": [
    "PACC突变领域目前无获批药物",
    "exon20ins 是 EGFR 罕见突变中先发优势最明确的亚型"
  ],
  
  "must_delete_or_compress": [
    {
      "issue_id": "dup-001",
      "location": "Part 2 第3段",
      "instruction": "压缩为一句总结，不再重复引言中的 exon20ins 先发优势，保留关键数据",
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
  
  "evidence_gap_list": [
    {
      "location": "Part 1",
      "missing_item": "ELCC官方 ORR/PFS 数据",
      "status": "pending",
      "action_if_missing": "标注'数据待补充'或使用可替代数据源"
    }
  ],
  
  "style_guard": {
    "forbidden_phrases": ["更深一层来看", "源头创新不是口号", "颠覆性突破"],
    "tone_requirement": "冷静洞察，不喊口号",
    "register": "R3"
  },
  
  "word_budget": {
    "total_delta": { "min": -100, "max": +200 },
    "section_budgets": {
      "intro": { "action": "locked", "delta": 0 },
      "part1": { "action": "expand", "delta": "+50~+100" },
      "part2": { "action": "compress", "delta": "-30~-50" }
    }
  }
}
```

### 4.2 字段说明

| 字段 | 用途 | 必需 |
|------|------|------|
| `rewrite_mode` | 指定改稿模式 | 是 |
| `locked_spans` | 锁定段落，不得改动 | 是（如有锁定） |
| `must_keep_claims` | 必须保留的核心信息点 | 是 |
| `must_delete_or_compress` | 必须删除或压缩的内容 | 是（如有重复） |
| `expand_targets` | 增补目标和约束 | 是（expand_patch 模式） |
| `evidence_gap_list` | 待补证据缺口 | 是（如有缺口） |
| `style_guard` | 风格约束 | 否 |
| `word_budget` | 字数预算 | 否 |

---

## 5. Writer 接收契约

### 5.1 接收字段

`medical-writing` 必须能接收并处理以下字段：

```json
{
  "task_goal": "用户目标描述",
  "source_packet": {},
  "constraints_context": {},
  "prototype_hint": "证据解读稿",
  "target_audience": "专科医师",
  
  "rewrite_mode": "expand_patch | dedupe_patch | deepen_patch | mixed_patch",
  "locked_spans": [],
  "must_keep_claims": [],
  "must_delete_or_compress": [],
  "expand_targets": [],
  "dedupe_map": {},
  "evidence_gap_list": [],
  "style_guard": {},
  "word_budget": {},
  "section_budget": {}
}
```

### 5.2 执行规则

| 改稿模式 | Writer 必须遵守的规则 |
|----------|----------------------|
| `expand_patch` | 只增加有效信息；禁止空泛过渡语、抽象口号、同义复述 |
| `dedupe_patch` | 压缩重复但保留信息；输出合并说明和信息守恒检查 |
| `deepen_patch` | 按指定维度深化；禁止抽象升华、宏大总结 |
| `mixed_patch` | 按各段落标记的模式分别执行 |

### 5.3 段落锁定规则

当 `locked_spans` 中某段落标记为 `keep_verbatim` 时：
- Writer 不得修改该段落的任何内容
- Writer 不得在该段落内插入新内容
- Writer 不得删除该段落
- 如需改动，必须返回错误并要求重新冻结 brief

---

## 6. 改稿前 Gate 校验

### 6.1 五项必查

进入改稿前，必须检查以下 5 项：

| 序号 | 检查项 | 不满足时的动作 |
|------|--------|----------------|
| 1 | 是否已有唯一冻结 brief | 回到 brief 冻结步骤 |
| 2 | 是否明确本轮改稿模式 | 回到策略策划步骤 |
| 3 | 是否列出锁定段落 | 如果无锁定段落，确认后继续 |
| 4 | 是否列出必须保留的信息点 | 回到 brief 冻结步骤 |
| 5 | 是否列出待补证据缺口 | 如果无缺口，确认后继续 |

### 6.2 Gate 输出格式

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

---

## 7. 验收标准

整改成功的判断标准：

1. **锁段有效** — 用户明确要求"不改引言"时，引言在改稿后保持逐字不变
2. **增补不灌水** — 新增内容以数据、机制、证据为主，空泛表达占比 < 20%
3. **去重不丢信息** — 字数可变，但关键信息点不丢失
4. **深化不空泛** — 深化后内容更具体，而非更抽象
5. **reviewer 可执行** — reviewer 输出可直接指导 writer 做局部 patch
6. **brief 唯一** — 系统能明确指出"当前唯一冻结 brief"

---

## 8. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03-13 | 初始版本，定义冻结 brief、三种改稿模式、patch 契约 |

---

## Evidence Summary

- 本协议基于整改方案 `2026-03-13-V2写作系统改稿控制整改方案.md` 编写
- 字段定义与现有 handoff 契约兼容，不破坏 router 分流机制
- 已验证三种改稿模式的输入/输出定义完整