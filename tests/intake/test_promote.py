"""
证据晋升模块测试

测试 PromoteManager 类的功能。
"""
import pytest
from datetime import datetime
from engine.intake import PromoteManager, promote_fragment, promote_fragments
from engine.evidence import EvidenceFragment, FragmentType, FactStatus
from engine.evidence.registry import EvidenceRegistry


class TestPromoteManager:
    """测试证据晋升管理器"""
    
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
    def promote_manager(self):
        """创建证据晋升管理器实例"""
        return PromoteManager()
    
    @pytest.fixture
    def registry(self):
        """创建证据注册表"""
        return EvidenceRegistry()
    
    def test_promote_fragment(self, promote_manager, sample_fragment):
        """测试晋升证据片段"""
        fact = promote_manager.promote(sample_fragment)
        assert fact is not None
        
        assert isinstance(fact, object)
        assert fact.fact_id is not None
        assert fact.fact_id.startswith("FACT-")
        
        assert fact.fact_key is not None
        assert fact.fact_key.startswith("FACT-")
        
        assert fact.content == sample_fragment.content
        assert fact.status == FactStatus.DRAFT
        
        # 检查元数据
        assert "promoted_at" in fact.metadata
        assert "original_fragment" in fact.metadata
        assert fact.metadata["original_fragment"] == sample_fragment.fragment_id
    
    def test_promote_batch(self, promote_manager, sample_fragment):
        """测试批量晋升"""
        fragments = [
            sample_fragment,
            sample_fragment,
            sample_fragment
        ]
        
        facts = promote_manager.promote_batch(fragments)
        assert len(facts) == 3
        
        for fact in facts:
            assert fact is not None
            assert fact.fact_id is not None
            assert fact.content == sample_fragment.content
    
    def test_promote_with_status(self, promote_manager, sample_fragment):
        """测试晋升时指定状态"""
        fact = promote_manager.promote(
            sample_fragment, 
            status=FactStatus.APPROVED,
            reviewer="test_reviewer"
        )
        
        assert fact.status == FactStatus.APPROVED
        assert fact.metadata["promoted_by"] == "test_reviewer"
    
    def test_promote_with_metadata(self, promote_manager, sample_fragment):
        """测试晋升时指定元数据"""
        metadata = {
            "domain": "efficacy",
            "source": "test.pdf"
        }
        
        fact = promote_manager.promote(
            sample_fragment, 
            status=FactStatus.APPROVED,
            reviewer="test_reviewer",
            metadata=metadata
        )
        
        assert fact.metadata["domain"] == "efficacy"
        assert fact.metadata["source"] == "test.pdf"
    
    def test_promote_with_registry(self, promote_manager, sample_fragment, registry):
        """测试使用注册表"""
        manager = PromoteManager(registry)
        fact = manager.promote(sample_fragment)
        
        assert registry.get_fact(fact.fact_id) == fact
    
    def test_update_fact_status(self, promote_manager, sample_fragment):
        """测试更新事实状态"""
        fact = promote_manager.promote(sample_fragment)
        assert fact.status == FactStatus.DRAFT
        
        updated_fact = promote_manager.update_fact_status(
            fact, 
            new_status=FactStatus.APPROVED,
            reviewer="test_reviewer",
            comment="通过审核"
        )
        
        assert updated_fact.status == FactStatus.APPROVED
        assert updated_fact.metadata["status_updated_by"] == "test_reviewer"
        assert updated_fact.metadata["status_comment"] == "通过审核"
        
        # 检查状态历史
        assert "status_history" in updated_fact.metadata
        assert len(updated_fact.metadata["status_history"]) > 0
        
        history_item = updated_fact.metadata["status_history"][0]
        assert history_item["status"] == FactStatus.APPROVED.value
        assert history_item["actor"] == "test_reviewer"
        assert history_item["comment"] == "通过审核"
    
    def test_get_promotion_history(self, promote_manager, sample_fragment):
        """测试获取晋升历史"""
        promote_manager.promote(sample_fragment)
        
        history = promote_manager.get_promotion_history()
        assert len(history) >= 1
        
        # 检查历史记录的属性
        entry = history[0]
        assert "fragment_id" in entry
        assert "fact_id" in entry
        assert "promoted_at" in entry
        assert "promoted_by" in entry
        assert "status" in entry
    
    def test_promote_approved(self, promote_manager, sample_fragment):
        """测试晋升已批准的片段"""
        # 创建模拟审核队列
        class MockReviewQueue:
            @property
            def REVIEW_STATUS_APPROVED(self):
                return "approved"
                
            def get_queue(self, status):
                return [
                    {
                        "fragment": sample_fragment
                    }
                ]
        
        queue = MockReviewQueue()
        
        facts = promote_manager.promote_approved(queue, "test_reviewer")
        
        assert len(facts) == 1
        
        fact = facts[0]
        assert fact is not None
        assert fact.status == FactStatus.APPROVED
    
    def test_convenience_functions(self, sample_fragment):
        """测试便捷函数"""
        # 测试单个片段晋升
        fact1 = promote_fragment(sample_fragment)
        assert fact1 is not None
        
        # 测试批量晋升
        facts2 = promote_fragments([sample_fragment, sample_fragment])
        assert len(facts2) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
