---
name: using-reqspec
description: 在每次会话开始时使用——建立如何查找和使用需求规格化技能的方法
---

# 使用 ReqSpec

## 概述

ReqSpec 是一个**纯需求文档生成**的技能系统。它帮助你从模糊的想法出发，通过结构化的流程，生成高质量的需求规格说明书。

**核心原则：只做需求文档，不写代码。**

## 技能发现

你拥有以下需求文档生成技能：

| 技能 | 何时使用 |
|------|---------|
| `reading-xlsx` | 用户提供了 xlsx/Excel 文件作为输入源，需要提取文本或图片 |
| `brainstorming` | 用户有一个模糊的想法，需要通过对话探索和澄清意图 |
| `specifying` | 想法已经清晰，需要生成结构化的需求规格文档 |
| `clarifying` | 需求文档已生成，需要消除歧义、补全边界 |
| `reviewing` | 需求文档需要质量审查，检测遗漏和问题 |
| `finalizing` | 审查通过，需要定稿归档 |

## 标准工作流

```
用户的输入（模糊想法 / Excel需求表 / PRD文档...）
      ↓
⓪ reading-xlsx（可选：提取Excel数据）
      ↓  从 xlsx 中提取文本和图片作为素材
① brainstorming（头脑风暴）
      ↓  输出：explorations/<name>.md
② specifying（需求规格化）
      ↓  输出：specs/<NNN>-<name>/requirements.md
③ clarifying（澄清补全）
      ↓  输出：specs/<NNN>-<name>/clarifications.md
④ reviewing（质量审查）
      ↓  输出：specs/<NNN>-<name>/review-report.md
⑤ finalizing（定稿归档）
      ↓  输出：specs/<NNN>-<name>/final-spec.md
```

## 如何使用技能

1. **根据用户意图匹配技能**——参考上面的表格
2. **使用 Skill 工具加载对应技能**——按需加载，不要一次加载全部
3. **严格遵循技能中的指令**——每个技能都有详细的步骤和规则
4. **技能可以跳步**——如果用户的需求已经足够清晰，可以直接从 `specifying` 开始

## 灵活性规则

- 用户可以在任何阶段停止
- 用户可以跳过 `brainstorming` 直接进入 `specifying`
- 用户可以在 `reviewing` 后返回 `specifying` 修改
- 用户可以多次运行 `clarifying` 和 `reviewing`
- **唯一不可跳过的顺序**：`finalizing` 必须在至少一次 `reviewing` 之后

## 目录结构约定

```
项目根目录/
├── explorations/           # 头脑风暴探索笔记
│   └── <name>.md
├── specs/                  # 需求规格文档
│   └── <NNN>-<name>/      # NNN = 三位数编号
│       ├── requirements.md     # 需求规格说明书
│       ├── clarifications.md   # 澄清记录
│       ├── review-report.md    # 审查报告
│       └── final-spec.md       # 最终定稿
└── specs/archive/          # 已归档的历史版本
```

## 与其他工具的关系

ReqSpec **只负责生成需求文档**。生成的需求规格说明书可以作为以下工具的输入：

- **game-feature-spec**（同级编排器）：串联 reqspec + gamedev-analysis，一站式完成需求规格化 + 控件映射 + 能力分析
- **gamedev-analysis**（同级分析包）：以需求文档为输入，完成 UMG 控件映射和通用能力分析
- **sys-code-generator**（同级代码生成包）：以需求文档集为输入，生成可执行的大厅系统 Lua 代码
- OpenSpec / Spec Kit / Superpowers 的代码实现阶段
- 任何 AI 编码助手的上下文参考
- 团队的需求评审和讨论材料

> 💡 以上四个包均位于 `lobby_sys_generator/` 大厅系统代码生成工具集中。

## 语言

所有技能提示词、模板和生成的文档均使用**简体中文**。
