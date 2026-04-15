#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心功能测试 - 简化版本
"""

import pytest
from datetime import datetime
from src.models.financial_data import (
    FinancialData, BalanceSheet, IncomeStatement, CashFlowStatement
)
from src.models.risk import Risk, RiskList, RiskLevel, RiskType
from src.core.indicator_calculator import calculate_indicators
from src.core.risk_detector import detect_risks
from src.core.report_generator import generate_report


def create_sample_financial_data():
    """创建示例财务数据"""
    balance = BalanceSheet(
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
        report_date=datetime(2023, 12, 31)
    )

    income = IncomeStatement(
        operating_revenue=800000.0,
        operating_cost=500000.0,
        gross_profit=300000.0,
        operating_profit=200000.0,
        total_profit=180000.0,
        net_profit=150000.0,
        selling_expense=50000.0,
        admin_expense=30000.0,
        financial_expense=20000.0,
        report_date=datetime(2023, 12, 31)
    )

    cash_flow = CashFlowStatement(
        operating_cash_inflow=300000.0,
        operating_cash_outflow=100000.0,
        net_operating_cash=200000.0,
        investing_cash_inflow=50000.0,
        investing_cash_outflow=150000.0,
        net_investing_cash=-100000.0,
        financing_cash_inflow=100000.0,
        financing_cash_outflow=150000.0,
        net_financing_cash=-50000.0,
        net_cash_increase=50000.0,
        report_date=datetime(2023, 12, 31)
    )

    financial_data = FinancialData(
        company_name="测试公司",
        report_year=2023,
        balance_sheet=balance,
        income_statement=income,
        cash_flow_statement=cash_flow,
        source_file="test.pdf",
        extraction_time=datetime.now()
    )

    return financial_data


class TestFinancialDataModels:
    """测试财务数据模型"""

    def test_create_balance_sheet(self):
        """测试创建资产负债表"""
        balance = BalanceSheet(
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
            report_date=datetime(2023, 12, 31)
        )

        assert balance.total_assets == 1000000.0
        assert balance.total_liabilities == 400000.0
        assert balance.total_equity == 600000.0
        assert balance.validate_balance() == True

    def test_create_income_statement(self):
        """测试创建利润表"""
        income = IncomeStatement(
            operating_revenue=800000.0,
            operating_cost=500000.0,
            gross_profit=300000.0,
            operating_profit=200000.0,
            total_profit=180000.0,
            net_profit=150000.0,
            selling_expense=50000.0,
            admin_expense=30000.0,
            financial_expense=20000.0,
            report_date=datetime(2023, 12, 31)
        )

        assert income.operating_revenue == 800000.0
        assert income.net_profit == 150000.0

    def test_create_cash_flow(self):
        """测试创建现金流量表"""
        cash_flow = CashFlowStatement(
            operating_cash_inflow=300000.0,
            operating_cash_outflow=100000.0,
            net_operating_cash=200000.0,
            investing_cash_inflow=50000.0,
            investing_cash_outflow=150000.0,
            net_investing_cash=-100000.0,
            financing_cash_inflow=100000.0,
            financing_cash_outflow=150000.0,
            net_financing_cash=-50000.0,
            net_cash_increase=50000.0,
            report_date=datetime(2023, 12, 31)
        )

        assert cash_flow.net_operating_cash == 200000.0

    def test_create_financial_data(self):
        """测试创建财务数据"""
        financial_data = create_sample_financial_data()
        assert financial_data.company_name == "测试公司"
        assert financial_data.report_year == 2023


class TestRiskModels:
    """测试风险模型"""

    def test_create_risk(self):
        """测试创建风险"""
        risk = Risk(
            risk_type=RiskType.FINANCIAL,
            risk_level=RiskLevel.HIGH,
            description="资产负债率过高",
            indicator_name="资产负债率",
            indicator_value=0.75,
            threshold=0.70,
            impact="财务风险较大",
            recommendation="优化资本结构"
        )

        assert risk.risk_type == RiskType.FINANCIAL
        assert risk.risk_level == RiskLevel.HIGH
        assert risk.description == "资产负债率过高"

    def test_risk_list(self):
        """测试风险列表"""
        risk1 = Risk(
            risk_type=RiskType.FINANCIAL,
            risk_level=RiskLevel.HIGH,
            description="风险1",
            indicator_name="指标1",
            indicator_value=0.8,
            threshold=0.7,
            impact="影响1",
            recommendation="建议1"
        )

        risk2 = Risk(
            risk_type=RiskType.OPERATION,
            risk_level=RiskLevel.MEDIUM,
            description="风险2",
            indicator_name="指标2",
            indicator_value=0.6,
            threshold=0.5,
            impact="影响2",
            recommendation="建议2"
        )

        risk_list = RiskList(
            company_name="测试公司",
            report_year=2023,
            risks=[risk1, risk2]
        )
        # 验证风险列表创建成功
        assert risk_list is not None
        assert len(risk_list.risks) == 2


class TestIndicatorCalculator:
    """测试指标计算器"""

    def test_calculate_indicators(self):
        """测试计算财务指标"""
        financial_data = create_sample_financial_data()
        indicators = calculate_indicators(financial_data)

        assert indicators is not None
        # 检查基本指标已计算
        assert hasattr(indicators, 'profitability')
        assert hasattr(indicators, 'solvency')

    def test_profitability_indicators(self):
        """测试盈利能力指标"""
        financial_data = create_sample_financial_data()
        indicators = calculate_indicators(financial_data)

        if indicators and hasattr(indicators, 'profitability'):
            # 毛利率 = 毛利润 / 营收 = 300000 / 800000 = 0.375
            assert indicators.profitability.gross_margin is not None


class TestRiskDetector:
    """测试风险识别器"""

    def test_detect_risks(self):
        """测试风险识别"""
        financial_data = create_sample_financial_data()
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)

        assert risk_list is not None
        # 风险列表应该有统计信息
        assert hasattr(risk_list, 'total_risks')


class TestReportGenerator:
    """测试报告生成器"""

    def test_generate_report(self):
        """测试生成报告"""
        financial_data = create_sample_financial_data()
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)

        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )

        assert report is not None
        assert len(report) > 0
        # 报告应包含公司信息
        assert "测试公司" in report or "2023" in report


class TestIntegration:
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 创建财务数据
        financial_data = create_sample_financial_data()
        assert financial_data is not None

        # 2. 计算指标
        indicators = calculate_indicators(financial_data)
        assert indicators is not None

        # 3. 识别风险
        risk_list = detect_risks(indicators)
        assert risk_list is not None

        # 4. 生成报告
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        assert report is not None
        assert len(report) > 100  # 报告应该有一定长度
