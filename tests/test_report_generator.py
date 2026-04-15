#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试报告生成器
"""

import pytest
from src.core.report_generator import generate_report
from src.core.indicator_calculator import calculate_indicators
from src.core.risk_detector import detect_risks


class TestReportGenerator:
    """测试报告生成器"""
    
    def test_generate_basic_report(self, sample_financial_data):
        """测试生成基本报告"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        assert report is not None
        assert len(report) > 0
    
    def test_report_contains_company_info(self, sample_financial_data):
        """测试报告包含公司信息"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告应包含公司名称和年度
        assert sample_financial_data.company_name in report
        assert sample_financial_data.report_year in report
    
    def test_report_contains_indicators(self, sample_financial_data):
        """测试报告包含财务指标"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告应包含主要指标
        assert "盈利能力" in report or "毛利率" in report
        assert "偿债能力" in report or "资产负债率" in report
    
    def test_report_contains_risks(self, sample_financial_data):
        """测试报告包含风险信息"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告应包含风险分析部分
        assert "风险" in report
    
    def test_report_markdown_format(self, sample_financial_data):
        """测试报告Markdown格式"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告应使用Markdown格式
        assert "#" in report  # 应有标题
        assert "\n" in report  # 应有换行
    
    def test_report_with_trend_analysis(self, sample_financial_data):
        """测试包含趋势分析的报告"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        # 创建模拟的趋势分析数据
        trend_analysis = {
            'revenue_trend': '上升',
            'profit_trend': '稳定',
            'growth_rate': 0.15
        }
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=trend_analysis,
            risk_list=risk_list
        )
        
        assert report is not None
        assert len(report) > 0
    
    def test_report_structure(self, sample_financial_data):
        """测试报告结构完整性"""
        indicators = calculate_indicators(sample_financial_data)
        risk_list = detect_risks(indicators)
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=risk_list
        )
        
        # 报告应包含主要章节
        # 1. 公司基本信息
        # 2. 财务指标分析
        # 3. 风险识别结果
        # 4. 综合评价
        
        assert len(report) > 500  # 报告应该有一定长度
    
    def test_report_with_no_risks(self, sample_financial_data):
        """测试无风险时的报告"""
        from src.models.risk import RiskList
        
        indicators = calculate_indicators(sample_financial_data)
        empty_risk_list = RiskList(risks=[])
        
        report = generate_report(
            indicators=indicators,
            trend_analysis=None,
            risk_list=empty_risk_list
        )
        
        # 即使无风险，报告也应正常生成
        assert report is not None
        assert len(report) > 0
