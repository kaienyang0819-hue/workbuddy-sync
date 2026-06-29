---
name: knowledge-entry
description: 知识入库 — 将KM文章、网页、手动内容结构化写入个人知识库
agent_created: true
version: "1.0"
triggers:
  - "入库"
  - "知识库"
  - "knowledge"
  - "存到知识库"
  - "记一下"
  - "这个值得记录"
---

# 知识入库 Skill

将外部信息结构化写入 `.workbuddy/knowledge/` 知识库，支持 Obsidian 双链语法。

## 知识库路径

```
g:/gpt_test/.workbuddy/knowledge/
```

## 分类目录

| 目录 | 关键词匹配 |
|------|-----------|
| `00-inbox/` | 默认暂存，不确定分类时放这里 |
| `01-ai-gaming/` | NPC、游戏AI、剧情生成、关卡设计、美术辅助、游戏测试、game AI |
| `02-llm-tech/` | LLM、大模型、RAG、Agent、Prompt、微调、推理、embedding、向量 |
| `03-competitive/` | 竞品、公司动态、产品拆解、技术栈对比、市场份额 |
| `04-game-design/` | 策划、数值、系统设计、玩家心理、关卡、战斗、经济系统 |
| `05-industry/` | 投融资、政策、学术、会议、趋势、行业报告 |

## 三种输入模式

### 模式1：KM文章URL

当用户提供 KM 链接时：

1. 调用 `mcp__km__show-article` 获取文章详情（`full_content: true`）
2. 提取：标题、作者、阅读/点赞/收藏数据、AI摘要、正文
3. 根据内容自动判断分类
4. 使用 `templates/km-article.md` 模板生成条目
5. 写入对应分类目录

### 模式2：网页URL

当用户提供非KM的网页链接时：

1. 调用 `WebFetch` 获取网页内容
2. 提取标题、核心内容
3. 自动生成摘要和标签
4. 使用 `templates/knowledge-entry.md` 模板
5. 写入对应分类目录

### 模式3：手动内容

当用户直接粘贴文本内容时：

1. 分析内容主题
2. 自动生成标题（如果用户没给）、摘要、标签
3. 使用 `templates/knowledge-entry.md` 模板
4. 写入对应分类目录

## 执行流程

### Step 1: 获取内容

根据输入类型调用对应的获取方式（KM API / WebFetch / 直接使用用户文本）。

### Step 2: 分析与分类

阅读内容后判断：
- 属于哪个分类目录（参考关键词匹配表）
- 如果跨多个分类，选最核心的那个，在条目中用 `related` 字段关联其他分类
- 如果不确定，放入 `00-inbox/`

### Step 3: 提取标签

从内容中自动提取标签，规则：
- 必须包含至少一个一级标签（领域级）
- 可选包含二级标签（主题级）
- KM文章额外加 `#src:km`，网页加 `#src:web`，手动加 `#src:manual`
- 标签用英文小写，多词用连字符：`#ai-gaming` `#prompt-engineering`

### Step 4: 生成摘要

**核心洞察**（必须）：用1-3句话概括这篇文章最核心的价值，以及对凯当前工作的启发。站在游戏策划+AI产品经理的视角判断。

**关键要点**：提取3-5个关键要点，每个要点用一句话概括。

**我的判断**：基于凯的工作背景（AI NPC群聊设计、Harness Engineering、AI+游戏落地、大模型产品化），给出价值判断和可信度评级。

### Step 5: 生成文件名

格式：`YYYY-MM-DD-简短标题.md`
- 日期用入库当天日期
- 标题用中文，简短概括（10字以内）
- 示例：`2026-06-24-WorkBuddy知识库搭建.md`

### Step 6: 写入文件

将生成的条目写入对应分类目录。

### Step 7: 更新索引

更新 `INDEX.md` 底部的统计信息（总条目数、最近更新时间）。

### Step 8: 反馈

向用户报告：
- 条目已入库到哪个目录
- 自动生成的标签
- 核心洞察的一句话概括
- 提示可以用 Obsidian 打开查看关系图谱

## 条目格式示例

```markdown
---
title: "AI NPC对话系统的三种架构方案"
date: 2026-06-24
tags: ["ai-gaming", "npc", "llm-tech", "dialogue-system", "src:km"]
source: "km"
source_url: "https://km.woa.com/articles/show/123456"
category: "ai-gaming"
project: ""
km_author: "zhangsan"
km_reads: 2000
km_likes: 80
confidence: 3
created_by: workbuddy
---

# AI NPC对话系统的三种架构方案

> **KM原文**: [链接](https://km.woa.com/articles/show/123456)
> **作者**: zhangsan | **阅读**: 2000 | **点赞**: 80

## 核心洞察

> 这篇文章对比了三种NPC对话架构（规则驱动/LLM直出/混合方案），
> 其中混合方案（规则约束+LLM生成）的思路和我们策略大模型NPC的方向一致，
> 可以参考他们的prompt约束设计。

## 关键要点

1. 纯LLM直出的NPC对话在一致性上表现差，需要规则层约束
2. 混合方案用System Prompt设定角色边界，用RAG注入记忆
3. 评测指标：角色一致性、响应延迟、玩家满意度

## 我的判断

- **对我的价值**: ★★★★
- **可信度**: ★★★
- **适用场景**: NPC群聊设计中的对话一致性问题
- **下一步**: 参考他们的prompt约束模板，优化我们的NPC System Prompt

## 关联条目

- [[2026-06-20-策略大模型NPC设计]]
- [[2026-06-15-RAG在游戏NPC中的应用]]

## 行动项

- [ ] 优化NPC System Prompt的角色约束层
- [ ] 测试混合方案的响应延迟

---

*来源: KM | 入库时间: 2026-06-24*
```

## 批量入库

当用户说"把这几篇都入库"时：
- 逐篇处理，每篇独立生成条目
- 最后汇总报告所有入库结果

## 与KM日报联动

当用户在查看KM AI日报时说"这篇入库"：
- 直接从日报数据中提取文章信息
- 如果日报中有AI摘要，直接使用
- 标记来源为 `#src:km` + `#src:daily-report`

## 注意事项

- 不要编造内容，只基于实际获取到的信息写条目
- 标签保持一致性，复用已有标签而非创建近义词
- 每次入库后提醒用户可以用 Obsidian 打开查看
- frontmatter 中的 tags 用 JSON 数组格式
