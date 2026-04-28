"""
XMind 写入器

职责: 数据模型 (Workbook) → .xmind 文件

依赖 xmind SDK (pip install xmind) 来创建符合 XMind 格式的文件。

使用方式 (AI Agent 调用):
    from xmind_toolkit.writer import write_xmind
    from xmind_toolkit.model import Workbook

    workbook = Workbook(...)  # 或从 md_parser 获得
    write_xmind(workbook, 'output.xmind')
"""

from __future__ import annotations
import xmind
from xmind.core.topic import TopicElement

from .model import Topic, Sheet, Workbook


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 内部辅助
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_topic(parent_xmind_topic, topic: Topic):
    """递归地将 Topic 数据模型写入 xmind SDK 的 topic 对象。

    Args:
        parent_xmind_topic: xmind SDK 的 TopicElement 对象
        topic: 我们的 Topic 数据模型
    """
    parent_xmind_topic.setTitle(topic.title or '(空)')

    # 标记图标
    for marker_id in topic.markers:
        parent_xmind_topic.addMarker(marker_id)

    # 标签
    for label in topic.labels:
        parent_xmind_topic.addLabel(label)

    # 备注
    if topic.note:
        parent_xmind_topic.setPlainNotes(topic.note)

    # 超链接
    if topic.link:
        parent_xmind_topic.setURLHyperlink(topic.link)

    # 评论
    for comment in topic.comments:
        try:
            parent_xmind_topic.addComment(comment)
        except (TypeError, AttributeError):
            # 某些版本的 xmind SDK 可能不支持 addComment
            # 退化为在备注中追加
            existing = parent_xmind_topic.getPlainNotes() or ''
            parent_xmind_topic.setPlainNotes(
                existing + f'\n💬 {comment}' if existing else f'💬 {comment}'
            )

    # 子节点
    for child in topic.children:
        child_xmind = parent_xmind_topic.addSubTopic()
        _build_topic(child_xmind, child)

    # 标注 (callout): xmind SDK 不原生支持，退化为特殊子节点
    for callout_text in topic.callouts:
        callout_node = parent_xmind_topic.addSubTopic()
        callout_node.setTitle(f'💡 {callout_text}')
        callout_node.addMarker('symbol-info')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 公开 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def write_xmind(workbook: Workbook, output_path: str) -> str:
    """将 Workbook 数据模型写入 .xmind 文件。

    Args:
        workbook:    Workbook 数据模型
        output_path: 输出 .xmind 文件路径 (需以 .xmind 结尾)

    Returns:
        输出文件的绝对路径
    """
    if not output_path.endswith('.xmind'):
        output_path += '.xmind'

    xmind_workbook = xmind.load(output_path)

    for idx, sheet_data in enumerate(workbook.sheets):
        if idx == 0:
            # 使用默认的第一个 sheet
            xmind_sheet = xmind_workbook.getPrimarySheet()
        else:
            xmind_sheet = xmind_workbook.createSheet()

        xmind_sheet.setTitle(sheet_data.title or f'画布 {idx + 1}')

        root_topic = xmind_sheet.getRootTopic()
        _build_topic(root_topic, sheet_data.root)

    xmind.save(xmind_workbook, output_path)
    return output_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI 入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("XMind Writer - 不支持直接命令行调用")
    print("请使用 md2xmind.py 进行 Markdown → XMind 转换")
    print("或通过 Python API: from xmind_toolkit.writer import write_xmind")
