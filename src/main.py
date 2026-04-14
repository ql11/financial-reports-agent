#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财报分析系统主程序入口

Author: CodeArts Agent
Date: 2026-04-14
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.utils.file_manager import FileManager
from src.core.pdf_table_extractor import extract_tables_from_pdf
from src.core.data_extractor import extract_financial_data
from src.core.indicator_calculator import calculate_indicators
from src.core.trend_analyzer import analyze_trend
from src.core.risk_detector import detect_risks
from src.core.report_generator import generate_report


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='财报分析系统 - 自动化分析上市公司财务报告'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='配置文件路径 (默认: config/config.yaml)'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='源文件夹路径（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='输出文件夹路径（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='单个PDF文件路径（只分析指定文件）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    return parser.parse_args()


def analyze_single_pdf(
    pdf_path: str,
    output_dir: str,
    config: ConfigLoader
) -> bool:
    """
    分析单个PDF文件
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        config: 配置加载器
        
    Returns:
        是否成功
    """
    try:
        logger.info(f"开始分析文件: {pdf_path}")
        
        # 1. 从PDF提取财务数据
        logger.info("步骤1: 提取财务数据...")
        financial_data = extract_financial_data(pdf_path)
        
        if not financial_data:
            logger.error("财务数据提取失败")
            return False
        
        logger.info(f"成功提取财务数据: {financial_data.company_name} {financial_data.report_year}")
        
        # 2. 计算财务指标
        logger.info("步骤2: 计算财务指标...")
        indicators = calculate_indicators(financial_data)
        
        if not indicators:
            logger.error("财务指标计算失败")
            return False
        
        logger.info("成功计算财务指标")
        
        # 3. 趋势分析（如果有历史数据）
        trend_analysis = None
        if config.get('analysis.trend_analysis', True):
            logger.info("步骤3: 趋势分析...")
            # TODO: 加载历史数据进行趋势分析
            logger.info("趋势分析完成（暂无历史数据）")
        
        # 4. 风险识别
        logger.info("步骤4: 风险识别...")
        risk_list = detect_risks(indicators, trend_analysis)
        
        if not risk_list:
            logger.warning("风险识别失败")
        else:
            logger.info(f"识别到 {risk_list.total_risks} 个风险")
        
        # 5. 生成报告
        logger.info("步骤5: 生成分析报告...")
        report = generate_report(
            indicators=indicators,
            trend_analysis=trend_analysis,
            risk_list=risk_list
        )
        
        if not report:
            logger.error("报告生成失败")
            return False
        
        # 6. 保存报告
        file_manager = FileManager()
        company_name = financial_data.company_name or "Unknown"
        report_year = financial_data.report_year or "Unknown"
        report_filename = f"{company_name}_{report_year}_分析报告.md"
        report_path = Path(output_dir) / report_filename
        
        file_manager.write_file(str(report_path), report)
        logger.info(f"报告已保存: {report_path}")
        
        logger.info(f"✅ 文件分析完成: {pdf_path}")
        return True
        
    except Exception as e:
        logger.error(f"分析文件失败: {pdf_path}, 错误: {str(e)}")
        return False


def main() -> int:
    """
    主程序入口
    
    Returns:
        退出码（0表示成功，非0表示失败）
    """
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 设置日志级别
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info("=" * 60)
        logger.info("财报分析系统启动")
        logger.info("=" * 60)
        
        # 加载配置
        logger.info(f"加载配置文件: {args.config}")
        config = ConfigLoader(args.config)
        
        # 获取源文件夹和输出文件夹
        source_dir = args.source or config.get('folders.source', './source')
        output_dir = args.output or config.get('folders.reports', './reports')
        
        logger.info(f"源文件夹: {source_dir}")
        logger.info(f"输出文件夹: {output_dir}")
        
        # 创建文件管理器
        file_manager = FileManager()
        
        # 确保输出目录存在
        file_manager.create_directory(output_dir)
        
        # 分析文件
        success_count = 0
        fail_count = 0
        
        if args.file:
            # 分析单个文件
            if analyze_single_pdf(args.file, output_dir, config):
                success_count = 1
            else:
                fail_count = 1
        else:
            # 批量分析源文件夹中的所有PDF文件
            source_path = Path(source_dir)
            pdf_files = list(source_path.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"源文件夹中没有找到PDF文件: {source_dir}")
                return 0
            
            logger.info(f"找到 {len(pdf_files)} 个PDF文件")
            
            for i, pdf_file in enumerate(pdf_files, 1):
                logger.info(f"\n处理文件 [{i}/{len(pdf_files)}]: {pdf_file.name}")
                
                if analyze_single_pdf(str(pdf_file), output_dir, config):
                    success_count += 1
                else:
                    fail_count += 1
        
        # 输出统计信息
        logger.info("\n" + "=" * 60)
        logger.info("分析完成统计")
        logger.info("=" * 60)
        logger.info(f"成功: {success_count} 个文件")
        logger.info(f"失败: {fail_count} 个文件")
        logger.info(f"总计: {success_count + fail_count} 个文件")
        logger.info("=" * 60)
        
        return 0 if fail_count == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
