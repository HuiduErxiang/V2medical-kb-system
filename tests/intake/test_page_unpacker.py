"""
页面解包器测试
"""
import pytest

from engine.intake import PageUnpacker, unpack_source
from engine.evidence.models import SourceRecord, SourceType, AssetType


class TestPageUnpacker:
    """测试页面解包器"""
    
    @pytest.fixture
    def pdf_source(self):
        """创建PDF来源"""
        return SourceRecord(
            source_id="SRC-PDF-TEST",
            source_type=SourceType.PDF,
            source_key="SRC-PDF-TEST"
        )
    
    @pytest.fixture
    def pptx_source(self):
        """创建PPTX来源"""
        return SourceRecord(
            source_id="SRC-PPTX-TEST",
            source_type=SourceType.PPTX,
            source_key="SRC-PPTX-TEST"
        )
    
    @pytest.fixture
    def web_source(self):
        """创建WEB来源"""
        return SourceRecord(
            source_id="SRC-WEB-TEST",
            source_type=SourceType.WEB,
            source_key="SRC-WEB-TEST"
        )
    
    def test_unpack_pdf(self, pdf_source):
        """测试PDF解包"""
        unpacker = PageUnpacker()
        assets = unpacker.unpack(pdf_source)
        
        assert len(assets) >= 1
        assert assets[0].source_id == pdf_source.source_id
        assert assets[0].asset_type == AssetType.DOCUMENT
    
    def test_unpack_pptx(self, pptx_source):
        """测试PPTX解包"""
        unpacker = PageUnpacker()
        assets = unpacker.unpack(pptx_source)
        
        assert len(assets) >= 1
        assert assets[0].source_id == pptx_source.source_id
        assert assets[0].asset_type == AssetType.SNAPSHOT
    
    def test_unpack_web(self, web_source):
        """测试WEB解包"""
        unpacker = PageUnpacker()
        assets = unpacker.unpack(web_source)
        
        assert len(assets) == 1
        assert assets[0].source_id == web_source.source_id
        assert assets[0].asset_type == AssetType.SNAPSHOT
    
    def test_unpack_generic(self):
        """测试通用解包"""
        unpacker = PageUnpacker()
        
        # MANUAL类型
        source = SourceRecord(
            source_id="SRC-MANUAL-TEST",
            source_type=SourceType.MANUAL,
            source_key="SRC-MANUAL-TEST"
        )
        
        assets = unpacker.unpack(source)
        
        assert len(assets) == 1
        assert assets[0].asset_type == AssetType.DOCUMENT
    
    def test_unpack_batch(self, pdf_source, pptx_source):
        """测试批量解包"""
        unpacker = PageUnpacker()
        sources = [pdf_source, pptx_source]
        
        result = unpacker.unpack_batch(sources)
        
        assert len(result) == 2
        assert pdf_source.source_id in result
        assert pptx_source.source_id in result
    
    def test_convenience_function(self, pdf_source):
        """测试便捷函数"""
        assets = unpack_source(pdf_source)
        
        assert len(assets) >= 1
    
    def test_asset_key_format(self, pdf_source):
        """测试资产键格式"""
        unpacker = PageUnpacker()
        assets = unpacker.unpack(pdf_source)
        
        for asset in assets:
            assert asset.asset_key.startswith("AST-")
            assert pdf_source.source_key in asset.asset_key


class TestAssetRecordCreation:
    """测试资产记录创建"""
    
    def test_asset_has_storage_key(self):
        """测试资产有存储键"""
        unpacker = PageUnpacker()
        
        source = SourceRecord(
            source_id="SRC-TEST",
            source_type=SourceType.PDF,
            source_key="SRC-TEST"
        )
        
        assets = unpacker.unpack(source)
        
        for asset in assets:
            assert asset.storage_key is not None
    
    def test_asset_has_metadata(self):
        """测试资产有元数据"""
        unpacker = PageUnpacker()
        
        source = SourceRecord(
            source_id="SRC-TEST",
            source_type=SourceType.PDF,
            source_key="SRC-TEST"
        )
        
        assets = unpacker.unpack(source)
        
        for asset in assets:
            assert "created_at" in asset.metadata