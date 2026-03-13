"""
证据访问层

提供统一的四层证据对象访问入口。

Phase 2 扩展：
- 新增 lineage 模块
- 新增 query 模块
"""

# 四层证据对象
from .models import (
    SourceRecord,
    AssetRecord,
    EvidenceFragment,
    FactRecord,
    SourceType,
    AssetType,
    FragmentType,
    FactStatus,
)

# 解析器
from .resolver import EvidenceResolver
from .registry import EvidenceRegistry
from .legacy_resolver import LegacyResolver

# Phase 2 新增
from .lineage import LineageResolver, LineageChain, LineageNode
from .query import (
    EvidenceQuery,
    QueryResult,
    QueryBuilder,
    QueryType,
    QueryStatus,
    query_product,
    query_domain,
    query_keys,
    query_search,
)

__all__ = [
    # 四层对象
    "SourceRecord",
    "AssetRecord",
    "EvidenceFragment",
    "FactRecord",
    # 枚举
    "SourceType",
    "AssetType",
    "FragmentType",
    "FactStatus",
    # 解析器
    "EvidenceResolver",
    "EvidenceRegistry",
    "LegacyResolver",
    # Phase 2 新增
    "LineageResolver",
    "LineageChain",
    "LineageNode",
    "EvidenceQuery",
    "QueryResult",
    "QueryBuilder",
    "QueryType",
    "QueryStatus",
    "query_product",
    "query_domain",
    "query_keys",
    "query_search",
]