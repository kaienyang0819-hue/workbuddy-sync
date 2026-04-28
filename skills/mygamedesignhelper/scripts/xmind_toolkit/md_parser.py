"""
结构化 Markdown 解析器

职责: 结构化 Markdown 文本 → 数据模型 (Workbook)

解析原理:
    本解析器处理由 reader.py 生成的树形文本格式。
    通过识别树形连接符 (├──/└──) 和缩进前缀 (│   /    ) 来恢复层级关系，
    通过识别元数据方括号 【...】 来恢复标记、标签、链接等属性，
    通过识别特殊前缀 (📝/💬/💡) 来恢复备注、评论、标注。

使用方式 (AI Agent 调用):
    from xmind_toolkit.md_parser import parse_markdown, parse_markdown_file

    # 从文本解析
    workbook = parse_markdown(md_text)

    # 从文件解析
    workbook = parse_markdown_file('path/to/file.md')
"""

from __future__ import annotations
import re
from typing import Optional

from .model import Topic, Sheet, Workbook
from .markers import emoji_to_marker, EMOJI_TO_MARKER


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 内部辅助
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 匹配树形节点行: 捕获 prefix + connector + title + optional metadata
_TREE_NODE_RE = re.compile(
    r'^(?P<prefix>(?:│   |    )*)'   # 缩进前缀 (│   或 4空格 的重复)
    r'(?P<connector>[├└]── )'         # 连接符
    r'(?P<rest>.+)$'                  # 剩余内容 (标题 + 可能的元数据)
)

# 匹配根节点: # 开头
_ROOT_RE = re.compile(r'^# (?P<rest>.+)$')

# 匹配元数据括号: 【...】
_META_RE = re.compile(r'^(?P<title>.*?)\s*【(?P<meta>.+)】$')

# 匹配画布标题行
_SHEET_RE = re.compile(r'^## 📑 画布 \d+: (?P<title>.+)$')

# 匹配布局行
_LAYOUT_RE = re.compile(r'^\s+布局: (?P<structure>.+)$')

# 匹配备注行
_NOTE_RE = re.compile(r'^(?P<prefix>.*)📝 (?P<text>.+)$')

# 匹配评论行
_COMMENT_RE = re.compile(r'^(?P<prefix>.*)💬 (?P<text>.+)$')

# 匹配标注行
_CALLOUT_RE = re.compile(r'^(?P<prefix>.*)💡 标注: (?P<text>.+)$')

# 匹配源文件行
_SOURCE_RE = re.compile(r'^📁 源文件: (?P<path>.+)$')


def _calc_depth(prefix: str) -> int:
    """计算树形前缀对应的层级深度。
    
    每 4 个字符 (│   或 4 空格) 代表一层。
    """
    if not prefix:
        return 0
    # 每段 4 字符宽
    return len(prefix) // 4


def _parse_meta(meta_str: str) -> dict:
    """解析方括号内的元数据字符串。

    格式: "emoji1  |  标签: a, b  |  🔗 url  |  📷 [附图]"

    Returns:
        dict with keys: markers, labels, link, image
    """
    result = {
        'markers': [],
        'labels': [],
        'link': None,
        'image': False,
    }

    parts = [p.strip() for p in meta_str.split('  |  ')]

    for part in parts:
        if not part:
            continue

        # 检查是否是链接
        if part.startswith('🔗 '):
            result['link'] = part[2:].strip()
            continue

        # 检查是否有附图
        if '📷' in part and '[附图]' in part:
            result['image'] = True
            continue

        # 检查是否是标签
        if part.startswith('标签:') or part.startswith('标签: '):
            label_text = part.split(':', 1)[1].strip()
            result['labels'] = [l.strip() for l in label_text.split(',')]
            continue

        # 其余的尝试匹配 marker
        # 一个 part 可能包含多个空格分隔的 marker
        tokens = part.split()
        for token in tokens:
            marker_id = emoji_to_marker(token)
            if marker_id:
                result['markers'].append(marker_id)
            else:
                # 尝试原始格式 [marker_id]
                m = re.match(r'^\[(.+)\]$', token)
                if m:
                    result['markers'].append(m.group(1))

    return result


def _parse_title_and_meta(raw: str) -> tuple[str, dict]:
    """分离标题文本和元数据。

    Args:
        raw: 节点的完整文本（标题 + 可能的 【...】）

    Returns:
        (title, meta_dict)
    """
    m = _META_RE.match(raw)
    if m:
        title = m.group('title').strip() or '(空)'
        meta = _parse_meta(m.group('meta'))
        return title, meta
    return raw.strip(), {'markers': [], 'labels': [], 'link': None, 'image': False}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主解析逻辑
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_tree_lines(lines: list[str]) -> Topic:
    """解析一组树形文本行为 Topic 树。

    解析策略:
        1. 第一行必须是 # 开头的根节点
        2. 后续行通过前缀深度确定父子关系
        3. 📝/💬/💡 行附加到最近的节点
    """
    if not lines:
        return Topic(title='(空)')

    # ── 解析根节点 ──
    first_line = lines[0].strip()
    root_match = _ROOT_RE.match(first_line)
    if root_match:
        raw_title = root_match.group('rest')
    else:
        raw_title = first_line

    title, meta = _parse_title_and_meta(raw_title)
    root = Topic(
        title=title,
        markers=meta['markers'],
        labels=meta['labels'],
        link=meta['link'],
        image=meta['image'],
    )

    # ── 逐行解析子节点 ──
    # stack: [(depth, Topic)] 用于追踪当前路径
    stack: list[tuple[int, Topic]] = [(-1, root)]
    last_topic: Topic = root

    for line in lines[1:]:
        # 跳过空行和分隔线
        if not line.strip() or line.strip().startswith('=' * 10):
            continue

        # 检查是否为备注行
        note_m = _NOTE_RE.match(line)
        if note_m:
            text = note_m.group('text').strip()
            if last_topic.note:
                last_topic.note += '\n' + text
            else:
                last_topic.note = text
            continue

        # 检查是否为评论行
        comment_m = _COMMENT_RE.match(line)
        if comment_m:
            last_topic.comments.append(comment_m.group('text').strip())
            continue

        # 检查是否为标注行
        callout_m = _CALLOUT_RE.match(line)
        if callout_m:
            last_topic.callouts.append(callout_m.group('text').strip())
            continue

        # 检查是否为树形节点
        tree_m = _TREE_NODE_RE.match(line)
        if tree_m:
            prefix = tree_m.group('prefix')
            raw_rest = tree_m.group('rest')
            depth = _calc_depth(prefix)

            t_title, t_meta = _parse_title_and_meta(raw_rest)
            new_topic = Topic(
                title=t_title,
                markers=t_meta['markers'],
                labels=t_meta['labels'],
                link=t_meta['link'],
                image=t_meta['image'],
            )

            # 找到父节点: stack 中 depth 小于当前的最后一个
            while len(stack) > 1 and stack[-1][0] >= depth:
                stack.pop()

            parent = stack[-1][1]
            parent.children.append(new_topic)
            stack.append((depth, new_topic))
            last_topic = new_topic
            continue

        # 其他行 (可能是人名注释、纯文本等): 
        # 如果不是已知格式，将作为备注附加到上一个节点
        stripped = line.strip()
        if stripped and not stripped.startswith('📋') and not stripped.startswith('📁'):
            # 可能是嵌在节点间的人名/标注文本
            # 检测是否像人名（短文本、无特殊符号）
            if len(stripped) < 20 and not any(c in stripped for c in '├└│──'):
                # 作为标签附加到最近的节点
                if stripped not in last_topic.labels:
                    last_topic.labels.append(stripped)
            else:
                if last_topic.note:
                    last_topic.note += '\n' + stripped
                else:
                    last_topic.note = stripped

    return root


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 公开 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_markdown(text: str) -> Workbook:
    """解析结构化 Markdown 文本为 Workbook 数据模型。

    支持单画布和多画布格式。

    Args:
        text: 由 reader.py 生成的结构化 Markdown 文本

    Returns:
        Workbook 数据模型
    """
    lines = text.split('\n')
    source_path = None
    sheets: list[Sheet] = []

    # ── 提取头部信息 ──
    for line in lines:
        src_m = _SOURCE_RE.match(line.strip())
        if src_m:
            source_path = src_m.group('path')
            break

    # ── 检查是否有多画布 ──
    sheet_indices = []
    for i, line in enumerate(lines):
        if _SHEET_RE.match(line.strip()):
            sheet_indices.append(i)

    if sheet_indices:
        # 多画布模式
        for idx, start in enumerate(sheet_indices):
            end = sheet_indices[idx + 1] if idx + 1 < len(sheet_indices) else len(lines)
            chunk = lines[start:end]

            sheet_title = ''
            structure = ''
            tree_start = 0

            for j, cline in enumerate(chunk):
                sm = _SHEET_RE.match(cline.strip())
                if sm:
                    sheet_title = sm.group('title')
                    continue
                lm = _LAYOUT_RE.match(cline)
                if lm:
                    structure = lm.group('structure')
                    continue
                if _ROOT_RE.match(cline.strip()):
                    tree_start = j
                    break

            root = _parse_tree_lines(chunk[tree_start:])
            sheets.append(Sheet(title=sheet_title, root=root, structure=structure))
    else:
        # 单画布模式: 找到 # 开头的行作为起始
        tree_start = 0
        for i, line in enumerate(lines):
            if _ROOT_RE.match(line.strip()):
                tree_start = i
                break

        root = _parse_tree_lines(lines[tree_start:])
        sheet_title = root.title
        sheets.append(Sheet(title=sheet_title, root=root))

    return Workbook(sheets=sheets, source_path=source_path)


def parse_markdown_file(file_path: str) -> Workbook:
    """从文件读取结构化 Markdown 并解析为 Workbook。

    Args:
        file_path: .md 文件路径

    Returns:
        Workbook 数据模型
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_markdown(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI 入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    import sys
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("用法: python -m xmind_toolkit.md_parser <input.md>")
        print("  输出解析后的 JSON 数据模型到 stdout")
        sys.exit(1)

    workbook = parse_markdown_file(sys.argv[1])
    print(json.dumps(workbook.to_dict(), ensure_ascii=False, indent=2))
