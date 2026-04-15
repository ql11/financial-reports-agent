"""
配置文件模块
提供阈值和权重的加载功能
"""

from .thresholds import load_thresholds, get_threshold
from .weights import load_weights, get_fraud_pattern_weight

__all__ = [
    'load_thresholds',
    'get_threshold',
    'load_weights',
    'get_fraud_pattern_weight'
]