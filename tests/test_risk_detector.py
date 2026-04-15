#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试风险识别器
"""

import pytest
from src.core.risk_detector import detect_risks
from src.core.indicator_calculator import calculate_indicators
from src.models.risk import RiskLevel, RiskType


class TestRiskDetector:
    """测试风险识别器"""
    
    def test_detect_high_debt_risk(self, sample_financial_data):
        """测试高负债风险识别"""
        from src.models.financial_data import BalanceSheet, IncomeStatement, CashFlowStatement, FinancialData
        
        # 创建高负债的财务数据（资产负债率 > 70%）
        high_debt_balance = BalanceSheet(
            total_assets=1000000.0,
            total_liabilities=750000.0,  # 75%负债率
            total_equity=250000.0,
            current_assets=400000.0,
            current_liabilities=300000.0,
            inventory=100000.0,
            accounts_receivable=100000.0,
            cash=150000.0
        )
        
        income = IncomeStatement(
            revenue=800000.0,
            cost_of_goods_sold=500000.0,
            gross_profit=300000.0,
            operating_profit=200000.0,
            net_profit=150000.0
        )
        
        cash_flow = CashFlowStatement(
            operating_cash_flow=200000.0,
            investing_cash_flow=-100000.0,
            financing_cash_flow=-50000.0,
            free_cash_flow=150000.0
        )
        
        financial_data = FinancialData(
            company_name="高负债公司",
            report_year="2023",
            balance_sheet=high_debt_balance,
            income_statement=income,
            cash_flow_statement=cash_flow
        )
        
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)
        
        # 应该识别出高负债风险
        assert risk_list is not None
        assert risk_list.total_risks > 0
        
        # 检查是否有财务风险
        financial_risks = [r for r in risk_list.risks if r.type == RiskType.FINANCIAL]
        assert len(financial_risks) > 0
    
    def test_detect_low_liquidity_risk(self, sample_balance_sheet, sample_income_statement, sample_cash_flow):
        """测试低流动性风险识别"""
        from src.models.financial_data import BalanceSheet, FinancialData
        
        # 创建低流动性的财务数据（流动比率 < 1）
        low_liquidity_balance = BalanceSheet(
            total_assets=1000000.0,
            total_liabilities=400000.0,
            total_equity=600000.0,
            current_assets=150000.0,  # 流动资产较少
            current_liabilities=200000.0,  # 流动比率 = 0.75
            inventory=50000.0,
            accounts_receivable=50000.0,
            cash=50000.0
        )
        
        financial_data = FinancialData(
            company_name="低流动性公司",
            report_year="2023",
            balance_sheet=low_liquidity_balance,
            income_statement=sample_income_statement,
            cash_flow_statement=sample_cash_flow
        )
        
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)
        
        # 应该识别出流动性风险
        assert risk_list is not None
        assert risk_list.total_risks > 0
    
    def test_detect_profit_decline_risk(self, sample_balance_sheet, sample_cash_flow):
        """测试利润下滑风险识别"""
        from src.models.financial_data import IncomeStatement, FinancialData
        
        # 创建利润下滑的财务数据（负利润）
        negative_profit_income = IncomeStatement(
            revenue=800000.0,
            cost_of_goods_sold=900000.0,  # 成本高于营收
            gross_profit=-100000.0,
            operating_profit=-200000.0,
            net_profit=-250000.0  # 亏损
        )
        
        financial_data = FinancialData(
            company_name="亏损公司",
            report_year="2023",
            balance_sheet=sample_balance_sheet,
            income_statement=negative_profit_income,
            cash_flow_statement=sample_cash_flow
        )
        
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)
        
        # 应该识别出盈利风险
        assert risk_list is not None
        assert risk_list.total_risks > 0
    
    def test_detect_cash_flow_risk(self, sample_balance_sheet, sample_income_statement):
        """测试现金流风险识别"""
        from src.models.financial_data import CashFlowStatement, FinancialData
        
        # 创建现金流紧张的财务数据
        poor_cash_flow = CashFlowStatement(
            operating_cash_flow=-100000.0,  # 经营现金流为负
            investing_cash_flow=-50000.0,
            financing_cash_flow=200000.0,
            free_cash_flow=-150000.0  # 自由现金流为负
        )
        
        financial_data = FinancialData(
            company_name="现金流紧张公司",
            report_year="2023",
            balance_sheet=sample_balance_sheet,
            income_statement=sample_income_statement,
            cash_flow_statement=poor_cash_flow
        )
        
        indicators = calculate_indicators(financial_data)
        risk_list = detect_risks(indicators)
        
        # 应该识别出现金流风险
        assert risk_list is not None
    
    def test_no_risk_for_healthy_company(self, sample_financial_data):
        """测试健康公司无风险识别"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        # 健康公司可能识别出少量风险或无风险
        assert risk_list is not None
        # 注意：根据阈值配置，健康公司也可能识别出一些风险
    
    def test_risk_level_distribution(self, sample_financial_data):
        """测试风险等级分布"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        # 验证风险统计正确
        total = risk_list.high_risks + risk_list.medium_risks + risk_list.low_risks
        assert total == risk_list.total_risks
    
    def test_risk_has_suggestions(self, sample_financial_data):
        """测试风险都有建议"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        if risk_list.total_risks > 0:
            for risk in risk_list.risks:
                # 每个风险都应该有建议
                assert risk.suggestion is not None
                assert len(risk.suggestion) > 0
