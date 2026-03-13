"""
来源分类器测试
"""
import pytest

from engine.intake import SourceClassifier, classify_source
from engine.evidence.models import SourceType


class TestSourceClassifier:
    """测试来源分类器"""
    
    def test_classify_pdf(self):
        """测试PDF分类"""
        classifier = SourceClassifier()
        source = classifier.classify("/path/to/document.pdf")
        
        assert source.source_type == SourceType.PDF
        assert source.source_key.startswith("SRC-PDF-")
    
    def test_classify_pptx(self):
        """测试PPTX分类"""
        classifier = SourceClassifier()
        source = classifier.classify("/path/to/slides.pptx")
        
        assert source.source_type == SourceType.PPTX
        assert source.source_key.startswith("SRC-PPTX-")
    
    def test_classify_web_url(self):
        """测试URL分类"""
        classifier = SourceClassifier()
        source = classifier.classify("https://example.com/article")
        
        assert source.source_type == SourceType.WEB
        assert source.source_key.startswith("SRC-WEB-")
    
    def test_classify_with_metadata(self):
        """测试带元数据分类"""
        classifier = SourceClassifier()
        source = classifier.classify(
            "/path/to/document.pdf",
            metadata={
                "title": "Test Document",
                "citation": "Author et al., 2024"
            }
        )
        
        assert source.title == "Test Document"
        assert source.citation == "Author et al., 2024"
    
    def test_classify_with_explicit_type(self):
        """测试显式类型指定"""
        classifier = SourceClassifier()
        source = classifier.classify(
            "/path/to/unknown",
            metadata={"source_type": "database"}
        )
        
        assert source.source_type == SourceType.DATABASE
    
    def test_classify_batch(self):
        """测试批量分类"""
        classifier = SourceClassifier()
        paths = [
            "/path/to/doc1.pdf",
            "/path/to/doc2.pdf",
            "https://example.com/page"
        ]
        
        sources = classifier.classify_batch(paths)
        
        assert len(sources) == 3
        assert sources[0].source_type == SourceType.PDF
        assert sources[2].source_type == SourceType.WEB
    
    def test_convenience_function(self):
        """测试便捷函数"""
        source = classify_source("/path/to/test.pdf")
        
        assert source.source_type == SourceType.PDF


class TestSourceTypeDetection:
    """测试来源类型检测"""
    
    def test_extension_detection(self):
        """测试扩展名检测"""
        classifier = SourceClassifier()
        
        # PDF
        source = classifier.classify("test.pdf")
        assert source.source_type == SourceType.PDF
        
        # PPTX
        source = classifier.classify("test.pptx")
        assert source.source_type == SourceType.PPTX
        
        # HTML
        source = classifier.classify("test.html")
        assert source.source_type == SourceType.WEB
    
    def test_url_detection(self):
        """测试URL检测"""
        classifier = SourceClassifier()
        
        source = classifier.classify("http://example.com")
        assert source.source_type == SourceType.WEB
        
        source = classifier.classify("https://example.com/path")
        assert source.source_type == SourceType.WEB
    
    def test_fallback_to_manual(self):
        """测试降级到MANUAL"""
        classifier = SourceClassifier()
        
        # 未知扩展名
        source = classifier.classify("/path/to/unknown.xyz")
        assert source.source_type == SourceType.MANUAL