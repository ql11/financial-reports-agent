"""
指标计算器模块

该模块负责计算五大类财务指标。

功能特性：
- 计算盈利能力指标
- 计算偿债能力指标
- 计算运营能力指标
- 计算成长能力指标
- 计算现金流指标
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from src.models.financial_data import FinancialData
from src.models.indicators import (
    ProfitabilityIndicators,
    SolvencyIndicators,
    OperationIndicators,
    GrowthIndicators,
    CashFlowIndicators,
    Indicators
)
from src.utils.logger import get_logger


class IndicatorCalculatorError(Exception):
    """指标计算器基础异常"""
    pass


class CalculationError(IndicatorCalculatorError):
    """计算异常"""
    pass


class IndicatorCalculator:
    """指标计算器

    负责计算五大类财务指标。

    Attributes:
        logger: 日志器
    """

    def __init__(self):
        """初始化指标计算器"""
        self.logger = get_logger('financial_analysis')
        self.logger.info("指标计算器初始化完成")

    def calculate_indicators(
        self,
        financial_data: FinancialData,
        historical_data: Optional[List[FinancialData]] = None
    ) -> Indicators:
        """计算所有财务指标

        Args:
            financial_data: 当期财务数据
            historical_data: 历史财务数据列表（用于计算成长指标）

        Returns:
            Indicators: 财务指标对象

        Raises:
            CalculationError: 计算失败时抛出
        """
        self.logger.info(f"开始计算财务指标: {financial_data.company_name}")

        try:
            # 计算各类指标
            profitability = self.calculate_profitability_indicators(financial_data)
            solvency = self.calculate_solvency_indicators(financial_data)
            operation = self.calculate_operation_indicators(financial_data)
            growth = self.calculate_growth_indicators(financial_data, historical_data)
            cashflow = self.calculate_cashflow_indicators(financial_data)

            # 创建指标对象
            indicators = Indicators(
                company_name=financial_data.company_name,
                report_year=financial_data.report_year,
                profitability=profitability,
                solvency=solvency,
                operation=operation,
                growth=growth,
                cashflow=cashflow,
                calculation_time=datetime.now()
            )

            self.logger.info("财务指标计算完成")
            return indicators

        except Exception as e:
            self.logger.error(f"计算财务指标失败: {e}")
            raise CalculationError(f"计算财务指标失败: {e}")

    def calculate_profitability_indicators(
        self,
        financial_data: FinancialData
    ) -> ProfitabilityIndicators:
        """计算盈利能力指标

        Args:
            financial_data: 财务数据

        Returns:
            ProfitabilityIndicators: 盈利能力指标
        """
        self.logger.debug("计算盈利能力指标")

        bs = financial_data.balance_sheet
        ins = financial_data.income_statement

        # 毛利率 = (营业收入 - 营业成本) / 营业收入
        gross_margin = self._safe_divide(
            ins.operating_revenue - ins.operating_cost,
            ins.operating_revenue
        ) * 100

        # 净利率 = 净利润 / 营业收入
        net_margin = self._safe_divide(
            ins.net_profit,
            ins.operating_revenue
        ) * 100

        # ROE = 净利润 / 平均净资产
        roe = self._safe_divide(
            ins.net_profit,
            bs.total_equity
        ) * 100

        # ROA = 净利润 / 平均总资产
        roa = self._safe_divide(
            ins.net_profit,
            bs.total_assets
        ) * 100

        # 营业利润率 = 营业利润 / 营业收入
        operating_margin = self._safe_divide(
            ins.operating_profit,
            ins.operating_revenue
        ) * 100

        return ProfitabilityIndicators(
            gross_margin=gross_margin,
            net_margin=net_margin,
            roe=roe,
            roa=roa,
            operating_margin=operating_margin
        )

    def calculate_solvency_indicators(
        self,
        financial_data: FinancialData
    ) -> SolvencyIndicators:
        """计算偿债能力指标

        Args:
            financial_data: 财务数据

        Returns:
            SolvencyIndicators: 偿债能力指标
        """
        self.logger.debug("计算偿债能力指标")

        bs = financial_data.balance_sheet

        # 资产负债率 = 负债总额 / 资产总额
        debt_ratio = self._safe_divide(
            bs.total_liabilities,
            bs.total_assets
        ) * 100

        # 流动比率 = 流动资产 / 流动负债
        current_ratio = self._safe_divide(
            bs.current_assets,
            bs.current_liabilities
        )

        # 速动比率 = (流动资产 - 存货) / 流动负债
        quick_ratio = self._safe_divide(
            bs.current_assets - bs.inventory,
            bs.current_liabilities
        )

        # 产权比率 = 负债总额 / 所有者权益
        equity_ratio = self._safe_divide(
            bs.total_liabilities,
            bs.total_equity
        )

        return SolvencyIndicators(
            debt_ratio=debt_ratio,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            equity_ratio=equity_ratio
        )

    def calculate_operation_indicators(
        self,
        financial_data: FinancialData
    ) -> OperationIndicators:
        """计算运营能力指标

        Args:
            financial_data: 财务数据

        Returns:
            OperationIndicators: 运营能力指标
        """
        self.logger.debug("计算运营能力指标")

        bs = financial_data.balance_sheet
        ins = financial_data.income_statement

        # 存货周转率 = 营业成本 / 平均存货
        inventory_turnover = self._safe_divide(
            ins.operating_cost,
            bs.inventory
        )

        # 应收账款周转率 = 营业收入 / 平均应收账款
        receivable_turnover = self._safe_divide(
            ins.operating_revenue,
            bs.accounts_receivable
        )

        # 总资产周转率 = 营业收入 / 平均总资产
        total_asset_turnover = self._safe_divide(
            ins.operating_revenue,
            bs.total_assets
        )

        # 存货周转天数 = 365 / 存货周转率
        inventory_days = self._safe_divide(365, inventory_turnover)

        # 应收账款周转天数 = 365 / 应收账款周转率
        receivable_days = self._safe_divide(365, receivable_turnover)

        return OperationIndicators(
            inventory_turnover=inventory_turnover,
            receivable_turnover=receivable_turnover,
            total_asset_turnover=total_asset_turnover,
            inventory_days=inventory_days,
            receivable_days=receivable_days
        )

    def calculate_growth_indicators(
        self,
        financial_data: FinancialData,
        historical_data: Optional[List[FinancialData]] = None
    ) -> GrowthIndicators:
        """计算成长能力指标

        Args:
            financial_data: 当期财务数据
            historical_data: 历史财务数据列表

        Returns:
            GrowthIndicators: 成长能力指标
        """
        self.logger.debug("计算成长能力指标")

        # 如果没有历史数据，返回默认值
        if not historical_data or len(historical_data) == 0:
            self.logger.warning("无历史数据，成长指标设为0")
            return GrowthIndicators(
                revenue_growth=0.0,
                profit_growth=0.0,
                asset_growth=0.0,
                equity_growth=0.0
            )

        # 使用最近一期的历史数据
        last_period = historical_data[-1]

        # 营收增长率 = (本期营收 - 上期营收) / 上期营收
        revenue_growth = self._safe_divide(
            financial_data.income_statement.operating_revenue - last_period.income_statement.operating_revenue,
            last_period.income_statement.operating_revenue
        ) * 100

        # 净利润增长率 = (本期净利润 - 上期净利润) / 上期净利润
        profit_growth = self._safe_divide(
            financial_data.income_statement.net_profit - last_period.income_statement.net_profit,
            last_period.income_statement.net_profit
        ) * 100

        # 总资产增长率 = (本期总资产 - 上期总资产) / 上期总资产
        asset_growth = self._safe_divide(
            financial_data.balance_sheet.total_assets - last_period.balance_sheet.total_assets,
            last_period.balance_sheet.total_assets
        ) * 100

        # 净资产增长率 = (本期净资产 - 上期净资产) / 上期净资产
        equity_growth = self._safe_divide(
            financial_data.balance_sheet.total_equity - last_period.balance_sheet.total_equity,
            last_period.balance_sheet.total_equity
        ) * 100

        return GrowthIndicators(
            revenue_growth=revenue_growth,
            profit_growth=profit_growth,
            asset_growth=asset_growth,
            equity_growth=equity_growth
        )

    def calculate_cashflow_indicators(
        self,
        financial_data: FinancialData
    ) -> CashFlowIndicators:
        """计算现金流指标

        Args:
            financial_data: 财务数据

        Returns:
            CashFlowIndicators: 现金流指标
        """
        self.logger.debug("计算现金流指标")

        bs = financial_data.balance_sheet
        cfs = financial_data.cash_flow_statement

        # 自由现金流 = 经营现金流 - 资本性支出
        # 简化计算：使用投资现金流净额作为资本性支出的近似
        free_cash_flow = cfs.net_operating_cash + cfs.net_investing_cash

        # 现金债务覆盖率 = 现金 / 负债总额
        cash_to_debt = self._safe_divide(
            bs.cash,
            bs.total_liabilities
        )

        # 经营现金流债务覆盖率 = 经营现金流 / 负债总额
        operating_cash_to_debt = self._safe_divide(
            cfs.net_operating_cash,
            bs.total_liabilities
        )

        return CashFlowIndicators(
            free_cash_flow=free_cash_flow,
            cash_to_debt=cash_to_debt,
            operating_cash_to_debt=operating_cash_to_debt
        )

    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """安全除法，避免除零错误

        Args:
            numerator: 分子
            denominator: 分母

        Returns:
            float: 计算结果
        """
        if denominator == 0:
            return 0.0
        return numerator / denominator


def calculate_indicators(
    financial_data: FinancialData,
    historical_data: Optional[List[FinancialData]] = None
) -> Indicators:
    """计算财务指标（便捷函数）

    Args:
        financial_data: 当期财务数据
        historical_data: 历史财务数据列表

    Returns:
        Indicators: 财务指标对象
    """
    calculator = IndicatorCalculator()
    return calculator.calculate_indicators(financial_data, historical_data)
