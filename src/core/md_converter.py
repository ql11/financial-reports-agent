"""
Markdown转换器模块

该模块负责使用Pandoc将PDF文件转换为Markdown格式。

功能特性：
- 使用Pandoc进行PDF到Markdown的转换
- 支持配置Pandoc参数
- 支持图片提取
- 支持批量转换
- 提供转换质量检查
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
import logging
import shutil

from src.utils.logger import get_logger


class MDConverterError(Exception):
    """Markdown转换器基础异常"""
    pass


class PandocNotFoundError(MDConverterError):
    """Pandoc未找到异常"""
    pass


class PDFParseError(MDConverterError):
    """PDF解析异常"""
    pass


class FileWriteError(MDConverterError):
    """文件写入异常"""
    pass


class MDConverter:
    """Markdown转换器

    负责使用Pandoc将PDF文件转换为Markdown格式。

    Attributes:
        pandoc_path: Pandoc可执行文件路径
        output_folder: 输出文件夹路径
        logger: 日志器
        pandoc_options: Pandoc转换参数
    """

    def __init__(
        self,
        pandoc_path: Union[str, Path] = "pandoc",
        output_folder: Optional[Union[str, Path]] = None,
        extract_media: bool = False,
        media_dir: Optional[str] = None,
        wrap: str = "none",
        markdown_headings: str = "atx"
    ):
        """初始化Markdown转换器

        Args:
            pandoc_path: Pandoc可执行文件路径
            output_folder: 输出文件夹路径
            extract_media: 是否提取图片
            media_dir: 图片提取目录（相对于输出文件夹）
            wrap: 换行设置（"none", "auto", "preserve"）
            markdown_headings: 标题风格（"atx" 或 "setext"）

        Raises:
            PandocNotFoundError: Pandoc未找到时抛出
        """
        self.pandoc_path = Path(pandoc_path)
        self.output_folder = Path(output_folder) if output_folder else None
        self.extract_media = extract_media
        self.media_dir = media_dir or "media"
        self.wrap = wrap
        self.markdown_headings = markdown_headings
        self.logger = get_logger('financial_analysis')

        # 验证Pandoc是否可用
        self._verify_pandoc()

        # 创建输出文件夹
        if self.output_folder:
            self.output_folder.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Markdown转换器初始化完成，Pandoc路径: {self.pandoc_path}")

    def _verify_pandoc(self) -> None:
        """验证Pandoc是否可用

        Raises:
            PandocNotFoundError: Pandoc未找到时抛出
        """
        # 检查Pandoc是否存在
        if not shutil.which(str(self.pandoc_path)):
            # 尝试直接执行
            try:
                result = subprocess.run(
                    [str(self.pandoc_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    raise PandocNotFoundError(f"Pandoc执行失败: {self.pandoc_path}")
            except FileNotFoundError:
                raise PandocNotFoundError(f"Pandoc未找到: {self.pandoc_path}")
            except subprocess.TimeoutExpired:
                raise PandocNotFoundError(f"Pandoc执行超时: {self.pandoc_path}")
            except Exception as e:
                raise PandocNotFoundError(f"Pandoc验证失败: {e}")

        self.logger.debug(f"Pandoc验证通过: {self.pandoc_path}")

    def convert_pdf_to_markdown(
        self,
        pdf_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> str:
        """将PDF文件转换为Markdown格式

        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径，None则自动生成
            **kwargs: 其他转换参数

        Returns:
            str: Markdown文件路径

        Raises:
            PDFParseError: PDF解析失败时抛出
            FileWriteError: 文件写入失败时抛出
        """
        pdf_path = Path(pdf_path)

        self.logger.info(f"开始转换PDF文件: {pdf_path.name}")

        # 验证PDF文件
        if not pdf_path.exists():
            raise PDFParseError(f"PDF文件不存在: {pdf_path}")

        if not pdf_path.suffix.lower() == '.pdf':
            raise PDFParseError(f"文件不是PDF格式: {pdf_path}")

        # 确定输出路径
        if output_path is None:
            if self.output_folder is None:
                output_path = pdf_path.with_suffix('.md')
            else:
                output_path = self.output_folder / (pdf_path.stem + '.md')
        else:
            output_path = Path(output_path)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 构建Pandoc命令
        cmd = self._build_pandoc_command(pdf_path, output_path, **kwargs)

        try:
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get('timeout', 120)
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"Pandoc转换失败: {error_msg}")
                raise PDFParseError(f"PDF转换失败: {error_msg}")

            # 检查输出文件
            if not output_path.exists():
                raise FileWriteError(f"输出文件未生成: {output_path}")

            # 清理和格式化Markdown内容
            self._clean_markdown(output_path)

            self.logger.info(f"PDF转换成功: {output_path.name}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            self.logger.error(f"PDF转换超时: {pdf_path.name}")
            raise PDFParseError(f"PDF转换超时: {pdf_path.name}")
        except Exception as e:
            if isinstance(e, (PDFParseError, FileWriteError)):
                raise
            self.logger.error(f"PDF转换异常: {e}")
            raise PDFParseError(f"PDF转换异常: {e}")

    def _build_pandoc_command(
        self,
        pdf_path: Path,
        output_path: Path,
        **kwargs
    ) -> List[str]:
        """构建Pandoc命令

        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径
            **kwargs: 其他参数

        Returns:
            List[str]: Pandoc命令参数列表
        """
        cmd = [str(self.pandoc_path)]

        # 输入文件
        cmd.append(str(pdf_path))

        # 输入格式
        cmd.extend(['-f', kwargs.get('from_format', 'pdf')])

        # 输出格式
        cmd.extend(['-t', kwargs.get('to_format', 'markdown')])

        # 输出文件
        cmd.extend(['-o', str(output_path)])

        # 换行设置
        if self.wrap:
            cmd.extend(['--wrap', self.wrap])

        # 标题风格
        if self.markdown_headings:
            cmd.extend(['--markdown-headings', self.markdown_headings])

        # 提取图片
        if self.extract_media:
            media_path = output_path.parent / self.media_dir
            cmd.extend([f'--extract-media={str(media_path)}'])

        # 其他参数
        if kwargs.get('extra_args'):
            cmd.extend(kwargs['extra_args'])

        self.logger.debug(f"Pandoc命令: {' '.join(cmd)}")
        return cmd

    def _clean_markdown(self, md_path: Path) -> None:
        """清理和格式化Markdown文件

        Args:
            md_path: Markdown文件路径
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除多余的空行
            lines = content.split('\n')
            cleaned_lines = []
            prev_empty = False

            for line in lines:
                is_empty = line.strip() == ''

                # 最多保留一个空行
                if is_empty:
                    if not prev_empty:
                        cleaned_lines.append(line)
                    prev_empty = True
                else:
                    cleaned_lines.append(line)
                    prev_empty = False

            # 写回文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cleaned_lines))

            self.logger.debug(f"Markdown文件清理完成: {md_path.name}")

        except Exception as e:
            self.logger.warning(f"Markdown文件清理失败: {e}")

    def batch_convert(
        self,
        pdf_files: List[Union[str, Path]],
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """批量转换PDF文件

        Args:
            pdf_files: PDF文件路径列表
            continue_on_error: 出错时是否继续

        Returns:
            Dict[str, Any]: 转换结果统计
        """
        self.logger.info(f"开始批量转换，共 {len(pdf_files)} 个文件")

        results = {
            'total': len(pdf_files),
            'success': 0,
            'failed': 0,
            'success_files': [],
            'failed_files': [],
            'errors': []
        }

        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                self.logger.info(f"转换进度: {i}/{len(pdf_files)} - {Path(pdf_file).name}")
                md_file = self.convert_pdf_to_markdown(pdf_file)
                results['success'] += 1
                results['success_files'].append(md_file)

            except Exception as e:
                results['failed'] += 1
                results['failed_files'].append(str(pdf_file))
                results['errors'].append({
                    'file': str(pdf_file),
                    'error': str(e)
                })

                self.logger.error(f"转换失败: {Path(pdf_file).name}, 错误: {e}")

                if not continue_on_error:
                    break

        self.logger.info(
            f"批量转换完成，成功: {results['success']}, 失败: {results['failed']}"
        )

        return results

    def get_conversion_info(
        self,
        pdf_path: Union[str, Path],
        md_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """获取转换信息

        Args:
            pdf_path: PDF文件路径
            md_path: Markdown文件路径

        Returns:
            Dict[str, Any]: 转换信息字典
        """
        pdf_path = Path(pdf_path)
        md_path = Path(md_path)

        pdf_stat = pdf_path.stat()
        md_stat = md_path.stat()

        return {
            'pdf_path': str(pdf_path),
            'md_path': str(md_path),
            'pdf_size': pdf_stat.st_size,
            'md_size': md_stat.st_size,
            'conversion_time': datetime.fromtimestamp(md_stat.st_mtime),
            'compression_ratio': md_stat.st_size / pdf_stat.st_size if pdf_stat.st_size > 0 else 0
        }


def convert_pdf_to_markdown(
    pdf_path: Union[str, Path],
    output_folder: Optional[Union[str, Path]] = None,
    pandoc_path: Union[str, Path] = "pandoc"
) -> str:
    """转换PDF为Markdown（便捷函数）

    Args:
        pdf_path: PDF文件路径
        output_folder: 输出文件夹路径
        pandoc_path: Pandoc可执行文件路径

    Returns:
        str: Markdown文件路径
    """
    converter = MDConverter(pandoc_path=pandoc_path, output_folder=output_folder)
    return converter.convert_pdf_to_markdown(pdf_path)
