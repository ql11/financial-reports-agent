"""
阈值配置模块
"""

import os
import yaml
from typing import Dict, Any, Optional

# 默认阈值配置
DEFAULT_THRESHOLDS = {
    "profitability": {
        "gross_margin": {"warning": 0.2, "critical": 0.1},
        "operating_margin": {"warning": 0.1, "critical": 0.05},
        "net_margin": {"warning": 0.05, "critical": 0.02},
        "roe": {"warning": 0.1, "critical": 0.05},
        "roa": {"warning": 0.05, "critical": 0.02}
    },
    "liquidity": {
        "current_ratio": {"warning": 1.5, "critical": 1.0},
        "quick_ratio": {"warning": 1.0, "critical": 0.5},
        "cash_ratio": {"warning": 0.2, "critical": 0.1}
    },
    "solvency": {
        "debt_to_equity": {"warning": 2.0, "critical": 3.0},
        "debt_to_assets": {"warning": 0.6, "critical": 0.8},
        "interest_coverage": {"warning": 3.0, "critical": 1.5}
    },
    "efficiency": {
        "asset_turnover": {"warning": 0.5, "critical": 0.3},
        "inventory_turnover": {"warning": 4.0, "critical": 2.0},
        "receivables_turnover": {"warning": 6.0, "critical": 3.0}
    },
    "growth": {
        "revenue_growth": {"warning": 0.1, "critical": 0.0},
        "profit_growth": {"warning": 0.1, "critical": 0.0},
        "asset_growth": {"warning": 0.2, "critical": 0.0}
    },
    "fraud_indicators": {
        "receivables_growth_vs_revenue": {"warning": 1.5, "critical": 2.0},
        "inventory_growth_vs_revenue": {"warning": 1.5, "critical": 2.0},
        "revenue_profit_divergence": {"warning": 0.3, "critical": 0.5},
        "cash_flow_profit_divergence": {"warning": 0.3, "critical": 0.5},
        "asset_quality_issues": {"warning": 0.1, "critical": 0.2},
        "accounting_policy_changes": {"warning": 2, "critical": 3},
        "related_party_transactions": {"warning": 0.1, "critical": 0.2},
        "audit_opinion_issues": {"warning": 1, "critical": 2},
        "executive_turnover": {"warning": 0.2, "critical": 0.3},
        "delayed_filing": {"warning": 7, "critical": 14}
    }
}


def load_thresholds(config_path: str = None) -> Dict[str, Any]:
    """
    加载阈值配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        阈值配置字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "thresholds.yaml")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                thresholds = yaml.safe_load(f)
            return thresholds
        except Exception as e:
            print(f"警告: 无法加载阈值配置文件 {config_path}: {e}")
            print("使用默认阈值配置")
            return DEFAULT_THRESHOLDS
    else:
        print(f"警告: 阈值配置文件 {config_path} 不存在")
        print("使用默认阈值配置")
        return DEFAULT_THRESHOLDS


def get_threshold(category: str, indicator: str, level: str = "warning") -> Optional[float]:
    """
    获取特定指标的阈值
    
    Args:
        category: 类别（如 profitability, liquidity 等）
        indicator: 指标名称
        level: 阈值级别（warning 或 critical）
        
    Returns:
        阈值值，如果未找到则返回None
    """
    thresholds = load_thresholds()
    
    try:
        category_thresholds = thresholds.get(category, {})
        indicator_thresholds = category_thresholds.get(indicator, {})
        return indicator_thresholds.get(level)
    except (KeyError, AttributeError):
        return None


def save_thresholds(thresholds: Dict[str, Any], config_path: str = None) -> bool:
    """
    保存阈值配置到文件
    
    Args:
        thresholds: 阈值配置字典
        config_path: 配置文件路径
        
    Returns:
        是否保存成功
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "thresholds.yaml")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(thresholds, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"错误: 无法保存阈值配置到 {config_path}: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    thresholds = load_thresholds()
    print(f"加载的阈值配置: {len(thresholds)} 个类别")
    
    # 测试获取阈值
    gross_margin_warning = get_threshold("profitability", "gross_margin", "warning")
    print(f"毛利率警告阈值: {gross_margin_warning}")
    
    # 测试保存
    if save_thresholds(thresholds):
        print("阈值配置保存成功")
    else:
        print("阈值配置保存失败")