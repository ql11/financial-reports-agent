# 快速开始指南

本指南帮助您快速上手财报分析系统。

## 第一步：环境准备

### 1. 检查Python版本
```bash
python --version
```
确保Python版本 >= 3.9

### 2. 安装依赖包
```bash
pip install -r requirements.txt
```

## 第二步：准备财报文件

1. 将PDF格式的财务报告文件放入 `source/` 文件夹
2. 确保文件命名清晰，建议格式：`公司名称_年度_报告类型.pdf`

## 第三步：配置系统（可选）

### 1. 修改主配置文件
编辑 `config/config.yaml`，根据需要调整：
- 分析维度
- 性能参数
- 日志级别

### 2. 修改风险阈值
编辑 `config/risk_thresholds.yaml`，根据行业特点调整：
- 偿债能力阈值
- 盈利能力阈值
- 成长能力阈值

### 3. 添加行业基准数据
编辑 `config/industry_benchmarks.yaml`，添加或修改：
- 行业分类
- 行业基准指标

## 第四步：运行分析

### 基本运行
```bash
python src/main.py
```

### 指定配置文件
```bash
python src/main.py --config config/custom_config.yaml
```

### 指定源文件夹
```bash
python src/main.py --source /path/to/pdf/folder
```

## 第五步：查看结果

### 1. Markdown文件
位置：`repository/` 文件夹
内容：从PDF转换的结构化Markdown文本

### 2. 分析报告
位置：`reports/` 文件夹
内容：包含以下章节的综合分析报告
- 执行摘要
- 关键指标一览表
- 详细分析
- 风险提示
- 综合评分

### 3. 日志文件
位置：`logs/` 文件夹
内容：详细的处理日志和错误信息

## 常见问题

### Q1: PDF解析失败
**原因**：PDF文件损坏或格式不标准
**解决**：
- 检查PDF文件是否完整
- 尝试重新下载或导出PDF
- 查看日志文件了解详细错误

### Q2: 数据提取不准确
**原因**：财报表格格式不标准
**解决**：
- 手动调整Markdown文件
- 重新运行分析程序
- 联系开发团队优化提取算法

### Q3: 内存不足
**原因**：处理大量或大型PDF文件
**解决**：
- 减少批处理大小（修改config.yaml中的batch_size）
- 分批处理文件
- 增加系统内存

### Q4: 处理速度慢
**原因**：PDF文件较大或数量较多
**解决**：
- 启用并行处理（修改config.yaml中的workers参数）
- 使用更快的存储设备
- 优化PDF文件大小

## 下一步

- 阅读完整文档：`README.md`
- 查看项目规范：`.codeartsdoer/specs/financial_analysis/spec.md`
- 查看技术设计：`.codeartsdoer/specs/financial_analysis/design.md`
- 查看开发任务：`.codeartsdoer/specs/financial_analysis/tasks.md`

## 获取帮助

如遇到问题，请：
1. 查看日志文件：`logs/financial_analysis.log`
2. 阅读项目文档：`README.md`
3. 提交Issue到项目仓库
