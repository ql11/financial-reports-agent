"""
验证工具函数
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def validate_pdf_file(filepath: str) -> Dict[str, Any]:
    """验证PDF文件
    
    Args:
        filepath: PDF文件路径
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "file_info": {}
    }
    
    try:
        path = Path(filepath)
        
        # 检查文件是否存在
        if not path.exists():
            result["errors"].append(f"文件不存在: {filepath}")
            return result
        
        # 检查文件扩展名
        if path.suffix.lower() != ".pdf":
            result["errors"].append(f"文件不是PDF格式: {filepath}")
            return result
        
        # 检查文件大小
        file_size = path.stat().st_size
        result["file_info"]["size_bytes"] = file_size
        result["file_info"]["size_mb"] = file_size / (1024 * 1024)
        
        if file_size == 0:
            result["errors"].append("文件大小为0")
            return result
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            result["warnings"].append("文件大小超过100MB，可能影响处理速度")
        
        # 检查文件是否可读
        try:
            with open(path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    result["errors"].append("文件不是有效的PDF格式")
                    return result
        except Exception as e:
            result["errors"].append(f"无法读取文件: {e}")
            return result
        
        result["valid"] = True
        result["file_info"]["path"] = str(path.absolute())
        result["file_info"]["name"] = path.name
        
        logger.info(f"PDF文件验证通过: {filepath}")
        
    except Exception as e:
        result["errors"].append(f"验证PDF文件时出错: {e}")
        logger.error(f"验证PDF文件失败: {e}")
    
    return result


def validate_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证财务数据
    
    Args:
        data: 财务数据
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "missing_fields": []
    }
    
    required_fields = [
        "company_name",
        "report_year",
        "operating_revenue",
        "net_profit",
        "total_assets",
        "total_liabilities",
        "total_equity"
    ]
    
    # 检查必填字段
    for field in required_fields:
        if field not in data or data[field] is None:
            result["missing_fields"].append(field)
    
    if result["missing_fields"]:
        result["errors"].append(f"缺少必填字段: {', '.join(result['missing_fields'])}")
        return result
    
    # 验证数值范围
    numeric_fields = [
        "operating_revenue",
        "net_profit",
        "total_assets",
        "total_liabilities",
        "total_equity"
    ]
    
    for field in numeric_fields:
        value = data.get(field)
        if value is not None:
            if not isinstance(value, (int, float)):
                result["errors"].append(f"字段 {field} 不是数值类型: {type(value)}")
            elif value < 0:
                result["warnings"].append(f"字段 {field} 为负值: {value}")
            elif value == 0:
                result["warnings"].append(f"字段 {field} 为零值")
    
    # 验证逻辑关系
    if "total_assets" in data and "total_liabilities" in data and "total_equity" in data:
        total_assets = data["total_assets"]
        total_liabilities = data["total_liabilities"]
        total_equity = data["total_equity"]
        
        # 检查资产 = 负债 + 所有者权益
        if abs(total_assets - (total_liabilities + total_equity)) > 0.01 * total_assets:
            result["warnings"].append("资产不等于负债加所有者权益，可能存在数据错误")
    
    # 验证增长率合理性
    if "revenue_growth" in data:
        growth = data["revenue_growth"]
        if abs(growth) > 1000:  # 增长率超过1000%
            result["warnings"].append(f"营业收入增长率异常: {growth}%")
    
    if "profit_growth" in data:
        growth = data["profit_growth"]
        if abs(growth) > 1000:  # 增长率超过1000%
            result["warnings"].append(f"净利润增长率异常: {growth}%")
    
    # 验证比率合理性
    if "gross_margin" in data:
        margin = data["gross_margin"]
        if margin < -100 or margin > 100:
            result["errors"].append(f"毛利率超出合理范围: {margin}%")
        elif margin < 0:
            result["warnings"].append(f"毛利率为负: {margin}%")
    
    if "debt_ratio" in data:
        ratio = data["debt_ratio"]
        if ratio < 0 or ratio > 100:
            result["errors"].append(f"资产负债率超出合理范围: {ratio}%")
        elif ratio > 90:
            result["warnings"].append(f"资产负债率过高: {ratio}%")
    
    if not result["errors"]:
        result["valid"] = True
    
    logger.info(f"财务数据验证完成: 有效={result['valid']}, 错误={len(result['errors'])}, 警告={len(result['warnings'])}")
    
    return result


def validate_company_name(name: str) -> bool:
    """验证公司名称
    
    Args:
        name: 公司名称
        
    Returns:
        bool: 是否有效
    """
    if not name or not name.strip():
        return False
    
    # 检查长度
    if len(name) < 2 or len(name) > 100:
        return False
    
    # 检查是否包含非法字符
    if re.search(r'[<>:"/\\|?*]', name):
        return False
    
    # 检查是否包含常见公司后缀
    valid_suffixes = ["公司", "有限公司", "股份有限公司", "集团", "企业", "厂", "店"]
    if not any(suffix in name for suffix in valid_suffixes):
        logger.warning(f"公司名称可能不完整: {name}")
    
    return True


def validate_stock_code(code: str) -> bool:
    """验证股票代码
    
    Args:
        code: 股票代码
        
    Returns:
        bool: 是否有效
    """
    if not code or not code.strip():
        return False
    
    # 移除空格和特殊字符
    code = code.strip()
    
    # 检查长度（A股通常6位）
    if len(code) != 6:
        return False
    
    # 检查是否全数字
    if not code.isdigit():
        return False
    
    # 检查交易所代码（沪市6开头，深市0或3开头）
    first_digit = code[0]
    if first_digit not in ['0', '3', '6']:
        return False
    
    return True


def validate_report_year(year: int) -> bool:
    """验证报告年度
    
    Args:
        year: 报告年度
        
    Returns:
        bool: 是否有效
    """
    current_year = 2025  # 假设当前年份
    
    # 检查范围（假设有效年份为2000-当前年份）
    if year < 2000 or year > current_year:
        return False
    
    return True


def validate_audit_opinion(opinion: str) -> bool:
    """验证审计意见
    
    Args:
        opinion: 审计意见
        
    Returns:
        bool: 是否有效
    """
    if not opinion or not opinion.strip():
        return False
    
    valid_opinions = [
        "标准无保留意见",
        "无保留意见",
        "保留意见",
        "否定意见",
        "无法表示意见",
        "带强调事项段的无保留意见",
        "带其他事项段的无保留意见"
    ]
    
    # 检查是否包含有效意见
    for valid in valid_opinions:
        if valid in opinion:
            return True
    
    logger.warning(f"审计意见可能不规范: {opinion}")
    return True  # 即使不规范也返回True，只记录警告


def validate_financial_ratios(ratios: Dict[str, float]) -> Dict[str, Any]:
    """验证财务比率
    
    Args:
        ratios: 财务比率字典
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # 定义合理范围
    valid_ranges = {
        "gross_margin": (-10, 100),  # 毛利率
        "net_margin": (-50, 50),      # 净利率
        "roe": (-100, 100),           # 净资产收益率
        "roa": (-50, 50),             # 总资产收益率
        "debt_ratio": (0, 100),       # 资产负债率
        "current_ratio": (0, 10),     # 流动比率
        "quick_ratio": (0, 10),       # 速动比率
        "inventory_turnover": (0, 100),  # 存货周转率
        "receivables_turnover": (0, 100),  # 应收账款周转率
        "total_asset_turnover": (0, 10)  # 总资产周转率
    }
    
    for ratio_name, value in ratios.items():
        if ratio_name in valid_ranges:
            min_val, max_val = valid_ranges[ratio_name]
            
            if value < min_val or value > max_val:
                result["warnings"].append(f"比率 {ratio_name} 超出合理范围: {value}")
            
            # 特定比率的额外检查
            if ratio_name == "debt_ratio" and value > 80:
                result["warnings"].append(f"资产负债率过高: {value}%")
            
            if ratio_name == "current_ratio" and value < 1:
                result["warnings"].append(f"流动比率过低: {value}")
            
            if ratio_name == "quick_ratio" and value < 0.5:
                result["warnings"].append(f"速动比率过低: {value}")
    
    if result["warnings"]:
        logger.warning(f"财务比率验证警告: {len(result['warnings'])} 个警告")
    
    return result