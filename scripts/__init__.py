"""脚本兼容入口。"""

from src.cli import analyze_main as analyze_fraud_main
from src.cli import batch_main as batch_analyze_main

__all__ = [
    "analyze_fraud_main",
    "batch_analyze_main",
]
