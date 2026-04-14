"""
数据模型包

该包包含财报分析系统的所有数据模型定义
"""

# 财务数据模型
from .financial_data import (
    BalanceSheet,
    BalanceSheetPydantic,
    IncomeStatement,
    IncomeStatementPydantic,
    CashFlowStatement,
    CashFlowStatementPydantic,
    FinancialData,
    FinancialDataPydantic
)

# 财务指标模型
from .indicators import (
    ProfitabilityIndicators,
    ProfitabilityIndicatorsPydantic,
    SolvencyIndicators,
    SolvencyIndicatorsPydantic,
    OperationIndicators,
    OperationIndicatorsPydantic,
    GrowthIndicators,
    GrowthIndicatorsPydantic,
    CashFlowIndicators,
    CashFlowIndicatorsPydantic,
    Indicators,
    IndicatorsPydantic
)

# 风险模型
from .risk import (
    RiskLevel,
    RiskType,
    Risk,
    RiskPydantic,
    RiskList,
    RiskListPydantic
)

# 报告模型
from .report import (
    ExecutiveSummary,
    ExecutiveSummaryPydantic,
    IndicatorTable,
    IndicatorTablePydantic,
    DetailedAnalysis,
    DetailedAnalysisPydantic,
    Report,
    ReportPydantic
)

# 配置模型
from .config import (
    RiskThresholds,
    RiskThresholdsPydantic,
    AnalysisConfig,
    AnalysisConfigPydantic,
    IndustryBenchmark,
    IndustryBenchmarkPydantic
)

__all__ = [
    # 财务数据模型
    'BalanceSheet',
    'BalanceSheetPydantic',
    'IncomeStatement',
    'IncomeStatementPydantic',
    'CashFlowStatement',
    'CashFlowStatementPydantic',
    'FinancialData',
    'FinancialDataPydantic',
    
    # 财务指标模型
    'ProfitabilityIndicators',
    'ProfitabilityIndicatorsPydantic',
    'SolvencyIndicators',
    'SolvencyIndicatorsPydantic',
    'OperationIndicators',
    'OperationIndicatorsPydantic',
    'GrowthIndicators',
    'GrowthIndicatorsPydantic',
    'CashFlowIndicators',
    'CashFlowIndicatorsPydantic',
    'Indicators',
    'IndicatorsPydantic',
    
    # 风险模型
    'RiskLevel',
    'RiskType',
    'Risk',
    'RiskPydantic',
    'RiskList',
    'RiskListPydantic',
    
    # 报告模型
    'ExecutiveSummary',
    'ExecutiveSummaryPydantic',
    'IndicatorTable',
    'IndicatorTablePydantic',
    'DetailedAnalysis',
    'DetailedAnalysisPydantic',
    'Report',
    'ReportPydantic',
    
    # 配置模型
    'RiskThresholds',
    'RiskThresholdsPydantic',
    'AnalysisConfig',
    'AnalysisConfigPydantic',
    'IndustryBenchmark',
    'IndustryBenchmarkPydantic'
]
