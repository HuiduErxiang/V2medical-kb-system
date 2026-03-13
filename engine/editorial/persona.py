"""
Persona Profile 模块

定义 V2 的作者画像契约，用于 editorial 层消费。

从 V1 L2_medical_playbook/authors 重建而来。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class VoiceStyle(Enum):
    """声音风格"""
    PUNCHY = "punchy"
    ANALYTICAL = "analytical"
    COMPASSIONATE = "compassionate"
    CRITICAL = "critical"
    PREDICTIVE = "predictive"
    DRAMATIC = "dramatic"
    DATA_DRIVEN = "data_driven"
    CYNICAL = "cynical"


class EmotionalTemperature(Enum):
    """情感温度"""
    DRAMATIC_PROVOCATIVE = "dramatic_provocative"
    COMPASSIONATE_RATIONAL = "compassionate_rational"
    NEUTRAL_OBJECTIVE = "neutral_objective"
    WARM_EDUCATIONAL = "warm_educational"


@dataclass
class PersonaKernel:
    """
    人格内核
    
    定义作者的核心认知身份和立场。
    """
    kernel_id: str
    name: str
    description: str
    cognitive_identity: str  # 认知身份
    stance: str  # 立场
    attention_order: List[str] = field(default_factory=list)  # 注意力顺序
    default_suspicions: List[str] = field(default_factory=list)  # 默认怀疑


@dataclass
class VoiceProfile:
    """
    声音配置
    
    定义作者的写作风格特征。
    """
    tone: str
    voice_styles: List[VoiceStyle] = field(default_factory=list)
    signature_phrases: List[str] = field(default_factory=list)
    preferred_evidence: str = ""
    emotional_temperature: EmotionalTemperature = EmotionalTemperature.NEUTRAL_OBJECTIVE


@dataclass
class PersonaProfile:
    """
    人格画像 (V2 契约)
    
    完整的作者画像，用于 editorial 层选择写作策略。
    
    来源映射：
    - V1 persona_config.base_persona -> V2 kernel_id
    - V1 persona_config.cognitive_identity -> V2 kernel.cognitive_identity
    - V1 persona_config.stance -> V2 kernel.stance
    - V1 persona_config.signature_voice -> V2 voice.voice_styles
    - V1 vocabulary_profile.preferred_terms -> V2 vocabulary_bias
    """
    profile_id: str  # 稳定标识
    author_id: str  # 作者ID
    author_name: str  # 作者名称
    source: str  # 来源 (e.g., "lighthouse_distillation")
    domain: str  # 领域
    kernel: PersonaKernel  # 人格内核
    voice: VoiceProfile  # 声音配置
    vocabulary_bias: List[str] = field(default_factory=list)  # 词汇偏好
    narrative_patterns: List[Dict[str, Any]] = field(default_factory=list)  # 叙事模式
    rhetoric_blocks: List[Dict[str, Any]] = field(default_factory=list)  # 修辞块
    expression_additions: Dict[str, List[str]] = field(default_factory=dict)  # 表达增补
    
    # V2 元数据
    content_hash: Optional[str] = None  # 内容哈希
    source_key: str = ""  # 来源键
    migration_batch: str = "Batch-2"  # 迁移批次
    migration_decision: str = "rebuild"  # 迁移决策