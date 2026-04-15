#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据模型
"""

import pytest
from datetime import datetime
from src.models.financial_data import (
    FinancialData, BalanceSheet, IncomeStatement, CashFlowStatement
)
from src.models.risk import Risk, RiskList, RiskLevel, RiskType


class TestBalanceSheet:
    """测试资产负债表模型"""

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

    def test_balance_validation(self):
        """测试资产负债表平衡验证"""
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

        # 验证资产负债表平衡
        assert balance.validate_balance() == True


class TestIncomeStatement:
    """测试利润表模型"""

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


class TestCashFlowStatement:
    """测试现金流量表模型"""

    def test_create_cash_flow(self):
        """测试创建现金流量表"""
        cash_flow = CashFlowStatement(
            net_operating_cash=200000.0,
            net_investing_cash=-100000.0,
            net_financing_cash=-50000.0,
            free_cash_flow=150000.0,
            net_cash_increase=50000.0,
            report_date=datetime(2023, 12, 31)
        )

        assert cash_flow.net_operating_cash == 200000.0
        assert cash_flow.free_cash_flow == 150000.0


class TestFinancialData:
    """测试财务数据模型"""

    def test_create_financial_data(self, sample_financial_data):
        """测试创建财务数据"""
        assert sample_financial_data.company_name == "测试公司"
        assert sample_financial_data.report_year == "2023"
        assert sample_financial_data.balance_sheet is not None
        assert sample_financial_data.income_statement is not None
        assert sample_financial_data.cash_flow_statement is not None


class TestRisk:
    """测试风险模型"""

    def test_create_risk(self):
        """测试创建风险"""
        risk = Risk(
            name="资产负债率过高",
            type=RiskType.FINANCIAL,
            level=RiskLevel.HIGH,
            description="资产负债率超过70%",
            suggestion="优化资本结构"
        )

        assert risk.name == "资产负债率过高"
        assert risk.type == RiskType.FINANCIAL
        assert risk.level == RiskLevel.HIGH

    def test_risk_level_comparison(self):
        """测试风险等级比较"""
        high_risk = Risk(
            name="高风险",
            type=RiskType.FINANCIAL,
            level=RiskLevel.HIGH,
            description="高风险描述"
        )

        low_risk = Risk(
            name="低风险",
            type=RiskType.FINANCIAL,
            level=RiskLevel.LOW,
            description="低风险描述"
        )

        assert high_risk.level.value > low_risk.level.value


class TestRiskList:
    """测试风险列表模型"""

    def test_create_risk_list(self):
        """测试创建风险列表"""
        risks = [
            Risk(
                name="风险1",
                type=RiskType.FINANCIAL,
                level=RiskLevel.HIGH,
                description="描述1"
            ),
            Risk(
                name="风险2",
                type=RiskType.OPERATIONAL,
                level=RiskLevel.MEDIUM,
                description="描述2"
            )
        ]

        risk_list = RiskList(risks=risks)

        assert risk_list.total_risks == 2
        assert risk_list.high_risks == 1
        assert risk_list.medium_risks == 1
        assert risk_list.low_risks == 0

    def test_add_risk(self):
        """测试添加风险"""
        risk_list = RiskList(risks=[])

        risk = Risk(
            name="新风险",
            type=RiskType.FINANCIAL,
            level=RiskLevel.HIGH,
            description="新风险描述"
        )

        risk_list.add_risk(risk)

        assert risk_list.total_risks == 1
        assert risk_list.high_risks == 1
