"""
工具模块

该模块提供财报分析系统的基础工具能力，包括：
- 文件管理：文件读写、目录操作、路径处理
- 配置加载：YAML配置文件加载和验证
- 日志记录：统一的日志记录功能
- 数据验证：各类数据有效性验证
"""

from .file_manager import (
    FileManager,
    FileManagerError,
    FileNotFoundError,
    PermissionError,
    InvalidPathError
)

from .config_loader import (
    ConfigLoader,
    ConfigLoaderError,
    ConfigFileNotFoundError,
    ConfigValidationError,
    ConfigParseError
)

from .logger import (
    LoggerManager,
    ContextLogger,
    setup_logger,
    get_logger,
    create_context_logger
)

from .validator import (
    Validator,
    ValidationResult,
    ValidationError,
    TypeValidationError,
    RangeValidationError,
    FormatValidationError,
    LogicValidationError,
    validate_email,
    validate_phone,
    validate_url
)

__all__ = [
    # 文件管理
    'FileManager',
    'FileManagerError',
    'FileNotFoundError',
    'PermissionError',
    'InvalidPathError',

    # 配置加载
    'ConfigLoader',
    'ConfigLoaderError',
    'ConfigFileNotFoundError',
    'ConfigValidationError',
    'ConfigParseError',

    # 日志记录
    'LoggerManager',
    'ContextLogger',
    'setup_logger',
    'get_logger',
    'create_context_logger',

    # 数据验证
    'Validator',
    'ValidationResult',
    'ValidationError',
    'TypeValidationError',
    'RangeValidationError',
    'FormatValidationError',
    'LogicValidationError',
    'validate_email',
    'validate_phone',
    'validate_url'
]
