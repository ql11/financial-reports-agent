"""命令行入口。"""

import argparse
import sys
import time
from pathlib import Path

from .core.analyzer import FinancialFraudAnalyzer
from .core.data_extractor import DataExtractionError
from .utils.file_utils import list_files
from .utils.validation_utils import validate_pdf_file


def cmd_analyze(args):
    """分析单个财报文件。"""
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
            report_year=args.year,
        )

        report_path = analyzer.report_generator.save_report(report, args.format)
        print(f"\n分析完成！报告已保存到: {report_path}")

        print("\n风险摘要:")
        print(f"  风险等级: {report.risk_assessment.risk_level.value}")
        print(f"  风险评分: {report.risk_assessment.total_score:.1f}/50")
        print(f"  检测到造假模式: {len(report.risk_assessment.fraud_patterns)} 个")
        print("\n投资建议:")
        print(f"  {report.investment_recommendation}")
        return 0
    except DataExtractionError as exc:
        print(f"\n数据提取失败: {exc}")
        print("请确认PDF为标准格式的上市公司年度报告。")
        return 1
    except Exception as exc:  # pragma: no cover - CLI兜底
        print(f"\n分析过程中出错: {exc}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def cmd_batch(args):
    """批量分析多个财报文件。"""
    input_path = Path(args.input)

    if input_path.is_dir():
        pdf_files = list_files(str(input_path), "*.pdf")
    elif "*" in str(input_path):
        pdf_files = list(input_path.parent.glob(input_path.name))
        pdf_files = [
            str(file_path)
            for file_path in pdf_files
            if file_path.is_file() and file_path.suffix.lower() == ".pdf"
        ]
    else:
        pdf_files = [str(input_path)] if input_path.is_file() else []

    if not pdf_files:
        print(f"未找到PDF文件: {args.input}")
        return 1

    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  {Path(pdf_file).name}")
    print()

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

    print("\n开始批量分析...")
    start_time = time.time()

    try:
        reports = analyzer.batch_analyze(
            valid_files,
            args.output,
            report_format=args.format,
        )
        elapsed_time = time.time() - start_time

        print(f"\n{'=' * 60}")
        print("批量分析完成!")
        print(f"{'=' * 60}")
        print("分析统计:")
        print(f"   总文件数: {len(pdf_files)}")
        print(f"   有效文件: {len(valid_files)}")
        print(f"   成功分析: {len(reports)}")
        print(f"   总耗时: {elapsed_time:.2f} 秒")
        print(f"\n报告保存到: {args.output}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI兜底
        print(f"\n批量分析过程中出错: {exc}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def build_analyze_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="财报造假分析工具 - 分析上市公司财务报告，识别财务风险和造假迹象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _configure_analyze_arguments(parser)
    return parser


def _configure_analyze_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("pdf_file", help="要分析的PDF财报文件路径")
    parser.add_argument("--company", "-c", default="", help="公司名称")
    parser.add_argument("--year", "-y", type=int, default=0, help="报告年度")
    parser.add_argument("--output", "-o", default="outputs", help="报告输出目录")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="报告格式",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    parser.add_argument("--version", action="version", version="财报造假分析系统 v2.0.0")


def build_batch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="批量财报分析工具 - 批量分析多个财报文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _configure_batch_arguments(parser)
    return parser


def _configure_batch_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("--output", "-o", default="outputs", help="报告输出目录")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="报告格式",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    parser.add_argument("--version", action="version", version="财报造假分析系统 v2.0.0")


def build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="财报造假分析系统 - 分析上市公司财务报告，识别财务风险和造假迹象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    analyze_parser = subparsers.add_parser("analyze", help="分析单个财报文件")
    _configure_analyze_arguments(analyze_parser)
    analyze_parser.set_defaults(func=cmd_analyze)

    batch_parser = subparsers.add_parser("batch", help="批量分析多个财报文件")
    _configure_batch_arguments(batch_parser)
    batch_parser.set_defaults(func=cmd_batch)

    parser.add_argument("--version", action="version", version="财报造假分析系统 v2.0.0")
    return parser


def analyze_main(argv: list[str] | None = None) -> int:
    args = build_analyze_parser().parse_args(argv)
    return cmd_analyze(args)


def batch_main(argv: list[str] | None = None) -> int:
    args = build_batch_parser().parse_args(argv)
    return cmd_batch(args)


def main(argv: list[str] | None = None) -> int:
    args = build_main_parser().parse_args(argv)

    if not hasattr(args, "func"):
        build_main_parser().print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
