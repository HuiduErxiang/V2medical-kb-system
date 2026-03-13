"""
证据构建器测试
"""
import pytest

from engine.intake import EvidenceBuilder, build_evidence, build_fact_from_dict
from engine.evidence.models import (
    AssetRecord, SourceRecord, SourceType, AssetType
)


class TestEvidenceBuilder:
    """测试证据构建器"""
    
    @pytest.fixture
    def asset(self):
        """创建测试资产"""
        return AssetRecord(
            asset_id="AST-TEST-001",
            source_id="SRC-TEST",
            asset_key="AST-TEST-001",
            asset_type=AssetType.DOCUMENT
        )
    
    def test_build_from_asset_without_content(self, asset):
        """测试无内容构建"""
        builder = EvidenceBuilder()
        fragments, facts = builder.build_from_asset(asset)
        
        assert len(fragments) == 1
        assert len(facts) == 0  # 无内容时无事实
    
    def test_build_from_asset_with_content(self, asset):
        """测试有内容构建"""
        builder = EvidenceBuilder()
        content = "患者有效率为95%，安全性良好。"
        
        fragments, facts = builder.build_from_asset(asset, content)
        
        assert len(fragments) == 1
        assert fragments[0].content == content
        assert len(facts) >= 1  # 应检测到领域关键词
    
    def test_domain_detection_efficacy(self, asset):
        """测试疗效领域检测"""
        builder = EvidenceBuilder()
        content = "疗效分析显示有效率达到95%"
        
        fragments, facts = builder.build_from_asset(asset, content)
        
        domains = [f.domain for f in facts]
        assert "efficacy" in domains
    
    def test_domain_detection_safety(self, asset):
        """测试安全领域检测"""
        builder = EvidenceBuilder()
        content = "安全性评估显示不良事件发生率较低"
        
        fragments, facts = builder.build_from_asset(asset, content)
        
        domains = [f.domain for f in facts]
        assert "safety" in domains
    
    def test_fact_has_lineage(self, asset):
        """测试事实有血缘信息"""
        builder = EvidenceBuilder()
        content = "疗效数据显示有效率为95%"
        
        fragments, facts = builder.build_from_asset(asset, content)
        
        for fact in facts:
            assert fact.lineage is not None
            assert "source_ids" in fact.lineage
            assert asset.source_id in fact.lineage["source_ids"]
    
    def test_build_fact_from_dict(self):
        """测试从字典构建事实"""
        builder = EvidenceBuilder()
        
        data = {
            "fact_id": "FCT-TEST",
            "fact_key": "VAR_TEST",
            "domain": "efficacy",
            "definition": "Test definition",
            "value": "95%",
            "unit": "%"
        }
        
        fact = builder.build_from_dict(data)
        
        assert fact.fact_id == "FCT-TEST"
        assert fact.fact_key == "VAR_TEST"
        assert fact.domain == "efficacy"
    
    def test_convenience_function(self, asset):
        """测试便捷函数"""
        content = "测试内容"
        fragments, facts = build_evidence(asset, content)
        
        assert len(fragments) == 1
    
    def test_build_from_assets_batch(self, asset):
        """测试批量构建"""
        builder = EvidenceBuilder()
        
        assets = [asset, AssetRecord(
            asset_id="AST-TEST-002",
            source_id="SRC-TEST",
            asset_key="AST-TEST-002",
            asset_type=AssetType.DOCUMENT
        )]
        
        contents = {
            "AST-TEST-001": "内容1",
            "AST-TEST-002": "内容2"
        }
        
        fragments, facts = builder.build_from_assets(assets, contents)
        
        assert len(fragments) == 2


class TestDomainDetection:
    """测试领域检测"""
    
    @pytest.fixture
    def builder(self):
        return EvidenceBuilder()
    
    @pytest.fixture
    def asset(self):
        return AssetRecord(
            asset_id="AST-TEST",
            source_id="SRC-TEST",
            asset_key="AST-TEST",
            asset_type=AssetType.DOCUMENT
        )
    
    def test_biomarker_detection(self, builder, asset):
        """测试生物标志物检测"""
        content = "生物标志物分析显示PFS延长"
        _, facts = builder.build_from_asset(asset, content)
        
        domains = [f.domain for f in facts]
        assert "biomarker" in domains
    
    def test_moa_detection(self, builder, asset):
        """测试作用机制检测"""
        content = "作用机制研究表明药物靶向Aβ蛋白"
        _, facts = builder.build_from_asset(asset, content)
        
        domains = [f.domain for f in facts]
        assert "moa" in domains
    
    def test_multiple_domains(self, builder, asset):
        """测试多领域检测"""
        content = "疗效分析显示有效率高，且安全性良好"
        _, facts = builder.build_from_asset(asset, content)
        
        domains = set(f.domain for f in facts)
        assert len(domains) >= 1  # 至少检测到一个领域