"""
来源分类器

识别来源类型并创建 SourceRecord 对象。
intake 前半段的第一阶段。
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes

from ..evidence.models import SourceRecord, SourceType


class SourceClassifier:
    """
    来源分类器
    
    识别来源类型（PDF/PPTX/WEB/DATABASE/MANUAL）并创建对应的 SourceRecord。
    
    Phase 2 实现：
    - 支持文件扩展名识别
    - 支持 MIME 类型识别
    - 支持 URL 模式识别
    - 支持来源元数据提取
    """
    
    # 扩展名到类型的映射
    EXTENSION_MAP: Dict[str, SourceType] = {
        ".pdf": SourceType.PDF,
        ".pptx": SourceType.PPTX,
        ".ppt": SourceType.PPTX,
        ".html": SourceType.WEB,
        ".htm": SourceType.WEB,
        ".url": SourceType.WEB,
    }
    
    # MIME 类型到类型的映射
    MIME_MAP: Dict[str, SourceType] = {
        "application/pdf": SourceType.PDF,
        "application/vnd.ms-powerpoint": SourceType.PPTX,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": SourceType.PPTX,
        "text/html": SourceType.WEB,
    }
    
    def __init__(self, registry=None):
        """
        Args:
            registry: EvidenceRegistry 实例（可选）
        """
        self.registry = registry
    
    def classify(self, source_path: str, metadata: Optional[Dict[str, Any]] = None) -> SourceRecord:
        """
        分类来源并创建 SourceRecord
        
        Args:
            source_path: 来源路径或URL
            metadata: 额外元数据
        
        Returns:
            SourceRecord: 分类后的来源记录
        """
        # 先检测URL模式（在转换为Path之前）
        source_type = self._detect_type_from_string(source_path, metadata)
        
        # 转换为Path用于后续处理
        path = Path(source_path)
        
        # 生成稳定键
        source_key = self._generate_source_key(path, source_type)
        
        # 提取标题
        title = metadata.get("title") if metadata else None
        if not title:
            title = path.stem if path.suffix else path.name
        
        # 提取引用信息
        citation = metadata.get("citation") if metadata else None
        
        # 计算 source_id
        source_id = self._generate_source_id(source_key, source_type)
        
        # 合并元数据
        full_metadata = {
            "original_path": str(source_path),
            "classified_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        record = SourceRecord(
            source_id=source_id,
            source_type=source_type,
            source_key=source_key,
            title=title,
            citation=citation,
            metadata=full_metadata
        )
        
        # 注册到 registry
        if self.registry:
            self.registry.register_source(record)
        
        return record
    
    def classify_batch(
        self, 
        source_paths: List[str], 
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[SourceRecord]:
        """
        批量分类来源
        
        Args:
            source_paths: 来源路径列表
            metadata_list: 元数据列表（可选）
        
        Returns:
            SourceRecord 列表
        """
        if metadata_list is None:
            metadata_list = [None] * len(source_paths)
        
        return [
            self.classify(path, meta)
            for path, meta in zip(source_paths, metadata_list)
        ]
    
    def _detect_type_from_string(self, source_path: str, metadata: Optional[Dict[str, Any]]) -> SourceType:
        """
        从字符串检测来源类型（在转换为Path之前）
        
        检测优先级：
        1. 元数据中显式指定
        2. URL 模式
        3. 文件扩展名
        4. MIME 类型
        5. 默认 MANUAL
        """
        # 1. 元数据显式指定
        if metadata and "source_type" in metadata:
            type_str = metadata["source_type"].lower()
            for st in SourceType:
                if st.value == type_str:
                    return st
        
        # 2. URL 模式（关键：在Path转换之前检测）
        path_str = source_path.lower()
        if path_str.startswith(("http://", "https://", "www.")):
            return SourceType.WEB
        
        # 3. 文件扩展名
        if '.' in source_path:
            ext = '.' + source_path.rsplit('.', 1)[-1].lower()
            if ext in self.EXTENSION_MAP:
                return self.EXTENSION_MAP[ext]
        
        # 4. MIME 类型
        mime_type, _ = mimetypes.guess_type(source_path)
        if mime_type and mime_type in self.MIME_MAP:
            return self.MIME_MAP[mime_type]
        
        # 5. 默认
        return SourceType.MANUAL
    
    def _detect_type(self, path: Path, metadata: Optional[Dict[str, Any]]) -> SourceType:
        """
        检测来源类型（保留兼容）
        
        检测优先级：
        1. 元数据中显式指定
        2. URL 模式
        3. 文件扩展名
        4. MIME 类型
        5. 默认 MANUAL
        """
        # 1. 元数据显式指定
        if metadata and "source_type" in metadata:
            type_str = metadata["source_type"].lower()
            for st in SourceType:
                if st.value == type_str:
                    return st
        
        # 2. URL 模式
        path_str = str(path).lower()
        if path_str.startswith(("http://", "https://", "www.")):
            return SourceType.WEB
        
        # 也检测字符串形式的URL（不依赖Path转换）
        if "http://" in path_str or "https://" in path_str:
            return SourceType.WEB
        
        # 3. 文件扩展名
        ext = path.suffix.lower()
        if ext in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[ext]
        
        # 4. MIME 类型
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type and mime_type in self.MIME_MAP:
            return self.MIME_MAP[mime_type]
        
        # 5. 默认
        return SourceType.MANUAL
    
    def _generate_source_key(self, path: Path, source_type: SourceType) -> str:
        """
        生成稳定的来源键
        
        格式: SRC-{TYPE}-{HASH}
        """
        # 使用路径的哈希作为唯一标识
        path_str = str(path)
        hash_part = hashlib.sha256(path_str.encode()).hexdigest()[:12].upper()
        type_code = source_type.value.upper()
        
        return f"SRC-{type_code}-{hash_part}"
    
    def _generate_source_id(self, source_key: str, source_type: SourceType) -> str:
        """
        生成 source_id
        
        首轮简化：直接使用 source_key
        """
        return source_key


# 便捷函数
def classify_source(source_path: str, metadata: Optional[Dict[str, Any]] = None) -> SourceRecord:
    """分类单个来源"""
    classifier = SourceClassifier()
    return classifier.classify(source_path, metadata)


def classify_sources(
    source_paths: List[str], 
    metadata_list: Optional[List[Dict[str, Any]]] = None
) -> List[SourceRecord]:
    """批量分类来源"""
    classifier = SourceClassifier()
    return classifier.classify_batch(source_paths, metadata_list)