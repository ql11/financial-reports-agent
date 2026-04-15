"""
财报造假分析器 - 主分析器
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.financial_data import FinancialData, FinancialStatement
from ..models.fraud_indicators import FraudPattern
from ..models.report_model import AnalysisReport, FinancialAnalysis, RiskAssessment
from .data_extractor import PDFDataExtractor
from .fraud_detector import FraudDetector
from .risk_assessor import RiskAssessor
from .report_generator import ReportGenerator


class FinancialFraudAnalyzer:
    """财报造假分析器"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.data_extractor = PDFDataExtractor()
        self.fraud_detector = FraudDetector()
        self.risk_assessor = RiskAssessor()
        self.report_generator = ReportGenerator(output_dir)
        
    def analyze(self, pdf_path: str, company_name: str = "", report_year: int = 0) -> AnalysisReport:
        """分析财报文件
        
        Args:
            pdf_path: PDF文件路径
            company_name: 公司名称（可选）
            report_year: 报告年度（可选）
            
        Returns:
            AnalysisReport: 分析报告
        """
        print("=" * 80)
        print("开始财报造假分析")
        print("=" * 80)
        
        # 1. 提取财务数据
        print("1. 提取财务数据...")
        financial_data = self.data_extractor.extract_from_pdf(pdf_path)
        
        # 更新公司名称和报告年度（如果提供）
        if company_name:
            financial_data.company_name = company_name
        if report_year:
            financial_data.report_year = report_year
        
        print(f"   公司: {financial_data.company_name}")
        print(f"   年度: {financial_data.report_year}")
        print(f"   审计师: {financial_data.auditor}")
        print(f"   审计意见: {financial_data.audit_opinion}")
        print()
        
        # 2. 进行财务分析
        print("2. 进行财务分析...")
        financial_analysis = self._analyze_financials(financial_data)
        
        # 3. 检测造假模式
        print("3. 检测造假模式...")
        fraud_patterns = self.fraud_detector.detect_fraud_patterns(financial_data)
        print(f"   检测到 {len(fraud_patterns)} 个造假模式")
        for pattern in fraud_patterns:
            pattern.calculate_score()
            print(f"   - {pattern.name}: {pattern.risk_level.value}风险")
        print()
        
        # 4. 评估风险
        print("4. 评估风险...")
        risk_assessment = self.risk_assessor.assess_risk(fraud_patterns, financial_data)
        print(f"   风险评分: {risk_assessment.total_score:.1f}/50")
        print(f"   风险等级: {risk_assessment.risk_level.value}")
        print()
        
        # 5. 生成报告
        print("5. 生成分析报告...")
        report = self.report_generator.generate_report(
            financial_data, financial_analysis, risk_assessment, fraud_patterns
        )
        
        # 6. 保存报告
        report_path = self.report_generator.save_report(report, "markdown")
        print(f"   报告已保存: {report_path}")
        print()
        
        # 7. 打印摘要
        self.report_generator.print_report_summary(report)
        
        return report
    
    def _analyze_financials(self, financial_data: FinancialData) -> FinancialAnalysis:
        """进行财务分析"""
        analysis = FinancialAnalysis()
        
        # 计算财务比率
        current = financial_data.current_year
        
        # 盈利能力比率
        analysis.profitability_ratios = {
            "毛利率": current.gross_margin,
            "净利率": current.net_margin,
            "净资产收益率": current.roe,
            "总资产收益率": current.roa
        }
        
        # 偿债能力比率
        analysis.solvency_ratios = {
            "资产负债率": current.debt_ratio,
            "流动比率": current.current_ratio,
            "速动比率": current.quick_ratio
        }
        
        # 运营能力比率
        analysis.operation_ratios = {
            "存货周转率": current.inventory_turnover,
            "应收账款周转率": current.receivables_turnover,
            "总资产周转率": current.total_asset_turnover
        }
        
        # 成长能力比率
        analysis.growth_ratios = {
            "营业收入增长率": financial_data.get_growth_rate("operating_revenue", 1),
            "净利润增长率": financial_data.get_growth_rate("net_profit", 1),
            "经营活动现金流增长率": financial_data.get_growth_rate("net_cash_flow_operating", 1)
        }
        
        # 趋势分析
        if financial_data.historical_data:
            analysis.trends = self._calculate_trends(financial_data)
        
        # 行业对比（这里使用示例数据，实际应用中应从数据库或API获取）
        analysis.industry_comparisons = {
            "毛利率": {"company": current.gross_margin, "industry_avg": 25.0, "industry_median": 24.5},
            "净利率": {"company": current.net_margin, "industry_avg": 8.0, "industry_median": 7.5},
            "资产负债率": {"company": current.debt_ratio, "industry_avg": 50.0, "industry_median": 48.0},
            "流动比率": {"company": current.current_ratio, "industry_avg": 1.5, "industry_median": 1.4}
        }
        
        # 检测异常指标
        analysis.anomalies = self._detect_anomalies(financial_data, analysis)
        
        return analysis
    
    def _calculate_trends(self, financial_data: FinancialData) -> Dict[str, Dict[str, float]]:
        """计算趋势"""
        trends = {}
        
        # 如果有历史数据，计算趋势
        if len(financial_data.historical_data) >= 2:
            years = sorted(financial_data.historical_data.keys())
            years.append(financial_data.report_year)
            
            # 收入趋势
            revenue_trend = {}
            for year in years:
                if year == financial_data.report_year:
                    stmt = financial_data.current_year
                else:
                    stmt = financial_data.historical_data[year]
                revenue_trend[str(year)] = stmt.operating_revenue
            trends["营业收入"] = revenue_trend
            
            # 利润趋势
            profit_trend = {}
            for year in years:
                if year == financial_data.report_year:
                    stmt = financial_data.current_year
                else:
                    stmt = financial_data.historical_data[year]
                profit_trend[str(year)] = stmt.net_profit
            trends["净利润"] = profit_trend
            
            # 现金流趋势
            cash_flow_trend = {}
            for year in years:
                if year == financial_data.report_year:
                    stmt = financial_data.current_year
                else:
                    stmt = financial_data.historical_data[year]
                cash_flow_trend[str(year)] = stmt.net_cash_flow_operating
            trends["经营活动现金流"] = cash_flow_trend
        
        return trends
    
    def _detect_anomalies(self, financial_data: FinancialData, 
                          analysis: FinancialAnalysis) -> List[Dict[str, Any]]:
        """检测异常指标"""
        anomalies = []
        
        current = financial_data.current_year
        
        # 检查毛利率异常
        if current.gross_margin < 10:  # 毛利率低于10%
            anomalies.append({
                "metric": "毛利率",
                "value": current.gross_margin,
                "threshold": 10.0,
                "description": "毛利率过低，可能面临成本压力或定价问题",
                "severity": "high"
            })
        
        # 检查净利率异常
        if current.net_margin < 3:  # 净利率低于3%
            anomalies.append({
                "metric": "净利率",
                "value": current.net_margin,
                "threshold": 3.0,
                "description": "净利率过低，盈利能力较弱",
                "severity": "medium"
            })
        
        # 检查资产负债率异常
        if current.debt_ratio > 70:  # 资产负债率高于70%
            anomalies.append({
                "metric": "资产负债率",
                "value": current.debt_ratio,
                "threshold": 70.0,
                "description": "资产负债率过高，财务风险较大",
                "severity": "high"
            })
        
        # 检查流动比率异常
        if current.current_ratio < 1.0:  # 流动比率低于1
            anomalies.append({
                "metric": "流动比率",
                "value": current.current_ratio,
                "threshold": 1.0,
                "description": "流动比率过低，短期偿债能力不足",
                "severity": "high"
            })
        
        # 检查收入增长异常
        revenue_growth = analysis.growth_ratios.get("营业收入增长率", 0)
        if revenue_growth < -20:  # 收入下降超过20%
            anomalies.append({
                "metric": "营业收入增长率",
                "value": revenue_growth,
                "threshold": -20.0,
                "description": "营业收入大幅下降，业务可能面临困难",
                "severity": "high"
            })
        
        # 检查现金流增长异常
        cash_flow_growth = analysis.growth_ratios.get("经营活动现金流增长率", 0)
        if cash_flow_growth < -30:  # 现金流下降超过30%
            anomalies.append({
                "metric": "经营活动现金流增长率",
                "value": cash_flow_growth,
                "threshold": -30.0,
                "description": "经营活动现金流大幅下降，现金流质量可能恶化",
                "severity": "high"
            })
        
        return anomalies
    
    def batch_analyze(self, pdf_files: List[str], output_dir: str = "reports") -> List[AnalysisReport]:
        """批量分析多个财报文件
        
        Args:
            pdf_files: PDF文件路径列表
            output_dir: 输出目录
            
        Returns:
            List[AnalysisReport]: 分析报告列表
        """
        reports = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n分析文件 {i}/{len(pdf_files)}: {Path(pdf_file).name}")
            print("-" * 60)
            
            try:
                report = self.analyze(pdf_file)
                reports.append(report)
            except Exception as e:
                print(f"分析文件 {pdf_file} 时出错: {e}")
                continue
        
        # 生成批量分析摘要
        if reports:
            self._generate_batch_summary(reports, output_dir)
        
        return reports
    
    def _generate_batch_summary(self, reports: List[AnalysisReport], output_dir: str):
        """生成批量分析摘要"""
        summary_path = Path(output_dir) / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 批量财报分析摘要\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分析文件数量: {len(reports)}\n\n")
            
            f.write("## 分析结果汇总\n\n")
            f.write("| 公司名称 | 报告年度 | 风险等级 | 风险评分 | 造假模式数量 | 投资建议 |\n")
            f.write("|----------|----------|----------|----------|--------------|----------|\n")
            
            for report in reports:
                risk_level = report.risk_assessment.risk_level.value
                risk_score = report.risk_assessment.total_score
                pattern_count = len(report.risk_assessment.fraud_patterns)
                
                # 简化投资建议
                if "暂停" in report.investment_recommendation:
                    recommendation = "暂停投资"
                elif "谨慎" in report.investment_recommendation:
                    recommendation = "谨慎投资"
                elif "适度" in report.investment_recommendation:
                    recommendation = "适度投资"
                else:
                    recommendation = "继续持有"
                
                f.write(f"| {report.company_name} | {report.report_year} | {risk_level} | {risk_score:.1f} | {pattern_count} | {recommendation} |\n")
            
            f.write("\n## 高风险公司\n\n")
            high_risk_reports = [r for r in reports if r.risk_assessment.risk_level.value in ["高", "极高"]]
            if high_risk_reports:
                for report in high_risk_reports:
                    f.write(f"### {report.company_name} ({report.report_year})\n")
                    f.write(f"- 风险等级: {report.risk_assessment.risk_level.value}\n")
                    f.write(f"- 风险评分: {report.risk_assessment.total_score:.1f}/50\n")
                    f.write(f"- 关键风险: {', '.join(report.key_findings[:3])}\n")
                    f.write("\n")
            else:
                f.write("未发现高风险公司。\n")
        
        print(f"\n批量分析摘要已保存: {summary_path}")