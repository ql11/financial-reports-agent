"""
财报造假分析系统 - 核心模块
"""

__version__ = "2.0.0"
__author__ = "Financial Reports Team"
__email__ = "support@financial-reports.com"

from .core.analyzer import FinancialFraudAnalyzer
from .core.data_extractor import PDFDataExtractor
from .core.fraud_detector import FraudDetector
from .core.risk_assessor import RiskAssessor
from .core.report_generator import ReportGenerator

__all__ = [
    "FinancialFraudAnalyzer",
    "PDFDataExtractor", 
    "FraudDetector",
    "RiskAssessor",
    "ReportGenerator"
]