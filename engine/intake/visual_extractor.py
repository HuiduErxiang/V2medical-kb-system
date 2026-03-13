"""
视觉内容抽取器

从页面内容中抽取视觉信息（图片、表格、图表等）。
intake 后半段的第一阶段。
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib

from ..evidence.models import AssetRecord, AssetType, EvidenceFragment, FragmentType


class VisualExtractor:
    """
    视觉内容抽取器
    
    从页面内容中抽取视觉信息（图片、表格、图表等）并创建对应的 AssetRecord。
    
    Phase 3 实现：
    - 支持基础的视觉元素检测
    - 创建视觉资产记录
    - 与 EvidenceBuilder 配合工作
    """
    
    # 支持的视觉元素类型
    VISUAL_TYPES: Dict[str, AssetType] = {
        "image": AssetType.IMAGE,
        "table": AssetType.TABLE,
        "chart": AssetType.CHART,
        "document": AssetType.DOCUMENT,
        "snapshot": AssetType.SNAPSHOT
    }
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
    
    def extract(self, page_content: Dict[str, Any], page_number: int, 
                source_record=None, metadata: Optional[Dict[str, Any]] = None) -> List[AssetRecord]:
        """
        从页面内容中抽取视觉资产
        
        Args:
            page_content: 页面内容字典
            page_number: 页码
            source_record: 来源记录（可选）
            metadata: 额外元数据
        
        Returns:
            List[AssetRecord]: 抽取的视觉资产记录列表
        """
        assets = []
        
        # 存储外部传入的 metadata
        self._external_metadata = metadata or {}
        
        # 提取图片
        images = self._extract_images(page_content, page_number)
        assets.extend(images)
        
        # 提取表格
        tables = self._extract_tables(page_content, page_number)
        assets.extend(tables)
        
        # 提取图表
        charts = self._extract_charts(page_content, page_number)
        assets.extend(charts)
        
        # 注册到 registry
        if self.registry:
            for asset in assets:
                self.registry.register_asset(asset)
        
        return assets
    
    def extract_batch(self, pages_content: List[Dict[str, Any]], 
                      source_record=None, metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[AssetRecord]:
        """
        批量抽取多个页面的视觉资产
        
        Args:
            pages_content: 页面内容列表
            source_record: 来源记录（可选）
            metadata_list: 元数据列表（可选）
        
        Returns:
            List[AssetRecord]: 抽取的视觉资产记录列表
        """
        all_assets = []
        
        if metadata_list is None:
            metadata_list = [None] * len(pages_content)
        
        for page_num, (page_content, meta) in enumerate(zip(pages_content, metadata_list), 1):
            assets = self.extract(page_content, page_num, source_record, meta)
            all_assets.extend(assets)
        
        return all_assets
    
    def _extract_images(self, page_content: Dict[str, Any], page_number: int) -> List[AssetRecord]:
        """提取图片资产"""
        images = []
        
        if "images" in page_content:
            for img_idx, img_data in enumerate(page_content["images"]):
                asset = self._create_visual_asset(
                    asset_type=AssetType.IMAGE,
                    page_number=page_number,
                    index=img_idx,
                    content=img_data
                )
                images.append(asset)
        
        return images
    
    def _extract_tables(self, page_content: Dict[str, Any], page_number: int) -> List[AssetRecord]:
        """提取表格资产"""
        tables = []
        
        if "tables" in page_content:
            for table_idx, table_data in enumerate(page_content["tables"]):
                asset = self._create_visual_asset(
                    asset_type=AssetType.TABLE,
                    page_number=page_number,
                    index=table_idx,
                    content=table_data
                )
                tables.append(asset)
        
        return tables
    
    def _extract_charts(self, page_content: Dict[str, Any], page_number: int) -> List[AssetRecord]:
        """提取图表资产"""
        charts = []
        
        if "charts" in page_content:
            for chart_idx, chart_data in enumerate(page_content["charts"]):
                asset = self._create_visual_asset(
                    asset_type=AssetType.CHART,
                    page_number=page_number,
                    index=chart_idx,
                    content=chart_data
                )
                charts.append(asset)
        
        return charts
    
    def _create_visual_asset(self, asset_type: AssetType, page_number: int, 
                             index: int, content: Dict[str, Any]) -> AssetRecord:
        """创建视觉资产记录"""
        # 生成资产键
        asset_key = self._generate_asset_key(asset_type, page_number, index, content)
        
        # 生成 asset_id
        asset_id = self._generate_asset_id(asset_key, asset_type)
        
        # 合并元数据：先合并外部 metadata，再合并 content（content 覆盖同名键）
        full_metadata = {
            **getattr(self, '_external_metadata', {}),  # 外部传入的 metadata
            "page_number": page_number,
            "extracted_at": datetime.now().isoformat(),
            "asset_index": index,
            **content
        }
        
        # 创建资产记录
        record = AssetRecord(
            asset_id=asset_id,
            source_id="VISUAL_EXTRACTOR",  # 默认来源ID
            asset_type=asset_type,
            asset_key=asset_key,
            metadata=full_metadata
        )
        
        return record
    
    def _generate_asset_key(self, asset_type: AssetType, page_number: int, 
                            index: int, content: Dict[str, Any]) -> str:
        """生成资产键"""
        content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:8].upper()
        type_code = asset_type.value.upper()
        
        return f"VIS-{type_code}-P{page_number}-I{index}-{content_hash}"
    
    def _generate_asset_id(self, asset_key: str, asset_type: AssetType) -> str:
        """生成资产ID"""
        return asset_key


def extract_visual_assets(page_content: Dict[str, Any], page_number: int, 
                          source_record=None, metadata: Optional[Dict[str, Any]] = None) -> List[AssetRecord]:
    """便捷函数：抽取单个页面的视觉资产"""
    extractor = VisualExtractor()
    return extractor.extract(page_content, page_number, source_record, metadata)


def extract_visual_assets_batch(pages_content: List[Dict[str, Any]], 
                                source_record=None, metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[AssetRecord]:
    """便捷函数：批量抽取多个页面的视觉资产"""
    extractor = VisualExtractor()
    return extractor.extract_batch(pages_content, source_record, metadata_list)
