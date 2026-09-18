# swimlane-roadmap — 泳道式 Roadmap 矩阵 Skill

把「多个内容维度在多个阶段上的演进」整理成一张可交互的 HTML Roadmap 矩阵。

- 纵轴 = 内容维度（泳道）
- 横轴 = 版本/阶段（时间轴）
- 交叉单元格 = 可展开/收起的「地块」，支持「展开全部 / 收起全部」

## 安装

1. 解压本压缩包，得到 `swimlane-roadmap` 文件夹。
2. 把整个 `swimlane-roadmap` 文件夹复制到你的 WorkBuddy skills 目录：

   ```
   Windows: C:\Users\<你的用户名>\.workbuddy\skills\
   macOS/Linux: ~/.workbuddy/skills/
   ```

3. 重启或刷新 WorkBuddy，skill 即被识别。

## 使用

直接对 AI 说「把这个需求列个 roadmap」，只要内容天然是「几个方向 × 几个阶段」两轴结构（例如商业化架构、能力规划、系统排期、里程碑拆解），AI 会自动调用本 skill 生成可交互 HTML。

## 文件结构

```
swimlane-roadmap/
├── SKILL.md                        # 核心规范：结构模型、视觉规范、踩坑清单、验证清单
└── templates/
    └── roadmap-template.html       # 黄金模板：完整 CSS/JS + 结构示例
```

## 关键参数

| 参数 | 位置 | 说明 |
|---|---|---|
| `--cols` | 模板 `:root` | 阶段列数，改一个数即可适配任意阶段数 |
| `dim-1` ~ `dim-5` | 泳道 class | 5 个预置维度色（蓝/紫/青/橙/绿），超 5 维加 `dim-6` |
| `.block` | 地块 | `<details>` 折叠块：标题 + 数量徽标 + 子项列表 |
| `.tag-risk` / `.tag-free` | 行内标 | 高风险红标 / For全体 青标 |
