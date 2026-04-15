#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试工具模块
"""

import pytest
from pathlib import Path
from src.utils.config_loader import ConfigLoader
from src.utils.file_manager import FileManager
from src.utils.validator import DataValidator


class TestConfigLoader:
    """测试配置加载器"""
    
    def test_load_config(self, config):
        """测试加载配置文件"""
        assert config is not None
    
    def test_get_folder_config(self, config):
        """测试获取文件夹配置"""
        source = config.get('folders.source')
        reports = config.get('folders.reports')
        
        assert source is not None
        assert reports is not None
    
    def test_get_analysis_config(self, config):
        """测试获取分析配置"""
        profitability = config.get('analysis.profitability')
        solvency = config.get('analysis.solvency')
        
        # 分析维度配置应该存在
        assert profitability is not None or solvency is not None
    
    def test_get_nonexistent_key(self, config):
        """测试获取不存在的配置项"""
        value = config.get('nonexistent.key', 'default_value')
        assert value == 'default_value'
    
    def test_config_caching(self, config):
        """测试配置缓存"""
        # 多次获取同一配置项应该返回相同值
        value1 = config.get('folders.source')
        value2 = config.get('folders.source')
        assert value1 == value2


class TestFileManager:
    """测试文件管理器"""
    
    def test_create_file_manager(self):
        """测试创建文件管理器"""
        fm = FileManager()
        assert fm is not None
    
    def test_create_directory(self, tmp_path):
        """测试创建目录"""
        fm = FileManager()
        test_dir = tmp_path / "test_dir"
        
        fm.create_directory(str(test_dir))
        assert test_dir.exists()
    
    def test_write_and_read_file(self, tmp_path):
        """测试写入和读取文件"""
        fm = FileManager()
        test_file = tmp_path / "test.txt"
        test_content = "测试内容"
        
        # 写入文件
        fm.write_file(str(test_file), test_content)
        assert test_file.exists()
        
        # 读取文件
        content = fm.read_file(str(test_file))
        assert content == test_content
    
    def test_file_exists(self, tmp_path):
        """测试文件存在检查"""
        fm = FileManager()
        test_file = tmp_path / "test.txt"
        
        # 文件不存在
        assert not fm.file_exists(str(test_file))
        
        # 创建文件
        test_file.write_text("test")
        assert fm.file_exists(str(test_file))
    
    def test_list_files(self, tmp_path):
        """测试列出文件"""
        fm = FileManager()
        
        # 创建一些测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.pdf").write_text("content3")
        
        # 列出所有txt文件
        txt_files = fm.list_files(str(tmp_path), pattern="*.txt")
        assert len(txt_files) == 2
        
        # 列出所有pdf文件
        pdf_files = fm.list_files(str(tmp_path), pattern="*.pdf")
        assert len(pdf_files) == 1


class TestDataValidator:
    """测试数据验证器"""
    
    def test_create_validator(self):
        """测试创建验证器"""
        validator = DataValidator()
        assert validator is not None
    
    def test_validate_positive_number(self):
        """测试验证正数"""
        validator = DataValidator()
        
        assert validator.validate_positive(100.0) == True
        assert validator.validate_positive(0.0) == False
        assert validator.validate_positive(-10.0) == False
    
    def test_validate_percentage(self):
        """测试验证百分比"""
        validator = DataValidator()
        
        assert validator.validate_percentage(0.5) == True  # 50%
        assert validator.validate_percentage(1.0) == True  # 100%
        assert validator.validate_percentage(1.5) == False  # 150% 超过100%
        assert validator.validate_percentage(-0.1) == False  # 负数
    
    def test_validate_financial_data(self, sample_financial_data):
        """测试验证财务数据"""
        validator = DataValidator()
        
        result = validator.validate_financial_data(sample_financial_data)
        assert result == True
    
    def test_validate_balance_sheet(self, sample_balance_sheet):
        """测试验证资产负债表"""
        validator = DataValidator()
        
        result = validator.validate_balance_sheet(sample_balance_sheet)
        assert result == True
    
    def test_validate_income_statement(self, sample_income_statement):
        """测试验证利润表"""
        validator = DataValidator()
        
        result = validator.validate_income_statement(sample_income_statement)
        assert result == True
    
    def test_validate_cash_flow(self, sample_cash_flow):
        """测试验证现金流量表"""
        validator = DataValidator()
        
        result = validator.validate_cash_flow_statement(sample_cash_flow)
        assert result == True


class TestLogger:
    """测试日志工具"""
    
    def test_get_logger(self):
        """测试获取日志器"""
        from src.utils.logger import get_logger
        
        logger = get_logger("test_module")
        assert logger is not None
    
    def test_logger_levels(self):
        """测试日志级别"""
        from src.utils.logger import get_logger
        
        logger = get_logger("test_module")
        
        # 应该能够记录不同级别的日志
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
