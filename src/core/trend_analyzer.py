"""
趋势分析器模块

该模块负责分析财务指标的趋势、进行行业和同行对比。

功能特性：
- 分析多年财务指标趋势
- 与行业基准对比
- 与同行公司对比
- 生成趋势分析结论
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import pandas as pd
import numpy as np

from src.models.indicators import Indicators
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class TrendAnalyzerError(Exception):
    """趋势分析器基础异常"""
    pass


class InsufficientDataError(TrendAnalyzerError):
    """数据不足异常"""
    pass


class TrendAnalyzer:
    """趋势分析器

    负责分析财务指标的趋势、进行行业和同行对比。

    Attributes:
        logger: 日志器
        industry_benchmarks: 行业基准数据
    """

    def __init__(self, industry_benchmarks_path: Optional[str] = None):
        """初始化趋势分析器

        Args:
            industry_benchmarks_path: 行业基准数据文件路径
        """
        self.logger = get_logger('financial_analysis')
        self.industry_benchmarks = self._load_industry_benchmarks(industry_benchmarks_path)
        self.logger.info("趋势分析器初始化完成")

    def _load_industry_benchmarks(self, path: Optional[str]) -> Dict[str, Any]:
        """加载行业基准数据

        Args:
            path: 配置文件路径

        Returns:
            Dict[str, Any]: 行业基准数据
        """
        if not path:
            path = "config/industry_benchmarks.yaml"

        try:
            loader = ConfigLoader(path)
            return loader.get('industries', {})
        except Exception as e:
            self.logger.warning(f"加载行业基准数据失败: {e}，使用默认值")
            return {}

    def analyze_trend(
        self,
        indicators_list: List[Indicators],
        min_years: int = 2
    ) -> Dict[str, Any]:
        """分析财务指标趋势

        Args:
            indicators_list: 多年财务指标列表
            min_years: 最小年份数

        Returns:
            Dict[str, Any]: 趋势分析结果

        Raises:
            InsufficientDataError: 数据不足时抛出
        """
        if len(indicators_list) < min_years:
            raise InsufficientDataError(
                f"数据不足，至少需要 {min_years} 年数据，当前只有 {len(indicators_list)} 年"
            )

        self.logger.info(f"开始趋势分析，共 {len(indicators_list)} 年数据")

        # 按年份排序
        sorted_indicators = sorted(indicators_list, key=lambda x: x.report_year)

        # 分析各类指标趋势
        trend_analysis = {
            'company_name': sorted_indicators[0].company_name,
            'years': [ind.report_year for ind in sorted_indicators],
            'profitability_trend': self._analyze_category_trend(
                sorted_indicators, 'profitability'
            ),
            'solvency_trend': self._analyze_category_trend(
                sorted_indicators, 'solvency'
            ),
            'operation_trend': self._analyze_category_trend(
                sorted_indicators, 'operation'
            ),
            'growth_trend': self._analyze_category_trend(
                sorted_indicators, 'growth'
            ),
            'cashflow_trend': self._analyze_category_trend(
                sorted_indicators, 'cashflow'
            ),
            'analysis_time': datetime.now()
        }

        # 生成综合趋势结论
        trend_analysis['overall_conclusion'] = self._generate_overall_conclusion(trend_analysis)

        self.logger.info("趋势分析完成")
        return trend_analysis

    def _analyze_category_trend(
        self,
        indicators_list: List[Indicators],
        category: str
    ) -> Dict[str, Any]:
        """分析单个类别指标趋势

        Args:
            indicators_list: 指标列表
            category: 类别名称

        Returns:
            Dict[str, Any]: 类别趋势分析结果
        """
        # 提取该类别的所有指标
        category_data = []
        for ind in indicators_list:
            category_obj = getattr(ind, category)
            category_dict = category_obj.to_dict()
            category_data.append({
                'year': ind.report_year,
                **category_dict
            })

        # 转换为DataFrame
        df = pd.DataFrame(category_data)

        # 分析每个指标的趋势
        trend_results = {}
        indicator_names = [col for col in df.columns if col != 'year']

        for indicator in indicator_names:
            values = df[indicator].values

            # 计算趋势
            if len(values) >= 2:
                # 简单线性趋势
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]

                # 平均变化率
                avg_change = (values[-1] - values[0]) / len(values)

                # 趋势方向
                if slope > 0:
                    direction = "上升"
                elif slope < 0:
                    direction = "下降"
                else:
                    direction = "平稳"

                trend_results[indicator] = {
                    'values': values.tolist(),
                    'slope': float(slope),
                    'avg_change': float(avg_change),
                    'direction': direction,
                    'latest_value': float(values[-1]),
                    'earliest_value': float(values[0])
                }

        return trend_results

    def compare_with_industry(
        self,
        indicators: Indicators,
        industry: str = 'default'
    ) -> Dict[str, Any]:
        """与行业基准对比

        Args:
            indicators: 财务指标
            industry: 行业名称

        Returns:
            Dict[str, Any]: 对比结果
        """
        self.logger.info(f"开始行业对比，行业: {industry}")

        # 获取行业基准
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks.get('default', {}))

        if not benchmark:
            self.logger.warning(f"未找到行业基准: {industry}")
            return {'error': f"未找到行业基准: {industry}"}

        # 对比各类指标
        comparison = {
            'company_name': indicators.company_name,
            'industry': industry,
            'industry_name': benchmark.get('name', industry),
            'profitability_comparison': self._compare_category(
                indicators.profitability.to_dict(),
                benchmark.get('profitability', {})
            ),
            'solvency_comparison': self._compare_category(
                indicators.solvency.to_dict(),
                benchmark.get('solvency', {})
            ),
            'operation_comparison': self._compare_category(
                indicators.operation.to_dict(),
                benchmark.get('operation', {})
            ),
            'growth_comparison': self._compare_category(
                indicators.growth.to_dict(),
                benchmark.get('growth', {})
            ),
            'comparison_time': datetime.now()
        }

        # 生成对比结论
        comparison['overall_conclusion'] = self._generate_comparison_conclusion(comparison)

        self.logger.info("行业对比完成")
        return comparison

    def _compare_category(
        self,
        company_data: Dict[str, float],
        benchmark_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """对比单个类别指标

        Args:
            company_data: 公司指标数据
            benchmark_data: 基准数据

        Returns:
            Dict[str, Any]: 对比结果
        """
        comparison = {}

        for indicator, value in company_data.items():
            benchmark_value = benchmark_data.get(indicator)

            if benchmark_value is not None and benchmark_value != 0:
                # 计算差异
                difference = value - benchmark_value
                percentage = (value / benchmark_value - 1) * 100

                # 判断优劣
                if percentage > 10:
                    status = "优于行业"
                elif percentage < -10:
                    status = "劣于行业"
                else:
                    status = "接近行业"

                comparison[indicator] = {
                    'company_value': value,
                    'benchmark_value': benchmark_value,
                    'difference': difference,
                    'percentage': percentage,
                    'status': status
                }
            else:
                comparison[indicator] = {
                    'company_value': value,
                    'benchmark_value': None,
                    'status': '无基准数据'
                }

        return comparison

    def compare_with_peers(
        self,
        indicators: Indicators,
        peer_indicators: List[Indicators]
    ) -> Dict[str, Any]:
        """与同行公司对比

        Args:
            indicators: 本公司财务指标
            peer_indicators: 同行公司财务指标列表

        Returns:
            Dict[str, Any]: 对比结果
        """
        if not peer_indicators:
            self.logger.warning("无同行公司数据")
            return {'error': '无同行公司数据'}

        self.logger.info(f"开始同行对比，共 {len(peer_indicators)} 家公司")

        # 计算同行平均值
        peer_avg = self._calculate_peer_average(peer_indicators)

        # 对比
        comparison = {
            'company_name': indicators.company_name,
            'peer_count': len(peer_indicators),
            'peer_names': [ind.company_name for ind in peer_indicators],
            'profitability_comparison': self._compare_category(
                indicators.profitability.to_dict(),
                peer_avg['profitability']
            ),
            'solvency_comparison': self._compare_category(
                indicators.solvency.to_dict(),
                peer_avg['solvency']
            ),
            'operation_comparison': self._compare_category(
                indicators.operation.to_dict(),
                peer_avg['operation']
            ),
            'growth_comparison': self._compare_category(
                indicators.growth.to_dict(),
                peer_avg['growth']
            ),
            'comparison_time': datetime.now()
        }

        self.logger.info("同行对比完成")
        return comparison

    def _calculate_peer_average(
        self,
        peer_indicators: List[Indicators]
    ) -> Dict[str, Dict[str, float]]:
        """计算同行平均值

        Args:
            peer_indicators: 同行公司指标列表

        Returns:
            Dict[str, Dict[str, float]]: 各类指标平均值
        """
        categories = ['profitability', 'solvency', 'operation', 'growth', 'cashflow']
        averages = {}

        for category in categories:
            # 收集所有公司的该类别指标
            all_values = {}
            for ind in peer_indicators:
                category_obj = getattr(ind, category)
                category_dict = category_obj.to_dict()

                for key, value in category_dict.items():
                    if key not in all_values:
                        all_values[key] = []
                    all_values[key].append(value)

            # 计算平均值
            averages[category] = {
                key: np.mean(values) for key, values in all_values.items()
            }

        return averages

    def _generate_overall_conclusion(self, trend_analysis: Dict[str, Any]) -> str:
        """生成综合趋势结论

        Args:
            trend_analysis: 趋势分析结果

        Returns:
            str: 综合结论
        """
        conclusions = []

        # 分析盈利能力趋势
        profitability_trend = trend_analysis['profitability_trend']
        if profitability_trend:
            roe_trend = profitability_trend.get('净资产收益率(ROE)', {})
            if roe_trend.get('direction') == '上升':
                conclusions.append("盈利能力持续改善")
            elif roe_trend.get('direction') == '下降':
                conclusions.append("盈利能力有所下滑")

        # 分析偿债能力趋势
        solvency_trend = trend_analysis['solvency_trend']
        if solvency_trend:
            debt_trend = solvency_trend.get('资产负债率', {})
            if debt_trend.get('direction') == '上升':
                conclusions.append("负债水平上升，需关注财务风险")
            elif debt_trend.get('direction') == '下降':
                conclusions.append("负债水平下降，财务结构优化")

        # 分析成长能力趋势
        growth_trend = trend_analysis['growth_trend']
        if growth_trend:
            revenue_trend = growth_trend.get('营收增长率', {})
            if revenue_trend.get('direction') == '上升':
                conclusions.append("营收增长加速")
            elif revenue_trend.get('direction') == '下降':
                conclusions.append("营收增长放缓")

        if not conclusions:
            conclusions.append("整体财务状况保持稳定")

        return "；".join(conclusions)

    def _generate_comparison_conclusion(self, comparison: Dict[str, Any]) -> str:
        """生成对比结论

        Args:
            comparison: 对比结果

        Returns:
            str: 对比结论
        """
        conclusions = []

        # 统计各类指标表现
        for category in ['profitability_comparison', 'solvency_comparison',
                         'operation_comparison', 'growth_comparison']:
            category_comparison = comparison.get(category, {})

            better_count = 0
            worse_count = 0

            for indicator, result in category_comparison.items():
                if result.get('status') == '优于行业':
                    better_count += 1
                elif result.get('status') == '劣于行业':
                    worse_count += 1

            if better_count > worse_count:
                conclusions.append(f"{category.split('_')[0]}表现优于行业平均")
            elif worse_count > better_count:
                conclusions.append(f"{category.split('_')[0]}表现劣于行业平均")

        if not conclusions:
            conclusions.append("整体表现接近行业平均水平")

        return "；".join(conclusions)


def analyze_trend(
    indicators_list: List[Indicators],
    min_years: int = 2
) -> Dict[str, Any]:
    """分析趋势（便捷函数）

    Args:
        indicators_list: 指标列表
        min_years: 最小年份数

    Returns:
        Dict[str, Any]: 趋势分析结果
    """
    analyzer = TrendAnalyzer()
    return analyzer.analyze_trend(indicators_list, min_years)
