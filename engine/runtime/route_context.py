"""
路由上下文处理

辅助函数：从RouteContext提取运行参数
"""
from typing import Dict, Any, Optional, Tuple

from ..contracts import RouteContext


def extract_runtime_params(context: RouteContext) -> Dict[str, Any]:
    """
    从RouteContext提取运行时参数
    
    Args:
        context: 路由上下文
        
    Returns:
        运行时参数字典
    """
    return {
        "product_id": context.product_id,
        "register": context.register,
        "audience": context.audience,
        "task_id": context.task_id,
        **context.metadata
    }


def validate_context(context: RouteContext) -> Tuple[bool, Optional[str]]:
    """
    验证RouteContext的有效性
    
    Args:
        context: 路由上下文
        
    Returns:
        (是否有效, 错误信息)
    """
    if not context.product_id:
        return False, "product_id不能为空"
    
    valid_registers = ['R1', 'R2', 'R3', 'R4', 'R5']
    if context.register not in valid_registers:
        return False, f"register必须是 {valid_registers} 之一"
    
    return True, None
