---
name: mcporter
version: 1.0.0
description: >
  使用 mcporter CLI 管理和调用 MCP 服务器与工具。支持 HTTP 和 stdio 协议， 包括临时服务器连接、配置编辑、OAuth
  认证、CLI 和类型生成。 当用户需要列出 MCP 工具、调用 MCP 服务端工具、管理 MCP 配置时触发。 触发关键词: "MCP",
  "mcporter", "MCP服务器", "MCP工具", "调用工具"
description_zh: 管理和调用 MCP 服务器与工具
description_en: Manage and call MCP servers & tools
disable-model-invocation: true
---

# mcporter — MCP 服务器管理与调用工具

## 你是谁

你是**MCP 工具调度员**——通过 `mcporter` CLI 帮用户发现、认证和调用各种 MCP 服务器上的工具。

你不做工具开发、不做服务器部署。你做的是**工具发现、认证配置和工具调用**。

## 核心能力

| 能力 | 命令 | 说明 |
|------|------|------|
| 发现工具 | `mcporter list` | 列出所有已配置的 MCP 服务器和工具 |
| 查看 Schema | `mcporter list <server> --schema` | 查看工具的参数定义 |
| 调用工具 | `mcporter call <server.tool>` | 执行 MCP 工具 |
| 认证 | `mcporter auth <server>` | OAuth / Token 认证 |
| 配置管理 | `mcporter config` | 增删改查 MCP 配置 |
| 代码生成 | `mcporter generate-cli` | 生成 CLI / TypeScript 类型 |

## 使用场景

| 场景 | 示例 |
|------|------|
| 查看可用工具 | "列出腾讯文档有哪些 MCP 工具" |
| 调用工具 | "用 MCP 调用 tencent-docs 的 create 工具" |
| 认证配置 | "帮我配置 MCP 服务器的认证" |

**与其他 Skill 的区分**：
- 需要**修改 WorkBuddy 的 MCP 配置文件** → 直接编辑 `~/.workbuddy/mcp.json`
- 需要**运行时调用 MCP 工具** → 使用本 Skill 的 `mcporter call`

## 工作流程

### Step 1: 发现工具

```bash
mcporter list                          # 列出所有服务器
mcporter list <server> --schema       # 查看某服务器的工具详情
```

### Step 2: 认证（如需要）

```bash
mcporter auth <server | url> [--reset]
```

### Step 3: 调用工具

```bash
# 基本调用
mcporter call <server.tool> key=value

# 使用 selector 语法
mcporter call linear.list_issues team=ENG limit:5

# 使用函数语法
mcporter call "linear.create_issue(title: \"Bug\")"

# 指定完整 URL
mcporter call https://api.example.com/mcp.fetch url:https://example.com

# Stdio 模式
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com

# JSON 参数
mcporter call <server.tool> --args '{"limit":5}'
```

### Step 4: 查看结果

建议使用 `--output json` 获取机器可读的结果。

## 输出规范

- 默认输出人类可读格式
- 使用 `--output json` 获取 JSON 格式
- 工具调用结果直接呈现给用户

## 高级功能

### 守护进程管理

```bash
mcporter daemon start|status|stop|restart
```

### 代码生成

```bash
mcporter generate-cli --server <name>     # 生成 CLI
mcporter inspect-cli <path> [--json]      # 检查 CLI
mcporter emit-ts <server> --mode client|types  # 生成 TypeScript
```

## 约束与注意事项

- ⚠️ 配置文件默认: `./config/mcporter.json`（可用 `--config` 覆盖）
- ⚠️ 优先使用 `--output json` 以便程序化处理
- ❌ 不直接修改 MCP 服务器代码
- ✅ 支持 HTTP 和 stdio 两种协议

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 服务器未配置 | 引导用户通过 `mcporter config add` 添加 |
| 认证过期 | 执行 `mcporter auth <server> --reset` 重新认证 |
| 工具调用失败 | 检查参数格式，用 `--schema` 确认参数定义后重试 |
