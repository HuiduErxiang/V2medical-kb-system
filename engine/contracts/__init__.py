"""
V2 中间契约对象包

定义主链中各阶段传递的标准数据契约。
"""

from .route_context import RouteContext
from .evidence_selection import EvidenceSelection
from .editorial_plan import EditorialPlan
from .compiled_prompt import CompiledPrompt
from .quality_result import QualityResult, GateStatus
from .delivery_result import DeliveryResult

__all__ = [
    "RouteContext",
    "EvidenceSelection",
    "EditorialPlan",
    "CompiledPrompt",
    "QualityResult",
    "GateStatus",
    "DeliveryResult",
]
