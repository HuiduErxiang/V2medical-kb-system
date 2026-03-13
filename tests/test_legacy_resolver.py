"""
LegacyResolver适配测试

验证V1旧结构到V2四层对象的适配。
"""
import pytest
from pathlib import Path

from engine.evidence import LegacyResolver, EvidenceRegistry


class TestLegacyResolverDefaultPath:
    """测试LegacyResolver默认路径"""
    
    def test_default_v1_path_is_correct(self):
        """验证默认V1路径是正确的绝对路径"""
        resolver = LegacyResolver()
        
        expected_path = Path(r"D:\汇度编辑部1\写作知识库\medical_kb_system")
        
        assert resolver.v1_base_path == expected_path, \
            f"默认路径错误: 期望 {expected_path}, 实际 {resolver.v1_base_path}"
    
    def test_default_v1_path_exists(self):
        """验证默认V1路径存在
        
        注意：此测试依赖本地环境，CI环境可能需要跳过。
        如果路径不存在，说明V1目录未正确部署或路径配置错误。
        """
        resolver = LegacyResolver()
        
        # 不使用assert，而是显式说明情况
        if not resolver.v1_base_path.exists():
            pytest.fail(
                f"默认V1路径不存在: {resolver.v1_base_path}\n"
                f"可能原因：\n"
                f"  1. V1目录未部署到预期位置\n"
                f"  2. 路径配置错误（检查LegacyResolver.DEFAULT_V1_BASE_PATH）\n"
                f"  3. 当前运行环境不是生产环境"
            )


class TestLegacyResolver:
    """测试LegacyResolver核心功能"""
    
    def test_custom_v1_path(self):
        """测试自定义V1路径"""
        custom_path = Path("/some/custom/path")
        resolver = LegacyResolver(v1_base_path=custom_path)
        
        assert resolver.v1_base_path == custom_path
    
    def test_resolve_sources_structure(self):
        """测试resolve_sources返回结构"""
        resolver = LegacyResolver()
        
        try:
            sources = resolver.resolve_sources({"product_id": "lecanemab"})
            assert isinstance(sources, list)
            
            if sources:
                source = sources[0]
                assert hasattr(source, 'source_id')
                assert hasattr(source, 'source_type')
                assert hasattr(source, 'source_key')
                assert source.source_key.startswith("SRC-")
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_facts_structure(self):
        """测试resolve_facts返回结构"""
        resolver = LegacyResolver()
        
        try:
            facts = resolver.resolve_facts({"product_id": "lecanemab"})
            assert isinstance(facts, list)
            
            if facts:
                fact = facts[0]
                assert hasattr(fact, 'fact_id')
                assert hasattr(fact, 'fact_key')
                assert hasattr(fact, 'domain')
                assert fact.fact_id.startswith("FCT-")
                assert fact.domain in ['efficacy', 'safety', 'biomarker', 'moa', 'trial_design', 'competitor']
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_facts_by_domain(self):
        """测试按domain过滤"""
        resolver = LegacyResolver()
        
        try:
            facts = resolver.resolve_facts({
                "product_id": "lecanemab",
                "domain": "efficacy"
            })
            for fact in facts:
                assert fact.domain == "efficacy"
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_resolve_fact_lineage(self):
        """测试事实血缘查询"""
        resolver = LegacyResolver()
        
        try:
            facts = resolver.resolve_facts({"product_id": "lecanemab"})
            if facts:
                fact_id = facts[0].fact_id
                lineage = resolver.resolve_fact_lineage(fact_id)
                assert "fact_id" in lineage
                assert "sources" in lineage
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_fact_lineage_invalid_id(self):
        """测试无效fact_id的血缘查询"""
        resolver = LegacyResolver()
        lineage = resolver.resolve_fact_lineage("invalid-id")
        
        assert "error" in lineage or "fact_id" in lineage


class TestLegacyResolverIntegration:
    """测试LegacyResolver与EvidenceRegistry集成"""
    
    def test_load_into_registry(self):
        """测试将V1数据加载到registry"""
        resolver = LegacyResolver()
        
        try:
            registry = EvidenceRegistry()
            sources = resolver.resolve_sources({"product_id": "lecanemab"})
            
            for source in sources:
                registry.register_source(source)
            
            assert len(registry.sources) == len(sources)
            
            if sources:
                retrieved = registry.get_source_by_key(sources[0].source_key)
                assert retrieved is not None
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")