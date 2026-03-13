# Distilled Articles Directory

本目录存放经过蒸馏的编辑风格素材，供 V2 系统消费。

## 目录结构

```
editorial/distilled_articles/
├── specialist_*.json         # 专科医师文章风格 (H004)
├── patient_education_*.json  # 患者教育文章风格 (H005)
├── primary_care_*.json       # 基层医护文章风格 (H006)
└── public_science_*.json     # 公众科普文章风格 (H006)
```

## 蒸馏批次

| 批次ID | 来源 | 文件数 | 受众 | 语体等级 | 状态 |
|--------|------|--------|------|----------|------|
| H004 | historical_articles/专科医师 | 44 | 专科医师 | R2 | 🔄 处理中 |
| H005 | historical_articles/患者教育 | 34 | 患者/家属 | R4 | 🔄 处理中 |
| H006 | historical_articles/基层医护 | 4 | 基层医护 | R3 | 🔄 处理中 |
| H006 | historical_articles/公众科普 | 3 | 公众 | R5 | 🔄 处理中 |

## 蒸馏格式

每个蒸馏文件提取以下 EDITORIAL/STYLE 资产：

```json
{
  "distillation_manifest": { ... },
  "metadata": {
    "title": "...",
    "content_type": "主张_证据 | 叙事_反思 | 场景_指导 | 对比_推荐 | 新闻_评论",
    "audience": "专科医师 | 患者教育 | 基层医护 | 公众科普"
  },
  "distilled_content": {
    "register_level": "R2 | R3 | R4 | R5",
    "narrative_patterns": [...],
    "rhetoric_blocks": [...],
    "hook_patterns": [...],
    "risk_disclosure_patterns": [...],
    "CTA_patterns": [...],
    "article_structure": [...]
  },
  "key_messages": [...],
  "writing_style_notes": { ... }
}
```

## 重要说明

**这些是 STYLE 资产，NOT EVIDENCE 来源。**

- 提取的是写作风格、叙事模式、修辞策略
- 不应作为事实真相源使用
- 适用于指导同类型文章的写作风格

## 索引位置
| H006 | historical_articles/基层医护 | 4 | 基层医护 | R3 | ✅ 已完成 |
| H006 | historical_articles/公众科普 | 3 | 公众 | R5 | ✅ 已完成 |
批次清单文件位于：
- `medical_kb_system_v2/manifests/h004_specialist_articles_manifest.json`
- `medical_kb_system_v2/manifests/h005_patient_education_manifest.json`
- `medical_kb_system_v2/manifests/h006_primary_care_public_manifest.json`

## 创建日期

- 2026-03-10
- 批次: H004-H006