"""
审核队列测试

测试 ReviewQueue 类的功能。
"""
import pytest
from datetime import datetime
from engine.intake import ReviewQueue, ReviewStatus, ReviewPriority, create_review_queue, add_to_queue
from engine.evidence import EvidenceFragment, FragmentType


class TestReviewQueue:
    """测试审核队列"""
    
    @pytest.fixture
    def sample_fragment(self):
        """返回示例证据片段"""
        return type('EvidenceFragment', (), {
            "fragment_id": "TEST-FRAG-1",
            "fragment_type": FragmentType.TEXT,
            "fragment_key": "TEST-FRAG-1",
            "content": "测试内容",
            "metadata": {
                "source": "test.pdf",
                "page": 1
            }
        })()
    
    @pytest.fixture
    def review_queue(self):
        """创建审核队列实例"""
        return ReviewQueue()
    
    def test_add_to_queue(self, review_queue, sample_fragment):
        """测试添加到队列"""
        review_id = review_queue.add_to_queue(sample_fragment)
        assert isinstance(review_id, str)
        assert review_id.startswith("REV-")
        
        queue = review_queue.get_queue()
        assert len(queue) == 1
        
        task = queue[0]
        assert task["review_id"] == review_id
        assert task["fragment"] == sample_fragment
        assert task["status"] == ReviewStatus.PENDING
        assert task["priority"] == ReviewPriority.MEDIUM
    
    def test_add_to_queue_with_metadata(self, review_queue, sample_fragment):
        """测试添加到队列时的元数据"""
        metadata = {
            "reviewer": "test_reviewer",
            "due_date": "2023-12-31"
        }
        
        review_id = review_queue.add_to_queue(
            sample_fragment, 
            priority=ReviewPriority.HIGH,
            reviewer="test_reviewer",
            metadata=metadata
        )
        
        queue = review_queue.get_queue()
        assert len(queue) == 1
        task = queue[0]
        
        assert task["priority"] == ReviewPriority.HIGH
        assert task["reviewer"] == "test_reviewer"
        assert task["metadata"] == metadata
    
    def test_get_queue_by_status(self, review_queue, sample_fragment):
        """测试按状态获取队列"""
        # 添加到队列
        review_queue.add_to_queue(sample_fragment)
        
        # 获取待审核任务
        pending_queue = review_queue.get_queue(status=ReviewStatus.PENDING)
        assert len(pending_queue) == 1
        
        # 开始审核
        review_id = pending_queue[0]["review_id"]
        review_queue.start_review(review_id, "reviewer1")
        
        # 获取审核中的任务
        in_review_queue = review_queue.get_queue(status=ReviewStatus.IN_REVIEW)
        assert len(in_review_queue) == 1
        assert in_review_queue[0]["review_id"] == review_id
        
        # 获取待审核任务（现在应该是空的）
        pending_queue = review_queue.get_queue(status=ReviewStatus.PENDING)
        assert len(pending_queue) == 0
    
    def test_get_queue_by_priority(self, review_queue, sample_fragment):
        """测试按优先级获取队列"""
        # 添加不同优先级的任务
        review_queue.add_to_queue(sample_fragment, priority=ReviewPriority.LOW)
        review_queue.add_to_queue(sample_fragment, priority=ReviewPriority.MEDIUM)
        review_queue.add_to_queue(sample_fragment, priority=ReviewPriority.HIGH)
        
        low_queue = review_queue.get_queue(priority=ReviewPriority.LOW)
        medium_queue = review_queue.get_queue(priority=ReviewPriority.MEDIUM)
        high_queue = review_queue.get_queue(priority=ReviewPriority.HIGH)
        
        assert len(low_queue) == 1
        assert len(medium_queue) == 1
        assert len(high_queue) == 1
        
        assert low_queue[0]["priority"] == ReviewPriority.LOW
        assert medium_queue[0]["priority"] == ReviewPriority.MEDIUM
        assert high_queue[0]["priority"] == ReviewPriority.HIGH
    
    def test_start_review(self, review_queue, sample_fragment):
        """测试开始审核"""
        review_id = review_queue.add_to_queue(sample_fragment)
        
        success = review_queue.start_review(review_id, "reviewer1")
        assert success is True
        
        queue = review_queue.get_queue(status=ReviewStatus.IN_REVIEW)
        assert len(queue) == 1
        assert queue[0]["reviewer"] == "reviewer1"
    
    def test_complete_review(self, review_queue, sample_fragment):
        """测试完成审核"""
        review_id = review_queue.add_to_queue(sample_fragment)
        review_queue.start_review(review_id, "reviewer1")
        
        success = review_queue.complete_review(
            review_id, 
            status=ReviewStatus.APPROVED,
            reviewer="reviewer1",
            comment="通过审核"
        )
        assert success is True
        
        # 检查是否已移动到历史记录
        queue = review_queue.get_queue()
        assert len(queue) == 0
        
        history = review_queue.get_review_history()
        assert len(history) == 1
        assert history[0]["review_id"] == review_id
    
    def test_complete_review_with_revision(self, review_queue, sample_fragment):
        """测试完成审核（需要修订）"""
        review_id = review_queue.add_to_queue(sample_fragment)
        review_queue.start_review(review_id, "reviewer1")
        
        success = review_queue.complete_review(
            review_id, 
            status=ReviewStatus.NEEDS_REVISION,
            reviewer="reviewer1",
            comment="需要进一步修订"
        )
        assert success is True
        
        # 检查是否仍在队列中，但状态为需要修订
        queue = review_queue.get_queue(status=ReviewStatus.NEEDS_REVISION)
        assert len(queue) == 1
        assert queue[0]["review_id"] == review_id
    
    def test_get_review_history(self, review_queue, sample_fragment):
        """测试获取审核历史"""
        # 添加到队列
        review_id = review_queue.add_to_queue(sample_fragment)
        
        # 开始审核
        review_queue.start_review(review_id, "reviewer1")
        
        # 完成审核
        review_queue.complete_review(
            review_id, 
            status=ReviewStatus.APPROVED,
            reviewer="reviewer1",
            comment="通过审核"
        )
        
        history = review_queue.get_review_history()
        assert len(history) == 1
        assert history[0]["review_id"] == review_id
        assert history[0]["status"] == ReviewStatus.APPROVED
        
        # 检查历史记录的属性
        assert "fragment_id" in history[0]
        assert "fragment" in history[0]
        assert "completed_at" in history[0]
        assert len(history[0]["history"]) > 0
    
    def test_get_statistics(self, review_queue, sample_fragment):
        """测试获取统计信息"""
        # 添加到队列
        review_queue.add_to_queue(sample_fragment)
        
        stats = review_queue.get_statistics()
        assert stats["pending"] == 1
        assert stats["in_review"] == 0
        assert stats["approved"] == 0
        assert stats["rejected"] == 0
        assert stats["total"] == 1
        
        # 开始审核
        review_id = review_queue.get_queue()[0]["review_id"]
        review_queue.start_review(review_id, "reviewer1")
        
        stats = review_queue.get_statistics()
        assert stats["pending"] == 0
        assert stats["in_review"] == 1
        assert stats["total"] == 1
        
        # 完成审核
        review_queue.complete_review(
            review_id, 
            status=ReviewStatus.APPROVED,
            reviewer="reviewer1",
            comment="通过审核"
        )
        
        stats = review_queue.get_statistics()
        assert stats["pending"] == 0
        assert stats["in_review"] == 0
        assert stats["approved"] == 1
        assert stats["total"] == 1
    
    def test_convenience_functions(self, sample_fragment):
        """测试便捷函数"""
        # 测试创建队列
        queue = create_review_queue()
        assert isinstance(queue, ReviewQueue)
        
        # 测试添加到队列
        review_id = add_to_queue(sample_fragment)
        assert isinstance(review_id, str)
        assert review_id.startswith("REV-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
