"""
视觉内容抽取器测试

测试 VisualExtractor 类的功能。
"""
import pytest
from datetime import datetime
from engine.intake import VisualExtractor, extract_visual_assets, extract_visual_assets_batch
from engine.evidence import AssetType, SourceType, SourceRecord
from engine.evidence.registry import EvidenceRegistry


class TestVisualExtractor:
    """测试视觉内容抽取器"""
    
    @pytest.fixture
    def sample_page_content(self):
        """返回示例页面内容"""
        return {
            "images": [
                {
                    "content": "Image content 1",
                    "filename": "image1.png",
                    "width": 100,
                    "height": 100
                },
                {
                    "content": "Image content 2",
                    "filename": "image2.png",
                    "width": 200,
                    "height": 200
                }
            ],
            "tables": [
                {
                    "content": "Table content 1",
                    "rows": 10,
                    "columns": 5
                }
            ],
            "charts": [
                {
                    "content": "Chart content 1",
                    "type": "bar"
                }
            ]
        }
    
    @pytest.fixture
    def visual_extractor(self):
        """创建视觉抽取器实例"""
        return VisualExtractor()
    
    @pytest.fixture
    def registry(self):
        """创建证据注册表"""
        return EvidenceRegistry()
    
    def test_extract_images(self, visual_extractor, sample_page_content):
        """测试图片抽取"""
        assets = visual_extractor.extract(sample_page_content, page_number=1)
        
        image_assets = [a for a in assets if a.asset_type == AssetType.IMAGE]
        assert len(image_assets) == 2
        
        # 检查资产类型和属性
        for asset in image_assets:
            assert asset.asset_type == AssetType.IMAGE
            assert asset.asset_id.startswith("VIS-")
            assert asset.asset_key.startswith("VIS-")
            assert "page_number" in asset.metadata
    
    def test_extract_tables(self, visual_extractor, sample_page_content):
        """测试表格抽取"""
        assets = visual_extractor.extract(sample_page_content, page_number=1)
        
        table_assets = [a for a in assets if a.asset_type == AssetType.TABLE]
        assert len(table_assets) == 1
        
        table = table_assets[0]
        assert table.asset_type == AssetType.TABLE
        assert "rows" in table.metadata
        assert "columns" in table.metadata
    
    def test_extract_charts(self, visual_extractor, sample_page_content):
        """测试图表抽取"""
        assets = visual_extractor.extract(sample_page_content, page_number=1)
        
        chart_assets = [a for a in assets if a.asset_type == AssetType.CHART]
        assert len(chart_assets) == 1
        
        chart = chart_assets[0]
        assert chart.asset_type == AssetType.CHART
        assert "type" in chart.metadata
    
    def test_extract_with_registry(self, visual_extractor, sample_page_content, registry):
        """测试使用注册表"""
        extractor = VisualExtractor(registry)
        assets = extractor.extract(sample_page_content, page_number=1)
        
        assert len(assets) == 4
        
        # 检查是否已注册到注册表
        for asset in assets:
            assert registry.get_asset(asset.asset_id) == asset
    
    def test_extract_batch(self, visual_extractor, sample_page_content):
        """测试批量抽取"""
        pages_content = [
            sample_page_content,
            sample_page_content
        ]
        
        assets = visual_extractor.extract_batch(pages_content)
        
        assert len(assets) == 8  # 4个资产/页面，2页
        
        # 检查页面编号
        page_numbers = set(asset.metadata.get("page_number") for asset in assets)
        assert len(page_numbers) == 2
        assert 1 in page_numbers
        assert 2 in page_numbers
    
    def test_extract_images_with_metadata(self, visual_extractor, sample_page_content):
        """测试使用元数据抽取"""
        metadata = {
            "source": "test_source.pdf",
            "confidence": 0.95
        }
        
        assets = visual_extractor.extract(
            sample_page_content, 
            page_number=1,
            metadata=metadata
        )
        
        assert len(assets) == 4
        
        # 检查元数据
        for asset in assets:
            assert "source" in asset.metadata
            assert "confidence" in asset.metadata
            assert asset.metadata["source"] == "test_source.pdf"
            assert asset.metadata["confidence"] == 0.95
    
    def test_convenience_functions(self, sample_page_content):
        """测试便捷函数"""
        # 测试单个页面
        assets1 = extract_visual_assets(sample_page_content, page_number=1)
        assert len(assets1) == 4
        
        # 测试批量抽取
        pages_content = [sample_page_content, sample_page_content]
        assets2 = extract_visual_assets_batch(pages_content)
        assert len(assets2) == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
