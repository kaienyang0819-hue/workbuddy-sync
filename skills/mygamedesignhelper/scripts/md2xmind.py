"""
md2xmind.py - 结构化 Markdown → XMind 命令行入口

用法:
    python md2xmind.py <input.md> <output.xmind>

示例:
    python md2xmind.py brainstorm/brainstorm.md brainstorm/brainstorm.xmind

依赖:
    pip install xmind xmindparser
"""

from __future__ import annotations
import sys
import os

# Windows 终端兼容：强制 UTF-8 输出
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 确保 xmind_toolkit 包可被导入（同级目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 3:
        print("用法: python md2xmind.py <input.md> <output.xmind>")
        print()
        print("将结构化 Markdown（树形连接符格式）转换为 XMind 文件。")
        print("输入 MD 必须使用 ├──/└── 树形连接符表示层级。")
        sys.exit(1)

    input_md = sys.argv[1]
    output_xmind = sys.argv[2]

    # ── 检查输入文件 ──
    if not os.path.isfile(input_md):
        print(f"❌ 输入文件不存在: {input_md}")
        sys.exit(1)

    # ── 检查依赖 ──
    try:
        from xmind_toolkit.md_parser import parse_markdown_file
    except ImportError as e:
        print(f"⚠️ [XMind处理] 依赖缺失: {e}")
        print("请运行: pip install xmind xmindparser")
        sys.exit(1)

    try:
        from xmind_toolkit.writer import write_xmind
    except ImportError as e:
        print(f"⚠️ [XMind处理] 依赖缺失: {e}")
        print("请运行: pip install xmind xmindparser")
        sys.exit(1)

    # ── 确保输出目录存在 ──
    output_dir = os.path.dirname(output_xmind)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # ── 执行转换 ──
    try:
        print(f"📖 读取: {input_md}")
        workbook = parse_markdown_file(input_md)

        sheet_count = len(workbook.sheets)
        node_count = 0
        for sheet in workbook.sheets:
            def count_nodes(topic):
                c = 1
                for child in topic.children:
                    c += count_nodes(child)
                return c
            node_count += count_nodes(sheet.root)

        print(f"📊 解析完成: {sheet_count} 个画布, {node_count} 个节点")
        print(f"💾 写入: {output_xmind}")

        result_path = write_xmind(workbook, output_xmind)
        print(f"✅ 转换成功: {result_path}")

    except Exception as e:
        print(f"⚠️ [XMind处理] 转换失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
