"""
版面绑定器测试

测试 LayoutBinder 类的功能。
"""
import pytest
from datetime import datetime
from engine.intake import LayoutBinder, bind_layout, bind_layout_batch
from engine.evidence import AssetType, SourceType, SourceRecord, EvidenceFragment, FragmentType
from engine.evidence.registry import EvidenceRegistry


class TestLayoutBinder:
    """测试版面绑定器"""
    
    @pytest.fixture
    def sample_page_content(self):
        """返回示例页面内容"""
        return {
            "text_blocks": [
                {
                    "content": "第一段文字内容",
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 50
                },
                {
                    "content": "第二段文字内容",
                    "x": 100,
                    "y": 200,
                    "width": 200,
                    "height": 50
                }
            ]
        }
    
    @pytest.fixture
    def sample_assets(self, registry):
        """返回示例资产列表"""
        assets = []
        
        # 创建图片资产
        asset1 = type('AssetRecord', (), {
            "asset_id": "TEST-ASSET-1",
            "asset_type": AssetType.IMAGE,
            "asset_key": "TEST-ASSET-1",
            "metadata": {
                "filename": "image1.png",
                "width": 100,
                "height": 100
            }
        })()
        
        # 创建表格资产
        asset2 = type('AssetRecord', (), {
            "asset_id": "TEST-ASSET-2",
            "asset_type": AssetType.TABLE,
            "asset_key": "TEST-ASSET-2",
            "metadata": {
                "rows": 10,
                "columns": 5
            }
        })()
        
        return [asset1, asset2]
    
    @pytest.fixture
    def layout_binder(self):
        """创建布局绑定器实例"""
        return LayoutBinder()
    
    @pytest.fixture
    def registry(self):
        """创建证据注册表"""
        return EvidenceRegistry()
    
    def test_bind_text_blocks(self, layout_binder, sample_page_content):
        """测试文本块绑定"""
        fragments = layout_binder.bind(sample_page_content, page_number=1, assets=[])
        
        text_fragments = [f for f in fragments if f.fragment_type == FragmentType.TEXT]
        assert len(text_fragments) == 2
        
        # 检查文本内容
        assert "第一段文字内容" in text_fragments[0].content
        assert "第二段文字内容" in text_fragments[1].content
        
        # 检查属性
        for fragment in text_fragments:
            assert fragment.fragment_id.startswith("FRG-")
            assert fragment.fragment_key.startswith("FRG-")
            assert fragment.asset_id is not None
            assert fragment.confidence == 1.0
    
    def test_bind_visual_assets(self, layout_binder, sample_page_content, sample_assets):
        """测试视觉资产绑定"""
        fragments = layout_binder.bind(sample_page_content, page_number=1, assets=sample_assets)
        
        image_fragments = [f for f in fragments if f.fragment_type == FragmentType.IMAGE]
        table_fragments = [f for f in fragments if f.fragment_type == FragmentType.TABLE]
        
        assert len(image_fragments) == 1
        assert len(table_fragments) == 1
        
        # 检查视觉片段内容
        image_fragment = image_fragments[0]
        assert image_fragment.content
        assert "filename" in image_fragment.metadata
        
        table_fragment = table_fragments[0]
        assert table_fragment.content
        assert "rows" in table_fragment.metadata
        assert "columns" in table_fragment.metadata
    
    def test_bind_with_registry(self, layout_binder, sample_page_content, sample_assets, registry):
        """测试使用注册表"""
        binder = LayoutBinder(registry)
        fragments = binder.bind(sample_page_content, page_number=1, assets=sample_assets)
        
        assert len(fragments) == 4
        
        # 检查是否已注册到注册表
        for fragment in fragments:
            assert registry.get_fragment(fragment.fragment_id) == fragment
    
    def test_bind_batch(self, layout_binder, sample_page_content, sample_assets):
        """测试批量绑定"""
        pages_content = [
            sample_page_content,
            sample_page_content
        ]
        
        pages_assets = [
            sample_assets,
            sample_assets
        ]
        
        fragments = layout_binder.bind_batch(pages_content, pages_assets)
        
        assert len(fragments) == 8  # 4个片段/页面，2页
        
        # 检查页面编号
        page_numbers = set(fragment.metadata["page_number"] for fragment in fragments)
        assert len(page_numbers) == 2
        assert 1 in page_numbers
        assert 2 in page_numbers
    
    def test_convenience_functions(self, sample_page_content, sample_assets):
        """测试便捷函数"""
        # 测试单个页面
        fragments1 = bind_layout(sample_page_content, page_number=1, assets=sample_assets)
        assert len(fragments1) == 4
        
        # 测试批量绑定
        pages_content = [sample_page_content, sample_page_content]
        pages_assets = [sample_assets, sample_assets]
        fragments2 = bind_layout_batch(pages_content, pages_assets)
        assert len(fragments2) == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
