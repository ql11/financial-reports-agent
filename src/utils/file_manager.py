"""
文件管理器模块

该模块提供文件和目录操作的基础工具，包括文件读写、目录创建、文件复制、路径处理等功能。

功能特性：
- 支持文本文件和二进制文件的读写操作
- 提供跨平台的路径处理功能
- 支持递归创建目录
- 支持文件复制操作
- 完善的异常处理和日志记录
- 路径安全性检查，防止路径遍历攻击
"""

import os
import shutil
from pathlib import Path
from typing import Union, Optional, List, BinaryIO
import logging

# 设置模块日志
logger = logging.getLogger(__name__)


class FileManagerError(Exception):
    """文件管理器基础异常"""
    pass


class FileNotFoundError(FileManagerError):
    """文件不存在异常"""
    pass


class PermissionError(FileManagerError):
    """权限不足异常"""
    pass


class InvalidPathError(FileManagerError):
    """路径无效异常"""
    pass


class FileManager:
    """文件管理器

    提供文件和目录操作的基础工具类，支持跨平台操作。

    Attributes:
        base_path: 基础路径，用于相对路径解析
        encoding: 默认文件编码
        max_file_size: 最大文件大小限制（字节）
    """

    def __init__(
        self,
        base_path: Optional[Union[str, Path]] = None,
        encoding: str = 'utf-8',
        max_file_size: int = 100 * 1024 * 1024  # 100MB
    ):
        """初始化文件管理器

        Args:
            base_path: 基础路径，默认为当前工作目录
            encoding: 默认文件编码，默认为UTF-8
            max_file_size: 最大文件大小限制（字节），默认为100MB
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.encoding = encoding
        self.max_file_size = max_file_size

        logger.info(f"文件管理器初始化完成，基础路径: {self.base_path}")

    def _validate_path(self, file_path: Union[str, Path]) -> Path:
        """验证并规范化文件路径

        Args:
            file_path: 待验证的文件路径

        Returns:
            Path: 规范化后的绝对路径

        Raises:
            InvalidPathError: 路径无效时抛出
        """
        try:
            path = Path(file_path)

            # 如果是相对路径，则相对于base_path
            if not path.is_absolute():
                path = self.base_path / path

            # 规范化路径（解析..和.）
            path = path.resolve()

            # 安全性检查：防止路径遍历攻击
            try:
                path.relative_to(self.base_path.resolve())
            except ValueError:
                logger.error(f"路径遍历攻击检测: {file_path}")
                raise InvalidPathError(f"路径无效：检测到路径遍历攻击 - {file_path}")

            return path

        except Exception as e:
            logger.error(f"路径验证失败: {file_path}, 错误: {e}")
            raise InvalidPathError(f"路径无效：{file_path}")

    def _check_file_size(self, file_path: Path) -> None:
        """检查文件大小是否超过限制

        Args:
            file_path: 文件路径

        Raises:
            FileManagerError: 文件大小超过限制时抛出
        """
        if file_path.exists():
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                logger.error(f"文件大小超过限制: {file_path}, 大小: {file_size}字节")
                raise FileManagerError(
                    f"文件大小超过限制: {file_path}, "
                    f"最大允许: {self.max_file_size}字节, "
                    f"实际大小: {file_size}字节"
                )

    def read_text(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None
    ) -> str:
        """读取文本文件

        Args:
            file_path: 文件路径
            encoding: 文件编码，默认使用初始化时设置的编码

        Returns:
            str: 文件内容

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(file_path)
        encoding = encoding or self.encoding

        logger.debug(f"读取文本文件: {path}")

        if not path.exists():
            logger.error(f"文件不存在: {path}")
            raise FileNotFoundError(f"文件不存在：{path}")

        if not path.is_file():
            logger.error(f"路径不是文件: {path}")
            raise InvalidPathError(f"路径不是文件：{path}")

        self._check_file_size(path)

        try:
            content = path.read_text(encoding=encoding)
            logger.debug(f"成功读取文件，大小: {len(content)}字符")
            return content
        except PermissionError as e:
            logger.error(f"权限不足，无法读取文件: {path}")
            raise PermissionError(f"权限不足：{path}")
        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误: {path}, 编码: {encoding}")
            raise FileManagerError(f"文件编码错误：{path}，请尝试其他编码")

    def read_binary(self, file_path: Union[str, Path]) -> bytes:
        """读取二进制文件

        Args:
            file_path: 文件路径

        Returns:
            bytes: 文件内容

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(file_path)

        logger.debug(f"读取二进制文件: {path}")

        if not path.exists():
            logger.error(f"文件不存在: {path}")
            raise FileNotFoundError(f"文件不存在：{path}")

        if not path.is_file():
            logger.error(f"路径不是文件: {path}")
            raise InvalidPathError(f"路径不是文件：{path}")

        self._check_file_size(path)

        try:
            content = path.read_bytes()
            logger.debug(f"成功读取文件，大小: {len(content)}字节")
            return content
        except PermissionError as e:
            logger.error(f"权限不足，无法读取文件: {path}")
            raise PermissionError(f"权限不足：{path}")

    def write_text(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: Optional[str] = None,
        create_dirs: bool = True
    ) -> None:
        """写入文本文件

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码，默认使用初始化时设置的编码
            create_dirs: 是否自动创建父目录，默认为True

        Raises:
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(file_path)
        encoding = encoding or self.encoding

        logger.debug(f"写入文本文件: {path}")

        # 自动创建父目录
        if create_dirs and not path.parent.exists():
            self.create_directory(path.parent)
            logger.debug(f"自动创建目录: {path.parent}")

        try:
            path.write_text(content, encoding=encoding)
            logger.debug(f"成功写入文件，大小: {len(content)}字符")
        except PermissionError as e:
            logger.error(f"权限不足，无法写入文件: {path}")
            raise PermissionError(f"权限不足：{path}")

    def write_binary(
        self,
        file_path: Union[str, Path],
        content: bytes,
        create_dirs: bool = True
    ) -> None:
        """写入二进制文件

        Args:
            file_path: 文件路径
            content: 文件内容
            create_dirs: 是否自动创建父目录，默认为True

        Raises:
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(file_path)

        logger.debug(f"写入二进制文件: {path}")

        # 自动创建父目录
        if create_dirs and not path.parent.exists():
            self.create_directory(path.parent)
            logger.debug(f"自动创建目录: {path.parent}")

        try:
            path.write_bytes(content)
            logger.debug(f"成功写入文件，大小: {len(content)}字节")
        except PermissionError as e:
            logger.error(f"权限不足，无法写入文件: {path}")
            raise PermissionError(f"权限不足：{path}")

    def create_directory(
        self,
        dir_path: Union[str, Path],
        parents: bool = True,
        exist_ok: bool = True
    ) -> None:
        """创建目录

        Args:
            dir_path: 目录路径
            parents: 是否创建父目录，默认为True
            exist_ok: 目录已存在时是否忽略，默认为True

        Raises:
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(dir_path)

        logger.debug(f"创建目录: {path}")

        if path.exists() and not exist_ok:
            logger.error(f"目录已存在: {path}")
            raise FileManagerError(f"目录已存在：{path}")

        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
            logger.debug(f"成功创建目录: {path}")
        except PermissionError as e:
            logger.error(f"权限不足，无法创建目录: {path}")
            raise PermissionError(f"权限不足：{path}")

    def copy_file(
        self,
        src_path: Union[str, Path],
        dst_path: Union[str, Path],
        create_dirs: bool = True
    ) -> None:
        """复制文件

        Args:
            src_path: 源文件路径
            dst_path: 目标文件路径
            create_dirs: 是否自动创建目标目录，默认为True

        Raises:
            FileNotFoundError: 源文件不存在时抛出
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        src = self._validate_path(src_path)
        dst = self._validate_path(dst_path)

        logger.debug(f"复制文件: {src} -> {dst}")

        if not src.exists():
            logger.error(f"源文件不存在: {src}")
            raise FileNotFoundError(f"源文件不存在：{src}")

        if not src.is_file():
            logger.error(f"源路径不是文件: {src}")
            raise InvalidPathError(f"源路径不是文件：{src}")

        # 自动创建目标目录
        if create_dirs and not dst.parent.exists():
            self.create_directory(dst.parent)
            logger.debug(f"自动创建目标目录: {dst.parent}")

        try:
            shutil.copy2(src, dst)
            logger.debug(f"成功复制文件")
        except PermissionError as e:
            logger.error(f"权限不足，无法复制文件: {src} -> {dst}")
            raise PermissionError(f"权限不足：无法复制文件到 {dst}")

    def delete_file(self, file_path: Union[str, Path]) -> None:
        """删除文件

        Args:
            file_path: 文件路径

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(file_path)

        logger.debug(f"删除文件: {path}")

        if not path.exists():
            logger.error(f"文件不存在: {path}")
            raise FileNotFoundError(f"文件不存在：{path}")

        if not path.is_file():
            logger.error(f"路径不是文件: {path}")
            raise InvalidPathError(f"路径不是文件：{path}")

        try:
            path.unlink()
            logger.debug(f"成功删除文件: {path}")
        except PermissionError as e:
            logger.error(f"权限不足，无法删除文件: {path}")
            raise PermissionError(f"权限不足：{path}")

    def delete_directory(
        self,
        dir_path: Union[str, Path],
        recursive: bool = False
    ) -> None:
        """删除目录

        Args:
            dir_path: 目录路径
            recursive: 是否递归删除，默认为False

        Raises:
            FileNotFoundError: 目录不存在时抛出
            PermissionError: 权限不足时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(dir_path)

        logger.debug(f"删除目录: {path}")

        if not path.exists():
            logger.error(f"目录不存在: {path}")
            raise FileNotFoundError(f"目录不存在：{path}")

        if not path.is_dir():
            logger.error(f"路径不是目录: {path}")
            raise InvalidPathError(f"路径不是目录：{path}")

        try:
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()
            logger.debug(f"成功删除目录: {path}")
        except PermissionError as e:
            logger.error(f"权限不足，无法删除目录: {path}")
            raise PermissionError(f"权限不足：{path}")

    def list_files(
        self,
        dir_path: Union[str, Path],
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """列出目录中的文件

        Args:
            dir_path: 目录路径
            pattern: 文件匹配模式，默认为"*"
            recursive: 是否递归搜索，默认为False

        Returns:
            List[Path]: 文件路径列表

        Raises:
            FileNotFoundError: 目录不存在时抛出
            InvalidPathError: 路径无效时抛出
        """
        path = self._validate_path(dir_path)

        logger.debug(f"列出目录文件: {path}, 模式: {pattern}, 递归: {recursive}")

        if not path.exists():
            logger.error(f"目录不存在: {path}")
            raise FileNotFoundError(f"目录不存在：{path}")

        if not path.is_dir():
            logger.error(f"路径不是目录: {path}")
            raise InvalidPathError(f"路径不是目录：{path}")

        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))

        # 只返回文件，不返回目录
        files = [f for f in files if f.is_file()]

        logger.debug(f"找到 {len(files)} 个文件")
        return files

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否存在
        """
        try:
            path = self._validate_path(file_path)
            return path.exists() and path.is_file()
        except InvalidPathError:
            return False

    def directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """检查目录是否存在

        Args:
            dir_path: 目录路径

        Returns:
            bool: 目录是否存在
        """
        try:
            path = self._validate_path(dir_path)
            return path.exists() and path.is_dir()
        except InvalidPathError:
            return False

    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            int: 文件大小（字节）

        Raises:
            FileNotFoundError: 文件不存在时抛出
        """
        path = self._validate_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")

        return path.stat().st_size

    def get_absolute_path(self, file_path: Union[str, Path]) -> Path:
        """获取绝对路径

        Args:
            file_path: 文件路径

        Returns:
            Path: 绝对路径
        """
        return self._validate_path(file_path)
