"""
质量检查结果

define quality gate output.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class GateStatus(Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass
class QualityResult:
    """
    质量检查结果 - 质控层的门禁输出
    
    Attributes:
        overall_status: 总体状态 (passed/warning/failed)
        gates_passed: 通过的门禁列表
        warnings: 警告列表
        errors: 错误列表
        metadata: 检查过程的元数据
    """
    overall_status: GateStatus = GateStatus.PASSED
    gates_passed: List[str] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_passed(self) -> bool:
        """检查是否通过所有门禁"""
        return self.overall_status in [GateStatus.PASSED, GateStatus.WARNING]
    
    def add_warning(self, gate: str, message: str):
        """添加警告"""
        self.warnings.append({"gate": gate, "message": message})
        if self.overall_status == GateStatus.PASSED:
            self.overall_status = GateStatus.WARNING
    
    def add_error(self, gate: str, message: str):
        """添加错误"""
        self.errors.append({"gate": gate, "message": message})
        self.overall_status = GateStatus.FAILED
