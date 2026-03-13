"""
Intake 模块

处理来源摄入、页面解包、证据构建及后半段流程。
"""
from .source_classifier import SourceClassifier, classify_source, classify_sources
from .page_unpacker import PageUnpacker, unpack_source, unpack_sources
from .evidence_builder import EvidenceBuilder, build_evidence, build_fact_from_dict
from .visual_extractor import VisualExtractor, extract_visual_assets, extract_visual_assets_batch
from .layout_binder import LayoutBinder, bind_layout, bind_layout_batch
from .review_queue import ReviewQueue, ReviewStatus, ReviewPriority, create_review_queue, add_to_queue
from .promote import PromoteManager, promote_fragment, promote_fragments

__all__ = [
    "SourceClassifier",
    "PageUnpacker",
    "EvidenceBuilder",
    "VisualExtractor",
    "LayoutBinder",
    "ReviewQueue",
    "PromoteManager",
    "classify_source",
    "classify_sources",
    "unpack_source",
    "unpack_sources",
    "build_evidence",
    "build_fact_from_dict",
    "extract_visual_assets",
    "extract_visual_assets_batch",
    "bind_layout",
    "bind_layout_batch",
    "create_review_queue",
    "add_to_queue",
    "promote_fragment",
    "promote_fragments",
    "ReviewStatus",
    "ReviewPriority"
]