---
name: team-kb
description: >
  团队知识库管理与检索工具。提供知识库的初始化、知识点增删改查、索引管理等能力。
  作为 mygamedesignhelper 工作流的外部依赖，提供知识库检索服务（只读消费）。
  触发关键词："知识库"、"team-kb"、"知识点"、"知识检索"。
metadata:
  version: "1.0"
  date: "2026-03-30"
---

# Team-KB — 团队知识库管理工具

## 概述

Team-KB 是一个本地文件系统知识库，使用 Markdown 文件存储知识点，JSON 索引加速检索。

## 核心能力

1. **知识检索** — 通过 `kb-search.py` CLI 脚本进行关键词/标签/分类检索
2. **知识管理** — 知识点的增删改查（Markdown 文件 + 自动索引更新）
3. **索引维护** — 全量索引 `all-knowledge.json` + 标签倒排索引 `tag-index.json`

## 目录结构

```
~/.workbuddy/skills/team-kb/
├── SKILL.md                    ← 本文件
├── .kb-config.json             ← 知识库配置（repo_path 指向仓库目录）
├── scripts/
│   └── kb-search.py            ← CLI 检索脚本
└── references/
    └── kb-search-guide.md      ← 检索使用指南

<知识库仓库>/                    ← 由 .kb-config.json 的 repo_path 指定
├── .kb-config.json
├── categories/
│   ├── 技术架构/
│   ├── 业务流程/
│   ├── 产品设计/
│   ├── 项目管理/
│   └── 通用知识/
├── _index/
│   ├── all-knowledge.json
│   └── tag-index.json
└── _drafts/pending-review/
```

## 使用方式

```powershell
# 关键词搜索（默认 Top-5）
python ~/.workbuddy/skills/team-kb/scripts/kb-search.py search "关键词"

# 按标签过滤
python ~/.workbuddy/skills/team-kb/scripts/kb-search.py search --tags "标签1,标签2"

# 关键词 + 分类过滤
python ~/.workbuddy/skills/team-kb/scripts/kb-search.py search "关键词" --category "分类名"

# 获取单条知识点摘要
python ~/.workbuddy/skills/team-kb/scripts/kb-search.py get KB-001

# 获取单条知识点全文
python ~/.workbuddy/skills/team-kb/scripts/kb-search.py get KB-001 --full
```
