"""
质量编排器

协调门禁和语义审查。
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..contracts import CompiledPrompt, QualityResult, GateStatus


# 关键gate列表：失败时阻断流程
CRITICAL_GATES = {"basic"}


@dataclass
class QualityOrchestrator:
    """
    质量编排器
    
    负责协调多个质量门禁的运行。
    首轮最小实现，预留workflow_gate和semantic_review接口。
    """
    
    enabled_gates: List[str] = field(default_factory=lambda: ["basic", "schema"])
    config: Dict[str, Any] = field(default_factory=dict)
    
    def run_gates(self, prompt: CompiledPrompt) -> QualityResult:
        """
        运行所有启用的门禁
        
        Args:
            prompt: 编译后的prompt
            
        Returns:
            QualityResult: 门禁检查结果
        """
        result = QualityResult()
        
        for gate in self.enabled_gates:
            try:
                gate_result = self._run_single_gate(gate, prompt)
                if gate_result:
                    result.gates_passed.append(gate)
                else:
                    # 区分关键gate和非关键gate
                    if gate in CRITICAL_GATES:
                        # 关键gate失败：添加错误，阻断流程
                        result.add_error(gate, f"{gate} gate failed - critical check failed")
                    else:
                        # 非关键gate失败：只添加警告
                        result.add_warning(gate, f"{gate} gate returned warnings")
            except Exception as e:
                result.add_error(gate, str(e))
        
        return result
    
    def _run_single_gate(self, gate_name: str, prompt: CompiledPrompt) -> bool:
        """运行单个门禁"""
        if gate_name == "basic":
            # 基础检查：prompt非空 - 关键gate
            if not prompt.system_prompt:
                return False
            if not prompt.user_prompt:
                return False
            return True
        elif gate_name == "schema":
            # schema检查：配置存在 - 非关键gate
            return bool(self.config)
        return True
    
    def semantic_review(self, content: str) -> Dict[str, Any]:
        """
        语义审查 - 预留接口
        
        Args:
            content: 待审查内容
            
        Returns:
            审查结果
        """
        return {
            "issues": [],
            "suggestions": [],
            "passed": True
        }