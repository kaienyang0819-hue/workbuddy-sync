---
name: design-md-apply
description: 读取项目根目录的 DESIGN.md 设计规范，将设计 token 应用到所有 HTML 产出中。确保风格一致性。
user: false
agent_created: true
disable-model-invocation: true
---

# DESIGN.md 设计规范应用

## 触发条件

在以下场景中自动加载此技能：
- 生成任何 HTML 文件（dashboard、报告、可视化、landing page、prototype）
- 用户要求"生成看板"、"做个 HTML"、"出个页面"
- 使用前端设计技能（design-taste-frontend、elite-frontend-design 等）时，作为**风格基础层**先加载

## 工作流程

### 第一步：加载设计规范

在生成 HTML **之前**，检查项目根目录是否存在 `DESIGN.md`：

```
读取 {项目根目录}/DESIGN.md
```

- 如果存在 → 解析 YAML front matter 提取设计 token，读取 Markdown 正文获取设计理念
- 如果不存在 → 使用内置默认值（见下方 Default Tokens），生成完成后提示用户可以创建 DESIGN.md 来统一风格

### 第二步：提取设计 Token

从 DESIGN.md 的 YAML front matter 中提取：

```yaml
colors:        # 颜色映射 → CSS 变量
typography:    # 字体层级 → font-family / font-size / font-weight
rounded:       # 圆角尺度 → border-radius
spacing:       # 间距尺度 → padding / margin / gap
components:    # 组件 token → 直接应用到对应组件
```

### 第三步：注入 CSS 变量

在 HTML 的 `<style>` 顶部注入 CSS 变量块：

```css
:root {
  /* Colors */
  --color-primary: {colors.primary};
  --color-secondary: {colors.secondary};
  --color-tertiary: {colors.tertiary};
  --color-accent: {colors.accent};
  --color-neutral: {colors.neutral};
  --color-surface: {colors.surface};
  --color-on-primary: {colors.on-primary};
  --color-on-surface: {colors.on-surface};
  --color-success: {colors.success};
  --color-error: {colors.error};
  --color-warning: {colors.warning};
  --color-muted: {colors.muted};

  /* Typography */
  --font-heading: {typography.h1.fontFamily};
  --font-body: {typography.body.fontFamily};
  --font-mono: {typography.mono.fontFamily};
  --text-h1: {typography.h1.fontSize};
  --text-h2: {typography.h2.fontSize};
  --text-h3: {typography.h3.fontSize};
  --text-body: {typography.body.fontSize};
  --text-caption: {typography.caption.fontSize};

  /* Rounded */
  --radius-sm: {rounded.sm};
  --radius-md: {rounded.md};
  --radius-lg: {rounded.lg};

  /* Spacing */
  --space-xs: {spacing.xs};
  --space-sm: {spacing.sm};
  --space-md: {spacing.md};
  --space-lg: {spacing.lg};
  --space-xl: {spacing.xl};
}
```

### 第四步：应用到 HTML

在生成 HTML 时：
1. 所有颜色引用使用 `var(--color-xxx)` 而非硬编码 hex
2. 字体使用 `var(--font-xxx)` 引用
3. 组件样式参考 DESIGN.md 中的 `components` 定义
4. 遵循 DESIGN.md 正文中的 Do's and Don'ts

## 与其他设计技能的协作

DESIGN.md 提供**风格基础层**（颜色 + 字体 + 间距 + 圆角），其他设计技能提供**布局与表现层**：

| 层次 | 负责方 | 内容 |
|------|--------|------|
| 风格基础 | DESIGN.md (本技能) | 颜色、字体、间距、圆角、组件 token |
| 布局结构 | design-taste-frontend / elite-frontend-design | 网格系统、响应式策略、组件架构 |
| 视觉品味 | high-end-visual-design / minimalist-ui | 高级感、留白哲学、排版细节 |
| 动效 | gpt-taste | GSAP 动画、过渡效果 |
| 品牌一致性 | cc-design | 设计系统完整性、reference 管理 |

**协作规则**：
1. 本技能**先于**其他设计技能加载，提供 token 基础
2. 其他技能的布局/结构规则**优先于**本技能的通用规则
3. 如果其他技能有明确的颜色/字体规则且与 DESIGN.md 冲突，以其他技能为准（它们是场景特化的）
4. 如果没有其他设计技能参与，本技能独立保证风格一致性

## Default Tokens

当项目根目录没有 DESIGN.md 时，使用以下默认值：

```yaml
colors:
  primary: "#1a1a2e"
  secondary: "#6B7280"
  tertiary: "#667eea"
  accent: "#F59E0B"
  neutral: "#F0F2F5"
  surface: "#FFFFFF"
  on-primary: "#FFFFFF"
  on-surface: "#1a1a2e"
  success: "#10B981"
  error: "#EF4444"
  warning: "#F59E0B"
  muted: "#9CA3AF"

typography:
  h1:
    fontFamily: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif
    fontSize: 22px
    fontWeight: 700
  h2:
    fontFamily: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif
    fontSize: 17px
    fontWeight: 600
  body:
    fontFamily: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif
    fontSize: 14px
  mono:
    fontFamily: "JetBrains Mono", "Fira Code", "SF Mono", monospace

rounded:
  sm: 8px
  md: 12px
  lg: 14px

spacing:
  xs: 4px
  sm: 8px
  md: 14px
  lg: 20px
  xl: 28px
```

## 命令

### 创建 DESIGN.md
如果用户说"创建设计规范"或"初始化 DESIGN.md"，使用 Default Tokens 生成一份到项目根目录。

### 查看当前规范
如果用户说"看看我的设计规范"，读取并格式化展示 DESIGN.md 内容。

### 更新 token
如果用户说"把主色改成 X"或"换字体为 Y"，直接编辑 DESIGN.md 中对应的 YAML 值。

### 导出
如果用户说"导出 Tailwind 配置"，使用 CLI 命令：
```bash
npx @google/design.md export --format json-tailwind DESIGN.md > tailwind.theme.json
```
