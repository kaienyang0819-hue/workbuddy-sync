# XMind Toolkit - AI 友好的 XMind 双向转换工具包

> **设计目标**: 让 AI Agent 能够无损地 **读取** 和 **生成** XMind 思维导图文件。

## 架构总览

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  .xmind 文件 │────▶│   reader    │────▶│  结构化 .md   │
└─────────────┘     └─────────────┘     └──────────────┘
                          │                      │
                          ▼                      ▼
                    ┌───────────┐          ┌───────────┐
                    │   model   │◀────────▶│ md_parser │
                    │ (数据模型) │          └───────────┘
                    └───────────┘
                          │
                          ▼
┌─────────────┐     ┌─────────────┐
│  .xmind 文件 │◀────│   writer    │
└─────────────┘     └─────────────┘
```

## 模块说明

| 模块 | 文件 | 职责 |
|------|------|------|
| **model** | `model.py` | 统一数据模型 (Topic / Sheet / Workbook) |
| **markers** | `markers.py` | 标记图标双向映射 (XMind ID ↔ Emoji) |
| **reader** | `reader.py` | XMind → 数据模型 → 结构化 Markdown |
| **md_parser** | `md_parser.py` | 结构化 Markdown → 数据模型 |
| **writer** | `writer.py` | 数据模型 → XMind 文件 |
| **md2xmind** | `md2xmind.py` | 主入口: Markdown → XMind 一键转换 |

## 快速使用

### 安装依赖

```bash
pip install xmind xmindparser
```

### Markdown → XMind

```bash
# 命令行
python md2xmind.py 策划案_结构化.md 策划案.xmind

# Python API
from xmind_toolkit.md_parser import parse_markdown_file
from xmind_toolkit.writer import write_xmind

workbook = parse_markdown_file('策划案_结构化.md')
write_xmind(workbook, '策划案.xmind')
```

### XMind → Markdown

```bash
# 命令行
python -m xmind_toolkit.reader 策划案.xmind 策划案_结构化.md

# Python API
from xmind_toolkit.reader import xmind_to_markdown

text = xmind_to_markdown('策划案.xmind', '策划案_结构化.md')
```

### 数据模型操作 (高级)

```python
from xmind_toolkit.model import Topic, Sheet, Workbook
from xmind_toolkit.writer import write_xmind

# 用代码构建思维导图
root = Topic(
    title='项目规划',
    children=[
        Topic(title='需求分析', markers=['priority-1']),
        Topic(title='技术方案', markers=['priority-2'], children=[
            Topic(title='前端', labels=['React']),
            Topic(title='后端', labels=['Python']),
        ]),
        Topic(title='测试验证', markers=['task-start']),
    ]
)

workbook = Workbook(sheets=[Sheet(title='规划', root=root)])
write_xmind(workbook, '项目规划.xmind')
```

## AI 友好设计

### 1. 结构化 Markdown 格式

输出格式对 AI 来说清晰可解析:

```
# 根节点标题
├── 一级子节点  【🔴P1】
│   ├── 二级子节点  【🔗 https://...  |  📷 [附图]】
│   │   📝 这是备注内容
│   └── 另一个二级节点  【✅  |  标签: 设计, 重要】
│       💬 这是评论
└── 最后一个一级节点
```

### 2. 元数据约定

| 符号 | 含义 | 示例 |
|------|------|------|
| `🔴P1`~`🟣P6` | 优先级 | `【🔴P1】` |
| `✅` / `❌` / `⚠️` / `❓` | 状态符号 | `【✅】` |
| `✅完成` / `🔄进行中` / `🔲待开始` | 任务进度 | `【✅完成】` |
| `⭐` / `🌟` | 星标 | `【⭐】` |
| `👍` | 点赞/推荐 | `【👍】` |
| `🔗 URL` | 超链接 | `【🔗 https://...】` |
| `📷 [附图]` | 有图片 | `【📷 [附图]】` |
| `标签: a, b` | 标签 | `【标签: 设计, 重要】` |
| `📝 文本` | 备注 | 单独一行 |
| `💬 文本` | 评论 | 单独一行 |
| `💡 标注: 文本` | 标注 | 单独一行 |

### 3. 数据模型 JSON 序列化

所有数据模型都支持 `to_dict()` / `from_dict()`:

```python
import json
workbook = parse_markdown_file('test.md')
print(json.dumps(workbook.to_dict(), ensure_ascii=False, indent=2))
```

## 与原 xmind_reader.py 的关系

本工具包是对原 `xmind_reader.py` 的全面重构和扩展:

| 改进 | 原版 | 新版 |
|------|------|------|
| 架构 | 单文件、硬编码路径 | 模块化、参数化 |
| 方向 | 仅读取 (XMind→MD) | 双向 (XMind↔MD) |
| 数据模型 | 直接操作字典 | 类型化 dataclass |
| 标记映射 | 内联字典 | 独立模块、双向映射 |
| AI 适配 | 输出格式固定 | 清晰的 API、JSON 序列化 |
| 格式兼容 | — | 100% 兼容原输出格式 |
