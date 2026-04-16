"""
分析报告模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from .fraud_indicators import RiskLevel, FraudPattern


@dataclass
class RiskAssessment:
    """风险评估"""
    
    total_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    fraud_patterns: List[FraudPattern] = field(default_factory=list)
    key_risks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    score_breakdown: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_total_score(self):
        """计算总分和风险等级"""
        if not self.fraud_patterns:
            return
        
        self.total_score = sum(pattern.total_score for pattern in self.fraud_patterns)
        
        # 根据总分确定风险等级（与risk_assessor的阈值对齐）
        if self.total_score >= 38:
            self.risk_level = RiskLevel.CRITICAL
        elif self.total_score >= 25:
            self.risk_level = RiskLevel.HIGH
        elif self.total_score >= 14:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_score": self.total_score,
            "risk_level": self.risk_level.value,
            "fraud_patterns": [pattern.to_dict() for pattern in self.fraud_patterns],
            "key_risks": self.key_risks,
            "recommendations": self.recommendations,
            "score_breakdown": self.score_breakdown,
        }


@dataclass
class FinancialAnalysis:
    """财务分析结果"""
    
    # 财务比率
    profitability_ratios: Dict[str, float] = field(default_factory=dict)
    solvency_ratios: Dict[str, float] = field(default_factory=dict)
    operation_ratios: Dict[str, float] = field(default_factory=dict)
    growth_ratios: Dict[str, float] = field(default_factory=dict)
    
    # 趋势分析
    trends: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # 行业对比
    industry_comparisons: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 异常指标
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "profitability_ratios": self.profitability_ratios,
            "solvency_ratios": self.solvency_ratios,
            "operation_ratios": self.operation_ratios,
            "growth_ratios": self.growth_ratios,
            "trends": self.trends,
            "industry_comparisons": self.industry_comparisons,
            "anomalies": self.anomalies
        }


@dataclass
class AnalysisReport:
    """分析报告"""
    
    # 报告基本信息
    report_id: str = ""
    company_name: str = ""
    stock_code: str = ""
    report_year: int = 0
    report_date: str = ""
    analysis_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    analyst: str = "财报造假分析系统"
    
    # 分析结果
    financial_analysis: FinancialAnalysis = field(default_factory=FinancialAnalysis)
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    
    # 摘要
    executive_summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    investment_recommendation: str = ""
    
    # 详细分析
    detailed_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def generate_executive_summary(self):
        """生成执行摘要"""
        summary_parts = []
        
        # 公司基本信息
        summary_parts.append(f"## 执行摘要")
        summary_parts.append(f"**公司名称**: {self.company_name}")
        summary_parts.append(f"**股票代码**: {self.stock_code}")
        summary_parts.append(f"**报告年度**: {self.report_year}")
        summary_parts.append(f"**分析日期**: {self.analysis_date}")
        summary_parts.append("")
        
        # 风险评估
        summary_parts.append(f"**风险评估**: {self.risk_assessment.risk_level.value}风险")
        summary_parts.append(f"**风险评分**: {self.risk_assessment.total_score:.1f}/50")
        summary_parts.append("")
        
        # 关键发现
        if self.key_findings:
            summary_parts.append("**关键发现**:")
            for finding in self.key_findings[:5]:  # 只显示前5个
                summary_parts.append(f"- {finding}")
            summary_parts.append("")
        
        # 投资建议
        if self.investment_recommendation:
            summary_parts.append(f"**投资建议**: {self.investment_recommendation}")
        
        self.executive_summary = "\n".join(summary_parts)

    @staticmethod
    def _collect_pattern_evidence(pattern: FraudPattern) -> List[str]:
        """汇总造假模式下带页码的原始证据片段，按出现顺序去重"""
        evidence_items: List[str] = []
        seen = set()

        for indicator in pattern.indicators:
            for evidence in indicator.evidence:
                normalized = evidence.strip()
                if (
                    normalized
                    and "第" in normalized
                    and "页" in normalized
                    and normalized not in seen
                ):
                    evidence_items.append(normalized)
                    seen.add(normalized)

        return evidence_items

    def _append_score_formula(self, markdown_parts: List[str]):
        """渲染风险评分计算式与分项分值。"""
        breakdown = self.risk_assessment.score_breakdown
        if not breakdown:
            return

        markdown_parts.append("### 风险评分计算式")
        formula = breakdown.get(
            "formula",
            "总分 = min(模式严重度 + 财务严重度 + 风险密度 + 风险广度 + 风险集中度 + 最高风险加分, 50)",
        )
        markdown_parts.append(formula)

        labels = [
            ("severity_score", "模式严重度"),
            ("financial_severity", "财务严重度"),
            ("density_score", "风险密度"),
            ("breadth_score", "风险广度"),
            ("concentration_score", "风险集中度"),
            ("max_risk_bonus", "最高风险加分"),
            ("total_before_cap", "封顶前总分"),
            ("total_score", "最终总分"),
        ]
        for key, label in labels:
            if key in breakdown:
                markdown_parts.append(f"- {label}: {breakdown[key]:.1f}")
        markdown_parts.append("")

    def _append_signal_status(self, markdown_parts: List[str]):
        """渲染信号状态分层。"""
        if not self.detailed_analysis:
            return

        summary = self.detailed_analysis.get("signal_status_summary")
        if not summary:
            return

        markdown_parts.append("### 信号状态")

        confirmed = summary.get("confirmed_anomalies", [])
        if confirmed:
            markdown_parts.append("#### 明确异常")
            for item in confirmed:
                risk_level = item.get("risk_level", "")
                suffix = f"（{risk_level}）" if risk_level else ""
                markdown_parts.append(
                    f"- {item.get('name', '')}{suffix}: {item.get('description', '')}"
                )

        weak_signals = summary.get("weak_signals", [])
        if weak_signals:
            markdown_parts.append("#### 弱信号")
            for item in weak_signals:
                markdown_parts.append(
                    f"- {item.get('name', '')}: {item.get('description', '')}"
                )

        missing_data = summary.get("missing_data", [])
        if missing_data:
            markdown_parts.append("#### 缺失数据")
            for item in missing_data:
                markdown_parts.append(
                    f"- {item.get('name', '')}: {item.get('description', '')}"
                )

        markdown_parts.append("")
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        self.generate_executive_summary()
        
        markdown_parts = []
        
        # 标题
        markdown_parts.append(f"# {self.company_name} {self.report_year}年度财报分析报告")
        markdown_parts.append(f"**报告ID**: {self.report_id}")
        markdown_parts.append(f"**分析日期**: {self.analysis_date}")
        markdown_parts.append("")
        
        # 执行摘要
        markdown_parts.append(self.executive_summary)
        markdown_parts.append("")
        
        # 财务分析
        markdown_parts.append("## 财务分析")
        
        # 盈利能力
        if self.financial_analysis.profitability_ratios:
            markdown_parts.append("### 盈利能力分析")
            for name, value in self.financial_analysis.profitability_ratios.items():
                markdown_parts.append(f"- **{name}**: {value:.2f}%")
            markdown_parts.append("")
        
        # 偿债能力
        if self.financial_analysis.solvency_ratios:
            markdown_parts.append("### 偿债能力分析")
            for name, value in self.financial_analysis.solvency_ratios.items():
                markdown_parts.append(f"- **{name}**: {value:.2f}%")
            markdown_parts.append("")
        
        # 运营能力
        if self.financial_analysis.operation_ratios:
            markdown_parts.append("### 运营能力分析")
            for name, value in self.financial_analysis.operation_ratios.items():
                markdown_parts.append(f"- **{name}**: {value:.2f}")
            markdown_parts.append("")
        
        # 成长能力
        if self.financial_analysis.growth_ratios:
            markdown_parts.append("### 成长能力分析")
            for name, value in self.financial_analysis.growth_ratios.items():
                markdown_parts.append(f"- **{name}**: {value:.2f}%")
            markdown_parts.append("")
        
        # 收入质量分析（新增）
        if self.detailed_analysis and "revenue_quality" in self.detailed_analysis:
            rq = self.detailed_analysis["revenue_quality"]
            if rq:
                markdown_parts.append("### 收入质量分析")
                for name, value in rq.items():
                    if isinstance(value, float):
                        markdown_parts.append(f"- **{name}**: {value:.2%}" if value < 1 else f"- **{name}**: {value:.1f}")
                    else:
                        markdown_parts.append(f"- **{name}**: {value}")
                markdown_parts.append("")
        
        # 现金流质量分析（新增）
        if self.detailed_analysis and "cash_flow_quality" in self.detailed_analysis:
            cq = self.detailed_analysis["cash_flow_quality"]
            if cq:
                markdown_parts.append("### 现金流质量分析")
                for name, value in cq.items():
                    if isinstance(value, float):
                        markdown_parts.append(f"- **{name}**: {value:.2f}")
                    else:
                        markdown_parts.append(f"- **{name}**: {value}")
                markdown_parts.append("")
        
        # 报表勾稽校验（新增）
        if self.detailed_analysis and "cross_statement_checks" in self.detailed_analysis:
            cs = self.detailed_analysis["cross_statement_checks"]
            if cs:
                markdown_parts.append("### 报表勾稽校验")
                for name, value in cs.items():
                    markdown_parts.append(f"- **{name}**: {value}")
                markdown_parts.append("")
        
        # 风险评估
        markdown_parts.append("## 风险评估")
        markdown_parts.append(f"**总体风险等级**: {self.risk_assessment.risk_level.value}")
        markdown_parts.append(f"**风险评分**: {self.risk_assessment.total_score:.1f}/50")
        markdown_parts.append("")
        self._append_score_formula(markdown_parts)
        self._append_signal_status(markdown_parts)
        
        # 造假模式
        if self.risk_assessment.fraud_patterns:
            markdown_parts.append("### 发现的造假模式")
            for pattern in self.risk_assessment.fraud_patterns:
                markdown_parts.append(f"#### {pattern.name}")
                markdown_parts.append(f"{pattern.description}")
                markdown_parts.append(f"**风险等级**: {pattern.risk_level.value}")
                markdown_parts.append(f"**风险评分**: {pattern.total_score:.1f}")
                pattern_evidence = self._collect_pattern_evidence(pattern)
                if pattern_evidence:
                    markdown_parts.append("##### 证据摘录")
                    for evidence in pattern_evidence:
                        markdown_parts.append(f"- {evidence}")
                markdown_parts.append("")
        
        # 关键风险
        if self.risk_assessment.key_risks:
            markdown_parts.append("### 关键风险点")
            for risk in self.risk_assessment.key_risks:
                markdown_parts.append(f"- {risk}")
            markdown_parts.append("")
        
        # 建议
        if self.risk_assessment.recommendations:
            markdown_parts.append("### 建议")
            for recommendation in self.risk_assessment.recommendations:
                markdown_parts.append(f"- {recommendation}")
            markdown_parts.append("")
        
        # 投资建议
        markdown_parts.append("## 投资建议")
        markdown_parts.append(self.investment_recommendation)
        markdown_parts.append("")
        
        # 附录
        markdown_parts.append("## 附录")
        markdown_parts.append(f"**分析师**: {self.analyst}")
        markdown_parts.append(f"**报告版本**: 2.0.0")
        markdown_parts.append("")
        markdown_parts.append("---")
        markdown_parts.append("*本报告由财报造假分析系统自动生成，仅供参考，不构成投资建议。*")
        
        return "\n".join(markdown_parts)
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON格式"""
        self.generate_executive_summary()
        
        return {
            "report_id": self.report_id,
            "company_name": self.company_name,
            "stock_code": self.stock_code,
            "report_year": self.report_year,
            "report_date": self.report_date,
            "analysis_date": self.analysis_date,
            "analyst": self.analyst,
            "executive_summary": self.executive_summary,
            "key_findings": self.key_findings,
            "investment_recommendation": self.investment_recommendation,
            "financial_analysis": self.financial_analysis.to_dict(),
            "risk_assessment": self.risk_assessment.to_dict(),
            "detailed_analysis": self.detailed_analysis
        }
