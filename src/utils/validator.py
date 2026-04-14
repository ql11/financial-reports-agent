"""
数据验证器模块

该模块对各类数据进行有效性验证，包括数值范围、日期格式、文件路径、财务数据逻辑等验证。

功能特性：
- 数值范围和类型验证
- 日期格式验证
- 文件路径验证
- 财务数据逻辑验证
- 批量验证支持
- 数据清洗功能
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Union, Optional, List, Dict, Tuple, Callable
import logging

# 设置模块日志
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证异常基类"""
    pass


class TypeValidationError(ValidationError):
    """类型验证异常"""
    pass


class RangeValidationError(ValidationError):
    """范围验证异常"""
    pass


class FormatValidationError(ValidationError):
    """格式验证异常"""
    pass


class LogicValidationError(ValidationError):
    """逻辑验证异常"""
    pass


class ValidationResult:
    """验证结果

    封装验证结果信息。

    Attributes:
        is_valid: 是否验证通过
        errors: 错误信息列表
        warnings: 警告信息列表
        cleaned_data: 清洗后的数据
    """

    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        cleaned_data: Any = None
    ):
        """初始化验证结果

        Args:
            is_valid: 是否验证通过
            errors: 错误信息列表
            warnings: 警告信息列表
            cleaned_data: 清洗后的数据
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.cleaned_data = cleaned_data

    def add_error(self, error: str) -> None:
        """添加错误信息

        Args:
            error: 错误信息
        """
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """添加警告信息

        Args:
            warning: 警告信息
        """
        self.warnings.append(warning)

    def merge(self, other: 'ValidationResult') -> None:
        """合并另一个验证结果

        Args:
            other: 另一个验证结果
        """
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def __bool__(self) -> bool:
        """支持布尔判断"""
        return self.is_valid

    def __repr__(self) -> str:
        """字符串表示"""
        status = "通过" if self.is_valid else "失败"
        return f"ValidationResult({status}, errors={len(self.errors)}, warnings={len(self.warnings)})"


class Validator:
    """数据验证器

    提供各类数据验证功能。

    Attributes:
        strict: 是否严格模式（严格模式下警告也视为错误）
    """

    def __init__(self, strict: bool = False):
        """初始化验证器

        Args:
            strict: 是否严格模式
        """
        self.strict = strict
        logger.info(f"验证器初始化完成，严格模式: {strict}")

    def validate_number(
        self,
        value: Any,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        allow_none: bool = False,
        field_name: str = "数值"
    ) -> ValidationResult:
        """验证数值

        Args:
            value: 待验证的值
            min_value: 最小值
            max_value: 最大值
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 检查类型
        if not isinstance(value, (int, float)):
            try:
                # 尝试转换为数值
                value = float(value)
                result.add_warning(f"{field_name}已从字符串转换为数值")
            except (ValueError, TypeError):
                result.add_error(
                    f"{field_name}类型错误：期望数值类型，实际类型为{type(value).__name__}"
                )
                return result

        # 检查范围
        if min_value is not None and value < min_value:
            result.add_error(
                f"{field_name}超出有效范围：{value}，最小值为{min_value}"
            )

        if max_value is not None and value > max_value:
            result.add_error(
                f"{field_name}超出有效范围：{value}，最大值为{max_value}"
            )

        result.cleaned_data = value
        return result

    def validate_date(
        self,
        value: Any,
        format_str: str = "%Y-%m-%d",
        allow_none: bool = False,
        field_name: str = "日期"
    ) -> ValidationResult:
        """验证日期

        Args:
            value: 待验证的值
            format_str: 日期格式字符串
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 如果已经是datetime对象
        if isinstance(value, datetime):
            result.cleaned_data = value
            return result

        # 尝试解析日期字符串
        try:
            parsed_date = datetime.strptime(str(value), format_str)
            result.cleaned_data = parsed_date
        except ValueError:
            result.add_error(
                f"{field_name}格式错误：{value}，期望格式为{format_str}"
            )

        return result

    def validate_path(
        self,
        value: Any,
        must_exist: bool = True,
        path_type: str = "any",
        allow_none: bool = False,
        field_name: str = "路径"
    ) -> ValidationResult:
        """验证文件路径

        Args:
            value: 待验证的值
            must_exist: 路径是否必须存在
            path_type: 路径类型（file, directory, any）
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 转换为Path对象
        try:
            path = Path(value)
        except Exception:
            result.add_error(f"{field_name}格式错误：{value}")
            return result

        # 检查路径是否存在
        if must_exist and not path.exists():
            result.add_error(f"{field_name}不存在：{value}")
            return result

        # 检查路径类型
        if path.exists():
            if path_type == "file" and not path.is_file():
                result.add_error(f"{field_name}不是文件：{value}")
            elif path_type == "directory" and not path.is_dir():
                result.add_error(f"{field_name}不是目录：{value}")

        result.cleaned_data = path
        return result

    def validate_string(
        self,
        value: Any,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allow_none: bool = False,
        field_name: str = "字符串"
    ) -> ValidationResult:
        """验证字符串

        Args:
            value: 待验证的值
            min_length: 最小长度
            max_length: 最大长度
            pattern: 正则表达式模式
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 转换为字符串
        str_value = str(value)

        # 检查长度
        if min_length is not None and len(str_value) < min_length:
            result.add_error(
                f"{field_name}长度不足：{len(str_value)}，最小长度为{min_length}"
            )

        if max_length is not None and len(str_value) > max_length:
            result.add_error(
                f"{field_name}长度超限：{len(str_value)}，最大长度为{max_length}"
            )

        # 检查正则表达式
        if pattern is not None:
            if not re.match(pattern, str_value):
                result.add_error(
                    f"{field_name}格式不匹配：{value}，期望模式为{pattern}"
                )

        result.cleaned_data = str_value
        return result

    def validate_financial_balance(
        self,
        assets: Union[int, float],
        liabilities: Union[int, float],
        equity: Union[int, float],
        tolerance: float = 0.01,
        field_name: str = "资产负债"
    ) -> ValidationResult:
        """验证财务数据平衡关系

        验证会计恒等式：资产 = 负债 + 所有者权益

        Args:
            assets: 资产总额
            liabilities: 负债总额
            equity: 所有者权益
            tolerance: 容差比例
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查数值有效性
        if not all(isinstance(v, (int, float)) for v in [assets, liabilities, equity]):
            result.add_error(f"{field_name}数据类型错误，必须为数值")
            return result

        # 计算平衡误差
        expected_assets = liabilities + equity
        if assets == 0:
            if expected_assets != 0:
                error_ratio = 1.0
            else:
                error_ratio = 0.0
        else:
            error_ratio = abs(assets - expected_assets) / abs(assets)

        # 检查平衡关系
        if error_ratio > tolerance:
            result.add_error(
                f"{field_name}不平衡：资产={assets}, "
                f"负债+权益={expected_assets}, "
                f"误差比例={error_ratio:.2%}"
            )
        elif error_ratio > 0:
            result.add_warning(
                f"{field_name}存在轻微误差：误差比例={error_ratio:.2%}"
            )

        result.cleaned_data = {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'is_balanced': error_ratio <= tolerance,
            'error_ratio': error_ratio
        }

        return result

    def validate_financial_ratio(
        self,
        numerator: Union[int, float],
        denominator: Union[int, float],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "财务比率"
    ) -> ValidationResult:
        """验证财务比率

        Args:
            numerator: 分子
            denominator: 分母
            min_value: 最小值
            max_value: 最大值
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查分母是否为0
        if denominator == 0:
            result.add_error(f"{field_name}计算错误：分母为0")
            return result

        # 计算比率
        ratio = numerator / denominator

        # 检查范围
        if min_value is not None and ratio < min_value:
            result.add_warning(
                f"{field_name}低于正常范围：{ratio:.4f}，最小值为{min_value}"
            )

        if max_value is not None and ratio > max_value:
            result.add_warning(
                f"{field_name}高于正常范围：{ratio:.4f}，最大值为{max_value}"
            )

        result.cleaned_data = ratio
        return result

    def validate_batch(
        self,
        data: Dict[str, Any],
        validators: Dict[str, Callable]
    ) -> ValidationResult:
        """批量验证

        Args:
            data: 待验证的数据字典
            validators: 验证器字典，键为字段名，值为验证函数

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        cleaned_data = {}

        for field_name, validator in validators.items():
            if field_name in data:
                field_result = validator(data[field_name])
                result.merge(field_result)
                if field_result.is_valid:
                    cleaned_data[field_name] = field_result.cleaned_data
            else:
                result.add_error(f"缺少必需字段：{field_name}")

        result.cleaned_data = cleaned_data
        return result

    def validate_list(
        self,
        value: Any,
        item_validator: Optional[Callable] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        allow_none: bool = False,
        field_name: str = "列表"
    ) -> ValidationResult:
        """验证列表

        Args:
            value: 待验证的值
            item_validator: 列表项验证函数
            min_length: 最小长度
            max_length: 最大长度
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 检查类型
        if not isinstance(value, (list, tuple)):
            result.add_error(
                f"{field_name}类型错误：期望列表类型，实际类型为{type(value).__name__}"
            )
            return result

        # 检查长度
        if min_length is not None and len(value) < min_length:
            result.add_error(
                f"{field_name}长度不足：{len(value)}，最小长度为{min_length}"
            )

        if max_length is not None and len(value) > max_length:
            result.add_error(
                f"{field_name}长度超限：{len(value)}，最大长度为{max_length}"
            )

        # 验证列表项
        cleaned_list = []
        if item_validator:
            for i, item in enumerate(value):
                item_result = item_validator(item)
                result.merge(item_result)
                if item_result.is_valid:
                    cleaned_list.append(item_result.cleaned_data)
                else:
                    # 为错误添加索引信息
                    for error in item_result.errors:
                        result.add_error(f"{field_name}[{i}]: {error}")
        else:
            cleaned_list = list(value)

        result.cleaned_data = cleaned_list
        return result

    def validate_dict(
        self,
        value: Any,
        key_validator: Optional[Callable] = None,
        value_validator: Optional[Callable] = None,
        required_keys: Optional[List[str]] = None,
        allow_none: bool = False,
        field_name: str = "字典"
    ) -> ValidationResult:
        """验证字典

        Args:
            value: 待验证的值
            key_validator: 键验证函数
            value_validator: 值验证函数
            required_keys: 必需的键列表
            allow_none: 是否允许None
            field_name: 字段名称

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 检查None
        if value is None:
            if allow_none:
                result.cleaned_data = None
                return result
            else:
                result.add_error(f"{field_name}不能为空")
                return result

        # 检查类型
        if not isinstance(value, dict):
            result.add_error(
                f"{field_name}类型错误：期望字典类型，实际类型为{type(value).__name__}"
            )
            return result

        # 检查必需的键
        if required_keys:
            for key in required_keys:
                if key not in value:
                    result.add_error(f"{field_name}缺少必需的键：{key}")

        # 验证键和值
        cleaned_dict = {}
        for k, v in value.items():
            # 验证键
            if key_validator:
                key_result = key_validator(k)
                result.merge(key_result)
                if not key_result.is_valid:
                    continue
                k = key_result.cleaned_data

            # 验证值
            if value_validator:
                val_result = value_validator(v)
                result.merge(val_result)
                if not val_result.is_valid:
                    continue
                v = val_result.cleaned_data

            cleaned_dict[k] = v

        result.cleaned_data = cleaned_dict
        return result


def validate_email(value: str) -> ValidationResult:
    """验证邮箱地址

    Args:
        value: 邮箱地址

    Returns:
        ValidationResult: 验证结果
    """
    validator = Validator()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validator.validate_string(value, pattern=pattern, field_name="邮箱")


def validate_phone(value: str) -> ValidationResult:
    """验证手机号码

    Args:
        value: 手机号码

    Returns:
        ValidationResult: 验证结果
    """
    validator = Validator()
    pattern = r'^1[3-9]\d{9}$'
    return validator.validate_string(value, pattern=pattern, field_name="手机号码")


def validate_url(value: str) -> ValidationResult:
    """验证URL

    Args:
        value: URL

    Returns:
        ValidationResult: 验证结果
    """
    validator = Validator()
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return validator.validate_string(value, pattern=pattern, field_name="URL")
