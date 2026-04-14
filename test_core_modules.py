"""
核心功能模块测试脚本

用于测试财报分析系统的核心功能模块是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.models.financial_data import (
    BalanceSheet,
    IncomeStatement,
    CashFlowStatement,
    FinancialData
)
from src.core.indicator_calculator import IndicatorCalculator
from src.core.risk_detector import RiskDetector
from src.core.report_generator import ReportGenerator
from datetime import datetime


def test_indicator_calculator():
    """测试指标计算器"""
    print("\n" + "="*60)
    print("测试指标计算器")
    print("="*60)

    # 创建测试数据
    balance_sheet = BalanceSheet(
        total_assets=1000000.0,
        current_assets=500000.0,
        non_current_assets=500000.0,
        cash=200000.0,
        accounts_receivable=100000.0,
        inventory=150000.0,
        total_liabilities=400000.0,
        current_liabilities=200000.0,
        non_current_liabilities=200000.0,
        total_equity=600000.0,
        report_date=datetime.now()
    )

    income_statement = IncomeStatement(
        operating_revenue=800000.0,
        operating_cost=500000.0,
        gross_profit=300000.0,
        operating_profit=200000.0,
        total_profit=180000.0,
        net_profit=150000.0,
        selling_expense=50000.0,
        admin_expense=30000.0,
        financial_expense=20000.0,
        report_date=datetime.now()
    )

    cash_flow_statement = CashFlowStatement(
        operating_cash_inflow=900000.0,
        operating_cash_outflow=700000.0,
        net_operating_cash=200000.0,
        investing_cash_inflow=50000.0,
        investing_cash_outflow=100000.0,
        net_investing_cash=-50000.0,
        financing_cash_inflow=100000.0,
        financing_cash_outflow=80000.0,
        net_financing_cash=20000.0,
        net_cash_increase=170000.0,
        report_date=datetime.now()
    )

    financial_data = FinancialData(
        company_name="测试公司",
        report_year=2023,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        cash_flow_statement=cash_flow_statement,
        source_file="test.pdf",
        extraction_time=datetime.now()
    )

    # 计算指标
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_indicators(financial_data)

    print(f"\n公司名称: {indicators.company_name}")
    print(f"报告年度: {indicators.report_year}")
    print(f"\n盈利能力指标:")
    print(f"  毛利率: {indicators.profitability.gross_margin:.2f}%")
    print(f"  净利率: {indicators.profitability.net_margin:.2f}%")
    print(f"  ROE: {indicators.profitability.roe:.2f}%")
    print(f"  ROA: {indicators.profitability.roa:.2f}%")

    print(f"\n偿债能力指标:")
    print(f"  资产负债率: {indicators.solvency.debt_ratio:.2f}%")
    print(f"  流动比率: {indicators.solvency.current_ratio:.2f}")
    print(f"  速动比率: {indicators.solvency.quick_ratio:.2f}")

    print(f"\n运营能力指标:")
    print(f"  存货周转率: {indicators.operation.inventory_turnover:.2f}")
    print(f"  应收账款周转率: {indicators.operation.receivable_turnover:.2f}")

    print(f"\n成长能力指标:")
    print(f"  营收增长率: {indicators.growth.revenue_growth:.2f}%")
    print(f"  净利润增长率: {indicators.growth.profit_growth:.2f}%")

    print(f"\n现金流指标:")
    print(f"  自由现金流: {indicators.cashflow.free_cash_flow:.2f}")

    return indicators


def test_risk_detector(indicators):
    """测试风险识别器"""
    print("\n" + "="*60)
    print("测试风险识别器")
    print("="*60)

    detector = RiskDetector()
    risk_list = detector.detect_risks(indicators)

    print(f"\n风险总数: {risk_list.total_risks}")
    print(f"高风险: {risk_list.high_risks}")
    print(f"中风险: {risk_list.medium_risks}")
    print(f"低风险: {risk_list.low_risks}")

    if risk_list.risks:
        print("\n风险详情:")
        for i, risk in enumerate(risk_list.risks, 1):
            print(f"\n{i}. {risk.description}")
            print(f"   类型: {risk.risk_type.value}")
            print(f"   等级: {risk.risk_level.value}")
            print(f"   建议: {risk.recommendation}")

    return risk_list


def test_report_generator(indicators, risk_list):
    """测试报告生成器"""
    print("\n" + "="*60)
    print("测试报告生成器")
    print("="*60)

    generator = ReportGenerator()
    report = generator.generate_report(indicators, risk_list=risk_list)

    # 保存报告
    output_path = "test_report.md"
    generator.save_report(report, output_path)

    print(f"\n报告已生成: {output_path}")
    print(f"报告长度: {len(report)} 字符")

    return report


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("财报分析系统核心功能模块测试")
    print("="*60)

    # 设置日志
    setup_logger(level='INFO', console_output=True, file_output=False)

    try:
        # 测试指标计算器
        indicators = test_indicator_calculator()

        # 测试风险识别器
        risk_list = test_risk_detector(indicators)

        # 测试报告生成器
        report = test_report_generator(indicators, risk_list)

        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ 测试失败: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
