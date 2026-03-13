"""
编辑计划

define editorial planning output.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class EditorialPlan:
    """
    编辑计划 - 编辑层输出的写作方案
    
    Attributes:
        thesis: 核心论点
        outline: 文章大纲 (章节列表)
        play_id: 选定的写作策略ID
        arc_id: 选定的叙事弧线ID
        target_audience: 目标受众细分
        key_evidence: 核心证据列表
        style_notes: 风格注释
    """
    thesis: str
    outline: List[Dict[str, Any]] = field(default_factory=list)
    play_id: Optional[str] = None
    arc_id: Optional[str] = None
    target_audience: Optional[str] = None
    key_evidence: List[str] = field(default_factory=list)
    style_notes: Dict[str, Any] = field(default_factory=dict)
