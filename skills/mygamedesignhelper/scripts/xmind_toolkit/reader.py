"""
XMind 读取器 (重构版)

职责: .xmind 文件 → 数据模型 → 结构化 Markdown

重构改进:
    1. 与数据模型解耦：解析和格式化分离
    2. 路径参数化：不再硬编码路径
    3. 模块化：可独立调用解析 / 格式化 / 完整转换
    4. AI 友好：函数签名清晰，文档完整

使用方式 (AI Agent 调用):
    from xmind_toolkit.reader import read_xmind, xmind_to_markdown

    # 方式 1: 一步到位
    md_text = xmind_to_markdown('path/to/file.xmind')

    # 方式 2: 分步操作 (需要中间数据时)
    workbook = read_xmind('path/to/file.xmind')
    md_text  = format_workbook(workbook)
"""

from __future__ import annotations
import os, sys
from xmindparser import xmind_to_dict

# 兼容直接脚本执行（python reader.py）和包导入（python -m xmind_toolkit.reader）
try:
    from .model import Topic, Sheet, Workbook
    from .markers import marker_to_emoji
except ImportError:
    # 直接执行时，把 xmind_toolkit 所在目录加入 sys.path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from xmind_toolkit.model import Topic, Sheet, Workbook
    from xmind_toolkit.markers import marker_to_emoji


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 第一层: XMind 文件 → 数据模型
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_topic(raw: dict) -> Topic:
    """递归解析 xmindparser 输出的 topic 字典为 Topic 对象。"""
    return Topic.from_dict(raw)


def read_xmind(file_path: str) -> Workbook:
    """读取 .xmind 文件，返回 Workbook 数据模型。

    Args:
        file_path: .xmind 文件的绝对路径

    Returns:
        Workbook 数据模型对象
    """
    raw_data = xmind_to_dict(file_path)
    sheets = []
    for sheet_raw in raw_data:
        topic_raw = sheet_raw.get('topic', {})
        sheet = Sheet(
            title=sheet_raw.get('title', ''),
            root=_parse_topic(topic_raw),
            structure=sheet_raw.get('structure', ''),
        )
        sheets.append(sheet)
    return Workbook(sheets=sheets, source_path=file_path)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 第二层: 数据模型 → 结构化 Markdown
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _format_markers(markers: list[str]) -> str:
    """格式化标记图标为人类可读文本。"""
    if not markers:
        return ''
    tags = [marker_to_emoji(m) for m in markers]
    return ' ' + ' '.join(tags)


def _format_topic(topic: Topic, depth: int = 0, prefix: str = "",
                  is_last: bool = True, is_root: bool = False) -> list[str]:
    """递归格式化 Topic 为树形文本行。

    输出格式与原 xmind_reader.py 完全兼容，确保双向转换无损。

    Args:
        topic:   Topic 数据对象
        depth:   当前层级深度 (0=根节点)
        prefix:  当前行前缀 (用于树形缩进)
        is_last: 是否为同级最后一个节点
        is_root: 是否为根节点

    Returns:
        格式化后的文本行列表
    """
    lines = []
    title = topic.title or '(空)'

    # ── 构建当前行 ──
    if is_root:
        line = f"# {title}"
    else:
        connector = "└── " if is_last else "├── "
        line = f"{prefix}{connector}{title}"

    # ── 附加元数据 (方括号内) ──
    extras = []

    markers_str = _format_markers(topic.markers)
    if markers_str:
        extras.append(markers_str.strip())

    if topic.labels:
        extras.append(f"标签: {', '.join(topic.labels)}")

    if topic.link:
        extras.append(f"🔗 {topic.link}")

    if topic.image:
        extras.append("📷 [附图]")

    if extras:
        line += f"  【{'  |  '.join(extras)}】"

    lines.append(line)

    # ── 备注 ──
    if topic.note:
        if is_root:
            note_prefix = "  "
        else:
            note_prefix = prefix + ("    " if is_last else "│   ")
        for note_line in topic.note.strip().split('\n'):
            lines.append(f"{note_prefix}📝 {note_line.strip()}")

    # ── 评论 ──
    if topic.comments:
        if is_root:
            comment_prefix = "  "
        else:
            comment_prefix = prefix + ("    " if is_last else "│   ")
        for c in topic.comments:
            lines.append(f"{comment_prefix}💬 {c}")

    # ── 子节点 ──
    if topic.children:
        if is_root:
            child_prefix_base = ""
        else:
            child_prefix_base = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(topic.children):
            is_last_child = (i == len(topic.children) - 1)
            lines.extend(_format_topic(
                child, depth + 1, child_prefix_base, is_last_child
            ))

    # ── 标注 ──
    if topic.callouts:
        if is_root:
            callout_prefix = ""
        else:
            callout_prefix = prefix + ("    " if is_last else "│   ")
        for c in topic.callouts:
            lines.append(f"{callout_prefix}💡 标注: {c}")

    return lines


def format_workbook(workbook: Workbook) -> str:
    """将 Workbook 数据模型格式化为结构化 Markdown 文本。

    Args:
        workbook: Workbook 数据模型

    Returns:
        完整的结构化 Markdown 文本
    """
    lines = []
    lines.append("=" * 60)
    lines.append("📋 XMind 结构化内容")
    if workbook.source_path:
        lines.append(f"📁 源文件: {workbook.source_path}")
    lines.append("=" * 60)
    lines.append("")

    for idx, sheet in enumerate(workbook.sheets):
        sheet_title = sheet.title or f'画布 {idx + 1}'

        if len(workbook.sheets) > 1:
            lines.append(f"## 📑 画布 {idx + 1}: {sheet_title}")
            if sheet.structure:
                lines.append(f"   布局: {sheet.structure}")
            lines.append("")

        lines.extend(_format_topic(sheet.root, depth=0, is_root=True))
        lines.append("")

    return '\n'.join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 便捷函数: 一步完成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def xmind_to_markdown(file_path: str, output_path: str | None = None) -> str:
    """将 .xmind 文件转换为结构化 Markdown。

    Args:
        file_path:   .xmind 文件路径
        output_path: 可选，输出 .md 文件路径；不提供则仅返回文本

    Returns:
        结构化 Markdown 文本
    """
    workbook = read_xmind(file_path)
    text = format_workbook(workbook)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI 入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("用法: python -m xmind_toolkit.reader <input.xmind> [output.md]")
        sys.exit(1)

    xmind_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = xmind_to_markdown(xmind_path, out_path)
    print(result)
    if out_path:
        print(f"\n✅ 已保存到: {out_path}")
