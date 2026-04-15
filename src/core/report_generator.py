"""
报告生成器
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.report_model import AnalysisReport, FinancialAnalysis, RiskAssessment
from ..models.fraud_indicators import FraudPattern


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, financial_data: FinancialData, 
                       financial_analysis: FinancialAnalysis,
                       risk_assessment: RiskAssessment,
                       fraud_patterns: List[FraudPattern]) -> AnalysisReport:
        """生成分析报告
        
        Args:
            financial_data: 财务数据
            financial_analysis: 财务分析结果
            risk_assessment: 风险评估结果
            fraud_patterns: 造假模式列表
            
        Returns:
            AnalysisReport: 分析报告
        """
        report = AnalysisReport()
        
        # 基本信息
        report.report_id = f"FR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        report.company_name = financial_data.company_name
        report.stock_code = financial_data.stock_code
        report.report_year = financial_data.report_year
        report.report_date = financial_data.report_date
        
        # 分析结果
        report.financial_analysis = financial_analysis
        report.risk_assessment = risk_assessment
        
        # 生成关键发现
        report.key_findings = self._extract_key_findings(fraud_patterns, financial_analysis)
        
        # 生成投资建议
        report.investment_recommendation = self._generate_investment_recommendation(risk_assessment)
        
        # 生成详细分析
        report.detailed_analysis = self._generate_detailed_analysis(
            financial_data, financial_analysis, fraud_patterns
        )
        
        return report
    
    def _extract_key_findings(self, fraud_patterns: List[FraudPattern], 
                             financial_analysis: FinancialAnalysis) -> List[str]:
        """提取关键发现"""
        key_findings = []
        
        # 从造假模式中提取关键发现
        for pattern in fraud_patterns:
            if pattern.risk_level.value in ["高", "极高"]:
                for indicator in pattern.indicators:
                    if indicator.risk_level.value in ["高", "极高"]:
                        key_findings.append(f"{indicator.name}: {indicator.description}")
        
        # 从财务分析中提取异常指标
        for anomaly in financial_analysis.anomalies:
            if anomaly.get("severity") in ["high", "critical"]:
                key_findings.append(f"{anomaly.get('metric')}: {anomaly.get('description')}")
        
        # 如果没有高风险发现，添加中等风险发现
        if not key_findings:
            for pattern in fraud_patterns:
                if pattern.risk_level.value == "中":
                    for indicator in pattern.indicators:
                        if indicator.risk_level.value == "中":
                            key_findings.append(f"{indicator.name}: {indicator.description}")
        
        # 限制最多10个关键发现
        return key_findings[:10]
    
    def _generate_investment_recommendation(self, risk_assessment: RiskAssessment) -> str:
        """生成投资建议"""
        risk_level = risk_assessment.risk_level.value
        total_score = risk_assessment.total_score
        
        recommendations = {
            "极高": (
                f"**强烈建议暂停投资**。风险评分{total_score:.1f}/50，风险等级{risk_level}。"
                f"发现高风险造假模式{sum(1 for p in risk_assessment.fraud_patterns if p.risk_level.value in ['高', '极高'])}个。"
                f"建议：1) 立即停止新增投资；2) 深入调查公司财务状况；3) 考虑减持现有持仓。"
            ),
            "高": (
                f"**建议谨慎投资**。风险评分{total_score:.1f}/50，风险等级{risk_level}。"
                f"发现中等及以上风险造假模式{len(risk_assessment.fraud_patterns)}个。"
                f"建议：1) 控制投资仓位不超过5%；2) 设置严格止损；3) 定期监控风险指标。"
            ),
            "中": (
                f"**可以适度投资**。风险评分{total_score:.1f}/50，风险等级{risk_level}。"
                f"发现需关注的风险点{len(risk_assessment.key_risks)}个。"
                f"建议：1) 分散投资；2) 设置适度止损；3) 定期审查公司财报。"
            ),
            "低": (
                f"**可以继续持有或适度增持**。风险评分{total_score:.1f}/50，风险等级{risk_level}。"
                f"未发现重大风险。"
                f"建议：1) 定期监控财务指标；2) 关注行业变化；3) 保持适度仓位。"
            )
        }
        
        return recommendations.get(risk_level, "无法确定投资建议")
    
    def _generate_detailed_analysis(self, financial_data: FinancialData,
                                   financial_analysis: FinancialAnalysis,
                                   fraud_patterns: List[FraudPattern]) -> Dict[str, Any]:
        """生成详细分析"""
        detailed_analysis = {
            "company_overview": {
                "name": financial_data.company_name,
                "stock_code": financial_data.stock_code,
                "report_year": financial_data.report_year,
                "auditor": financial_data.auditor,
                "audit_opinion": financial_data.audit_opinion
            },
            "financial_ratios": {
                "profitability": financial_analysis.profitability_ratios,
                "solvency": financial_analysis.solvency_ratios,
                "operation": financial_analysis.operation_ratios,
                "growth": financial_analysis.growth_ratios
            },
            "trend_analysis": financial_analysis.trends,
            "industry_comparison": financial_analysis.industry_comparisons,
            "fraud_patterns": [pattern.to_dict() for pattern in fraud_patterns],
            "anomalies": financial_analysis.anomalies,
            "notes": financial_data.notes
        }
        
        return detailed_analysis
    
    def save_report(self, report: AnalysisReport, format: str = "markdown") -> str:
        """保存报告到文件
        
        Args:
            report: 分析报告
            format: 报告格式，支持"markdown"或"json"
            
        Returns:
            str: 保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report.company_name}_{report.report_year}_analysis_{timestamp}"
        
        if format.lower() == "json":
            filepath = self.output_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report.to_json(), f, ensure_ascii=False, indent=2)
        else:
            filepath = self.output_dir / f"{filename}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report.to_markdown())
        
        return str(filepath)
    
    def print_report_summary(self, report: AnalysisReport):
        """打印报告摘要"""
        print("=" * 80)
        print(f"财报分析报告摘要")
        print("=" * 80)
        print(f"公司名称: {report.company_name}")
        print(f"股票代码: {report.stock_code}")
        print(f"报告年度: {report.report_year}")
        print(f"分析日期: {report.analysis_date}")
        print(f"报告ID: {report.report_id}")
        print()
        
        print(f"风险评估: {report.risk_assessment.risk_level.value}风险")
        print(f"风险评分: {report.risk_assessment.total_score:.1f}/50")
        print(f"造假模式数量: {len(report.risk_assessment.fraud_patterns)}")
        print()
        
        print("关键发现:")
        for i, finding in enumerate(report.key_findings[:5], 1):
            print(f"  {i}. {finding}")
        print()
        
        print("投资建议:")
        print(f"  {report.investment_recommendation}")
        print("=" * 80)