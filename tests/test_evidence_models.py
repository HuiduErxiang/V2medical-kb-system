"""
四层证据对象测试

验证证据模型和注册表功能。
"""
import pytest
from datetime import datetime

from engine.evidence import (
    SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
    SourceType, AssetType, FragmentType, FactStatus,
    EvidenceRegistry
)


class TestSourceRecord:
    """测试SourceRecord"""
    
    def test_creation(self):
        """创建测试"""
        source = SourceRecord(
            source_id="SRC001",
            source_type=SourceType.PDF,
            source_key="SRC-TEST-001",
            title="测试来源"
        )
        
        assert source.source_id == "SRC001"
        assert source.source_type == SourceType.PDF
        assert source.source_key == "SRC-TEST-001"


class TestAssetRecord:
    """测试AssetRecord"""
    
    def test_creation(self):
        """创建测试"""
        asset = AssetRecord(
            asset_id="AST001",
            source_id="SRC001",
            asset_key="AST-TEST-001",
            asset_type=AssetType.DOCUMENT,
            storage_key="storage/001"
        )
        
        assert asset.asset_id == "AST001"
        assert asset.content_hash is None


class TestEvidenceFragment:
    """测试EvidenceFragment"""
    
    def test_creation(self):
        """创建测试"""
        fragment = EvidenceFragment(
            fragment_id="FRG001",
            asset_id="AST001",
            fragment_key="FRG-TEST-001",
            fragment_type=FragmentType.TEXT,
            content="测试内容"
        )
        
        assert fragment.confidence == 1.0
        assert fragment.bbox is None


class TestFactRecord:
    """测试FactRecord"""
    
    def test_creation(self):
        """创建测试"""
        fact = FactRecord(
            fact_id="FCT001",
            fact_key="VAR_EFF_001",
            domain="efficacy",
            value="95%",
            unit="百分比"
        )
        
        assert fact.status == FactStatus.ACTIVE
        assert fact.domain == "efficacy"


class TestEvidenceRegistry:
    """测试EvidenceRegistry"""
    
    def test_register_and_get_source(self):
        """注册和查询来源"""
        registry = EvidenceRegistry()
        source = SourceRecord(
            source_id="SRC001",
            source_type=SourceType.PDF,
            source_key="SRC-TEST-001"
        )
        
        registry.register_source(source)
        
        # 通过ID查询
        retrieved = registry.get_source("SRC001")
        assert retrieved is not None
        assert retrieved.source_key == "SRC-TEST-001"
        
        # 通过key查询
        retrieved_by_key = registry.get_source_by_key("SRC-TEST-001")
        assert retrieved_by_key is not None
    
    def test_register_chain(self):
        """测试完整四层注册链"""
        registry = EvidenceRegistry()
        
        # 注册source
        source = SourceRecord(
            source_id="SRC001",
            source_type=SourceType.PDF,
            source_key="SRC-TEST-001"
        )
        registry.register_source(source)
        
        # 注册asset
        asset = AssetRecord(
            asset_id="AST001",
            source_id="SRC001",
            asset_key="AST-TEST-001",
            asset_type=AssetType.DOCUMENT
        )
        registry.register_asset(asset)
        
        # 注册fragment
        fragment = EvidenceFragment(
            fragment_id="FRG001",
            asset_id="AST001",
            fragment_key="FRG-TEST-001",
            fragment_type=FragmentType.TEXT,
            content="测试证据"
        )
        registry.register_fragment(fragment)
        
        # 注册fact
        fact = FactRecord(
            fact_id="FCT001",
            fact_key="VAR_TEST",
            domain="efficacy",
            value="test",
            fragment_ids=["FRG001"]
        )
        registry.register_fact(fact)
        
        # 验证关联查询
        assets = registry.get_assets_by_source("SRC001")
        assert len(assets) == 1
        
        fragments = registry.get_fragments_by_asset("AST001")
        assert len(fragments) == 1
        
        facts = registry.get_facts_by_domain("efficacy")
        assert len(facts) == 1
    
    def test_lineage(self):
        """测试血缘查询"""
        registry = EvidenceRegistry()
        
        # 构建链
        source = SourceRecord(
            source_id="SRC001",
            source_type=SourceType.PDF,
            source_key="SRC-TEST-001",
            citation="Test Citation"
        )
        registry.register_source(source)
        
        asset = AssetRecord(
            asset_id="AST001",
            source_id="SRC001",
            asset_key="AST-TEST-001",
            asset_type=AssetType.DOCUMENT
        )
        registry.register_asset(asset)
        
        fragment = EvidenceFragment(
            fragment_id="FRG001",
            asset_id="AST001",
            fragment_key="FRG-TEST-001",
            fragment_type=FragmentType.TEXT,
            content="Evidence content"
        )
        registry.register_fragment(fragment)
        
        fact = FactRecord(
            fact_id="FCT001",
            fact_key="VAR_TEST",
            domain="efficacy",
            value="value",
            fragment_ids=["FRG001"],
            lineage={"timestamps": ["2026-03-09T00:00:00"]}
        )
        registry.register_fact(fact)
        
        # 查询血缘
        lineage = registry.get_fact_lineage("FCT001")
        
        assert lineage["fact_key"] == "VAR_TEST"
        assert len(lineage["fragments"]) == 1
        assert len(lineage["sources"]) == 1
