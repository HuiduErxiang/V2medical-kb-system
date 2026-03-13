"""
证据选择结果

define evidence selection result from evidence layer.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# 导入四层证据对象
from ..evidence.models import EvidenceFragment, FactRecord


@dataclass
class EvidenceSelection:
    """
    证据选择结果 - 从证据层返回的择证结果
    
    Attributes:
        selected_facts: 选择的事实ID列表
        source_refs: 来源引用映射 {fact_id: [source_ids]}
        evidence_fragments: 证据片段列表 (EvidenceFragment对象)
        fact_records: 完整的事实记录列表 (FactRecord对象)
        metadata: 选择过程的元数据 (置信度、选择策略等)
    """
    selected_facts: List[str] = field(default_factory=list)
    source_refs: Dict[str, List[str]] = field(default_factory=dict)
    evidence_fragments: List[EvidenceFragment] = field(default_factory=list)
    fact_records: List[FactRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_fact(self, fact_id: str, source_ids: List[str]):
        """添加一个选定的事实及其来源"""
        if fact_id not in self.selected_facts:
            self.selected_facts.append(fact_id)
        self.source_refs[fact_id] = source_ids
    
    def add_fact_record(self, fact: FactRecord):
        """添加完整的FactRecord对象"""
        if fact.fact_id not in self.selected_facts:
            self.selected_facts.append(fact.fact_id)
        self.source_refs[fact.fact_id] = fact.lineage.get("source_ids", [])
        self.fact_records.append(fact)
    
    def add_fragment(self, fragment: EvidenceFragment):
        """添加EvidenceFragment对象"""
        self.evidence_fragments.append(fragment)
    
    def get_facts_by_domain(self, domain: str) -> List[FactRecord]:
        """按领域过滤事实"""
        return [f for f in self.fact_records if f.domain == domain]