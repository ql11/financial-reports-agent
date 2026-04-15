"""
阈值配置加载工具
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_thresholds(config_path: str = None) -> Dict[str, Any]:
    """加载阈值配置
    
    Args:
        config_path: 配置文件路径，默认为configs/thresholds.yaml
        
    Returns:
        Dict[str, Any]: 阈值配置字典
    """
    if config_path is None:
        config_path = Path(__file__).parent / "thresholds.yaml"
    else:
        config_path = Path(config_path)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            thresholds = yaml.safe_load(f)
        
        logger.info(f"阈值配置已加载: {config_path}")
        return thresholds or {}
        
    except FileNotFoundError:
        logger.warning(f"阈值配置文件不存在: {config_path}，使用默认配置")
        return _get_default_thresholds()
    except Exception as e:
        logger.error(f"加载阈值配置失败: {e}")
        return _get_default_thresholds()


def _get_default_thresholds() -> Dict[str, Any]:
    """获取默认阈值配置"""
    return {
        "profitability": {
            "gross_margin": {"warning": 10.0, "critical": 5.0, "excellent": 30.0},
            "net_margin": {"warning": 3.0, "critical": 1.0, "excellent": 15.0},
            "roe": {"warning": 5.0, "critical": 2.0, "excellent": 15.0},
            "roa": {"warning": 3.0, "critical": 1.0, "excellent": 8.0}
        },
        "solvency": {
            "debt_ratio": {"warning": 70.0, "critical": 85.0, "excellent": 50.0},
            "current_ratio": {"warning": 1.0, "critical": 0.8, "excellent": 2.0},
            "quick_ratio": {"warning": 0.5, "critical": 0.3, "excellent": 1.0}
        },
        "operation": {
            "inventory_turnover": {"warning": 2.0, "critical": 1.0, "excellent": 5.0},
            "receivables_turnover": {"warning": 3.0, "critical": 1.5, "excellent": 8.0},
            "total_asset_turnover": {"warning": 0.3, "critical": 0.1, "excellent": 0.8}
        },
        "growth": {
            "revenue_growth": {"warning": -10.0, "critical": -20.0, "excellent": 20.0},
            "profit_growth": {"warning": -20.0, "critical": -40.0, "excellent": 30.0},
            "cash_flow_growth": {"warning": -30.0, "critical": -50.0, "excellent": 20.0}
        },
        "fraud_detection": {
            "revenue_profit_divergence": {
                "revenue_decline": -5.0,
                "profit_growth": 5.0,
                "score": 2.5
            },
            "cash_flow_divergence": {
                "profit_growth": 5.0,
                "cash_flow_decline": -20.0,
                "score": 3.0
            },
            "receivables_anomalies": {
                "growth_exceed_revenue": 10.0,
                "score": 2.0
            },
            "inventory_anomalies": {
                "growth_exceed_revenue": 15.0,
                "score": 2.0
            },
            "related_party_transactions": {
                "percentage_threshold": 20.0,
                "score": 2.0
            }
        },
        "risk_levels": {
            "critical": 30.0,
            "high": 20.0,
            "medium": 10.0,
            "low": 0.0
        }
    }


def get_threshold(category: str, metric: str, level: str) -> Optional[float]:
    """获取特定阈值
    
    Args:
        category: 类别（如 profitability, solvency 等）
        metric: 指标名称（如 gross_margin, debt_ratio 等）
        level: 阈值级别（如 warning, critical, excellent）
        
    Returns:
        Optional[float]: 阈值值，未找到返回None
    """
    thresholds = load_thresholds()
    
    try:
        return thresholds.get(category, {}).get(metric, {}).get(level)
    except (KeyError, AttributeError):
        return None


def check_threshold(value: float, category: str, metric: str) -> Dict[str, Any]:
    """检查值是否超过阈值
    
    Args:
        value: 要检查的值
        category: 类别
        metric: 指标名称
        
    Returns:
        Dict[str, Any]: 检查结果
    """
    thresholds = load_thresholds()
    
    result = {
        "value": value,
        "category": category,
        "metric": metric,
        "level": "normal",  # normal, warning, critical, excellent
        "message": ""
    }
    
    try:
        metric_thresholds = thresholds.get(category, {}).get(metric, {})
        
        # 检查优秀阈值
        excellent_threshold = metric_thresholds.get("excellent")
        if excellent_threshold is not None:
            if category in ["profitability", "growth"]:
                # 对于盈利能力和成长能力，值越大越好
                if value >= excellent_threshold:
                    result["level"] = "excellent"
                    result["message"] = f"{metric} 优秀 ({value:.2f} >= {excellent_threshold:.2f})"
                    return result
            else:
                # 对于偿债能力和运营能力，需要根据具体指标判断
                if metric in ["debt_ratio"]:
                    # 资产负债率越低越好
                    if value <= excellent_threshold:
                        result["level"] = "excellent"
                        result["message"] = f"{metric} 优秀 ({value:.2f} <= {excellent_threshold:.2f})"
                        return result
                else:
                    # 其他指标值越大越好
                    if value >= excellent_threshold:
                        result["level"] = "excellent"
                        result["message"] = f"{metric} 优秀 ({value:.2f} >= {excellent_threshold:.2f})"
                        return result
        
        # 检查严重警告阈值
        critical_threshold = metric_thresholds.get("critical")
        if critical_threshold is not None:
            if category in ["profitability", "growth"]:
                # 对于盈利能力和成长能力，值越小越差
                if value <= critical_threshold:
                    result["level"] = "critical"
                    result["message"] = f"{metric} 严重警告 ({value:.2f} <= {critical_threshold:.2f})"
                    return result
            else:
                # 对于偿债能力和运营能力，需要根据具体指标判断
                if metric in ["debt_ratio"]:
                    # 资产负债率越高越差
                    if value >= critical_threshold:
                        result["level"] = "critical"
                        result["message"] = f"{metric} 严重警告 ({value:.2f} >= {critical_threshold:.2f})"
                        return result
                else:
                    # 其他指标值越小越差
                    if value <= critical_threshold:
                        result["level"] = "critical"
                        result["message"] = f"{metric} 严重警告 ({value:.2f} <= {critical_threshold:.2f})"
                        return result
        
        # 检查警告阈值
        warning_threshold = metric_thresholds.get("warning")
        if warning_threshold is not None:
            if category in ["profitability", "growth"]:
                # 对于盈利能力和成长能力，值越小越差
                if value <= warning_threshold:
                    result["level"] = "warning"
                    result["message"] = f"{metric} 警告 ({value:.2f} <= {warning_threshold:.2f})"
                    return result
            else:
                # 对于偿债能力和运营能力，需要根据具体指标判断
                if metric in ["debt_ratio"]:
                    # 资产负债率越高越差
                    if value >= warning_threshold:
                        result["level"] = "warning"
                        result["message"] = f"{metric} 警告 ({value:.2f} >= {warning_threshold:.2f})"
                        return result
                else:
                    # 其他指标值越小越差
                    if value <= warning_threshold:
                        result["level"] = "warning"
                        result["message"] = f"{metric} 警告 ({value:.2f} <= {warning_threshold:.2f})"
                        return result
        
        # 正常范围
        result["message"] = f"{metric} 正常 ({value:.2f})"
        return result
        
    except Exception as e:
        logger.error(f"检查阈值时出错: {e}")
        result["level"] = "error"
        result["message"] = f"检查阈值时出错: {e}"
        return result