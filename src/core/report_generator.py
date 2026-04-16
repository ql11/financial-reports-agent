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
from ..utils.logging_utils import get_logger


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger(__name__)
    
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
        
        review_override = self._build_review_override(financial_data, risk_assessment)
        if review_override:
            review_note = "待核验：证据链未闭合或审计意见存在重大不确定性，暂不采用自动投资建议。"
            retained_recommendations = self._strip_summary_recommendations(
                risk_assessment.recommendations
            )
            risk_assessment.recommendations = [
                review_note,
                *retained_recommendations,
            ][:10]
            report.investment_recommendation = review_override
        else:
            report.investment_recommendation = self._generate_investment_recommendation(
                risk_assessment, financial_data
            )
        
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
    
    def _has_key_statement_evidence(self, financial_data: FinancialData) -> bool:
        required_fields = (
            "operating_revenue",
            "net_profit",
            "net_cash_flow_operating",
            "total_assets",
            "total_liabilities",
        )
        has_required_fields = all(
            financial_data.evidence_refs.get(f"statement:{field}")
            for field in required_fields
        )
        has_equity_evidence = bool(
            financial_data.evidence_refs.get("statement:total_equity")
        ) or (
            financial_data.evidence_refs.get("statement:total_assets")
            and financial_data.evidence_refs.get("statement:total_liabilities")
        )
        return has_required_fields and has_equity_evidence

    def _build_review_override(
        self, financial_data: FinancialData, risk_assessment: RiskAssessment
    ) -> Optional[str]:
        """在证据链不完整时覆盖默认投资建议。"""
        if (
            "持续经营" in financial_data.audit_opinion
            or "重大不确定性" in financial_data.audit_opinion
        ):
            return (
                f"**待核验**。审计意见为“{financial_data.audit_opinion}”，"
                "存在持续经营重大不确定性相关事项，不能直接按低风险处理。"
                "建议：1) 人工复核审计报告原文；2) 核验持续经营风险来源；3) 暂不采用自动投资建议。"
            )

        if (
            risk_assessment.risk_level.value == "低"
            and not self._has_key_statement_evidence(financial_data)
        ):
            return (
                f"**待核验**。当前自动评分为{risk_assessment.total_score:.1f}/50，"
                "但主表关键字段证据链不完整，不能直接给出低风险增持结论。"
                "建议：1) 先补齐营业收入、净利润、现金流和资产负债表页码证据；"
                "2) 完成人工抽样复核；3) 复核后再使用自动投资建议。"
            )

        return None

    @staticmethod
    def _strip_summary_recommendations(recommendations: List[str]) -> List[str]:
        """去掉风险评估器自动生成的摘要建议，只保留具体复核动作。"""
        summary_prefixes = (
            "**极高风险**：",
            "**高风险**：",
            "**中等风险**：",
            "**低风险**：",
        )
        summary_lines = {
            "重点关注现金流异常和审计问题",
            "关注业绩背离和应收账款异常",
            "关注存货异常和政府补助操纵",
            "关注财务指标变化趋势",
        }

        filtered: List[str] = []
        seen = set()
        for recommendation in recommendations:
            if recommendation.startswith(summary_prefixes):
                continue
            if recommendation in summary_lines:
                continue
            if recommendation not in seen:
                filtered.append(recommendation)
                seen.add(recommendation)
        return filtered

    def _generate_investment_recommendation(
        self, risk_assessment: RiskAssessment, financial_data: FinancialData
    ) -> str:
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
        current = financial_data.current_year
        
        # 收入质量分析（新增）
        revenue_quality = {}
        if current.operating_revenue > 0:
            if hasattr(current, 'cash_from_sales') and current.cash_from_sales > 0:
                revenue_quality["现金收入比"] = round(current.cash_from_sales / current.operating_revenue, 4)
            if current.accounts_receivable > 0:
                revenue_quality["应收账款占收入比"] = round(current.accounts_receivable / current.operating_revenue, 4)
            if current.accounts_receivable > 0:
                revenue_quality["应收账款周转天数"] = round(365 * current.accounts_receivable / current.operating_revenue, 1)
        
        # 现金流质量分析（新增）
        cash_flow_quality = {}
        if current.net_profit > 0:
            cash_flow_quality["经营现金流/净利润"] = round(current.net_cash_flow_operating / current.net_profit, 4) if current.net_profit != 0 else None
        if current.net_cash_flow_operating > 0 and current.net_profit > 0:
            ratio = current.net_cash_flow_operating / current.net_profit
            if ratio >= 1:
                cash_flow_quality["盈利质量评价"] = "好（经营现金流≥净利润）"
            elif ratio >= 0.5:
                cash_flow_quality["盈利质量评价"] = "一般（经营现金流<净利润）"
            else:
                cash_flow_quality["盈利质量评价"] = "差（经营现金流远低于净利润）"
        elif current.net_profit > 0 and current.net_cash_flow_operating <= 0:
            cash_flow_quality["盈利质量评价"] = "极差（净利润为正但经营现金流为负，典型造假信号）"
        
        # 报表勾稽校验结果（新增）
        cross_statement_checks = {}
        if current.total_assets > 0 and current.total_liabilities > 0:
            implied_equity = current.total_assets - current.total_liabilities
            if hasattr(current, 'total_equity') and current.total_equity > 0:
                equity_diff = abs(implied_equity - current.total_equity)
                cross_statement_checks["资产-负债=权益校验"] = "通过" if equity_diff / current.total_assets < 0.05 else f"异常（差异{equity_diff:,.0f}）"
        
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
            "revenue_quality": revenue_quality,
            "cash_flow_quality": cash_flow_quality,
            "cross_statement_checks": cross_statement_checks,
            "trend_analysis": financial_analysis.trends,
            "industry_comparison": financial_analysis.industry_comparisons,
            "fraud_patterns": [pattern.to_dict() for pattern in fraud_patterns],
            "anomalies": financial_analysis.anomalies,
            "notes": financial_data.notes,
            "evidence_refs": financial_data.evidence_refs,
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
        self.logger.info("%s", "=" * 80)
        self.logger.info("财报分析报告摘要")
        self.logger.info("%s", "=" * 80)
        self.logger.info("公司名称: %s", report.company_name)
        self.logger.info("股票代码: %s", report.stock_code)
        self.logger.info("报告年度: %s", report.report_year)
        self.logger.info("分析日期: %s", report.analysis_date)
        self.logger.info("报告ID: %s", report.report_id)
        self.logger.info("风险评估: %s风险", report.risk_assessment.risk_level.value)
        self.logger.info("风险评分: %.1f/50", report.risk_assessment.total_score)
        self.logger.info("造假模式数量: %s", len(report.risk_assessment.fraud_patterns))
        self.logger.info("关键发现:")
        for i, finding in enumerate(report.key_findings[:5], 1):
            self.logger.info("  %s. %s", i, finding)
        self.logger.info("投资建议:")
        self.logger.info("  %s", report.investment_recommendation)
        self.logger.info("%s", "=" * 80)
