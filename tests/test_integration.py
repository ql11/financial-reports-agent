#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
集成测试 - 测试完整的工作流程
"""

import pytest
from pathlib import Path
from src.core.indicator_calculator import calculate_indicators
from src.core.risk_detector import detect_risks
from src.core.report_generator import generate_report
from src.utils.file_manager import FileManager


class TestIntegration:
    """集成测试"""
    
    def test_full_analysis_workflow(self, sample_financial_data):
        """测试完整分析工作流程"""
        # 1. 计算指标
        indicators = calculate_indicators(sample_financial_data)
        assert indicators is not None
        
        # 2. 识别风险
        risk_list = detect_risks(indicators)
        assert risk_list is not None
        
        # 3. 生成报告
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        assert report is not None
        assert len(report) > 0
    
    def test_save_and_load_report(self, sample_financial_data, tmp_path):
        """测试保存和加载报告"""
        # 生成报告
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 保存报告
        fm = FileManager()
        report_file = tmp_path / "test_report.md"
        fm.write_file(str(report_file), report)
        
        # 验证文件已创建
        assert report_file.exists()
        
        # 加载报告
        loaded_report = fm.read_file(str(report_file))
        assert loaded_report == report
    
    def test_multiple_companies_analysis(self):
        """测试多公司分析"""
        from src.models.financial_data import (
            FinancialData, BalanceSheet, IncomeStatement, CashFlowStatement
        )
        
        companies = []
        
        # 创建多个公司的测试数据
        for i in range(3):
            balance = BalanceSheet(
                total_assets=1000000.0 * (i + 1),
                total_liabilities=400000.0 * (i + 1),
                total_equity=600000.0 * (i + 1),
                current_assets=500000.0 * (i + 1),
                current_liabilities=200000.0 * (i + 1),
                inventory=150000.0 * (i + 1),
                accounts_receivable=100000.0 * (i + 1),
                cash=200000.0 * (i + 1)
            )
            
            income = IncomeStatement(
                revenue=800000.0 * (i + 1),
                cost_of_goods_sold=500000.0 * (i + 1),
                gross_profit=300000.0 * (i + 1),
                operating_profit=200000.0 * (i + 1),
                net_profit=150000.0 * (i + 1)
            )
            
            cash_flow = CashFlowStatement(
                operating_cash_flow=200000.0 * (i + 1),
                investing_cash_flow=-100000.0 * (i + 1),
                financing_cash_flow=-50000.0 * (i + 1),
                free_cash_flow=150000.0 * (i + 1)
            )
            
            financial_data = FinancialData(
                company_name=f"公司{i+1}",
                report_year="2023",
                balance_sheet=balance,
                income_statement=income,
                cash_flow_statement=cash_flow
            )
            
            companies.append(financial_data)
        
        # 分析所有公司
        results = []
        for company_data in companies:
            indicators = calculate_indicators(company_data)
            risk_list = detect_risks(indicators)
            report = generate_report(
                indicators=indicators,
                trend_analysis=None,
                risk_list=risk_list
            )
            results.append({
                'company': company_data.company_name,
                'indicators': indicators,
                'risks': risk_list,
                'report': report
            })
        
        # 验证所有公司都成功分析
        assert len(results) == 3
        for result in results:
            assert result['indicators'] is not None
            assert result['risks'] is not None
            assert result['report'] is not None
    
    def test_data_consistency(self, sample_financial_data):
        """测试数据一致性"""
        # 多次计算应该得到相同结果
        indicators1 = calculate_indicators(sample_financial_data)
        indicators2 = calculate_indicators(sample_financial_data)
        
        assert indicators1.gross_profit_margin == indicators2.gross_profit_margin
        assert indicators1.net_profit_margin == indicators2.net_profit_margin
        assert indicators1.roe == indicators2.roe
        assert indicators1.roa == indicators2.roa
    
    def test_edge_case_zero_values(self):
        """测试边界情况 - 零值"""
        from src.models.financial_data import (
            FinancialData, BalanceSheet, IncomeStatement, CashFlowStatement
        )
        
        # 创建包含零值的数据
        balance = BalanceSheet(
            total_assets=0.0,
            total_liabilities=0.0,
            total_equity=0.0,
            current_assets=0.0,
            current_liabilities=0.0,
            inventory=0.0,
            accounts_receivable=0.0,
            cash=0.0
        )
        
        income = IncomeStatement(
            revenue=0.0,
            cost_of_goods_sold=0.0,
            gross_profit=0.0,
            operating_profit=0.0,
            net_profit=0.0
        )
        
        cash_flow = CashFlowStatement(
            operating_cash_flow=0.0,
            investing_cash_flow=0.0,
            financing_cash_flow=0.0,
            free_cash_flow=0.0
        )
        
        financial_data = FinancialData(
            company_name="零值公司",
            report_year="2023",
            balance_sheet=balance,
            income_statement=income,
            cash_flow_statement=cash_flow
        )
        
        # 应该能够处理零值而不崩溃
        try:
            indicators = calculate_indicators(financial_data)
            # 即使数据为零，也应该返回结果
            assert indicators is not None
        except Exception as e:
            # 如果抛出异常，应该是可预期的异常
            pytest.fail(f"不应该抛出异常: {e}")
    
    def test_report_quality(self, sample_financial_data):
        """测试报告质量"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告质量检查
        # 1. 长度合理
        assert len(report) > 500
        
        # 2. 包含必要信息
        assert sample_financial_data.company_name in report
        assert sample_financial_data.report_year in report
        
        # 3. 格式正确
        assert "#" in report  # Markdown标题
        assert "\n" in report  # 有换行
