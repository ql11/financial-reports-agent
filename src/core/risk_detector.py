"""
风险识别器模块

该模块负责识别财务风险、经营风险，划分风险等级。

功能特性：
- 识别财务风险
- 识别经营风险
- 划分风险等级
- 生成风险清单
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.models.indicators import Indicators
from src.models.risk import Risk, RiskList, RiskLevel, RiskType
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class RiskDetectorError(Exception):
    """风险识别器基础异常"""
    pass


class RiskDetector:
    """风险识别器

    负责识别财务风险、经营风险，划分风险等级。

    Attributes:
        logger: 日志器
        risk_thresholds: 风险阈值配置
    """

    def __init__(self, risk_thresholds_path: Optional[str] = None):
        """初始化风险识别器

        Args:
            risk_thresholds_path: 风险阈值配置文件路径
        """
        self.logger = get_logger('financial_analysis')
        self.risk_thresholds = self._load_risk_thresholds(risk_thresholds_path)
        self.logger.info("风险识别器初始化完成")

    def _load_risk_thresholds(self, path: Optional[str]) -> Dict[str, Any]:
        """加载风险阈值配置

        Args:
            path: 配置文件路径

        Returns:
            Dict[str, Any]: 风险阈值配置
        """
        if not path:
            path = "config/risk_thresholds.yaml"

        try:
            loader = ConfigLoader(path)
            return loader.get_all()
        except Exception as e:
            self.logger.warning(f"加载风险阈值配置失败: {e}，使用默认值")
            return self._get_default_thresholds()

    def _get_default_thresholds(self) -> Dict[str, Any]:
        """获取默认风险阈值

        Returns:
            Dict[str, Any]: 默认阈值配置
        """
        return {
            'solvency': {
                'debt_ratio': {'high': 0.7, 'medium': 0.6, 'low': 0.5},
                'current_ratio': {'high': 0.8, 'medium': 1.0, 'low': 1.5},
                'quick_ratio': {'high': 0.4, 'medium': 0.5, 'low': 1.0}
            },
            'profitability': {
                'gross_margin': {'high': 0.1, 'medium': 0.2, 'low': 0.3},
                'net_margin': {'high': 0.02, 'medium': 0.05, 'low': 0.1},
                'roe': {'high': 0.05, 'medium': 0.1, 'low': 0.15}
            },
            'growth': {
                'revenue_growth': {'high': -0.2, 'medium': -0.1, 'low': 0.0},
                'profit_growth': {'high': -0.3, 'medium': -0.1, 'low': 0.0}
            }
        }

    def detect_risks(
        self,
        indicators: Indicators,
        trend_analysis: Optional[Dict[str, Any]] = None
    ) -> RiskList:
        """识别所有风险

        Args:
            indicators: 财务指标
            trend_analysis: 趋势分析结果

        Returns:
            RiskList: 风险清单
        """
        self.logger.info(f"开始风险识别: {indicators.company_name}")

        risk_list = RiskList(
            company_name=indicators.company_name,
            report_year=indicators.report_year,
            risks=[],
            detection_time=datetime.now()
        )

        # 识别财务风险
        financial_risks = self.detect_financial_risks(indicators)
        for risk in financial_risks:
            risk_list.add_risk(risk)

        # 识别经营风险
        operation_risks = self.detect_operation_risks(indicators, trend_analysis)
        for risk in operation_risks:
            risk_list.add_risk(risk)

        self.logger.info(
            f"风险识别完成，共识别 {risk_list.total_risks} 项风险 "
            f"(高: {risk_list.high_risks}, 中: {risk_list.medium_risks}, 低: {risk_list.low_risks})"
        )

        return risk_list

    def detect_financial_risks(self, indicators: Indicators) -> List[Risk]:
        """识别财务风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 财务风险列表
        """
        self.logger.debug("识别财务风险")

        risks = []

        # 偿债能力风险
        risks.extend(self._check_solvency_risks(indicators))

        # 盈利能力风险
        risks.extend(self._check_profitability_risks(indicators))

        # 现金流风险
        risks.extend(self._check_cashflow_risks(indicators))

        return risks

    def detect_operation_risks(
        self,
        indicators: Indicators,
        trend_analysis: Optional[Dict[str, Any]] = None
    ) -> List[Risk]:
        """识别经营风险

        Args:
            indicators: 财务指标
            trend_analysis: 趋势分析结果

        Returns:
            List[Risk]: 经营风险列表
        """
        self.logger.debug("识别经营风险")

        risks = []

        # 成长能力风险
        risks.extend(self._check_growth_risks(indicators))

        # 运营能力风险
        risks.extend(self._check_operation_risks(indicators))

        # 趋势风险
        if trend_analysis:
            risks.extend(self._check_trend_risks(indicators, trend_analysis))

        return risks

    def _check_solvency_risks(self, indicators: Indicators) -> List[Risk]:
        """检查偿债能力风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 风险列表
        """
        risks = []
        solvency_thresholds = self.risk_thresholds.get('solvency', {})

        # 资产负债率风险
        debt_ratio = indicators.solvency.debt_ratio
        debt_thresholds = solvency_thresholds.get('debt_ratio', {})

        if debt_ratio > debt_thresholds.get('high', 70):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.HIGH,
                description="资产负债率过高，财务风险较大",
                indicator_name="资产负债率",
                indicator_value=debt_ratio,
                threshold=debt_thresholds['high'],
                impact="企业负债压力大，偿债能力不足，可能面临财务危机",
                recommendation="优化资本结构，降低负债比例，增加权益融资"
            ))
        elif debt_ratio > debt_thresholds.get('medium', 60):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.MEDIUM,
                description="资产负债率偏高，需关注财务风险",
                indicator_name="资产负债率",
                indicator_value=debt_ratio,
                threshold=debt_thresholds['medium'],
                impact="负债水平较高，财务杠杆较大",
                recommendation="适度控制负债规模，优化债务结构"
            ))

        # 流动比率风险
        current_ratio = indicators.solvency.current_ratio
        current_thresholds = solvency_thresholds.get('current_ratio', {})

        if current_ratio < current_thresholds.get('high', 0.8):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.HIGH,
                description="流动比率过低，短期偿债能力严重不足",
                indicator_name="流动比率",
                indicator_value=current_ratio,
                threshold=current_thresholds['high'],
                impact="短期偿债压力大，可能面临流动性危机",
                recommendation="增加流动资产，优化流动负债结构，提高短期偿债能力"
            ))
        elif current_ratio < current_thresholds.get('medium', 1.0):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.MEDIUM,
                description="流动比率偏低，短期偿债能力较弱",
                indicator_name="流动比率",
                indicator_value=current_ratio,
                threshold=current_thresholds['medium'],
                impact="短期偿债能力不足",
                recommendation="加强流动资产管理，提高流动比率"
            ))

        return risks

    def _check_profitability_risks(self, indicators: Indicators) -> List[Risk]:
        """检查盈利能力风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 风险列表
        """
        risks = []
        profitability_thresholds = self.risk_thresholds.get('profitability', {})

        # 毛利率风险
        gross_margin = indicators.profitability.gross_margin
        gross_thresholds = profitability_thresholds.get('gross_margin', {})

        if gross_margin < gross_thresholds.get('high', 10):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.HIGH,
                description="毛利率过低，产品竞争力严重不足",
                indicator_name="毛利率",
                indicator_value=gross_margin,
                threshold=gross_thresholds['high'],
                impact="盈利能力弱，产品缺乏市场竞争力",
                recommendation="优化产品结构，降低成本，提高产品附加值"
            ))

        # 净利率风险
        net_margin = indicators.profitability.net_margin
        net_thresholds = profitability_thresholds.get('net_margin', {})

        if net_margin < net_thresholds.get('high', 2):
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.HIGH,
                description="净利率过低，盈利能力严重不足",
                indicator_name="净利率",
                indicator_value=net_margin,
                threshold=net_thresholds['high'],
                impact="净利润率低，企业盈利能力弱",
                recommendation="控制费用支出，提高运营效率，增加收入"
            ))

        return risks

    def _check_cashflow_risks(self, indicators: Indicators) -> List[Risk]:
        """检查现金流风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 风险列表
        """
        risks = []

        # 自由现金流风险
        free_cash_flow = indicators.cashflow.free_cash_flow

        if free_cash_flow < 0:
            risks.append(Risk(
                risk_type=RiskType.FINANCIAL,
                risk_level=RiskLevel.HIGH,
                description="自由现金流为负，资金链紧张",
                indicator_name="自由现金流",
                indicator_value=free_cash_flow,
                threshold=0,
                impact="资金链紧张，可能面临流动性危机",
                recommendation="加强现金流管理，优化资本支出，提高经营现金流"
            ))

        return risks

    def _check_growth_risks(self, indicators: Indicators) -> List[Risk]:
        """检查成长能力风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 风险列表
        """
        risks = []
        growth_thresholds = self.risk_thresholds.get('growth', {})

        # 营收增长率风险
        revenue_growth = indicators.growth.revenue_growth
        revenue_thresholds = growth_thresholds.get('revenue_growth', {})

        if revenue_growth < revenue_thresholds.get('high', -20):
            risks.append(Risk(
                risk_type=RiskType.OPERATION,
                risk_level=RiskLevel.HIGH,
                description="营收大幅下滑，业务萎缩严重",
                indicator_name="营收增长率",
                indicator_value=revenue_growth,
                threshold=revenue_thresholds['high'],
                impact="业务规模快速萎缩，市场份额下降",
                recommendation="分析营收下滑原因，调整经营策略，开拓新市场"
            ))
        elif revenue_growth < revenue_thresholds.get('medium', -10):
            risks.append(Risk(
                risk_type=RiskType.OPERATION,
                risk_level=RiskLevel.MEDIUM,
                description="营收负增长，业务出现萎缩",
                indicator_name="营收增长率",
                indicator_value=revenue_growth,
                threshold=revenue_thresholds['medium'],
                impact="业务规模萎缩，需关注市场变化",
                recommendation="加强市场开拓，提升产品竞争力"
            ))

        # 净利润增长率风险
        profit_growth = indicators.growth.profit_growth
        profit_thresholds = growth_thresholds.get('profit_growth', {})

        if profit_growth < profit_thresholds.get('high', -30):
            risks.append(Risk(
                risk_type=RiskType.OPERATION,
                risk_level=RiskLevel.HIGH,
                description="净利润大幅下滑，盈利能力急剧下降",
                indicator_name="净利润增长率",
                indicator_value=profit_growth,
                threshold=profit_thresholds['high'],
                impact="盈利能力快速下降，经营状况恶化",
                recommendation="分析利润下滑原因，控制成本费用，提升盈利能力"
            ))

        return risks

    def _check_operation_risks(self, indicators: Indicators) -> List[Risk]:
        """检查运营能力风险

        Args:
            indicators: 财务指标

        Returns:
            List[Risk]: 风险列表
        """
        risks = []
        operation_thresholds = self.risk_thresholds.get('operation', {})

        # 存货周转率风险
        inventory_turnover = indicators.operation.inventory_turnover
        inventory_thresholds = operation_thresholds.get('inventory_turnover', {})

        if inventory_turnover < inventory_thresholds.get('high', 2):
            risks.append(Risk(
                risk_type=RiskType.OPERATION,
                risk_level=RiskLevel.HIGH,
                description="存货周转率过低，存货积压严重",
                indicator_name="存货周转率",
                indicator_value=inventory_turnover,
                threshold=inventory_thresholds['high'],
                impact="存货积压，资金占用大，存在跌价风险",
                recommendation="加强存货管理，优化库存结构，加快存货周转"
            ))

        return risks

    def _check_trend_risks(
        self,
        indicators: Indicators,
        trend_analysis: Dict[str, Any]
    ) -> List[Risk]:
        """检查趋势风险

        Args:
            indicators: 财务指标
            trend_analysis: 趋势分析结果

        Returns:
            List[Risk]: 风险列表
        """
        risks = []

        # 检查盈利能力下降趋势
        profitability_trend = trend_analysis.get('profitability_trend', {})
        roe_trend = profitability_trend.get('净资产收益率(ROE)', {})

        if roe_trend.get('direction') == '下降':
            risks.append(Risk(
                risk_type=RiskType.WARNING,
                risk_level=RiskLevel.LOW,
                description="ROE呈下降趋势，盈利能力持续下滑",
                indicator_name="净资产收益率(ROE)",
                indicator_value=roe_trend.get('latest_value', 0),
                threshold=roe_trend.get('earliest_value', 0),
                impact="盈利能力持续下降，需关注经营状况",
                recommendation="分析盈利下降原因，采取措施提升盈利能力"
            ))

        return risks


def detect_risks(
    indicators: Indicators,
    trend_analysis: Optional[Dict[str, Any]] = None
) -> RiskList:
    """识别风险（便捷函数）

    Args:
        indicators: 财务指标
        trend_analysis: 趋势分析结果

    Returns:
        RiskList: 风险清单
    """
    detector = RiskDetector()
    return detector.detect_risks(indicators, trend_analysis)
