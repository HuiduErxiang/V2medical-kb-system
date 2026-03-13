"""
血缘追溯模块测试
"""
import pytest

from engine.evidence import (
    EvidenceRegistry, LineageResolver, LineageChain, LineageNode
)
from engine.evidence.models import (
    SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
    SourceType, AssetType, FragmentType, FactStatus
)


class TestLineageNode:
    """测试LineageNode"""
    
    def test_creation(self):
        """创建测试"""
        from datetime import datetime
        node = LineageNode(
            node_id="test_id",
            node_type="source",
            node_key="SRC-TEST"
        )
        
        assert node.node_id == "test_id"
        assert node.node_type == "source"
        assert node.node_key == "SRC-TEST"
        assert isinstance(node.timestamp, datetime)


class TestLineageChain:
    """测试LineageChain"""
    
    def test_creation(self):
        """创建测试"""
        chain = LineageChain(fact_id="FCT-001", fact_key="VAR_TEST")
        
        assert chain.fact_id == "FCT-001"
        assert chain.fact_key == "VAR_TEST"
        assert chain.chain == []
    
    def test_add_node(self):
        """添加节点测试"""
        chain = LineageChain(fact_id="FCT-001", fact_key="VAR_TEST")
        
        node = LineageNode(
            node_id="SRC-001",
            node_type="source",
            node_key="SRC-TEST"
        )
        chain.add_node(node)
        
        assert len(chain.chain) == 1
        assert len(chain.timestamps) == 1
    
    def test_get_sources(self):
        """获取来源节点测试"""
        chain = LineageChain(fact_id="FCT-001", fact_key="VAR_TEST")
        
        chain.add_node(LineageNode("FCT-001", "fact", "VAR_TEST"))
        chain.add_node(LineageNode("FRG-001", "fragment", "FRG-TEST"))
        chain.add_node(LineageNode("AST-001", "asset", "AST-TEST"))
        chain.add_node(LineageNode("SRC-001", "source", "SRC-TEST"))
        
        sources = chain.get_sources()
        assert len(sources) == 1
        assert sources[0].node_type == "source"


class TestLineageResolver:
    """测试LineageResolver"""
    
    @pytest.fixture
    def registry(self):
        """创建测试registry"""
        registry = EvidenceRegistry()
        
        # 注册完整链路
        source = SourceRecord(
            source_id="SRC-001",
            source_type=SourceType.PDF,
            source_key="SRC-TEST",
            citation="Test Citation"
        )
        registry.register_source(source)
        
        asset = AssetRecord(
            asset_id="AST-001",
            source_id="SRC-001",
            asset_key="AST-TEST",
            asset_type=AssetType.DOCUMENT
        )
        registry.register_asset(asset)
        
        fragment = EvidenceFragment(
            fragment_id="FRG-001",
            asset_id="AST-001",
            fragment_key="FRG-TEST",
            fragment_type=FragmentType.TEXT,
            content="Test content"
        )
        registry.register_fragment(fragment)
        
        fact = FactRecord(
            fact_id="FCT-001",
            fact_key="VAR_TEST",
            domain="efficacy",
            value="95%",
            fragment_ids=["FRG-001"],
            lineage={"timestamps": ["2026-03-09T00:00:00"]}
        )
        registry.register_fact(fact)
        
        return registry
    
    def test_resolve_lineage(self, registry):
        """测试血缘解析"""
        resolver = LineageResolver(registry)
        chain = resolver.resolve_lineage("FCT-001")
        
        assert chain.fact_id == "FCT-001"
        assert chain.fact_key == "VAR_TEST"
        assert len(chain.chain) == 4  # fact, fragment, asset, source
        assert len(chain.get_sources()) == 1
    
    def test_resolve_lineage_not_found(self, registry):
        """测试不存在的事实"""
        resolver = LineageResolver(registry)
        chain = resolver.resolve_lineage("NOT-EXIST")
        
        assert chain.fact_id == "NOT-EXIST"
        assert chain.fact_key == ""
        assert len(chain.chain) == 0
    
    def test_find_conflicts(self, registry):
        """测试冲突检测"""
        resolver = LineageResolver(registry)
        
        # 添加一个相同fact_key的事实
        fact2 = FactRecord(
            fact_id="FCT-002",
            fact_key="VAR_TEST",  # 相同key
            domain="efficacy",
            value="90%"
        )
        registry.register_fact(fact2)
        
        conflicts = resolver.find_conflicts("FCT-001")
        
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "duplicate_key"
    
    def test_get_temporal_versions(self, registry):
        """测试时序版本"""
        resolver = LineageResolver(registry)
        
        # 添加同key的另一个版本
        fact2 = FactRecord(
            fact_id="FCT-002",
            fact_key="VAR_TEST",
            domain="efficacy",
            value="90%",
            lineage={"timestamps": ["2026-03-10T00:00:00"]}
        )
        registry.register_fact(fact2)
        
        versions = resolver.get_temporal_versions("VAR_TEST")
        
        assert len(versions) == 2