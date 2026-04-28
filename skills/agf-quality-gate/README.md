# AGF — Agent Governance Framework
# AI 助手行为治理框架

**让 AI 助手的可靠性从"看运气"变成"看配置"。**

---

## 这是什么？

AGF 是一套 **AI 助手行为治理框架**——通过工程化的规则、钩子和工作流，确保 AI 助手的产出质量可预测、可审计、可复用。

灵感来源于 [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)（GitHub 100K+ Stars），将其"配置工程化"的思路从编码场景扩展到**所有 AI 辅助工作场景**。

## 核心组件

| 组件 | 说明 | 状态 |
|------|------|------|
| 🛡️ **agf-quality-gate** | 策划文档质量门禁——生成前提取指纹，生成后对比校验 | ✅ 可用 |
| 📋 **agf-research-workflow** | 调研标准化工作流——5阶段流程+信源管理+质量自评 | ✅ 可用 |
| 🔀 **agf-orchestrator** | 多技能编排引擎——意图路由+管道执行+断点续传 | ✅ 可用 |

## 快速开始

### 安装

AGF 的三个组件已安装为 WorkBuddy 的 user-level skills：

```
~/.workbuddy/skills/
├── agf-quality-gate/          ← 质量门禁
│   ├── SKILL.md
│   ├── scripts/
│   │   └── quality_gate.py
│   └── config/
│       └── quality_rules.yaml
├── agf-research-workflow/     ← 调研标准化
│   └── SKILL.md
└── agf-orchestrator/          ← 编排引擎
    └── SKILL.md
```

### 使用

**无需手动调用**——AGF 与 AI 助手自动集成：

- 生成策划文档后 → 自动触发 **quality-gate**
- 收到调研任务时 → 自动启动 **research-workflow**
- 多 skill 协作时 → 自动使用 **orchestrator** 编排

也可以独立使用质量门禁的 CLI：

```bash
python scripts/quality_gate.py 源文档.xlsx 产出文档.xlsx [报告目录]
```

## 团队分享

### 方式一：直接复制 skills 目录（最快）

```bash
# 导出
xcopy /E /I "%USERPROFILE%\.workbuddy\skills\agf-*" agf-export\

# 同事导入
xcopy /E /I agf-export\agf-* "%USERPROFILE%\.workbuddy\skills\"
```

### 方式二：Git 仓库管理（推荐团队使用）

```bash
# 将 AGF skills 放入团队共享仓库
git init agf-team-config
cp -r ~/.workbuddy/skills/agf-* agf-team-config/
cd agf-team-config && git add . && git commit -m "AGF v1.0"

# 同事克隆并链接
git clone <repo-url> agf-team-config
# 将目录复制或链接到 ~/.workbuddy/skills/
```

### 方式三：场景包定制

修改配置文件适配团队需求：

- `quality_rules.yaml` — 调整质量阈值（严格/宽松）
- `SKILL.md` — 调整流程规范和模板
- 添加团队特定的管道定义

## 许可证

MIT License

---

*AGF v1.0 | 2026-04-01 | Built by Kai for 凯*
