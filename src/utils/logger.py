"""
日志工具模块

该模块提供统一的日志记录功能，支持控制台输出和文件输出，支持日志轮转和彩色显示。

功能特性：
- 统一的日志初始化接口
- 支持同时输出到控制台和文件
- 支持日志文件轮转（按大小和时间）
- 支持控制台彩色输出
- 支持自定义日志格式
- 自动创建日志目录
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Union, Dict, Any
import colorlog


class LoggerError(Exception):
    """日志工具异常"""
    pass


class LoggerManager:
    """日志管理器

    提供统一的日志初始化和管理功能。

    Attributes:
        loggers: 已创建的日志器字典
        default_config: 默认日志配置
    """

    _instance = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化日志管理器"""
        if self._initialized:
            return

        self.loggers: Dict[str, logging.Logger] = {}
        self.default_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'console_output': True,
            'file_output': False,
            'log_dir': 'logs',
            'filename': 'app.log',
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'colorlog': True
        }
        self._initialized = True

    def create_logger(
        self,
        name: str,
        level: Optional[str] = None,
        log_dir: Optional[Union[str, Path]] = None,
        filename: Optional[str] = None,
        console_output: Optional[bool] = None,
        file_output: Optional[bool] = None,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None,
        format_str: Optional[str] = None,
        date_format: Optional[str] = None,
        use_colorlog: Optional[bool] = None,
        **kwargs
    ) -> logging.Logger:
        """创建日志器

        Args:
            name: 日志器名称
            level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            log_dir: 日志目录
            filename: 日志文件名
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留日志文件数量
            format_str: 日志格式字符串
            date_format: 日期格式字符串
            use_colorlog: 是否使用彩色日志
            **kwargs: 其他配置参数

        Returns:
            logging.Logger: 日志器对象
        """
        # 如果日志器已存在，直接返回
        if name in self.loggers:
            return self.loggers[name]

        # 合并配置
        config = self.default_config.copy()
        if level:
            config['level'] = level
        if log_dir:
            config['log_dir'] = str(log_dir)
        if filename:
            config['filename'] = filename
        if console_output is not None:
            config['console_output'] = console_output
        if file_output is not None:
            config['file_output'] = file_output
        if max_bytes:
            config['max_bytes'] = max_bytes
        if backup_count:
            config['backup_count'] = backup_count
        if format_str:
            config['format'] = format_str
        if date_format:
            config['date_format'] = date_format
        if use_colorlog is not None:
            config['colorlog'] = use_colorlog

        # 创建日志器
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config['level'].upper()))

        # 清除已有的处理器
        logger.handlers.clear()

        # 添加控制台处理器
        if config['console_output']:
            self._add_console_handler(logger, config)

        # 添加文件处理器
        if config['file_output']:
            self._add_file_handler(logger, config)

        # 保存日志器
        self.loggers[name] = logger

        return logger

    def _add_console_handler(
        self,
        logger: logging.Logger,
        config: Dict[str, Any]
    ) -> None:
        """添加控制台处理器

        Args:
            logger: 日志器
            config: 配置字典
        """
        if config['colorlog']:
            # 使用彩色日志
            console_format = (
                '%(log_color)s%(asctime)s - %(name)s - '
                '%(levelname)s - %(message)s%(reset)s'
            )
            formatter = colorlog.ColoredFormatter(
                console_format,
                datefmt=config['date_format'],
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
        else:
            # 普通日志
            formatter = logging.Formatter(
                config['format'],
                datefmt=config['date_format']
            )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    def _add_file_handler(
        self,
        logger: logging.Logger,
        config: Dict[str, Any]
    ) -> None:
        """添加文件处理器

        Args:
            logger: 日志器
            config: 配置字典
        """
        # 创建日志目录
        log_dir = Path(config['log_dir'])
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"无法创建日志目录: {log_dir}，仅输出到控制台")
            return

        # 日志文件路径
        log_file = log_dir / config['filename']

        try:
            # 创建轮转文件处理器
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=config['max_bytes'],
                backupCount=config['backup_count'],
                encoding='utf-8'
            )

            # 设置格式
            formatter = logging.Formatter(
                config['format'],
                datefmt=config['date_format']
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        except Exception as e:
            logger.warning(f"无法创建日志文件: {log_file}，仅输出到控制台")

    def get_logger(self, name: str) -> logging.Logger:
        """获取日志器

        Args:
            name: 日志器名称

        Returns:
            logging.Logger: 日志器对象
        """
        if name not in self.loggers:
            return self.create_logger(name)
        return self.loggers[name]

    def remove_logger(self, name: str) -> None:
        """移除日志器

        Args:
            name: 日志器名称
        """
        if name in self.loggers:
            logger = self.loggers[name]
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            del self.loggers[name]

    def set_level(self, name: str, level: str) -> None:
        """设置日志级别

        Args:
            name: 日志器名称
            level: 日志级别
        """
        if name in self.loggers:
            self.loggers[name].setLevel(getattr(logging, level.upper()))

    def shutdown(self) -> None:
        """关闭所有日志器"""
        for name in list(self.loggers.keys()):
            self.remove_logger(name)


# 全局日志管理器实例
logger_manager = LoggerManager()


def setup_logger(
    name: str = 'financial_analysis',
    level: str = 'INFO',
    log_dir: Union[str, Path] = 'logs',
    filename: str = 'financial_analysis.log',
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    use_colorlog: bool = True,
    **kwargs
) -> logging.Logger:
    """设置日志器（便捷函数）

    Args:
        name: 日志器名称
        level: 日志级别
        log_dir: 日志目录
        filename: 日志文件名
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留日志文件数量
        use_colorlog: 是否使用彩色日志
        **kwargs: 其他配置参数

    Returns:
        logging.Logger: 日志器对象
    """
    return logger_manager.create_logger(
        name=name,
        level=level,
        log_dir=log_dir,
        filename=filename,
        console_output=console_output,
        file_output=file_output,
        max_bytes=max_bytes,
        backup_count=backup_count,
        use_colorlog=use_colorlog,
        **kwargs
    )


def get_logger(name: str = 'financial_analysis') -> logging.Logger:
    """获取日志器（便捷函数）

    Args:
        name: 日志器名称

    Returns:
        logging.Logger: 日志器对象
    """
    return logger_manager.get_logger(name)


class ContextLogger:
    """上下文日志器

    提供带上下文信息的日志记录功能。

    Attributes:
        logger: 基础日志器
        context: 上下文信息
    """

    def __init__(
        self,
        logger: logging.Logger,
        context: Optional[Dict[str, Any]] = None
    ):
        """初始化上下文日志器

        Args:
            logger: 基础日志器
            context: 上下文信息
        """
        self.logger = logger
        self.context = context or {}

    def _format_message(self, message: str) -> str:
        """格式化消息，添加上下文信息

        Args:
            message: 原始消息

        Returns:
            str: 格式化后的消息
        """
        if self.context:
            context_str = ' | '.join(f"{k}={v}" for k, v in self.context.items())
            return f"[{context_str}] {message}"
        return message

    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志"""
        self.logger.debug(self._format_message(message), **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志"""
        self.logger.info(self._format_message(message), **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志"""
        self.logger.warning(self._format_message(message), **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录ERROR级别日志"""
        self.logger.error(self._format_message(message), **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """记录CRITICAL级别日志"""
        self.logger.critical(self._format_message(message), **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """记录异常日志"""
        self.logger.exception(self._format_message(message), **kwargs)

    def add_context(self, key: str, value: Any) -> None:
        """添加上下文信息

        Args:
            key: 键
            value: 值
        """
        self.context[key] = value

    def remove_context(self, key: str) -> None:
        """移除上下文信息

        Args:
            key: 键
        """
        self.context.pop(key, None)

    def clear_context(self) -> None:
        """清空上下文信息"""
        self.context.clear()


def create_context_logger(
    name: str = 'financial_analysis',
    context: Optional[Dict[str, Any]] = None
) -> ContextLogger:
    """创建上下文日志器（便捷函数）

    Args:
        name: 日志器名称
        context: 上下文信息

    Returns:
        ContextLogger: 上下文日志器
    """
    logger = get_logger(name)
    return ContextLogger(logger, context)
