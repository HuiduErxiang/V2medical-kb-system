"""
主链集成测试
"""
import pytest
from pathlib import Path

from engine.runtime import Application
from engine.contracts import RouteContext
from engine.evidence import (
    EvidenceQuery, QueryBuilder, QueryType, QueryStatus
)
from engine.evidence.models import (
    SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
    SourceType, AssetType, FragmentType, FactStatus
)


class MockResolver:
    """Mock resolver for testing"""
    
    def resolve_sources(self, query):
        return [SourceRecord(
            source_id="SRC_MOCK",
            source_type=SourceType.PDF,
            source_key="SRC-MOCK",
            citation="Mock Citation"
        )]
    
    def resolve_assets(self, source_ids):
        return [AssetRecord(
            asset_id="AST_MOCK",
            source_id="SRC_MOCK",
            asset_key="AST-MOCK",
            asset_type=AssetType.DOCUMENT
        )]
    
    def resolve_fragments(self, asset_ids):
        return [EvidenceFragment(
            fragment_id="FRG_MOCK",
            asset_id="AST_MOCK",
            fragment_key="FRG-MOCK",
            fragment_type=FragmentType.TEXT,
            content="Mock content"
        )]
    
    def resolve_facts(self, query):
        return [FactRecord(
            fact_id="FCT_MOCK",
            fact_key="VAR_MOCK",
            domain="efficacy",
            value="Mock Value",
            fragment_ids=["FRG_MOCK"],
            lineage={"timestamps": ["2026-03-09T00:00:00"]}
        )]
    
    # Phase 2 扩展方法
    def resolve_by_domain(self, product_id, domain):
        return [FactRecord(
            fact_id="FCT_MOCK_2",
            fact_key="VAR_MOCK_2",
            domain=domain,
            value="Mock Value 2"
        )]
    
    def resolve_by_fact_keys(self, product_id, fact_keys):
        return []
    
    def resolve_by_time_range(self, product_id, start_time, end_time):
        return []
    
    def resolve_conflicts(self, product_id):
        return {}
    
    def search_facts(self, product_id, keyword):
        return []


class TestApplicationQuery:
    """测试Application的query方法"""
    
    @pytest.fixture
    def app(self):
        return Application(evidence_resolver=MockResolver())
    
    def test_query_by_product(self, app):
        """测试按产品查询"""
        query = EvidenceQuery.for_product("test_product")
        result = app.query(query)
        
        assert result.status == QueryStatus.SUCCESS
        assert len(result.facts) > 0
        assert len(result.sources) > 0
    
    def test_query_by_domain(self, app):
        """测试按领域查询"""
        query = EvidenceQuery.for_domain("test_product", "efficacy")
        result = app.query(query)
        
        assert result.status == QueryStatus.SUCCESS
    
    def test_query_with_lineage(self, app):
        """测试带血缘查询"""
        query = (QueryBuilder()
            .product("test_product")
            .include_lineage()
            .build())
        
        result = app.query(query)
        
        assert len(result.lineages) > 0
        assert "fact_id" in result.lineages[0]
    
    def test_query_result_has_timing(self, app):
        """测试结果有耗时"""
        query = EvidenceQuery.for_product("test_product")
        result = app.query(query)
        
        assert result.elapsed_ms > 0


class TestApplicationBuilder:
    """测试QueryBuilder"""
    
    def test_builder_product(self):
        """测试builder设置产品"""
        query = (QueryBuilder()
            .product("test_product")
            .build())
        
        assert query.product_id == "test_product"
    
    def test_builder_domain(self):
        """测试builder设置领域"""
        query = (QueryBuilder()
            .product("test_product")
            .domain("efficacy")
            .build())
        
        assert query.domain == "efficacy"
        assert query.query_type == QueryType.BY_DOMAIN
    
    def test_builder_limit(self):
        """测试builder设置限制"""
        query = (QueryBuilder()
            .product("test_product")
            .limit(50)
            .build())
        
        assert query.limit == 50
    
    def test_builder_requires_product(self):
        """测试builder必须设置产品"""
        builder = QueryBuilder()
        
        with pytest.raises(ValueError):
            builder.build()


class TestRuntimeIntegration:
    """测试runtime集成"""
    
    @pytest.fixture
    def app(self):
        return Application(evidence_resolver=MockResolver())
    
    def test_run_creates_output(self, app, tmp_path):
        """测试运行创建输出"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.log_dir = tmp_path / "logs"
        
        context = RouteContext(
            product_id="test_product",
            register="R3",
            audience="医生"
        )
        
        result = app.run(context)
        
        assert result.output_path is not None
        assert result.output_path.exists()
    
    def test_run_with_query(self, app, tmp_path):
        """测试使用query运行"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.log_dir = tmp_path / "logs"
        
        context = RouteContext(
            product_id="test_product",
            register="R3"
        )
        
        result = app.run(context)
        
        assert result.summary["status"] == "success"


class TestDeliveryResultLogPaths:
    """测试交付结果日志路径回填"""
    
    @pytest.fixture
    def app(self):
        return Application(evidence_resolver=MockResolver())
    
    def test_result_has_log_paths(self, app, tmp_path):
        """测试交付结果包含日志路径"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.repo_root = tmp_path
        
        context = RouteContext(
            product_id="test_product",
            register="R3",
            project_name="测试项目",
            deliverable_type="article"
        )
        
        result = app.run(context)
        
        # 验证日志路径列表不为空
        assert len(result.task_log_paths) > 0
        
        # 验证所有日志路径都存在
        for log_path in result.task_log_paths:
            assert log_path.exists()
    
    def test_result_has_primary_log_path(self, app, tmp_path):
        """测试交付结果包含主日志路径"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.repo_root = tmp_path
        
        context = RouteContext(
            product_id="test_product",
            register="R3",
            project_name="测试项目"
        )
        
        result = app.run(context)
        
        # 验证主日志路径已设置
        assert result.task_log_path is not None
        assert result.task_log_path.exists()
    
    def test_project_task_has_double_logs(self, app, tmp_path):
        """测试项目任务有双层日志"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.repo_root = tmp_path
        
        context = RouteContext(
            product_id="test_product",
            register="R3",
            project_name="测试项目",
            task_category="project"
        )
        
        result = app.run(context)
        
        # 项目任务应该有2个日志文件
        assert len(result.task_log_paths) == 2
    
    def test_system_task_has_single_log(self, app, tmp_path):
        """测试系统任务只有单层日志"""
        app.writer.output_dir = tmp_path / "output"
        app.logger.repo_root = tmp_path
        
        context = RouteContext(
            product_id="system",
            register="R1",
            task_category="system"
        )
        
        result = app.run(context)
        
        # 系统任务只有1个日志文件
        assert len(result.task_log_paths) == 1
        
        # 验证是主系统日志
        root_log_dir = tmp_path / "写作项目运行日志"
        assert result.task_log_path.parent == root_log_dir