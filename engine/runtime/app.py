"""
运行时应用

V2主链入口。
只做最小调度，不重新长成小号m7。

Phase 2 扩展：
- 使用 EvidenceQuery 进行结构化查询
- 集成 LineageResolver
- 支持 QueryResult
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from ..contracts import (
    RouteContext, EvidenceSelection, EditorialPlan,
    CompiledPrompt, QualityResult, DeliveryResult
)
from ..evidence import (
    EvidenceResolver, EvidenceRegistry, LegacyResolver,
    EvidenceQuery, QueryResult, QueryBuilder, QueryType, QueryStatus,
    LineageResolver
)

from ..editorial import EditorialPlanner
from ..prompt import PromptCompiler
from ..quality import QualityOrchestrator
from ..delivery import MarkdownWriter, TaskLogger


@dataclass
class Application:
    """
    V2运行时应用
    
    主链：
    evidence.resolve -> editorial.plan -> prompt.compile -> quality.run -> delivery.write
    
    Phase 2 增强：
    - 支持 EvidenceQuery 结构化查询
    - 集成 LineageResolver
    - LegacyResolver 作为降级备选
    
    不做：
    - 不聚合所有职责（不像m7那样什么都做）
    - 不直接读取旧facts/sources结构（统一走evidence access layer）
    """
    
    # 核心组件
    evidence_resolver: Optional[EvidenceResolver] = field(default=None)
    evidence_registry: EvidenceRegistry = field(default_factory=EvidenceRegistry)
    lineage_resolver: Optional[LineageResolver] = field(default=None)
    
    # 主链组件
    planner: EditorialPlanner = field(default_factory=EditorialPlanner)
    compiler: PromptCompiler = field(default_factory=PromptCompiler)
    quality: QualityOrchestrator = field(default_factory=QualityOrchestrator)
    writer: MarkdownWriter = field(default_factory=MarkdownWriter)
    logger: TaskLogger = field(default_factory=TaskLogger)
    
    def __post_init__(self):
        """初始化默认组件"""
        if self.evidence_resolver is None:
            self.evidence_resolver = LegacyResolver()
        
        if self.lineage_resolver is None:
            self.lineage_resolver = LineageResolver(self.evidence_registry)
    
    def run(self, context: RouteContext) -> DeliveryResult:
        """
        运行主链
        
        Args:
            context: 路由上下文
            
        Returns:
            DeliveryResult: 交付结果
        """
        # Step 1: 证据层 - 使用 EvidenceQuery
        evidence = self._resolve_evidence(context)
        
        # Step 2: 编辑层 - 生成编辑计划
        plan = self._plan_editorial(context, evidence)
        
        # Step 3: Prompt层 - 编译prompt
        prompt = self._compile_prompt(plan)
        
        # Step 4: 质量层 - 运行门禁
        quality_result = self._run_quality(prompt)
        
        if not quality_result.is_passed:
            return DeliveryResult(
                summary={
                    "status": "failed",
                    "errors": quality_result.errors
                }
            )
        
        # Step 5: 交付层 - 生成输出
        result = self._deliver(plan, context)
        
        return result
    
    def query(self, query: EvidenceQuery) -> QueryResult:
        """
        执行结构化证据查询
        
        Phase 3 增强：支持所有 QueryType 类型，收紧查询/结果契约
        
        Args:
            query: 证据查询对象
            
        Returns:
            QueryResult: 查询结果
        """
        import time
        start_time = time.time()
        
        result = QueryResult(query_id=query.query_id)
        
        try:
            # 根据查询类型调用相应方法
            if query.query_type == QueryType.BY_PRODUCT:
                result.facts = self.evidence_resolver.resolve_facts({
                    "product_id": query.product_id
                })
                result.sources = self.evidence_resolver.resolve_sources({
                    "product_id": query.product_id
                })
            
            elif query.query_type == QueryType.BY_DOMAIN:
                result.facts = self.evidence_resolver.resolve_by_domain(
                    query.product_id, query.domain
                )
            
            elif query.query_type == QueryType.BY_KEYS:
                result.facts = self.evidence_resolver.resolve_by_fact_keys(
                    query.product_id, query.fact_keys
                )
            
            elif query.query_type == QueryType.BY_TIME_RANGE:
                result.facts = self.evidence_resolver.resolve_by_time_range(
                    query.product_id, query.start_time, query.end_time
                )
            
            elif query.query_type == QueryType.SEARCH:
                result.facts = self.evidence_resolver.search_facts(
                    query.product_id, query.keyword
                )
            
            elif query.query_type == QueryType.CONFLICTS:
                conflicts = self.evidence_resolver.resolve_conflicts(query.product_id)
                for fact_key, facts in conflicts.items():
                    result.facts.extend(facts)
                # 记录冲突信息
                conflict_details = self.evidence_resolver.resolve_conflicting_facts(query.product_id)
                for conflict in conflict_details:
                    result.add_conflict(conflict)
            
            elif query.query_type == QueryType.BY_STATUS:
                result.facts = self.evidence_resolver.resolve_facts_by_status(
                    query.product_id, query.status
                )
            
            elif query.query_type == QueryType.BY_TYPE:
                if query.asset_type:
                    result.facts = self.evidence_resolver.resolve_assets_by_type(
                        query.product_id, query.asset_type
                    )
                elif query.fragment_type:
                    result.facts = self.evidence_resolver.resolve_fragments_by_type(
                        query.product_id, query.fragment_type
                    )
            
            elif query.query_type == QueryType.LATEST:
                result.facts = self.evidence_resolver.resolve_latest_facts(
                    query.product_id, query.limit
                )
            
            # 注册到 registry
            for source in result.sources:
                self.evidence_registry.register_source(source)
            for fact in result.facts:
                self.evidence_registry.register_fact(fact)
            
            # 包含血缘信息
            if query.include_lineage:
                for fact in result.facts:
                    lineage = self.lineage_resolver.resolve_lineage(fact.fact_id)
                    result.lineages.append({
                        "fact_id": fact.fact_id,
                        "lineage": lineage
                    })
            
            result.status = QueryStatus.SUCCESS if result.facts else QueryStatus.EMPTY
            
        except Exception as e:
            result.status = QueryStatus.FAILED
            result.metadata["error"] = str(e)
        
        result.elapsed_ms = (time.time() - start_time) * 1000
        
        return result
    def _resolve_evidence(self, context: RouteContext) -> EvidenceSelection:
        """解析证据 - 使用 EvidenceQuery"""
        # 构建 EvidenceQuery
        query = (QueryBuilder()
            .product(context.product_id)
            .limit(10)
            .include_lineage(True)
            .build())
        
        # 执行查询
        query_result = self.query(query)
        
        # 转换为 EvidenceSelection
        selection = EvidenceSelection()
        
        for fact in query_result.facts:
            selection.add_fact_record(fact)
            
            # 构建简化片段
            from ..evidence.models import EvidenceFragment, FragmentType
            fragment = EvidenceFragment(
                fragment_id=f"FRG-{fact.fact_id}",
                asset_id=f"AST-{fact.fact_key}",
                fragment_key=f"FRG-{fact.fact_key}",
                fragment_type=FragmentType.TEXT,
                content=f"{fact.definition or fact.definition_zh or ''}: {fact.value} {fact.unit or ''}".strip(),
                confidence=1.0,
                metadata={"domain": fact.domain}
            )
            selection.add_fragment(fragment)
        
        selection.metadata = {
            "query_id": query.query_id,
            "query_type": query.query_type.value,
            "total_facts": len(query_result.facts),
            "total_sources": len(query_result.sources),
            "selected_count": len(selection.selected_facts),
            "resolver_type": type(self.evidence_resolver).__name__,
            "elapsed_ms": query_result.elapsed_ms
        }
        
        return selection
    
    def _plan_editorial(self, context: RouteContext, evidence: EvidenceSelection) -> EditorialPlan:
        """生成编辑计划"""
        return self.planner.plan(context, evidence)
    
    def _compile_prompt(self, plan: EditorialPlan) -> CompiledPrompt:
        """编译prompt"""
        return self.compiler.compile(plan)
    
    def _run_quality(self, prompt: CompiledPrompt) -> QualityResult:
        """运行质量门禁"""
        return self.quality.run_gates(prompt)
    
    def _deliver(self, plan: EditorialPlan, context: RouteContext) -> DeliveryResult:
        """交付结果"""
        output_path = self.writer.write(plan)
        
        result = DeliveryResult(
            output_path=output_path,
            summary={
                "status": "success",
                "product_id": context.product_id,
                "register": context.register
            }
        )
        
        # 记录任务日志并回填路径
        log_paths = self.logger.log_task(context, result)
        for log_path in log_paths:
            result.add_log_path(log_path)
        
        return result