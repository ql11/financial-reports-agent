"""
PDF表格提取器模块

该模块负责直接从PDF文件中提取表格数据，无需转换为Markdown。

功能特性：
- 使用pdfplumber提取PDF表格
- 支持多页表格提取和合并
- 智能识别财务报表表格
- 表格数据清洗和验证
- 支持批量处理
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import logging
import pdfplumber
import pandas as pd

from src.utils.logger import get_logger


class PDFTableExtractorError(Exception):
    """PDF表格提取器基础异常"""
    pass


class PDFFileNotFoundError(PDFTableExtractorError):
    """PDF文件不存在异常"""
    pass


class PDFParseError(PDFTableExtractorError):
    """PDF解析异常"""
    pass


class TableExtractionError(PDFTableExtractorError):
    """表格提取异常"""
    pass


class PDFTableExtractor:
    """PDF表格提取器

    负责直接从PDF文件中提取表格数据。

    Attributes:
        logger: 日志器
        pdf_path: PDF文件路径
        pdf: pdfplumber.PDF对象
    """

    def __init__(self, pdf_path: Union[str, Path]):
        """初始化PDF表格提取器

        Args:
            pdf_path: PDF文件路径

        Raises:
            PDFFileNotFoundError: PDF文件不存在时抛出
            PDFParseError: PDF解析失败时抛出
        """
        self.pdf_path = Path(pdf_path)
        self.logger = get_logger('financial_analysis')
        self.pdf: Optional[pdfplumber.PDF] = None

        # 验证PDF文件
        if not self.pdf_path.exists():
            raise PDFFileNotFoundError(f"PDF文件不存在: {self.pdf_path}")

        if not self.pdf_path.suffix.lower() == '.pdf':
            raise PDFParseError(f"文件不是PDF格式: {self.pdf_path}")

        # 打开PDF文件
        try:
            self.pdf = pdfplumber.open(self.pdf_path)
            self.logger.info(f"成功打开PDF文件: {self.pdf_path.name}, 共 {len(self.pdf.pages)} 页")
        except Exception as e:
            self.logger.error(f"打开PDF文件失败: {e}")
            raise PDFParseError(f"打开PDF文件失败: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def close(self) -> None:
        """关闭PDF文件"""
        if self.pdf:
            self.pdf.close()
            self.pdf = None

    def extract_all_tables(
        self,
        pages: Optional[List[int]] = None,
        min_rows: int = 2,
        min_cols: int = 2
    ) -> List[Dict[str, Any]]:
        """提取所有表格

        Args:
            pages: 页码列表（从0开始），None表示提取所有页
            min_rows: 最小行数
            min_cols: 最小列数

        Returns:
            List[Dict[str, Any]]: 表格列表，每个表格包含数据和元数据

        Raises:
            TableExtractionError: 表格提取失败时抛出
        """
        if not self.pdf:
            raise PDFParseError("PDF文件未打开")

        self.logger.info(f"开始提取表格，页码: {pages or '全部'}")

        all_tables = []
        target_pages = pages if pages else range(len(self.pdf.pages))

        for page_num in target_pages:
            if page_num >= len(self.pdf.pages):
                self.logger.warning(f"页码 {page_num} 超出范围，跳过")
                continue

            try:
                page_tables = self._extract_tables_from_page(
                    page_num,
                    min_rows=min_rows,
                    min_cols=min_cols
                )
                all_tables.extend(page_tables)

            except Exception as e:
                self.logger.error(f"提取第 {page_num} 页表格失败: {e}")
                continue

        self.logger.info(f"表格提取完成，共提取 {len(all_tables)} 个表格")
        return all_tables

    def _extract_tables_from_page(
        self,
        page_num: int,
        min_rows: int,
        min_cols: int
    ) -> List[Dict[str, Any]]:
        """从单页提取表格

        Args:
            page_num: 页码
            min_rows: 最小行数
            min_cols: 最小列数

        Returns:
            List[Dict[str, Any]]: 表格列表
        """
        page = self.pdf.pages[page_num]
        tables = []

        # 使用pdfplumber提取表格
        extracted_tables = page.extract_tables()

        for table_idx, table_data in enumerate(extracted_tables):
            if not table_data:
                continue

            # 过滤太小的表格
            if len(table_data) < min_rows or len(table_data[0]) < min_cols:
                continue

            # 清理表格数据
            cleaned_data = self._clean_table_data(table_data)

            # 转换为DataFrame
            df = self._dataframe_from_table(cleaned_data)

            if df is not None and not df.empty:
                tables.append({
                    'page': page_num,
                    'table_index': table_idx,
                    'data': df,
                    'raw_data': cleaned_data,
                    'shape': df.shape,
                    'extraction_time': datetime.now()
                })

        self.logger.debug(f"第 {page_num} 页提取到 {len(tables)} 个表格")
        return tables

    def _clean_table_data(self, table_data: List[List[str]]) -> List[List[str]]:
        """清理表格数据

        Args:
            table_data: 原始表格数据

        Returns:
            List[List[str]]: 清理后的表格数据
        """
        cleaned = []
        for row in table_data:
            if row is None:
                continue

            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_row.append('')
                else:
                    # 清理空白字符
                    cell_str = str(cell).strip()
                    # 移除多余的空格和换行
                    cell_str = ' '.join(cell_str.split())
                    cleaned_row.append(cell_str)

            # 跳过全空行
            if any(cell for cell in cleaned_row):
                cleaned.append(cleaned_row)

        return cleaned

    def _dataframe_from_table(self, table_data: List[List[str]]) -> Optional[pd.DataFrame]:
        """从表格数据创建DataFrame

        Args:
            table_data: 表格数据

        Returns:
            Optional[pd.DataFrame]: DataFrame对象
        """
        if not table_data or len(table_data) < 2:
            return None

        try:
            # 第一行作为列名
            headers = table_data[0]
            data = table_data[1:]

            # 创建DataFrame
            df = pd.DataFrame(data, columns=headers)

            # 移除全空的列
            df = df.dropna(axis=1, how='all')

            # 移除全空的行
            df = df.dropna(axis=0, how='all')

            return df

        except Exception as e:
            self.logger.warning(f"创建DataFrame失败: {e}")
            return None

    def find_financial_tables(
        self,
        keywords: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """查找财务报表表格

        Args:
            keywords: 关键词列表，用于识别财务报表

        Returns:
            Dict[str, List[Dict[str, Any]]]: 分类后的财务报表表格
        """
        if keywords is None:
            keywords = [
                '资产负债表', '资产', '负债', '所有者权益',
                '利润表', '损益表', '收入', '成本', '利润',
                '现金流量表', '现金流', '经营活动', '投资活动', '筹资活动'
            ]

        all_tables = self.extract_all_tables()
        classified = {
            'balance_sheet': [],
            'income_statement': [],
            'cash_flow_statement': [],
            'other': []
        }

        for table_info in all_tables:
            df = table_info['data']

            # 检查表格内容是否包含关键词
            table_text = ' '.join(str(col) for col in df.columns)
            for _, row in df.iterrows():
                table_text += ' ' + ' '.join(str(val) for val in row.values)

            # 分类
            if any(kw in table_text for kw in ['资产负债表', '资产', '负债', '所有者权益']):
                classified['balance_sheet'].append(table_info)
            elif any(kw in table_text for kw in ['利润表', '损益表', '收入', '成本', '利润']):
                classified['income_statement'].append(table_info)
            elif any(kw in table_text for kw in ['现金流量表', '现金流', '经营', '投资', '筹资']):
                classified['cash_flow_statement'].append(table_info)
            else:
                classified['other'].append(table_info)

        self.logger.info(
            f"财务报表分类完成: "
            f"资产负债表 {len(classified['balance_sheet'])} 个, "
            f"利润表 {len(classified['income_statement'])} 个, "
            f"现金流量表 {len(classified['cash_flow_statement'])} 个"
        )

        return classified

    def extract_table_to_excel(
        self,
        output_path: Union[str, Path],
        pages: Optional[List[int]] = None
    ) -> str:
        """提取表格并保存到Excel

        Args:
            output_path: 输出Excel文件路径
            pages: 页码列表

        Returns:
            str: Excel文件路径
        """
        output_path = Path(output_path)
        all_tables = self.extract_all_tables(pages=pages)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, table_info in enumerate(all_tables):
                sheet_name = f"Page{table_info['page']}_Table{table_info['table_index']}"
                df = table_info['data']
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        self.logger.info(f"表格已保存到Excel: {output_path}")
        return str(output_path)

    def get_page_count(self) -> int:
        """获取PDF页数

        Returns:
            int: 页数
        """
        return len(self.pdf.pages) if self.pdf else 0

    def get_file_info(self) -> Dict[str, Any]:
        """获取PDF文件信息

        Returns:
            Dict[str, Any]: 文件信息
        """
        stat = self.pdf_path.stat()

        return {
            'path': str(self.pdf_path),
            'filename': self.pdf_path.name,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'pages': self.get_page_count(),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime)
        }


def extract_pdf_tables(
    pdf_path: Union[str, Path],
    output_excel: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """提取PDF表格（便捷函数）

    Args:
        pdf_path: PDF文件路径
        output_excel: 输出Excel文件路径

    Returns:
        List[Dict[str, Any]]: 表格列表
    """
    with PDFTableExtractor(pdf_path) as extractor:
        tables = extractor.extract_all_tables()

        if output_excel:
            extractor.extract_table_to_excel(output_excel)

        return tables
