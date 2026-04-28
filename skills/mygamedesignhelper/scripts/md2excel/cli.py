# -*- coding: utf-8 -*-
"""
命令行入口 - MD → Excel 转换工具

用法:
  python -m md2excel.cli input.md [-o output.xlsx] [--images-dir ./images]
  python convert.py input.md [-o output.xlsx]
"""
import argparse
import sys
import time
from pathlib import Path

from .md_parser import parse_md_file, get_content_stats
from .excel_generator import generate_excel


def main(args=None):
    parser = argparse.ArgumentParser(
        description="MD 策划文档 → Excel 转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python convert.py 战斗系统策划案.md
  python convert.py 战斗系统策划案.md -o output/战斗系统.xlsx
  python convert.py 战斗系统策划案.md --images-dir ./images
        """,
    )
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("-o", "--output", help="输出 Excel 文件路径 (默认: 与输入同名.xlsx)")
    parser.add_argument("--images-dir", help="图片搜索目录 (默认: MD文件所在目录)")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细日志")

    opts = parser.parse_args(args)

    input_path = Path(opts.input)
    if not input_path.exists():
        print(f"[错误] 输入文件不存在: {input_path}")
        sys.exit(1)

    # 确定输出路径
    if opts.output:
        output_path = Path(opts.output)
    else:
        output_path = input_path.with_suffix(".xlsx")

    print(f"[MD→Excel] 开始转换")
    print(f"  输入: {input_path}")
    print(f"  输出: {output_path}")
    print()

    start_time = time.time()

    # 1. 解析 MD
    print("[1/3] 解析 Markdown 文档...")
    try:
        doc = parse_md_file(str(input_path))
    except Exception as e:
        print(f"[错误] MD 解析失败: {e}")
        sys.exit(1)

    content_stats = get_content_stats(doc)

    if opts.verbose:
        print(f"  项目名称: {doc.project_title}")
        print(f"  Sheet 列表: {content_stats['sheets']}")
        print(f"  内容块总数: {content_stats['total_blocks']}")
        print(f"  内容块类型分布: {content_stats['by_type']}")
        print()

    # 2. 生成 Excel
    print("[2/3] 生成 Excel 文件...")
    try:
        gen_stats = generate_excel(doc, str(output_path))
    except Exception as e:
        print(f"[错误] Excel 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 3. 输出转换报告
    elapsed = time.time() - start_time

    print("[3/3] 转换完成!")
    print()
    print("=" * 50)
    print("  转换报告")
    print("=" * 50)
    print(f"  项目名称: {doc.project_title}")
    print(f"  Sheet 数量: {gen_stats['sheets_created']}")
    print(f"  Sheet 列表: {', '.join(content_stats['sheets'])}")
    print(f"  内容单元格: {gen_stats['total_cells']}")
    print(f"  图片已插入: {gen_stats['images_inserted']}")
    print(f"  图片占位符: {gen_stats['images_placeholder']}")
    if gen_stats['images_not_found'] > 0:
        print(f"  [警告] 图片未找到: {gen_stats['images_not_found']}")
    print(f"  耗时: {elapsed:.2f}s")
    print(f"  输出文件: {output_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
