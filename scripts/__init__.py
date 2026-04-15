"""
脚本模块
"""

from .analyze_fraud import main as analyze_fraud_main
from .batch_analyze import main as batch_analyze_main

__all__ = [
    "analyze_fraud_main",
    "batch_analyze_main"
]