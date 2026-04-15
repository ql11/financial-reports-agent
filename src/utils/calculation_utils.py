"""
计算工具函数
"""

from typing import Dict, List, Optional, Union
import numpy as np


def calculate_ratios(financial_data: Dict[str, float]) -> Dict[str, float]:
    """计算财务比率
    
    Args:
        financial_data: 财务数据字典
        
    Returns:
        Dict[str, float]: 财务比率字典
    """
    ratios = {}
    
    # 提取数据
    operating_revenue = financial_data.get("operating_revenue", 0)
    gross_profit = financial_data.get("gross_profit", 0)
    net_profit = financial_data.get("net_profit", 0)
    total_assets = financial_data.get("total_assets", 0)
    total_equity = financial_data.get("total_equity", 0)
    total_liabilities = financial_data.get("total_liabilities", 0)
    current_assets = financial_data.get("current_assets", 0)
    current_liabilities = financial_data.get("current_liabilities", 0)
    inventory = financial_data.get("inventory", 0)
    accounts_receivable = financial_data.get("accounts_receivable", 0)
    
    # 盈利能力比率
    if operating_revenue > 0:
        ratios["gross_margin"] = (gross_profit / operating_revenue) * 100  # 毛利率
        ratios["net_margin"] = (net_profit / operating_revenue) * 100  # 净利率
    
    if total_equity > 0:
        ratios["roe"] = (net_profit / total_equity) * 100  # 净资产收益率
    
    if total_assets > 0:
        ratios["roa"] = (net_profit / total_assets) * 100  # 总资产收益率
    
    # 偿债能力比率
    if total_assets > 0:
        ratios["debt_ratio"] = (total_liabilities / total_assets) * 100  # 资产负债率
    
    if current_liabilities > 0:
        ratios["current_ratio"] = current_assets / current_liabilities  # 流动比率
        quick_assets = current_assets - inventory
        ratios["quick_ratio"] = quick_assets / current_liabilities  # 速动比率
    
    # 运营能力比率
    if inventory > 0 and operating_revenue > 0:
        # 简化计算，实际应使用平均存货
        ratios["inventory_turnover"] = operating_revenue / inventory  # 存货周转率
    
    if accounts_receivable > 0 and operating_revenue > 0:
        # 简化计算，实际应使用平均应收账款
        ratios["receivables_turnover"] = operating_revenue / accounts_receivable  # 应收账款周转率
    
    if total_assets > 0 and operating_revenue > 0:
        ratios["total_asset_turnover"] = operating_revenue / total_assets  # 总资产周转率
    
    return ratios


def calculate_growth(current_value: float, previous_value: float) -> float:
    """计算增长率
    
    Args:
        current_value: 当前值
        previous_value: 前期值
        
    Returns:
        float: 增长率（百分比）
    """
    if previous_value == 0:
        return 0.0
    
    return ((current_value - previous_value) / abs(previous_value)) * 100


def calculate_trend(values: List[float]) -> Dict[str, float]:
    """计算趋势
    
    Args:
        values: 数值列表
        
    Returns:
        Dict[str, float]: 趋势统计
    """
    if not values:
        return {}
    
    values_array = np.array(values)
    
    trend = {
        "mean": float(np.mean(values_array)),
        "median": float(np.median(values_array)),
        "std": float(np.std(values_array)),
        "min": float(np.min(values_array)),
        "max": float(np.max(values_array)),
        "range": float(np.max(values_array) - np.min(values_array))
    }
    
    # 计算趋势（简单线性回归斜率）
    if len(values_array) > 1:
        x = np.arange(len(values_array))
        slope, _ = np.polyfit(x, values_array, 1)
        trend["slope"] = float(slope)
        
        # 判断趋势方向
        if slope > 0.1:
            trend["direction"] = "上升"
        elif slope < -0.1:
            trend["direction"] = "下降"
        else:
            trend["direction"] = "平稳"
    else:
        trend["slope"] = 0.0
        trend["direction"] = "未知"
    
    return trend


def calculate_percentage_change(current: float, previous: float) -> float:
    """计算百分比变化
    
    Args:
        current: 当前值
        previous: 前期值
        
    Returns:
        float: 百分比变化
    """
    if previous == 0:
        return 0.0
    
    return ((current - previous) / previous) * 100


def calculate_compound_growth_rate(values: List[float]) -> float:
    """计算复合增长率
    
    Args:
        values: 数值列表（按时间顺序）
        
    Returns:
        float: 复合增长率（百分比）
    """
    if len(values) < 2:
        return 0.0
    
    first_value = values[0]
    last_value = values[-1]
    n_periods = len(values) - 1
    
    if first_value == 0:
        return 0.0
    
    cagr = (last_value / first_value) ** (1 / n_periods) - 1
    return cagr * 100


def calculate_z_score(value: float, mean: float, std: float) -> float:
    """计算Z分数
    
    Args:
        value: 数值
        mean: 均值
        std: 标准差
        
    Returns:
        float: Z分数
    """
    if std == 0:
        return 0.0
    
    return (value - mean) / std


def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
    """检测异常值
    
    Args:
        values: 数值列表
        threshold: Z分数阈值
        
    Returns:
        List[int]: 异常值索引列表
    """
    if len(values) < 3:
        return []
    
    values_array = np.array(values)
    mean = np.mean(values_array)
    std = np.std(values_array)
    
    if std == 0:
        return []
    
    z_scores = np.abs((values_array - mean) / std)
    outliers = np.where(z_scores > threshold)[0]
    
    return outliers.tolist()


def calculate_correlation(x: List[float], y: List[float]) -> float:
    """计算相关系数
    
    Args:
        x: 变量X
        y: 变量Y
        
    Returns:
        float: 相关系数
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    x_array = np.array(x)
    y_array = np.array(y)
    
    correlation = np.corrcoef(x_array, y_array)[0, 1]
    
    # 处理NaN
    if np.isnan(correlation):
        return 0.0
    
    return float(correlation)


def normalize_values(values: List[float]) -> List[float]:
    """归一化数值（0-1）
    
    Args:
        values: 数值列表
        
    Returns:
        List[float]: 归一化后的数值
    """
    if not values:
        return []
    
    values_array = np.array(values)
    min_val = np.min(values_array)
    max_val = np.max(values_array)
    
    if max_val == min_val:
        return [0.5] * len(values)
    
    normalized = (values_array - min_val) / (max_val - min_val)
    return normalized.tolist()