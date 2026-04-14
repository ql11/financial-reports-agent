"""
配置加载器模块

该模块负责加载和解析YAML格式的配置文件，提供配置验证和默认值合并功能。

功能特性：
- 支持YAML格式配置文件加载
- 配置验证和类型检查
- 默认配置与用户配置合并
- 便捷的点分隔路径访问
- 配置热重载
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import yaml
import logging
from copy import deepcopy

# 设置模块日志
logger = logging.getLogger(__name__)


class ConfigLoaderError(Exception):
    """配置加载器基础异常"""
    pass


class ConfigFileNotFoundError(ConfigLoaderError):
    """配置文件不存在异常"""
    pass


class ConfigValidationError(ConfigLoaderError):
    """配置验证异常"""
    pass


class ConfigParseError(ConfigLoaderError):
    """配置解析异常"""
    pass


class ConfigLoader:
    """配置加载器

    负责加载和解析YAML格式的配置文件，提供配置验证和默认值合并功能。

    Attributes:
        config_path: 配置文件路径
        config: 配置字典
        default_config: 默认配置字典
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        default_config: Optional[Dict[str, Any]] = None,
        auto_reload: bool = False
    ):
        """初始化配置加载器

        Args:
            config_path: 配置文件路径
            default_config: 默认配置字典
            auto_reload: 是否自动重载配置文件（当文件修改时）
        """
        self.config_path = Path(config_path) if config_path else None
        self.default_config = default_config or {}
        self.auto_reload = auto_reload
        self.config: Dict[str, Any] = {}
        self._last_modified: Optional[float] = None

        # 如果提供了配置文件路径，则立即加载
        if self.config_path:
            self.load()

        logger.info("配置加载器初始化完成")

    def load(self, config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """加载配置文件

        Args:
            config_path: 配置文件路径，如果提供则覆盖初始化时的路径

        Returns:
            Dict[str, Any]: 配置字典

        Raises:
            ConfigFileNotFoundError: 配置文件不存在时抛出
            ConfigParseError: 配置文件解析失败时抛出
        """
        if config_path:
            self.config_path = Path(config_path)

        if not self.config_path:
            logger.warning("未指定配置文件路径，使用默认配置")
            self.config = deepcopy(self.default_config)
            return self.config

        logger.info(f"加载配置文件: {self.config_path}")

        # 检查文件是否存在
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.config = deepcopy(self.default_config)
            return self.config

        # 记录文件修改时间
        self._last_modified = self.config_path.stat().st_mtime

        try:
            # 读取并解析YAML文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}

            # 合并默认配置
            self.config = self._merge_config(self.default_config, user_config)

            logger.info(f"成功加载配置文件，配置项数量: {len(self.config)}")
            return self.config

        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {self.config_path}, 错误: {e}")
            raise ConfigParseError(f"配置文件格式错误：{self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {self.config_path}, 错误: {e}")
            raise ConfigLoaderError(f"配置文件加载失败：{self.config_path}")

    def _merge_config(
        self,
        default: Dict[str, Any],
        user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并默认配置和用户配置

        Args:
            default: 默认配置
            user: 用户配置

        Returns:
            Dict[str, Any]: 合并后的配置
        """
        result = deepcopy(default)

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并字典
                result[key] = self._merge_config(result[key], value)
            else:
                # 用户配置覆盖默认配置
                result[key] = deepcopy(value)

        return result

    def get(
        self,
        key: str,
        default: Optional[Any] = None
    ) -> Any:
        """获取配置项

        支持点分隔路径访问，例如：'database.host'

        Args:
            key: 配置项键，支持点分隔路径
            default: 默认值

        Returns:
            Any: 配置项值
        """
        # 检查是否需要自动重载
        if self.auto_reload and self._check_file_modified():
            self.load()

        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            logger.debug(f"配置项不存在: {key}，使用默认值: {default}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        save: bool = False
    ) -> None:
        """设置配置项

        Args:
            key: 配置项键，支持点分隔路径
            value: 配置项值
            save: 是否保存到文件
        """
        keys = key.split('.')
        config = self.config

        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value
        logger.debug(f"设置配置项: {key} = {value}")

        # 保存到文件
        if save and self.config_path:
            self.save()

    def save(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """保存配置到文件

        Args:
            config_path: 配置文件路径，如果提供则覆盖初始化时的路径
        """
        path = Path(config_path) if config_path else self.config_path

        if not path:
            raise ConfigLoaderError("未指定配置文件路径")

        logger.info(f"保存配置到文件: {path}")

        try:
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            # 写入YAML文件
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, allow_unicode=True)

            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"配置保存失败: {path}, 错误: {e}")
            raise ConfigLoaderError(f"配置保存失败：{path}")

    def _check_file_modified(self) -> bool:
        """检查配置文件是否被修改

        Returns:
            bool: 文件是否被修改
        """
        if not self.config_path or not self.config_path.exists():
            return False

        current_modified = self.config_path.stat().st_mtime
        return current_modified != self._last_modified

    def validate(
        self,
        schema: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """验证配置

        Args:
            schema: 验证模式，定义配置项的类型和约束
            config: 待验证的配置，默认为当前配置

        Returns:
            bool: 验证是否通过

        Raises:
            ConfigValidationError: 验证失败时抛出
        """
        config = config or self.config
        errors = []

        self._validate_recursive(config, schema, errors, prefix='')

        if errors:
            error_msg = '\n'.join(errors)
            logger.error(f"配置验证失败:\n{error_msg}")
            raise ConfigValidationError(f"配置验证失败:\n{error_msg}")

        logger.info("配置验证通过")
        return True

    def _validate_recursive(
        self,
        config: Dict[str, Any],
        schema: Dict[str, Any],
        errors: List[str],
        prefix: str
    ) -> None:
        """递归验证配置

        Args:
            config: 配置字典
            schema: 验证模式
            errors: 错误列表
            prefix: 键前缀
        """
        for key, rules in schema.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # 检查必需项
            if rules.get('required', False) and key not in config:
                errors.append(f"缺少必需配置项: {full_key}")
                continue

            # 如果配置项不存在且有默认值，则跳过验证
            if key not in config:
                continue

            value = config[key]

            # 类型检查
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f"配置项类型错误: {full_key}, "
                    f"期望类型: {expected_type.__name__}, "
                    f"实际类型: {type(value).__name__}"
                )
                continue

            # 范围检查
            if 'min' in rules and isinstance(value, (int, float)):
                if value < rules['min']:
                    errors.append(
                        f"配置项值过小: {full_key}, "
                        f"最小值: {rules['min']}, "
                        f"实际值: {value}"
                    )

            if 'max' in rules and isinstance(value, (int, float)):
                if value > rules['max']:
                    errors.append(
                        f"配置项值过大: {full_key}, "
                        f"最大值: {rules['max']}, "
                        f"实际值: {value}"
                    )

            # 枚举值检查
            if 'choices' in rules:
                if value not in rules['choices']:
                    errors.append(
                        f"配置项值无效: {full_key}, "
                        f"有效值: {rules['choices']}, "
                        f"实际值: {value}"
                    )

            # 嵌套验证
            if 'schema' in rules and isinstance(value, dict):
                self._validate_recursive(value, rules['schema'], errors, full_key)

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        return deepcopy(self.config)

    def update(self, config: Dict[str, Any], save: bool = False) -> None:
        """更新配置

        Args:
            config: 新配置字典
            save: 是否保存到文件
        """
        self.config = self._merge_config(self.config, config)
        logger.info(f"更新配置，配置项数量: {len(self.config)}")

        if save and self.config_path:
            self.save()

    def reload(self) -> Dict[str, Any]:
        """重新加载配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        logger.info("重新加载配置")
        return self.load()

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问

        Args:
            key: 配置项键

        Returns:
            Any: 配置项值
        """
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """支持字典式设置

        Args:
            key: 配置项键
            value: 配置项值
        """
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """支持 in 操作符

        Args:
            key: 配置项键

        Returns:
            bool: 配置项是否存在
        """
        return self.get(key) is not None

    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置节

        Args:
            section: 配置节名称

        Returns:
            Dict[str, Any]: 配置节字典
        """
        return self.get(section, {})

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 配置字典
        """
        return self.get_all()
