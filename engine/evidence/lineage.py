"""
血缘追溯模块
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class LineageNode:
    node_id: str
    node_type: str
    node_key: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def copy(self):
        return LineageNode(
            node_id=self.node_id,
            node_type=self.node_type,
            node_key=self.node_key,
            timestamp=self.timestamp,
            version=self.version,
            metadata=self.metadata.copy()
        )

@dataclass
class LineageChain:
    fact_id: str = ""
    fact_key: str = ""
    chain: List[LineageNode] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_node(self, node: LineageNode):
        """添加血缘节点"""
        self.chain.append(node)
        self.timestamps.append(node.timestamp)
    
    @property
    def nodes(self) -> List[LineageNode]:
        """为兼容性提供nodes属性"""
        return self.chain
    
    @nodes.setter
    def nodes(self, value: List[LineageNode]):
        """为兼容性提供nodes属性的设置器"""
        self.chain = value
    
    def get_sources(self) -> List[LineageNode]:
        """获取所有来源节点"""
        return [n for n in self.chain if n.node_type == "source"]
    
    def get_assets(self) -> List[LineageNode]:
        return [n for n in self.chain if n.node_type == "asset"]
    
    def get_fragments(self) -> List[LineageNode]:
        return [n for n in self.chain if n.node_type == "fragment"]
    
    def get_fact_nodes(self) -> List[LineageNode]:
        return [n for n in self.chain if n.node_type == "fact"]
    
    def get_versions(self) -> List[int]:
        return sorted({node.version for node in self.chain})
    
    def get_temporal_sequence(self) -> List[LineageNode]:
        return sorted(self.chain, key=lambda x: x.timestamp)

class LineageResolver:
    """
    血缘解析器 - 负责解析四层证据对象的完整血缘链
    """
    def __init__(self, registry):
        self.registry = registry
    
    def resolve_lineage(self, fact_id: str) -> LineageChain:
        chain = LineageChain(fact_id=fact_id)
        fact = self.registry.get_fact(fact_id)
        
        if fact:
            chain.fact_key = fact.fact_key
            
            fact_node = LineageNode(
                node_id=fact.fact_id,
                node_type="fact",
                node_key=fact.fact_key
            )
            chain.add_node(fact_node)
            
            for fragment_id in fact.fragment_ids:
                fragment = self.registry.get_fragment(fragment_id)
                if fragment:
                    fragment_node = LineageNode(
                        node_id=fragment.fragment_id,
                        node_type="fragment",
                        node_key=fragment.fragment_key
                    )
                    chain.add_node(fragment_node)
                    
                    asset = self.registry.get_asset(fragment.asset_id)
                    if asset:
                        asset_node = LineageNode(
                            node_id=asset.asset_id,
                            node_type="asset",
                            node_key=asset.asset_key
                        )
                        chain.add_node(asset_node)
                        
                        source = self.registry.get_source(asset.source_id)
                        if source:
                            source_node = LineageNode(
                                node_id=source.source_id,
                                node_type="source",
                                node_key=source.source_key
                            )
                            chain.add_node(source_node)
        
        return chain
    
    def resolve_lineage_batch(self, fact_ids: List[str]) -> Dict[str, LineageChain]:
        return {fid: self.resolve_lineage(fid) for fid in fact_ids}
    
    def find_conflicts(self, fact_id: str) -> List[Dict[str, Any]]:
        fact = self.registry.get_fact(fact_id)
        if not fact:
            return []
            
        conflicts = []
        for other_fid, other_fact in self.registry.facts.items():
            if other_fid != fact_id and other_fact.fact_key == fact.fact_key:
                conflicts.append({
                    "type": "duplicate_key",
                    "fact_id_1": fact_id,
                    "fact_id_2": other_fid,
                    "fact_key": fact.fact_key
                })
        
        return conflicts
    
    def get_temporal_versions(self, fact_key: str) -> List[Dict[str, Any]]:
        versions = []
        
        for fact in self.registry.facts.values():
            if fact.fact_key == fact_key:
                version_info = {
                    "fact_id": fact.fact_id,
                    "fact_key": fact.fact_key,
                    "value": fact.value,
                    "status": fact.status.value,
                    "fragment_ids": fact.fragment_ids,
                    "timestamps": []
                }
                
                if fact.lineage and "timestamps" in fact.lineage:
                    version_info["timestamps"] = fact.lineage["timestamps"]
                elif fact.metadata and "promoted_at" in fact.metadata:
                    version_info["timestamps"] = [fact.metadata["promoted_at"]]
                elif fact.metadata and "last_updated_at" in fact.metadata:
                    version_info["timestamps"] = [fact.metadata["last_updated_at"]]
                elif fact.metadata and "created_at" in fact.metadata:
                    version_info["timestamps"] = [fact.metadata["created_at"]]
                else:
                    version_info["timestamps"] = ["1970-01-01T00:00:00"]
                
                versions.append(version_info)
        
        return sorted(versions, key=lambda x: x.get("timestamps", []))
    
    def find_latest_version(self, fact_key: str) -> Optional[Dict[str, Any]]:
        versions = self.get_temporal_versions(fact_key)
        if not versions:
            return None
            
        return max(versions, key=lambda x: x.get("timestamps", []))
    
    def compare_versions(self, fact_id1: str, fact_id2: str) -> Dict[str, Any]:
        fact1 = self.registry.get_fact(fact_id1)
        fact2 = self.registry.get_fact(fact_id2)
        
        if not fact1 or not fact2:
            return {
                "fact_id1": fact_id1,
                "fact_id2": fact_id2,
                "result": "not_found"
            }
            
        comparison = {
            "fact_id1": fact_id1,
            "fact_id2": fact_id2,
            "domain": fact1.domain == fact2.domain,
            "definition": fact1.definition == fact2.definition,
            "definition_zh": fact1.definition_zh == fact2.definition_zh,
            "value": fact1.value == fact2.value,
            "unit": fact1.unit == fact2.unit,
            "status": fact1.status == fact2.status,
            "fragment_count": len(fact1.fragment_ids) == len(fact2.fragment_ids)
        }
        
        if fact1.lineage and fact2.lineage:
            comparison["timeline_match"] = fact1.lineage == fact2.lineage
            
        return comparison
    
    def build_dependency_graph(self, fact_ids: List[str]) -> Dict[str, List[str]]:
        graph = {fid: [] for fid in fact_ids}
        
        for fact_id in fact_ids:
            chain = self.resolve_lineage(fact_id)
            dependencies = []
            
            for other_fact_id, other_fact in self.registry.facts.items():
                if other_fact_id == fact_id:
                    continue
                    
                # Check if the other fact shares the same fact_key (same logical fact)
                if other_fact.fact_key == chain.fact_key and other_fact_id != fact_id:
                    dependencies.append(other_fact_id)
                    continue
                    
                other_chain = self.resolve_lineage(other_fact_id)
                
                # Check for overlapping fragments
                fact_fragments = set([n.node_id for n in chain.get_fragments()])
                other_fragments = set([n.node_id for n in other_chain.get_fragments()])
                
                if fact_fragments & other_fragments:
                    dependencies.append(other_fact_id)
                    continue
                    
                # Check for overlapping assets
                fact_assets = set([n.node_id for n in chain.get_assets()])
                other_assets = set([n.node_id for n in other_chain.get_assets()])
                
                if fact_assets & other_assets:
                    dependencies.append(other_fact_id)
                    continue
                    
                # Check for overlapping sources
                fact_sources = set([n.node_id for n in chain.get_sources()])
                other_sources = set([n.node_id for n in other_chain.get_sources()])
                
                if fact_sources & other_sources:
                    dependencies.append(other_fact_id)
                    
            graph[fact_id] = list(set(dependencies))  # Remove duplicates
            
        return graph
