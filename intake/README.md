# Intake 数据目录

本目录存放 V2 intake 模块的数据资产，包括来源索引和批次清单。

## 目录结构

```
intake/
├── manifests/           # 来源索引与批次注册
│   ├── source_index_schema.json   # 来源索引规范
│   └── batch_registry.json        # 批次注册表
└── README.md            # 本文件
```

## 来源索引规范

`source_index_schema.json` 定义了 V2 的来源索引契约：

- **source_key**: 来源唯一标识，格式 `SRC-{category}-{name}`
- **asset_key**: 资产唯一标识，格式 `AST-{type}-{name}`
- **storage_key**: 存储路径，格式 `{zone}/{category}/{year}/{month}/{filename}`
- **content_hash**: 内容哈希（sha256前16位）

## 批次注册表

`batch_registry.json` 记录所有进入系统的 intake 批次：

- 批次ID格式: `BATCH-{YYYY}-{MM}-{序号}`
- 状态: pending / processing / completed / failed

## 与 V1 的关系

- V1 `source_ingestion/manifests` 为空，无历史资产需要迁移
- 本目录为 V2 新建，从 Batch-3 开始正式建立来源索引能力

## 存储区域说明

实际文件存储在共享资产区：

- `sources/evidence_assets/` - 外部证据资产
- `sources/analysis_snapshots/` - 分析快照

本目录仅保留索引和元数据，不存储二进制文件。