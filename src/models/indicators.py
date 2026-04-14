"""
财务指标模型

该模块定义了五大类财务指标的数据模型：
- ProfitabilityIndicators: 盈利能力指标
- SolvencyIndicators: 偿债能力指标
- OperationIndicators: 运营能力指标
- GrowthIndicators: 成长能力指标
- CashFlowIndicators: 现金流指标
- Indicators: 财务指标总模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field, validator


@dataclass
class ProfitabilityIndicators:
    """盈利能力指标

    Attributes:
        gross_margin: 毛利率（%）
        net_margin: 净利率（%）
        roe: 净资产收益率（%）
        roa: 总资产收益率（%）
        operating_margin: 营业利润率（%）
    """
    gross_margin: float
    net_margin: float
    roe: float
    roa: float
    operating_margin: float

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 指标字典
        """
        return {
            '毛利率': self.gross_margin,
            '净利率': self.net_margin,
            '净资产收益率(ROE)': self.roe,
            '总资产收益率(ROA)': self.roa,
            '营业利润率': self.operating_margin
        }

    def get_evaluation(self) -> Dict[str, str]:
        """获取指标评价

        Returns:
            Dict[str, str]: 指标评价字典
        """
        evaluation = {}

        # 毛利率评价
        if self.gross_margin >= 40:
            evaluation['毛利率'] = '优秀'
        elif self.gross_margin >= 30:
            evaluation['毛利率'] = '良好'
        elif self.gross_margin >= 20:
            evaluation['毛利率'] = '一般'
        else:
            evaluation['毛利率'] = '较差'

        # 净利率评价
        if self.net_margin >= 15:
            evaluation['净利率'] = '优秀'
        elif self.net_margin >= 10:
            evaluation['净利率'] = '良好'
        elif self.net_margin >= 5:
            evaluation['净利率'] = '一般'
        else:
            evaluation['净利率'] = '较差'

        # ROE评价
        if self.roe >= 20:
            evaluation['净资产收益率(ROE)'] = '优秀'
        elif self.roe >= 15:
            evaluation['净资产收益率(ROE)'] = '良好'
        elif self.roe >= 10:
            evaluation['净资产收益率(ROE)'] = '一般'
        else:
            evaluation['净资产收益率(ROE)'] = '较差'

        return evaluation


class ProfitabilityIndicatorsPydantic(BaseModel):
    """盈利能力指标（Pydantic版本）"""
    gross_margin: float = Field(..., description="毛利率")
    net_margin: float = Field(..., description="净利率")
    roe: float = Field(..., description="净资产收益率")
    roa: float = Field(..., description="总资产收益率")
    operating_margin: float = Field(..., description="营业利润率")


@dataclass
class SolvencyIndicators:
    """偿债能力指标

    Attributes:
        debt_ratio: 资产负债率（%）
        current_ratio: 流动比率
        quick_ratio: 速动比率
        equity_ratio: 产权比率
    """
    debt_ratio: float
    current_ratio: float
    quick_ratio: float
    equity_ratio: float

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 指标字典
        """
        return {
            '资产负债率': self.debt_ratio,
            '流动比率': self.current_ratio,
            '速动比率': self.quick_ratio,
            '产权比率': self.equity_ratio
        }

    def get_evaluation(self) -> Dict[str, str]:
        """获取指标评价

        Returns:
            Dict[str, str]: 指标评价字典
        """
        evaluation = {}

        # 资产负债率评价
        if self.debt_ratio <= 40:
            evaluation['资产负债率'] = '优秀'
        elif self.debt_ratio <= 60:
            evaluation['资产负债率'] = '良好'
        elif self.debt_ratio <= 70:
            evaluation['资产负债率'] = '一般'
        else:
            evaluation['资产负债率'] = '风险较高'

        # 流动比率评价
        if self.current_ratio >= 2.0:
            evaluation['流动比率'] = '优秀'
        elif self.current_ratio >= 1.5:
            evaluation['流动比率'] = '良好'
        elif self.current_ratio >= 1.0:
            evaluation['流动比率'] = '一般'
        else:
            evaluation['流动比率'] = '风险较高'

        # 速动比率评价
        if self.quick_ratio >= 1.0:
            evaluation['速动比率'] = '优秀'
        elif self.quick_ratio >= 0.8:
            evaluation['速动比率'] = '良好'
        elif self.quick_ratio >= 0.5:
            evaluation['速动比率'] = '一般'
        else:
            evaluation['速动比率'] = '风险较高'

        return evaluation


class SolvencyIndicatorsPydantic(BaseModel):
    """偿债能力指标（Pydantic版本）"""
    debt_ratio: float = Field(..., ge=0, le=100, description="资产负债率")
    current_ratio: float = Field(..., ge=0, description="流动比率")
    quick_ratio: float = Field(..., ge=0, description="速动比率")
    equity_ratio: float = Field(..., ge=0, description="产权比率")


@dataclass
class OperationIndicators:
    """运营能力指标

    Attributes:
        inventory_turnover: 存货周转率（次）
        receivable_turnover: 应收账款周转率（次）
        total_asset_turnover: 总资产周转率（次）
        inventory_days: 存货周转天数
        receivable_days: 应收账款周转天数
    """
    inventory_turnover: float
    receivable_turnover: float
    total_asset_turnover: float
    inventory_days: float
    receivable_days: float

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 指标字典
        """
        return {
            '存货周转率': self.inventory_turnover,
            '应收账款周转率': self.receivable_turnover,
            '总资产周转率': self.total_asset_turnover,
            '存货周转天数': self.inventory_days,
            '应收账款周转天数': self.receivable_days
        }

    def get_evaluation(self) -> Dict[str, str]:
        """获取指标评价

        Returns:
            Dict[str, str]: 指标评价字典
        """
        evaluation = {}

        # 存货周转天数评价
        if self.inventory_days <= 60:
            evaluation['存货周转天数'] = '优秀'
        elif self.inventory_days <= 90:
            evaluation['存货周转天数'] = '良好'
        elif self.inventory_days <= 120:
            evaluation['存货周转天数'] = '一般'
        else:
            evaluation['存货周转天数'] = '较慢'

        # 应收账款周转天数评价
        if self.receivable_days <= 30:
            evaluation['应收账款周转天数'] = '优秀'
        elif self.receivable_days <= 60:
            evaluation['应收账款周转天数'] = '良好'
        elif self.receivable_days <= 90:
            evaluation['应收账款周转天数'] = '一般'
        else:
            evaluation['应收账款周转天数'] = '较慢'

        return evaluation


class OperationIndicatorsPydantic(BaseModel):
    """运营能力指标（Pydantic版本）"""
    inventory_turnover: float = Field(..., ge=0, description="存货周转率")
    receivable_turnover: float = Field(..., ge=0, description="应收账款周转率")
    total_asset_turnover: float = Field(..., ge=0, description="总资产周转率")
    inventory_days: float = Field(..., ge=0, description="存货周转天数")
    receivable_days: float = Field(..., ge=0, description="应收账款周转天数")


@dataclass
class GrowthIndicators:
    """成长能力指标

    Attributes:
        revenue_growth: 营收增长率（%）
        profit_growth: 净利润增长率（%）
        asset_growth: 总资产增长率（%）
        equity_growth: 净资产增长率（%）
    """
    revenue_growth: float
    profit_growth: float
    asset_growth: float
    equity_growth: float

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 指标字典
        """
        return {
            '营收增长率': self.revenue_growth,
            '净利润增长率': self.profit_growth,
            '总资产增长率': self.asset_growth,
            '净资产增长率': self.equity_growth
        }

    def get_evaluation(self) -> Dict[str, str]:
        """获取指标评价

        Returns:
            Dict[str, str]: 指标评价字典
        """
        evaluation = {}

        # 营收增长率评价
        if self.revenue_growth >= 30:
            evaluation['营收增长率'] = '高速增长'
        elif self.revenue_growth >= 15:
            evaluation['营收增长率'] = '稳健增长'
        elif self.revenue_growth >= 0:
            evaluation['营收增长率'] = '低速增长'
        else:
            evaluation['营收增长率'] = '负增长'

        # 净利润增长率评价
        if self.profit_growth >= 30:
            evaluation['净利润增长率'] = '高速增长'
        elif self.profit_growth >= 15:
            evaluation['净利润增长率'] = '稳健增长'
        elif self.profit_growth >= 0:
            evaluation['净利润增长率'] = '低速增长'
        else:
            evaluation['净利润增长率'] = '负增长'

        return evaluation


class GrowthIndicatorsPydantic(BaseModel):
    """成长能力指标（Pydantic版本）"""
    revenue_growth: float = Field(..., description="营收增长率")
    profit_growth: float = Field(..., description="净利润增长率")
    asset_growth: float = Field(..., description="总资产增长率")
    equity_growth: float = Field(..., description="净资产增长率")


@dataclass
class CashFlowIndicators:
    """现金流指标

    Attributes:
        free_cash_flow: 自由现金流
        cash_to_debt: 现金债务覆盖率
        operating_cash_to_debt: 经营现金流债务覆盖率
    """
    free_cash_flow: float
    cash_to_debt: float
    operating_cash_to_debt: float

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 指标字典
        """
        return {
            '自由现金流': self.free_cash_flow,
            '现金债务覆盖率': self.cash_to_debt,
            '经营现金流债务覆盖率': self.operating_cash_to_debt
        }

    def get_evaluation(self) -> Dict[str, str]:
        """获取指标评价

        Returns:
            Dict[str, str]: 指标评价字典
        """
        evaluation = {}

        # 自由现金流评价
        if self.free_cash_flow > 0:
            evaluation['自由现金流'] = '正向'
        else:
            evaluation['自由现金流'] = '负向'

        # 现金债务覆盖率评价
        if self.cash_to_debt >= 0.5:
            evaluation['现金债务覆盖率'] = '优秀'
        elif self.cash_to_debt >= 0.3:
            evaluation['现金债务覆盖率'] = '良好'
        elif self.cash_to_debt >= 0.1:
            evaluation['现金债务覆盖率'] = '一般'
        else:
            evaluation['现金债务覆盖率'] = '较差'

        return evaluation


class CashFlowIndicatorsPydantic(BaseModel):
    """现金流指标（Pydantic版本）"""
    free_cash_flow: float = Field(..., description="自由现金流")
    cash_to_debt: float = Field(..., ge=0, description="现金债务覆盖率")
    operating_cash_to_debt: float = Field(..., ge=0, description="经营现金流债务覆盖率")


@dataclass
class Indicators:
    """财务指标总模型

    Attributes:
        company_name: 公司名称
        report_year: 报告年度
        profitability: 盈利能力指标
        solvency: 偿债能力指标
        operation: 运营能力指标
        growth: 成长能力指标
        cashflow: 现金流指标
        calculation_time: 计算时间
    """
    company_name: str
    report_year: int

    profitability: ProfitabilityIndicators
    solvency: SolvencyIndicators
    operation: OperationIndicators
    growth: GrowthIndicators
    cashflow: CashFlowIndicators

    calculation_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        """转换为字典格式

        Returns:
            Dict[str, Dict[str, float]]: 所有指标的字典
        """
        return {
            '盈利能力': self.profitability.to_dict(),
            '偿债能力': self.solvency.to_dict(),
            '运营能力': self.operation.to_dict(),
            '成长能力': self.growth.to_dict(),
            '现金流': self.cashflow.to_dict()
        }

    def get_all_evaluations(self) -> Dict[str, Dict[str, str]]:
        """获取所有指标评价

        Returns:
            Dict[str, Dict[str, str]]: 所有指标的评价
        """
        return {
            '盈利能力': self.profitability.get_evaluation(),
            '偿债能力': self.solvency.get_evaluation(),
            '运营能力': self.operation.get_evaluation(),
            '成长能力': self.growth.get_evaluation(),
            '现金流': self.cashflow.get_evaluation()
        }

    def get_summary(self) -> dict:
        """获取指标摘要

        Returns:
            dict: 指标摘要
        """
        return {
            'company_name': self.company_name,
            'report_year': self.report_year,
            'gross_margin': self.profitability.gross_margin,
            'net_margin': self.profitability.net_margin,
            'roe': self.profitability.roe,
            'debt_ratio': self.solvency.debt_ratio,
            'current_ratio': self.solvency.current_ratio,
            'revenue_growth': self.growth.revenue_growth,
            'profit_growth': self.growth.profit_growth
        }


class IndicatorsPydantic(BaseModel):
    """财务指标总模型（Pydantic版本）"""
    company_name: str = Field(..., min_length=1, description="公司名称")
    report_year: int = Field(..., ge=2000, le=2100, description="报告年度")

    profitability: ProfitabilityIndicatorsPydantic = Field(..., description="盈利能力指标")
    solvency: SolvencyIndicatorsPydantic = Field(..., description="偿债能力指标")
    operation: OperationIndicatorsPydantic = Field(..., description="运营能力指标")
    growth: GrowthIndicatorsPydantic = Field(..., description="成长能力指标")
    cashflow: CashFlowIndicatorsPydantic = Field(..., description="现金流指标")

    calculation_time: datetime = Field(default_factory=datetime.now, description="计算时间")

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
