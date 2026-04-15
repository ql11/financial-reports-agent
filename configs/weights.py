"""
权重配置模块
"""

import os
import yaml
from typing import Dict, Any, Optional

# 默认权重配置
DEFAULT_WEIGHTS = {
    "fraud_patterns": {
        "revenue_profit_divergence": 1.5,
        "cash_flow_profit_divergence": 1.8,
        "receivables_growth_vs_revenue": 1.2,
        "inventory_growth_vs_revenue": 1.1,
        "asset_quality_issues": 1.3,
        "accounting_policy_changes": 1.4,
        "related_party_transactions": 1.6,
        "audit_opinion_issues": 1.7,
        "executive_turnover": 1.0,
        "delayed_filing": 1.2
    },
    "financial_ratios": {
        "profitability": 1.0,
        "liquidity": 0.8,
        "solvency": 1.2,
        "efficiency": 0.9,
        "growth": 1.1
    },
    "risk_levels": {
        "low": 0.5,
        "medium": 1.0,
        "high": 1.5,
        "critical": 2.0
    }
}


def load_weights(config_path: str = None) -> Dict[str, Any]:
    """
    加载权重配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        权重配置字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "weights.yaml")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                weights = yaml.safe_load(f)
            return weights
        except Exception as e:
            print(f"警告: 无法加载权重配置文件 {config_path}: {e}")
            print("使用默认权重配置")
            return DEFAULT_WEIGHTS
    else:
        print(f"警告: 权重配置文件 {config_path} 不存在")
        print("使用默认权重配置")
        return DEFAULT_WEIGHTS


def get_fraud_pattern_weight(pattern_name: str) -> Optional[float]:
    """
    获取造假模式的权重
    
    Args:
        pattern_name: 造假模式名称
        
    Returns:
        权重值，如果未找到则返回None
    """
    weights = load_weights()
    
    try:
        fraud_patterns = weights.get("fraud_patterns", {})
        return fraud_patterns.get(pattern_name)
    except (KeyError, AttributeError):
        return None


def get_financial_ratio_weight(category: str) -> Optional[float]:
    """
    获取财务比率类别的权重
    
    Args:
        category: 财务比率类别
        
    Returns:
        权重值，如果未找到则返回None
    """
    weights = load_weights()
    
    try:
        financial_ratios = weights.get("financial_ratios", {})
        return financial_ratios.get(category)
    except (KeyError, AttributeError):
        return None


def get_risk_level_weight(risk_level: str) -> Optional[float]:
    """
    获取风险等级的权重
    
    Args:
        risk_level: 风险等级（low, medium, high, critical）
        
    Returns:
        权重值，如果未找到则返回None
    """
    weights = load_weights()
    
    try:
        risk_levels = weights.get("risk_levels", {})
        return risk_levels.get(risk_level.lower())
    except (KeyError, AttributeError):
        return None


def save_weights(weights: Dict[str, Any], config_path: str = None) -> bool:
    """
    保存权重配置到文件
    
    Args:
        weights: 权重配置字典
        config_path: 配置文件路径
        
    Returns:
        是否保存成功
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "weights.yaml")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(weights, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"错误: 无法保存权重配置到 {config_path}: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    weights = load_weights()
    print(f"加载的权重配置: {len(weights)} 个类别")
    
    # 测试获取权重
    revenue_profit_weight = get_fraud_pattern_weight("revenue_profit_divergence")
    print(f"业绩背离权重: {revenue_profit_weight}")
    
    profitability_weight = get_financial_ratio_weight("profitability")
    print(f"盈利能力权重: {profitability_weight}")
    
    high_risk_weight = get_risk_level_weight("high")
    print(f"高风险权重: {high_risk_weight}")
    
    # 测试保存
    if save_weights(weights):
        print("权重配置保存成功")
    else:
        print("权重配置保存失败")