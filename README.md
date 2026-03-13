# 辰公子的医学写作系统 V2

目录名：`medical_kb_system_v2`

状态：**当前默认入口**（Phase 5）

---

## 目的

本目录是医学编辑智能写作系统的**当前默认入口**，承接 V2 平行重建成果。

| 版本 | 目录 | 状态 | 用途 |
|------|------|------|------|
| **V2（当前）** | `medical_kb_system_v2/` | 活跃 | 默认生产入口 |
| V1（旧版） | `medical_kb_system/` | 只读/归档计划 | 历史追溯、回滚备用 |

---

## 当前骨架

```text
medical_kb_system_v2/
  engine/
    runtime/          # 运行时核心
    intake/           # 摄入层
    evidence/         # 证据层
    editorial/        # 编辑层
    prompt/           # 提示层
    quality/          # 质量层
    delivery/         # 交付层
  tests/              # 测试文件（146 passed）
  docs/               # 内部说明文档
  rules/              # L1-L2 规则
  structured/         # L3-L4 结构化知识
  editorial/          # 编辑层资产
  evidence/           # 证据层资产
  intake/             # 摄入层资产
  skills/             # OpenCode 技能定义
  templates/          # 模板
  manifests/          # 清单文件
```

---

## 当前阶段

**Phase 5 已验证 - 外层切换完成**

已完成：
- ✅ Phase 0: V1 冻结
- ✅ Phase 1: V2 骨架与最小闭环
- ✅ Phase 2: 扩展 evidence access layer 与 intake 前半段
- ✅ Phase 3: intake 后半段与新证据层稳定化
- ✅ Phase 4: 资产迁移（Batch-1~4）
- ✅ Phase 5: 外层切换

待启动：
- ⏳ Phase 6: V1 退役归档
---

## 测试状态

```powershell
cd D:\汇度编辑部1\写作知识库\medical_kb_system_v2
python -m pytest -q
# 预期结果：146 passed
```

---

## 文档入口

执行总控与配套文档位于：

- `D:\汇度编辑部1\写作知识库\V2重建_20260309\`

其中重点入口：

- `V2重建执行总控_20260309.md` — 总控入口
- `Phase5搭建计划_20260310.md` — Phase 5 唯一正式执行入口
- `V2重建进度追踪表_20260309.md` — 进度追踪
- `Phase4资产盘点总表_20260309.md` — 资产盘点
- `Phase4回归与回滚说明_20260310.md` — 回滚说明

---

## V1 回滚说明

如需回滚到 V1：

1. 将默认入口切回 `medical_kb_system/`
2. V2 进入只读状态
3. 详见 `V2重建_20260309/Phase4回归与回滚说明_20260310.md`

---

## 一句话原则

> V2 是当前默认入口，V1 已进入只读/归档计划状态。