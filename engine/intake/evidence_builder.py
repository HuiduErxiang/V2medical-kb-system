"""
证据构建器

从资产中提取证据片段并构建事实记录。
intake 前半段的第三阶段。
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib
import json

from ..evidence.models import (
    AssetRecord, EvidenceFragment, FactRecord, 
    FragmentType, FactStatus
)


class EvidenceBuilder:
    """
    证据构建器
    
    从资产中提取证据片段，并构建结构化的事实记录。
    
    Phase 2 实现：
    - 从文本资产提取片段
    - 构建简化的事实记录
    - 建立片段到事实的关联
    """
    
    # 领域映射
    DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "efficacy": ["疗效", "有效性", "有效率", "response", "efficacy", "outcome"],
        "safety": ["安全", "不良", "副作用", "safety", "adverse", "tolerability"],
        "biomarker": ["生物标志物", "标志物", "biomarker", "marker", "检测"],
        "moa": ["机制", "作用机制", "机制", "moa", "mechanism", "靶点"],
        "trial_design": ["试验设计", "入排标准", "设计", "trial", "study design", "入组"],
        "competitor": ["竞品", "竞争", "对照", "competitor", "comparison", "对比"]
    }
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
    
    def build_from_asset(
        self, 
        asset: AssetRecord, 
        content: Optional[str] = None
    ) -> tuple[List[EvidenceFragment], List[FactRecord]]:
        """
        从资产构建证据片段和事实
        
        Args:
            asset: 资产记录
            content: 资产内容（可选，用于文本资产）
        
        Returns:
            (fragments, facts)
        """
        fragments = []
        facts = []
        
        # 创建证据片段
        fragment = self._create_fragment(asset, content)
        fragments.append(fragment)
        
        # 如果有内容，尝试提取事实
        if content:
            extracted_facts = self._extract_facts(asset, fragment, content)
            facts.extend(extracted_facts)
        
        # 注册
        if self.registry:
            for f in fragments:
                self.registry.register_fragment(f)
            for f in facts:
                self.registry.register_fact(f)
        
        return fragments, facts
    
    def _create_fragment(
        self, 
        asset: AssetRecord, 
        content: Optional[str]
    ) -> EvidenceFragment:
        """创建证据片段"""
        fragment_id = f"FRG-{asset.asset_id}-001"
        fragment_key = f"FRG-{asset.asset_key}-001"
        
        # 确定片段类型
        fragment_type = FragmentType.TEXT
        if asset.asset_type.value in ["image", "chart"]:
            fragment_type = FragmentType.VISUAL
        
        return EvidenceFragment(
            fragment_id=fragment_id,
            asset_id=asset.asset_id,
            fragment_key=fragment_key,
            fragment_type=fragment_type,
            content=content or "",
            confidence=1.0,
            metadata={
                "source_asset": asset.asset_key,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def _extract_facts(
        self, 
        asset: AssetRecord,
        fragment: EvidenceFragment,
        content: str
    ) -> List[FactRecord]:
        """
        从内容中提取事实
        
        首轮简化实现：基于关键词匹配创建占位事实
        真实实现应使用 NLP 或规则引擎
        """
        facts = []
        
        # 检测领域
        detected_domains = self._detect_domains(content)
        
        # 为每个检测到的领域创建一个简化事实
        for domain in detected_domains:
            fact_id = f"FCT-{asset.source_id}-{domain}-{hashlib.md5(content[:100].encode()).hexdigest()[:8]}"
            fact_key = f"VAR_{domain.upper()}_{hashlib.md5(content[:50].encode()).hexdigest()[:6].upper()}"
            
            fact = FactRecord(
                fact_id=fact_id,
                fact_key=fact_key,
                domain=domain,
                definition=f"Extracted from {asset.asset_key}",
                definition_zh=f"从 {asset.asset_key} 提取",
                value=content[:200],  # 截取前200字符作为值
                fragment_ids=[fragment.fragment_id],
                status=FactStatus.ACTIVE,
                lineage={
                    "source_ids": [asset.source_id],
                    "timestamps": [datetime.now().isoformat()],
                    "extraction_method": "keyword_detection"
                },
                metadata={
                    "source_asset": asset.asset_key,
                    "domain_detection": domain,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            facts.append(fact)
        
        return facts
    
    def _detect_domains(self, content: str) -> List[str]:
        """
        检测内容所属领域
        
        基于关键词匹配
        """
        detected = []
        content_lower = content.lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if domain not in detected:
                        detected.append(domain)
                    break
        
        # 如果没有检测到，默认为 efficacy
        if not detected:
            detected.append("efficacy")
        
        return detected
    
    def build_from_assets(
        self, 
        assets: List[AssetRecord],
        contents: Optional[Dict[str, str]] = None
    ) -> tuple[List[EvidenceFragment], List[FactRecord]]:
        """
        批量构建证据
        
        Args:
            assets: 资产列表
            contents: {asset_id: content} 映射
        
        Returns:
            (fragments, facts)
        """
        all_fragments = []
        all_facts = []
        
        contents = contents or {}
        
        for asset in assets:
            content = contents.get(asset.asset_id)
            fragments, facts = self.build_from_asset(asset, content)
            all_fragments.extend(fragments)
            all_facts.extend(facts)
        
        return all_fragments, all_facts
    
    def build_from_dict(self, data: Dict[str, Any]) -> FactRecord:
        """
        从字典数据构建事实记录
        
        用于从 V1 数据或 JSON 构建
        """
        fact = FactRecord(
            fact_id=data.get("fact_id", ""),
            fact_key=data.get("fact_key", ""),
            domain=data.get("domain", "efficacy"),
            definition=data.get("definition"),
            definition_zh=data.get("definition_zh"),
            value=data.get("value"),
            unit=data.get("unit"),
            fragment_ids=data.get("fragment_ids", []),
            status=FactStatus.ACTIVE,
            lineage=data.get("lineage", {}),
            metadata=data.get("metadata", {})
        )
        
        if self.registry:
            self.registry.register_fact(fact)
        
        return fact


# 便捷函数
def build_evidence(
    asset: AssetRecord, 
    content: Optional[str] = None
) -> tuple[List[EvidenceFragment], List[FactRecord]]:
    """从资产构建证据"""
    builder = EvidenceBuilder()
    return builder.build_from_asset(asset, content)


def build_fact_from_dict(data: Dict[str, Any]) -> FactRecord:
    """从字典构建事实"""
    builder = EvidenceBuilder()
    return builder.build_from_dict(data)