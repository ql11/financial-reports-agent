# 财报造假分析系统 - 使用指南

## 📋 项目结构概览

```
Financial_Reports/
├── src/                          # 源代码目录
│   ├── core/                     # 核心分析模块
│   │   ├── analyzer.py           # 主分析器 - 协调整个分析流程
│   │   ├── data_extractor.py     # 数据提取器 - 从PDF提取财务数据
│   │   ├── fraud_detector.py     # 造假检测器 - 检测财报造假迹象
│   │   ├── risk_assessor.py      # 风险评估器 - 评估财务风险
│   │   └── report_generator.py   # 报告生成器 - 生成分析报告
│   ├── models/                   # 数据模型
│   │   ├── financial_data.py     # 财务数据模型
│   │   ├── fraud_indicators.py   # 造假指标模型
│   │   └── report_model.py       # 报告模型
│   └── utils/                    # 工具函数
│       ├── file_utils.py         # 文件工具
│       ├── calculation_utils.py  # 计算工具
│       └── validation_utils.py   # 验证工具
├── configs/                      # 配置文件
│   ├── thresholds.yaml           # 阈值配置
│   └── weights.yaml              # 权重配置
├── scripts/                      # 命令行脚本
│   ├── analyze_fraud.py          # 单文件分析脚本
│   └── batch_analyze.py          # 批量分析脚本
├── examples/                     # 使用示例
├── tests/                        # 单元测试
├── main.py                       # 统一入口点
├── requirements.txt              # 依赖包
└── README.md                     # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 使用命令行工具

#### 分析单个财报文件
```bash
python main.py analyze path/to/report.pdf
```

#### 指定公司名称和报告年度
```bash
python main.py analyze path/to/report.pdf --company "英洛华科技" --year 2025
```

#### 批量分析多个财报文件
```bash
python main.py batch path/to/reports/*.pdf
```

#### 指定输出目录和格式
```bash
python main.py analyze path/to/report.pdf --output custom_reports/ --format json
```

#### 显示详细输出
```bash
python main.py analyze path/to/report.pdf --verbose
```

### 3. 使用Python API

```python
from src.core.analyzer import FinancialFraudAnalyzer

# 创建分析器
analyzer = FinancialFraudAnalyzer(output_dir="reports")

# 分析财报
report = analyzer.analyze(
    pdf_path="path/to/report.pdf",
    company_name="英洛华科技",
    report_year=2025
)

# 查看分析结果
print(f"风险等级: {report.risk_assessment.risk_level.value}")
print(f"风险评分: {report.risk_assessment.total_score:.1f}/50")
print(f"投资建议: {report.investment_recommendation}")

# 保存报告
analyzer.save_report(report, "custom_report.md")
```

### 4. 批量分析

```python
from src.core.analyzer import FinancialFraudAnalyzer

# 创建分析器
analyzer = FinancialFraudAnalyzer(output_dir="batch_reports")

# 批量分析
pdf_files = [
    "path/to/report1.pdf",
    "path/to/report2.pdf",
    "path/to/report3.pdf"
]

reports = analyzer.batch_analyze(pdf_files, "batch_reports")
print(f"成功分析 {len(reports)} 个文件")
```

## 🔧 配置说明

### 阈值配置 (configs/thresholds.yaml)
```yaml
profitability:
  gross_margin:
    warning: 0.2      # 毛利率警告阈值
    critical: 0.1     # 毛利率严重阈值
  operating_margin:
    warning: 0.1
    critical: 0.05
```

### 权重配置 (configs/weights.yaml)
```yaml
fraud_patterns:
  revenue_profit_divergence: 1.5    # 业绩背离权重
  cash_flow_profit_divergence: 1.8  # 现金流与利润背离权重
  receivables_growth_vs_revenue: 1.2 # 应收账款增长权重
```

## 📊 分析指标

### 财务比率分析
- **盈利能力**: 毛利率、营业利润率、净利润率、ROE、ROA
- **偿债能力**: 流动比率、速动比率、现金比率
- **运营效率**: 资产周转率、存货周转率、应收账款周转率
- **成长能力**: 营收增长率、利润增长率、资产增长率

### 造假检测指标
1. **业绩背离**: 营收增长与利润增长不匹配
2. **现金流异常**: 经营现金流与净利润背离
3. **资产质量**: 应收账款/存货异常增长
4. **会计政策**: 频繁变更会计政策
5. **关联交易**: 异常关联交易
6. **审计意见**: 非标准审计意见
7. **高管变动**: 异常高管离职
8. **延迟披露**: 财报延迟披露

## 📈 风险等级

| 风险等级 | 评分范围 | 说明 |
|---------|---------|------|
| 低风险 | 0-15分 | 财务健康，无明显造假迹象 |
| 中风险 | 16-30分 | 存在一定风险，需要关注 |
| 高风险 | 31-40分 | 存在明显造假迹象，建议谨慎 |
| 极高风险 | 41-50分 | 存在严重造假迹象，建议回避 |

## 🎯 投资建议

基于风险评分，系统提供以下投资建议：
- **强烈推荐**: 低风险，财务健康
- **推荐**: 中低风险，基本面良好
- **谨慎**: 中高风险，需要进一步调查
- **回避**: 高风险，存在明显造假迹象
- **强烈回避**: 极高风险，存在严重造假

## 🔍 高级功能

### 自定义配置
```python
from src.core.analyzer import FinancialFraudAnalyzer
from configs.thresholds import load_thresholds
from configs.weights import load_weights

# 加载自定义配置
custom_thresholds = load_thresholds("custom_thresholds.yaml")
custom_weights = load_weights("custom_weights.yaml")

# 创建自定义分析器
analyzer = FinancialFraudAnalyzer(
    output_dir="reports",
    thresholds=custom_thresholds,
    weights=custom_weights
)
```

### 扩展分析模块
```python
from src.core.fraud_detector import FraudDetector
from src.core.risk_assessor import RiskAssessor
from src.core.report_generator import ReportGenerator

# 使用独立模块
detector = FraudDetector()
risk_assessor = RiskAssessor()
report_generator = ReportGenerator("reports")

# 自定义分析流程
financial_data = {...}  # 财务数据
indicators = detector.detect_fraud(financial_data)
risk_assessment = risk_assessor.assess_risk(indicators)
report = report_generator.generate_report(financial_data, risk_assessment)
```

## 🧪 测试

### 运行单元测试
```bash
python -m pytest tests/
```

### 测试特定模块
```bash
python -m pytest tests/test_fraud_detector.py
```

## 📝 报告格式

系统生成的分析报告包含以下部分：

1. **公司基本信息**: 公司名称、报告年度、分析日期
2. **财务数据摘要**: 关键财务指标
3. **财务比率分析**: 盈利能力、偿债能力、运营效率、成长能力
4. **造假检测结果**: 检测到的造假指标和风险等级
5. **风险评估**: 总体风险评分和风险等级
6. **投资建议**: 基于风险评级的投资建议
7. **详细分析**: 各项指标的详细分析
8. **建议措施**: 针对发现问题的建议

## 🔄 更新日志

### v2.0.0 (2025-04-15)
- **重构项目结构**: 从Agent架构迁移到模块化设计
- **统一入口点**: 创建main.py作为统一入口
- **模块化设计**: 分离数据模型、核心模块、工具函数
- **配置管理**: 独立的配置文件系统
- **命令行接口**: 支持命令行参数和批量处理
- **Python API**: 提供完整的Python API接口
- **类型提示**: 完整的类型提示和文档字符串
- **测试覆盖**: 完善的测试框架

### v1.0.0 (2025-04-14)
- **初始版本**: 基于Agent架构的财报造假分析系统
- **基础功能**: PDF解析、财务分析、造假检测、报告生成
- **Agent架构**: 基于角色的Agent工作流

## 📞 支持与反馈

如有问题或建议，请：
1. 查看 `examples/` 目录中的使用示例
2. 阅读源代码中的文档字符串
3. 提交Issue到项目仓库
4. 联系项目维护者

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。