"""
V2 写作命令行入口

用法:
    python -m engine.run --product <产品ID> --register <R1-R5> [选项]

示例:
    python -m engine.run --product lecanemab --register R3 --audience 专科医师
    python -m engine.run --product lecanemab --register R4 --project-name 仑卡奈单抗患者教育 --deliverable-type article
"""
import argparse
import sys
from pathlib import Path

from engine.runtime import Application
from engine.contracts import RouteContext
from engine.evidence import LegacyResolver


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='V2 医学写作系统 - 项目写作入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础项目写作
  python -m engine.run --product lecanemab --register R3 --audience 专科医师

  # 完整项目写作（自动双层留档）
  python -m engine.run --product lecanemab --register R3 \\
      --project-name "仑卡奈单抗患者教育项目" \\
      --deliverable-type article \\
      --audience "专科医师"

  # 系统治理任务（只写主系统日志）
  python -m engine.run --product system --register R1 --task-category system

可用产品 ID:
  - lecanemab (仑卡奈单抗)
  - furmonertinib (伏美替尼)
  - trastuzumab_deruxtecan_gastric (T-DXd 胃癌)
  - lemborexant (莱博雷生)
  - donanemab (多奈单抗)
  - pluvicto (普罗文奇)
        """
    )
    
    parser.add_argument(
        '--product', '-p',
        required=True,
        help='产品标识符 (如 lecanemab, furmonertinib)'
    )
    
    parser.add_argument(
        '--register', '-r',
        required=True,
        choices=['R1', 'R2', 'R3', 'R4', 'R5'],
        help='语体等级 (R1-R5)'
    )
    
    parser.add_argument(
        '--audience', '-a',
        default=None,
        help='目标受众描述'
    )
    
    parser.add_argument(
        '--project-name',
        default=None,
        help='项目名称 (用于项目级归档，设置后启用双层日志)'
    )
    
    parser.add_argument(
        '--deliverable-type',
        default=None,
        help='交付物类型 (如 article, outline, review)'
    )
    
    parser.add_argument(
        '--task-category',
        default='project',
        choices=['project', 'system'],
        help='任务类别 (project=独立项目任务, system=系统治理任务)'
    )
    
    parser.add_argument(
        '--output-dir',
        default=None,
        help='输出目录 (默认: 仓库根目录/output/)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式，只输出结果路径'
    )
    
    return parser.parse_args()


def main():
    """主入口"""
    args = parse_args()
    
    # 构建路由上下文
    context = RouteContext(
        product_id=args.product,
        register=args.register,
        audience=args.audience,
        project_name=args.project_name,
        deliverable_type=args.deliverable_type,
        task_category=args.task_category
    )
    
    # 创建应用实例
    app = Application(evidence_resolver=LegacyResolver())
    
    # 设置输出目录
    if args.output_dir:
        app.writer.output_dir = Path(args.output_dir)
    
    # 运行主链
    result = app.run(context)
    
    # 输出结果
    if args.quiet:
        if result.output_path:
            print(str(result.output_path))
    else:
        print(f"任务完成: {context.task_id}")
        print(f"状态: {result.summary.get('status', 'unknown')}")
        
        if result.output_path:
            print(f"输出: {result.output_path}")
        
        if result.task_log_paths:
            print(f"日志文件:")
            for log_path in result.task_log_paths:
                print(f"  - {log_path}")
        
        if result.task_log_path:
            print(f"主日志: {result.task_log_path}")
    
    # 返回退出码
    sys.exit(0 if result.summary.get('status') == 'success' else 1)


if __name__ == '__main__':
    main()