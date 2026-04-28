# -*- coding: utf-8 -*-
"""
快捷启动脚本 - MD → Excel 转换

用法:
  python convert.py input.md
  python convert.py input.md -o output.xlsx
  python convert.py input.md -v
"""
import sys
import os

# 确保 scripts/ 目录在 sys.path 中（convert.py 在 scripts/md2excel/ 下）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from md2excel.cli import main

if __name__ == "__main__":
    main()
