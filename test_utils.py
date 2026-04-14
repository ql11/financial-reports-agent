"""
工具模块测试脚本

用于验证工具模块的基本功能是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils import (
    FileManager,
    ConfigLoader,
    setup_logger,
    Validator,
    ValidationResult
)


def test_file_manager():
    """测试文件管理器"""
    print("\n=== 测试文件管理器 ===")

    # 创建文件管理器
    fm = FileManager(base_path=project_root)
    print(f"[OK] 文件管理器创建成功，基础路径: {fm.base_path}")

    # 测试路径验证
    test_path = "config/config.yaml"
    abs_path = fm.get_absolute_path(test_path)
    print(f"[OK] 路径验证成功: {test_path} -> {abs_path}")

    # 测试文件存在检查
    exists = fm.file_exists(test_path)
    print(f"[OK] 文件存在检查: {test_path} -> {exists}")

    # 测试文件读取
    if exists:
        content = fm.read_text(test_path)
        print(f"[OK] 文件读取成功，内容长度: {len(content)} 字符")

    print("[OK] 文件管理器测试通过")


def test_config_loader():
    """测试配置加载器"""
    print("\n=== 测试配置加载器 ===")

    # 创建配置加载器
    config_path = project_root / "config" / "config.yaml"
    loader = ConfigLoader(config_path=config_path)
    print(f"[OK] 配置加载器创建成功")

    # 测试配置访问
    log_level = loader.get('logging.level')
    print(f"[OK] 配置访问成功: logging.level = {log_level}")

    # 测试点分隔路径访问
    log_filename = loader.get('logging.filename')
    print(f"[OK] 点分隔路径访问成功: logging.filename = {log_filename}")

    # 测试默认值
    test_value = loader.get('nonexistent.key', default='default_value')
    print(f"[OK] 默认值测试成功: nonexistent.key = {test_value}")

    print("[OK] 配置加载器测试通过")


def test_logger():
    """测试日志工具"""
    print("\n=== 测试日志工具 ===")

    # 创建日志器
    logger = setup_logger(
        name='test_logger',
        level='DEBUG',
        log_dir=project_root / 'logs',
        filename='test.log',
        console_output=True,
        file_output=True,
        use_colorlog=True
    )
    print("[OK] 日志器创建成功")

    # 测试各级别日志
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    print("[OK] 日志记录测试成功")

    print("[OK] 日志工具测试通过")


def test_validator():
    """测试数据验证器"""
    print("\n=== 测试数据验证器 ===")

    # 创建验证器
    validator = Validator()
    print("[OK] 验证器创建成功")

    # 测试数值验证
    result = validator.validate_number(100, min_value=0, max_value=200)
    print(f"[OK] 数值验证成功: {result}")

    # 测试日期验证
    result = validator.validate_date("2024-01-01", format_str="%Y-%m-%d")
    print(f"[OK] 日期验证成功: {result}, 清洗后数据: {result.cleaned_data}")

    # 测试路径验证
    result = validator.validate_path("config/config.yaml", must_exist=True)
    print(f"[OK] 路径验证成功: {result}")

    # 测试财务数据验证
    result = validator.validate_financial_balance(
        assets=1000,
        liabilities=600,
        equity=400,
        tolerance=0.01
    )
    print(f"[OK] 财务数据验证成功: {result}, 平衡状态: {result.cleaned_data['is_balanced']}")

    # 测试批量验证
    data = {
        'amount': 100,
        'date': '2024-01-01',
        'description': '测试数据'
    }
    validators = {
        'amount': lambda x: validator.validate_number(x, min_value=0),
        'date': lambda x: validator.validate_date(x),
        'description': lambda x: validator.validate_string(x, min_length=1)
    }
    result = validator.validate_batch(data, validators)
    print(f"[OK] 批量验证成功: {result}")

    print("[OK] 数据验证器测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试工具模块")
    print("=" * 60)

    try:
        test_file_manager()
        test_config_loader()
        test_logger()
        test_validator()

        print("\n" + "=" * 60)
        print("[OK] 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
