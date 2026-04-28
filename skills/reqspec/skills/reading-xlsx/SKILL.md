---
name: reading-xlsx
description: 当需要从 xlsx/Excel 文件中提取文本内容或图片时使用——作为需求文档工作流的数据源读取工具
---

# 读取 Excel 文件

## 概述

提供**零外部依赖**的 xlsx 文件读取能力，从 Excel 文件中提取文本内容和内嵌图片，作为需求文档工作流（`brainstorming` / `specifying`）的**上游数据源**。

**核心原则：只读取和提取，不修改原始文件。**

## 何时使用

- 用户提供了 `.xlsx` 文件作为需求输入源（如策划表、需求表、数据表）
- 需要从 Excel 中提取特定 sheet 的文本内容
- 需要从 Excel 中提取内嵌图片（如交互图、流程图、UI 截图）
- 需要了解 xlsx 文件的结构（sheet 列表、媒体文件清单）

## 何时不使用

- 用户需要**创建或编辑** Excel 文件 → 这不是本技能的范围
- 用户提供的是 `.csv` 或纯文本表格 → 直接读取即可，无需本技能
- 用户已经把 Excel 内容以文本形式粘贴到对话中 → 无需再提取

## 工具位置

本技能附带一个 Python 脚本：

```
reqspec/skills/reading-xlsx/xlsx_tool.py
```

**零外部依赖**——仅使用 Python 标准库（`zipfile` + `xml.etree`），无需安装 `pandas`、`openpyxl` 等。

## 流程

### 第一步：确认文件和目标

向用户确认：
1. **xlsx 文件路径**
2. **需要提取的内容**：特定 sheet？全部？图片？

如果用户描述模糊（"帮我看看这个 Excel"），先运行 `list` 命令查看 sheet 列表，再与用户确认。

### 第二步：选择合适的命令

根据需要选择命令：

| 命令 | 用途 | 示例 |
|------|------|------|
| `list` | 列出所有 sheet 名称 | `python xlsx_tool.py data.xlsx list` |
| `read` | 读取指定 sheet 文本内容 | `python xlsx_tool.py data.xlsx read "装备保险"` |
| `read --all` | 读取所有 sheet | `python xlsx_tool.py data.xlsx read --all` |
| `images` | 提取 sheet 关联图片 | `python xlsx_tool.py data.xlsx images "装备保险" -o ./imgs` |
| `media` | 列出所有媒体文件 | `python xlsx_tool.py data.xlsx media` |
| `dump` | 一次性导出全部 | `python xlsx_tool.py data.xlsx dump -o ./export` |

**常用组合参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--all` | 处理所有 sheet | 否 |
| `--output / -o` | 图片输出目录 | 当前目录 |
| `--format / -f` | 输出格式：`table` / `csv` / `markdown` | `table` |
| `--max-cols` | 最大列数 | 50 |
| `--max-cell-len` | 单元格最大字符数 | 500 |

### 第三步：执行提取

使用终端执行脚本。脚本路径相对于 reqspec 目录：

```bash
python reqspec/skills/reading-xlsx/xlsx_tool.py <xlsx文件> <命令> [选项]
```

<HARD-GATE>
- 执行前必须确认 xlsx 文件路径正确且文件存在
- 对于大文件（>100 sheet），先用 `list` 确认再用 `read` 读取特定 sheet，避免一次性读取全部
- 图片提取前先用 `images` 查看清单，确认输出目录不会覆盖现有文件
</HARD-GATE>

### 第四步：处理输出

根据后续用途处理提取结果：

| 后续用途 | 处理方式 |
|---------|---------|
| 输入到 `brainstorming` | 直接将文本内容作为对话上下文提供 |
| 输入到 `specifying` | 将表格内容整理为用户故事或功能需求的素材 |
| 提取交互图 | 将图片保存到项目 output 目录，在需求文档中引用路径 |
| 数据分析 | 使用 `--format csv` 导出后进一步处理 |

### 第五步（可选）：作为 API 在脚本中使用

`xlsx_tool.py` 也可以作为 Python 模块导入使用：

```python
from xlsx_tool import XlsxReader

with XlsxReader('data.xlsx') as reader:
    # 列出 sheet
    sheets = reader.list_sheets()

    # 模糊匹配
    matched = reader.find_sheets(['保险', '装备'])

    # 读取内容
    data = reader.read_sheet('装备保险')
    for row_idx, row_data in sorted(data['data'].items()):
        print(row_idx, row_data)

    # 提取图片
    images = reader.extract_images('装备保险', './output/images')
```

## 功能清单

本工具整合了以下能力（对应原始迭代脚本）：

| 能力 | 说明 |
|------|------|
| **Sheet 文本读取** | 支持共享字符串、内联字符串、直接值三种单元格格式 |
| **合并单元格检测** | 报告合并区域，便于理解表格结构 |
| **模糊 Sheet 匹配** | 按关键词匹配 sheet 名称，无需记住全名 |
| **图片位置映射** | 解析 drawing XML，获取图片与单元格的对应关系 |
| **图片提取** | 支持按 sheet 提取关联图片，或提取全部媒体文件 |
| **多格式输出** | 支持管道分隔表、CSV、Markdown 表格三种格式 |
| **批量导出** | `dump` 命令一次性导出所有文本和图片 |

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| "文件不存在"错误 | 检查路径是否使用正确的斜杠方向（Windows 用 `\` 或 `r'...'`） |
| Sheet 名称匹配不到 | 先用 `list` 查看完整名称，注意中文全角/半角差异 |
| 图片提取为空 | 部分 xlsx 的图片在 `xl/media/` 下，部分在 `xl/drawings/media/` 下，`dump` 命令会提取全部 |
| 单元格内容截断 | 使用 `--max-cell-len 2000` 增大限制 |
| 表格列太多 | 使用 `--max-cols 100` 增大限制 |

## 语言

所有输出使用**简体中文**提示信息。
