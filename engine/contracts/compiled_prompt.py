"""
编译后的Prompt

define compiled prompt output.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class CompiledPrompt:
    """
    编译后的Prompt - Prompt层输出的最终生成指令
    
    Attributes:
        system_prompt: 系统级指令
        user_prompt: 用户级指令 (主内容)
        model_config: 模型配置参数
        metadata: 编译过程的元数据
    """
    system_prompt: str
    user_prompt: str
    model_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_messages(self) -> list:
        """转换为OpenAI风格的messages格式"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]
