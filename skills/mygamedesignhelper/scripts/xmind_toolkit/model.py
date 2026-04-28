"""
统一数据模型

定义 Topic / Sheet / Workbook 三层数据结构，
作为 XMind 文件和结构化 Markdown 之间的中间表示。

设计原则 (AI 友好):
    1. 纯 Python dataclass，无外部依赖
    2. 可直接 JSON 序列化 (dict/list)
    3. 字段名与 XMind 内部术语对齐
    4. 所有字段都有类型标注和默认值
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Topic:
    """思维导图节点。

    Attributes:
        title:    节点标题文本
        markers:  标记图标 ID 列表，如 ['priority-1', 'symbol-right']
        labels:   标签文本列表
        note:     备注文本 (纯文本，可含换行)
        link:     超链接 URL
        image:    是否有附图 (读取时为 True/False，写入时忽略)
        comments: 评论文本列表
        callouts: 标注文本列表
        children: 子节点列表
    """
    title: str = ''
    markers: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    note: Optional[str] = None
    link: Optional[str] = None
    image: bool = False
    comments: list[str] = field(default_factory=list)
    callouts: list[str] = field(default_factory=list)
    children: list[Topic] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转为可 JSON 序列化的字典 (递归)。"""
        d = {'title': self.title}
        if self.markers:
            d['markers'] = self.markers
        if self.labels:
            d['labels'] = self.labels
        if self.note:
            d['note'] = self.note
        if self.link:
            d['link'] = self.link
        if self.image:
            d['image'] = True
        if self.comments:
            d['comments'] = self.comments
        if self.callouts:
            d['callouts'] = self.callouts
        if self.children:
            d['children'] = [c.to_dict() for c in self.children]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Topic:
        """从字典创建 (递归)。兼容 xmindparser 的输出格式。"""
        children_raw = d.get('children') or d.get('topics', [])
        return cls(
            title=d.get('title', ''),
            markers=d.get('markers') or d.get('makers', []) or [],
            labels=d.get('labels', []) or [],
            note=d.get('note'),
            link=d.get('link'),
            image=bool(d.get('image')),
            comments=d.get('comments') or d.get('comment', []) or [],
            callouts=d.get('callouts') or d.get('callout', []) or [],
            children=[cls.from_dict(c) for c in children_raw],
        )


@dataclass
class Sheet:
    """工作表 (画布)。
    
    Attributes:
        title:     画布标题
        root:      根主题节点
        structure: 布局类型 (如 'org.xmind.ui.map.unbalanced')
    """
    title: str = ''
    root: Topic = field(default_factory=Topic)
    structure: str = ''

    def to_dict(self) -> dict:
        d = {'title': self.title, 'root': self.root.to_dict()}
        if self.structure:
            d['structure'] = self.structure
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Sheet:
        """从字典创建。兼容 xmindparser 输出格式。"""
        topic_data = d.get('root') or d.get('topic', {})
        return cls(
            title=d.get('title', ''),
            root=Topic.from_dict(topic_data),
            structure=d.get('structure', ''),
        )


@dataclass
class Workbook:
    """工作簿 (一个 .xmind 文件)。

    Attributes:
        sheets:      所有画布列表
        source_path: 原始文件路径 (可选)
    """
    sheets: list[Sheet] = field(default_factory=list)
    source_path: Optional[str] = None

    def to_dict(self) -> dict:
        d = {'sheets': [s.to_dict() for s in self.sheets]}
        if self.source_path:
            d['source_path'] = self.source_path
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Workbook:
        sheets_data = d.get('sheets', [])
        return cls(
            sheets=[Sheet.from_dict(s) for s in sheets_data],
            source_path=d.get('source_path'),
        )
