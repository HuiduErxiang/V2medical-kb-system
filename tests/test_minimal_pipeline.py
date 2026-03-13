"""
最小主链串联测试

验证Application.run()可完整运行主链。
"""
import pytest
from pathlib import Path

from engine.runtime import Application
from engine.contracts import RouteContext


class TestMinimalPipeline:
    """测试最小主链"""
    
    @pytest.fixture
    def app(self):
        """创建应用实例，使用默认的LegacyResolver"""
        # LegacyResolver默认路径已配置为正确的绝对路径，无需显式指定
        return Application()
    
    def test_application_creation(self, app):
        """测试Application创建"""
        assert app is not None
        assert app.evidence_resolver is not None
        assert app.planner is not None
        assert app.compiler is not None
        assert app.quality is not None
        assert app.writer is not None
        assert app.logger is not None
    
    def test_run_with_mock_data(self, tmp_path, monkeypatch):
        """测试使用mock数据运行主链"""
        # 创建mock resolver避免依赖V1
        from engine.evidence import EvidenceResolver
        from engine.evidence.models import (
            SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
            SourceType, AssetType, FragmentType, FactStatus
        )
        
        class MockResolver(EvidenceResolver):
            """Mock resolver for testing"""
            
            def resolve_sources(self, query):
                return [SourceRecord(
                    source_id="SRC_TEST",
                    source_type=SourceType.PDF,
                    source_key="SRC-TEST",
                    citation="Test Citation"
                )]
            
            def resolve_assets(self, source_ids):
                return [AssetRecord(
                    asset_id="AST_TEST",
                    source_id="SRC_TEST",
                    asset_key="AST-TEST",
                    asset_type=AssetType.DOCUMENT
                )]
            
            def resolve_fragments(self, asset_ids):
                return [EvidenceFragment(
                    fragment_id="FRG_TEST",
                    asset_id="AST_TEST",
                    fragment_key="FRG-TEST",
                    fragment_type=FragmentType.TEXT,
                    content="Test content"
                )]
            
            def resolve_facts(self, query):
                return [FactRecord(
                    fact_id="FCT_TEST",
                    fact_key="VAR_TEST",
                    domain="efficacy",
                    value="95%",
                    unit="percent",
                    fragment_ids=["FRG_TEST"]
                )]
        
        # 修改输出目录到临时目录
        from engine.delivery import MarkdownWriter, TaskLogger
        
        mock_app = Application(evidence_resolver=MockResolver())
        mock_app.writer.output_dir = tmp_path / "output"
        mock_app.logger.log_dir = tmp_path / "logs"
        
        # 创建上下文
        context = RouteContext(
            product_id="test_product",
            register="R3",
            audience="医生"
        )
        
        # 运行主链
        result = mock_app.run(context)
        
        # 验证结果
        assert result is not None
        assert result.output_path is not None
        assert result.output_path.exists()  # Markdown文件应已生成
        assert result.summary["status"] == "success"
        assert result.summary["product_id"] == "test_product"
        assert result.summary["register"] == "R3"
    
    def test_run_with_v1_data(self, app, tmp_path, monkeypatch):
        """测试使用V1数据运行主链（如果V1存在）"""
        # 修改输出目录
        app.writer.output_dir = tmp_path / "output"
        app.logger.log_dir = tmp_path / "logs"
        
        context = RouteContext(
            product_id="lecanemab",
            register="R3",
            audience="医生"
        )
        
        try:
            result = app.run(context)
            
            # 验证结果
            assert result is not None
            if result.summary.get("status") == "success":
                assert result.output_path is not None
                # 验证生成的文件
                content = result.output_path.read_text(encoding='utf-8')
                # Phase 2: thesis 现在包含 domain 信息
                assert "关于lecanemab" in content

                
        except FileNotFoundError:
            pytest.skip("V1 evidence database not found")
    
    def test_quality_gate_failure(self, tmp_path):
        """测试质量门禁场景"""
        # 创建mock resolver
        from engine.evidence import EvidenceResolver
        from engine.evidence.models import FactRecord
        
        class SimpleResolver(EvidenceResolver):
            def resolve_facts(self, query):
                return [FactRecord(
                    fact_id="FCT_TEST",
                    fact_key="VAR_TEST",
                    domain="efficacy",
                    value="test"
                )]
            def resolve_sources(self, query): return []
            def resolve_assets(self, source_ids): return []
            def resolve_fragments(self, asset_ids): return []
        
        mock_app = Application(evidence_resolver=SimpleResolver())
        mock_app.writer.output_dir = tmp_path / "output"
        mock_app.logger.log_dir = tmp_path / "logs"
        
        context = RouteContext(
            product_id="test",
            register="R3"
        )
        
        result = mock_app.run(context)
        
        # 验证run()能正常返回DeliveryResult
        assert result is not None
        assert result.summary is not None