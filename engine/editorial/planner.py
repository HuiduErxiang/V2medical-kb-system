"""
编辑计划器

根据证据选择生成编辑计划。

Phase 2 增强：
- 支持从 fact_records 获取更丰富的证据信息
- 支持按 domain 组织大纲
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..contracts import RouteContext, EvidenceSelection, EditorialPlan


@dataclass
class EditorialPlanner:
    """
    编辑计划器
    
    基于证据选择和路由上下文生成编辑计划。
    
    Phase 2 增强：
    - 支持从 fact_records 构建更丰富的大纲
    - 支持按 domain 分组
    """
    
    config: Dict[str, Any] = field(default_factory=dict)
    
    def plan(self, context: RouteContext, evidence: EvidenceSelection) -> EditorialPlan:
        """
        生成编辑计划
        
        Args:
            context: 路由上下文
            evidence: 证据选择结果
            
        Returns:
            EditorialPlan: 编辑计划
        """
        thesis = self._build_thesis(context, evidence)
        outline = self._build_outline(context, evidence)
        play_id = self._select_play(context, evidence)
        arc_id = self._select_arc(context, evidence)
        
        return EditorialPlan(
            thesis=thesis,
            outline=outline,
            play_id=play_id,
            arc_id=arc_id,
            target_audience=context.audience,
            key_evidence=evidence.selected_facts[:5],
            style_notes=self._build_style_notes(context)
        )
    
    def _build_thesis(self, context: RouteContext, evidence: EvidenceSelection) -> str:
        """构建核心论点"""
        # Phase 2 增强：从 fact_records 提取更有意义的论点
        if evidence.fact_records:
            domains = set(f.domain for f in evidence.fact_records)
            if domains:
                domain_str = "、".join(list(domains)[:2])
                return f"关于{context.product_id}的{domain_str}分析"
        
        return f"关于{context.product_id}的医学写作"
    
    def _build_outline(self, context: RouteContext, evidence: EvidenceSelection) -> List[Dict[str, Any]]:
        """
        构建文章大纲
        
        Phase 2 增强：按 domain 组织大纲
        """
        outline = [
            {"title": "引言", "type": "intro"},
        ]
        
        # Phase 2: 使用 fact_records 获取 domain 信息
        if evidence.fact_records:
            # 按 domain 分组
            by_domain: Dict[str, List[Any]] = {}
            for fact in evidence.fact_records:
                if fact.domain not in by_domain:
                    by_domain[fact.domain] = []
                by_domain[fact.domain].append(fact)
            
            # 为每个 domain 创建章节
            for domain, facts in by_domain.items():
                outline.append({
                    "title": self._domain_to_title(domain),
                    "type": "domain_section",
                    "domain": domain,
                    "fact_count": len(facts)
                })
        else:
            # 降级：使用 selected_facts
            for fact_id in evidence.selected_facts[:3]:
                outline.append({
                    "title": f"章节: {fact_id}",
                    "type": "evidence",
                    "fact_id": fact_id
                })
        
        outline.append({"title": "结论", "type": "conclusion"})
        
        return outline
    
    def _domain_to_title(self, domain: str) -> str:
        """将 domain 转换为中文标题"""
        domain_titles = {
            "efficacy": "疗效分析",
            "safety": "安全性评估",
            "biomarker": "生物标志物",
            "moa": "作用机制",
            "trial_design": "试验设计",
            "competitor": "竞品对比"
        }
        return domain_titles.get(domain, domain.title())
    
    def _select_play(self, context: RouteContext, evidence: EvidenceSelection) -> str:
        """选择写作策略"""
        play_map = {
            "R1": "academic",
            "R2": "professional",
            "R3": "clinical",
            "R4": "patient",
            "R5": "casual"
        }
        return play_map.get(context.register, "standard")
    
    def _select_arc(self, context: RouteContext, evidence: EvidenceSelection) -> str:
        """选择叙事弧线"""
        # Phase 2: 基于 evidence 数量选择弧线
        if len(evidence.fact_records) > 5:
            return "evidence_rich"
        return "evidence_driven"
    
    def _build_style_notes(self, context: RouteContext) -> Dict[str, Any]:
        """构建风格注释"""
        return {
            "register": context.register,
            "formality": self._register_to_formality(context.register)
        }
    
    def _register_to_formality(self, register: str) -> str:
        """语体等级转正式程度"""
        mapping = {
            "R1": "highly_formal",
            "R2": "formal",
            "R3": "semi_formal",
            "R4": "informal",
            "R5": "casual"
        }
        return mapping.get(register, "neutral")