#!/usr/bin/env python
"""
批量财报分析工具
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.analyzer import FinancialFraudAnalyzer
from src.utils.file_utils import list_files
from src.utils.validation_utils import validate_pdf_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量财报分析工具 - 批量分析多个财报文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s inputs/*.pdf
  %(prog)s inputs/ --output batch_results/
  %(prog)s inputs/ --format json --verbose
        """
    )
    
    parser.add_argument(
        "input",
        help="输入文件或目录（支持通配符）"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="报告输出目录（默认: outputs）",
        default="outputs"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        help="报告格式（默认: markdown）",
        default="markdown"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        type=int,
        help="并行处理数量（默认: 1）",
        default=1
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="批量财报分析工具 v2.0.0"
    )
    
    args = parser.parse_args()
    
    # 获取PDF文件列表
    input_path = Path(args.input)
    
    if input_path.is_dir():
        pdf_files = list_files(str(input_path), "*.pdf")
    elif "*" in str(input_path):
        # 处理通配符
        pdf_files = list(input_path.parent.glob(input_path.name))
        pdf_files = [str(f) for f in pdf_files if f.is_file() and f.suffix.lower() == ".pdf"]
    else:
        pdf_files = [str(input_path)] if input_path.is_file() else []
    
    if not pdf_files:
        print(f"❌ 未找到PDF文件: {args.input}")
        sys.exit(1)
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  📄 {Path(pdf_file).name}")
    print()
    
    # 验证所有PDF文件
    valid_files = []
    for pdf_file in pdf_files:
        if args.verbose:
            print(f"验证文件: {Path(pdf_file).name}")
        
        validation_result = validate_pdf_file(pdf_file)
        
        if validation_result["valid"]:
            valid_files.append(pdf_file)
            if args.verbose:
                print(f"  ✅ 验证通过")
        else:
            print(f"  ❌ 验证失败: {Path(pdf_file).name}")
            for error in validation_result["errors"]:
                print(f"     - {error}")
    
    if not valid_files:
        print("❌ 没有有效的PDF文件")
        sys.exit(1)
    
    print(f"\n✅ 验证通过 {len(valid_files)}/{len(pdf_files)} 个文件")
    
    # 创建分析器
    analyzer = FinancialFraudAnalyzer(output_dir=args.output)
    
    # 批量分析
    print(f"\n开始批量分析...")
    start_time = time.time()
    
    try:
        reports = analyzer.batch_analyze(valid_files, args.output)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n{'='*60}")
        print(f"批量分析完成!")
        print(f"{'='*60}")
        print(f"📊 分析统计:")
        print(f"   总文件数: {len(pdf_files)}")
        print(f"   有效文件: {len(valid_files)}")
        print(f"   成功分析: {len(reports)}")
        print(f"   失败文件: {len(valid_files) - len(reports)}")
        print(f"   总耗时: {elapsed_time:.2f} 秒")
        print(f"   平均耗时: {elapsed_time/len(reports):.2f} 秒/文件" if reports else "N/A")
        print()
        
        # 风险统计
        if reports:
            risk_counts = {
                "极高": 0,
                "高": 0,
                "中": 0,
                "低": 0
            }
            
            for report in reports:
                risk_level = report.risk_assessment.risk_level.value
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            print(f"📈 风险分布:")
            for level, count in risk_counts.items():
                if count > 0:
                    percentage = (count / len(reports)) * 100
                    print(f"   {level}风险: {count} 个 ({percentage:.1f}%)")
            
            # 高风险公司列表
            high_risk_reports = [r for r in reports if r.risk_assessment.risk_level.value in ["高", "极高"]]
            if high_risk_reports:
                print(f"\n⚠️  高风险公司 ({len(high_risk_reports)} 个):")
                for report in high_risk_reports[:5]:  # 只显示前5个
                    print(f"   • {report.company_name} ({report.report_year}) - {report.risk_assessment.risk_level.value}风险")
                
                if len(high_risk_reports) > 5:
                    print(f"   ... 还有 {len(high_risk_reports) - 5} 个高风险公司")
            
            # 建议
            print(f"\n💡 建议:")
            if risk_counts["极高"] > 0:
                print(f"   • 发现 {risk_counts['极高']} 个极高风险公司，建议立即调查")
            if risk_counts["高"] > 0:
                print(f"   • 发现 {risk_counts['高']} 个高风险公司，建议谨慎投资")
            if risk_counts["中"] > 0:
                print(f"   • 发现 {risk_counts['中']} 个中风险公司，建议关注风险点")
            if risk_counts["低"] > 0:
                print(f"   • 发现 {risk_counts['低']} 个低风险公司，可以继续持有")
        
        print(f"\n📁 报告保存到: {args.output}")
        print(f"   单个报告: {args.output}/公司名_年份_analysis_时间戳.md")
        print(f"   批量摘要: {args.output}/batch_summary_时间戳.md")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 批量分析过程中出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())