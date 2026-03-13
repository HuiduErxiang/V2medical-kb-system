"""
证据晋升模块

负责将通过审核的证据片段晋升为事实记录。
intake 后半段的第四阶段。
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

from ..evidence.models import EvidenceFragment, FactRecord, FactStatus
from ..evidence.lineage import LineageChain, LineageNode
from ..evidence.query import EvidenceQuery, QueryType


class PromoteManager:
    """
    证据晋升管理器
    
    负责将通过审核的证据片段晋升为事实记录。
    
    Phase 3 实现：
    - 支持证据片段到事实记录的转换
    - 事实状态管理
    - 晋升历史记录
    - 质量检查接口
    """
    
    def __init__(self, registry=None, query: Optional[EvidenceQuery] = None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
            query: EvidenceQuery 实例（可选）
        """
        self.registry = registry
        self.query = query or EvidenceQuery(registry)
        self._promotion_history: List[Dict[str, Any]] = []
    
    def promote(self, fragment: EvidenceFragment, 
                status: FactStatus = FactStatus.DRAFT,
                reviewer: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> FactRecord:
        """
        晋升证据片段为事实记录
        
        Args:
            fragment: 证据片段
            status: 事实状态
            reviewer: 晋升审核者（可选）
            metadata: 额外元数据
        
        Returns:
            FactRecord: 创建的事实记录
        """
        # 检查是否已存在相同内容的事实
        existing_fact = self._find_existing_fact(fragment)
        if existing_fact:
            return self._update_existing_fact(existing_fact, fragment, reviewer)
        
        # 创建新事实记录
        fact_record = self._create_fact_from_fragment(fragment, status, reviewer, metadata)
        
        # 记录晋升历史
        self._record_promotion(fragment, fact_record, reviewer)
        
        # 注册到 registry
        if self.registry:
            self.registry.register_fact(fact_record)
        
        return fact_record
    
    def promote_batch(self, fragments: List[EvidenceFragment],
                     status: FactStatus = FactStatus.DRAFT,
                     reviewer: Optional[str] = None,
                     metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[FactRecord]:
        """
        批量晋升证据片段为事实记录
        
        Args:
            fragments: 证据片段列表
            status: 事实状态
            reviewer: 晋升审核者（可选）
            metadata_list: 元数据列表（可选）
        
        Returns:
            List[FactRecord]: 创建的事实记录列表
        """
        facts = []
        
        if metadata_list is None:
            metadata_list = [None] * len(fragments)
        
        for fragment, meta in zip(fragments, metadata_list):
            fact = self.promote(fragment, status, reviewer, meta)
            facts.append(fact)
        
        return facts
    
    def promote_approved(self, queue: Any, reviewer: str) -> List[FactRecord]:
        """
        晋升所有已批准的证据片段
        
        Args:
            queue: 审核队列
            reviewer: 审核者
        
        Returns:
            List[FactRecord]: 创建的事实记录列表
        """
        approved_fragments = []
        
        # 从审核队列获取已批准的片段
        approved_tasks = queue.get_queue(status=queue.REVIEW_STATUS_APPROVED)  # type: ignore
        for task in approved_tasks:
            approved_fragments.append(task["fragment"])
        
        # 晋升所有已批准片段
        return self.promote_batch(approved_fragments, FactStatus.APPROVED, reviewer)
    
    def update_fact_status(self, fact_record: FactRecord, 
                         new_status: FactStatus,
                         reviewer: Optional[str] = None,
                         comment: str = "") -> FactRecord:
        """
        更新事实状态
        
        Args:
            fact_record: 事实记录
            new_status: 新状态
            reviewer: 审核者（可选）
            comment: 状态变更说明
        
        Returns:
            FactRecord: 更新后的事实记录
        """
        fact_record.status = new_status
        fact_record.metadata["status_updated_at"] = datetime.now().isoformat()
        fact_record.metadata["status_updated_by"] = reviewer
        fact_record.metadata["status_comment"] = comment
        
        if "status_history" not in fact_record.metadata:
            fact_record.metadata["status_history"] = []
        
        fact_record.metadata["status_history"].append({
            "status": new_status.value,
            "timestamp": datetime.now().isoformat(),
            "actor": reviewer,
            "comment": comment
        })
        
        # 重新注册到 registry
        if self.registry:
            self.registry.register_fact(fact_record)
        
        return fact_record
    
    def get_promotion_history(self, fragment_id: Optional[str] = None,
                           fact_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取晋升历史记录
        
        Args:
            fragment_id: 片段ID筛选（可选）
            fact_id: 事实ID筛选（可选）
        
        Returns:
            List[Dict[str, Any]]: 晋升历史记录
        """
        history = self._promotion_history
        
        if fragment_id:
            history = [h for h in history if h["fragment_id"] == fragment_id]
        
        if fact_id:
            history = [h for h in history if h["fact_id"] == fact_id]
        
        return sorted(history, key=lambda x: x["promoted_at"], reverse=True)
    
    def _find_existing_fact(self, fragment: EvidenceFragment) -> Optional[FactRecord]:
        """查找是否已存在相同内容的事实"""
        # 简化实现：通过内容哈希查找
        if self.query:
            # 这里可以使用 query 查找类似内容的事实
            pass
        
        return None
    
    def _create_fact_from_fragment(self, fragment: EvidenceFragment, 
                                  status: FactStatus, reviewer: str,
                                  metadata: Optional[Dict[str, Any]] = None) -> FactRecord:
        """从证据片段创建事实记录"""
        fact_key = self._generate_fact_key(fragment)
        fact_id = self._generate_fact_id(fact_key)
        
        lineage = self._create_lineage_for_fact(fragment)
        
        full_metadata = {
            "promoted_at": datetime.now().isoformat(),
            "promoted_by": reviewer,
            "original_fragment": fragment.fragment_id,
            **(metadata or {}),
            **fragment.metadata
        }
        
        fact_record = FactRecord(
            fact_id=fact_id,
            fact_key=fact_key,
            domain=full_metadata.get("domain", "general"),
            content=fragment.content,
            status=status,
            metadata=full_metadata,
            lineage=lineage
        )
        
        return fact_record
    
    def _update_existing_fact(self, existing_fact: FactRecord, 
                           fragment: EvidenceFragment,
                           reviewer: str) -> FactRecord:
        """更新已存在的事实记录"""
        # 合并内容和元数据
        existing_fact.content = fragment.content
        existing_fact.metadata.update({
            "last_updated_at": datetime.now().isoformat(),
            "last_updated_by": reviewer,
            "last_promoted_fragment": fragment.fragment_id
        })
        
        return existing_fact
    
    def _create_lineage_for_fact(self, fragment: EvidenceFragment) -> LineageChain:
        """为事实创建 lineage"""
        lineage = LineageChain()
        
        # 检查片段是否有 lineage 属性
        if hasattr(fragment, 'lineage') and fragment.lineage:
            if hasattr(fragment.lineage, 'nodes'):
                for node in fragment.lineage.nodes:
                    lineage.add_node(node.copy())
        
        # 添加晋升节点
        promotion_node = LineageNode(
            node_type="promotion",
            node_id=f"promote-{datetime.now().timestamp()}",
            node_key=f"promote-{datetime.now().timestamp()}",
            metadata={
                "promoted_at": datetime.now().isoformat(),
                "promotion_type": "initial"
            }
        )
        
        lineage.add_node(promotion_node)
        
        return lineage
    
    def _record_promotion(self, fragment: EvidenceFragment, 
                        fact_record: FactRecord, reviewer: str):
        """记录晋升历史"""
        self._promotion_history.append({
            "fragment_id": fragment.fragment_id,
            "fact_id": fact_record.fact_id,
            "promoted_at": datetime.now().isoformat(),
            "promoted_by": reviewer,
            "status": fact_record.status.value,
            "lineage_length": len(fact_record.lineage.nodes) if fact_record.lineage else 0
        })
    
    def _generate_fact_key(self, fragment: EvidenceFragment) -> str:
        """生成事实键"""
        content_hash = hashlib.sha256(fragment.content.encode()).hexdigest()[:8].upper()
        return f"FACT-{content_hash}"
    
    def _generate_fact_id(self, fact_key: str) -> str:
        """生成事实ID"""
        return fact_key


def promote_fragment(fragment: EvidenceFragment, 
                    status: FactStatus = FactStatus.DRAFT,
                    reviewer: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> FactRecord:
    """便捷函数：晋升单个证据片段"""
    manager = PromoteManager()
    return manager.promote(fragment, status, reviewer, metadata)


def promote_fragments(fragments: List[EvidenceFragment],
                     status: FactStatus = FactStatus.DRAFT,
                     reviewer: Optional[str] = None,
                     metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[FactRecord]:
    """便捷函数：批量晋升证据片段"""
    manager = PromoteManager()
    return manager.promote_batch(fragments, status, reviewer, metadata_list)
