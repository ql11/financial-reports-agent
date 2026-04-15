# 财报分析系统 - Agent架构

## 📋 项目概述

本项目是一个基于Agent架构的财报分析系统，专门用于自动化分析上市公司财务报告。系统采用模块化设计，通过多个专业Agent协同工作，提供完整的财务分析解决方案。

## 🏗️ 架构设计

### 核心架构
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

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements_agent.txt

# 创建必要目录
mkdir -p logs inputs outputs data/raw data/processed data/results
```

### 2. 启动系统
```bash
# 启动Agent系统
python run_agent.py
```

### 3. 运行分析
将PDF财报文件放入 `inputs/` 目录，然后运行：
```bash
# 示例：分析单个财报
python run_agent.py --file inputs/company_report.pdf --company "示例公司" --year 2025
```

## 🤖 Agent说明

### 财务分析主Agent (`financial_analysis_agent`)
- **职责**：协调整个分析流程
- **技能**：PDF处理、数据分析、风险检测、报告写作
- **输入**：PDF财报文件
- **输出**：完整的财务分析报告

### 数据提取Agent (`data_extraction_agent`)
- **职责**：从PDF提取结构化财务数据
- **技能**：PDF处理
- **输入**：PDF文件
- **输出**：结构化财务数据

### 风险评估Agent (`risk_assessment_agent`)
- **职责**：识别和评估财务风险
- **技能**：风险检测、数据分析
- **输入**：财务指标
- **输出**：风险评估结果和建议

### 报告生成Agent (`report_generation_agent`)
- **职责**：生成专业财务分析报告
- **技能**：报告写作、数据分析
- **输入**：分析结果
- **输出**：格式化的分析报告

## 🔧 技能说明

### PDF处理技能 (`pdf_processing`)
- 从PDF文件中提取文本和表格数据
- 检测和解析PDF中的表格
- 提取财务报表数据
- 验证数据完整性

### 数据分析技能 (`data_analysis`)
- 计算财务指标（盈利能力、偿债能力等）
- 趋势分析和对比分析
- 财务比率分析
- 行业基准对比

### 风险检测技能 (`risk_detection`)
- 识别财务风险
- 评估风险等级
- 阈值分析
- 风险评分
- 生成风险缓解建议

### 报告写作技能 (`report_writing`)
- 生成财务分析报告
- 模板渲染
- 数据可视化
- 生成执行摘要
- 建议综合

## 📊 工作流

### 完整分析工作流
1. **PDF文件验证** → 2. **数据提取** → 3. **数据分析** → 4. **风险评估** → 5. **报告生成** → 6. **质量检查**

### 快速分析工作流
1. **数据提取和分析** → 2. **风险评估** → 3. **报告生成**

## ⚙️ 配置说明

### 主配置文件 (`configs/main_config.yaml`)
```yaml
# 系统设置
settings:
  language: "zh-CN"
  timezone: "Asia/Shanghai"
  log_level: "INFO"
  max_concurrent_tasks: 5

# Agent配置
agents:
  financial_analysis:
    enabled: true
    config_file: "./agents/financial_analysis/agent.yaml"
    skills:
      - pdf_processing
      - data_analysis
      - risk_detection
      - report_writing
```

### 工作流配置 (`workflows/financial_analysis_workflow.yaml`)
```yaml
# 工作流定义
workflow:
  name: "财报分析完整流程"
  steps:
    - step: "数据提取"
      agent: "data_extraction_agent"
    - step: "数据分析"
      agent: "financial_analysis_agent"
    - step: "风险评估"
      agent: "risk_assessment_agent"
    - step: "报告生成"
      agent: "report_generation_agent"
```

## 📁 目录结构说明

- `agents/` - 包含所有Agent的YAML配置文件
- `skills/` - 包含所有技能的YAML配置文件
- `configs/` - 系统配置文件
- `workflows/` - 工作流定义文件
- `data/` - 数据存储目录
  - `raw/` - 原始数据
  - `processed/` - 处理后的数据
  - `results/` - 分析结果
- `inputs/` - 输入文件目录（放置PDF财报）
- `outputs/` - 输出文件目录
- `reports/` - 生成的报告文件
- `logs/` - 系统日志

## 🎯 功能特性

### 核心功能
- ✅ PDF财报自动解析
- ✅ 财务指标自动计算
- ✅ 风险智能识别
- ✅ 专业报告生成
- ✅ 多格式输出支持

### 高级功能
- 🔄 工作流编排
- 📊 数据可视化
- ⚠️ 风险预警
- 📈 趋势分析
- 🎯 行业对比

### 性能特性
- ⚡ 并行处理
- 💾 缓存机制
- 📈 可扩展架构
- 🔧 配置驱动
- 📋 监控和日志

## 🔄 迁移说明

### 从Python架构迁移
本项目已从传统的Python核心架构迁移到Agent架构，主要变化包括：

1. **架构重构**：从单一应用拆分为多个Agent
2. **配置驱动**：使用YAML配置文件管理
3. **模块化设计**：每个功能模块独立
4. **工作流支持**：支持复杂的工作流编排

### 文件对应关系
| Python架构 | Agent架构 |
|------------|-----------|
| `src/core/` | `skills/` + `agents/` |
| `config/config.yaml` | `configs/main_config.yaml` |
| `src/main.py` | `run_agent.py` + 工作流配置 |

## 🛠️ 开发指南

### 添加新Agent
1. 在 `agents/` 目录下创建新目录
2. 创建 `agent.yaml` 配置文件
3. 定义Agent的职责、技能、输入输出
4. 在 `configs/main_config.yaml` 中注册Agent

### 添加新技能
1. 在 `skills/` 目录下创建新目录
2. 创建 `skill.yaml` 配置文件
3. 定义技能的能力、参数、依赖
4. 在相关Agent中引用该技能

### 创建新工作流
1. 在 `workflows/` 目录下创建YAML文件
2. 定义工作流步骤和顺序
3. 配置输入输出映射
4. 设置错误处理和监控

## 📈 性能优化

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

## 📊 监控和日志

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

## 🐛 故障排除

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

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：support@financial-reports.com
- GitHub Issues：项目问题跟踪

---

**🎯 项目状态**：Agent架构重构完成，系统已就绪！

**📅 最后更新**：2026-04-15

**🔧 版本**：v2.0.0 (Agent架构)
