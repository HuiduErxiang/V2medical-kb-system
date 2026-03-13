"""
TaskLogger 双层日志测试

测试项目自动留档能力：
1. 项目任务双层日志
2. 系统治理任务单层日志
3. Windows 文件名合法化
4. 缺失 project_name 的行为
"""
import pytest
from pathlib import Path
from datetime import datetime

from engine.delivery.task_logger import (
    TaskLogger, sanitize_filename, find_repo_root, WINDOWS_RESERVED_NAMES
)
from engine.contracts import RouteContext, DeliveryResult


class TestSanitizeFilename:
    """测试 Windows 文件名合法化"""
    
    def test_normal_name(self):
        """普通文件名不变"""
        assert sanitize_filename("project_alpha") == "project_alpha"
    
    def test_invalid_chars(self):
        """非法字符被替换"""
        assert sanitize_filename("project<test>") == "project_test_"
        assert sanitize_filename("file:name?.txt") == "file_name_.txt"
    
    def test_reserved_names(self):
        """保留名添加前缀"""
        assert sanitize_filename("CON") == "_CON"
        assert sanitize_filename("nul") == "_nul"
        assert sanitize_filename("AUX") == "_AUX"
    
    def test_empty_name(self):
        """空名称返回默认值"""
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"
    
    def test_long_name(self):
        """超长名称被截断"""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 200
    
    def test_chinese_name(self):
        """中文名称保持"""
        assert sanitize_filename("项目测试") == "项目测试"


class TestFindRepoRoot:
    """测试仓库根目录查找"""
    
    def test_finds_root(self):
        """能找到仓库根目录"""
        root = find_repo_root()
        assert root.exists()
        # 验证是正确的根目录
        assert (root / "medical_kb_system_v2").exists()
        assert (root / "projects").exists()


class TestTaskLoggerPaths:
    """测试 TaskLogger 路径解析"""
    
    def test_root_log_dir(self, tmp_path):
        """主系统日志目录正确"""
        logger = TaskLogger(repo_root=tmp_path)
        root_log = logger.get_root_log_dir()
        
        assert root_log == tmp_path / "写作项目运行日志"
    
    def test_project_log_dir(self, tmp_path):
        """项目日志目录正确"""
        logger = TaskLogger(repo_root=tmp_path)
        project_log = logger.get_project_log_dir("test_project")
        
        assert project_log == tmp_path / "projects" / "test_project" / "项目日志"
    
    def test_project_log_dir_sanitized(self, tmp_path):
        """项目名称合法化"""
        logger = TaskLogger(repo_root=tmp_path)
        project_log = logger.get_project_log_dir("test<project>")
        
        assert "<" not in str(project_log)
        assert ">" not in str(project_log)


class TestTaskLoggerDoubleLayer:
    """测试双层日志机制"""
    
    @pytest.fixture
    def logger(self, tmp_path):
        """创建测试用 logger"""
        return TaskLogger(repo_root=tmp_path)
    
    @pytest.fixture
    def project_context(self):
        """创建项目任务上下文"""
        return RouteContext(
            product_id="lecanemab",
            register="R3",
            audience="专科医师",
            project_name="仑卡奈单抗患者教育项目",
            deliverable_type="article",
            task_category="project"
        )
    
    @pytest.fixture
    def system_context(self):
        """创建系统治理任务上下文"""
        return RouteContext(
            product_id="system",
            register="R1",
            task_category="system"
        )
    
    @pytest.fixture
    def delivery_result(self, tmp_path):
        """创建交付结果"""
        return DeliveryResult(
            output_path=tmp_path / "output" / "article.md",
            summary={
                "status": "success",
                "product_id": "lecanemab",
                "word_count": 1500
            }
        )
    
    def test_project_task_creates_double_logs(self, logger, project_context, delivery_result):
        """项目任务创建双层日志"""
        log_paths = logger.log_task(project_context, delivery_result)
        
        # 应该有 2 个日志文件
        assert len(log_paths) == 2
        
        # 验证主系统日志存在
        root_log_dir = logger.get_root_log_dir()
        assert root_log_dir.exists()
        assert log_paths[0].parent == root_log_dir
        
        # 验证项目日志存在
        project_log_dir = logger.get_project_log_dir(project_context.project_name)
        assert project_log_dir.exists()
        assert log_paths[1].parent == project_log_dir
    
    def test_system_task_creates_single_log(self, logger, system_context, delivery_result):
        """系统治理任务只创建主系统日志"""
        log_paths = logger.log_task(system_context, delivery_result)
        
        # 应该只有 1 个日志文件
        assert len(log_paths) == 1
        
        # 验证只有主系统日志存在
        root_log_dir = logger.get_root_log_dir()
        assert root_log_dir.exists()
        assert log_paths[0].parent == root_log_dir
    
    def test_log_content_is_markdown(self, logger, project_context, delivery_result):
        """日志内容是 Markdown 格式"""
        log_paths = logger.log_task(project_context, delivery_result)
        
        for log_path in log_paths:
            content = log_path.read_text(encoding='utf-8')
            # 应该是 Markdown 格式
            assert content.startswith("#")
            assert "**" in content  # 有加粗文本
    
    def test_log_contains_task_info(self, logger, project_context, delivery_result):
        """日志包含任务信息"""
        log_paths = logger.log_task(project_context, delivery_result)
        
        root_log = log_paths[0].read_text(encoding='utf-8')
        assert project_context.product_id in root_log
        assert project_context.register in root_log
        assert project_context.project_name in root_log
        
        project_log = log_paths[1].read_text(encoding='utf-8')
        assert project_context.task_id in project_log
        assert project_context.deliverable_type in project_log
    
    def test_log_without_project_name(self, logger, delivery_result):
        """没有 project_name 的项目任务仍能写主系统日志"""
        context = RouteContext(
            product_id="lecanemab",
            register="R3",
            task_category="project"
            # 注意：没有 project_name
        )
        
        # 应该正常完成（只写主系统日志）
        log_paths = logger.log_task(context, delivery_result)
        
        assert len(log_paths) == 1
        assert log_paths[0].parent == logger.get_root_log_dir()


class TestRouteContextProjectFields:
    """测试 RouteContext 新增字段"""
    
    def test_project_name_field(self):
        """测试 project_name 字段"""
        context = RouteContext(
            product_id="test",
            register="R3",
            project_name="测试项目"
        )
        
        assert context.project_name == "测试项目"
    
    def test_deliverable_type_field(self):
        """测试 deliverable_type 字段"""
        context = RouteContext(
            product_id="test",
            register="R3",
            deliverable_type="article"
        )
        
        assert context.deliverable_type == "article"
    
    def test_task_category_default(self):
        """测试 task_category 默认值"""
        context = RouteContext(
            product_id="test",
            register="R3"
        )
        
        assert context.task_category == "project"
    
    def test_is_project_task_true(self):
        """测试 is_project_task 返回 True"""
        context = RouteContext(
            product_id="test",
            register="R3",
            project_name="项目A",
            task_category="project"
        )
        
        assert context.is_project_task() is True
    
    def test_is_project_task_false_no_name(self):
        """测试 is_project_task 无项目名返回 False"""
        context = RouteContext(
            product_id="test",
            register="R3",
            task_category="project"
        )
        
        assert context.is_project_task() is False
    
    def test_is_project_task_false_system(self):
        """测试 is_project_task 系统任务返回 False"""
        context = RouteContext(
            product_id="test",
            register="R3",
            project_name="项目A",
            task_category="system"
        )
        
        assert context.is_project_task() is False
    
    def test_backward_compatibility(self):
        """测试向后兼容：旧代码仍然工作"""
        context = RouteContext(
            product_id="lecanemab",
            register="R3",
            audience="专科医师"
        )
        
        assert context.product_id == "lecanemab"
        assert context.register == "R3"
        assert context.audience == "专科医师"
        assert context.project_name is None
        assert context.deliverable_type is None