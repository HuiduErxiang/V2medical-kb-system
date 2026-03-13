"""
模块导入关系测试

验证所有模块可正确导入。
"""


class TestContractsImport:
    """测试contracts包导入"""
    
    def test_import_all_contracts(self):
        """导入所有契约对象"""
        from engine.contracts import (
            RouteContext,
            EvidenceSelection,
            EditorialPlan,
            CompiledPrompt,
            QualityResult,
            DeliveryResult
        )
        assert True  # 如果导入失败会抛出ImportError
    
    def test_import_gate_status(self):
        """导入GateStatus枚举"""
        from engine.contracts import GateStatus
        assert GateStatus.PASSED is not None


class TestEvidenceImport:
    """测试evidence包导入"""
    
    def test_import_four_layer_objects(self):
        """导入四层证据对象"""
        from engine.evidence import (
            SourceRecord,
            AssetRecord,
            EvidenceFragment,
            FactRecord
        )
        assert True
    
    def test_import_enums(self):
        """导入枚举类型"""
        from engine.evidence import (
            SourceType,
            AssetType,
            FragmentType,
            FactStatus
        )
        assert SourceType.PDF is not None
    
    def test_import_resolver_classes(self):
        """导入解析器类"""
        from engine.evidence import (
            EvidenceResolver,
            EvidenceRegistry,
            LegacyResolver
        )
        assert True


class TestQualityImport:
    """测试quality包导入"""
    
    def test_import_orchestrator(self):
        """导入QualityOrchestrator"""
        from engine.quality import QualityOrchestrator
        assert True


class TestDeliveryImport:
    """测试delivery包导入"""
    
    def test_import_writers(self):
        """导入writer类"""
        from engine.delivery import MarkdownWriter, TaskLogger
        assert True


class TestEditorialImport:
    """测试editorial包导入"""
    
    def test_import_planner(self):
        """导入EditorialPlanner"""
        from engine.editorial import EditorialPlanner
        assert True


class TestPromptImport:
    """测试prompt包导入"""
    
    def test_import_compiler(self):
        """导入PromptCompiler"""
        from engine.prompt import PromptCompiler
        assert True


class TestRuntimeImport:
    """测试runtime包导入"""
    
    def test_import_application(self):
        """导入Application"""
        from engine.runtime import Application
        assert True
    
    def test_import_helpers(self):
        """导入辅助函数"""
        from engine.runtime import extract_runtime_params, validate_context
        assert True
