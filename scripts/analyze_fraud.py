#!/usr/bin/env python
"""单文件财报分析脚本。"""

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.cli import analyze_main


def main():
    return analyze_main()


if __name__ == "__main__":
    sys.exit(main())
