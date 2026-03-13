"""
交付结果

define delivery output.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class DeliveryResult:
    """
    交付结果 - 交付层的输出
    
    Attributes:
        output_path: 主输出文件路径
        task_log_path: 任务日志路径
        artifacts: 所有生成产物的路径列表
        summary: 交付摘要
        completed_at: 完成时间
    """
    output_path: Optional[Path] = None
    task_log_path: Optional[Path] = None
    task_log_paths: List[Path] = field(default_factory=list)
    artifacts: List[Path] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)
    
    def add_artifact(self, path: Path):
        """添加产物路径"""
        self.artifacts.append(path)
    
    def add_log_path(self, path: Path):
        """添加日志路径"""
        self.task_log_paths.append(path)
        if self.task_log_path is None:
            self.task_log_path = path  # 第一个作为主日志
    
    def add_artifact(self, path: Path):
        """添加产物路径"""
        self.artifacts.append(path)
