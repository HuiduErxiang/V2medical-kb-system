"""
血缘追溯深化测试

测试 LineageResolver 类的高级功能，包括时间序列和版本对比。
"""
import pytest
from datetime import datetime
from engine.evidence import LineageResolver, EvidenceRegistry
from engine.evidence.models import SourceRecord, AssetRecord, EvidenceFragment, FactRecord
from engine.evidence.models import SourceType, AssetType, FragmentType, FactStatus


class TestLineageDeepening:
    """测试血缘追溯深化功能"""
    
    @pytest.fixture
    def registry(self):
        """创建包含测试数据的证据注册表"""
        registry = EvidenceRegistry()
        
        # 创建源记录
        source1 = SourceRecord(
            source_id="SRC-1",
            source_type=SourceType.PDF,
            source_key="SRC-1",
            title="Test Source 1",
            metadata={"promoted_at": "2023-01-01T00:00:00"}
        )
        source2 = SourceRecord(
            source_id="SRC-2",
            source_type=SourceType.PDF,
            source_key="SRC-2",
            title="Test Source 2",
            metadata={"promoted_at": "2023-02-01T00:00:00"}
        )
        registry.register_source(source1)
        registry.register_source(source2)
        
        # 创建资产记录
        asset1 = AssetRecord(
            asset_id="AST-1",
            source_id="SRC-1",
            asset_key="AST-1",
            asset_type=AssetType.DOCUMENT,
            metadata={"promoted_at": "2023-01-02T00:00:00"}
        )
        asset2 = AssetRecord(
            asset_id="AST-2",
            source_id="SRC-2",
            asset_key="AST-2",
            asset_type=AssetType.DOCUMENT,
            metadata={"promoted_at": "2023-02-02T00:00:00"}
        )
        registry.register_asset(asset1)
        registry.register_asset(asset2)
        
        # 创建证据片段
        fragment1 = EvidenceFragment(
            fragment_id="FRG-1",
            asset_id="AST-1",
            fragment_key="FRG-1",
            fragment_type=FragmentType.TEXT,
            content="Content from source 1",
            metadata={"promoted_at": "2023-01-03T00:00:00"}
        )
        fragment2 = EvidenceFragment(
            fragment_id="FRG-2",
            asset_id="AST-2",
            fragment_key="FRG-2",
            fragment_type=FragmentType.TEXT,
            content="Content from source 2",
            metadata={"promoted_at": "2023-02-03T00:00:00"}
        )
        registry.register_fragment(fragment1)
        registry.register_fragment(fragment2)
        
        # 创建事实记录（不同版本）
        fact1 = FactRecord(
            fact_id="FACT-1",
            fact_key="FACT-1",
            domain="efficacy",
            definition="Blood Pressure",
            definition_zh="血压",
            value="120/80 mmHg",
            unit="mmHg",
            content="Normal blood pressure is 120/80 mmHg",
            fragment_ids=["FRG-1"],
            status=FactStatus.ACTIVE,
            metadata={"promoted_at": "2023-01-04T00:00:00"}
        )
        fact2 = FactRecord(
            fact_id="FACT-2",
            fact_key="FACT-1",  # 相同的 fact_key，表示同一事实的不同版本
            domain="efficacy",
            definition="Blood Pressure",
            definition_zh="血压",
            value="130/85 mmHg",
            unit="mmHg",
            content="Updated blood pressure is 130/85 mmHg",
            fragment_ids=["FRG-2"],
            status=FactStatus.SUPERSEDED,
            metadata={"promoted_at": "2023-02-04T00:00:00"}
        )
        registry.register_fact(fact1)
        registry.register_fact(fact2)
        
        return registry
    
    @pytest.fixture
    def lineage_resolver(self, registry):
        """创建血缘解析器实例"""
        return LineageResolver(registry)
    
    def test_temporal_versions(self, lineage_resolver):
        """测试获取时间序列版本"""
        versions = lineage_resolver.get_temporal_versions("FACT-1")
        assert len(versions) == 2
        
        # 检查版本按时间排序
        assert versions[0]["fact_id"] == "FACT-1"
        assert versions[1]["fact_id"] == "FACT-2"
        
        # 检查版本信息
        assert versions[0]["status"] == "active"
        assert versions[1]["status"] == "superseded"
        
        assert "timestamps" in versions[0]
        assert "timestamps" in versions[1]
    
    def test_find_latest_version(self, lineage_resolver):
        """测试找到最新版本"""
        latest = lineage_resolver.find_latest_version("FACT-1")
        assert latest is not None
        
        assert latest["fact_id"] == "FACT-2"
        assert latest["status"] == "superseded"
    
    def test_compare_versions(self, lineage_resolver):
        """测试版本对比"""
        comparison = lineage_resolver.compare_versions("FACT-1", "FACT-2")
        assert comparison is not None
        
        assert comparison["fact_id1"] == "FACT-1"
        assert comparison["fact_id2"] == "FACT-2"
        
        assert comparison["domain"] == True  # 领域相同
        assert comparison["definition"] == True  # 定义相同
        assert comparison["value"] == False  # 值不同
        assert comparison["status"] == False  # 状态不同
        assert comparison["fragment_count"] == True  # 片段数量相同
    
    def test_get_temporal_sequence(self, lineage_resolver):
        """测试获取时间序列"""
        chain = lineage_resolver.resolve_lineage("FACT-1")
        sequence = chain.get_temporal_sequence()
        
        assert len(sequence) >= 1
        
        # 检查时间序列是否按时间排序
        timestamps = [node.timestamp for node in sequence]
        sorted_timestamps = sorted(timestamps)
        assert timestamps == sorted_timestamps
    
    def test_get_versions_list(self, lineage_resolver):
        """测试获取版本列表"""
        chain = lineage_resolver.resolve_lineage("FACT-1")
        versions = chain.get_versions()
        
        assert len(versions) == 1  # 只包含一个版本
    
    def test_conflict_detection(self, lineage_resolver):
        """测试冲突检测"""
        conflicts = lineage_resolver.find_conflicts("FACT-1")
        assert len(conflicts) == 1
        
        conflict = conflicts[0]
        assert conflict["type"] == "duplicate_key"
        assert conflict["fact_id_1"] == "FACT-1"
        assert conflict["fact_id_2"] == "FACT-2"
        assert conflict["fact_key"] == "FACT-1"
    
    def test_dependency_graph(self, lineage_resolver):
        """测试依赖图构建"""
        graph = lineage_resolver.build_dependency_graph(["FACT-1"])
        assert len(graph) == 1
        
        # FACT-1 依赖于 FACT-2，因为它们具有相同的 fact_key 但不同的 fact_id
        assert len(graph["FACT-1"]) == 1
        assert "FACT-2" in graph["FACT-1"]
    
    def test_resolve_lineage_batch(self, lineage_resolver):
        """测试批量解析血缘链"""
        chains = lineage_resolver.resolve_lineage_batch(["FACT-1", "FACT-2"])
        assert len(chains) == 2
        
        assert "FACT-1" in chains
        assert "FACT-2" in chains
        
        assert len(chains["FACT-1"].nodes) > 0
        assert len(chains["FACT-2"].nodes) > 0
    
    def test_chain_completeness(self, lineage_resolver):
        """测试血缘链完整性"""
        chain = lineage_resolver.resolve_lineage("FACT-1")
        
        assert len(chain.nodes) > 0
        assert len(chain.get_sources()) > 0
        assert len(chain.get_fragments()) > 0
        assert len(chain.get_assets()) > 0
        assert len(chain.get_fact_nodes()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
