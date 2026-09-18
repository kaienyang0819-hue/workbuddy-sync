---
name: swimlane-roadmap
description: Generate an interactive "swimlane × timeline" roadmap matrix as a single self-contained HTML file, for multi-dimensional phased product/feature planning. Use when the user asks to lay out a roadmap where several content dimensions (e.g. gameplay scenarios, assistant capabilities, system features, characters, model abilities) each evolve across versions or stages (CG milestones, quarters, phases), rendered as collapsible blocks per cell with an expand/collapse-all control. Produces light-theme high-readability HTML following a fixed visual spec: colored swimlane lanes, medium-light-blue timeline header, white cards with colored left borders, inline For-all and risk tags.
description_zh: 泳道式Roadmap矩阵（维度×阶段）
description_en: Swimlane roadmap matrix
disable: false
agent_created: true
---

# swimlane-roadmap

把「多个内容维度在多个阶段上的演进」整理成一张可交互的 HTML Roadmap 矩阵。核心形态：**纵轴 = 内容维度（泳道），横轴 = 版本/阶段（时间轴），交叉单元格里放可展开的「地块」**。

## When to use

- 用户要把一项需求/规划「列成 roadmap」，且内容天然有**两个正交轴**：`内容维度`（有哪些方向要建设）× `阶段/版本`（按什么节奏拆解）。
- 典型场景：商业化架构、能力 roadmap、系统排期、里程碑拆解——每个维度都要说清「这个阶段做什么、下个阶段做什么」。
- 用户明确要 HTML 交付、要「目录式 + 点开看细节」的交互，而不是一张静态图。

**不要用**的场景：
- 内容只有一个维度（只有阶段、没有分类）→ 用简单时间线即可。
- 内容是线性流程/依赖关系 → 用流程图（drawio/mermaid）。
- 单条路线无交叉 → 普通列表即可。

## 结构模型（先想清楚再写 HTML）

### 两个轴

1. **横轴（阶段）**：时间推进，通常 3–6 个节点。命名遵循用户原话（如 CG39 → CG40 → CG41 → CG42 → 长线规划），不要擅自改名。每个节点可带一个短标签（该阶段主题）。
2. **纵轴（泳道/维度）**：内容分类，通常 4–6 个。维度命名要**互相独立、覆盖完整**——同一件事只归一个泳道。命名用序号前缀（① ② ③…）帮助对齐。

### 单元格 = 地块（block）

每个交叉格子里放 0 个或多个「地块」；格子为空时显示占位符「—」。

地块结构：`标题 + 数量徽标 + 子项列表`，默认收起，点击标题展开。子项用 ①②③… 编号，每个子项单独成行。

### 拆维度的判断（关键）

- **维度名要能回答「这条泳道负责什么」**。宁可维度少而清晰，不要硬凑。
- 同一条信息只放一个泳道；如果某项似乎横跨两个维度，选最本质的那个，别复制两份。
- 若某个维度在多数阶段都是空的，说明它可能不该独立成泳道，考虑并入别的维度或删掉。

## 视觉规范（固定，不要偏离）

| 项目 | 规则 |
|---|---|
| 基调 | 浅底深字，正文 `#1a2233`，弱化文字 `#7a8499` |
| 页面容器 | 白底卡片 + 圆角 18px + 柔和阴影 |
| 时间轴头部 | 中等浅蓝渐变 `#dbe7f5 → #c9daf0`，版本号深蓝 `#1d3a6e`，阶段标签白底描边胶囊 |
| 泳道维度色 | 蓝 `#3b82f6` / 紫 `#8b5cf6` / 青 `#0891b2` / 橙 `#f59e0b` / 绿 `#10b981`，每色配 `--c-bg`（极浅底）与 `--c-line`（描边） |
| 地块卡片 | 白底、左侧 4px 彩色竖条、圆角 10px、细描边 `#d8e1ef` |
| 数量徽标 | 地块标题右侧小胶囊，颜色跟随维度色，显示「N项」 |
| 高风险标 | 红色渐变小标 `#ef4444→#dc2626`，白字 |
| For全体 标 | 青色描边小标，仅标记「免费/全体玩家可用」的子项，放在子项文字末尾 |

## Steps

1. **读需求，拆两轴**：确认内容维度（泳道）和阶段（列），各列出清单；先跟用户对齐维度与阶段的命名/顺序（高风险任务必须先给方案清单确认）。
2. **搭骨架**：从 `templates/roadmap-template.html` 复制完整 CSS + JS（不要自己重写样式，直接复用，保证视觉一致）。改动点只有两处：
   - `:root` 里的 `--cols: N`（阶段数）；
   - 每个泳道用 `dim-1` ~ `dim-5` 中的一个颜色类（超过 5 个维度时，在 CSS 里新增 `dim-6` 并自定义 `--c/--c-bg/--c-line`）。
3. **填内容**：按「泳道 → 阶段 → 地块」逐格填。每个地块一个 `<details class="block">`，内含 `<summary>`（标题 + `.cnt` 数量 + 可选 `.tag-risk`）和 `.block-body`（若干 `<span class="item">` 子项）。
4. **空格子**：放 `<div class="cell-empty">—</div>`。
5. **标签**：需要强调「全体玩家可用」的子项，末尾加 `<span class="tag-free">For全体</span>`；高风险地块在 summary 里加 `<span class="tag-risk">高风险</span>`。
6. **交付**：单文件自包含 HTML，保存到用户指定目录；需要时用 `present_files` 预览。

## 模板

- 黄金模板：`templates/roadmap-template.html`（含完整 CSS/JS 与结构示例，含注释说明如何扩展维度与阶段）。
- 生成时**务必以模板为准**，不要凭记忆重写 CSS——视觉一致性和换行问题都靠模板保证。

## Pitfalls（踩坑清单，来自实战）

1. **换行渲染**：子项之间绝对不要用 `<br>` 分隔，也不要依赖 `white-space: pre-line`。每条子项必须包成独立的块级 `<span class="item">`（`display: block`），物理上不可能粘连。模板里已是这种写法，别改。
2. **并行编辑竞态**：对同一 HTML 文件做多处修改时，并行多次 Edit 会静默丢失部分改动。改为**用一个 Python 脚本串行执行所有替换**（Write 写 `.py` → bash 执行 → 校验 → 删脚本）。
3. **中文编码**：`python -c` 内联传中文会被 Git Bash 破坏编码。凡要处理中文，一律先 Write 一个 `.py` 脚本文件再执行，不要内联。
4. **阶段列数**：新增/删除阶段时，必须同步改 `--cols`；否则网格会错位。空格子务必补 `cell-empty`，否则该行会塌。
5. **时间轴存在感**：时间轴背景别用近白（`#f7fafd` 级别太浅，存在感丢失），保持在中等浅蓝 `#dbe7f5→#c9daf0`。
6. **维度色区分**：相邻泳道不要用相近色（蓝/青、橙/黄容易混）。优先用模板里现成的 5 色，尽量拉开色相。
7. **命名接地气**：这是向上汇报材料，术语要面向决策者（如「订阅权益」而非「对外统一心智」），去掉生造词。

## Verification

生成后自查：

- [ ] 阶段数与 `--cols` 一致，时间轴列数和泳道列数对齐，无错位/塌陷。
- [ ] 每个非空格子都有 `<details class="block">`，空格子都有 `cell-empty`。
- [ ] 每个地块标题带数量徽标，数量与实际子项数一致。
- [ ] 子项用块级 `.item` 分隔，无 `<br>` 残留，无粘连。
- [ ] 「展开全部 / 收起全部」按钮能一键切换，单个地块点击可展开。
- [ ] 浏览器打开无 JS 报错、无样式错乱。
- [ ] 维度命名互斥且覆盖完整，无重复归类。
