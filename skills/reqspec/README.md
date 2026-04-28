# ReqSpec — AI 驱动的需求文档生成器

> 📋 只做需求文档，不写代码。

ReqSpec 是一个面向 AI 编码助手的**需求规格说明书生成技能系统**。它通过 5 个结构化步骤，帮助你从模糊的想法出发，生成高质量的需求文档。

## ✨ 特性

- 🧠 **苏格拉底式头脑风暴**：通过对话引导思考，而非替代思考
- 📝 **结构化需求规格化**：自动生成带用户故事和验收标准的规范文档
- 🔍 **多维度澄清**：10 大分类法扫描歧义，逐个消除
- ✅ **六维质量审查**：完整性、一致性、可测试性、无歧义性、可行性、优先级合理性
- 📦 **版本化定稿归档**：支持增量更新和历史版本管理
- 🇨🇳 **中文优先**：所有提示词、模板和生成文档均为简体中文

## 🔄 工作流

```
用户的模糊想法
      ↓
① brainstorming（头脑风暴）     → explorations/<name>.md
      ↓
② specifying（需求规格化）      → specs/<NNN>-<name>/requirements.md
      ↓
③ clarifying（澄清补全）       → specs/<NNN>-<name>/clarifications.md
      ↓
④ reviewing（质量审查）         → specs/<NNN>-<name>/review-report.md
      ↓
⑤ finalizing（定稿归档）       → specs/<NNN>-<name>/final-spec.md
```

每个步骤都可以独立使用，也可以跳步执行。唯一的约束是：定稿前必须至少审查一次。

## 🚀 安装

### Claude Code

```bash
# 方式 1：作为插件安装
claude plugin add /path/to/reqspec

# 方式 2：复制到项目中
cp -r reqspec/ your-project/.reqspec/
```

### Cursor / Windsurf / Copilot

将 `skills/` 目录下的 SKILL.md 文件添加为项目的 Agent 规则：

```
# 在 .cursorrules 或对应的配置文件中引用
@reqspec/skills/using-reqspec/SKILL.md
```

### Gemini CLI

```bash
# 将 GEMINI.md 放在项目根目录
cp reqspec/GEMINI.md your-project/GEMINI.md
```

### 手动使用

直接将技能文件内容粘贴到 AI 对话中即可使用。

## 📁 项目结构

```
reqspec/
├── skills/
│   ├── using-reqspec/              # 入口技能（会话启动自动加载）
│   │   └── SKILL.md
│   ├── brainstorming/              # 头脑风暴
│   │   ├── SKILL.md
│   │   └── spec-document-reviewer-prompt.md
│   ├── specifying/                 # 需求规格化
│   │   ├── SKILL.md
│   │   └── requirements-template.md
│   ├── clarifying/                 # 澄清补全
│   │   └── SKILL.md
│   ├── reviewing/                  # 质量审查
│   │   ├── SKILL.md
│   │   └── review-report-template.md
│   ├── reading-xlsx/               # Excel 读取
│   │   ├── SKILL.md
│   │   └── xlsx_tool.py
│   └── finalizing/                 # 定稿归档
│       └── SKILL.md
├── templates/                      # 需求模板
│   └── requirements-spec-template.md  # 游戏功能需求模板
├── hooks/                          # 会话启动钩子
│   ├── hooks.json
│   ├── run-hook.cmd
│   └── session-start
├── GEMINI.md                       # Gemini CLI 入口
└── README.md
```

## 📖 使用示例

### 场景 1：从零开始

```
用户：我想做一个团队协作的番茄钟应用

AI：[自动加载 brainstorming 技能]
    让我先了解一下你的想法...
    1. 你们团队目前是怎么管理工作节奏的？
    2. 主要的使用场景是同步协作还是异步？
    3. 最核心的一个功能是什么？

... 对话探索 ...

AI：[生成探索笔记 → 切换到 specifying → 生成需求文档]

AI：📄 需求文档已生成！
    位置：specs/001-团队番茄钟/requirements.md
    用户故事：P1 x 3, P2 x 2, P3 x 1
    待澄清：1 项
    建议下一步：运行 clarifying 消除待澄清项
```

### 场景 2：已有清晰需求

```
用户：我需要一个用户认证模块，包含注册、登录、找回密码、
      第三方登录（微信+Google），需要支持 2FA

AI：[直接加载 specifying 技能，跳过 brainstorming]
    需求描述已经很清晰，我直接生成需求文档...
```

### 场景 3：已有文档需要审查

```
用户：帮我审查一下 specs/001-用户认证/requirements.md 的质量

AI：[加载 reviewing 技能]
    📋 审查完成！
    CRITICAL: 0  HIGH: 2  MEDIUM: 3  LOW: 1
    总体评分：78/100
    详细报告：specs/001-用户认证/review-report.md
```

## 🎯 设计理念

ReqSpec 融合了三个优秀 SDD 工具的精华：

| 来源 | 借鉴的设计 |
|------|-----------|
| **Spec Kit** (GitHub) | 严格的需求质量保证（澄清分类法、"需求单元测试"、一致性分析） |
| **OpenSpec** (Fission-AI) | 灵活的制品管理（增量更新、版本归档） |
| **Superpowers** (obra) | 苏格拉底式对话 + 反合理化设计 + 技能系统 |

**关键差异**：上述工具都是"从需求到代码"的全链路方案。ReqSpec **只做需求文档**，是一个专注的、轻量的需求质量保证工具。

## 🤝 与其他工具的配合

ReqSpec 生成的 `final-spec.md` 可以作为以下工具的输入：

- **OpenSpec**：`/opsx:propose` 时引用 final-spec 作为上下文
- **Spec Kit**：直接作为 `/speckit.plan` 的输入
- **Superpowers**：作为 `writing-plans` 技能的 spec 输入
- **任何 AI 编码助手**：直接粘贴到对话中作为上下文

## 📋 与竞品对比

| 维度 | ReqSpec | OpenSpec | Spec Kit | Superpowers |
|------|---------|---------|----------|-------------|
| **范围** | ⭐ 只做需求文档 | 需求→代码全流程 | 需求→代码全流程 | 需求→代码全流程 |
| **安装** | 复制文件夹即可 | npm install | pip install | 复制文件夹 |
| **学习成本** | 5 个技能 | 11+ 命令 | 9 个命令 | 14 个技能 |
| **语言** | 🇨🇳 中文 | 🇬🇧 英文 | 🇬🇧 英文 | 🇬🇧 英文 |
| **核心价值** | 需求质量保证 | 规范管理 | 全流程治理 | 执行纪律 |

## 📄 License

MIT
