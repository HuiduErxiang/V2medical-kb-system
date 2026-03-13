# Evidence Ingested Directory

本目录存放经过蒸馏的证据素材，供 V2 系统消费。

## 目录结构

```
evidence/ingested/
├── guidelines/     # 指南/共识类证据 (H001)
│   ├── bystander_effect_dxd_2016.json
│   ├── egfr_ex20ins_detection_consensus_2024.json
│   ├── dxd_tdm1_resistance_gastric_2017.json
│   └── egfr_ex20ins_treatment_consensus_2024.json
└── references/     # 参考文献类证据 (H002, H003)
    └── (待后台任务完成)
```

## 蒸馏批次

| 批次ID | 来源 | 文件数 | 状态 | 目标目录 |
|--------|------|--------|------|----------|
| H001 | sources/guidelines | 5 | ✅ 完成 | guidelines/ |
| H002 | references/仑卡奈核心证据 | 46 | 🔄 处理中 | references/ |
| H003 | references/竞品证据 | 32 | 🔄 处理中 | references/ |

## 蒸馏格式

每个蒸馏文件包含以下结构：

```json
{
  "distillation_manifest": {
    "manifest_version": "1.0",
    "distillation_date": "2026-03-10",
    "batch_id": "H001",
    "source_key": "SRC-...",
    "asset_key": "AST-...",
    "content_hash": "...",
    "source_type": "journal_article | clinical_consensus",
    "distillation_status": "completed"
  },
  "metadata": { ... },
  "distilled_content": {
    "key_findings": [...],
    "recommendations": [...],
    "comparative_signals": [...]
  },
  "index_terms": { ... },
  "lineage": { ... }
}
```

## 索引位置

批次清单文件位于：
- `medical_kb_system_v2/manifests/h001_guidelines_distillation_manifest.json`
- `medical_kb_system_v2/manifests/h002_lecanemab_references_manifest.json`
- `medical_kb_system_v2/manifests/h003_competitor_references_manifest.json`

## 与原始资产的关系

- 原始文件保持在 V1 原位置
- 本目录仅保留蒸馏后的 JSON 结构化结果
- 通过 `source_key` 和 `asset_key` 保持引用关系

## 创建日期

- 2026-03-10
- 批次: H001-H003