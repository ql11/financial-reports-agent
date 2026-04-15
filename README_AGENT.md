# 财报分析系统 - Agent架构版本

## 概述

本项目已从传统的Python核心架构转换为基于Agent和Agent Skills的现代化架构。新架构采用模块化设计，通过多个专业Agent协同工作，提供更灵活、可扩展的财报分析解决方案。

## 架构设计

### 核心组件

```
Financial_Reports/
├── agents/                    # Agent定义
│   ├── financial_analysis/    # 财务分析主Agent
│   ├── data_extraction/       # 数据提取Agent
│   ├── report_generation/     # 报告生成Agent
│   └── risk_assessment/       # 风险评估Agent
├── skills/                    # 技能定义
│   ├── pdf_processing/        # PDF处理技能
│   ├── data_analysis/         # 数据分析技能
│   ├── risk_detection/        # 风险检测技能
│   └── report_writing/        # 报告写作技能
├── configs/                   # 配置文件
│   └── main_config.yaml       # 主配置文件
├── workflows/                 # 工作流定义
│   └── financial_analysis_workflow.yaml
├── data/                      # 数据目录
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后的数据
│   └── results/               # 分析结果
├── inputs/                    # 输入文件
├── outputs/                   # 输出文件
└── reports/                   # 生成报告
```

### Agent架构优势

1. **模块化设计**：每个Agent专注于特定任务，职责清晰
2. **可扩展性**：易于添加新的Agent和技能
3. **灵活性**：可以根据需求组合不同的工作流
4. **可维护性**：独立的配置和版本管理
5. **协作性**：Agent之间可以协同工作

## Agent说明

### 1. 财务分析主Agent (`financial_analysis_agent`)
- **职责**：协调整个分析流程
- **技能**：PDF处理、数据分析、风险检测、报告写作
- **输入**：PDF财报文件
- **输出**：完整的财务分析报告

### 2. 数据提取Agent (`data_extraction_agent`)
- **职责**：从PDF提取结构化财务数据
- **技能**：PDF处理
- **输入**：PDF文件
- **输出**：结构化财务数据

### 3. 风险评估Agent (`risk_assessment_agent`)
- **职责**：识别和评估财务风险
- **技能**：风险检测、数据分析
- **输入**：财务指标
- **输出**：风险评估结果和建议

### 4. 报告生成Agent (`report_generation_agent`)
- **职责**：生成专业财务分析报告
- **技能**：报告写作、数据分析
- **输入**：分析结果
- **输出**：格式化的分析报告

## 技能说明

### 1. PDF处理技能 (`pdf_processing`)
- 从PDF文件中提取文本和表格数据
- 检测和解析PDF中的表格
- 提取财务报表数据
- 验证数据完整性

### 2. 数据分析技能 (`data_analysis`)
- 计算财务指标（盈利能力、偿债能力等）
- 趋势分析和对比分析
- 财务比率分析
- 行业基准对比

### 3. 风险检测技能 (`risk_detection`)
- 识别财务风险
- 评估风险等级
- 阈值分析
- 风险评分
- 生成风险缓解建议

### 4. 报告写作技能 (`report_writing`)
- 生成财务分析报告
- 模板渲染
- 数据可视化
- 生成执行摘要
- 建议综合

## 工作流

### 完整分析工作流
1. **PDF文件验证** → 2. **数据提取** → 3. **数据分析** → 4. **风险评估** → 5. **报告生成** → 6. **质量检查**

### 快速分析工作流
1. **数据提取和分析** → 2. **风险评估** → 3. **报告生成**

## 配置说明

### 主配置文件 (`configs/main_config.yaml`)
- 系统设置（语言、时区、日志级别）
- Agent配置（启用状态、技能关联）
- 技能配置（依赖库、参数）
- 工作流配置
- 性能配置（超时、内存限制）
- 输出配置（格式、包含内容）

### 工作流配置 (`workflows/financial_analysis_workflow.yaml`)
- 工作流步骤定义
- 输入输出定义
- 错误处理策略
- 监控指标
- 通知配置

## 使用方法

### 1. 启动系统
```bash
# 安装依赖
pip install -r requirements.txt

# 启动主Agent
python -m agents.financial_analysis.main
```

### 2. 运行分析
```yaml
# 配置文件示例
inputs:
  pdf_file: "inputs/company_report.pdf"
  company_name: "示例公司"
  report_year: 2025
  output_format: "markdown"

workflow: "full_analysis"
```

### 3. 查看结果
- 分析报告：`outputs/reports/`
- 财务指标：`outputs/data/indicators.json`
- 风险评估：`outputs/data/risk_assessment.json`
- 日志文件：`logs/`

## 扩展开发

### 添加新Agent
1. 在 `agents/` 目录下创建新Agent目录
2. 创建 `agent.yaml` 配置文件
3. 定义Agent的职责、技能、输入输出
4. 在主配置文件中注册Agent

### 添加新技能
1. 在 `skills/` 目录下创建新技能目录
2. 创建 `skill.yaml` 配置文件
3. 定义技能的能力、参数、依赖
4. 在相关Agent中引用该技能

### 创建新工作流
1. 在 `workflows/` 目录下创建YAML文件
2. 定义工作流步骤和顺序
3. 配置输入输出映射
4. 设置错误处理和监控

## 性能优化

### 并行处理
- 支持多个Agent并行执行
- 可配置最大并发任务数
- 智能任务调度

### 缓存机制
- 数据提取结果缓存
- 分析结果缓存
- 可配置缓存TTL

### 资源管理
- 内存使用限制
- 超时控制
- 错误重试机制

## 监控和日志

### 监控指标
- 处理时间
- 成功率
- 错误率
- 资源使用率

### 日志级别
- DEBUG: 详细调试信息
- INFO: 常规操作信息
- WARNING: 警告信息
- ERROR: 错误信息

### 通知机制
- 完成通知
- 错误通知
- 警告通知
- 支持多种通知渠道

## 迁移说明

### 从Python架构迁移
1. **功能对应关系**：
   - `src/core/pdf_extractor.py` → `skills/pdf_processing/`
   - `src/core/data_extractor.py` → `agents/data_extraction/`
   - `src/core/indicator_calculator.py` → `skills/data_analysis/`
   - `src/core/risk_detector.py` → `skills/risk_detection/`
   - `src/core/report_generator.py` → `skills/report_writing/`

2. **配置迁移**：
   - `config/config.yaml` → `configs/main_config.yaml`
   - 风险阈值和行业基准配置保持不变

3. **数据迁移**：
   - 现有数据文件可继续使用
   - 输出格式保持兼容

### 优势对比
| 特性 | Python架构 | Agent架构 |
|------|------------|-----------|
| 模块化 | 中等 | 优秀 |
| 可扩展性 | 一般 | 优秀 |
| 维护性 | 中等 | 优秀 |
| 灵活性 | 一般 | 优秀 |
| 协作性 | 有限 | 优秀 |

## 故障排除

### 常见问题
1. **Agent启动失败**：检查依赖库是否安装
2. **PDF解析错误**：检查PDF文件格式和权限
3. **内存不足**：调整 `performance.memory_limit_mb` 配置
4. **超时错误**：调整 `performance.timeout_seconds` 配置

### 调试模式
```yaml
# 在配置中启用调试
settings:
  log_level: "DEBUG"
  debug_mode: true
```

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：support@financial-reports.com
- GitHub Issues：项目问题跟踪
