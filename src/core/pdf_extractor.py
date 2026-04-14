"""
PDF文件提取器模块

该模块负责扫描源文件夹，识别并提取PDF格式的财报文件。

功能特性：
- 扫描指定文件夹及其子文件夹中的PDF文件
- 支持批量处理PDF文件
- 支持文件过滤（按文件名、大小、修改时间等）
- 提供文件信息统计功能
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

from src.utils.logger import get_logger


class PDFExtractorError(Exception):
    """PDF提取器基础异常"""
    pass


class FolderNotFoundError(PDFExtractorError):
    """文件夹不存在异常"""
    pass


class PDFExtractor:
    """PDF文件提取器

    负责扫描源文件夹，识别并提取PDF格式的财报文件。

    Attributes:
        source_folder: 源文件夹路径
        logger: 日志器
        pdf_files: PDF文件列表
    """

    def __init__(
        self,
        source_folder: Union[str, Path],
        recursive: bool = True,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None
    ):
        """初始化PDF文件提取器

        Args:
            source_folder: 源文件夹路径
            recursive: 是否递归扫描子文件夹
            min_size: 文件最小大小（字节），None表示不限制
            max_size: 文件最大大小（字节），None表示不限制

        Raises:
            FolderNotFoundError: 源文件夹不存在时抛出
        """
        self.source_folder = Path(source_folder)
        self.recursive = recursive
        self.min_size = min_size
        self.max_size = max_size
        self.logger = get_logger('financial_analysis')
        self.pdf_files: List[Dict[str, Any]] = []

        # 验证源文件夹
        if not self.source_folder.exists():
            self.logger.error(f"源文件夹不存在: {self.source_folder}")
            raise FolderNotFoundError(f"源文件夹不存在: {self.source_folder}")

        if not self.source_folder.is_dir():
            self.logger.error(f"路径不是文件夹: {self.source_folder}")
            raise PDFExtractorError(f"路径不是文件夹: {self.source_folder}")

        self.logger.info(f"PDF提取器初始化完成，源文件夹: {self.source_folder}")

    def extract_pdf_files(self) -> List[str]:
        """提取所有PDF文件

        扫描源文件夹，识别并提取所有PDF文件。

        Returns:
            List[str]: PDF文件路径列表

        Raises:
            PDFExtractorError: 扫描过程中出现错误时抛出
        """
        self.logger.info(f"开始扫描PDF文件，源文件夹: {self.source_folder}")
        self.pdf_files = []

        try:
            # 扫描PDF文件
            if self.recursive:
                pdf_paths = list(self.source_folder.rglob("*.pdf"))
            else:
                pdf_paths = list(self.source_folder.glob("*.pdf"))

            # 过滤并收集文件信息
            for pdf_path in pdf_paths:
                file_info = self._get_file_info(pdf_path)

                # 应用过滤器
                if self._filter_file(file_info):
                    self.pdf_files.append(file_info)

            # 按文件名排序
            self.pdf_files.sort(key=lambda x: x['filename'])

            self.logger.info(f"扫描完成，共找到 {len(self.pdf_files)} 个PDF文件")

            # 返回文件路径列表
            return [file_info['path'] for file_info in self.pdf_files]

        except Exception as e:
            self.logger.error(f"扫描PDF文件失败: {e}")
            raise PDFExtractorError(f"扫描PDF文件失败: {e}")

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息字典
        """
        stat = file_path.stat()

        return {
            'path': str(file_path),
            'filename': file_path.name,
            'stem': file_path.stem,
            'extension': file_path.suffix,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'is_readable': os.access(file_path, os.R_OK)
        }

    def _filter_file(self, file_info: Dict[str, Any]) -> bool:
        """过滤文件

        Args:
            file_info: 文件信息字典

        Returns:
            bool: 是否通过过滤
        """
        # 检查文件大小
        if self.min_size and file_info['size'] < self.min_size:
            self.logger.debug(f"文件过小，跳过: {file_info['filename']}")
            return False

        if self.max_size and file_info['size'] > self.max_size:
            self.logger.debug(f"文件过大，跳过: {file_info['filename']}")
            return False

        # 检查文件可读性
        if not file_info['is_readable']:
            self.logger.warning(f"文件不可读，跳过: {file_info['filename']}")
            return False

        return True

    def get_file_list(self) -> List[Dict[str, Any]]:
        """获取PDF文件列表

        Returns:
            List[Dict[str, Any]]: PDF文件信息列表
        """
        return self.pdf_files

    def get_file_count(self) -> int:
        """获取PDF文件数量

        Returns:
            int: PDF文件数量
        """
        return len(self.pdf_files)

    def get_total_size(self) -> int:
        """获取PDF文件总大小

        Returns:
            int: PDF文件总大小（字节）
        """
        return sum(file_info['size'] for file_info in self.pdf_files)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        if not self.pdf_files:
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_mb': 0,
                'avg_size': 0,
                'min_size': 0,
                'max_size': 0
            }

        sizes = [file_info['size'] for file_info in self.pdf_files]
        total_size = sum(sizes)

        return {
            'total_files': len(self.pdf_files),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'avg_size': total_size / len(self.pdf_files),
            'min_size': min(sizes),
            'max_size': max(sizes)
        }

    def filter_by_keywords(
        self,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[str]:
        """按关键词过滤PDF文件

        Args:
            keywords: 关键词列表
            case_sensitive: 是否区分大小写

        Returns:
            List[str]: 匹配的PDF文件路径列表
        """
        matched_files = []

        for file_info in self.pdf_files:
            filename = file_info['filename']
            if not case_sensitive:
                filename = filename.lower()

            for keyword in keywords:
                search_keyword = keyword if case_sensitive else keyword.lower()
                if search_keyword in filename:
                    matched_files.append(file_info['path'])
                    break

        self.logger.info(f"关键词过滤完成，匹配 {len(matched_files)} 个文件")
        return matched_files

    def filter_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_field: str = 'modified_time'
    ) -> List[str]:
        """按日期范围过滤PDF文件

        Args:
            start_date: 开始日期
            end_date: 结束日期
            date_field: 日期字段（'created_time' 或 'modified_time'）

        Returns:
            List[str]: 匹配的PDF文件路径列表
        """
        matched_files = []

        for file_info in self.pdf_files:
            file_date = file_info[date_field]

            if start_date and file_date < start_date:
                continue

            if end_date and file_date > end_date:
                continue

            matched_files.append(file_info['path'])

        self.logger.info(f"日期范围过滤完成，匹配 {len(matched_files)} 个文件")
        return matched_files

    def group_by_year(self) -> Dict[int, List[str]]:
        """按年份分组PDF文件

        Returns:
            Dict[int, List[str]]: 年份到文件路径列表的映射
        """
        groups: Dict[int, List[str]] = {}

        for file_info in self.pdf_files:
            year = file_info['modified_time'].year
            if year not in groups:
                groups[year] = []
            groups[year].append(file_info['path'])

        self.logger.info(f"按年份分组完成，共 {len(groups)} 个年份")
        return groups

    def print_summary(self) -> None:
        """打印摘要信息"""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("PDF文件提取摘要")
        print("=" * 60)
        print(f"源文件夹: {self.source_folder}")
        print(f"PDF文件数量: {stats['total_files']}")
        print(f"总大小: {stats['total_size_mb']:.2f} MB")
        print(f"平均大小: {stats['avg_size'] / (1024 * 1024):.2f} MB")
        print(f"最小文件: {stats['min_size'] / (1024 * 1024):.2f} MB")
        print(f"最大文件: {stats['max_size'] / (1024 * 1024):.2f} MB")
        print("=" * 60 + "\n")


def extract_pdf_files(
    source_folder: Union[str, Path],
    recursive: bool = True
) -> List[str]:
    """提取PDF文件（便捷函数）

    Args:
        source_folder: 源文件夹路径
        recursive: 是否递归扫描子文件夹

    Returns:
        List[str]: PDF文件路径列表
    """
    extractor = PDFExtractor(source_folder, recursive=recursive)
    return extractor.extract_pdf_files()
