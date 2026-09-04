---
name: aibox
description: "AIBox 核心技能，覆盖 skill 全生命周期与平台资源查询。能力包括：① 从远端搜索/下载/安装/更新 skill；② 对 skill 做安全扫描与质量评分；③ 查询平台资源——知识库（含内容检索）、MCP Server、Workflow、CLI 工具、A2A Agent；④ 把本地文档（Markdown/PDF/Word/Excel/Text）批量导入 TRAG 向量知识库或清空 collection；⑤ 管理鉴权 Token（X-AMS-TOKEN / TAI-TOKEN）；⑥ 安装使用上报 Hooks。当用户提到 aibox、安装/搜索/更新 skill、skill 商店/市场/列表、检查 skill 安全或质量、生成/编排工作流、查询或搜索知识库/MCP Server/Workflow/CLI 工具/Agent、把文档导入 TRAG/知识库、清空 collection、设置/配置 token（AMS/太湖）、安装 hooks 等任意意图时，应主动使用本技能——即使用户没有明确点名 aibox。"
metadata:
  author: AIBox
  version: 1.5.0
  category: platform
  tags: [skill-management, skill-download, skill-quality, skill-orchestration, knowledge-search, mcp-server, workflow-query, token-auth]
---

> 说明：下文中的 `{SKILL_DIR}` 指本技能的安装目录（即本 `SKILL.md` 所在目录），执行脚本时请替换为实际路径。

## 能力路由

先根据用户意图定位到对应章节，再按该章节的指引操作：

| 用户意图 | 对应章节 |
|---------|---------|
| 安装 / 搜索 / 更新 skill | Skill 下载与安装 |
| 安装使用上报 Hooks | Hooks 安装 |
| 设置 / 配置鉴权 token | Token 鉴权设置 |
| 检查 skill 安全 / 质量 | Skill 安全和质量检测 |
| 查询 MCP / 知识库 / Workflow / CLI / Agent | 平台资源查询 |
| 文档导入 / 清空 TRAG | Markdown 文档导入 / 清空 TRAG |

## 前置检查

⚠️ 执行任何操作前，先检查 Hooks 是否已安装（用于使用数据上报与质量分析）；若未安装，请先按下文「Hooks 安装」章节完成安装。

## Skill 下载与安装

### 基本用法（完整的用法可以通过 `-h` 查看）

```bash
# 列出远端所有可用 skill
python3 {SKILL_DIR}/scripts/download_skill.py --list

# 搜索 skill
python3 {SKILL_DIR}/scripts/download_skill.py --search "faas"

# 安装 skill
python3 {SKILL_DIR}/scripts/download_skill.py --install <skill_name>
```

### 参数说明

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--list`, `-l` | - | 列出远端所有可用 skill |
| `--search`, `-s` | - | 按关键词搜索 skill |
| `--install`, `-i` | - | 下载并安装指定 skill |
| `--skills-dir` | 按检测到的 Agent 取 `<项目根>/.codebuddy/skills` 等 | 本地 skills 安装目录（默认随 Agent 类型：`.codebuddy` / `.workbuddy` / `.claude` / `.cursor` / `.openclaw`） |

### 安装流程

1. **检查前置依赖** — 某些 skill 依赖其他 skill 才能正常工作。检查前置 skill 是否已安装，未安装则自动下载。
2. **版本检查与确认** — 如果本地已有同名 skill 且远端有新版本，提示用户确认是否覆盖（交互模式），或通过 `--force` 跳过确认。
3. **安全安装** — 安装前自动备份原有 skill，失败时自动恢复，确保不会丢失用户已有配置。
4. **包验证** — zip 包解压到临时目录后，验证包含 `SKILL.md` 才移动到目标位置，防止安装损坏的包。
5. **列表展示** — 使用 `--list` 参数时，通过 Markdown 表格展示所有 skill 的 `name, description, version, 是否已安装/可更新`。

### 远端未找到 skill 的处理

如果远端 API 返回 404 或未找到指定 skill_name：

1. **提醒用户**：告知可以从 https://skills.sh/ 搜索第三方 skill
   > ⚠️ 仅提醒用户，不要自动下载第三方 skill
2. **用户同意后**：
   - 确保 `find-skills` skill 已安装：`python3 {SKILL_DIR}/scripts/download_skill.py --install find-skills`
   - 使用 `find-skills` 搜索相似的 skill，将结果展示给用户
   - 用户选择后，安装对应的 skill
3. **用户拒绝**：直接返回，不做额外操作

---

## Hooks 安装

### 功能描述

基于 Code Hooks 机制实现的自动化上报功能，**兼容 codebuddy / workbuddy / claude code / cursor** 等 Agent 工具。
Hooks 会在工具调用前后、用户提交 prompt、会话结束等关键节点自动触发，用于收集 skill 使用数据和质量分析。

### ⚠️ 安装注意事项
- 支持系统 macOS、Linux 和 Windows
- macOS/Linux 安装路径：安装到全局目录 `~/.codebuddy/hooks/`、`~/.workbuddy/hooks/`、`~/.claude/hooks/` 或 `~/.cursor/hooks/`
- Windows 安装路径：安装到全局目录 `%USERPROFILE%\.codebuddy\hooks\`、`%USERPROFILE%\.workbuddy\hooks\`、`%USERPROFILE%\.claude\hooks\` 或 `%USERPROFILE%\.cursor\hooks\`
- hooks 上报支持 codebuddy / workbuddy / claude code / cursor，其他工具禁止安装 hooks；openclaw 的 hooks 机制不同（进程内 TS 模块，非命令行脚本），不支持 hooks 上报，仅支持 token 存储（见下文 Token 鉴权设置）。
- Agent 类型自动判断优先级：环境变量（`WORKBUDDY_PROJECT_DIR` / `CODEBUDDY_PROJECT_DIR` / `CLAUDE_PROJECT_DIR`）→ 本 skill 安装路径包含的配置目录名（`/.workbuddy/` 等，workbuddy 下最可靠）→ `pwd` 项目路径包含的配置目录名。

### 目标目录判定

根据当前检测到的 Agent 类型（通过环境变量和 skill 安装路径自动判断）和操作系统，确定目标目录：

**macOS / Linux：**

| Agent 类型 | hooks 目录 | settings 文件 |
|-----------|-----------|--------------|
| codebuddy | `~/.codebuddy/hooks/` | `~/.codebuddy/settings.json` |
| workbuddy | `~/.workbuddy/hooks/` | `~/.workbuddy/settings.json` |
| claude | `~/.claude/hooks/` | `~/.claude/settings.json` |
| cursor | `~/.cursor/hooks/` | `~/.cursor/hooks.json` |

**Windows：（先检查 `%USERPROFILE%` 是否存在，如果不存在则退出安装）**

| Agent 类型 | hooks 目录 | settings 文件 |
|-----------|-----------|--------------|
| codebuddy | `%USERPROFILE%\.codebuddy\hooks\` | `%USERPROFILE%\.codebuddy\settings.json` |
| workbuddy | `%USERPROFILE%\.workbuddy\hooks\` | `%USERPROFILE%\.workbuddy\settings.json` |
| claude | `%USERPROFILE%\.claude\hooks\` | `%USERPROFILE%\.claude\settings.json` |
| cursor | `%USERPROFILE%\.cursor\hooks\` | `%USERPROFILE%\.cursor\hooks.json` |

> ⚠️ Cursor 的配置文件是 `hooks.json`（`version: 1` 格式，事件名为 `beforeShellExecution` / `afterFileEdit` / `beforeSubmitPrompt` 等小驼峰风格），与 codebuddy / workbuddy / claude 的 `settings.json` 格式不同，合并时不要混用。`aibox_hooks.py` 已内置 Cursor 事件名映射，模板中的 command 无需特殊处理。

### 安装流程

1. **检查是否已安装** — 查看目标 hooks 目录下是否已存在 `aibox_hooks.py`。如果已安装，直接返回，避免重复操作。
2. **环境自检** — 执行自检命令验证脚本在本机是否能正常运行（检查 Python 版本、依赖库、网络连通性等）。这一步确保安装后 hooks 能真正工作。
   - macOS/Linux：`python3 {SKILL_DIR}/references/aibox_hooks.py test`
   - Windows：`py -3 {SKILL_DIR}/references/aibox_hooks.py test`
3. **自检通过 → 复制脚本** — 将 `aibox_hooks.py` 复制到目标 hooks 目录，已存在则覆盖（新版本可能修复了问题）。
4. **自检失败 → 跳过安装** — 输出失败原因，跳过 hooks 安装。不强制安装无法运行的脚本，避免后续每次操作都报错。
5. **判断 Agent 类型和操作系统，选择配置模板**：
   - macOS/Linux + codebuddy → `{SKILL_DIR}/references/settings.codebuddy.json`
   - macOS/Linux + workbuddy → `{SKILL_DIR}/references/settings.workbuddy.json`
   - macOS/Linux + claude → `{SKILL_DIR}/references/settings.claude.json`
   - macOS/Linux + cursor → `{SKILL_DIR}/references/settings.cursor.json`
   - Windows + codebuddy → `{SKILL_DIR}/references/settings.codebuddy.windows.json`
   - Windows + workbuddy → `{SKILL_DIR}/references/settings.workbuddy.windows.json`
   - Windows + claude → `{SKILL_DIR}/references/settings.claude.windows.json`
   - Windows + cursor → `{SKILL_DIR}/references/settings.cursor.windows.json`
6. **合并 settings** — 将模板内容与目标 settings 文件合并（codebuddy / workbuddy / claude 合并到 `settings.json`，cursor 合并到 `hooks.json`）。如果目标文件已存在且包含当前 hooks 配置则跳过，没有则创建并写入或者合并，这一步注册了 hooks 的触发事件。
7. **安装完成** — hooks 设置完毕，后续操作会自动触发上报。

### openclaw 说明

OpenClaw 的 hooks 是进程内运行的 JS/TS 模块（`HOOK.md` + `handler.ts` 清单结构），与基于 stdin/stdout 的命令行 hooks 脚本不兼容，因此**不支持**自动上报 hooks 安装。如需在 openclaw 环境使用 AIBox 的 token 鉴权，可通过 `auth.py --agent openclaw` 指定存储位置（见下文）。

---

## Token 鉴权设置

为访问需要鉴权的 AIBox 后端接口，可以在本地保存两类 Token，所有 `scripts/` 下的请求会自动带上这两个 Token（不存在或为空则不带）：

| Token 类型 | 用途 | Header 名 |
|-----------|------|-----------|
| `X-AMS-TOKEN` | 用户增值部 Token | `X-AMS-TOKEN` |
| `TAI-TOKEN`   | 太湖 Token      | `TAI-TOKEN`   |

### 触发规则

当用户表达「设置 token / 配置 token / 填 token / 登录 aibox」等意图时：

1. **先询问 Token 类型** — 明确是 `X-AMS-TOKEN`（用户增值部 token）还是 `TAI-TOKEN`（太湖 token）。
2. **获取 Token 值** — 用户提供后，调用 `auth.py set` 保存。
3. **确认保存结果** — 展示保存路径（不回显 token 值）。

### 基本用法（完整的用法可以通过 `-h` 查看）

```bash
# 设置 X-AMS-TOKEN（用户增值部 Token）
python3 {SKILL_DIR}/scripts/auth.py set --type X-AMS-TOKEN --token <token_value>

# 设置 TAI-TOKEN（太湖 Token）
python3 {SKILL_DIR}/scripts/auth.py set --type TAI-TOKEN --token <token_value>

# 显式指定 Agent 类型（codebuddy / workbuddy / claude / cursor / openclaw），默认自动判断
python3 {SKILL_DIR}/scripts/auth.py set --type TAI-TOKEN --token <token_value> --agent workbuddy

# 查看已保存的 token 类型（默认脱敏显示）
python3 {SKILL_DIR}/scripts/auth.py list

# 删除指定类型的 token
python3 {SKILL_DIR}/scripts/auth.py delete --type X-AMS-TOKEN

# 清空所有 token
python3 {SKILL_DIR}/scripts/auth.py clear
```

### 存储位置与格式

- **存储路径**（存放于各 Agent hooks 目录下的 `aibox.secret` 文件，按检测到的 Agent 类型自动选择）：

  | Agent 类型 | macOS / Linux | Windows |
  |-----------|---------------|---------|
  | codebuddy | `$HOME/.codebuddy/hooks/aibox.secret` | `%USERPROFILE%\.codebuddy\hooks\aibox.secret` |
  | workbuddy | `$HOME/.workbuddy/hooks/aibox.secret` | `%USERPROFILE%\.workbuddy\hooks\aibox.secret` |
  | claude | `$HOME/.claude/hooks/aibox.secret` | `%USERPROFILE%\.claude\hooks\aibox.secret` |
  | cursor | `$HOME/.cursor/hooks/aibox.secret` | `%USERPROFILE%\.cursor\hooks\aibox.secret` |
  | openclaw | `$HOME/.openclaw/hooks/aibox.secret` | `%USERPROFILE%\.openclaw\hooks\aibox.secret` |

  Windows 下先检查 `%USERPROFILE%` 是否存在，如果不存在则退出设置。Agent 类型自动判断优先级见「Hooks 安装」章节，也可通过 `--agent` 显式指定。

- **文件格式**：每行一条 base64 编码条目，解码后为 `<token类型>##<token值>`，相同类型覆盖。

  示例（解码前）：
  ```
  WC1BTVMtVE9LRU4jI2FiYzEyMw==
  VEFJLVRPS0VOIyN4eXo0NTY=
  ```
  对应解码后：
  ```
  X-AMS-TOKEN##abc123
  TAI-TOKEN##xyz456
  ```

### 请求头注入规则

`download_skill.py` 和 `search.py` 会在每次请求前自动读取 `aibox.secret`，将其中 **非空** 的 token 以对应类型作为 header 加入：
- 仅设置 `X-AMS-TOKEN` → 请求头只带 `X-AMS-TOKEN`
- 仅设置 `TAI-TOKEN`  → 请求头只带 `TAI-TOKEN`
- 两个都设置          → 请求头同时带 `X-AMS-TOKEN` 和 `TAI-TOKEN`
- 都未设置 / 值为空   → 不附加 token 头

## Skill 安全和质量检测（需要输入 skill_name 或多个 skill_name）

安装第三方 skill 前进行安全和质量检测，可以避免引入恶意代码或低质量 skill 影响项目安全与稳定。

### 前置条件

以下三个 skill 各司其职，缺一不可，如果未安装，会自动下载：
- `tca-skill` — 负责安全扫描（敏感信息、危险操作等）
- `skill-quality-inspector` — 负责质量评分（代码规范、文档完整性等）
- `skill-creator` — 负责检查是否符合 skill 编写规范（结构、frontmatter 等）

### 执行流程

1. **确保前置 skill 就绪** — 逐个检查上述三个 skill，未安装的自动下载安装。
2. **安全扫描** — 调用 `tca-skill` 对目标 skill 进行安全扫描，检测敏感信息、危险操作等安全风险。
3. **质量检查** — 调用 `skill-quality-inspector` 对目标 skill 进行质量检查，输出质量评分。
4. **规范检查** — 调用 `skill-creator` 检查目标 skill 是否符合 skill 编写规范。
5. **汇总报告** — 综合以上结果，生成最终报告和修改建议：

```
## skill: xxx
- 评分：100
- 必须修改：xx
- 建议修改：xx
- 安全问题：无

## skill: xxx
...
```

---

## 平台资源查询

查询 AIBox 平台的 MCP Server、知识库、Workflow、CLI 工具、A2A Agent 等资源，如果用户询问，可以通过组合如下命令查询：

### 基本用法（完整的用法可以通过 `-h` 查看）

```bash
# 查询 MCP Server 列表
python3 {SKILL_DIR}/scripts/search.py mcp

# 按关键词搜索 MCP Server
python3 {SKILL_DIR}/scripts/search.py mcp --keyword "git"

# 查询知识库列表
python3 {SKILL_DIR}/scripts/search.py knowledge

# 按关键词过滤知识库
python3 {SKILL_DIR}/scripts/search.py knowledge --keyword "文档"

# 搜索知识库内容（需指定知识库 ID 和查询内容）
python3 {SKILL_DIR}/scripts/search.py knowledge --id <project_id> --query "如何部署"

# 查询 Workflow 列表
python3 {SKILL_DIR}/scripts/search.py workflow

# 查看 Workflow 详情（下载 SKILL.md）
python3 {SKILL_DIR}/scripts/search.py workflow --id <project_id>

# 查询 CLI 工具列表
python3 {SKILL_DIR}/scripts/search.py cli

# 按关键词搜索 CLI 工具
python3 {SKILL_DIR}/scripts/search.py cli --keyword "deploy"

# 查看 CLI 工具详情（含下载地址、文件列表、README）
python3 {SKILL_DIR}/scripts/search.py cli --id <tool_name>

# 查询 A2A Agent 列表
python3 {SKILL_DIR}/scripts/search.py agent

# 按关键词搜索 Agent
python3 {SKILL_DIR}/scripts/search.py agent --keyword "translate"

# 查看 Agent 详情（含实时探测连通性）
python3 {SKILL_DIR}/scripts/search.py agent --id <agent_name>

# 以 JSON 格式输出
python3 {SKILL_DIR}/scripts/search.py mcp --json
```

### 参数说明

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `resource` (位置参数) | - | 资源类型: `mcp` / `knowledge` / `workflow` / `cli` / `agent` |
| `--id` | - | 资源 ID（知识库/Workflow 的 project_id、CLI 工具名、Agent 名称） |
| `--query`, `-q` | - | 知识库搜索内容（需配合 `--id` 使用） |
| `--keyword`, `-k` | - | 按关键词过滤列表（模糊匹配名称或描述） |
| `--limit` | 5 | 知识库搜索返回的最大结果数 |
| `--base-url` | 环境变量或默认地址 | API 基础地址（覆盖环境变量） |
| `--json` | false | 以 JSON 格式输出原始数据 |

---

## Markdown 文档导入 / 清空 TRAG

当用户要求"把本地文档导入知识库 / 导入 TRAG / 导入 collection / markdown 入库"，或要求"清空 collection / 清理 TRAG / 删除 collection 全部内容"时使用。

### 基本用法（完整的用法可以通过 `-h` 查看）

```bash
# 导入指定目录到已有 collection
python3 {SKILL_DIR}/scripts/import_md_to_trag.py \
    --dir /path/to/docs \
    --collection col-xxxxxx

# 只导入 Markdown 和 PDF
python3 {SKILL_DIR}/scripts/import_md_to_trag.py \
    --dir /path/to/docs \
    --collection col-xxxxxx \
    --ext md pdf

# 清空指定 collection 的全部内容（不导入，需交互输入集合编码确认）
python3 {SKILL_DIR}/scripts/import_md_to_trag.py \
    --clean \
    --collection col-xxxxxx
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--dir` | 必填 | 本地文档目录（递归扫描） |
| `--collection` | 必填 | TRAG collection code（如 col-xxxxxxxx） |
| `--base-url` | 环境变量或 http://ai.px.woa.com | AIBox 后端地址 |
| `--chunk-size` | 1500 | 分块大小，字符数 |
| `--chunk-overlap` | 200 | 分块重叠字符数 |
| `--encoding` | utf-8 | 文本文件编码 |
| `--ext` | 全部白名单 | 限定扫描扩展名（不含点号，可多个） |
| `--dry-run` | false | 只扫描/过滤/转换/分块，不调用后端 |
| `--delay` | 0.2 | chunk 间请求间隔秒数 |
| `--clean` | false | 清空 `--collection` 指定集合的全部内容（不导入） |
| `--yes` / `-y` | false | 清空时跳过交互确认（危险） |

### 支持的文件类型（白名单）

| 类型 | 扩展名 | 处理方式 |
|------|--------|----------|
| Markdown | `.md` / `.markdown` | 原样读取 |
| Text | `.txt` | 原样读取 |
| PDF | `.pdf` | markitdown 转 Markdown |
| Word | `.doc` / `.docx` | markitdown 转 Markdown |
| Excel | `.xls` / `.xlsx` | markitdown 转 Markdown |

不在白名单内的文件（图片、音视频、压缩包、二进制等）一律跳过并输出提醒：
```
[跳过] 不支持的文件类型 (.png): images/demo.png
```

> PDF/Word/Excel 转换需要 `markitdown`：`pip install markitdown`

---

## 文件目录

```
.codebuddy/skills/aibox/
├── SKILL.md                                # 本文件 — skill 入口说明
├── scripts/
│   ├── download_skill.py                   # Skill 下载与安装脚本
│   ├── search.py                           # 平台资源查询脚本（MCP/知识库/Workflow/CLI/Agent）
│   ├── auth.py                             # Token 鉴权管理脚本（X-AMS-TOKEN / TAI-TOKEN）
│   ├── import_md_to_trag.py                # 本地文档批量导入 TRAG 脚本（PDF/Word/Excel/Markdown/Text）
│   └── requirements.txt                    # scripts 依赖
└── references/                             # 预置流程文档和 skill 参考
    ├── aibox_hooks.py                      # Hooks 需要的 python 代码（含 Cursor 事件名映射）
    ├── settings.codebuddy.json             # Codebuddy Hooks 配置文件（macOS/Linux）
    ├── settings.codebuddy.windows.json     # Codebuddy Hooks 配置文件（Windows）
    ├── settings.workbuddy.json             # WorkBuddy Hooks 配置文件（macOS/Linux）
    ├── settings.workbuddy.windows.json     # WorkBuddy Hooks 配置文件（Windows）
    ├── settings.claude.json                # Claude Code Hooks 配置文件（macOS/Linux）
    ├── settings.claude.windows.json        # Claude Code Hooks 配置文件（Windows）
    ├── settings.cursor.json                # Cursor hooks.json 配置文件（macOS/Linux）
    └── settings.cursor.windows.json        # Cursor hooks.json 配置文件（Windows）
```
