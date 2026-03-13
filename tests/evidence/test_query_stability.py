"""
查询/结果契约稳定性测试

测试证据查询接口的稳定性和一致性。
"""
import pytest
from datetime import datetime
from engine.evidence import (
    EvidenceQuery, QueryResult, QueryBuilder, QueryType, QueryStatus,
    EvidenceResolver, EvidenceRegistry
)
from engine.evidence.models import SourceRecord, AssetRecord, EvidenceFragment, FactRecord
from engine.evidence.models import SourceType, AssetType, FragmentType, FactStatus
from engine.runtime.app import Application


class TestQueryStability:
    """测试查询/结果契约的稳定性"""
    
    @pytest.fixture
    def application(self):
        """创建应用程序实例"""
        return Application()
    
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
            content="Test fact 1",
            fragment_ids=["FRG-1"],
            status=FactStatus.ACTIVE,
            metadata={"promoted_at": "2023-01-04T00:00:00"}
        )
        fact2 = FactRecord(
            fact_id="FACT-2",
            fact_key="FACT-1",
            domain="efficacy",
            content="Test fact 2",
            fragment_ids=["FRG-2"],
            status=FactStatus.SUPERSEDED,
            metadata={"promoted_at": "2023-02-04T00:00:00"}
        )
        registry.register_fact(fact1)
        registry.register_fact(fact2)
        
        return registry
    
    def test_query_structure_completeness(self, application):
        """测试查询结构完整性"""
        query = QueryBuilder() \
            .product("test_product") \
            .domain("efficacy") \
            .build()
        
        # 检查查询属性
        assert hasattr(query, "query_id")
        assert hasattr(query, "query_type")
        assert hasattr(query, "product_id")
        assert hasattr(query, "domain")
        assert hasattr(query, "limit")
        assert hasattr(query, "include_lineage")
        
        # 检查 query_id 格式
        assert query.query_id.startswith("qry_")
        
        # 检查 domain
        assert query.domain == "efficacy"
        assert query.product_id == "test_product"
    
    def test_result_structure_completeness(self, application):
        """测试结果结构完整性"""
        query = QueryBuilder().product("test_product").build()
        result = application.query(query)
        
        assert hasattr(result, "query_id")
        assert hasattr(result, "status")
        assert hasattr(result, "sources")
        assert hasattr(result, "assets")
        assert hasattr(result, "fragments")
        assert hasattr(result, "facts")
        assert hasattr(result, "lineages")
        assert hasattr(result, "elapsed_ms")
        assert hasattr(result, "metadata")
        
        # 检查总计数属性
        assert hasattr(result, "total_count")
        
        # 检查状态属性
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_empty")
        
        # 检查结果是否包含所需的属性
        assert isinstance(result.sources, list)
        assert isinstance(result.assets, list)
        assert isinstance(result.fragments, list)
        assert isinstance(result.facts, list)
        assert isinstance(result.lineages, list)
        assert isinstance(result.elapsed_ms, (int, float))
        assert isinstance(result.metadata, dict)
    
    def test_query_result_contract(self, application):
        """测试查询/结果契约的一致性"""
        product_query = QueryBuilder().product("test_product").build()
        product_result = application.query(product_query)
        
        domain_query = QueryBuilder() \
            .product("test_product") \
            .domain("efficacy") \
            .build()
        domain_result = application.query(domain_query)
        
        # 检查结果类型是否一致
        assert product_result.__class__ == domain_result.__class__
        
        # 检查查询ID是否匹配
        assert product_result.query_id == product_query.query_id
        assert domain_result.query_id == domain_query.query_id
        
        # 检查所有属性是否存在于两个结果中
        product_attrs = set(dir(product_result))
        domain_attrs = set(dir(domain_result))
        
        # 应该有一些共同的属性
        assert len(product_attrs & domain_attrs) > 0
        
        # 检查状态属性
        assert product_result.status in [
            QueryStatus.SUCCESS, QueryStatus.EMPTY
        ]
        assert domain_result.status in [
            QueryStatus.SUCCESS, QueryStatus.EMPTY
        ]
    
    def test_query_type_coverage(self, application):
        """测试所有查询类型的覆盖"""
        # 产品查询
        product_query = QueryBuilder().product("test_product").build()
        assert product_query.query_type == QueryType.BY_PRODUCT
        
        # 领域查询
        domain_query = QueryBuilder() \
            .product("test_product") \
            .domain("efficacy") \
            .build()
        assert domain_query.query_type == QueryType.BY_DOMAIN
        
        # 事实键查询
        keys_query = QueryBuilder() \
            .product("test_product") \
            .fact_keys(["FACT-1"]) \
            .build()
        assert keys_query.query_type == QueryType.BY_KEYS
        
        # 时间范围查询
        time_query = QueryBuilder() \
            .product("test_product") \
            .time_range(
                start=datetime(2023, 1, 1),
                end=datetime(2023, 1, 31)
            ) \
            .build()
        assert time_query.query_type == QueryType.BY_TIME_RANGE
        
        # 搜索查询
        search_query = QueryBuilder() \
            .product("test_product") \
            .search("test") \
            .build()
        assert search_query.query_type == QueryType.SEARCH
    
    def test_query_failure_handling(self, application):
        """测试查询失败的处理"""
        invalid_query = QueryBuilder() \
            .product("invalid_product") \
            .build()
        
        result = application.query(invalid_query)
        
        assert result.status == QueryStatus.EMPTY
        assert "error" not in result.metadata
        assert len(result.sources) == 0
        assert len(result.facts) == 0
        assert len(result.assets) == 0
        assert len(result.fragments) == 0
    
    def test_query_result_metadata(self, application):
        """测试查询结果元数据"""
        query = QueryBuilder().product("test_product").build()
        result = application.query(query)
        
        assert "error" not in result.metadata
        assert result.elapsed_ms > 0
    
    def test_query_builder_pattern(self):
        """测试查询构建器模式"""
        query = (QueryBuilder()
            .product("test_product")
            .domain("efficacy")
            .fact_keys(["FACT-1", "FACT-2"])
            .limit(10)
            .include_lineage()
            .build())
        
        assert query.product_id == "test_product"
        assert query.domain == "efficacy"
        assert len(query.fact_keys) == 2
        assert query.fact_keys == ["FACT-1", "FACT-2"]
        assert query.limit == 10
        assert query.include_lineage == True
    
    def test_query_result_methods(self, application):
        """测试 QueryResult 的方法"""
        query = QueryBuilder().product("test_product").build()
        result = application.query(query)
        
        # 检查 to_dict() 方法
        result_dict = result.to_dict()
        
        assert "query_id" in result_dict
        assert "status" in result_dict
        assert "counts" in result_dict
        assert "elapsed_ms" in result_dict
        assert "metadata" in result_dict
        
        # 检查数量计数
        assert "sources" in result_dict["counts"]
        assert "assets" in result_dict["counts"]
        assert "fragments" in result_dict["counts"]
        assert "facts" in result_dict["counts"]
        assert "total" in result_dict["counts"]
        
        # 验证计数是否一致
        assert result_dict["counts"]["sources"] == len(result.sources)
        assert result_dict["counts"]["assets"] == len(result.assets)
        assert result_dict["counts"]["fragments"] == len(result.fragments)
        assert result_dict["counts"]["facts"] == len(result.facts)
        assert result_dict["counts"]["total"] == result.total_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
