"""
Prompt编译器

将编辑计划编译为可执行的prompt。

Phase 2 增强：
- 支持从 fact_records 构建更详细的证据上下文
- 支持 domain 分组信息
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..contracts import EditorialPlan, EvidenceSelection, CompiledPrompt


@dataclass
class PromptCompiler:
    """
    Prompt编译器
    
    将编辑计划编译为LLM可用的prompt。
    只负责编译，不负责路由和择证。
    
    Phase 2 增强：
    - 支持从 fact_records 构建详细证据上下文
    - 支持 domain 分组
    """
    
    base_system_prompt: str = field(default="你是一个医学写作助手。")
    
    def compile(self, plan: EditorialPlan) -> CompiledPrompt:
        """
        编译prompt
        
        Args:
            plan: 编辑计划
            
        Returns:
            CompiledPrompt: 编译后的prompt
        """
        system_prompt = self._build_system_prompt(plan)
        user_prompt = self._build_user_prompt(plan)
        
        return CompiledPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_config=self._build_model_config(plan),
            metadata={
                "play_id": plan.play_id,
                "arc_id": plan.arc_id,
                "thesis": plan.thesis
            }
        )
    
    def compile_with_evidence(
        self, 
        plan: EditorialPlan, 
        evidence: EvidenceSelection
    ) -> CompiledPrompt:
        """
        编译带详细证据信息的 prompt
        
        Phase 2 新增：支持从 fact_records 获取详细信息
        
        Args:
            plan: 编辑计划
            evidence: 证据选择
            
        Returns:
            CompiledPrompt
        """
        system_prompt = self._build_system_prompt(plan)
        user_prompt = self._build_user_prompt_with_evidence(plan, evidence)
        
        return CompiledPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_config=self._build_model_config(plan),
            metadata={
                "play_id": plan.play_id,
                "arc_id": plan.arc_id,
                "thesis": plan.thesis,
                "fact_count": len(evidence.fact_records)
            }
        )
    
    def _build_system_prompt(self, plan: EditorialPlan) -> str:
        """构建系统prompt"""
        lines = [
            self.base_system_prompt,
            "",
            f"写作策略: {plan.play_id}",
            f"叙事弧线: {plan.arc_id}",
            f"目标受众: {plan.target_audience or '未指定'}",
        ]
        
        if plan.style_notes:
            lines.extend([
                "",
                "风格要求:",
                f"- 语体等级: {plan.style_notes.get('register', '未指定')}",
                f"- 正式程度: {plan.style_notes.get('formality', '未指定')}",
            ])
        
        return "\n".join(lines)
    
    def _build_user_prompt(self, plan: EditorialPlan) -> str:
        """构建用户prompt"""
        lines = [
            f"主题: {plan.thesis}",
            "",
            "大纲:",
        ]
        
        for i, section in enumerate(plan.outline, 1):
            title = section['title']
            # Phase 2: 包含 domain 信息
            if section.get('type') == 'domain_section':
                title = f"{section['title']} ({section.get('fact_count', 0)}条证据)"
            lines.append(f"{i}. {title}")
        
        if plan.key_evidence:
            lines.extend([
                "",
                "核心证据:",
            ])
            for evidence in plan.key_evidence:
                lines.append(f"- {evidence}")
        
        lines.extend([
            "",
            "请根据以上信息生成文章。"
        ])
        
        return "\n".join(lines)
    
    def _build_user_prompt_with_evidence(
        self, 
        plan: EditorialPlan, 
        evidence: EvidenceSelection
    ) -> str:
        """
        构建包含详细证据的用户prompt
        
        Phase 2 新增
        """
        lines = [
            f"主题: {plan.thesis}",
            "",
            "大纲:",
        ]
        
        for i, section in enumerate(plan.outline, 1):
            lines.append(f"{i}. {section['title']}")
        
        # Phase 2: 使用 fact_records 构建详细证据
        if evidence.fact_records:
            lines.extend([
                "",
                "证据详情:",
                ""
            ])
            
            # 按 domain 分组
            by_domain: Dict[str, List[Any]] = {}
            for fact in evidence.fact_records:
                if fact.domain not in by_domain:
                    by_domain[fact.domain] = []
                by_domain[fact.domain].append(fact)
            
            for domain, facts in by_domain.items():
                lines.append(f"【{domain}】")
                for fact in facts[:3]:  # 每个 domain 最多3条
                    value_str = f"{fact.value} {fact.unit or ''}".strip()
                    lines.append(f"- {fact.definition or fact.definition_zh or fact.fact_key}: {value_str}")
                lines.append("")
        
        lines.extend([
            "请根据以上信息生成文章。"
        ])
        
        return "\n".join(lines)
    
    def _build_model_config(self, plan: EditorialPlan) -> Dict[str, Any]:
        """构建模型配置"""
        base_config = {
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        if plan.style_notes:
            register = plan.style_notes.get('register', '')
            if register in ['R1', 'R2']:
                base_config['temperature'] = 0.5
            elif register in ['R4', 'R5']:
                base_config['temperature'] = 0.8
        
        return base_config