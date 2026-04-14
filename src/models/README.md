# 数据模型文档

## 概述

本模块实现了财报分析系统的所有数据模型，使用Python dataclass和Pydantic实现，提供完整的数据验证和类型安全。

## 模型结构

### 1. 财务数据模型 (`financial_data.py`)

#### BalanceSheet - 资产负债表
```python
from datetime import datetime
from src.models import BalanceSheet

balance_sheet = BalanceSheet(
    total_assets=1000000,          # 资产总计
    current_assets=500000,         # 流动资产
    non_current_assets=500000,     # 非流动资产
    cash=200000,                   # 货币资金
    accounts_receivable=150000,    # 应收账款
    inventory=150000,              # 存货
    total_liabilities=600000,      # 负债总计
    current_liabilities=300000,    # 流动负债
    non_current_liabilities=300000,# 非流动负债
    total_equity=400000,           # 所有者权益
    report_date=datetime.now()     # 报告日期
)

# 验证资产负债表平衡性
is_balanced = balance_sheet.validate_balance()
```

#### IncomeStatement - 利润表
```python
from src.models import IncomeStatement

income_statement = IncomeStatement(
    operating_revenue=800000,      # 营业收入
    operating_cost=500000,         # 营业成本
    gross_profit=300000,           # 毛利
    operating_profit=200000,       # 营业利润
    total_profit=180000,           # 利润总额
    net_profit=150000,             # 净利润
    selling_expense=50000,         # 销售费用
    admin_expense=30000,           # 管理费用
    financial_expense=20000,       # 财务费用
    report_date=datetime.now()     # 报告日期
)
```

#### CashFlowStatement - 现金流量表
```python
from src.models import CashFlowStatement

cash_flow = CashFlowStatement(
    operating_cash_inflow=900000,    # 经营现金流入
    operating_cash_outflow=700000,   # 经营现金流出
    net_operating_cash=200000,       # 经营现金净流量
    investing_cash_inflow=100000,    # 投资现金流入
    investing_cash_outflow=150000,   # 投资现金流出
    net_investing_cash=-50000,       # 投资现金净流量
    financing_cash_inflow=50000,     # 筹资现金流入
    financing_cash_outflow=30000,    # 筹资现金流出
    net_financing_cash=20000,        # 筹资现金净流量
    net_cash_increase=170000,        # 现金净增加额
    report_date=datetime.now()       # 报告日期
)
```

#### FinancialData - 财务数据总模型
```python
from src.models import FinancialData

financial_data = FinancialData(
    company_name='测试公司',
    report_year=2023,
    balance_sheet=balance_sheet,
    income_statement=income_statement,
    cash_flow_statement=cash_flow,
    source_file='test.pdf',
    extraction_time=datetime.now(),
    data_quality_score=1.0
)

# 获取财务数据摘要
summary = financial_data.get_summary()
```

### 2. 财务指标模型 (`indicators.py`)

#### 五大类指标
- **ProfitabilityIndicators**: 盈利能力指标
- **SolvencyIndicators**: 偿债能力指标
- **OperationIndicators**: 运营能力指标
- **GrowthIndicators**: 成长能力指标
- **CashFlowIndicators**: 现金流指标

```python
from src.models import ProfitabilityIndicators, Indicators

# 盈利能力指标
profitability = ProfitabilityIndicators(
    gross_margin=37.5,      # 毛利率
    net_margin=18.75,       # 净利率
    roe=37.5,               # 净资产收益率
    roa=15.0,               # 总资产收益率
    operating_margin=25.0   # 营业利润率
)

# 获取指标评价
evaluation = profitability.get_evaluation()

# 转换为字典
indicators_dict = profitability.to_dict()
```

### 3. 风险模型 (`risk.py`)

#### Risk - 风险模型
```python
from src.models import Risk, RiskLevel, RiskType

risk = Risk(
    risk_type=RiskType.FINANCIAL,      # 风险类型
    risk_level=RiskLevel.HIGH,         # 风险等级
    description='资产负债率过高',      # 风险描述
    indicator_name='资产负债率',       # 相关指标
    indicator_value=75.0,              # 指标值
    threshold=70.0,                    # 风险阈值
    impact='偿债压力大',               # 影响说明
    recommendation='降低负债水平'      # 建议措施
)
```

#### RiskList - 风险清单
```python
from src.models import RiskList

risk_list = RiskList(
    company_name='测试公司',
    report_year=2023
)

# 添加风险
risk_list.add_risk(risk)

# 获取风险摘要
summary = risk_list.get_summary()

# 按等级筛选风险
high_risks = risk_list.get_risks_by_level(RiskLevel.HIGH)
```

### 4. 报告模型 (`report.py`)

#### ExecutiveSummary - 执行摘要
```python
from src.models import ExecutiveSummary

summary = ExecutiveSummary(
    company_name='测试公司',
    report_year=2023,
    overall_score=8,
    key_findings=['盈利能力优秀', '偿债能力良好'],
    major_risks=['资产负债率偏高'],
    recommendation='建议优化资本结构'
)
```

#### Report - 分析报告
```python
from src.models import Report, IndicatorTable, DetailedAnalysis

report = Report(
    company_name='测试公司',
    report_year=2023,
    report_date=datetime.now(),
    executive_summary=summary,
    overall_score=8
)

# 添加指标表
indicator_table = IndicatorTable(category='盈利能力')
indicator_table.add_indicator('毛利率', 37.5, 30.0)
report.add_indicator_table(indicator_table)

# 获取报告目录
toc = report.get_table_of_contents()
```

### 5. 配置模型 (`config.py`)

#### RiskThresholds - 风险阈值配置
```python
from src.models import RiskThresholds

thresholds = RiskThresholds(
    debt_ratio_high=0.7,      # 资产负债率高风险阈值
    debt_ratio_medium=0.6,    # 资产负债率中风险阈值
    current_ratio_low=1.0,    # 流动比率低风险阈值
    quick_ratio_low=0.5       # 速动比率低风险阈值
)
```

#### AnalysisConfig - 分析配置
```python
from src.models import AnalysisConfig

config = AnalysisConfig(
    source_folder='source',
    repository_folder='repository',
    output_folder='reports',
    log_level='INFO',
    batch_size=10,
    timeout=300
)

# 检查分析维度是否启用
if config.is_dimension_enabled('盈利能力'):
    print('盈利能力分析已启用')
```

## 数据验证

### 使用dataclass验证
```python
# 内置验证方法
is_valid = balance_sheet.validate_balance()
is_valid = income_statement.validate_gross_profit()
is_valid = cash_flow.validate_net_cash()
```

### 使用Pydantic验证
```python
from src.models import BalanceSheetPydantic

try:
    balance_sheet = BalanceSheetPydantic(
        total_assets=1000000,
        current_assets=500000,
        # ... 其他字段
    )
except ValueError as e:
    print(f'数据验证失败: {e}')
```

## 类型安全

所有模型都使用Python类型注解，确保类型安全：

```python
from typing import Dict, List, Optional
from datetime import datetime

def calculate_indicators(
    financial_data: FinancialData
) -> Indicators:
    """计算财务指标"""
    # 实现代码
    pass
```

## 最佳实践

1. **使用dataclass版本**：对于内部数据处理，使用dataclass版本更轻量
2. **使用Pydantic版本**：对于外部数据输入，使用Pydantic版本进行严格验证
3. **调用验证方法**：创建对象后，调用验证方法确保数据一致性
4. **使用类型注解**：在函数签名中使用类型注解，提高代码可读性

## 依赖

- Python 3.9+
- pydantic >= 2.0

## 安装

```bash
pip install pydantic
```
