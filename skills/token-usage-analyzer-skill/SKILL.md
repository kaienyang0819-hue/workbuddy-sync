---
name: token-usage-analyzer-skill
display_name: Token 看板使用分析与报告
version: 0.0.1
description: 当用户想分析 token.woa.com 看板的使用记录、找出"提问很短但 token/费用很高"的请求、了解为什么消耗高、或需要省 token 建议与成本报告（文本/HTML）时使用。触发词如"分析 token 消耗 / 为什么这么费 token / token 看板报告 / 哪些请求最贵 / 怎么省 token"。
tags: [token, analytics, devtools]
keywords: [token, cost-analysis, chrome-mcp, report, woa, dashboard]
---

# Token 看板使用分析与报告

## 目标

从 `https://token.woa.com/` Token 看板抓取「详细使用记录」，识别两类异常并产出分析报告：

1. **提问很短、但总 Tokens / 费用很高**的记录。
2. **绝对费用最高**的记录。

并解释「短提问为什么贵」的根因，给出可执行的省 token 建议。报告可输出为对话内文本，或一份深色主题的 HTML 文件。

## 触发场景

- 想知道 token / 费用花在哪、为什么某些请求特别贵。
- 想找出「就打了几个字，却消耗几百万 token」的请求。
- 需要一份 token 成本分析报告（文本或 HTML）。
- 需要省 token 的优化建议。

## 前置条件

- 本 skill 依赖 **Chrome MCP**（`chrome-devtools` server）。未安装时按「步骤 0」自动检测并安装。
- 访问 `token.woa.com` 需登录企业身份；若已在 Chrome 登录态，会直接进入看板。

## 使用流程

### 0. 执行前：检测并安装 Chrome MCP（必做）

本 skill 依赖 Chrome MCP，开始任何浏览器操作前必须先确认它已安装并启用。

1. 优先检查当前会话是否已能调用 `chrome-devtools` 的工具（如 `navigate_page`）。能调用则跳过本步。
2. 否则运行检测脚本：

   ```bash
   node <skill_path>/script/ensure-chrome-mcp.js --check
   ```

   - 退出码 `0`：已就绪，直接进入步骤 1。
   - 退出码 `3`：未安装，执行安装：`node <skill_path>/script/ensure-chrome-mcp.js`
   - 退出码 `4`：**存在但被用户显式禁用**（`disabled: true`）。此时脚本**不会静默启用**，以尊重用户意图；需用户二选一确认：
     - 手动把 `~/.codebuddy/mcp.json` 中该项 `disabled` 改为 `false`；
     - 或显式确认后运行：`node <skill_path>/script/ensure-chrome-mcp.js --force-enable`（仅翻转 `disabled`，保留用户原有 command/args/版本）。

3. 脚本会**修改用户系统配置文件** `<用户主目录>/.codebuddy/mcp.json`，在其 `mcpServers` 下写入下面的配置（已存在且启用则不改动；首次写入会自动创建目录/文件，并保留其它已有 MCP 配置）：

   ```json
   "chrome-devtools": {
     "command": "npx",
     "args": ["-y", "chrome-devtools-mcp@1.1.1"],
     "type": "stdio",
     "disabled": false
   }
   ```

   > 注意：版本号已锁定为 `1.1.1`（不用 `@latest`），避免供应链风险。升级时修改 `ensure-chrome-mcp.js` 的 `CHROME_MCP_VERSION` 常量。

4. 若脚本提示 `[installed]` / `[enabled]`，说明刚写入配置，需在 CodeBuddy 中**重新加载 / 重启 MCP** 后才能调用 chrome 工具，再继续步骤 1。

### 1. 打开看板并处理登录

1. 用 Chrome MCP `navigate_page` 打开 `https://token.woa.com/`。
2. 若被重定向到 `std.passport.woa.com` 登录页：
   - 先 `take_snapshot` 读取页面结构，找到登录 / 授权按钮并 `click`；
   - 若是 SSO 直接跳转，可 `navigate_page` 重新打开 `https://token.woa.com/`，多数情况下会带着登录态直接进入；
   - 仍停在登录页则提示用户手动完成账号登录后再继续。
3. `take_snapshot` 确认页面标题为 `Token 看板`、能看到「当前用户」即为已登录。

### 2. 调整每页记录数到 100

- 在快照里找到「每页显示」的 `combobox`（select 元素），用 Chrome MCP `fill` 把值设为 `100`，一次性加载更多记录，减少翻页。
- 如需更多数据可再翻页重复抓取后合并。

### 3. 抓取详细使用记录

- 用 Chrome MCP `evaluate_script` 执行 `script/browser-extract.js` 导出的 `EXTRACT_RECORDS_FN`，
  返回 `{ rowCount, headers, rows }`，其中每行列序为：
  `[时间, 产品, 模型, 提问, 总Tokens, 费用, 观测]`。
- 把返回的 JSON 原样保存为本地文件（如 `records.json`），交给分析脚本。

### 4. 分析并生成报告

运行分析脚本（跨平台，Node.js）：

```bash
node <skill_path>/script/analyze.js --input records.json --out report.html --user <用户名> --quota-used 1294.89 --quota-total 10000
```

参数说明：

| 参数 | 含义 | 默认 |
|---|---|---|
| `--input` | 抓取到的记录 JSON（必填） | - |
| `--out` | 输出 HTML 报告路径；不填则只打印文本摘要 | - |
| `--user` | 报告显示的用户名 | `-` |
| `--source` | 数据来源描述 | `Token 看板` |
| `--short-len` | 「短提问」最大字数 | `20` |
| `--min-tokens` | 进入「短提问高消耗」榜的最低 token | `300000` |
| `--min-fee` | 进入「短提问高消耗」榜的最低费用 | `3` |
| `--top` | 各榜单取前 N | `10` |
| `--quota-used` / `--quota-total` | 本月已用 / 总额度，用于概览卡片 | 不显示 |

脚本会：
- 解析 token（`1,234,567` / `1.2M`）与费用（`¥38.89`）；
- 计算「短提问高消耗榜」「费用最高榜」「token 最高榜」、按产品 / 模型聚合；
- 控制台打印文本摘要，并按需写出 HTML 报告。

#### 运行环境要求

- **Node.js ≥ 16**（脚本使用 ES Module、`node:fs`/`node:os`/`node:path` 内置模块）。
- 运行前可执行 `node -v` 确认；若提示找不到 `node`，需先安装 Node.js（建议 LTS 18/20）。
- 若 `node --check` 报语法错误，多半是 Node 版本过低，请升级。

#### 输出示例（控制台文本摘要）

```text
Token 使用分析（共 100 条，总费用 ¥1294.89，单条均价 ¥12.95）

一、提问 ≤ 20 字但消耗高（按费用）：
  1. [2026-06-05 15:24:36] "仅入口删除" — 6,826,151 tokens / ¥38.89 (Claude-Opus-4.8)
  2. [2026-06-05 11:18:11] "继续做面板对接子模块" — 5,100,346 tokens / ¥37.10 (Claude-Opus-4.8)
  ...

二、绝对费用最高：
  1. [2026-06-05 10:21:35] "空仓库, 你使用mcp在这里面建立…" — 12,018,058 tokens / ¥57.35
  ...

HTML 报告已生成：/path/to/report.html
```

#### 异常路径处理

| 情况 | 表现 / 处理 |
|---|---|
| 未传 `--input` | 报错并打印用法，退出码 `1`。 |
| 输入文件不存在 / 路径错误 | `readFileSync` 抛错，退出码非 0；请核对路径（支持相对/绝对）。 |
| 输入 JSON 格式损坏 | `JSON.parse` 抛错；请确认是 `evaluate_script` 原样返回的结构。 |
| 输入结构无法识别 | 打印「无法识别的输入结构」，退出码 `1`；需为 `{rows}`、二维数组或对象数组之一。 |
| **空数据**（`rows` 为空 / 抓取到 0 条） | 摘要显示「共 0 条」，各榜单为空，HTML 仍生成但表格为空。应回看页面是否未登录、未加载或筛选条件过严，重新抓取。 |
| 抓取阶段表格未找到 | `EXTRACT_RECORDS_FN` 返回 `{rowCount:0, error:'no table found'}`；确认已进入「Token 看板」且「详细使用记录」已渲染。 |
| 未安装 Node.js | `node` 命令不存在；先安装 Node.js ≥ 16。 |

### 5. 预览 HTML 报告（直接打开本地文件，无需启动 web 服务）

报告生成后，**直接用本地文件路径打开预览即可，不需要启动任何 web 服务**：

```bash
# 方式一：skill 内置脚本（跨平台，零依赖，调用系统默认程序打开本地文件）
node <skill_path>/script/preview-report.js --path <报告文件完整路径>
# 或： node <skill_path>/script/preview-report.js --dir <报告目录> --file report.html

# 方式二：直接用系统命令打开本地文件
#   Windows : Invoke-Item <报告文件路径>      （或 start <路径>）
#   macOS   : open <报告文件路径>
#   Linux   : xdg-open <报告文件路径>
```

> 不使用本地 HTTP 服务、不使用 `preview_url`、不使用 open_result_view；用本地路径 / `file://` 直接打开即可。

## 完整端到端示例（可直接运行验证）

仓库内置脱敏样例数据 `script/examples/sample-records.json`，无需打开看板即可验证脚本与环境：

```bash
cd <skill_path>/script

# 方式一：用内置 npm 脚本（等价于下面的完整命令）
npm run demo

# 方式二：手动完整命令
node analyze.js \
  --input examples/sample-records.json \
  --out examples/sample-report.html \
  --user demo --quota-used 1294.89 --quota-total 10000
```

预期控制台输出（节选）：

```text
Token 使用分析（共 8 条，总费用 ¥184.92，单条均价 ¥23.12）

一、提问 ≤ 20 字但消耗高（按费用）：
  1. [2026-06-05 15:24:36] "仅入口删除" — 6,826,151 tokens / ¥38.89 (Claude-Opus-4.8)
  2. [2026-06-05 11:18:11] "继续做面板对接子模块" — 5,100,346 tokens / ¥37.10 (Claude-Opus-4.8)
  ...
二、绝对费用最高：
  1. [2026-06-05 10:21:35] "空仓库, 你使用mcp在这里面建立 https:…" — 12,018,058 tokens / ¥57.35
  ...
HTML 报告已生成：<skill_path>/script/examples/sample-report.html
```

运行后会在 `examples/` 下生成 `sample-report.html`，用本地服务 + `preview_url` 打开即可看到完整报告样式。真实使用时，把 `--input` 换成步骤 3 抓取保存的 `records.json` 即可。

## 报告内容

1. **概览**：记录数、总 tokens、总费用、单条均价（如提供额度则显示本月费用 / 额度 / 占比）。
2. **短提问高消耗榜**：提问 ≤ N 字但 token 或费用超阈值，按费用降序，含模型标签（1m 版高亮区分）。
3. **费用最高榜**。
4. **逐条诊断与针对性节约建议**：对高消耗记录（短提问榜 + 费用榜去重）逐条推断成因并给出对应建议，按费用严重度（高/中/低）标色。
5. **按产品 / 模型聚合**。
6. **成因分析**：历史累积、大文件读取、MCP 数据体积、Agent 多轮循环、模型计费差异。
7. **省 token 建议（通用）**（按收益排序）。

## 逐条诊断规则（advisor）

`script/lib/advisor.js` 基于每条记录的「提问文本特征 + token/费用量级 + 模型」做启发式推断，输出成因标签与针对性建议。识别的特征与对应建议：

| 成因标签 | 命中特征 | 针对性建议 |
|---|---|---|
| 包含图片输入 | `@image`、`.png/.jpg` 等 | 图片 token 大，非必要不传，用文字/坐标描述 |
| 读取 Figma 设计稿数据 | 含 `figma.com` | 只取目标 node-id，避免整页/整文件 |
| 抓取外部 URL | 含 `http(s)`（非 figma） | 只取关键片段/字段，设 maxOutputLength |
| 读取/分析大数据结构 | `json`、`数据结构`、`字段`、`数组` 等 | 脚本预处理只取需要字段/样例 |
| 携带大量注入上下文 | `<user_info>`、`<question_answer>`、`User's input is:` | 检查会话是否过长，必要时开新会话 |
| 触发 MCP 大体积返回 | `mcp`、`浏览器`、`chrome`、`快照` | 限制 MCP 返回量，只取关键区域 |
| 定时任务自动消耗 | `[cron` | 评估频率与数据量，精简输出 |
| 模糊/续作指令 | `继续/ok/删除/需要` 等短指令 | 讲清对象与范围，减少翻历史和来回轮次 |
| 提问短但上下文累积大 | 提问 ≤ N 字且 token ≥ 30 万 | 任务切换开新会话（收益最大） |
| 使用 1m 上下文版 | 模型名含 `1m` | 小操作换普通/便宜模型 |
| 疑似长会话累积（兜底） | 未命中以上但 token/费用很高 | 适时开新会话，减少整文件读取 |

> 结论为启发式推断，仅用于定位优化方向，不代表绝对成因。

## 成因分析要点（用于解释「短提问为什么贵」）

- 计费按**整次请求的全部上下文**算，「提问」列只是最后一句话。
- 主因是**历史对话累积** —— 短指令出现在长会话后期时单次最贵。
- **大文件 / 大 JSON / 整文件读取**、**MCP 返回（figma、chrome 快照、网页内容）**、**Agent 多轮工具循环**都会把单条记录撑大。
- **模型与计费差异**：1m 上下文版单价更高；cache 写入比读取贵。

## 省 token 建议（按收益排序）

**A. 会话与上下文管理（收益最大）**

1. 任务切换就开新会话——每轮请求都重发全部历史，换需求/模块时开新会话最省。
2. 长会话定期重开，用一句话总结结论带入新会话，而不是拖着长历史继续。
3. 不在一个会话里塞多个无关任务，避免彼此上下文互相计费。

**B. 文件与数据读取**

4. 避免整文件读取，先搜索/grep 定位，再按需读取相关行范围（offset/limit）。
5. 大 JSON / 数据先用脚本预处理，只取需要字段或前几条样例。
6. 长日志 / 命令输出先 grep / head 截取关键部分再分析。
7. 避免重复粘贴同一段内容，让模型记住一次即可。

**C. 指令表达**

8. 指令一次讲清对象与范围（哪个文件、哪段、改成什么）。
9. 少用"继续/删除/需要/ok"等模糊词，避免模型重读大量上下文。
10. 批量需求一次说清，减少多轮交互累积。
11. 给精确路径 / 行号（@文件、行号），省去全局搜索开销。

**D. 工具与 MCP**

12. 控制 MCP 返回量，调用时设置 maxOutputLength，优先精确查询。
13. Figma 只取目标 node-id，避免拉取整页/整文件。
14. 浏览器快照 / 网页只取关键区域或用选择器定位。
15. 减少不必要的探索轮次，明确告诉模型改哪、不要全局乱搜。

**E. 模型与多媒体**

16. 按需选模型，小任务用便宜模型，复杂重构才用高价模型。
17. 谨慎使用 1m 上下文版（单价更高），仅确需超长上下文时用。
18. 图片 / 截图按需传，能用文字/坐标/报错文本描述就别截图。

**F. 工程化沉淀**

19. 重复说明沉淀成项目规则 / skill，避免每次重复输入。
20. 保持稳定前缀以命中缓存（cache 读取远比重新写入便宜）。

## 脚本资源

- `script/ensure-chrome-mcp.js`：前置检查，检测 / 安装 `chrome-devtools` MCP；`--check` 仅检测（退出码 `0` 就绪、`3` 缺失、`4` 被用户禁用），`--force-enable` 才会启用被禁用项。
- `script/browser-extract.js`：导出 `EXTRACT_RECORDS_FN`（页面内执行函数字符串）与 `extractRecordsInPage`，供 Chrome MCP `evaluate_script` 抓取记录。
- `script/lib/parser.js`：`parseTokens` / `parseFee` / `normalizeRows` / `analyze`，负责解析与排行计算。
- `script/lib/advisor.js`：`analyzeRecord` / `attachAnalysis`，逐条记录成因诊断与针对性建议。
- `script/lib/report.js`：`generateHtml` / `generateTextSummary`，负责报告生成。
- `script/analyze.js`：CLI 主入口，串联解析、分析、报告输出。
- `script/preview-report.js`：零依赖跨平台脚本，直接用系统默认程序打开本地报告文件预览（不启动 web 服务、不依赖 `preview_url`）。
- `script/examples/sample-records.json`：脱敏样例输入，用于端到端验证（`npm run demo`）。

## 注意事项

- 所有需要执行的代码都放在 `script/` 下，使用 **Node.js ≥ 16（ES Module）**，兼容 Windows / macOS / Linux。
- `ensure-chrome-mcp.js` 会**修改用户系统配置文件** `~/.codebuddy/mcp.json`：缺失时新增 `chrome-devtools` 项（保留其它配置）；若用户已显式禁用（`disabled:true`），**默认不静默启用**，仅提示，需 `--force-enable` 或手动确认。
- chrome MCP 版本已锁定（`chrome-devtools-mcp@1.1.1`），不使用 `@latest`，规避供应链风险。
- 不修改看板页面任何数据，仅做只读抓取。
- 提问文本可能含 `<...>` 等标签，报告生成已做 HTML 转义（防 XSS）。
- 抓取到空数据时不报假结论，应提示重新确认登录态与页面加载情况。
- 涉及时间统一按当前时区展示。
