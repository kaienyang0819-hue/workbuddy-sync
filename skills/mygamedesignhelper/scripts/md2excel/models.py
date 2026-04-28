# -*- coding: utf-8 -*-
"""
中间数据模型 - MD 解析后的结构化数据表示

层级关系:
  Document
    ├── DocumentMeta (frontmatter 元信息)
    ├── systems: list[SystemSection] (各系统, 对应 ## 标题)
    │     └── blocks: list[ContentBlock] (内容块)
    │           └── children: list[ContentBlock] (子内容块)
    ├── tlog: SystemSection | None (数据打点及tlog)
    ├── data_stats: SystemSection | None (数据统计需求)
    └── lessons: SystemSection | None (经验和教训)
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentMeta:
    """文档元信息，来自 YAML frontmatter"""
    title: str = ""
    author: str = ""
    planner: str = ""
    programmer: str = ""
    artist: str = ""
    created_date: str = ""
    status: str = "草案"


@dataclass
class ContentBlock:
    """
    内容块 - MD文档中的一个语义单元

    type 取值:
      - "heading3": ### 功能标题 → Excel 2级标题(暗红底), 写在B列
      - "heading4": #### 规则标题 → Excel 3级标题(深灰底), 写在C列
      - "heading5": ##### 规则细项标题 → Excel 加粗黑字, 写在D列
      - "text": 普通段落
      - "bold_text": 整行加粗的重点文本
      - "mixed_text": 含加粗片段的混合文本, segments 存储分段
      - "list_item": 列表项 (- 或 *)
      - "ordered_list_item": 有序列表项 (1. 2. 3.)
      - "sub_list_item": 缩进子列表项
      - "image": 图片引用 ![desc](path)
      - "image_placeholder": 图片占位符 [图片占位:desc]
      - "table": Markdown 表格
      - "raw": 无法识别的原始文本(容错)
    """
    type: str
    content: str = ""
    level: int = 0
    children: list = field(default_factory=list)
    image_path: str = ""
    image_desc: str = ""
    segments: list = field(default_factory=list)  # 混合文本的分段 [("text", "普通"), ("bold", "重点")]
    table_headers: list = field(default_factory=list)  # 表格表头
    table_rows: list = field(default_factory=list)  # 表格数据行
    table_name: str = ""  # 表格名称（用于数值表格设计Sheet引用）
    parent_heading: str = ""  # 所属的上级标题（用于标识表格来源）


@dataclass
class SystemSection:
    """系统章节 - 对应一个 Sheet"""
    name: str
    blocks: list = field(default_factory=list)  # list[ContentBlock]


@dataclass
class Document:
    """完整文档结构"""
    meta: DocumentMeta = field(default_factory=DocumentMeta)
    systems: list = field(default_factory=list)  # list[SystemSection]
    tlog: Optional[SystemSection] = None  # 数据打点及tlog
    data_stats: Optional[SystemSection] = None
    lessons: Optional[SystemSection] = None

    @property
    def project_title(self) -> str:
        """获取项目标题，优先使用 meta.title"""
        return self.meta.title or "未命名项目"

    @property
    def all_sheet_names(self) -> list:
        """获取所有 Sheet 名称列表（按顺序）"""
        names = ["文档维护"]
        names.extend(s.name for s in self.systems)
        names.append("数值表格设计")  # 固定Sheet
        if self.tlog:
            names.append(self.tlog.name)
        else:
            names.append("数据打点及tlog")
        if self.data_stats:
            names.append(self.data_stats.name)
        else:
            names.append("数据统计需求")
        if self.lessons:
            names.append(self.lessons.name)
        else:
            names.append("经验和教训")
        return names

    def collect_all_tables(self) -> list:
        """
        收集所有系统Sheet中的表格，用于生成"数值表格设计"Sheet

        返回: list of (system_name, table_name, ContentBlock)
        """
        tables = []
        table_counter = 0
        for section in self.systems:
            last_heading = section.name
            for block in section.blocks:
                if block.type in ("heading3", "heading4", "heading5"):
                    last_heading = block.content
                if block.type == "table":
                    table_counter += 1
                    name = block.table_name or f"表{table_counter}-{last_heading}"
                    tables.append((section.name, name, block))
        return tables
