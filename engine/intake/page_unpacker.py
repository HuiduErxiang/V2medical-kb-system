"""
页面解包器

从来源中提取页面资产。
intake 前半段的第二阶段。
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib

from ..evidence.models import AssetRecord, AssetType, SourceRecord, SourceType


class PageUnpacker:
    """
    页面解包器
    
    从来源（主要是 PDF/PPTX）中提取页面级别的资产。
    
    Phase 2 实现：
    - PDF 页面提取（简化版，返回页面信息而非实际图像）
    - PPTX 幻灯片提取
    - 网页快照（占位）
    """
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
    
    def unpack(self, source: SourceRecord) -> List[AssetRecord]:
        """
        从来源解包页面资产
        
        Args:
            source: 来源记录
        
        Returns:
            AssetRecord 列表
        """
        if source.source_type == SourceType.PDF:
            return self._unpack_pdf(source)
        elif source.source_type == SourceType.PPTX:
            return self._unpack_pptx(source)
        elif source.source_type == SourceType.WEB:
            return self._unpack_web(source)
        else:
            # 对于 MANUAL 和 DATABASE 类型，返回单个占位资产
            return self._unpack_generic(source)
    
    def _unpack_pdf(self, source: SourceRecord) -> List[AssetRecord]:
        """
        解包 PDF 页面
        
        简化实现：返回占位的页面资产（不实际提取）
        真实实现需要 pdf2image 或 PyMuPDF
        """
        # 首轮简化：假设每个 PDF 有一个占位页面资产
        # 真实实现应该扫描实际页数
        
        assets = []
        
        # 创建页面资产（简化版）
        # TODO: 真实实现时使用 PyMuPDF 获取实际页数
        page_count = 1  # 占位
        
        for page_num in range(1, page_count + 1):
            asset_id = f"AST-{source.source_id}-PG{page_num:03d}"
            asset_key = f"AST-{source.source_key}-PG{page_num:03d}"
            
            asset = AssetRecord(
                asset_id=asset_id,
                source_id=source.source_id,
                asset_key=asset_key,
                asset_type=AssetType.DOCUMENT,
                page_range=str(page_num),
                storage_key=f"{source.source_key}/pages/{page_num:03d}",
                metadata={
                    "page_number": page_num,
                    "source_type": "pdf",
                    "created_at": datetime.now().isoformat()
                }
            )
            
            if self.registry:
                self.registry.register_asset(asset)
            
            assets.append(asset)
        
        return assets
    
    def _unpack_pptx(self, source: SourceRecord) -> List[AssetRecord]:
        """
        解包 PPTX 幻灯片
        
        简化实现：返回占位的幻灯片资产
        """
        assets = []
        
        # 创建幻灯片资产（简化版）
        slide_count = 1  # 占位
        
        for slide_num in range(1, slide_count + 1):
            asset_id = f"AST-{source.source_id}-SLD{slide_num:03d}"
            asset_key = f"AST-{source.source_key}-SLD{slide_num:03d}"

            
            asset = AssetRecord(
                asset_id=asset_id,
                source_id=source.source_id,
                asset_key=asset_key,
                asset_type=AssetType.SNAPSHOT,
                page_range=str(slide_num),
                storage_key=f"{source.source_key}/slides/{slide_num:03d}",
                metadata={
                    "slide_number": slide_num,
                    "source_type": "pptx",
                    "created_at": datetime.now().isoformat()
                }
            )
            
            if self.registry:
                self.registry.register_asset(asset)
            
            assets.append(asset)
        
        return assets
    
    def _unpack_web(self, source: SourceRecord) -> List[AssetRecord]:
        """
        解包网页
        
        简化实现：返回单个快照资产
        """
        asset_id = f"AST-{source.source_id}-SNAP001"
        asset_key = f"AST-{source.source_key}-SNAP001"
        
        asset = AssetRecord(
            asset_id=asset_id,
            source_id=source.source_id,
            asset_key=asset_key,
            asset_type=AssetType.SNAPSHOT,
            storage_key=f"{source.source_key}/snapshot/001",
            metadata={
                "snapshot_type": "web",
                "created_at": datetime.now().isoformat()
            }
        )
        
        if self.registry:
            self.registry.register_asset(asset)
        
        return [asset]
    
    def _unpack_generic(self, source: SourceRecord) -> List[AssetRecord]:
        """
        通用解包：返回单个文档资产
        """
        asset_id = f"AST-{source.source_id}-DOC001"
        asset_key = f"AST-{source.source_key}-DOC001"
        
        asset = AssetRecord(
            asset_id=asset_id,
            source_id=source.source_id,
            asset_key=asset_key,
            asset_type=AssetType.DOCUMENT,
            storage_key=f"{source.source_key}/document/001",
            metadata={
                "source_type": source.source_type.value,
                "created_at": datetime.now().isoformat()
            }
        )
        
        if self.registry:
            self.registry.register_asset(asset)
        
        return [asset]
    
    def unpack_batch(self, sources: List[SourceRecord]) -> Dict[str, List[AssetRecord]]:
        """
        批量解包
        
        Args:
            sources: 来源记录列表
        
        Returns:
            {source_id: [AssetRecord]}
        """
        return {source.source_id: self.unpack(source) for source in sources}


# 便捷函数
def unpack_source(source: SourceRecord) -> List[AssetRecord]:
    """解包单个来源"""
    unpacker = PageUnpacker()
    return unpacker.unpack(source)


def unpack_sources(sources: List[SourceRecord]) -> Dict[str, List[AssetRecord]]:
    """批量解包来源"""
    unpacker = PageUnpacker()
    return unpacker.unpack_batch(sources)