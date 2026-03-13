"""
证据解析器基类

定义证据访问接口。所有具体解析器应继承此类。
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .models import SourceRecord, AssetRecord, EvidenceFragment, FactRecord


class EvidenceResolver(ABC):
    """
    证据解析器基类
    
    定义统一的证据访问接口。任何具体解析器(如LegacyResolver)
    都应实现这些接口。
    
    Phase 3 扩展：
    - 增加时间序列查询、冲突解决、版本对比等方法
    - 收紧查询/结果契约
    """
    
    # ==================== 核心抽象方法 ====================
    
    @abstractmethod
    def resolve_sources(self, query: Dict[str, Any]) -> List[SourceRecord]:
        """
        解析来源
        
        Args:
            query: 查询条件 {product_id, source_type, source_keys, etc}
        
        Returns:
            匹配的SourceRecord列表
        """
        pass
    
    @abstractmethod
    def resolve_assets(self, source_ids: List[str]) -> List[AssetRecord]:
        """
        解析资产
        
        Args:
            source_ids: 来源ID列表
        
        Returns:
            关联的AssetRecord列表
        """
        pass
    
    @abstractmethod
    def resolve_fragments(self, asset_ids: List[str]) -> List[EvidenceFragment]:
        """
        解析证据片段
        
        Args:
            asset_ids: 资产ID列表
        
        Returns:
            关联的EvidenceFragment列表
        """
        pass
    
    @abstractmethod
    def resolve_facts(self, query: Dict[str, Any]) -> List[FactRecord]:
        """
        解析事实
        
        Args:
            query: 查询条件 {product_id, domain, fact_keys, etc}
        
        Returns:
            匹配的FactRecord列表
        """
        pass
    
    # ==================== Phase 2 扩展方法 ====================
    
    def resolve_by_domain(self, product_id: str, domain: str) -> List[FactRecord]:
        """
        按领域解析事实
        
        Args:
            product_id: 产品ID
            domain: 领域 (efficacy/safety/biomarker/moa/trial_design/competitor)
        
        Returns:
            匹配的FactRecord列表
        """
        return self.resolve_facts({"product_id": product_id, "domain": domain})
    
    def resolve_by_fact_keys(self, product_id: str, fact_keys: List[str]) -> List[FactRecord]:
        """
        按事实键列表解析事实
        
        Args:
            product_id: 产品ID
            fact_keys: 事实键列表
        
        Returns:
            匹配的FactRecord列表
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        return [f for f in all_facts if f.fact_key in fact_keys]
    
    def resolve_by_time_range(
        self, 
        product_id: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[FactRecord]:
        """
        按时间范围解析事实
        
        Args:
            product_id: 产品ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
        
        Returns:
            匹配的FactRecord列表
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        
        filtered = []
        for fact in all_facts:
            # 从元数据中提取时间戳
            timestamps = []
            
            if fact.metadata and "promoted_at" in fact.metadata:
                timestamps.append(fact.metadata["promoted_at"])
            if fact.metadata and "last_updated_at" in fact.metadata:
                timestamps.append(fact.metadata["last_updated_at"])
            
            if not timestamps:
                continue
            
            # 解析时间戳
            try:
                fact_time = datetime.fromisoformat(timestamps[0])
            except (ValueError, IndexError):
                continue
            
            # 时间范围过滤
            if start_time and fact_time < start_time:
                continue
            if end_time and fact_time > end_time:
                continue
            
            filtered.append(fact)
        
        return filtered
    
    def resolve_conflicts(self, product_id: str) -> Dict[str, List[FactRecord]]:
        """
        解析冲突事实
        
        检测同一 fact_key 下存在多个版本或冲突值的情况
        
        Args:
            product_id: 产品ID
        
        Returns:
            {fact_key: [冲突的FactRecord列表]}
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        
        # 按 fact_key 分组
        by_key: Dict[str, List[FactRecord]] = {}
        for fact in all_facts:
            if fact.fact_key not in by_key:
                by_key[fact.fact_key] = []
            by_key[fact.fact_key].append(fact)
        
        # 找出冲突（同一 key 下有多个 fact）
        conflicts = {
            key: facts 
            for key, facts in by_key.items() 
            if len(facts) > 1
        }
        
        return conflicts
    
    def resolve_fact_lineage(self, fact_id: str) -> Dict[str, Any]:
        """
        解析事实血缘
        
        Args:
            fact_id: 事实ID
        
        Returns:
            血缘信息 {sources, assets, fragments, timestamps}
        """
        return {
            "fact_id": fact_id,
            "sources": [],
            "assets": [],
            "fragments": [],
            "timestamps": []
        }
    
    def resolve_source_by_type(
        self, 
        product_id: str, 
        source_type: str
    ) -> List[SourceRecord]:
        """
        按来源类型解析来源
        
        Args:
            product_id: 产品ID
            source_type: 来源类型 (pdf/pptx/web/database/manual)
        
        Returns:
            匹配的SourceRecord列表
        """
        return self.resolve_sources({
            "product_id": product_id,
            "source_type": source_type
        })
    
    def resolve_latest_facts(self, product_id: str, limit: int = 10) -> List[FactRecord]:
        """
        解析最新的事实
        
        Args:
            product_id: 产品ID
            limit: 返回数量限制
        
        Returns:
            按时间倒序排列的FactRecord列表
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        
        # 按时间戳排序
        def get_timestamp(fact: FactRecord) -> str:
            if fact.metadata and "promoted_at" in fact.metadata:
                return fact.metadata["promoted_at"]
            if fact.metadata and "last_updated_at" in fact.metadata:
                return fact.metadata["last_updated_at"]
            return ""
        
        sorted_facts = sorted(all_facts, key=get_timestamp, reverse=True)
        
        return sorted_facts[:limit]
    
    def count_facts_by_domain(self, product_id: str) -> Dict[str, int]:
        """
        统计各领域的事实数量
        
        Args:
            product_id: 产品ID
        
        Returns:
            {domain: count}
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        
        counts: Dict[str, int] = {}
        for fact in all_facts:
            domain = fact.domain
            counts[domain] = counts.get(domain, 0) + 1
        
        return counts
    
    def search_facts(self, product_id: str, keyword: str) -> List[FactRecord]:
        """
        搜索事实（按关键词）
        
        Args:
            product_id: 产品ID
            keyword: 搜索关键词
        
        Returns:
            匹配的FactRecord列表
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        
        keyword_lower = keyword.lower()
        
        matched = []
        for fact in all_facts:
            # 在定义和值中搜索
            if fact.definition and keyword_lower in fact.definition.lower():
                matched.append(fact)
            elif fact.definition_zh and keyword_lower in fact.definition_zh.lower():
                matched.append(fact)
            elif fact.value and keyword_lower in str(fact.value).lower():
                matched.append(fact)
        
        return matched
    
    # ==================== Phase 3 新增高级方法 ====================
    
    def resolve_temporal_versions(self, product_id: str, fact_key: str) -> List[FactRecord]:
        """
        解析事实的时间序列版本
        
        Args:
            product_id: 产品ID
            fact_key: 事实键
        
        Returns:
            按时间排序的事实版本列表
        """
        all_facts = self.resolve_by_fact_keys(product_id, [fact_key])
        
        # 按时间戳排序
        def get_timestamp(fact: FactRecord) -> str:
            if fact.metadata and "promoted_at" in fact.metadata:
                return fact.metadata["promoted_at"]
            if fact.metadata and "last_updated_at" in fact.metadata:
                return fact.metadata["last_updated_at"]
            return ""
        
        return sorted(all_facts, key=get_timestamp)
    
    def resolve_latest_version(self, product_id: str, fact_key: str) -> Optional[FactRecord]:
        """
        解析事实的最新版本
        
        Args:
            product_id: 产品ID
            fact_key: 事实键
        
        Returns:
            最新版本的事实记录
        """
        versions = self.resolve_temporal_versions(product_id, fact_key)
        return versions[-1] if versions else None
    
    def resolve_conflicting_facts(self, product_id: str) -> List[Dict[str, Any]]:
        """
        解析冲突事实的详细信息
        
        Returns:
            冲突信息列表，包含fact_key、事实数量、各事实详情
        """
        conflicts = self.resolve_conflicts(product_id)
        
        conflict_details = []
        for fact_key, facts in conflicts.items():
            conflict_details.append({
                "fact_key": fact_key,
                "conflict_count": len(facts),
                "facts": [
                    {
                        "fact_id": fact.fact_id,
                        "value": fact.value,
                        "status": fact.status.value,
                        "domain": fact.domain,
                        "promoted_at": fact.metadata.get("promoted_at", "")
                    }
                    for fact in facts
                ]
            })
        
        return conflict_details
    
    def resolve_facts_by_status(self, product_id: str, status: str) -> List[FactRecord]:
        """
        按状态解析事实
        
        Args:
            product_id: 产品ID
            status: 状态 (active/draft/approved/rejected/needs_revision/superseded/conflicted/reviewed)
        
        Returns:
            匹配的FactRecord列表
        """
        all_facts = self.resolve_facts({"product_id": product_id})
        return [fact for fact in all_facts if fact.status.value == status]
    
    def resolve_assets_by_type(self, product_id: str, asset_type: str) -> List[AssetRecord]:
        """
        按资产类型解析资产
        
        Args:
            product_id: 产品ID
            asset_type: 资产类型 (image/table/chart/document/snapshot)
        
        Returns:
            匹配的AssetRecord列表
        """
        # 先获取所有来源
        sources = self.resolve_sources({"product_id": product_id})
        source_ids = [source.source_id for source in sources]
        
        # 再获取所有资产
        all_assets = self.resolve_assets(source_ids)
        
        return [asset for asset in all_assets if asset.asset_type.value == asset_type]
    
    def resolve_fragments_by_type(self, product_id: str, fragment_type: str) -> List[EvidenceFragment]:
        """
        按片段类型解析证据片段
        
        Args:
            product_id: 产品ID
            fragment_type: 片段类型 (text/image/table/chart/mixed)
        
        Returns:
            匹配的EvidenceFragment列表
        """
        # 先获取所有来源和资产
        sources = self.resolve_sources({"product_id": product_id})
        source_ids = [source.source_id for source in sources]
        assets = self.resolve_assets(source_ids)
        asset_ids = [asset.asset_id for asset in assets]
        
        # 再获取所有片段
        all_fragments = self.resolve_fragments(asset_ids)
        
        return [frag for frag in all_fragments if frag.fragment_type.value == fragment_type]
    
    def resolve_evidence_chain(self, fact_id: str) -> Dict[str, Any]:
        """
        解析完整的证据链
        
        Args:
            fact_id: 事实ID
        
        Returns:
            完整的证据链信息 {fact, fragments, assets, sources}
        """
        # 获取事实
        all_facts = self.resolve_facts({"fact_ids": [fact_id]})
        fact = all_facts[0] if all_facts else None
        
        if not fact:
            return {"error": "Fact not found"}
        
        # 获取片段
        fragments = self.resolve_fragments(fact.fragment_ids)
        
        # 获取资产
        asset_ids = list(set([frag.asset_id for frag in fragments]))
        assets = self.resolve_assets(asset_ids)
        
        # 获取来源
        source_ids = list(set([asset.source_id for asset in assets]))
        sources = self.resolve_sources({"source_ids": source_ids})
        
        return {
            "fact": fact,
            "fragments": fragments,
            "assets": assets,
            "sources": sources
        }
