"""
任务日志器

记录任务执行日志，支持双层日志机制：
1. 主系统摘要日志：写作项目运行日志/
2. 项目内详细日志：projects/{项目名}/项目日志/
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from ..contracts import RouteContext, DeliveryResult


# Windows 保留名
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

# Windows 非法字符
WINDOWS_INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Windows 文件名合法化
    
    Args:
        name: 原始文件名
        replacement: 替换字符
        
    Returns:
        合法化的文件名
    """
    if not name:
        return "unnamed"
    
    # 替换非法字符
    sanitized = WINDOWS_INVALID_CHARS.sub(replacement, name)
    
    # 去除首尾空格和点
    sanitized = sanitized.strip(' .')
    
    # 检查保留名
    name_upper = sanitized.upper()
    if name_upper in WINDOWS_RESERVED_NAMES:
        sanitized = f"_{sanitized}"
    
    # 限制长度 (Windows 路径限制)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized or "unnamed"


def find_repo_root() -> Path:
    """
    查找仓库根目录
    
    从当前文件向上查找，直到找到包含 .git 目录或特定标记文件的目录。
    
    Returns:
        仓库根目录路径
    """
    current = Path(__file__).resolve()
    
    # 最多向上查找 10 层
    for _ in range(10):
        # 检查是否是仓库根目录
        if (current / '.git').exists():
            return current
        if (current / 'medical_kb_system_v2').exists() and (current / 'projects').exists():
            return current
        if (current / '项目规范').exists():
            return current
        
        parent = current.parent
        if parent == current:
            break
        current = parent
    
    # 回退：假设 medical_kb_system_v2 的父目录是仓库根
    return Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class TaskLogger:
    """
    任务日志记录器
    
    支持"双层日志"机制：
    1. 主系统摘要日志：记录任务摘要索引
    2. 项目内详细日志：保存完整过程文档
    
    路径解析基于仓库根目录，不依赖当前工作目录。
    """
    
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    repo_root: Optional[Path] = field(default=None)
    
    # 双层日志目录名
    ROOT_LOG_DIR_NAME: str = "写作项目运行日志"
    PROJECT_LOG_DIR_NAME: str = "项目日志"
    PROJECTS_DIR_NAME: str = "projects"
    
    def __post_init__(self):
        """初始化仓库根目录"""
        if self.repo_root is None:
            self.repo_root = find_repo_root()
    
    def get_root_log_dir(self) -> Path:
        """获取主系统日志目录"""
        return self.repo_root / self.ROOT_LOG_DIR_NAME
    
    def get_project_log_dir(self, project_name: str) -> Path:
        """
        获取项目日志目录
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目日志目录路径
        """
        safe_project = sanitize_filename(project_name)
        return self.repo_root / self.PROJECTS_DIR_NAME / safe_project / self.PROJECT_LOG_DIR_NAME
    
    def log_task(self, context: RouteContext, result: DeliveryResult) -> List[Path]:
        """
        记录任务日志
        
        根据 task_category 和 project_name 决定日志写入位置：
        - 系统治理任务：只写主系统日志
        - 独立项目任务：写双层日志（主系统摘要 + 项目内详细日志）
        
        Args:
            context: 路由上下文
            result: 交付结果
            
        Returns:
            日志文件路径列表
        """
        log_paths = []
        
        # 判断是否为项目任务
        is_project = context.is_project_task()
        
        if is_project:
            # 项目任务：写双层日志
            # 1. 主系统摘要日志
            root_log_path = self._write_root_summary(context, result)
            log_paths.append(root_log_path)
            
            # 2. 项目内详细日志
            project_log_path = self._write_project_detail(context, result)
            log_paths.append(project_log_path)
        else:
            # 系统治理任务：只写主系统日志
            root_log_path = self._write_root_summary(context, result)
            log_paths.append(root_log_path)
        
        return log_paths
    
    def _write_root_summary(self, context: RouteContext, result: DeliveryResult) -> Path:
        """
        写入主系统摘要日志
        
        Args:
            context: 路由上下文
            result: 交付结果
            
        Returns:
            日志文件路径
        """
        root_log_dir = self.get_root_log_dir()
        root_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_suffix = f"_{sanitize_filename(context.project_name)}" if context.project_name else ""
        filename = f"{timestamp}{project_suffix}_{context.task_id[:12]}.md"
        filename = sanitize_filename(filename)
        
        log_path = root_log_dir / filename
        
        # 构建 Markdown 摘要
        lines = [
            f"# 任务日志 - {context.task_id}",
            "",
            f"**创建时间**: {context.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**完成时间**: {result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if result.completed_at else 'N/A'}",
            f"**产品ID**: {context.product_id}",
            f"**语体等级**: {context.register}",
            f"**受众**: {context.audience or '未指定'}",
            f"**任务类型**: {context.task_category}",
            "",
        ]
        
        if context.project_name:
            lines.extend([
                f"**项目名称**: {context.project_name}",
                "",
            ])
        
        if context.deliverable_type:
            lines.extend([
                f"**交付物类型**: {context.deliverable_type}",
                "",
            ])
        
        lines.extend([
            "## 输出",
            "",
            f"- **输出路径**: {result.output_path or '无'}",
            f"- **状态**: {result.summary.get('status', 'unknown')}",
            "",
        ])
        
        if result.artifacts:
            lines.extend([
                "## 产物",
                "",
            ])
            for artifact in result.artifacts:
                lines.append(f"- {artifact}")
            lines.append("")
        
        # 项目任务：添加详细日志位置
        if context.is_project_task():
            project_log_dir = self.get_project_log_dir(context.project_name)
            lines.extend([
                "## 详细日志",
                "",
                f"项目详细日志位置: `{project_log_dir}`",
                "",
            ])
        
        log_path.write_text("\n".join(lines), encoding='utf-8')
        
        return log_path
    
    def _write_project_detail(self, context: RouteContext, result: DeliveryResult) -> Path:
        """
        写入项目内详细日志
        
        Args:
            context: 路由上下文
            result: 交付结果
            
        Returns:
            日志文件路径
        """
        if not context.project_name:
            raise ValueError("项目任务缺少 project_name，无法写入项目日志")
        
        project_log_dir = self.get_project_log_dir(context.project_name)
        project_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deliverable_suffix = f"_{context.deliverable_type}" if context.deliverable_type else ""
        filename = f"{timestamp}{deliverable_suffix}_{context.task_id[:12]}_detail.md"
        filename = sanitize_filename(filename)
        
        log_path = project_log_dir / filename
        
        # 构建详细 Markdown 日志
        lines = [
            f"# 项目任务详细日志",
            "",
            f"**任务ID**: {context.task_id}",
            f"**项目名称**: {context.project_name}",
            "",
            "---",
            "",
            "## 基本信息",
            "",
            f"| 字段 | 值 |",
            f"|------|-----|",
            f"| 产品ID | {context.product_id} |",
            f"| 语体等级 | {context.register} |",
            f"| 受众 | {context.audience or '未指定'} |",
            f"| 交付物类型 | {context.deliverable_type or '未指定'} |",
            f"| 创建时间 | {context.created_at.strftime('%Y-%m-%d %H:%M:%S')} |",
            f"| 完成时间 | {result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if result.completed_at else 'N/A'} |",
            "",
        ]
        
        lines.extend([
            "## 执行结果",
            "",
            f"- **状态**: {result.summary.get('status', 'unknown')}",
            f"- **输出路径**: `{result.output_path or '无'}`",
            "",
        ])
        
        if result.artifacts:
            lines.extend([
                "## 产物列表",
                "",
            ])
            for i, artifact in enumerate(result.artifacts, 1):
                lines.append(f"{i}. `{artifact}`")
            lines.append("")
        
        # 添加完整摘要
        lines.extend([
            "## 完整摘要",
            "",
            "```json",
            json.dumps(result.summary, ensure_ascii=False, indent=2),
            "```",
            "",
        ])
        
        # 添加元数据
        if context.metadata:
            lines.extend([
                "## 扩展元数据",
                "",
                "```json",
                json.dumps(context.metadata, ensure_ascii=False, indent=2),
                "```",
                "",
            ])
        
        log_path.write_text("\n".join(lines), encoding='utf-8')
        
        return log_path