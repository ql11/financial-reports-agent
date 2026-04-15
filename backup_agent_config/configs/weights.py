"""
权重配置加载工具
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_weights(config_path: str = None) -> Dict[str, Any]:
    """加载权重配置
    
    Args:
        config_path: 配置文件路径，默认为configs/weights.yaml
        
    Returns:
        Dict[str, Any]: 权重配置字典
    """
    if config_path is None:
        config_path = Path(__file__).parent / "weights.yaml"
    else:
        config_path = Path(config_path)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            weights = yaml.safe_load(f)
        
        logger.info(f"权重配置已加载: {config_path}")
        return weights or {}
        
    except FileNotFoundError:
        logger.warning(f"权重配置文件不存在: {config_path}，使用默认配置")
        return _get_default_weights()
    except Exception as e:
        logger.error(f"加载权重配置失败: {e}")
        return _get_default_weights()


def _get_default_weights() -> Dict[str, Any]:
    """获取默认权重配置"""
    return {
        "fraud_pattern_weights": {
            "revenue_profit_divergence": 1.2,
            "cash_flow_divergence": 1.5,
            "receivables_anomalies": 1.0,
            "inventory_anomalies": 1.0,
            "subsidy_manipulation": 0.8,
            "capacity_anomalies": 0.7,
            "related_party_issues": 1.3,
            "accounting_changes": 0.5,
            "audit_issues": 2.0,
            "historical_violations": 1.8
        },
        "risk_indicator_weights": {
            "gross_margin": 1.0,
            "net_margin": 1.2,
            "roe": 1.5,
            "roa": 1.3,
            "debt_ratio": 1.4,
            "current_ratio": 1.1,
            "quick_ratio": 1.2,
            "inventory_turnover": 0.9,
            "receivables_turnover": 1.0,
            "total_asset_turnover": 0.8,
            "revenue_growth": 1.2,
            "profit_growth": 1.5,
            "cash_flow_growth": 1.3
        },
        "industry_adjustments": {
            "manufacturing": {
                "inventory_turnover": 1.2,
                "receivables_turnover": 1.1,
                "total_asset_turnover": 0.9
            },
            "technology": {
                "gross_margin": 1.3,
                "net_margin": 1.4,
                "revenue_growth": 1.5
            },
            "retail": {
                "inventory_turnover": 1.4,
                "gross_margin": 0.8,
                "current_ratio": 1.2
            },
            "real_estate": {
                "debt_ratio": 1.6,
                "current_ratio": 1.3,
                "quick_ratio": 1.2
            }
        },
        "size_adjustments": {
            "large_cap": {
                "revenue_growth": 0.8,
                "profit_growth": 0.9,
                "volatility": 0.7
            },
            "mid_cap": {
                "revenue_growth": 1.0,
                "profit_growth": 1.0,
                "volatility": 1.0
            },
            "small_cap": {
                "revenue_growth": 1.3,
                "profit_growth": 1.4,
                "volatility": 1.5
            }
        },
        "time_weights": {
            "current_year": 1.0,
            "previous_year": 0.8,
            "two_years_ago": 0.6,
            "three_years_ago": 0.4,
            "older": 0.2
        },
        "audit_opinion_weights": {
            "standard_unqualified": 1.0,
            "unqualified": 1.0,
            "qualified": 1.5,
            "adverse": 2.0,
            "disclaimer": 2.5,
            "unqualified_with_emphasis": 1.2,
            "unqualified_with_other": 1.2
        },
        "historical_violation_weights": {
            "warning": 1.2,
            "criticism": 1.5,
            "fine": 2.0,
            "suspension": 2.5,
            "delisting": 3.0
        },
        "composite_weights": {
            "financial_ratios": 0.3,
            "growth_trends": 0.25,
            "fraud_patterns": 0.35,
            "external_factors": 0.1
        }
    }


def get_fraud_pattern_weight(pattern_name: str) -> float:
    """获取造假模式权重
    
    Args:
        pattern_name: 造假模式名称
        
    Returns:
        float: 权重值
    """
    weights = load_weights()
    pattern_weights = weights.get("fraud_pattern_weights", {})
    return pattern_weights.get(pattern_name, 1.0)


def get_risk_indicator_weight(indicator_name: str) -> float:
    """获取风险指标权重
    
    Args:
        indicator_name: 风险指标名称
        
    Returns:
        float: 权重值
    """
    weights = load_weights()
    indicator_weights = weights.get("risk_indicator_weights", {})
    return indicator_weights.get(indicator_name, 1.0)


def get_industry_adjustment(industry: str, indicator: str) -> float:
    """获取行业调整系数
    
    Args:
        industry: 行业类型
        indicator: 指标名称
        
    Returns:
        float: 调整系数
    """
    weights = load_weights()
    industry_adjustments = weights.get("industry_adjustments", {})
    industry_weights = industry_adjustments.get(industry, {})
    return industry_weights.get(indicator, 1.0)


def get_size_adjustment(size: str, indicator: str) -> float:
    """获取公司规模调整系数
    
    Args:
        size: 公司规模（large_cap, mid_cap, small_cap）
        indicator: 指标名称
        
    Returns:
        float: 调整系数
    """
    weights = load_weights()
    size_adjustments = weights.get("size_adjustments", {})
    size_weights = size_adjustments.get(size, {})
    return size_weights.get(indicator, 1.0)


def get_time_weight(years_ago: int) -> float:
    """获取时间权重
    
    Args:
        years_ago: 多少年前
        
    Returns:
        float: 时间权重
    """
    weights = load_weights()
    time_weights = weights.get("time_weights", {})
    
    if years_ago == 0:
        return time_weights.get("current_year", 1.0)
    elif years_ago == 1:
        return time_weights.get("previous_year", 0.8)
    elif years_ago == 2:
        return time_weights.get("two_years_ago", 0.6)
    elif years_ago == 3:
        return time_weights.get("three_years_ago", 0.4)
    else:
        return time_weights.get("older", 0.2)


def get_audit_opinion_weight(opinion: str) -> float:
    """获取审计意见权重
    
    Args:
        opinion: 审计意见
        
    Returns:
        float: 权重值
    """
    weights = load_weights()
    audit_weights = weights.get("audit_opinion_weights", {})
    
    # 尝试匹配审计意见
    opinion_lower = opinion.lower()
    
    if "标准无保留" in opinion_lower:
        return audit_weights.get("standard_unqualified", 1.0)
    elif "无保留" in opinion_lower and ("强调" in opinion_lower or "其他" in opinion_lower):
        if "强调" in opinion_lower:
            return audit_weights.get("unqualified_with_emphasis", 1.2)
        else:
            return audit_weights.get("unqualified_with_other", 1.2)
    elif "无保留" in opinion_lower:
        return audit_weights.get("unqualified", 1.0)
    elif "保留" in opinion_lower:
        return audit_weights.get("qualified", 1.5)
    elif "否定" in opinion_lower:
        return audit_weights.get("adverse", 2.0)
    elif "无法表示" in opinion_lower:
        return audit_weights.get("disclaimer", 2.5)
    else:
        return 1.0  # 默认权重


def get_historical_violation_weight(violation_type: str) -> float:
    """获取历史违规权重
    
    Args:
        violation_type: 违规类型
        
    Returns:
        float: 权重值
    """
    weights = load_weights()
    violation_weights = weights.get("historical_violation_weights", {})
    return violation_weights.get(violation_type, 1.0)


def get_composite_weight(component: str) -> float:
    """获取综合权重
    
    Args:
        component: 组件名称（financial_ratios, growth_trends, fraud_patterns, external_factors）
        
    Returns:
        float: 权重值
    """
    weights = load_weights()
    composite_weights = weights.get("composite_weights", {})
    return composite_weights.get(component, 0.25)  # 默认平均分配