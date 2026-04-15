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

from scripts.analyze_fraud import main as analyze_fraud_main
from scripts.batch_analyze import main as batch_analyze_main


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="财报造假分析系统 - 分析上市公司财务报告，识别财务风险和造假迹象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令:
  analyze     分析单个财报文件
  batch       批量分析多个财报文件
  help        显示帮助信息

示例:
  %(prog)s analyze report.pdf
  %(prog)s analyze report.pdf --company "英洛华科技" --year 2025
  %(prog)s batch reports/*.pdf
  %(prog)s batch reports/ --output batch_results/
        """
    )
    
    parser.add_argument(
        "command",
        choices=["analyze", "batch", "help"],
        help="要执行的命令"
    )
    
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="命令参数"
    )
    
    # 添加版本选项
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="财报造假分析系统 v2.0.0"
    )
    
    args = parser.parse_args()
    
    if args.command == "help":
        parser.print_help()
        return 0
    
    # 根据命令调用相应的函数
    if args.command == "analyze":
        # 重新解析参数给analyze_fraud_main
        analyze_parser = argparse.ArgumentParser(
            description="分析单个财报文件",
            add_help=False
        )
        analyze_parser.add_argument("pdf_file")
        analyze_parser.add_argument("--company", "-c", default="")
        analyze_parser.add_argument("--year", "-y", type=int, default=0)
        analyze_parser.add_argument("--output", "-o", default="reports")
        analyze_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
        analyze_parser.add_argument("--verbose", action="store_true")
        
        try:
            analyze_args = analyze_parser.parse_args(args.args)
            return analyze_fraud_main()
        except SystemExit:
            # argparse打印帮助信息后退出
            return 0
        except Exception as e:
            print(f"错误: {e}")
            analyze_parser.print_help()
            return 1
    
    elif args.command == "batch":
        # 重新解析参数给batch_analyze_main
        batch_parser = argparse.ArgumentParser(
            description="批量分析多个财报文件",
            add_help=False
        )
        batch_parser.add_argument("input")
        batch_parser.add_argument("--output", "-o", default="reports")
        batch_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
        batch_parser.add_argument("--verbose", action="store_true")
        batch_parser.add_argument("--parallel", "-p", type=int, default=1)
        
        try:
            batch_args = batch_parser.parse_args(args.args)
            return batch_analyze_main()
        except SystemExit:
            # argparse打印帮助信息后退出
            return 0
        except Exception as e:
            print(f"错误: {e}")
            batch_parser.print_help()
            return 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())