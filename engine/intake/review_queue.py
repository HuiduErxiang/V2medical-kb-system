"""
审核队列管理

管理证据片段的审核排队与处理流程。
intake 后半段的第三阶段。
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import hashlib

from ..evidence.models import EvidenceFragment, FactRecord, FactStatus
from ..evidence.lineage import LineageChain, LineageNode


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ReviewPriority(Enum):
    """审核优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewQueue:
    """
    审核队列
    
    管理证据片段的审核排队、分发和处理流程。
    
    Phase 3 实现：
    - 支持基础的审核队列管理
    - 审核状态跟踪
    - 优先级排序
    - 审核历史记录
    """
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
        self._queue: List[Dict[str, Any]] = []
        self._history: List[Dict[str, Any]] = []
    
    def add_to_queue(self, fragment: EvidenceFragment, 
                     priority: ReviewPriority = ReviewPriority.MEDIUM,
                     reviewer: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加到审核队列
        
        Args:
            fragment: 证据片段
            priority: 审核优先级
            reviewer: 指派的审核者（可选）
            metadata: 额外元数据
        
        Returns:
            str: 审核任务ID
        """
        review_task = {
            "review_id": self._generate_review_id(fragment),
            "fragment_id": fragment.fragment_id,
            "fragment": fragment,
            "status": ReviewStatus.PENDING,
            "priority": priority,
            "reviewer": reviewer,
            "added_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "history": []
        }
        
        # 记录初始状态
        review_task["history"].append({
            "status": ReviewStatus.PENDING.value,
            "timestamp": review_task["added_at"],
            "action": "added_to_queue",
            "actor": None
        })
        
        # 添加到队列
        self._queue.append(review_task)
        
        return review_task["review_id"]
    
    def add_batch_to_queue(self, fragments: List[EvidenceFragment],
                          priority: ReviewPriority = ReviewPriority.MEDIUM,
                          reviewer: Optional[str] = None,
                          metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        批量添加到审核队列
        
        Args:
            fragments: 证据片段列表
            priority: 审核优先级
            reviewer: 指派的审核者（可选）
            metadata_list: 元数据列表（可选）
        
        Returns:
            List[str]: 审核任务ID列表
        """
        review_ids = []
        
        if metadata_list is None:
            metadata_list = [None] * len(fragments)
        
        for fragment, meta in zip(fragments, metadata_list):
            review_id = self.add_to_queue(fragment, priority, reviewer, meta)
            review_ids.append(review_id)
        
        return review_ids
    
    def get_queue(self, status: Optional[ReviewStatus] = None,
                 priority: Optional[ReviewPriority] = None) -> List[Dict[str, Any]]:
        """
        获取审核队列
        
        Args:
            status: 状态筛选（可选）
            priority: 优先级筛选（可选）
        
        Returns:
            List[Dict[str, Any]]: 符合条件的审核任务列表
        """
        filtered = self._queue
        
        if status:
            filtered = [task for task in filtered if task["status"] == status]
        
        if priority:
            filtered = [task for task in filtered if task["priority"] == priority]
        
        # 按优先级排序
        filtered = sorted(filtered, key=lambda x: self._priority_to_number(x["priority"]))
        
        return filtered
    
    def start_review(self, review_id: str, reviewer: str) -> bool:
        """
        开始审核
        
        Args:
            review_id: 审核任务ID
            reviewer: 审核者
        
        Returns:
            bool: 是否成功
        """
        task = self._find_task(review_id)
        if task and task["status"] == ReviewStatus.PENDING:
            task["status"] = ReviewStatus.IN_REVIEW
            task["reviewer"] = reviewer
            task["history"].append({
                "status": ReviewStatus.IN_REVIEW.value,
                "timestamp": datetime.now().isoformat(),
                "action": "start_review",
                "actor": reviewer
            })
            return True
        return False
    
    def complete_review(self, review_id: str, status: ReviewStatus,
                       reviewer: str, comment: str = "",
                       revised_fragment: Optional[EvidenceFragment] = None) -> bool:
        """
        完成审核
        
        Args:
            review_id: 审核任务ID
            status: 审核结果状态
            reviewer: 审核者
            comment: 审核意见
            revised_fragment: 修订后的片段（可选）
        
        Returns:
            bool: 是否成功
        """
        task = self._find_task(review_id)
        if task and task["status"] in [ReviewStatus.PENDING, ReviewStatus.IN_REVIEW]:
            task["status"] = status
            task["completed_at"] = datetime.now().isoformat()
            task["history"].append({
                "status": status.value,
                "timestamp": task["completed_at"],
                "action": "complete_review",
                "actor": reviewer,
                "comment": comment,
                "revised_fragment": revised_fragment.fragment_id if revised_fragment else None
            })
            
            # 如果是批准状态，移动到历史记录
            if status == ReviewStatus.APPROVED:
                self._history.append(task)
                self._queue.remove(task)
            
            return True
        return False
    
    def get_review_history(self, fragment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取审核历史记录
        
        Args:
            fragment_id: 片段ID筛选（可选）
        
        Returns:
            List[Dict[str, Any]]: 审核历史记录
        """
        all_history = self._history.copy()
        
        if fragment_id:
            all_history = [task for task in all_history if task["fragment_id"] == fragment_id]
        
        return sorted(all_history, key=lambda x: x["completed_at"], reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        total_pending = len(self.get_queue(ReviewStatus.PENDING))
        total_in_review = len(self.get_queue(ReviewStatus.IN_REVIEW))
        total_approved = len([task for task in self._history if task["status"] == ReviewStatus.APPROVED])
        total_rejected = len([task for task in self._history if task["status"] == ReviewStatus.REJECTED])
        
        return {
            "pending": total_pending,
            "in_review": total_in_review,
            "approved": total_approved,
            "rejected": total_rejected,
            "total": total_pending + total_in_review + total_approved + total_rejected
        }
    
    def _find_task(self, review_id: str) -> Optional[Dict[str, Any]]:
        """查找审核任务"""
        for task in self._queue:
            if task["review_id"] == review_id:
                return task
        return None
    
    def _generate_review_id(self, fragment: EvidenceFragment) -> str:
        """生成审核任务ID"""
        hash_part = hashlib.sha256(fragment.fragment_id.encode()).hexdigest()[:8].upper()
        return f"REV-{hash_part}"
    
    def _priority_to_number(self, priority: ReviewPriority) -> int:
        """将优先级转换为数字以便排序"""
        priority_map = {
            ReviewPriority.LOW: 4,
            ReviewPriority.MEDIUM: 3,
            ReviewPriority.HIGH: 2,
            ReviewPriority.CRITICAL: 1
        }
        return priority_map.get(priority, 3)


def create_review_queue(registry=None) -> ReviewQueue:
    """创建审核队列实例"""
    return ReviewQueue(registry)


def add_to_queue(fragment: EvidenceFragment, 
                priority: ReviewPriority = ReviewPriority.MEDIUM,
                reviewer: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> str:
    """便捷函数：添加到审核队列"""
    queue = ReviewQueue()
    return queue.add_to_queue(fragment, priority, reviewer, metadata)
