#!/usr/bin/env python
"""
财报造假分析系统 - 主入口点
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.analyzer import FinancialFraudAnalyzer
from src.utils.validation_utils import validate_pdf_file
from src.utils.file_utils import list_files


def cmd_analyze(args):
    """分析单个财报文件"""
    # 验证PDF文件
    print("验证PDF文件...")
    validation_result = validate_pdf_file(args.pdf_file)

    if not validation_result["valid"]:
        print("PDF文件验证失败:")
        for error in validation_result["errors"]:
            print(f"   - {error}")
        return 1

    print("PDF文件验证通过")
    print(f"   文件: {validation_result['file_info']['name']}")
    print(f"   大小: {validation_result['file_info']['size_mb']:.2f} MB")
    print()

    try:
        analyzer = FinancialFraudAnalyzer(output_dir=args.output)
        report = analyzer.analyze(
            pdf_path=args.pdf_file,
            company_name=args.company,
            report_year=args.year
        )

        report_path = analyzer.report_generator.save_report(report, args.format)
        print(f"\n分析完成！报告已保存到: {report_path}")

        print(f"\n风险摘要:")
        print(f"  风险等级: {report.risk_assessment.risk_level.value}")
        print(f"  风险评分: {report.risk_assessment.total_score:.1f}/50")
        print(f"  检测到造假模式: {len(report.risk_assessment.fraud_patterns)} 个")
        print(f"\n投资建议:")
        print(f"  {report.investment_recommendation}")

        return 0

    except Exception as e:
        print(f"\n分析过程中出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_batch(args):
    """批量分析多个财报文件"""
    import time

    input_path = Path(args.input)

    if input_path.is_dir():
        pdf_files = list_files(str(input_path), "*.pdf")
    elif "*" in str(input_path):
        pdf_files = list(input_path.parent.glob(input_path.name))
        pdf_files = [str(f) for f in pdf_files if f.is_file() and f.suffix.lower() == ".pdf"]
    else:
        pdf_files = [str(input_path)] if input_path.is_file() else []

    if not pdf_files:
        print(f"未找到PDF文件: {args.input}")
        return 1

    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  {Path(pdf_file).name}")
    print()

    # 验证所有PDF文件
    valid_files = []
    for pdf_file in pdf_files:
        validation_result = validate_pdf_file(pdf_file)
        if validation_result["valid"]:
            valid_files.append(pdf_file)

    if not valid_files:
        print("没有有效的PDF文件")
        return 1

    print(f"验证通过 {len(valid_files)}/{len(pdf_files)} 个文件")

    analyzer = FinancialFraudAnalyzer(output_dir=args.output)

    print(f"\n开始批量分析...")
    start_time = time.time()

    try:
        reports = analyzer.batch_analyze(valid_files, args.output)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\n{'='*60}")
        print(f"批量分析完成!")
        print(f"{'='*60}")
        print(f"分析统计:")
        print(f"   总文件数: {len(pdf_files)}")
        print(f"   有效文件: {len(valid_files)}")
        print(f"   成功分析: {len(reports)}")
        print(f"   总耗时: {elapsed_time:.2f} 秒")

        print(f"\n报告保存到: {args.output}")
        return 0

    except Exception as e:
        print(f"\n批量分析过程中出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="财报造假分析系统 - 分析上市公司财务报告，识别财务风险和造假迹象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # analyze 子命令
    analyze_parser = subparsers.add_parser("analyze", help="分析单个财报文件")
    analyze_parser.add_argument("pdf_file", help="要分析的PDF财报文件路径")
    analyze_parser.add_argument("--company", "-c", default="", help="公司名称")
    analyze_parser.add_argument("--year", "-y", type=int, default=0, help="报告年度")
    analyze_parser.add_argument("--output", "-o", default="outputs", help="报告输出目录")
    analyze_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="报告格式")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    analyze_parser.set_defaults(func=cmd_analyze)

    # batch 子命令
    batch_parser = subparsers.add_parser("batch", help="批量分析多个财报文件")
    batch_parser.add_argument("input", help="输入文件或目录")
    batch_parser.add_argument("--output", "-o", default="outputs", help="报告输出目录")
    batch_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="报告格式")
    batch_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    batch_parser.set_defaults(func=cmd_batch)

    parser.add_argument("--version", action="version", version="财报造假分析系统 v2.0.0")

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
