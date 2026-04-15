"""
文件工具函数
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> Path:
    """确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        Path: 目录Path对象
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> bool:
    """保存数据为JSON文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        indent: 缩进空格数
        
    Returns:
        bool: 是否成功
    """
    try:
        path = Path(filepath)
        ensure_directory(path.parent)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        logger.info(f"JSON文件已保存: {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {e}")
        return False


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """从JSON文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[Dict[str, Any]]: 加载的数据，失败返回None
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error(f"JSON文件不存在: {filepath}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"JSON文件已加载: {filepath}")
        return data
    except Exception as e:
        logger.error(f"加载JSON文件失败: {e}")
        return None


def save_yaml(data: Dict[str, Any], filepath: str) -> bool:
    """保存数据为YAML文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        path = Path(filepath)
        ensure_directory(path.parent)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"YAML文件已保存: {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存YAML文件失败: {e}")
        return False


def load_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    """从YAML文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[Dict[str, Any]]: 加载的数据，失败返回None
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error(f"YAML文件不存在: {filepath}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        logger.info(f"YAML文件已加载: {filepath}")
        return data
    except Exception as e:
        logger.error(f"加载YAML文件失败: {e}")
        return None


def save_markdown(content: str, filepath: str) -> bool:
    """保存内容为Markdown文件
    
    Args:
        content: Markdown内容
        filepath: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        path = Path(filepath)
        ensure_directory(path.parent)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Markdown文件已保存: {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存Markdown文件失败: {e}")
        return False


def read_markdown(filepath: str) -> Optional[str]:
    """读取Markdown文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[str]: 文件内容，失败返回None
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error(f"Markdown文件不存在: {filepath}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Markdown文件已读取: {filepath}")
        return content
    except Exception as e:
        logger.error(f"读取Markdown文件失败: {e}")
        return None


def get_file_size(filepath: str) -> Optional[int]:
    """获取文件大小（字节）
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[int]: 文件大小，失败返回None
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error(f"文件不存在: {filepath}")
            return None
        
        return path.stat().st_size
    except Exception as e:
        logger.error(f"获取文件大小失败: {e}")
        return None


def get_file_extension(filepath: str) -> Optional[str]:
    """获取文件扩展名
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[str]: 文件扩展名，失败返回None
    """
    try:
        path = Path(filepath)
        return path.suffix.lower()
    except Exception as e:
        logger.error(f"获取文件扩展名失败: {e}")
        return None


def list_files(directory: str, pattern: str = "*") -> list:
    """列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件模式
        
    Returns:
        list: 文件路径列表
    """
    try:
        path = Path(directory)
        if not path.exists():
            logger.error(f"目录不存在: {directory}")
            return []
        
        files = list(path.glob(pattern))
        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        return []