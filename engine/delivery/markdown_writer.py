"""
Markdown写入器

负责生成Markdown格式的输出文件。
"""
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..contracts import EditorialPlan, DeliveryResult


@dataclass
class MarkdownWriter:
    """
    Markdown文件写入器
    
    根据EditorialPlan生成Markdown格式的文章。
    首轮最小实现：生成结构化文档框架。
    """
    
    output_dir: Path = field(default_factory=lambda: Path("output"))
    
    def write(self, plan: EditorialPlan, content: Optional[str] = None) -> Path:
        """
        写入Markdown文件
        
        Args:
            plan: 编辑计划
            content: 预生成内容 (可选)
            
        Returns:
            输出文件路径
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plan.thesis[:30].replace(' ', '_')}_{timestamp}.md"
        output_path = self.output_dir / filename
        
        # 构建Markdown内容
        lines = [
            f"# {plan.thesis}",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            f"**目标受众**: {plan.target_audience or '未指定'}",
            f"**策略**: {plan.play_id or '未指定'}",
            f"**弧线**: {plan.arc_id or '未指定'}",
            "",
            "## 大纲",
            ""
        ]
        
        for i, section in enumerate(plan.outline, 1):
            lines.append(f"{i}. {section.get('title', '未命名章节')}")
        
        lines.extend([
            "",
            "## 核心证据",
            ""
        ])
        
        for evidence in plan.key_evidence:
            lines.append(f"- {evidence}")
        
        if content:
            lines.extend([
                "",
                "## 正文",
                "",
                content
            ])
        else:
            lines.extend([
                "",
                "## 正文",
                "",
                "*[正文内容待生成]*"
            ])
        
        # 写入文件
        output_path.write_text("\n".join(lines), encoding='utf-8')
        
        return output_path
