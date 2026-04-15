#!/usr/bin/env python
"""
财报造假分析命令行工具
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.analyzer import FinancialFraudAnalyzer
from src.utils.file_utils import validate_pdf_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="财报造假分析工具 - 分析上市公司财务报告，识别财务风险和造假迹象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s report.pdf
  %(prog)s report.pdf --company "英洛华科技" --year 2025
  %(prog)s report.pdf --output custom_reports/
  %(prog)s report.pdf --format json
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="要分析的PDF财报文件路径"
    )
    
    parser.add_argument(
        "--company", "-c",
        help="公司名称（可选）",
        default=""
    )
    
    parser.add_argument(
        "--year", "-y",
        type=int,
        help="报告年度（可选）",
        default=0
    )
    
    parser.add_argument(
        "--output", "-o",
        help="报告输出目录（默认: reports）",
        default="reports"
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
        "--version",
        action="version",
        version="财报造假分析工具 v2.0.0"
    )
    
    args = parser.parse_args()
    
    # 验证PDF文件
    print("验证PDF文件...")
    validation_result = validate_pdf_file(args.pdf_file)
    
    if not validation_result["valid"]:
        print("❌ PDF文件验证失败:")
        for error in validation_result["errors"]:
            print(f"   - {error}")
        sys.exit(1)
    
    print("✅ PDF文件验证通过")
    print(f"   文件: {validation_result['file_info']['name']}")
    print(f"   大小: {validation_result['file_info']['size_mb']:.2f} MB")
    print()
    
    try:
        # 创建分析器
        analyzer = FinancialFraudAnalyzer(output_dir=args.output)
        
        # 分析财报
        print("开始分析财报...")
        report = analyzer.analyze(
            pdf_path=args.pdf_file,
            company_name=args.company,
            report_year=args.year
        )
        
        # 保存报告
        report_path = analyzer.report_generator.save_report(report, args.format)
        print(f"\n✅ 分析完成！报告已保存到: {report_path}")
        
        # 显示报告路径
        print(f"\n报告文件:")
        print(f"  📄 {report_path}")
        
        # 显示风险摘要
        print(f"\n风险摘要:")
        print(f"  ⚠️  风险等级: {report.risk_assessment.risk_level.value}")
        print(f"  📊 风险评分: {report.risk_assessment.total_score:.1f}/50")
        print(f"  🔍 检测到造假模式: {len(report.risk_assessment.fraud_patterns)} 个")
        
        # 显示高风险模式
        high_risk_patterns = [p for p in report.risk_assessment.fraud_patterns 
                             if p.risk_level.value in ["高", "极高"]]
        if high_risk_patterns:
            print(f"\n高风险模式:")
            for pattern in high_risk_patterns:
                print(f"  • {pattern.name} ({pattern.risk_level.value}风险)")
        
        # 显示投资建议
        print(f"\n投资建议:")
        print(f"  💡 {report.investment_recommendation}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())