#!/usr/bin/env python
"""
高级使用示例
"""

import sys
from pathlib import Path
from typing import List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.analyzer import FinancialFraudAnalyzer
from src.core.data_extractor import PDFDataExtractor
from src.core.fraud_detector import FraudDetector
from src.core.risk_assessor import RiskAssessor
from src.core.report_generator import ReportGenerator
from src.models.financial_data import FinancialData


def main():
    """高级使用示例 - 自定义分析流程"""
    print("=" * 60)
    print("财报造假分析系统 - 高级使用示例")
    print("=" * 60)
    
    # 示例PDF文件路径
    pdf_file = "path/to/your/financial_report.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        print("\n请将您的PDF财报文件放在项目目录下并修改pdf_file变量")
        return
    
    try:
        # 1. 创建各个组件
        print("1. 初始化组件...")
        data_extractor = PDFDataExtractor()
        fraud_detector = FraudDetector()
        risk_assessor = RiskAssessor()
        report_generator = ReportGenerator(output_dir="reports")
        
        # 2. 提取财务数据
        print("2. 提取财务数据...")
        financial_data = data_extractor.extract_from_pdf(pdf_file)
        
        # 自定义公司信息
        financial_data.company_name = "自定义公司名称"
        financial_data.stock_code = "000001"
        financial_data.report_year = 2025
        financial_data.auditor = "自定义会计师事务所"
        financial_data.audit_opinion = "标准无保留意见"
        
        print(f"   公司: {financial_data.company_name}")
        print(f"   股票代码: {financial_data.stock_code}")
        print(f"   报告年度: {financial_data.report_year}")
        print(f"   审计师: {financial_data.auditor}")
        print(f"   审计意见: {financial_data.audit_opinion}")
        
        # 3. 手动设置财务数据（示例）
        print("3. 设置财务数据...")
        current = financial_data.current_year
        
        # 利润表数据
        current.operating_revenue = 1000000000  # 10亿元
        current.operating_cost = 700000000  # 7亿元
        current.gross_profit = 300000000  # 3亿元
        current.operating_expenses = 100000000  # 1亿元
        current.operating_profit = 200000000  # 2亿元
        current.net_profit = 150000000  # 1.5亿元
        current.net_profit_attributable = 150000000  # 归母净利润1.5亿元
        
        # 现金流量表数据
        current.net_cash_flow_operating = 180000000  # 1.8亿元
        current.cash_from_sales = 950000000  # 9.5亿元
        
        # 资产负债表数据
        current.total_assets = 2000000000  # 20亿元
        current.total_liabilities = 800000000  # 8亿元
        current.total_equity = 1200000000  # 12亿元
        current.current_assets = 800000000  # 8亿元
        current.current_liabilities = 400000000  # 4亿元
        current.inventory = 200000000  # 2亿元
        current.accounts_receivable = 300000000  # 3亿元
        
        # 计算财务比率
        current.calculate_ratios()
        
        print(f"   营业收入: {current.operating_revenue:,.0f} 元")
        print(f"   净利润: {current.net_profit:,.0f} 元")
        print(f"   毛利率: {current.gross_margin:.2f}%")
        print(f"   净利率: {current.net_margin:.2f}%")
        print(f"   资产负债率: {current.debt_ratio:.2f}%")
        
        # 4. 添加历史数据
        print("4. 添加历史数据...")
        prev_year = financial_data.current_year.__class__()
        prev_year.operating_revenue = 900000000  # 9亿元
        prev_year.net_profit = 140000000  # 1.4亿元
        prev_year.net_cash_flow_operating = 170000000  # 1.7亿元
        financial_data.historical_data[2024] = prev_year
        
        # 5. 检测造假模式
        print("5. 检测造假模式...")
        fraud_patterns = fraud_detector.detect_fraud_patterns(financial_data)
        print(f"   检测到 {len(fraud_patterns)} 个造假模式")
        
        for pattern in fraud_patterns:
            print(f"   • {pattern.name}: {pattern.risk_level.value}风险")
            for indicator in pattern.indicators:
                print(f"     - {indicator.name}: {indicator.description}")
        
        # 6. 评估风险
        print("6. 评估风险...")
        risk_assessment = risk_assessor.assess_risk(fraud_patterns, financial_data)
        print(f"   风险评分: {risk_assessment.total_score:.1f}/50")
        print(f"   风险等级: {risk_assessment.risk_level.value}")
        
        # 7. 生成投资建议
        print("7. 生成投资建议...")
        investment_recommendation = risk_assessor.generate_investment_recommendation(risk_assessment)
        print(f"   投资建议: {investment_recommendation}")
        
        # 8. 生成报告
        print("8. 生成报告...")
        
        # 创建财务分析结果
        from src.models.report_model import FinancialAnalysis
        financial_analysis = FinancialAnalysis()
        
        # 设置财务比率
        financial_analysis.profitability_ratios = {
            "毛利率": current.gross_margin,
            "净利率": current.net_margin,
            "净资产收益率": current.roe,
            "总资产收益率": current.roa
        }
        
        financial_analysis.solvency_ratios = {
            "资产负债率": current.debt_ratio,
            "流动比率": current.current_ratio,
            "速动比率": current.quick_ratio
        }
        
        # 计算增长率
        revenue_growth = ((current.operating_revenue - prev_year.operating_revenue) / 
                         abs(prev_year.operating_revenue)) * 100
        profit_growth = ((current.net_profit - prev_year.net_profit) / 
                        abs(prev_year.net_profit)) * 100
        
        financial_analysis.growth_ratios = {
            "营业收入增长率": revenue_growth,
            "净利润增长率": profit_growth
        }
        
        # 生成报告
        report = report_generator.generate_report(
            financial_data, financial_analysis, risk_assessment, fraud_patterns
        )
        
        # 保存报告
        report_path = report_generator.save_report(report, "markdown")
        
        print("\n✅ 分析完成!")
        print(f"报告已保存: {report_path}")
        print(f"报告ID: {report.report_id}")
        
        # 9. 打印报告摘要
        print("\n" + "=" * 60)
        print("报告摘要")
        print("=" * 60)
        report_generator.print_report_summary(report)
        
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()


def batch_analysis_example():
    """批量分析示例"""
    print("\n" + "=" * 60)
    print("批量分析示例")
    print("=" * 60)
    
    # 创建分析器
    analyzer = FinancialFraudAnalyzer(output_dir="batch_reports")
    
    # 示例文件列表
    pdf_files = [
        "path/to/report1.pdf",
        "path/to/report2.pdf",
        "path/to/report3.pdf"
    ]
    
    # 过滤存在的文件
    existing_files = [f for f in pdf_files if Path(f).exists()]
    
    if not existing_files:
        print("❌ 没有找到PDF文件")
        print("\n请将PDF文件放在指定路径或修改文件列表")
        return
    
    print(f"找到 {len(existing_files)} 个PDF文件")
    
    try:
        # 批量分析
        reports = analyzer.batch_analyze(existing_files, "batch_reports")
        
        print(f"\n✅ 批量分析完成!")
        print(f"成功分析 {len(reports)} 个文件")
        
        # 统计风险分布
        risk_distribution = {}
        for report in reports:
            risk_level = report.risk_assessment.risk_level.value
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        print("\n风险分布:")
        for level, count in risk_distribution.items():
            percentage = (count / len(reports)) * 100
            print(f"  {level}风险: {count} 个 ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"\n❌ 批量分析过程中出错: {e}")


if __name__ == "__main__":
    main()
    
    # 取消注释以下行以运行批量分析示例
    # batch_analysis_example()