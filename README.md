# 财报分析系统

一个专业的上市公司财务报告自动化分析系统，能够从PDF文件中提取财报数据，进行全面的财务分析，识别财务风险和异常问题。

## 功能特性

### 核心功能
- **PDF财报提取**：自动识别和提取PDF格式的财务报告
- **Markdown转换**：使用Pandoc将PDF转换为结构化的Markdown格式
- **数据提取**：提取三大财务报表数据（资产负债表、利润表、现金流量表）
- **指标计算**：计算五大类财务指标
  - 盈利能力指标：毛利率、净利率、ROE、ROA
  - 偿债能力指标：资产负债率、流动比率、速动比率
  - 运营能力指标：存货周转率、应收账款周转率、总资产周转率
  - 成长能力指标：营收增长率、净利润增长率
  - 现金流指标：自由现金流、现金债务覆盖率
- **趋势分析**：多年数据趋势分析、行业对比、同行对比
- **风险识别**：识别财务风险、经营风险和潜在问题
- **报告生成**：生成Markdown格式的综合分析报告

### 技术特性
- 支持批量处理（≥50份财报）
- 单份财报分析时间 ≤ 2分钟
- PDF解析成功率 ≥ 95%
- 数据提取准确率 ≥ 90%
- 跨平台支持（Windows、Linux、macOS）

## 项目结构

```
Financial_Reports/
├── .codeartsdoer/          # SDD规范文档
│   └── specs/
│       └── financial_analysis/
│           ├── spec.md      # 项目规范文档
│           ├── design.md    # 技术设计文档
│           └── tasks.md     # 开发任务清单
├── source/                  # 源文件夹（放置PDF财报）
├── repository/              # 仓库文件夹（存储Markdown文件）
├── reports/                 # 分析报告输出目录
├── config/                  # 配置文件目录
│   ├── config.yaml          # 主配置文件
│   ├── risk_thresholds.yaml # 风险阈值配置
│   └── industry_benchmarks.yaml # 行业基准数据
├── src/                     # 源代码目录
│   ├── core/                # 核心功能模块
│   ├── utils/               # 工具模块
│   ├── models/              # 数据模型
│   └── main.py              # 主程序入口
├── tests/                   # 测试代码目录
├── logs/                    # 日志文件目录
├── requirements.txt         # 依赖包列表
└── README.md                # 项目说明文档
```

## 安装部署

### 环境要求
- Python 3.9+
- pip包管理器
- Pandoc 3.9+（文档转换工具）

### 安装步骤

1. 安装Pandoc
```bash
# Windows: 从 https://pandoc.org/installing.html 下载安装
# 或使用 chocolatey
choco install pandoc

# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

2. 克隆项目
```bash
git clone <repository-url>
cd Financial_Reports
```

3. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 配置项目
```bash
# 复制配置文件模板
cp config/config.yaml.example config/config.yaml
# 编辑配置文件，设置源文件夹、输出文件夹等参数
```

## 使用方法

### 基本使用

1. 将PDF财报文件放入 `source/` 文件夹

2. 运行分析程序
```bash
python src/main.py
```

3. 查看分析报告
- Markdown文件：`repository/` 文件夹
- 分析报告：`reports/` 文件夹

### 高级使用

#### 指定配置文件
```bash
python src/main.py --config config/custom_config.yaml
```

#### 指定源文件夹
```bash
python src/main.py --source /path/to/pdf/folder
```

#### 批量处理
```bash
python src/main.py --batch --workers 4
```

## 配置说明

### 主配置文件 (config.yaml)
```yaml
# 文件夹配置
source_folder: ./source
repository_folder: ./repository
output_folder: ./reports

# 分析维度
analysis_dimensions:
  - profitability
  - solvency
  - operation
  - growth
  - cashflow

# 性能配置
batch_size: 50
timeout: 120
```

### 风险阈值配置 (risk_thresholds.yaml)
```yaml
# 偿债能力阈值
debt_ratio_high: 0.7
debt_ratio_medium: 0.6
current_ratio_low: 1.0
quick_ratio_low: 0.5

# 盈利能力阈值
gross_margin_low: 0.2
net_margin_low: 0.05
roe_low: 0.1

# 成长能力阈值
revenue_growth_low: -0.1
profit_growth_low: -0.1
```

## 分析报告示例

分析报告包含以下章节：

1. **执行摘要**：核心结论和主要发现
2. **关键指标一览表**：所有财务指标的汇总表格
3. **详细分析**：
   - 盈利能力分析
   - 偿债能力分析
   - 运营能力分析
   - 成长能力分析
   - 现金流分析
   - 趋势分析
   - 对比分析
4. **风险提示**：识别的风险和预警
5. **综合评分**：1-10分的综合评分

## 开发指南

### 运行测试
```bash
pytest tests/
```

### 代码质量检查
```bash
flake8 src/
black src/
```

### 生成测试覆盖率报告
```bash
pytest --cov=src tests/
```

## 常见问题

### Q: PDF解析失败怎么办？
A: 检查PDF文件是否损坏，确保文件编码为UTF-8或GBK。系统会自动跳过损坏的文件并记录日志。

### Q: 数据提取不准确怎么办？
A: 确保PDF文件中的表格格式规范，系统对标准格式的财报表格识别率最高。可以手动调整Markdown文件后重新分析。

### Q: 如何添加自定义风险规则？
A: 在 `config/risk_thresholds.yaml` 中添加自定义阈值，或在 `src/core/risk_detector.py` 中添加新的风险识别规则。

## 技术栈

- **PDF处理**：pdfplumber, PyPDF2
- **数据处理**：pandas, numpy
- **可视化**：matplotlib, plotly
- **配置管理**：pyyaml, python-dotenv
- **测试**：pytest, pytest-cov

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request。在提交PR前，请确保：
1. 代码通过所有测试
2. 代码符合PEP8规范
3. 添加了必要的文档和注释

## 联系方式

如有问题或建议，请提交Issue或联系项目维护者。
