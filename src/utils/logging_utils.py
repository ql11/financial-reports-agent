"""统一日志配置。"""

import logging


DEFAULT_LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def configure_logging(verbose: bool = False) -> None:
    """配置应用日志输出。"""
    level = logging.DEBUG if verbose else logging.INFO
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(level=level, format=DEFAULT_LOG_FORMAT)
    else:
        root_logger.setLevel(level)
        for handler in root_logger.handlers:
            handler.setLevel(level)
            if handler.formatter is None:
                handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

    for noisy_logger in ("pdfminer", "pdfplumber", "PIL"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取共享 logger。"""
    return logging.getLogger(name)
