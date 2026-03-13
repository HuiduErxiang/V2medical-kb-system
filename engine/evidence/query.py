"""
证据查询对象

定义稳定的查询和结果契约。
Phase 3 扩展，用于收紧 evidence access layer 的输入输出边界。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class QueryStatus(Enum):
    """查询状态"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    EMPTY = "empty"


class QueryType(Enum):
    """查询类型"""
    BY_PRODUCT = "by_product"
    BY_DOMAIN = "by_domain"
    BY_KEYS = "by_keys"
    BY_TIME_RANGE = "by_time_range"
    SEARCH = "search"
    CONFLICTS = "conflicts"
    BY_STATUS = "by_status"
    BY_TYPE = "by_type"
    LATEST = "latest"


@dataclass
class EvidenceQuery:
    """
    证据查询对象 - 定义查询输入契约
    
    所有查询都通过此对象标准化，确保接口稳定性。
    
    Attributes:
        query_id: 查询唯一标识
        query_type: 查询类型
        product_id: 产品ID（必需）
        domain: 领域过滤（可选）
        fact_keys: 事实键列表（可选）
        source_keys: 来源键列表（可选）
        start_time: 时间范围起始（可选）
        end_time: 时间范围结束（可选）
        keyword: 搜索关键词（可选）
        limit: 结果数量限制
        include_lineage: 是否包含血缘信息
        status: 状态过滤（可选）
        asset_type: 资产类型过滤（可选）
        fragment_type: 片段类型过滤（可选）
        metadata: 扩展元数据
    """
    query_id: str = field(default_factory=lambda: f"qry_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    query_type: QueryType = QueryType.BY_PRODUCT
    product_id: str = ""
    domain: Optional[str] = None
    fact_keys: List[str] = field(default_factory=list)
    source_keys: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = None
    limit: int = 100
    include_lineage: bool = False
    status: Optional[str] = None
    asset_type: Optional[str] = None
    fragment_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（兼容旧接口）"""
        result = {
            "query_id": self.query_id,
            "query_type": self.query_type.value,
            "product_id": self.product_id,
            "limit": self.limit,
            "include_lineage": self.include_lineage
        }
        
        if self.domain:
            result["domain"] = self.domain
        if self.fact_keys:
            result["fact_keys"] = self.fact_keys
        if self.source_keys:
            result["source_keys"] = self.source_keys
        if self.start_time:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
        if self.keyword:
            result["keyword"] = self.keyword
        if self.status:
            result["status"] = self.status
        if self.asset_type:
            result["asset_type"] = self.asset_type
        if self.fragment_type:
            result["fragment_type"] = self.fragment_type
        
        return result
    
    @classmethod
    def for_product(cls, product_id: str) -> "EvidenceQuery":
        """创建按产品查询"""
        return cls(
            query_type=QueryType.BY_PRODUCT,
            product_id=product_id
        )
    
    @classmethod
    def for_domain(cls, product_id: str, domain: str) -> "EvidenceQuery":
        """创建按领域查询"""
        return cls(
            query_type=QueryType.BY_DOMAIN,
            product_id=product_id,
            domain=domain
        )
    
    @classmethod
    def for_keys(cls, product_id: str, fact_keys: List[str]) -> "EvidenceQuery":
        """创建按键列表查询"""
        return cls(
            query_type=QueryType.BY_KEYS,
            product_id=product_id,
            fact_keys=fact_keys
        )
    
    @classmethod
    def for_search(cls, product_id: str, keyword: str) -> "EvidenceQuery":
        """创建关键词搜索"""
        return cls(
            query_type=QueryType.SEARCH,
            product_id=product_id,
            keyword=keyword
        )
    
    @classmethod
    def for_status(cls, product_id: str, status: str) -> "EvidenceQuery":
        """创建按状态查询"""
        return cls(
            query_type=QueryType.BY_STATUS,
            product_id=product_id,
            status=status
        )
    
    @classmethod
    def for_type(cls, product_id: str, asset_type: str = None, fragment_type: str = None) -> "EvidenceQuery":
        """创建按类型查询"""
        return cls(
            query_type=QueryType.BY_TYPE,
            product_id=product_id,
            asset_type=asset_type,
            fragment_type=fragment_type
        )
    
    @classmethod
    def for_latest(cls, product_id: str, limit: int = 10) -> "EvidenceQuery":
        """创建最新事实查询"""
        return cls(
            query_type=QueryType.LATEST,
            product_id=product_id,
            limit=limit
        )


@dataclass
class QueryResult:
    """
    查询结果对象 - 定义查询输出契约
    
    所有查询结果都通过此对象标准化，确保接口稳定性。
    
    Attributes:
        query_id: 关联的查询ID
        status: 查询状态
        sources: 来源结果列表
        assets: 资产结果列表
        fragments: 片段结果列表
        facts: 事实结果列表
        lineages: 血缘信息列表（可选）
        conflicts: 冲突信息（可选）
        elapsed_ms: 查询耗时（毫秒）
        metadata: 扩展元数据
    """
    query_id: str = ""
    status: QueryStatus = QueryStatus.SUCCESS
    sources: List[Any] = field(default_factory=list)  # List[SourceRecord]
    assets: List[Any] = field(default_factory=list)   # List[AssetRecord]
    fragments: List[Any] = field(default_factory=list)  # List[EvidenceFragment]
    facts: List[Any] = field(default_factory=list)    # List[FactRecord]
    lineages: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    elapsed_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 注意：total_count 改为 property 动态计算
    
    @property
    def total_count(self) -> int:
        """动态计算总数量"""
        return (
            len(self.sources) + 
            len(self.assets) + 
            len(self.fragments) + 
            len(self.facts)
        )
    
    @property
    def is_success(self) -> bool:
        """查询是否成功"""
        return self.status in [QueryStatus.SUCCESS, QueryStatus.PARTIAL]
    
    @property
    def is_empty(self) -> bool:
        """结果是否为空"""
        return self.total_count == 0
    
    @property
    def has_conflicts(self) -> bool:
        """是否有冲突结果"""
        return len(self.conflicts) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "query_id": self.query_id,
            "status": self.status.value,
            "counts": {
                "sources": len(self.sources),
                "assets": len(self.assets),
                "fragments": len(self.fragments),
                "facts": len(self.facts),
                "total": self.total_count
            },
            "has_conflicts": self.has_conflicts,
            "conflict_count": len(self.conflicts),
            "elapsed_ms": self.elapsed_ms,
            "metadata": self.metadata
        }
    
    def add_fact(self, fact: Any) -> "QueryResult":
        """添加事实到结果"""
        self.facts.append(fact)
        return self
    
    def add_source(self, source: Any) -> "QueryResult":
        """添加来源到结果"""
        self.sources.append(source)
        return self
    
    def add_asset(self, asset: Any) -> "QueryResult":
        """添加资产到结果"""
        self.assets.append(asset)
        return self
    
    def add_fragment(self, fragment: Any) -> "QueryResult":
        """添加片段到结果"""
        self.fragments.append(fragment)
        return self
    
    def add_lineage(self, lineage: Dict[str, Any]) -> "QueryResult":
        """添加血缘信息到结果"""
        self.lineages.append(lineage)
        return self
    
    def add_conflict(self, conflict: Dict[str, Any]) -> "QueryResult":
        """添加冲突信息到结果"""
        self.conflicts.append(conflict)
        return self


@dataclass
class QueryBuilder:
    """
    查询构建器 - 提供流式查询构建
    
    Usage:
        query = (QueryBuilder()
            .product("lecanemab")
            .domain("efficacy")
            .limit(50)
            .include_lineage()
            .build())
    """
    _query: EvidenceQuery = field(default_factory=EvidenceQuery)
    
    def product(self, product_id: str) -> "QueryBuilder":
        """设置产品ID"""
        self._query.product_id = product_id
        return self
    
    def domain(self, domain: str) -> "QueryBuilder":
        """设置领域过滤"""
        self._query.domain = domain
        self._query.query_type = QueryType.BY_DOMAIN
        return self
    
    def fact_keys(self, keys: List[str]) -> "QueryBuilder":
        """设置事实键列表"""
        self._query.fact_keys = keys
        self._query.query_type = QueryType.BY_KEYS
        return self
    
    def source_keys(self, keys: List[str]) -> "QueryBuilder":
        """设置来源键列表"""
        self._query.source_keys = keys
        return self
    
    def status(self, status: str) -> "QueryBuilder":
        """设置状态过滤"""
        self._query.status = status
        self._query.query_type = QueryType.BY_STATUS
        return self
    
    def asset_type(self, asset_type: str) -> "QueryBuilder":
        """设置资产类型过滤"""
        self._query.asset_type = asset_type
        self._query.query_type = QueryType.BY_TYPE
        return self
    
    def fragment_type(self, fragment_type: str) -> "QueryBuilder":
        """设置片段类型过滤"""
        self._query.fragment_type = fragment_type
        self._query.query_type = QueryType.BY_TYPE
        return self
    
    def time_range(
        self, 
        start: Optional[datetime] = None, 
        end: Optional[datetime] = None
    ) -> "QueryBuilder":
        """设置时间范围"""
        self._query.start_time = start
        self._query.end_time = end
        self._query.query_type = QueryType.BY_TIME_RANGE
        return self
    
    def search(self, keyword: str) -> "QueryBuilder":
        """设置关键词搜索"""
        self._query.keyword = keyword
        self._query.query_type = QueryType.SEARCH
        return self
    
    def limit(self, n: int) -> "QueryBuilder":
        """设置结果数量限制"""
        self._query.limit = n
        return self
    
    def include_lineage(self, include: bool = True) -> "QueryBuilder":
        """是否包含血缘信息"""
        self._query.include_lineage = include
        return self
    
    def build(self) -> EvidenceQuery:
        """构建查询对象"""
        if not self._query.product_id:
            raise ValueError("product_id is required")
        return self._query


# 便捷函数
def query_product(product_id: str) -> EvidenceQuery:
    """创建产品查询"""
    return EvidenceQuery.for_product(product_id)


def query_domain(product_id: str, domain: str) -> EvidenceQuery:
    """创建领域查询"""
    return EvidenceQuery.for_domain(product_id, domain)


def query_keys(product_id: str, fact_keys: List[str]) -> EvidenceQuery:
    """创建键列表查询"""
    return EvidenceQuery.for_keys(product_id, fact_keys)


def query_search(product_id: str, keyword: str) -> EvidenceQuery:
    """创建搜索查询"""
    return EvidenceQuery.for_search(product_id, keyword)


def query_status(product_id: str, status: str) -> EvidenceQuery:
    """创建状态查询"""
    return EvidenceQuery.for_status(product_id, status)


def query_type(product_id: str, asset_type: str = None, fragment_type: str = None) -> EvidenceQuery:
    """创建类型查询"""
    return EvidenceQuery.for_type(product_id, asset_type, fragment_type)


def query_latest(product_id: str, limit: int = 10) -> EvidenceQuery:
    """创建最新事实查询"""
    return EvidenceQuery.for_latest(product_id, limit)
