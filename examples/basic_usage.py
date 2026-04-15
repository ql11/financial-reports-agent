#!/usr/bin/env python
"""
基础使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.analyzer import FinancialFraudAnalyzer


def main():
    """基础使用示例"""
    print("=" * 60)
    print("财报造假分析系统 - 基础使用示例")
    print("=" * 60)
    
    # 创建分析器
    analyzer = FinancialFraudAnalyzer(output_dir="reports")
    
    # 示例PDF文件路径
    # 注意：这里使用示例文件，实际使用时请替换为真实的PDF文件路径
    pdf_file = "path/to/your/financial_report.pdf"
    
    # 检查文件是否存在
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        print("\n请按照以下步骤使用:")
        print("1. 将您的PDF财报文件放在项目目录下")
        print("2. 修改pdf_file变量为您的文件路径")
        print("3. 运行此示例")
        print("\n或者使用命令行工具:")
        print("  python scripts/analyze_fraud.py your_report.pdf")
        return
    
    try:
        # 分析财报
        print(f"分析文件: {Path(pdf_file).name}")
        print("-" * 60)
        
        report = analyzer.analyze(
            pdf_path=pdf_file,
            company_name="示例公司",
            report_year=2025
        )
        
        print("\n✅ 分析完成!")
        print(f"报告已保存到: reports/目录")
        print(f"报告ID: {report.report_id}")
        
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        print("\n可能的原因:")
        print("1. PDF文件格式不正确")
        print("2. 文件损坏或受密码保护")
        print("3. 缺少必要的依赖库")
        print("\n解决方案:")
        print("1. 确保PDF文件是有效的财报文件")
        print("2. 安装依赖: pip install -r requirements.txt")
        print("3. 检查文件权限")


if __name__ == "__main__":
    main()