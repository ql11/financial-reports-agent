"""
报告模型

该模块定义了分析报告相关的数据模型：
- ExecutiveSummary: 执行摘要
- IndicatorTable: 指标一览表
- DetailedAnalysis: 详细分析
- Report: 分析报告模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field

from .risk import RiskList


@dataclass
class ExecutiveSummary:
    """执行摘要

    Attributes:
        company_name: 公司名称
        report_year: 报告年度
        overall_score: 综合评分（1-10分）
        key_findings: 核心发现列表
        major_risks: 主要风险列表
        recommendation: 总体建议
    """
    company_name: str
    report_year: int
    overall_score: int
    key_findings: List[str] = field(default_factory=list)
    major_risks: List[str] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 执行摘要字典
        """
        return {
            '公司名称': self.company_name,
            '报告年度': self.report_year,
            '综合评分': self.overall_score,
            '核心发现': self.key_findings,
            '主要风险': self.major_risks,
            '总体建议': self.recommendation
        }

    def get_score_level(self) -> str:
        """获取评分等级

        Returns:
            str: 评分等级描述
        """
        if self.overall_score >= 8:
            return "优秀"
        elif self.overall_score >= 6:
            return "良好"
        elif self.overall_score >= 4:
            return "一般"
        else:
            return "较差"

    def add_finding(self, finding: str) -> None:
        """添加核心发现

        Args:
            finding: 发现内容
        """
        self.key_findings.append(finding)

    def add_risk(self, risk: str) -> None:
        """添加主要风险

        Args:
            risk: 风险描述
        """
        self.major_risks.append(risk)


class ExecutiveSummaryPydantic(BaseModel):
    """执行摘要（Pydantic版本）"""
    company_name: str = Field(..., min_length=1, description="公司名称")
    report_year: int = Field(..., ge=2000, le=2100, description="报告年度")
    overall_score: int = Field(..., ge=1, le=10, description="综合评分")
    key_findings: List[str] = Field(default_factory=list, description="核心发现")
    major_risks: List[str] = Field(default_factory=list, description="主要风险")
    recommendation: str = Field(default="", description="总体建议")


@dataclass
class IndicatorTable:
    """指标一览表

    Attributes:
        category: 指标类别
        indicators: 指标名称和值
        industry_avg: 行业平均值
        comparison: 对比结果（"优于"/"劣于"/"持平"）
    """
    category: str
    indicators: Dict[str, float] = field(default_factory=dict)
    industry_avg: Dict[str, float] = field(default_factory=dict)
    comparison: Dict[str, str] = field(default_factory=dict)

    def add_indicator(self, name: str, value: float,
                      industry_value: Optional[float] = None) -> None:
        """添加指标

        Args:
            name: 指标名称
            value: 指标值
            industry_value: 行业平均值（可选）
        """
        self.indicators[name] = value

        if industry_value is not None:
            self.industry_avg[name] = industry_value

            # 计算对比结果
            if value > industry_value * 1.05:
                self.comparison[name] = "优于"
            elif value < industry_value * 0.95:
                self.comparison[name] = "劣于"
            else:
                self.comparison[name] = "持平"

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 指标表字典
        """
        return {
            '指标类别': self.category,
            '指标数据': self.indicators,
            '行业平均': self.industry_avg,
            '对比结果': self.comparison
        }

    def get_better_indicators(self) -> List[str]:
        """获取优于行业平均的指标

        Returns:
            List[str]: 优于行业平均的指标列表
        """
        return [name for name, result in self.comparison.items()
                if result == "优于"]

    def get_worse_indicators(self) -> List[str]:
        """获取劣于行业平均的指标

        Returns:
            List[str]: 劣于行业平均的指标列表
        """
        return [name for name, result in self.comparison.items()
                if result == "劣于"]


class IndicatorTablePydantic(BaseModel):
    """指标一览表（Pydantic版本）"""
    category: str = Field(..., min_length=1, description="指标类别")
    indicators: Dict[str, float] = Field(default_factory=dict, description="指标数据")
    industry_avg: Dict[str, float] = Field(default_factory=dict, description="行业平均")
    comparison: Dict[str, str] = Field(default_factory=dict, description="对比结果")


@dataclass
class DetailedAnalysis:
    """详细分析

    Attributes:
        profitability_analysis: 盈利能力分析
        solvency_analysis: 偿债能力分析
        operation_analysis: 运营能力分析
        growth_analysis: 成长能力分析
        cashflow_analysis: 现金流分析
        trend_analysis: 趋势分析
        comparison_analysis: 对比分析
    """
    profitability_analysis: str = ""
    solvency_analysis: str = ""
    operation_analysis: str = ""
    growth_analysis: str = ""
    cashflow_analysis: str = ""
    trend_analysis: str = ""
    comparison_analysis: str = ""

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式

        Returns:
            Dict[str, str]: 详细分析字典
        """
        return {
            '盈利能力分析': self.profitability_analysis,
            '偿债能力分析': self.solvency_analysis,
            '运营能力分析': self.operation_analysis,
            '成长能力分析': self.growth_analysis,
            '现金流分析': self.cashflow_analysis,
            '趋势分析': self.trend_analysis,
            '对比分析': self.comparison_analysis
        }

    def get_all_analyses(self) -> List[str]:
        """获取所有分析内容

        Returns:
            List[str]: 所有分析内容列表
        """
        return [
            self.profitability_analysis,
            self.solvency_analysis,
            self.operation_analysis,
            self.growth_analysis,
            self.cashflow_analysis,
            self.trend_analysis,
            self.comparison_analysis
        ]


class DetailedAnalysisPydantic(BaseModel):
    """详细分析（Pydantic版本）"""
    profitability_analysis: str = Field(default="", description="盈利能力分析")
    solvency_analysis: str = Field(default="", description="偿债能力分析")
    operation_analysis: str = Field(default="", description="运营能力分析")
    growth_analysis: str = Field(default="", description="成长能力分析")
    cashflow_analysis: str = Field(default="", description="现金流分析")
    trend_analysis: str = Field(default="", description="趋势分析")
    comparison_analysis: str = Field(default="", description="对比分析")


@dataclass
class Report:
    """分析报告模型

    Attributes:
        company_name: 公司名称
        report_year: 报告年度
        report_date: 报告生成日期
        executive_summary: 执行摘要
        indicator_tables: 指标一览表列表
        detailed_analysis: 详细分析
        risk_list: 风险清单
        overall_score: 综合评分
        report_path: 报告文件路径
        generation_time: 生成时间
    """
    company_name: str
    report_year: int
    report_date: datetime
    executive_summary: ExecutiveSummary
    indicator_tables: List[IndicatorTable] = field(default_factory=list)
    detailed_analysis: DetailedAnalysis = field(default_factory=DetailedAnalysis)
    risk_list: Optional[RiskList] = None
    overall_score: int = 0
    report_path: str = ""
    generation_time: datetime = field(default_factory=datetime.now)

    def add_indicator_table(self, table: IndicatorTable) -> None:
        """添加指标表

        Args:
            table: 指标表对象
        """
        self.indicator_tables.append(table)

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 报告字典
        """
        result = {
            '公司名称': self.company_name,
            '报告年度': self.report_year,
            '报告日期': self.report_date.isoformat(),
            '执行摘要': self.executive_summary.to_dict(),
            '指标一览表': [table.to_dict() for table in self.indicator_tables],
            '详细分析': self.detailed_analysis.to_dict(),
            '综合评分': self.overall_score,
            '生成时间': self.generation_time.isoformat()
        }

        if self.risk_list:
            result['风险清单'] = self.risk_list.to_dict()

        return result

    def get_summary(self) -> str:
        """获取报告摘要

        Returns:
            str: 报告摘要文本
        """
        summary_lines = [
            f"财务分析报告",
            f"公司：{self.company_name}",
            f"报告年度：{self.report_year}年",
            f"综合评分：{self.overall_score}/10 ({self.executive_summary.get_score_level()})",
            f"生成时间：{self.generation_time.strftime('%Y-%m-%d %H:%M:%S')}"
        ]

        if self.risk_list:
            summary_lines.append(f"风险总数：{self.risk_list.total_risks}项")

        return "\n".join(summary_lines)

    def get_table_of_contents(self) -> List[str]:
        """获取报告目录

        Returns:
            List[str]: 目录列表
        """
        toc = [
            "一、执行摘要",
            "二、财务指标分析"
        ]

        # 添加指标类别
        for i, table in enumerate(self.indicator_tables, start=1):
            toc.append(f"  {i}. {table.category}")

        toc.extend([
            "三、详细分析",
            "  1. 盈利能力分析",
            "  2. 偿债能力分析",
            "  3. 运营能力分析",
            "  4. 成长能力分析",
            "  5. 现金流分析",
            "  6. 趋势分析",
            "  7. 对比分析",
            "四、风险识别",
            "五、综合评价"
        ])

        return toc


class ReportPydantic(BaseModel):
    """分析报告模型（Pydantic版本）"""
    company_name: str = Field(..., min_length=1, description="公司名称")
    report_year: int = Field(..., ge=2000, le=2100, description="报告年度")
    report_date: datetime = Field(..., description="报告生成日期")
    executive_summary: ExecutiveSummaryPydantic = Field(..., description="执行摘要")
    indicator_tables: List[IndicatorTablePydantic] = Field(
        default_factory=list, description="指标一览表"
    )
    detailed_analysis: DetailedAnalysisPydantic = Field(
        default_factory=DetailedAnalysisPydantic, description="详细分析"
    )
    risk_list: Optional[RiskList] = Field(default=None, description="风险清单")
    overall_score: int = Field(default=0, ge=0, le=10, description="综合评分")
    report_path: str = Field(default="", description="报告文件路径")
    generation_time: datetime = Field(
        default_factory=datetime.now, description="生成时间"
    )

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
