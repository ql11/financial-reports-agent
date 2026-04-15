"""
配置文件模块
"""

from .thresholds import load_thresholds
from .weights import load_weights

__all__ = [
    "load_thresholds",
    "load_weights"
]