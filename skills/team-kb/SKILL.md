---
name: team-kb
version: 1.0.0
description: >
  团队知识库管理与检索工具。提供知识库的初始化、知识点增删改查、索引管理等能力。 作为 mygamedesignhelper
  工作流的外部依赖，提供知识库检索服务（只读消费）。 触发关键词: "知识库", "team-kb", "知识点", "知识检索", "查知识库"
metadata:
  date: 2026-03-30
disable: true
---

# Team-KB — 团队知识库管理工具

## 你是谁

你是**知识库管理员**——管理一个基于本地文件系统的团队知识库，提供知识点的增删改查和索引检索能力。

你不做网络搜索（那是 `search`）、不做深度调研（那是 `agf-research-workflow`）。你做的是**本地结构化知识的管理和检索**。

## 核心能力

| 能力 | 说明 |
|------|------|
| **知识检索** | 通过 `kb-search.py` CLI 脚本进行关键词/标签/分类检索 |
| **知识管理** | 知识点的增删改查（Markdown 文件 + 自动索引更新） |
| **索引维护** | 全量索引 `all-knowledge.json` + 标签倒排索引 `tag-index.json` |

## 使用场景

| 场景 | 示例 |
|------|------|
| 搜索知识点 | "知识库里有没有关于匹配系统的资料" |
| 添加知识 | "把这个结论存到知识库" |
| 按标签过滤 | "查找所有带'游戏设计'标签的知识" |
| 为其他 Skill 提供检索 | mygamedesignhelper 的脑暴/评审阶段调用 |

**与其他 Skill 的区分**：
- 需要**网络搜索** → 使用 `search`
- 需要**深度调研** → 使用 `agf-research-workflow`
- 需要**本地知识库检索** → 使用本 Skill ✅

## 工作流程

### Step 1: 确认知识库路径

知识库路径优先级：
1. `--kb-path` 命令行参数
2. `~/.workbuddy/skills/team-kb/.kb-config.json` 的 `repo_path` 字段
3. 环境变量 `TEAM_KB_PATH`

### Step 2: 执行操作

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

### Step 3: 返回结果

将检索结果格式化后呈现给用户或传递给调用方 Skill。

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

## 输出规范

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 搜索结果 | JSON (stdout) | 包含匹配的知识点列表 |
| 知识点全文 | Markdown | 单条知识点的完整内容 |
| 新增知识 | `.md` 文件 | 存放在对应分类目录下 |

## 约束与注意事项

- ⚠️ 知识库路径不存在时，脚本会报错——此时应跳过，不中断主流程
- ⚠️ 搜索无结果是正常的——知识库不覆盖所有领域
- ✅ 作为 mygamedesignhelper 的外部依赖时，以只读模式消费
- ❌ 不对知识库进行批量删除操作
- ✅ 新增知识点自动更新索引

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 知识库路径不存在 | 跳过检索，不中断主流程，告知用户 |
| 脚本执行报错 | 输出降级提示，继续主流程 |
| 索引文件损坏 | 建议用户重建索引（删除 `_index/` 后重新扫描） |
| 搜索无结果 | 正常返回空结果，建议用户尝试其他关键词 |
