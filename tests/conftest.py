#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置文件 - pytest fixtures
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config_loader import ConfigLoader


@pytest.fixture
def config():
    """配置加载器"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    return ConfigLoader(str(config_path))


@pytest.fixture
def sample_pdf_path():
    """示例PDF文件路径"""
    return Path(__file__).parent.parent / "source" / "英洛华_2025_年报.pdf"
