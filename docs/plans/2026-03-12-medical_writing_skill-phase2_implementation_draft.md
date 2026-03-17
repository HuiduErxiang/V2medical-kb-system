# 医学写作 Skill 封装 Phase 2 执行方案草案

> **For Other AI:** REQUIRED GUARDRAILS: 使用 `document-integrity-guard`，并遵守 `D:\汇度编辑部1\写作知识库\AGENTS.md`。本文件在登记到总控前，不得被当作正式执行入口。
> **唯一候选路径:** `D:\汇度编辑部1\写作知识库\medical_kb_system_v2\docs\plans\2026-03-12-医学写作skill封装-phase2执行方案草案.md`

**Goal:** 在不扩原型数量的前提下，用真实任务把 `medical-content-router + 三原型 + 链式 handoff` 从“已能工作”推进到“可持续真实运行”。

**Architecture:** Phase 2 不再重复做 Phase 1 的入口唯一化和三原型首轮落地，而是围绕真实任务样本池、链路观察、缺陷台账、最小修正和定向复跑建立稳定化闭环。执行出口仍是现有 5 个 live skill；控制面继续由 `系统运行.md` 和既有真相源承接。

**Tech Stack:** Markdown 计划与日志、`C:\Users\96138\.config\opencode\skills\` 下 5 个 live skill、`D:\汇度编辑部1\写作知识库\写作项目运行日志\` 根索引、`D:\汇度编辑部1\写作知识库\projects\{项目名}\项目日志\` 详细日志、PowerShell 文件核对。

---

## 文档状态

- 性质：Phase 2 执行方案草案
- 当前状态：待复核
- 真相源状态：未登记，不是正式执行入口
- 适用目录：`D:\汇度编辑部1\写作知识库`

## 当前判断

当前已知、且可直接被文件支持的起点只有这些：

1. Phase 1 全量验收已形成，并被写为 `已验证`
2. 三类独立试跑日志已存在
3. `medical-content-router`、`medical-writing`、`medical-opinion-generator`、`medical-article-reviewer`、`medical-database-query` 的 Phase 1 改造已落文件

当前**不能**直接宣称：

1. Phase 2 已启动
2. 当前草案已经成为唯一正式计划
3. 当前草案涉及的验收条件已满足

---

## 文档与日志边界

在登记到总控前，本文件是 Phase 2 的唯一候选正文。为避免同阶段双草案并存：

1. `medical_kb_system_v2/docs/plans/2026-03-12-医学写作skill封装-phase2执行方案草案.md` 保留完整正文。
2. `medical_kb_system_v2/docs/medical_writing_skill_phase2_implementation_draft_20260312.md` 只能保留跳转说明，不再承载另一份正文。

Phase 2 的日志必须遵守 `系统运行.md` 的双层日志规则：

1. `D:\汇度编辑部1\写作知识库\写作项目运行日志\` 只放治理索引，不落完整过程材料。
2. 真实任务的完整输入、输出、reviewer 明细、复跑说明和中间判断，写入 `D:\汇度编辑部1\写作知识库\projects\{项目名}\项目日志\`。
3. 根索引文档必须回链到项目详细日志路径，否则该样本不能算 Phase 2 已验证证据。

---

## Phase 2 总目标

Phase 2 只做 4 件事：

1. 建立真实任务样本池，不再只靠演示样例判断系统稳定性。
2. 连续验证 router 分流、直写阈值、三原型差异和链式 handoff。
3. 对真实运行中反复出现的缺陷做最小修正，并执行定向复跑。
4. 产出一份带直接证据的 Phase 2 验收报告，为是否进入下一阶段提供依据。

## 本轮范围

### In Scope

- 真实任务样本池
- 入口分流与直写阈值验证
- `query_to_write`、`opinion_to_write`、`review_then_rewrite`、`planning_to_write`、`write_direct` 覆盖
- 三原型稳定性验证
- reviewer 是否仍会回退到旧 `M2`
- 缺陷归类、最小修正、定向复跑
- 验收报告与真相源同步建议

### Out Of Scope

- 新增第 4 原型
- 新增超出当前上限的长链路模板
- 重写控制面
- 把 router 扩成第二个总控层
- 在没有登记真相源前宣布 Phase 2 已启动

---

## 执行输出

本轮执行至少应产出以下文件：

- 创建根日志治理索引：`D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2真实任务样本池_20260312.md`
- 创建根日志治理索引：`D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2链路观察记录_20260312.md`
- 创建根日志治理索引：`D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2缺陷台账_20260312.md`
- 创建项目级详细日志：`D:\汇度编辑部1\写作知识库\projects\{项目名}\项目日志\试跑_*.md`
- 创建根日志验收报告：`D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2_全量验收报告_20260312.md`

其中 `Phase2_全量验收报告_YYYYMMDD.md` 虽位于根日志目录，但只允许写治理摘要、覆盖统计、缺陷闭环结论和项目详细日志链接，不承载完整样本过程或复跑细节。

如 Phase 2 中出现明确缺陷，允许修改：

- `C:\Users\96138\.config\opencode\skills\medical-content-router\SKILL.md`
- `C:\Users\96138\.config\opencode\skills\medical-writing\SKILL.md`
- `C:\Users\96138\.config\opencode\skills\medical-opinion-generator\SKILL.md`
- `C:\Users\96138\.config\opencode\skills\medical-article-reviewer\SKILL.md`
- `C:\Users\96138\.config\opencode\skills\medical-database-query\SKILL.md`

---

### Task 1: 冻结样本池与记录模板

**Files:**
- Create: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2真实任务样本池_20260312.md`
- Create: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2链路观察记录_20260312.md`
- Create: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2缺陷台账_20260312.md`
- Read: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase1_全量验收报告_20260312.md`
- Read: `D:\汇度编辑部1\写作知识库\project_standards\必看\系统运行.md`

**Step 1: 建立最小覆盖矩阵**

最小样本量设为 `10`，必须覆盖：

- `query_to_write` >= 3
- `opinion_to_write` >= 2
- `review_then_rewrite` >= 2
- `planning_to_write` >= 1
- `write_direct` >= 1

原型至少覆盖：

- 证据解读稿 >= 3
- 患者教育稿 >= 3
- 观点社论稿 >= 2

样本计数口径固定为：

- 同一底层真实任务只计 `1` 个样本。
- 同一任务的定向复跑、修后回归、review 后重跑，只能挂在原样本 ID 下，不能重复计入 `10` 个样本。
- 是否为新样本，以“是否是新的真实业务请求/新的项目详细日志主记录”为准，而不是以运行次数为准。

**Step 2: 固定记录字段**

根日志样本池只记录治理索引字段：

- 样本 ID
- 项目名
- 项目详细日志路径
- 用户请求摘要
- 入口判断
- 模板选择
- 原型判定
- 缺陷码
- 当前结果
- 是否复跑

项目详细日志至少记录完整过程字段：

- 完整用户输入
- `control_context` / `log_context` 状态
- handoff 摘要
- 输出摘要
- reviewer 摘要
- 定向复跑说明
- 是否出现缺陷

禁止把完整用户输入、完整输出、完整 reviewer 明细只堆在根日志目录。

**Step 3: 运行前校验**

Run:
```powershell
Get-ChildItem 'D:\汇度编辑部1\写作知识库\写作项目运行日志' -File | Select-Object Name,LastWriteTime
```

Expected:
- 能看到 `Phase1_全量验收报告_20260312.md`
- 能看到 3 个独立试跑日志
- 能从根日志索引定位到对应项目日志目录结构

### Task 2: 验证 router 分流与直写阈值

**Files:**
- Read: `C:\Users\96138\.config\opencode\skills\medical-content-router\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-writing\SKILL.md`
- Modify if needed: same files
- Log to: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2链路观察记录_20260312.md`

**Step 1: 验证模糊请求与组合请求**

检查：

- 是否稳定进入 `medical-content-router`
- 是否仍存在绕过 router 的误命中

**Step 2: 验证显式直写阈值**

检查：

- 素材/原型/受众/改写目标不足 2 项时，是否仍被正确拦到 router
- 满足 2 项时，是否允许进入 `medical-writing`

**Step 3: 记录误分流缺陷**

缺陷分类固定为：

- `route_misclassification`
- `write_direct_threshold_error`
- `planning_route_gap`

### Task 3: 验证 handoff 契约与单次握手

**Files:**
- Read: `C:\Users\96138\.config\opencode\skills\medical-content-router\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-opinion-generator\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-article-reviewer\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-database-query\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-writing\SKILL.md`
- Log to: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2链路观察记录_20260312.md`

**Step 1: 核对 4 条关键模板**

必须验证：

- `query_to_write`
- `opinion_to_write`
- `review_then_rewrite`
- `planning_to_write`

**Step 2: 核对下游是否重复握手**

禁止出现：

- 第二次读取控制面
- 第二次初始化日志
- 第二次启动确认

**Step 3: 记录字段缺口**

缺陷分类固定为：

- `handoff_missing_field`
- `handoff_semantic_ambiguity`
- `handoff_payload_bloat`
- `duplicate_handshake`

Verification command:
```powershell
Select-String -Path `
  'C:\Users\96138\.config\opencode\skills\medical-opinion-generator\SKILL.md', `
  'C:\Users\96138\.config\opencode\skills\medical-article-reviewer\SKILL.md', `
  'C:\Users\96138\.config\opencode\skills\medical-database-query\SKILL.md' `
  -Pattern 'control_context|log_context'
```

Expected:
- 三个子模块都能检到 `control_context`
- 三个子模块都能检到 `log_context`

### Task 4: 验证三原型稳定性与 reviewer 行为

**Files:**
- Read: `C:\Users\96138\.config\opencode\skills\medical-writing\SKILL.md`
- Read: `C:\Users\96138\.config\opencode\skills\medical-article-reviewer\SKILL.md`
- Create: `D:\汇度编辑部1\写作知识库\projects\{项目名}\项目日志\试跑_*.md`
- Log to: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2链路观察记录_20260312.md`

**Step 1: 连续观察三原型差异**

每条样本必须记录：

- 开篇方式
- 证据密度
- 术语使用与 Register
- 结尾动作
- 是否重新同质化

**Step 2: 验证 reviewer 是否摆脱旧 M2**

必须验证：

- 证据解读稿按研究问题/结果/边界/启示审
- 患者教育稿按术语转译/可理解性/风险提示审
- 观点社论稿按一文一主张/证据闭环/边界透明审
- 不再把旧 `M2骨架完整性` 当全局门槛

**Step 3: 记录缺陷**

缺陷分类固定为：

- `prototype_drift`
- `register_misalignment`
- `reviewer_m2_fallback`
- `reviewer_prototype_mismatch`

### Task 5: 最小修正、定向复跑与收口报告

**Files:**
- Modify if needed: 5 个 live skill 文件
- Create: `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase2_全量验收报告_20260312.md`
- Optionally update after registration: 真相源文件

`Phase2_全量验收报告_YYYYMMDD.md` 只允许承载治理摘要、覆盖统计、缺陷闭环结论和项目详细日志链接；完整样本过程与复跑细节仍只留在项目日志。

**Step 1: 只修重复出现的真实缺陷**

不允许：

- 顺手扩第 4 原型
- 顺手增加新长链模板
- 以“重写架构”代替最小修正

**Step 2: 定向复跑**

每条已修缺陷必须至少有 1 次定向复跑记录。

**Step 3: 写 Phase 2 验收报告**

报告必须区分：

- `已实现`
- `已验证`
- `已关闭`

只有在真相源同步后，才允许写 `已关闭`。

---

## 验收标准

Phase 2 要写成 `已验证`，必须同时满足：

1. 样本池、观察记录、缺陷台账、试跑日志、验收报告都已生成。
2. 真实任务唯一样本不少于 10 个，同一底层任务的复跑不重复计数。
3. 三原型和五类关键模板达到最小覆盖要求。
4. 未留下未记录的阻塞性误分流。
5. router 首入口握手后，下游不重复握手。
6. 关键 handoff 模板无阻塞性字段缺口，或已修复并复跑。
7. reviewer 在真实稿件中未再回退到旧 `M2` 总门槛。
8. 根日志索引与项目详细日志路径一一对应，且能从索引回读到完整过程材料。
9. 验收报告含 `Evidence Summary`，且不是报告自证报告。

Phase 2 要写成 `已关闭`，还必须额外满足：

1. 总控、进度追踪表、当前阶段正式计划已同轮同步。
2. 遗留问题已明确归入下一阶段或显式关闭。
3. 不存在“已验证”和“已关闭”口径混写。

---

## 复核问题

给其他 AI 复核时，建议重点问这 6 个问题：

1. Phase 2 是否应该继续聚焦真实运行验证，而不是扩新原型。
2. 最小样本量 `10` 和当前覆盖矩阵是否足够。
3. `planning_to_write` 是否应保留为硬性覆盖项。
4. 当前缺陷分类是否足够支撑 Phase 2 收口。
5. 根日志治理索引与项目详细日志的职责边界是否已经写清。
6. 当前草案是否已经清楚避免“未登记先冒充正式入口”。

---

## 建议结论

这份草案建议把 Phase 2 定义为：

**真实任务稳定化阶段**

而不是：

- 扩原型阶段
- 扩模板阶段
- 重写控制面阶段

如果复核通过，下一步再把它登记为正式计划文件，并同步到当前真相源。

---

## Evidence Summary

- 已直接核对 `D:\汇度编辑部1\写作知识库\medical_kb_system_v2\docs\medical_writing_skill_plan_20260311.md` 中关于 MVP 三原型、固定模板和试跑验收重点的定义，确认 Phase 2 应顺着“真实运行验证”继续，而不是先扩新原型。
- 已直接核对 `D:\汇度编辑部1\写作知识库\写作项目运行日志\Phase1_全量验收报告_20260312.md` 与 3 个独立试跑日志，确认当前存在 Phase 1 已验证基线，可作为 Phase 2 起点。
- 已直接核对 `D:\汇度编辑部1\写作知识库\project_standards\必看\系统运行.md` 与 `D:\汇度编辑部1\写作知识库\AGENTS.md`，确认根日志只保留摘要索引，且未登记的阶段草案不能冒充正式执行入口。
