"""
契约对象测试

验证6个契约对象可正确实例化。
"""
import pytest
from datetime import datetime

from engine.contracts import (
    RouteContext,
    EvidenceSelection,
    EditorialPlan,
    CompiledPrompt,
    QualityResult,
    DeliveryResult,
    GateStatus
)


class TestRouteContext:
    """测试RouteContext"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        ctx = RouteContext(
            product_id="test_product",
            register="R3",
            audience="医生"
        )
        
        assert ctx.product_id == "test_product"
        assert ctx.register == "R3"
        assert ctx.audience == "医生"
        assert ctx.task_id.startswith("task_")
        assert isinstance(ctx.created_at, datetime)
    
    def test_register_validation(self):
        """register值验证测试"""
        with pytest.raises(ValueError):
            RouteContext(
                product_id="test",
                register="invalid"  # 无效值
            )


class TestEvidenceSelection:
    """测试EvidenceSelection"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        selection = EvidenceSelection()
        assert selection.selected_facts == []
        assert selection.source_refs == {}
    
    def test_add_fact(self):
        """添加事实测试"""
        selection = EvidenceSelection()
        selection.add_fact("VAR_001", ["SRC_01"])
        
        assert "VAR_001" in selection.selected_facts
        assert selection.source_refs["VAR_001"] == ["SRC_01"]


class TestEditorialPlan:
    """测试EditorialPlan"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        plan = EditorialPlan(
            thesis="测试论点",
            outline=[{"title": "章节1"}],
            play_id="test_play"
        )
        
        assert plan.thesis == "测试论点"
        assert len(plan.outline) == 1
        assert plan.play_id == "test_play"


class TestCompiledPrompt:
    """测试CompiledPrompt"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        prompt = CompiledPrompt(
            system_prompt="系统指令",
            user_prompt="用户指令"
        )
        
        assert prompt.system_prompt == "系统指令"
        assert prompt.user_prompt == "用户指令"
    
    def test_to_messages(self):
        """转换为messages格式测试"""
        prompt = CompiledPrompt(
            system_prompt="系统",
            user_prompt="用户"
        )
        
        messages = prompt.to_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


class TestQualityResult:
    """测试QualityResult"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        result = QualityResult()
        
        assert result.overall_status == GateStatus.PASSED
        assert result.is_passed is True
    
    def test_add_warning(self):
        """添加警告测试"""
        result = QualityResult()
        result.add_warning("test_gate", "警告信息")
        
        assert result.overall_status == GateStatus.WARNING
        assert len(result.warnings) == 1
        assert result.is_passed is True  # warning也算通过
    
    def test_add_error(self):
        """添加错误测试"""
        result = QualityResult()
        result.add_error("test_gate", "错误信息")
        
        assert result.overall_status == GateStatus.FAILED
        assert len(result.errors) == 1
        assert result.is_passed is False


class TestDeliveryResult:
    """测试DeliveryResult"""
    
    def test_basic_creation(self):
        """基本创建测试"""
        result = DeliveryResult()
        
        assert result.output_path is None
        assert result.artifacts == []
        assert isinstance(result.completed_at, datetime)
    
    def test_add_artifact(self):
        """添加产物测试"""
        from pathlib import Path
        result = DeliveryResult()
        result.add_artifact(Path("test.md"))
        
        assert len(result.artifacts) == 1
