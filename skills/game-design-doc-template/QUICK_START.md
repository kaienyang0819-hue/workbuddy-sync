# 快速开始指南

## 核心理念

**这是一个通用的策划文档生成器，不是固定模板！**

- ✅ 根据需求动态生成内容
- ✅ 支持各类系统策划文档
- ✅ 灵活扩展新模块类型
- ✅ 统一的样式和格式规范
- ✅ 支持从 xmind 脑图提取内容生成文档

## 使用方式

### 方式1: 直接描述需求（推荐）

```
用户: 帮我生成一个装备强化系统的策划文档
AI → 分析需求 → 动态构建 → 生成文档
```

### 方式2: 提供图片/截图/脑图

```
用户: 根据这个xmind脑图生成策划文档
AI → 解析脑图 → 提取模块和规则 → 生成文档
```

### 方式3: 优化现有文档

```
用户: 在现有文档中添加XX模块
AI → 读取现有文档 → 添加新模块 → 保存
```

## 层级缩进规范

所有函数已固定列号，**调用时不需要传 col 参数**：

| 列 | 用途 | 函数 |
|----|------|------|
| B列 | 标题/单行内容 | `add_title_1/2/3` `add_single_line` |
| C列 | 规则标题 | `add_rule_title` |
| D列 | 标签/待决策项 | `add_label` `add_pending_item` |
| E列 | 正文内容 | `add_content` |

## 页签1 标准构建

```python
row = 1
row = add_title_1(ws1, row, '【系统名称】')
row = add_doc_info(ws1, row, '功能定位', '系统功能描述')
row += 1
row = add_version_table(ws1, row, [
    ('2026-03-27', 'V1.0', '初版文档', 'XXX'),
])
row += 1
row = add_doc_info(ws1, row, '文档状态', '评审中')
row += 1
row = add_people_table(ws1, row, [
    ('策划', 'XXX'), ('程序', 'XXX'), ('测试', 'XXX'),
])
row += 1
row = add_doc_info(ws1, row, '关联文档', 'xxx.md')
```

## 页签2 规则结构

```python
row = add_rule_title(ws2, row, '规则1：功能触发')
row = add_label(ws2, row, '1、规则说明')
reset_auto_number()  # ← 每个规则前重置
row = add_content(ws2, row, '第一条规则', auto_number=True)   # → 1. 第一条规则
row = add_content(ws2, row, '第二条规则', auto_number=True)   # → 2. 第二条规则
row = add_label(ws2, row, '2、交互图')
row = add_content(ws2, row, '[嵌入：流程图.png]', is_comment=True)
row = add_label(ws2, row, '3、表格配置')
row = add_content(ws2, row, '→ 配置表.xxx（页签3-表1）', is_link=True)
```

## 页签3/4 表格创建

```python
row = add_table(ws3, row, '表1-配置表名称',
    headers=['字段名', '类型', '说明', '示例值'],
    data=[
        ['field_id', 'int', '字段ID', '1'],
        ['field_name', 'string', '字段名称', '示例'],
    ])
```

## 注意事项

1. 输出路径：`G:/project_output/`
2. 规则三件套：1、规则说明 → 2、交互图 → 3、表格配置
3. `reset_auto_number()` 在每个规则的"1、规则说明"前调用
4. `add_content(auto_number=True)` 自动递增序号
5. 图片引用用 `is_comment=True`，表格引用用 `is_link=True`
6. 概述性内容用 `add_title_2` + `add_single_line`
7. 表格数据用 `add_table()` 一站式创建
