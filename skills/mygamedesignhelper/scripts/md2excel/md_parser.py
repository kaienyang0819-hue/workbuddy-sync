# -*- coding: utf-8 -*-
"""
MD 解析器 - 将 Markdown 策划文档解析为结构化中间数据模型

解析流程:
  1. 提取 YAML frontmatter → DocumentMeta
  2. 逐行扫描，识别标题层级和内容类型
  3. 按 ## 标题切分系统章节
  4. 特殊章节（数据打点及tlog、数据统计需求、经验和教训）归入固定字段
  5. 为表格自动编号命名，记录所属标题
  6. 内容完整性统计
"""
import re
import yaml
from pathlib import Path
from .models import Document, DocumentMeta, ContentBlock, SystemSection


# ============================================================
#  正则表达式
# ============================================================
RE_FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
RE_HEADING = re.compile(r'^(#{1,5})\s+(.+)$')
RE_IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
RE_IMAGE_PLACEHOLDER = re.compile(r'\[图片占位[:：]\s*(.+?)\]')
RE_BOLD_FULL = re.compile(r'^\*\*(.+)\*\*$')  # 整行都是加粗
RE_BOLD_PARTIAL = re.compile(r'\*\*(.+?)\*\*')  # 行内含加粗片段
RE_UNORDERED_LIST = re.compile(r'^(\s*)[*\-+]\s+(.+)$')
RE_ORDERED_LIST = re.compile(r'^(\s*)\d+[.)]\s+(.+)$')
RE_TABLE_ROW = re.compile(r'^\|(.+)\|$')
RE_TABLE_SEP = re.compile(r'^\|[\s\-:|]+\|$')
RE_HTML_TAG = re.compile(r'<[^>]+>')

# 特殊 Sheet 关键词匹配
KEYWORDS_TLOG = ["打点", "tlog", "埋点"]
KEYWORDS_DATA_STATS = ["数据统计"]
KEYWORDS_LESSONS = ["经验", "教训"]


def _is_special_section(title: str, keywords: list) -> bool:
    """判断标题是否匹配特殊章节关键词"""
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def _parse_frontmatter(text: str):
    """
    解析 YAML frontmatter
    返回: (DocumentMeta, 剩余文本)
    """
    match = RE_FRONTMATTER.match(text)
    if not match:
        return DocumentMeta(), text

    yaml_str = match.group(1)
    remaining = text[match.end():]

    try:
        data = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        return DocumentMeta(), text

    meta = DocumentMeta(
        title=str(data.get("title", "")),
        author=str(data.get("author", "")),
        planner=str(data.get("planner", "")),
        programmer=str(data.get("programmer", "")),
        artist=str(data.get("artist", "")),
        created_date=str(data.get("created_date", "")),
        status=str(data.get("status", "草案")),
    )
    return meta, remaining


def _parse_mixed_text(line: str):
    """
    解析含有加粗片段的混合文本行
    返回: list of (type, text) 元组
      type: "text" | "bold"
    """
    segments = []
    last_end = 0
    for m in RE_BOLD_PARTIAL.finditer(line):
        if m.start() > last_end:
            segments.append(("text", line[last_end:m.start()]))
        segments.append(("bold", m.group(1)))
        last_end = m.end()
    if last_end < len(line):
        segments.append(("text", line[last_end:]))
    return segments


def _clean_html(text: str) -> str:
    """去除 HTML 标签，保留纯文本"""
    return RE_HTML_TAG.sub("", text)


def parse_md(md_text: str, source_path: str = "") -> Document:
    """
    解析 Markdown 文本为 Document 对象

    参数:
      md_text: Markdown 文本内容
      source_path: MD 文件路径（用于解析相对图片路径）

    返回:
      Document 对象
    """
    doc = Document()

    # 1. 解析 frontmatter
    doc.meta, body = _parse_frontmatter(md_text)

    # 2. 逐行扫描
    lines = body.split("\n")
    total_lines = len(lines)
    content_lines = 0

    current_section = None  # 当前 SystemSection
    current_blocks = []     # 当前章节的内容块列表
    project_title = ""      # # 一级标题

    # 表格解析状态
    in_table = False
    table_headers = []
    table_rows = []
    table_separator_seen = False

    # 层级跟踪（用于给表格命名、确定列号）
    last_heading3 = ""  # 最近的 ### 标题
    last_heading4 = ""  # 最近的 #### 标题
    last_heading5 = ""  # 最近的 ##### 标题
    # 表格自动计数器
    table_counter = 0

    def _get_parent_heading():
        """获取当前最近的上级标题"""
        return last_heading5 or last_heading4 or last_heading3 or (current_section.name if current_section else "")

    def _flush_table():
        """将累积的表格数据创建为 ContentBlock"""
        nonlocal in_table, table_headers, table_rows, table_separator_seen, table_counter
        if table_headers or table_rows:
            table_counter += 1
            parent = _get_parent_heading()
            table_name = f"表{table_counter}-{parent}"
            block = ContentBlock(
                type="table",
                content="",
                table_headers=table_headers[:],
                table_rows=[r[:] for r in table_rows],
                table_name=table_name,
                parent_heading=parent,
            )
            current_blocks.append(block)
        in_table = False
        table_headers = []
        table_rows = []
        table_separator_seen = False

    def _flush_section():
        """将当前章节保存"""
        nonlocal current_section, current_blocks, last_heading3, last_heading4, last_heading5
        if current_section is not None:
            current_section.blocks = current_blocks[:]
            name = current_section.name

            if _is_special_section(name, KEYWORDS_TLOG):
                doc.tlog = current_section
            elif _is_special_section(name, KEYWORDS_DATA_STATS):
                doc.data_stats = current_section
            elif _is_special_section(name, KEYWORDS_LESSONS):
                doc.lessons = current_section
            else:
                doc.systems.append(current_section)

        current_section = None
        current_blocks = []
        last_heading3 = ""
        last_heading4 = ""
        last_heading5 = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 跳过空行
        if not stripped:
            if in_table:
                _flush_table()
            i += 1
            continue

        content_lines += 1

        # --- 表格检测 ---
        table_match = RE_TABLE_ROW.match(stripped)
        if table_match:
            cells = [c.strip() for c in table_match.group(1).split("|")]

            if RE_TABLE_SEP.match(stripped):
                # 分隔行
                table_separator_seen = True
                i += 1
                continue

            if not in_table:
                # 表格开始，第一行为表头
                in_table = True
                table_headers = cells
                table_separator_seen = False
            else:
                if table_separator_seen:
                    # 数据行
                    table_rows.append(cells)
                else:
                    # 没有分隔行，可能不是标准表格，当正文处理
                    _flush_table()
                    current_blocks.append(ContentBlock(type="raw", content=_clean_html(stripped)))
            i += 1
            continue
        elif in_table:
            _flush_table()

        # --- 标题检测 ---
        heading_match = RE_HEADING.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()

            if level == 1:
                # # 一级标题 → 项目名称
                project_title = title
                if not doc.meta.title:
                    doc.meta.title = title

            elif level == 2:
                # ## 二级标题 → 新建 Sheet
                _flush_table()
                _flush_section()
                current_section = SystemSection(name=title)
                current_blocks = []

            elif level == 3:
                # ### 三级标题 → 功能标题 (暗红底, B列)
                last_heading3 = title
                last_heading4 = ""
                last_heading5 = ""
                current_blocks.append(ContentBlock(type="heading3", content=title, level=3))

            elif level == 4:
                # #### 四级标题 → 规则标题 (深灰底, C列)
                last_heading4 = title
                last_heading5 = ""
                current_blocks.append(ContentBlock(type="heading4", content=title, level=4))

            elif level == 5:
                # ##### 五级标题 → 规则细项 (加粗黑字, D列)
                last_heading5 = title
                current_blocks.append(ContentBlock(type="heading5", content=title, level=5))

            i += 1
            continue

        # --- 图片检测 ---
        img_match = RE_IMAGE.match(stripped)
        if img_match:
            desc = img_match.group(1)
            path = img_match.group(2)
            # 解析相对路径
            if source_path and not Path(path).is_absolute():
                abs_path = str(Path(source_path).parent / path)
            else:
                abs_path = path
            current_blocks.append(ContentBlock(
                type="image", content=desc,
                image_path=abs_path, image_desc=desc
            ))
            i += 1
            continue

        # --- 图片占位符检测 ---
        placeholder_match = RE_IMAGE_PLACEHOLDER.match(stripped)
        if placeholder_match:
            desc = placeholder_match.group(1)
            current_blocks.append(ContentBlock(
                type="image_placeholder", content=desc, image_desc=desc
            ))
            i += 1
            continue

        # --- 列表检测 ---
        ul_match = RE_UNORDERED_LIST.match(line)  # 用原始 line 保留缩进
        if ul_match:
            indent = len(ul_match.group(1))
            text = _clean_html(ul_match.group(2).strip())
            if indent >= 4:
                block_type = "sub_list_item"
            else:
                block_type = "list_item"

            # 检查列表项内是否有加粗
            if RE_BOLD_PARTIAL.search(text):
                segments = _parse_mixed_text(text)
                current_blocks.append(ContentBlock(
                    type=block_type, content=text, segments=segments
                ))
            else:
                current_blocks.append(ContentBlock(type=block_type, content=text))
            i += 1
            continue

        ol_match = RE_ORDERED_LIST.match(line)
        if ol_match:
            indent = len(ol_match.group(1))
            text = _clean_html(ol_match.group(2).strip())
            if indent >= 4:
                block_type = "sub_list_item"
            else:
                block_type = "ordered_list_item"

            if RE_BOLD_PARTIAL.search(text):
                segments = _parse_mixed_text(text)
                current_blocks.append(ContentBlock(
                    type=block_type, content=text, segments=segments
                ))
            else:
                current_blocks.append(ContentBlock(type=block_type, content=text))
            i += 1
            continue

        # --- 文本行 ---
        text = _clean_html(stripped)

        # 整行加粗检测
        bold_full = RE_BOLD_FULL.match(text)
        if bold_full:
            current_blocks.append(ContentBlock(
                type="bold_text", content=bold_full.group(1)
            ))
            i += 1
            continue

        # 行内含加粗片段
        if RE_BOLD_PARTIAL.search(text):
            segments = _parse_mixed_text(text)
            current_blocks.append(ContentBlock(
                type="mixed_text", content=text, segments=segments
            ))
            i += 1
            continue

        # 普通文本
        current_blocks.append(ContentBlock(type="text", content=text))
        i += 1

    # 收尾
    if in_table:
        _flush_table()
    _flush_section()

    # 如果没有任何 ## 章节，所有内容归入一个默认 Sheet
    if not doc.systems and not doc.tlog and not doc.data_stats and not doc.lessons and current_blocks:
        default_section = SystemSection(name="内容概述", blocks=current_blocks)
        doc.systems.append(default_section)

    # 统计信息
    doc._stats = {
        "total_lines": total_lines,
        "content_lines": content_lines,
        "system_count": len(doc.systems),
        "has_tlog": doc.tlog is not None,
        "has_data_stats": doc.data_stats is not None,
        "has_lessons": doc.lessons is not None,
    }

    return doc


def parse_md_file(filepath: str) -> Document:
    """
    从文件路径解析 MD 文档

    参数:
      filepath: MD 文件的路径

    返回:
      Document 对象
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"MD 文件不存在: {filepath}")

    text = path.read_text(encoding="utf-8")
    doc = parse_md(text, source_path=str(path))

    # 如果 title 仍为空，用文件名
    if not doc.meta.title:
        doc.meta.title = path.stem

    return doc


def get_content_stats(doc: Document) -> dict:
    """
    统计文档内容，用于完整性校验

    返回:
      {
        "total_blocks": int,  # 总内容块数
        "by_type": dict,      # 按类型统计
        "sheet_count": int,   # Sheet 数量
        "sheets": list,       # Sheet 名称列表
      }
    """
    stats = {"total_blocks": 0, "by_type": {}, "sheet_count": 0, "sheets": []}

    all_sections = list(doc.systems)
    if doc.tlog:
        all_sections.append(doc.tlog)
    if doc.data_stats:
        all_sections.append(doc.data_stats)
    if doc.lessons:
        all_sections.append(doc.lessons)

    stats["sheet_count"] = len(all_sections) + 1  # +1 文档维护
    stats["sheets"] = doc.all_sheet_names

    for section in all_sections:
        for block in section.blocks:
            stats["total_blocks"] += 1
            t = block.type
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    return stats
