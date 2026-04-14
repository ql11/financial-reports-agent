# 工具模块使用说明

本模块为财报分析系统提供基础工具能力，包括文件管理、配置加载、日志记录和数据验证等功能。

## 模块结构

```
src/utils/
├── __init__.py           # 模块初始化，导出所有工具类
├── file_manager.py       # 文件管理器
├── config_loader.py      # 配置加载器
├── logger.py            # 日志工具
└── validator.py         # 数据验证器
```

## 1. 文件管理器 (FileManager)

### 功能特性
- 支持文本文件和二进制文件的读写操作
- 提供跨平台的路径处理功能
- 支持递归创建目录
- 支持文件复制操作
- 完善的异常处理和日志记录
- 路径安全性检查，防止路径遍历攻击

### 使用示例

```python
from src.utils import FileManager

# 创建文件管理器
fm = FileManager(base_path='./')

# 读取文本文件
content = fm.read_text('config/config.yaml')

# 写入文本文件
fm.write_text('output/result.txt', 'Hello, World!')

# 创建目录
fm.create_directory('output/data')

# 复制文件
fm.copy_file('source/file.txt', 'backup/file.txt')

# 列出目录中的文件
files = fm.list_files('data', pattern='*.csv', recursive=True)

# 检查文件是否存在
if fm.file_exists('config.yaml'):
    print("文件存在")
```

## 2. 配置加载器 (ConfigLoader)

### 功能特性
- 支持YAML格式配置文件加载
- 配置验证和类型检查
- 默认配置与用户配置合并
- 便捷的点分隔路径访问
- 配置热重载

### 使用示例

```python
from src.utils import ConfigLoader

# 创建配置加载器
loader = ConfigLoader(config_path='config/config.yaml')

# 获取配置项（支持点分隔路径）
log_level = loader.get('logging.level')
log_file = loader.get('logging.filename')

# 获取配置项，提供默认值
timeout = loader.get('performance.timeout', default=120)

# 设置配置项
loader.set('logging.level', 'DEBUG')

# 保存配置到文件
loader.save()

# 重新加载配置
loader.reload()
```

## 3. 日志工具 (Logger)

### 功能特性
- 统一的日志初始化接口
- 支持同时输出到控制台和文件
- 支持日志文件轮转（按大小和时间）
- 支持控制台彩色输出
- 支持自定义日志格式
- 自动创建日志目录

### 使用示例

```python
from src.utils import setup_logger, get_logger, create_context_logger

# 创建日志器
logger = setup_logger(
    name='financial_analysis',
    level='INFO',
    log_dir='logs',
    filename='app.log',
    console_output=True,
    file_output=True,
    use_colorlog=True
)

# 记录日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 使用上下文日志器
context_logger = create_context_logger(
    name='financial_analysis',
    context={'module': 'analyzer', 'function': 'parse_pdf'}
)
context_logger.info("处理PDF文件")
```

## 4. 数据验证器 (Validator)

### 功能特性
- 数值范围和类型验证
- 日期格式验证
- 文件路径验证
- 财务数据逻辑验证
- 批量验证支持
- 数据清洗功能

### 使用示例

```python
from src.utils import Validator

# 创建验证器
validator = Validator()

# 验证数值
result = validator.validate_number(
    value=100,
    min_value=0,
    max_value=200,
    field_name="金额"
)
if result.is_valid:
    print(f"验证通过，清洗后数据: {result.cleaned_data}")
else:
    print(f"验证失败: {result.errors}")

# 验证日期
result = validator.validate_date(
    value="2024-01-01",
    format_str="%Y-%m-%d"
)

# 验证路径
result = validator.validate_path(
    value="config/config.yaml",
    must_exist=True,
    path_type="file"
)

# 验证财务数据平衡关系（资产 = 负债 + 所有者权益）
result = validator.validate_financial_balance(
    assets=1000,
    liabilities=600,
    equity=400,
    tolerance=0.01
)

# 批量验证
data = {
    'amount': 100,
    'date': '2024-01-01',
    'description': '测试数据'
}
validators = {
    'amount': lambda x: validator.validate_number(x, min_value=0),
    'date': lambda x: validator.validate_date(x),
    'description': lambda x: validator.validate_string(x, min_length=1)
}
result = validator.validate_batch(data, validators)
```

## 异常处理

所有工具模块都定义了明确的异常类：

### 文件管理器异常
- `FileManagerError`: 基础异常
- `FileNotFoundError`: 文件不存在
- `PermissionError`: 权限不足
- `InvalidPathError`: 路径无效

### 配置加载器异常
- `ConfigLoaderError`: 基础异常
- `ConfigFileNotFoundError`: 配置文件不存在
- `ConfigValidationError`: 配置验证失败
- `ConfigParseError`: 配置解析失败

### 验证器异常
- `ValidationError`: 基础异常
- `TypeValidationError`: 类型验证失败
- `RangeValidationError`: 范围验证失败
- `FormatValidationError`: 格式验证失败
- `LogicValidationError`: 逻辑验证失败

## 设计原则

1. **类型安全**: 所有函数都添加了类型注解
2. **文档完整**: 所有函数都添加了文档字符串
3. **异常处理**: 完善的异常处理和日志记录
4. **PEP8规范**: 代码符合PEP8规范
5. **跨平台兼容**: 支持Windows、Linux、macOS
6. **安全性**: 文件路径安全性检查，防止路径遍历攻击

## 性能指标

根据spec.md中的DFX约束：

- 文件读取操作响应时间不超过100ms（文件大小<10MB）
- 配置加载时间不超过500ms
- 日志写入操作响应时间不超过10ms
- 数据验证操作响应时间不超过50ms

## 依赖包

- `pyyaml>=6.0`: YAML配置文件解析
- `colorlog>=6.7.0`: 彩色日志输出
- `pathlib`: 路径处理（Python标准库）
- `logging`: 日志记录（Python标准库）
