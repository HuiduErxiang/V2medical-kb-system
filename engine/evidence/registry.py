"""
证据注册表

管理四层证据对象的注册和索引。

Phase 3 增强：
- 完善时间序列索引
- 增强版本追踪和冲突检测
- 收紧与查询器的接口契约
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

from .models import (
    SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
    SourceType, AssetType, FragmentType, FactStatus
)


@dataclass
class EvidenceRegistry:
    """
    证据注册表
    
    提供四层证据对象的注册、查询和索引功能。
    
    Attributes:
        sources: {source_id: SourceRecord}
        assets: {asset_id: AssetRecord}
        fragments: {fragment_id: EvidenceFragment}
        facts: {fact_id: FactRecord}
        indexes: 辅助索引
    """
    # 主存储
    sources: Dict[str, SourceRecord] = field(default_factory=dict)
    assets: Dict[str, AssetRecord] = field(default_factory=dict)
    fragments: Dict[str, EvidenceFragment] = field(default_factory=dict)
    facts: Dict[str, FactRecord] = field(default_factory=dict)
    
    # 正向索引
    _source_by_key: Dict[str, str] = field(default_factory=dict)  # source_key -> source_id
    _asset_by_key: Dict[str, str] = field(default_factory=dict)   # asset_key -> asset_id
    _fragment_by_key: Dict[str, str] = field(default_factory=dict)  # fragment_key -> fragment_id
    _fact_by_key: Dict[str, str] = field(default_factory=dict)    # fact_key -> fact_id
    
    # 反向索引
    _assets_by_source: Dict[str, List[str]] = field(default_factory=dict)  # source_id -> [asset_ids]
    _fragments_by_asset: Dict[str, List[str]] = field(default_factory=dict)  # asset_id -> [fragment_ids]
    _facts_by_domain: Dict[str, List[str]] = field(default_factory=dict)  # domain -> [fact_ids]
    _facts_by_fragment: Dict[str, List[str]] = field(default_factory=dict)  # fragment_id -> [fact_ids]
    
    # 版本追踪
    _fact_versions: Dict[str, List[str]] = field(default_factory=dict)  # fact_key -> [fact_ids with same key]
    
    # 时间序列索引
    _facts_by_timestamp: Dict[str, List[str]] = field(default_factory=dict)  # timestamp -> [fact_ids]
    
    # ==================== 注册方法 ====================
    
    def register_source(self, source: SourceRecord) -> str:
        """注册来源"""
        self.sources[source.source_id] = source
        self._source_by_key[source.source_key] = source.source_id
        return source.source_id
    
    def register_asset(self, asset: AssetRecord) -> str:
        """注册资产"""
        self.assets[asset.asset_id] = asset
        self._asset_by_key[asset.asset_key] = asset.asset_id
        
        if asset.source_id not in self._assets_by_source:
            self._assets_by_source[asset.source_id] = []
        self._assets_by_source[asset.source_id].append(asset.asset_id)
        
        return asset.asset_id
    
    def register_fragment(self, fragment: EvidenceFragment) -> str:
        """注册证据片段"""
        self.fragments[fragment.fragment_id] = fragment
        self._fragment_by_key[fragment.fragment_key] = fragment.fragment_id
        
        if fragment.asset_id not in self._fragments_by_asset:
            self._fragments_by_asset[fragment.asset_id] = []
        self._fragments_by_asset[fragment.asset_id].append(fragment.fragment_id)
        
        return fragment.fragment_id
    
    def register_fact(self, fact: FactRecord) -> str:
        """注册事实"""
        self.facts[fact.fact_id] = fact
        self._fact_by_key[fact.fact_key] = fact.fact_id
        
        if fact.domain not in self._facts_by_domain:
            self._facts_by_domain[fact.domain] = []
        self._facts_by_domain[fact.domain].append(fact.fact_id)
        
        # 更新片段反向索引
        for fragment_id in fact.fragment_ids:
            if fragment_id not in self._facts_by_fragment:
                self._facts_by_fragment[fragment_id] = []
            self._facts_by_fragment[fragment_id].append(fact.fact_id)
        
        # 更新版本追踪
        if fact.fact_key not in self._fact_versions:
            self._fact_versions[fact.fact_key] = []
        self._fact_versions[fact.fact_key].append(fact.fact_id)
        
        # 更新时间序列索引
        timestamp = self._get_fact_timestamp(fact)
        if timestamp not in self._facts_by_timestamp:
            self._facts_by_timestamp[timestamp] = []
        self._facts_by_timestamp[timestamp].append(fact.fact_id)
        
        return fact.fact_id
    
    # ==================== 批量注册方法 ====================
    
    def register_sources(self, sources: List[SourceRecord]) -> List[str]:
        """批量注册来源"""
        return [self.register_source(s) for s in sources]
    
    def register_assets(self, assets: List[AssetRecord]) -> List[str]:
        """批量注册资产"""
        return [self.register_asset(a) for a in assets]
    
    def register_fragments(self, fragments: List[EvidenceFragment]) -> List[str]:
        """批量注册证据片段"""
        return [self.register_fragment(f) for f in fragments]
    
    def register_facts(self, facts: List[FactRecord]) -> List[str]:
        """批量注册事实"""
        return [self.register_fact(f) for f in facts]
    
    # ==================== 查询方法 ====================
    
    def get_source(self, source_id: str) -> Optional[SourceRecord]:
        """获取来源"""
        return self.sources.get(source_id)
    
    def get_source_by_key(self, source_key: str) -> Optional[SourceRecord]:
        """通过source_key获取来源"""
        source_id = self._source_by_key.get(source_key)
        if source_id:
            return self.sources.get(source_id)
        return None
    
    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        """获取资产"""
        return self.assets.get(asset_id)
    
    def get_asset_by_key(self, asset_key: str) -> Optional[AssetRecord]:
        """通过asset_key获取资产"""
        asset_id = self._asset_by_key.get(asset_key)
        if asset_id:
            return self.assets.get(asset_id)
        return None
    
    def get_assets_by_source(self, source_id: str) -> List[AssetRecord]:
        """获取来源关联的所有资产"""
        asset_ids = self._assets_by_source.get(source_id, [])
        return [self.assets[aid] for aid in asset_ids if aid in self.assets]
    
    def get_fragment(self, fragment_id: str) -> Optional[EvidenceFragment]:
        """获取证据片段"""
        return self.fragments.get(fragment_id)
    
    def get_fragment_by_key(self, fragment_key: str) -> Optional[EvidenceFragment]:
        """通过fragment_key获取证据片段"""
        fragment_id = self._fragment_by_key.get(fragment_key)
        if fragment_id:
            return self.fragments.get(fragment_id)
        return None
    
    def get_fragments_by_asset(self, asset_id: str) -> List[EvidenceFragment]:
        """获取资产关联的所有证据片段"""
        fragment_ids = self._fragments_by_asset.get(asset_id, [])
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_fact(self, fact_id: str) -> Optional[FactRecord]:
        """获取事实"""
        return self.facts.get(fact_id)
    
    def get_fact_by_key(self, fact_key: str) -> Optional[FactRecord]:
        """通过fact_key获取事实（返回最新版本）"""
        fact_id = self._fact_by_key.get(fact_key)
        if fact_id:
            return self.facts.get(fact_id)
        return None
    
    def get_facts_by_domain(self, domain: str) -> List[FactRecord]:
        """获取领域关联的所有事实"""
        fact_ids = self._facts_by_domain.get(domain, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]
    
    def get_facts_by_fragment(self, fragment_id: str) -> List[FactRecord]:
        """获取片段关联的所有事实"""
        fact_ids = self._facts_by_fragment.get(fragment_id, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]
    
    def get_facts_by_status(self, status: str) -> List[FactRecord]:
        """获取指定状态的所有事实"""
        return [
            fact for fact in self.facts.values()
            if fact.status.value == status
        ]
    
    def get_facts_by_asset_type(self, asset_type: str) -> List[FactRecord]:
        """获取与特定类型资产关联的所有事实"""
        asset_ids = [
            asset_id for asset_id, asset in self.assets.items()
            if asset.asset_type.value == asset_type
        ]
        
        fragment_ids = []
        for asset_id in asset_ids:
            fragment_ids.extend(self._fragments_by_asset.get(asset_id, []))
        
        fact_ids = []
        for fragment_id in fragment_ids:
            fact_ids.extend(self._facts_by_fragment.get(fragment_id, []))
        
        return [self.facts[fid] for fid in set(fact_ids) if fid in self.facts]
    
    def get_all_facts(self) -> List[FactRecord]:
        """获取所有事实"""
        return list(self.facts.values())
    
    def get_all_sources(self) -> List[SourceRecord]:
        """获取所有来源"""
        return list(self.sources.values())
    
    # ==================== 版本追踪方法 ====================
    
    def get_fact_versions(self, fact_key: str) -> List[FactRecord]:
        """
        获取事实的所有版本
        
        Args:
            fact_key: 事实键
        
        Returns:
            该fact_key下的所有版本FactRecord列表
        """
        fact_ids = self._fact_versions.get(fact_key, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]
    
    def get_latest_fact_version(self, fact_key: str) -> Optional[FactRecord]:
        """
        获取事实的最新版本
        
        Args:
            fact_key: 事实键
        
        Returns:
            最新版本的FactRecord
        """
        versions = self.get_fact_versions(fact_key)
        if not versions:
            return None
        
        # 按时间戳排序，返回最新的
        sorted_versions = sorted(
            versions,
            key=lambda x: self._get_fact_timestamp(x),
            reverse=True
        )
        return sorted_versions[0] if sorted_versions else None
    
    # ==================== 时间序列方法 ====================
    
    def _get_fact_timestamp(self, fact: FactRecord) -> str:
        """获取事实的时间戳（用于排序）"""
        if fact.metadata and "promoted_at" in fact.metadata:
            return fact.metadata["promoted_at"]
        if fact.metadata and "last_updated_at" in fact.metadata:
            return fact.metadata["last_updated_at"]
        return ""
    
    def get_facts_by_time_range(self, start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[FactRecord]:
        """
        获取时间范围内的事实
        
        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
        
        Returns:
            时间范围内的事实列表
        """
        filtered_facts = []
        
        for fact in self.facts.values():
            # 获取事实的时间戳
            fact_timestamp_str = self._get_fact_timestamp(fact)
            
            try:
                fact_time = datetime.fromisoformat(fact_timestamp_str)
            except:
                continue
            
            # 检查时间范围
            if (start_time and fact_time < start_time) or (end_time and fact_time > end_time):
                continue
            
            filtered_facts.append(fact)
        
        # 按时间排序
        return sorted(filtered_facts, key=lambda x: self._get_fact_timestamp(x))
    
    def get_latest_facts(self, limit: int = 10) -> List[FactRecord]:
        """
        获取最新的事实
        
        Args:
            limit: 返回数量限制
        
        Returns:
            最新的事实列表（按时间倒序）
        """
        all_facts = sorted(
            self.facts.values(),
            key=lambda x: self._get_fact_timestamp(x),
            reverse=True
        )
        
        return all_facts[:limit]
    
    # ==================== 统计方法 ====================
    
    def count_sources(self) -> int:
        """统计来源数量"""
        return len(self.sources)
    
    def count_assets(self) -> int:
        """统计资产数量"""
        return len(self.assets)
    
    def count_fragments(self) -> int:
        """统计片段数量"""
        return len(self.fragments)
    
    def count_facts(self) -> int:
        """统计事实数量"""
        return len(self.facts)
    
    def count_facts_by_domain(self) -> Dict[str, int]:
        """统计各领域事实数量"""
        return {domain: len(fact_ids) for domain, fact_ids in self._facts_by_domain.items()}
    
    def count_facts_by_status(self) -> Dict[str, int]:
        """统计各状态事实数量"""
        status_counts = {}
        for fact in self.facts.values():
            status = fact.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    # ==================== 血缘追溯方法 ====================
    
    def get_fact_lineage(self, fact_id: str) -> Dict[str, Any]:
        """
        获取事实血缘
        
        返回从fact到source的完整追溯链
        """
        fact = self.get_fact(fact_id)
        if not fact:
            return {}
        
        lineage = {
            "fact_id": fact_id,
            "fact_key": fact.fact_key,
            "fragments": [],
            "assets": [],
            "sources": [],
            "timestamps": self._get_fact_timestamp(fact)
        }
        
        # 追溯片段
        for fid in fact.fragment_ids:
            fragment = self.get_fragment(fid)
            if fragment:
                lineage["fragments"].append({
                    "fragment_id": fid,
                    "fragment_key": fragment.fragment_key,
                    "content": fragment.content[:200] if fragment.content else ""
                })
                
                # 追溯资产
                asset = self.get_asset(fragment.asset_id)
                if asset:
                    lineage["assets"].append({
                        "asset_id": asset.asset_id,
                        "asset_key": asset.asset_key,
                        "asset_type": asset.asset_type.value
                    })
                    
                    # 追溯来源
                    source = self.get_source(asset.source_id)
                    if source:
                        lineage["sources"].append({
                            "source_id": source.source_id,
                            "source_key": source.source_key,
                            "citation": source.citation
                        })
        
        return lineage
    
    # ==================== 清理方法 ====================
    
    def clear(self):
        """清空所有数据"""
        self.sources.clear()
        self.assets.clear()
        self.fragments.clear()
        self.facts.clear()
        self._source_by_key.clear()
        self._asset_by_key.clear()
        self._fragment_by_key.clear()
        self._fact_by_key.clear()
        self._assets_by_source.clear()
        self._fragments_by_asset.clear()
        self._facts_by_domain.clear()
        self._facts_by_fragment.clear()
        self._fact_versions.clear()
        self._facts_by_timestamp.clear()
