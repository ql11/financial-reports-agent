"""
报告生成器模块

该模块负责生成Markdown格式的财务分析报告。

功能特性：
- 生成执行摘要
- 生成指标一览表
- 生成详细分析
- 生成风险提示
- 计算综合评分
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging

from src.models.indicators import Indicators
from src.models.risk import RiskList, RiskLevel
from src.utils.logger import get_logger


class ReportGeneratorError(Exception):
    """报告生成器基础异常"""
    pass


class ReportGenerationError(ReportGeneratorError):
    """报告生成异常"""
    pass


class ReportGenerator:
    """报告生成器

    负责生成Markdown格式的财务分析报告。

    Attributes:
        logger: 日志器
    """

    def __init__(self):
        """初始化报告生成器"""
        self.logger = get_logger('financial_analysis')
        self.logger.info("报告生成器初始化完成")

    def generate_report(
        self,
        indicators: Indicators,
        trend_analysis: Optional[Dict[str, Any]] = None,
        risk_list: Optional[RiskList] = None,
        industry_comparison: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成分析报告

        Args:
            indicators: 财务指标
            trend_analysis: 趋势分析结果
            risk_list: 风险清单
            industry_comparison: 行业对比结果

        Returns:
            str: Markdown格式的报告内容

        Raises:
            ReportGenerationError: 报告生成失败时抛出
        """
        self.logger.info(f"开始生成分析报告: {indicators.company_name}")

        try:
            # 计算综合评分
            overall_score = self.calculate_score(risk_list, indicators) if risk_list else 10

            # 构建报告内容
            report_sections = []

            # 1. 报告标题
            report_sections.append(self._generate_title(indicators))

            # 2. 执行摘要
            report_sections.append(
                self._generate_executive_summary(
                    indicators,
                    risk_list,
                    overall_score
                )
            )

            # 3. 指标一览表
            report_sections.append(self._generate_indicator_tables(indicators))

            # 4. 详细分析
            report_sections.append(
                self._generate_detailed_analysis(
                    indicators,
                    trend_analysis,
                    industry_comparison
                )
            )

            # 5. 风险提示
            if risk_list:
                report_sections.append(self._generate_risk_warnings(risk_list))

            # 6. 综合评分
            report_sections.append(self._generate_score_section(overall_score))

            # 7. 报告信息
            report_sections.append(self._generate_report_info())

            # 合并所有部分
            report_content = "\n\n".join(report_sections)

            self.logger.info("分析报告生成完成")
            return report_content

        except Exception as e:
            self.logger.error(f"生成分析报告失败: {e}")
            raise ReportGenerationError(f"生成分析报告失败: {e}")

    def calculate_score(
        self,
        risk_list: Optional[RiskList],
        indicators: Indicators
    ) -> int:
        """计算综合评分

        Args:
            risk_list: 风险清单
            indicators: 财务指标

        Returns:
            int: 综合评分（1-10分）
        """
        self.logger.debug("计算综合评分")

        # 初始分数
        score = 10.0

        # 根据风险扣分
        if risk_list:
            score -= risk_list.get_total_score_impact() * 0.5

        # 根据盈利能力调整
        if indicators.profitability.roe >= 15:
            score += 0.5
        elif indicators.profitability.roe < 5:
            score -= 1.0

        # 根据偿债能力调整
        if indicators.solvency.debt_ratio > 70:
            score -= 1.0
        elif indicators.solvency.debt_ratio < 50:
            score += 0.5

        # 根据成长能力调整
        if indicators.growth.revenue_growth > 20:
            score += 0.5
        elif indicators.growth.revenue_growth < -10:
            score -= 1.0

        # 确保分数在1-10范围内
        score = max(1, min(10, score))

        return int(round(score))

    def _generate_title(self, indicators: Indicators) -> str:
        """生成报告标题

        Args:
            indicators: 财务指标

        Returns:
            str: 标题内容
        """
        return f"""# {indicators.company_name} {indicators.report_year}年度财务分析报告

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---"""

    def _generate_executive_summary(
        self,
        indicators: Indicators,
        risk_list: Optional[RiskList],
        overall_score: int
    ) -> str:
        """生成执行摘要

        Args:
            indicators: 财务指标
            risk_list: 风险清单
            overall_score: 综合评分

        Returns:
            str: 执行摘要内容
        """
        # 核心发现
        key_findings = []

        # 盈利能力评价
        if indicators.profitability.roe >= 15:
            key_findings.append("✅ 盈利能力优秀，ROE达到{:.2f}%".format(indicators.profitability.roe))
        elif indicators.profitability.roe >= 10:
            key_findings.append("📊 盈利能力良好，ROE为{:.2f}%".format(indicators.profitability.roe))
        else:
            key_findings.append("⚠️ 盈利能力较弱，ROE仅为{:.2f}%".format(indicators.profitability.roe))

        # 偿债能力评价
        if indicators.solvency.debt_ratio <= 50:
            key_findings.append("✅ 财务结构稳健，资产负债率{:.2f}%".format(indicators.solvency.debt_ratio))
        elif indicators.solvency.debt_ratio <= 70:
            key_findings.append("📊 财务杠杆适中，资产负债率{:.2f}%".format(indicators.solvency.debt_ratio))
        else:
            key_findings.append("⚠️ 负债水平较高，资产负债率{:.2f}%".format(indicators.solvency.debt_ratio))

        # 成长能力评价
        if indicators.growth.revenue_growth > 10:
            key_findings.append("✅ 成长性良好，营收增长{:.2f}%".format(indicators.growth.revenue_growth))
        elif indicators.growth.revenue_growth > 0:
            key_findings.append("📊 保持正增长，营收增长{:.2f}%".format(indicators.growth.revenue_growth))
        else:
            key_findings.append("⚠️ 营收负增长{:.2f}%，需关注".format(indicators.growth.revenue_growth))

        # 主要风险
        major_risks = []
        if risk_list and risk_list.has_high_risk():
            major_risks.append(f"存在{risk_list.high_risks}项高风险")
        if risk_list and risk_list.medium_risks > 0:
            major_risks.append(f"存在{risk_list.medium_risks}项中风险")

        # 总体建议
        if overall_score >= 8:
            recommendation = "财务状况优秀，建议保持当前经营策略"
        elif overall_score >= 6:
            recommendation = "财务状况良好，建议关注风险点并持续优化"
        elif overall_score >= 4:
            recommendation = "财务状况一般，建议采取措施改善经营"
        else:
            recommendation = "财务状况较差，建议全面检视经营策略"

        return f"""## 一、执行摘要

### 综合评分

**{overall_score}** / 10 分

### 核心发现

{chr(10).join(key_findings)}

### 主要风险

{'; '.join(major_risks) if major_risks else '暂无明显风险'}

### 总体建议

{recommendation}"""

    def _generate_indicator_tables(self, indicators: Indicators) -> str:
        """生成指标一览表

        Args:
            indicators: 财务指标

        Returns:
            str: 指标表内容
        """
        # 盈利能力指标表
        profitability_table = self._create_indicator_table(
            "盈利能力指标",
            indicators.profitability.to_dict(),
            indicators.profitability.get_evaluation()
        )

        # 偿债能力指标表
        solvency_table = self._create_indicator_table(
            "偿债能力指标",
            indicators.solvency.to_dict(),
            indicators.solvency.get_evaluation()
        )

        # 运营能力指标表
        operation_table = self._create_indicator_table(
            "运营能力指标",
            indicators.operation.to_dict(),
            indicators.operation.get_evaluation()
        )

        # 成长能力指标表
        growth_table = self._create_indicator_table(
            "成长能力指标",
            indicators.growth.to_dict(),
            indicators.growth.get_evaluation()
        )

        # 现金流指标表
        cashflow_table = self._create_indicator_table(
            "现金流指标",
            indicators.cashflow.to_dict(),
            indicators.cashflow.get_evaluation()
        )

        return f"""## 二、指标一览表

### 2.1 盈利能力指标

{profitability_table}

### 2.2 偿债能力指标

{solvency_table}

### 2.3 运营能力指标

{operation_table}

### 2.4 成长能力指标

{growth_table}

### 2.5 现金流指标

{cashflow_table}"""

    def _create_indicator_table(
        self,
        title: str,
        indicators_dict: Dict[str, float],
        evaluation: Dict[str, str]
    ) -> str:
        """创建指标表格

        Args:
            title: 表格标题
            indicators_dict: 指标字典
            evaluation: 评价字典

        Returns:
            str: 表格内容
        """
        table_lines = ["| 指标名称 | 指标值 | 评价 |", "|---------|--------|------|"]

        for name, value in indicators_dict.items():
            eval_result = evaluation.get(name, "-")
            table_lines.append(f"| {name} | {value:.2f} | {eval_result} |")

        return "\n".join(table_lines)

    def _generate_detailed_analysis(
        self,
        indicators: Indicators,
        trend_analysis: Optional[Dict[str, Any]],
        industry_comparison: Optional[Dict[str, Any]]
    ) -> str:
        """生成详细分析

        Args:
            indicators: 财务指标
            trend_analysis: 趋势分析结果
            industry_comparison: 行业对比结果

        Returns:
            str: 详细分析内容
        """
        # 盈利能力分析
        profitability_analysis = self._analyze_profitability(indicators)

        # 偿债能力分析
        solvency_analysis = self._analyze_solvency(indicators)

        # 运营能力分析
        operation_analysis = self._analyze_operation(indicators)

        # 成长能力分析
        growth_analysis = self._analyze_growth(indicators)

        # 趋势分析
        trend_section = ""
        if trend_analysis:
            trend_section = f"""
### 3.5 趋势分析

{trend_analysis.get('overall_conclusion', '暂无趋势分析结论')}
"""

        # 行业对比分析
        comparison_section = ""
        if industry_comparison:
            comparison_section = f"""
### 3.6 行业对比分析

{industry_comparison.get('overall_conclusion', '暂无行业对比结论')}
"""

        return f"""## 三、详细分析

### 3.1 盈利能力分析

{profitability_analysis}

### 3.2 偿债能力分析

{solvency_analysis}

### 3.3 运营能力分析

{operation_analysis}

### 3.4 成长能力分析

{growth_analysis}
{trend_section}
{comparison_section}"""

    def _analyze_profitability(self, indicators: Indicators) -> str:
        """分析盈利能力

        Args:
            indicators: 财务指标

        Returns:
            str: 分析内容
        """
        analysis_lines = []

        # 毛利率分析
        gross_margin = indicators.profitability.gross_margin
        if gross_margin >= 40:
            analysis_lines.append(f"毛利率达到{gross_margin:.2f}%，处于优秀水平，产品竞争力强。")
        elif gross_margin >= 30:
            analysis_lines.append(f"毛利率为{gross_margin:.2f}%，处于良好水平，产品有一定竞争力。")
        else:
            analysis_lines.append(f"毛利率仅为{gross_margin:.2f}%，产品竞争力不足，需优化产品结构。")

        # 净利率分析
        net_margin = indicators.profitability.net_margin
        if net_margin >= 15:
            analysis_lines.append(f"净利率达到{net_margin:.2f}%，盈利能力优秀。")
        elif net_margin >= 10:
            analysis_lines.append(f"净利率为{net_margin:.2f}%，盈利能力良好。")
        else:
            analysis_lines.append(f"净利率仅为{net_margin:.2f}%，盈利能力较弱，需控制费用支出。")

        # ROE分析
        roe = indicators.profitability.roe
        if roe >= 20:
            analysis_lines.append(f"ROE达到{roe:.2f}%，股东权益回报率优秀。")
        elif roe >= 15:
            analysis_lines.append(f"ROE为{roe:.2f}%，股东权益回报率良好。")
        else:
            analysis_lines.append(f"ROE为{roe:.2f}%，股东权益回报率偏低。")

        return "\n\n".join(analysis_lines)

    def _analyze_solvency(self, indicators: Indicators) -> str:
        """分析偿债能力

        Args:
            indicators: 财务指标

        Returns:
            str: 分析内容
        """
        analysis_lines = []

        # 资产负债率分析
        debt_ratio = indicators.solvency.debt_ratio
        if debt_ratio <= 50:
            analysis_lines.append(f"资产负债率为{debt_ratio:.2f}%，财务结构稳健，负债水平合理。")
        elif debt_ratio <= 70:
            analysis_lines.append(f"资产负债率为{debt_ratio:.2f}%，财务杠杆适中，需关注偿债压力。")
        else:
            analysis_lines.append(f"资产负债率达{debt_ratio:.2f}%，负债水平较高，财务风险较大。")

        # 流动比率分析
        current_ratio = indicators.solvency.current_ratio
        if current_ratio >= 2.0:
            analysis_lines.append(f"流动比率为{current_ratio:.2f}，短期偿债能力优秀。")
        elif current_ratio >= 1.5:
            analysis_lines.append(f"流动比率为{current_ratio:.2f}，短期偿债能力良好。")
        else:
            analysis_lines.append(f"流动比率仅为{current_ratio:.2f}，短期偿债能力不足。")

        return "\n\n".join(analysis_lines)

    def _analyze_operation(self, indicators: Indicators) -> str:
        """分析运营能力

        Args:
            indicators: 财务指标

        Returns:
            str: 分析内容
        """
        analysis_lines = []

        # 存货周转分析
        inventory_days = indicators.operation.inventory_days
        if inventory_days <= 60:
            analysis_lines.append(f"存货周转天数为{inventory_days:.0f}天，存货周转效率高。")
        elif inventory_days <= 90:
            analysis_lines.append(f"存货周转天数为{inventory_days:.0f}天，存货周转效率良好。")
        else:
            analysis_lines.append(f"存货周转天数为{inventory_days:.0f}天，存货周转较慢，需加强库存管理。")

        # 应收账款周转分析
        receivable_days = indicators.operation.receivable_days
        if receivable_days <= 30:
            analysis_lines.append(f"应收账款周转天数为{receivable_days:.0f}天，回款速度快。")
        elif receivable_days <= 60:
            analysis_lines.append(f"应收账款周转天数为{receivable_days:.0f}天，回款速度良好。")
        else:
            analysis_lines.append(f"应收账款周转天数为{receivable_days:.0f}天，回款速度较慢，需加强应收账款管理。")

        return "\n\n".join(analysis_lines)

    def _analyze_growth(self, indicators: Indicators) -> str:
        """分析成长能力

        Args:
            indicators: 财务指标

        Returns:
            str: 分析内容
        """
        analysis_lines = []

        # 营收增长分析
        revenue_growth = indicators.growth.revenue_growth
        if revenue_growth >= 30:
            analysis_lines.append(f"营收增长率达{revenue_growth:.2f}%，处于高速增长期。")
        elif revenue_growth >= 15:
            analysis_lines.append(f"营收增长率为{revenue_growth:.2f}%，保持稳健增长。")
        elif revenue_growth >= 0:
            analysis_lines.append(f"营收增长率为{revenue_growth:.2f}%，增长速度较慢。")
        else:
            analysis_lines.append(f"营收增长率为{revenue_growth:.2f}%，出现负增长，需关注市场变化。")

        # 净利润增长分析
        profit_growth = indicators.growth.profit_growth
        if profit_growth >= 30:
            analysis_lines.append(f"净利润增长率达{profit_growth:.2f}%，盈利能力快速提升。")
        elif profit_growth >= 15:
            analysis_lines.append(f"净利润增长率为{profit_growth:.2f}%，盈利能力稳步提升。")
        elif profit_growth >= 0:
            analysis_lines.append(f"净利润增长率为{profit_growth:.2f}%，盈利增长较慢。")
        else:
            analysis_lines.append(f"净利润增长率为{profit_growth:.2f}%，盈利能力下降。")

        return "\n\n".join(analysis_lines)

    def _generate_risk_warnings(self, risk_list: RiskList) -> str:
        """生成风险提示

        Args:
            risk_list: 风险清单

        Returns:
            str: 风险提示内容
        """
        risk_sections = []

        # 高风险
        high_risks = risk_list.get_risks_by_level(RiskLevel.HIGH)
        if high_risks:
            risk_sections.append("### 🔴 高风险")
            for risk in high_risks:
                risk_sections.append(f"""
**{risk.description}**

- 相关指标：{risk.indicator_name} = {risk.indicator_value:.2f}
- 风险阈值：{risk.threshold:.2f}
- 影响说明：{risk.impact}
- 建议措施：{risk.recommendation}
""")

        # 中风险
        medium_risks = risk_list.get_risks_by_level(RiskLevel.MEDIUM)
        if medium_risks:
            risk_sections.append("### 🟡 中风险")
            for risk in medium_risks:
                risk_sections.append(f"""
**{risk.description}**

- 相关指标：{risk.indicator_name} = {risk.indicator_value:.2f}
- 建议措施：{risk.recommendation}
""")

        # 低风险
        low_risks = risk_list.get_risks_by_level(RiskLevel.LOW)
        if low_risks:
            risk_sections.append("### 🟢 低风险")
            for risk in low_risks:
                risk_sections.append(f"- {risk.description}")

        return f"""## 四、风险提示

{chr(10).join(risk_sections)}

**风险统计**: 共识别{risk_list.total_risks}项风险（高风险{risk_list.high_risks}项，中风险{risk_list.medium_risks}项，低风险{risk_list.low_risks}项）"""

    def _generate_score_section(self, overall_score: int) -> str:
        """生成评分部分

        Args:
            overall_score: 综合评分

        Returns:
            str: 评分内容
        """
        if overall_score >= 8:
            rating = "优秀"
            color = "🟢"
        elif overall_score >= 6:
            rating = "良好"
            color = "🟡"
        elif overall_score >= 4:
            rating = "一般"
            color = "🟠"
        else:
            rating = "较差"
            color = "🔴"

        return f"""## 五、综合评分

### 评分结果

{color} **{overall_score}** / 10 分 - {rating}

### 评分说明

- 8-10分：财务状况优秀
- 6-7分：财务状况良好
- 4-5分：财务状况一般
- 1-3分：财务状况较差"""

    def _generate_report_info(self) -> str:
        """生成报告信息

        Returns:
            str: 报告信息内容
        """
        return f"""---

## 报告信息

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **报告版本**: v1.0
- **分析工具**: 财报分析系统

---

*本报告由系统自动生成，仅供参考，不构成投资建议。*"""

    def save_report(
        self,
        report_content: str,
        output_path: str
    ) -> str:
        """保存报告到文件

        Args:
            report_content: 报告内容
            output_path: 输出文件路径

        Returns:
            str: 报告文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        self.logger.info(f"报告已保存: {output_path}")
        return str(output_path)


def generate_report(
    indicators: Indicators,
    trend_analysis: Optional[Dict[str, Any]] = None,
    risk_list: Optional[RiskList] = None
) -> str:
    """生成报告（便捷函数）

    Args:
        indicators: 财务指标
        trend_analysis: 趋势分析结果
        risk_list: 风险清单

    Returns:
        str: 报告内容
    """
    generator = ReportGenerator()
    return generator.generate_report(indicators, trend_analysis, risk_list)
