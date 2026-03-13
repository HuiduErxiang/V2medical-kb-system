"""
版面绑定器

分析页面布局并绑定视觉元素到内容结构。
intake 后半段的第二阶段。
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import hashlib

from ..evidence.models import EvidenceFragment, FragmentType, AssetRecord, AssetType
from ..evidence.lineage import LineageChain, LineageNode


class LayoutBinder:
    """
    版面绑定器
    
    分析页面布局结构，将视觉元素与文本内容绑定，创建证据片段。
    
    Phase 3 实现：
    - 支持基础的布局分析
    - 视觉元素与文本内容绑定
    - 生成证据片段的 lineage 信息
    """
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
    
    def bind(self, page_content: Dict[str, Any], page_number: int, 
             assets: List[AssetRecord], source_record=None, 
             metadata: Optional[Dict[str, Any]] = None) -> List[EvidenceFragment]:
        """
        绑定页面布局与内容
        
        Args:
            page_content: 页面内容字典
            page_number: 页码
            assets: 页面的视觉资产列表
            source_record: 来源记录（可选）
            metadata: 额外元数据
        
        Returns:
            List[EvidenceFragment]: 绑定后的证据片段列表
        """
        fragments = []
        
        # 分析文本与视觉元素的关系
        text_fragments = self._analyze_text_layout(page_content, page_number)
        fragments.extend(text_fragments)
        
        # 分析表格与图表的布局关系
        visual_fragments = self._analyze_visual_layout(page_content, page_number, assets)
        fragments.extend(visual_fragments)
        
        # 注册到 registry
        if self.registry:
            for fragment in fragments:
                self.registry.register_fragment(fragment)
        
        return fragments
    
    def bind_batch(self, pages_content: List[Dict[str, Any]], 
                   pages_assets: List[List[AssetRecord]], 
                   source_record=None, metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[EvidenceFragment]:
        """
        批量绑定多个页面的布局
        
        Args:
            pages_content: 页面内容列表
            pages_assets: 每页的视觉资产列表
            source_record: 来源记录（可选）
            metadata_list: 元数据列表（可选）
        
        Returns:
            List[EvidenceFragment]: 绑定后的证据片段列表
        """
        all_fragments = []
        
        if metadata_list is None:
            metadata_list = [None] * len(pages_content)
        
        for page_num, (page_content, assets, meta) in enumerate(zip(pages_content, pages_assets, metadata_list), 1):
            fragments = self.bind(page_content, page_num, assets, source_record, meta)
            all_fragments.extend(fragments)
        
        return all_fragments
    
    def _analyze_text_layout(self, page_content: Dict[str, Any], page_number: int) -> List[EvidenceFragment]:
        """分析文本布局并创建片段"""
        fragments = []
        
        if "text_blocks" in page_content:
            for block_idx, text_block in enumerate(page_content["text_blocks"]):
                fragment = self._create_text_fragment(text_block, page_number, block_idx)
                fragments.append(fragment)
        
        return fragments
    
    def _analyze_visual_layout(self, page_content: Dict[str, Any], page_number: int, 
                               assets: List[AssetRecord]) -> List[EvidenceFragment]:
        """分析视觉元素布局并创建片段"""
        fragments = []
        
        for asset in assets:
            fragment = self._create_visual_fragment(asset, page_number)
            fragments.append(fragment)
        
        return fragments
    
    def _create_text_fragment(self, text_block: Dict[str, Any], page_number: int, 
                             block_index: int) -> EvidenceFragment:
        """创建文本证据片段"""
        fragment_key = self._generate_fragment_key(FragmentType.TEXT, page_number, block_index, text_block)
        
        fragment_id = self._generate_fragment_id(fragment_key, FragmentType.TEXT)
        
        lineage = self._create_lineage_for_text(block_index, page_number)
        
        full_metadata = {
            "page_number": page_number,
            "block_index": block_index,
            "bound_at": datetime.now().isoformat(),
            **text_block
        }
        
        fragment = EvidenceFragment(
            fragment_id=fragment_id,
            asset_id=f"AST-PAGE-{page_number}",
            fragment_type=FragmentType.TEXT,
            fragment_key=fragment_key,
            content=text_block.get("content", ""),
            metadata=full_metadata,
            lineage=lineage
        )
        
        return fragment
    
    def _create_visual_fragment(self, asset: AssetRecord, page_number: int) -> EvidenceFragment:
        """创建视觉证据片段"""
        fragment_type = self._asset_type_to_fragment_type(asset.asset_type)
        
        fragment_key = self._generate_fragment_key(fragment_type, page_number, 0, asset.metadata)
        
        fragment_id = self._generate_fragment_id(fragment_key, fragment_type)
        
        lineage = self._create_lineage_for_visual(asset)
        
        full_metadata = {
            "page_number": page_number,
            "asset_id": asset.asset_id,
            "bound_at": datetime.now().isoformat(),
            **asset.metadata
        }
        
        fragment = EvidenceFragment(
            fragment_id=fragment_id,
            asset_id=asset.asset_id,
            fragment_type=fragment_type,
            fragment_key=fragment_key,
            content=self._generate_visual_content(asset),
            metadata=full_metadata,
            lineage=lineage
        )
        
        return fragment
    
    def _generate_visual_content(self, asset: AssetRecord) -> str:
        """生成视觉片段的内容，提供稳定降级策略"""
        # 优先使用 metadata 中的 content
        content = asset.metadata.get("content", "")
        if content:
            return str(content)
        
        # 降级策略：根据资产类型生成默认描述
        type_descriptions = {
            AssetType.IMAGE: f"Image asset: {asset.asset_key}",
            AssetType.TABLE: f"Table asset: {asset.asset_key}",
            AssetType.CHART: f"Chart asset: {asset.asset_key}",
            AssetType.DOCUMENT: f"Document asset: {asset.asset_key}",
            AssetType.SNAPSHOT: f"Snapshot asset: {asset.asset_key}"
        }
        
        return type_descriptions.get(asset.asset_type, f"Visual asset: {asset.asset_key}")
    
    def _asset_type_to_fragment_type(self, asset_type) -> FragmentType:
        """将资产类型转换为片段类型"""
        if asset_type == AssetType.IMAGE:
            return FragmentType.IMAGE
        elif asset_type == AssetType.TABLE:
            return FragmentType.TABLE
        elif asset_type == AssetType.CHART:
            return FragmentType.CHART
        elif asset_type == AssetType.DOCUMENT:
            return FragmentType.TEXT
        elif asset_type == AssetType.SNAPSHOT:
            return FragmentType.VISUAL
        else:
            return FragmentType.OTHER
    
    def _create_lineage_for_text(self, block_index: int, page_number: int) -> LineageChain:
        """为文本片段创建 lineage"""
        node = LineageNode(
            node_type="text_block",
            node_id=f"text-block-{page_number}-{block_index}",
            node_key=f"text-block-{page_number}-{block_index}",
            metadata={
                "page_number": page_number,
                "block_index": block_index,
                "created_at": datetime.now().isoformat()
            }
        )
        
        chain = LineageChain()
        chain.add_node(node)
        return chain
    
    def _create_lineage_for_visual(self, asset: AssetRecord) -> LineageChain:
        """为视觉片段创建 lineage"""
        node = LineageNode(
            node_type="visual_asset",
            node_id=asset.asset_id,
            node_key=asset.asset_key,
            metadata={
                "asset_type": asset.asset_type,
                "created_at": datetime.now().isoformat()
            }
        )
        
        chain = LineageChain()
        chain.add_node(node)
        return chain
    
    def _generate_fragment_key(self, fragment_type: FragmentType, page_number: int, 
                              index: int, content: Dict[str, Any]) -> str:
        """生成片段键"""
        content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:8].upper()
        type_code = fragment_type.value.upper()
        
        return f"FRG-{type_code}-P{page_number}-I{index}-{content_hash}"
    
    def _generate_fragment_id(self, fragment_key: str, fragment_type: FragmentType) -> str:
        """生成片段ID"""
        return fragment_key


def bind_layout(page_content: Dict[str, Any], page_number: int, 
               assets: List[AssetRecord], source_record=None, 
               metadata: Optional[Dict[str, Any]] = None) -> List[EvidenceFragment]:
    """便捷函数：绑定单个页面的布局"""
    binder = LayoutBinder()
    return binder.bind(page_content, page_number, assets, source_record, metadata)


def bind_layout_batch(pages_content: List[Dict[str, Any]], 
                     pages_assets: List[List[AssetRecord]], 
                     source_record=None, metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[EvidenceFragment]:
    """便捷函数：批量绑定多个页面的布局"""
    binder = LayoutBinder()
    return binder.bind_batch(pages_content, pages_assets, source_record, metadata_list)
