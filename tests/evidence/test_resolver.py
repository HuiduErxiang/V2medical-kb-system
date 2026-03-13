"""
EvidenceResolver Phase 2 扩展方法测试
"""
import pytest
from datetime import datetime, timedelta

from engine.evidence import (
    EvidenceRegistry, LegacyResolver
)
from engine.evidence.models import FactRecord, FactStatus


class TestResolverExtendedMethods:
    """测试resolver扩展方法"""
    
    @pytest.fixture
    def resolver(self):
        """创建LegacyResolver实例"""
        return LegacyResolver()
    
    def test_resolve_by_domain(self, resolver):
        """测试按领域查询"""
        try:
            facts = resolver.resolve_by_domain("lecanemab", "efficacy")
            
            for fact in facts:
                assert fact.domain == "efficacy"
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_by_fact_keys(self, resolver):
        """测试按键列表查询"""
        try:
            # 先获取所有事实，然后选取几个key
            all_facts = resolver.resolve_facts({"product_id": "lecanemab"})
            
            if len(all_facts) >= 2:
                keys = [f.fact_key for f in all_facts[:2]]
                facts = resolver.resolve_by_fact_keys("lecanemab", keys)
                
                assert len(facts) <= 2
                for fact in facts:
                    assert fact.fact_key in keys
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_by_time_range(self, resolver):
        """测试按时间范围查询"""
        try:
            now = datetime.now()
            start = now - timedelta(days=365)
            end = now
            
            facts = resolver.resolve_by_time_range("lecanemab", start, end)
            
            assert isinstance(facts, list)
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_conflicts(self, resolver):
        """测试冲突检测"""
        try:
            conflicts = resolver.resolve_conflicts("lecanemab")
            
            assert isinstance(conflicts, dict)
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_count_facts_by_domain(self, resolver):
        """测试按领域统计"""
        try:
            counts = resolver.count_facts_by_domain("lecanemab")
            
            assert isinstance(counts, dict)
            
            for domain, count in counts.items():
                assert isinstance(domain, str)
                assert count > 0

        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_search_facts(self, resolver):
        """测试关键词搜索"""
        try:
            # 使用常见的医学关键词
            facts = resolver.search_facts("lecanemab", "efficacy")
            
            assert isinstance(facts, list)
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_latest_facts(self, resolver):
        """测试获取最新事实"""
        try:
            facts = resolver.resolve_latest_facts("lecanemab", limit=5)
            
            assert len(facts) <= 5
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")