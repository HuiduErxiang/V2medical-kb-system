"""
路由上下文

定义任务启动时的路由参数和运行配置。
这是主链的入口契约。
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class RouteContext:
    """
    路由上下文 - 任务启动参数
    
    Attributes:
        product_id: 产品标识符 (如 'lecanemab', 'furmonertinib')
        register: 语体等级 (R1-R5)
        audience: 目标受众描述
        task_id: 任务唯一标识 (自动生成)
        created_at: 任务创建时间
        project_name: 项目名称 (用于项目级归档)
        deliverable_type: 交付物类型 (如 'article', 'outline', 'review')
        task_category: 任务类别 ('project' 或 'system')
        metadata: 扩展元数据
    """
    product_id: str
    register: str  # R1-R5
    audience: Optional[str] = None
    task_id: str = field(default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    project_name: Optional[str] = None
    deliverable_type: Optional[str] = None
    task_category: str = "project"  # 'project' 或 'system'
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证register值"""
        valid_registers = ['R1', 'R2', 'R3', 'R4', 'R5']
        if self.register not in valid_registers:
            raise ValueError(f"register必须是 {valid_registers} 之一，当前: {self.register}")
    
    def is_project_task(self) -> bool:
        """判断是否为独立项目任务"""
        return self.task_category == "project" and self.project_name is not None
