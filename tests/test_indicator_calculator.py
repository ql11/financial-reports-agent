#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试指标计算器
"""

import pytest
from src.core.indicator_calculator import calculate_indicators
from src.models.financial_data import FinancialData


class TestIndicatorCalculator:
    """测试指标计算器"""
    
    def test_calculate_profitability_indicators(self, sample_financial_data):
        """测试盈利能力指标计算"""
        indicators = calculate_indicators(sample_financial_data)
        
        assert indicators is not None
        # 毛利率 = 毛利润 / 营收 = 300000 / 800000 = 0.375
        assert abs(indicators.gross_profit_margin - 0.375) < 0.01
        # 净利率 = 净利润 / 营收 = 150000 / 800000 = 0.1875
        assert abs(indicators.net_profit_margin - 0.1875) < 0.01
    
    def test_calculate_solvency_indicators(self, sample_financial_data):
        """测试偿债能力指标计算"""
        indicators = calculate_indicators(sample_financial_data)
        
        assert indicators is not None
        # 资产负债率 = 总负债 / 总资产 = 400000 / 1000000 = 0.4
        assert abs(indicators.debt_ratio - 0.4) < 0.01
        # 流动比率 = 流动资产 / 流动负债 = 500000 / 200000 = 2.5
        assert abs(indicators.current_ratio - 2.5) < 0.01
        # 速动比率 = (流动资产 - 存货) / 流动负债 = (500000 - 150000) / 200000 = 1.75
        assert abs(indicators.quick_ratio - 1.75) < 0.01
    
    def test_calculate_operational_indicators(self, sample_financial_data):
        """测试运营能力指标计算"""
        indicators = calculate_indicators(sample_financial_data)
        
        assert indicators is not None
        # 存货周转率 = 营业成本 / 存货 = 500000 / 150000 ≈ 3.33
        assert indicators.inventory_turnover is not None
        # 应收账款周转率 = 营收 / 应收账款 = 800000 / 100000 = 8.0
        assert abs(indicators.accounts_receivable_turnover - 8.0) < 0.01
    
    def test_calculate_roe_roa(self, sample_financial_data):
        """测试ROE和ROA计算"""
        indicators = calculate_indicators(sample_financial_data)
        
        assert indicators is not None
        # ROE = 净利润 / 所有者权益 = 150000 / 600000 = 0.25
        assert abs(indicators.roe - 0.25) < 0.01
        # ROA = 净利润 / 总资产 = 150000 / 1000000 = 0.15
        assert abs(indicators.roa - 0.15) < 0.01
    
    def test_calculate_cash_flow_indicators(self, sample_financial_data):
        """测试现金流指标计算"""
        indicators = calculate_indicators(sample_financial_data)
        
        assert indicators is not None
        # 自由现金流
        assert indicators.free_cash_flow == 150000.0
    
    def test_calculate_with_zero_revenue(self, sample_balance_sheet, sample_cash_flow):
        """测试营收为0的情况"""
        from src.models.financial_data import IncomeStatement
        
        # 创建营收为0的利润表
        income_statement = IncomeStatement(
            revenue=0.0,
            cost_of_goods_sold=0.0,
            gross_profit=0.0,
            operating_profit=0.0,
            net_profit=0.0
        )
        
        financial_data = FinancialData(
            company_name="零营收公司",
            report_year="2023",
            balance_sheet=sample_balance_sheet,
            income_statement=income_statement,
            cash_flow_statement=sample_cash_flow
        )
        
        # 应该能够处理零营收情况而不报错
        indicators = calculate_indicators(financial_data)
        assert indicators is not None
    
    def test_indicator_completeness(self, sample_financial_data):
        """测试指标完整性"""
        indicators = calculate_indicators(sample_financial_data)
        
        # 检查所有主要指标都已计算
        assert indicators.gross_profit_margin is not None
        assert indicators.net_profit_margin is not None
        assert indicators.roe is not None
        assert indicators.roa is not None
        assert indicators.debt_ratio is not None
        assert indicators.current_ratio is not None
        assert indicators.quick_ratio is not None
