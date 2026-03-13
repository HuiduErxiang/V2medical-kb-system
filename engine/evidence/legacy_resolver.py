"""
V1 兼容性解析器

专门为读取和转换 V1 (medical_kb_system) 证据数据而设计的解析器。
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path

from typing import List, Dict, Any, Optional

from .resolver import EvidenceResolver
from .models import (
    SourceRecord, AssetRecord, EvidenceFragment, FactRecord,
    SourceType, AssetType, FragmentType, FactStatus
)

class LegacyResolver(EvidenceResolver):
    """
    V1 证据兼容性解析器

    负责读取 V1 格式的 evidence database 并转换为 V2 的证据对象结构。
    """
    
    def __init__(self, v1_base_path: Optional[Path] = None):
        super().__init__()
        
        # 默认路径: 指向 V1 系统目录
        if v1_base_path is None:
            self.v1_base_path = Path(r"D:\汇度编辑部1\写作知识库\medical_kb_system")
        else:
            self.v1_base_path = Path(v1_base_path)
        
        # 缓存
        self._cache = {}
    
    def _load_v1_database(self, product_id: str) -> Dict[str, Any]:
        """加载V1的证据数据库"""
        if product_id in self._cache:
            return self._cache[product_id]
        
        # 构建V1路径: medical_kb_system/L4_product_knowledge/{product_id}/m6_evidence_database.json
        db_path = self.v1_base_path / "L4_product_knowledge" / product_id / "m6_evidence_database.json"
        
        if not db_path.exists():
            # 如果V1数据库不存在，返回空结构而不是抛出异常
            self._cache[product_id] = {"sources": [], "facts": []}
            return self._cache[product_id]
        
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._cache[product_id] = data
        return data
    
    def _compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _v1_source_type_to_enum(self, v1_type: str) -> SourceType:
        """V1 source_type映射到V2 SourceType"""
        mapping = {
            "literature": SourceType.PDF,
            "pdf": SourceType.PDF,
            "web": SourceType.WEB,
            "database": SourceType.DATABASE,
            "manual": SourceType.MANUAL
        }
        return mapping.get(v1_type.lower(), SourceType.PDF)
    
    def resolve_sources(self, query: Dict[str, Any]) -> List[SourceRecord]:
        """
        从V1加载并返回SourceRecord列表
        
        query格式: {product_id: str}
        """
        product_id = query.get("product_id")
        if not product_id:
            return []
        
        v1_data = self._load_v1_database(product_id)
        v1_sources = v1_data.get("sources", [])
        
        sources = []
        for v1_src in v1_sources:
            source = SourceRecord(
                source_id=v1_src["source_id"],
                source_type=self._v1_source_type_to_enum(v1_src.get("source_type", "pdf")),
                source_key=f"SRC-{product_id.upper()}-{v1_src['source_id']}",
                title=v1_src.get("file", ""),
                citation=v1_src.get("citation", ""),
                metadata={"v1_file": v1_src.get("file", "")}
            )
            sources.append(source)
        
        return sources
    
    def resolve_assets(self, source_ids: List[str]) -> List[AssetRecord]:
        """
        V1到V2的简化资产映射
        
        首轮简化: 每个source对应一个asset，不细分页面
        
        不需要再加载V1数据库，直接创建简化asset
        """
        assets = []
        for source_id in source_ids:
            # 直接创建简化asset，不再尝试加载V1数据库
            asset = AssetRecord(
                asset_id=f"AST-{source_id}",
                source_id=source_id,
                asset_key=f"AST-{source_id}-MAIN",
                asset_type=AssetType.DOCUMENT,
                storage_key=f"v1_sources/{source_id}",
                metadata={"v1_source_id": source_id}
            )
            assets.append(asset)
        
        return assets
    
    def resolve_fragments(self, asset_ids: List[str]) -> List[EvidenceFragment]:
        """
        V1到V2的证据片段映射
        
        首轮简化: 每个asset对应一个fragment
        """
        fragments = []
        for asset_id in asset_ids:
            # 从asset_id中提取source_id
            # asset_id格式: AST-src-123 -> source_id = src-123
            if asset_id.startswith("AST-"):
                source_id = asset_id[len("AST-"):]
            else:
                source_id = asset_id
            
            # 获取V1源信息
            parts = source_id.split("-")
            if len(parts) < 3:
                continue
                
            product_id = parts[0]
            v1_data = self._load_v1_database(product_id)
            v1_sources = {s["source_id"]: s for s in v1_data.get("sources", [])}
            
            if source_id not in v1_sources:
                continue
                
            v1_src = v1_sources[source_id]
            content = f"Citation: {v1_src.get('citation', '')}"
            
            fragment = EvidenceFragment(
                fragment_id=f"FRG-{asset_id}",
                asset_id=asset_id,
                fragment_key=f"FRG-{asset_id}-CITATION",
                fragment_type=FragmentType.TEXT,
                content=content,
                confidence=1.0,
                metadata={"v1_source_type": v1_src.get("source_type", "unknown")}
            )
            fragments.append(fragment)
        
        return fragments
    
    def resolve_facts(self, query: Dict[str, Any]) -> List[FactRecord]:
        """
        从V1加载并返回FactRecord列表
        
        query格式: {product_id: str, domain: Optional[str]}
        """
        product_id = query.get("product_id")
        domain_filter = query.get("domain")
        
        if not product_id:
            return []
        
        v1_data = self._load_v1_database(product_id)
        v1_facts = v1_data.get("facts", {})
        
        facts = []
        if isinstance(v1_facts, dict):
            # 正常V1格式：{domain: {fact_key: fact}}
            for domain, domain_facts in v1_facts.items():
                if domain_filter and domain != domain_filter:
                    continue
                
                for fact_key, v1_fact in domain_facts.items():
                    # 处理V1数据格式：可能是dict或字符串
                    if isinstance(v1_fact, str):
                        continue
                        
                    if not isinstance(v1_fact, dict):
                        continue
                        
                    # 处理source_id/source_ids
                    source_ids = v1_fact.get("source_ids", [])
                    if not source_ids:
                        single_source = v1_fact.get("source_id")
                        if single_source:
                            source_ids = [single_source]
                            
                    # 映射为fragment_ids
                    fragment_ids = [f"FRG-AST-{sid}-CITATION" for sid in source_ids]
                    
                    # 值字段可能是value或data_point
                    value = v1_fact.get("value") or v1_fact.get("data_point")
                    
                    fact = FactRecord(
                        fact_id=f"FCT-{product_id}-{domain}-{fact_key}",
                        fact_key=fact_key,
                        domain=domain,
                        definition=v1_fact.get("definition", ""),
                        definition_zh=v1_fact.get("definition_zh", ""),
                        value=value,
                        unit=v1_fact.get("unit", ""),
                        fragment_ids=fragment_ids,
                        status=FactStatus.ACTIVE,
                        lineage={
                            "source_ids": source_ids,
                            "timestamps": [datetime.now().isoformat()],
                            "v1_fact_key": fact_key
                        },
                        metadata={
                            "v1_domain": domain,
                            "v1_value_field": "value" if "value" in v1_fact else "data_point"
                        }
                    )
                    facts.append(fact)
        elif isinstance(v1_facts, list):
            # 简化测试格式：[fact]
            for idx, v1_fact in enumerate(v1_facts):
                if domain_filter and v1_fact.get("domain", "") != domain_filter:
                    continue
                
                domain = v1_fact.get("domain", "general")
                fact_key = f"test-fact-{idx}"
                
                # 处理source_id/source_ids
                source_ids = v1_fact.get("source_ids", [])
                if not source_ids:
                    single_source = v1_fact.get("source_id")
                    if single_source:
                        source_ids = [single_source]
                        
                fragment_ids = [f"FRG-AST-{sid}-CITATION" for sid in source_ids]
                
                value = v1_fact.get("value") or v1_fact.get("data_point")
                
                fact = FactRecord(
                    fact_id=f"FCT-{product_id}-{domain}-{fact_key}",
                    fact_key=fact_key,
                    domain=domain,
                    definition=v1_fact.get("definition", ""),
                    definition_zh=v1_fact.get("definition_zh", ""),
                    value=value,
                    unit=v1_fact.get("unit", ""),
                    fragment_ids=fragment_ids,
                    status=FactStatus.ACTIVE,
                    lineage={
                        "source_ids": source_ids,
                        "timestamps": [datetime.now().isoformat()],
                        "v1_fact_key": fact_key
                    },
                    metadata={
                        "v1_domain": domain,
                        "v1_value_field": "value" if "value" in v1_fact else "data_point"
                    }
                )
                facts.append(fact)
        
        return facts
    
    # Phase 2新增方法: 支持证据查询接口中的domain查询
    def resolve_by_domain(self, product_id: str, domain: str) -> List[FactRecord]:
        """按领域解析事实"""
        return self.resolve_facts({"product_id": product_id, "domain": domain})
    
    # Phase 2新增方法: 支持证据查询接口中的事实键查询
    def resolve_by_fact_keys(self, product_id: str, fact_keys: List[str]) -> List[FactRecord]:
        """按事实键列表解析事实"""
        all_facts = self.resolve_facts({"product_id": product_id})
        return [f for f in all_facts if f.fact_key in fact_keys]
    
    # Phase 2新增方法: 支持证据查询接口中的时间范围查询
    def resolve_by_time_range(self, product_id: str, start_time: Optional[datetime] = None, 
                          end_time: Optional[datetime] = None) -> List[FactRecord]:
        """按时间范围解析事实"""
        all_facts = self.resolve_facts({"product_id": product_id})
        
        filtered = []
        for fact in all_facts:
            if fact.lineage and "timestamps" in fact.lineage and fact.lineage["timestamps"]:
                # 使用第一个时间戳进行比较
                ts_str = fact.lineage["timestamps"][0]
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue
                    
                filtered.append(fact)
                
        return filtered
    
    # Phase 2新增方法: 支持证据查询接口中的全文搜索
    def search_facts(self, product_id: str, keyword: str) -> List[FactRecord]:
        """搜索事实（按关键词）"""
        all_facts = self.resolve_facts({"product_id": product_id})
        
        keyword_lower = keyword.lower()
        matched = []
        
        for fact in all_facts:
            if fact.definition and keyword_lower in fact.definition.lower():
                matched.append(fact)
            elif fact.definition_zh and keyword_lower in fact.definition_zh.lower():
                matched.append(fact)
            elif fact.value and keyword_lower in str(fact.value).lower():
                matched.append(fact)
                
        return matched
    
    # Phase 2新增方法: 支持冲突检测
    def resolve_conflicts(self, product_id: str) -> Dict[str, List[FactRecord]]:
        """解析冲突事实（同一fact_key有多个版本的情况）"""
        all_facts = self.resolve_facts({"product_id": product_id})
        
        key_to_facts = {}
        for fact in all_facts:
            if fact.fact_key not in key_to_facts:
                key_to_facts[fact.fact_key] = []
            key_to_facts[fact.fact_key].append(fact)
            
        conflicts = {k: facts for k, facts in key_to_facts.items() if len(facts) > 1}
        return conflicts
    
    # Phase 2新增方法: 统计方法
    def count_facts_by_domain(self, product_id: str) -> Dict[str, int]:
        """统计各领域的事实数量"""
        all_facts = self.resolve_facts({"product_id": product_id})
        
        domain_counts = {}
        for fact in all_facts:
            domain_counts[fact.domain] = domain_counts.get(fact.domain, 0) + 1
            
        return domain_counts
    
    # Phase 2新增方法: 获取最新的事实
    def resolve_latest_facts(self, product_id: str, limit: int = 10) -> List[FactRecord]:
        """获取最新的事实"""
        all_facts = self.resolve_facts({"product_id": product_id})
        
        # 按时间戳排序
        sorted_facts = sorted(all_facts, 
                           key=lambda x: x.lineage.get("timestamps", [])[0] if x.lineage and "timestamps" in x.lineage and x.lineage["timestamps"] else "1970-01-01T00:00:00",
                           reverse=True)
        
        return sorted_facts[:limit]
