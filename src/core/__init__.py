"""
核心功能模块

该包包含财报分析系统的核心功能模块：
- pdf_table_extractor: PDF表格提取器
- data_extractor: 数据提取器
- indicator_calculator: 指标计算器
- trend_analyzer: 趋势分析器
- risk_detector: 风险识别器
- report_generator: 报告生成器
"""

from src.core.pdf_table_extractor import (
    PDFTableExtractor,
    extract_pdf_tables
)

from src.core.data_extractor import (
    FinancialDataExtractor,
    extract_financial_data
)

from src.core.indicator_calculator import (
    IndicatorCalculator,
    calculate_indicators
)

from src.core.trend_analyzer import (
    TrendAnalyzer,
    analyze_trend
)

from src.core.risk_detector import (
    RiskDetector,
    detect_risks
)

from src.core.report_generator import (
    ReportGenerator,
    generate_report
)


__all__ = [
    # PDF表格提取器
    'PDFTableExtractor',
    'extract_pdf_tables',

    # 数据提取器
    'FinancialDataExtractor',
    'extract_financial_data',

    # 指标计算器
    'IndicatorCalculator',
    'calculate_indicators',

    # 趋势分析器
    'TrendAnalyzer',
    'analyze_trend',

    # 风险识别器
    'RiskDetector',
    'detect_risks',

    # 报告生成器
    'ReportGenerator',
    'generate_report'
]
