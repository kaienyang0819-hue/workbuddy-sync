# 系统策划文档标准格式生成器

提供标准化的策划文档生成API和样式规范,**支持根据实际需求动态生成不同类型系统的策划文档**。

## 核心特点

- **通用性** - 适用于各类系统策划文档
- **灵活性** - 根据需求动态构建模块
- **可扩展** - 支持新增自定义模块
- **规范性** - 统一的样式、格式、层级结构

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速使用

```python
from scripts.generate_design_doc import *

wb, ws1, ws2, ws3, ws4 = create_workbook()
for ws in [ws1, ws2, ws3, ws4]:
    setup_column_widths(ws)

# 页签1: 文档信息
row = 1
row = add_title_1(ws1, row, '【系统名称】')
row = add_doc_info(ws1, row, '功能定位', '系统功能描述')
row += 1
row = add_version_table(ws1, row, [('2026-03-27', 'V1.0', '初版', 'XXX')])
row += 1
row = add_people_table(ws1, row, [('策划', 'XXX'), ('程序', 'XXX')])

# 页签2: 设计内容（规则结构）
row = 1
row = add_title_1(ws2, row, '【系统流程】')
row = add_rule_title(ws2, row, '规则1：功能触发')
row = add_label(ws2, row, '1、规则说明')
reset_auto_number()
row = add_content(ws2, row, '触发条件', auto_number=True)   # → 1. 触发条件
row = add_content(ws2, row, '执行逻辑', auto_number=True)   # → 2. 执行逻辑
row = add_label(ws2, row, '2、交互图')
row = add_content(ws2, row, '[嵌入：流程图.png]', is_comment=True)
row = add_label(ws2, row, '3、表格配置')
row = add_content(ws2, row, '→ 配置表.xxx（页签3-表1）', is_link=True)

# 页签3: 数值表格（一站式）
row = 1
row = add_title_1(ws3, row, '【数值表格设计】')
row = add_table(ws3, row, '表1-配置表',
    headers=['字段名', '类型', '说明', '示例值'],
    data=[['field_id', 'int', '字段ID', '1']])

wb.save('G:/project_output/output.xlsx')
```

## 层级缩进规范

| 列 | 用途 | 函数 |
|----|------|------|
| B列 | 标题 / 单行内容 / 表格标题 | `add_title_1/2/3` `add_single_line` |
| C列 | 规则标题 | `add_rule_title` |
| D列 | 标签 / 待决策项 | `add_label` `add_pending_item` |
| E列 | 正文内容 | `add_content` |

**所有函数已固定列号,无需传 col 参数。**

## 标准页签结构

1. **文档信息**: `add_doc_info` + `add_version_table` + `add_people_table`
2. **设计内容**: 动态构建模块（规则结构 / 概述结构）
3. **数值表格设计**: `add_table()` 一站式创建
4. **tlog及打点设计**: `add_table()` 一站式创建

## 工作流程

```
接收需求 → 分析内容 → 动态构建模块 → 生成文档
```

## 示例文件

- `examples/create_sample_doc.py` - 基础示例
- `examples/create_panel_switch_doc.py` - 面板开关控制示例

## 许可证

MIT License
