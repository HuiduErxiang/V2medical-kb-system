"""
四层证据对象模型

定义来源/资产/证据片段/事实四层结构。

Phase 3 稳定化：
- 补齐 AssetRecord 的 storage_key, content_hash, page_range 字段
- 补齐 EvidenceFragment 的 bbox 字段
- FactRecord 的 lineage 默认为空字典
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SourceType(Enum):
    """来源类型"""
    PDF = "pdf"
    PPTX = "pptx"
    WEB = "web"
    DATABASE = "database"
    MANUAL = "manual"


class AssetType(Enum):
    """资产类型"""
    DOCUMENT = "document"
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    SNAPSHOT = "snapshot"


class FragmentType(Enum):
    """证据片段类型"""
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    MIXED = "mixed"
    VISUAL = "visual"
    OTHER = "other"


class FactStatus(Enum):
    """事实状态"""
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    CONFLICTED = "conflicted"
    REVIEWED = "reviewed"
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class SourceRecord:
    """
    来源记录 - 第一层：来源层
    
    对应V1的sources条目，但增加稳定引用字段
    
    Attributes:
        source_id: 来源唯一标识
        source_type: 来源类型
        source_key: 稳定来源键 (不依赖路径)
        title: 来源标题
        citation: 引用信息
        ingestion_date: 入库日期
        metadata: 扩展元数据
    """
    source_id: str
    source_type: SourceType
    source_key: str  # 稳定引用键
    title: Optional[str] = None
    citation: Optional[str] = None
    ingestion_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetRecord:
    """
    资产记录 - 第二层：资产层
    
    从来源提取/生成的可引用资产
    
    Attributes:
        asset_id: 资产唯一标识
        source_id: 关联来源ID
        asset_key: 稳定资产键
        asset_type: 资产类型
        page_range: 页码范围
        storage_key: 外置存储键
        content_hash: 内容哈希
        metadata: 扩展元数据
    """
    asset_id: str
    source_id: str
    asset_key: str
    asset_type: AssetType
    page_range: Optional[str] = None
    storage_key: Optional[str] = None  # 外置存储定位
    content_hash: Optional[str] = None  # sha256哈希
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceFragment:
    """
    证据片段 - 第三层：证据片段层
    
    从资产提取的具体证据内容
    
    Attributes:
        fragment_id: 片段唯一标识
        asset_id: 关联资产ID
        fragment_key: 稳定片段键
        fragment_type: 片段类型
        content: 内容 (文本/OCR结果/描述)
        bbox: 区域坐标
        confidence: 置信度
        lineage: 血缘信息
        metadata: 扩展元数据
    """
    fragment_id: str
    asset_id: str
    fragment_key: str
    fragment_type: FragmentType
    content: str
    bbox: Optional[Dict[str, float]] = None  # {x, y, width, height}
    confidence: float = 1.0
    lineage: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FactRecord:
    """
    事实记录 - 第四层：事实层
    
    从证据片段提炼的结构化事实
    
    Attributes:
        fact_id: 事实唯一标识
        fact_key: 稳定事实键
        domain: 所属领域 (efficacy/safety/etc)
        definition: 定义/标签
        definition_zh: 中文定义
        value: 值
        unit: 单位
        content: 内容（可选）
        fragment_ids: 关联证据片段ID列表
        status: 事实状态
        lineage: 血缘信息（默认为空字典，避免 NoneType 错误）
        metadata: 扩展元数据
    """
    fact_id: str
    fact_key: str
    domain: str  # efficacy, safety, biomarker, moa, trial_design, competitor
    definition: Optional[str] = None
    definition_zh: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    content: Optional[str] = None
    fragment_ids: List[str] = field(default_factory=list)
    status: FactStatus = FactStatus.ACTIVE
    lineage: Dict[str, Any] = field(default_factory=dict)  # 默认空字典，避免 NoneType
    metadata: Dict[str, Any] = field(default_factory=dict)