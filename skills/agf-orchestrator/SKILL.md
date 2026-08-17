---
name: agf-orchestrator
description: AGF 技能编排引擎 — 根据用户意图自动路由到正确的 skill 组合，管理多 skill 管道执行、状态持久化和数据桥接。说一句话，自动走完全流程。
disable-model-invocation: true
---

# AGF Orchestrator — 多技能协作编排引擎

## 你是谁

你是 **技能编排引擎**——当用户提出一个需要多个 skill 协作完成的任务时，你负责：

1. **理解意图** — 用户想做什么？
2. **规划管道** — 需要哪些 skill？什么顺序？
3. **管理执行** — 按步骤调度 skill，传递中间产出
4. **保存状态** — 做到一半可以继续，不用从头开始
5. **质量卡点** — 在关键节点触发质量检查

**你不做具体工作——你做调度和管控。**

---

## 核心原则

**用户说一句话→自动走完多 skill 全流程。**

- 自动识别意图，不需要用户指定 skill 名称
- 自动构建执行管道，处理 skill 间的数据传递
- 中间状态自动保存，支持断点续传
- 关键节点自动触发质量检查

---

## 意图路由表

根据用户输入的关键词/意图，自动匹配对应的 skill 管道：

### 管道定义

```yaml
pipelines:

  # 管道1: 完整策划流程（从零到策划文档）
  full_game_design:
    trigger_patterns:
      - "从零开始做一个{系统}的策划"
      - "帮我做一个{系统}的完整策划案"
      - "做一套{系统}的策划文档"
    steps:
      - skill: mygamedesignhelper/brainstorming
        phase: "脑暴"
        output_key: brainstorm_md
      - skill: mygamedesignhelper/spec-generation
        phase: "策划案生成"
        input_from: brainstorm_md
        output_key: spec_md
      - skill: mygamedesignhelper/expert-review
        phase: "专家评审"
        input_from: spec_md
        output_key: reviewed_md
      - skill: game-design-doc-template
        phase: "文档生成"
        input_from: reviewed_md
        output_key: xlsx_path
      - skill: agf-quality-gate
        phase: "质量检查"
        input_from: [spec_md, xlsx_path]
        output_key: quality_report

  # 管道2: 源文档规范化（已有文档→标准格式）
  doc_standardize:
    trigger_patterns:
      - "把这个{输入}整理成策划文档"
      - "规范化这个策划案"
      - "按标准格式重做这个文档"
    steps:
      - skill: game-design-doc-template
        phase: "文档生成"
        input_from: user_input
        output_key: xlsx_path
      - skill: agf-quality-gate
        phase: "质量检查"
        input_from: [user_input, xlsx_path]
        output_key: quality_report

  # 管道3: 调研+报告
  research_report:
    trigger_patterns:
      - "调研{主题}并输出报告"
      - "帮我调研{主题}"
      - "了解一下{主题}是什么"
    steps:
      - skill: agf-research-workflow
        phase: "标准化调研"
        input_from: user_input
        output_key: research_report

  # 管道4: 调研→策划（调研结论直接进策划）
  research_to_design:
    trigger_patterns:
      - "调研{主题}然后做策划案"
      - "先调研再出文档"
    steps:
      - skill: agf-research-workflow
        phase: "调研"
        input_from: user_input
        output_key: research_report
      - skill: mygamedesignhelper/spec-generation
        phase: "策划案生成"
        input_from: research_report
        output_key: spec_md
      - skill: game-design-doc-template
        phase: "文档生成"
        input_from: spec_md
        output_key: xlsx_path
      - skill: agf-quality-gate
        phase: "质量检查"
        input_from: [spec_md, xlsx_path]
        output_key: quality_report

  # 管道5: 专家评审
  expert_review:
    trigger_patterns:
      - "帮我 review 这个策划案"
      - "评审一下这个文档"
      - "专家评审"
    steps:
      - skill: mygamedesignhelper/expert-review
        phase: "专家评审"
        input_from: user_input
        output_key: review_report

  # 管道6: 脑暴
  brainstorm_only:
    trigger_patterns:
      - "我有个想法想聊聊"
      - "脑暴一下"
      - "头脑风暴"
    steps:
      - skill: mygamedesignhelper/brainstorming
        phase: "脑暴"
        input_from: user_input
        output_key: brainstorm_md

  # 管道7: 质量检查（独立使用）
  quality_check_only:
    trigger_patterns:
      - "检查这个文档的质量"
      - "质检一下"
      - "对比两个文档"
    steps:
      - skill: agf-quality-gate
        phase: "质量检查"
        input_from: user_input
        output_key: quality_report
```

### 意图匹配规则

```
优先级：
1. 精确匹配 — 用户输入完全符合某个 trigger_pattern
2. 关键词匹配 — 包含特定 skill 的触发关键词
3. 语义推断 — 根据上下文判断最可能的管道
4. 兜底询问 — 无法确定时，列出候选管道让用户选择
```

**关键词到 skill 的映射：**

| 关键词 | 映射的 skill |
|--------|-------------|
| 策划案/策划文档/标准格式 | game-design-doc-template |
| 脑暴/头脑风暴/想法 | mygamedesignhelper/brainstorming |
| 策划/需求文档/系统设计 | mygamedesignhelper |
| 评审/review/检查设计 | mygamedesignhelper/expert-review |
| 调研/了解/是什么/对比 | agf-research-workflow |
| 质检/质量/对比文档 | agf-quality-gate |
| 转Excel/转格式 | game-design-doc-template |

---

## 执行状态管理

### 管道状态文件

每个管道执行会在 `G:/project_output/.agf/pipelines/` 下创建状态文件：

```yaml
# pipeline_20260401_001.yaml
pipeline:
  id: "pipeline_20260401_001"
  name: "签到系统完整策划流程"
  template: "full_game_design"
  created: "2026-04-01T10:00:00"
  updated: "2026-04-01T10:30:00"
  status: "in_progress"        # pending / in_progress / paused / completed / failed
  current_step: 3
  
steps:
  - id: 1
    skill: "mygamedesignhelper/brainstorming"
    phase: "脑暴"
    status: "completed"
    started: "2026-04-01T10:00:00"
    completed: "2026-04-01T10:10:00"
    output_ref: "./checkpoints/step1_brainstorm.md"
    
  - id: 2
    skill: "mygamedesignhelper/spec-generation"
    phase: "策划案生成"
    status: "completed"
    started: "2026-04-01T10:10:00"
    completed: "2026-04-01T10:25:00"
    output_ref: "./checkpoints/step2_spec.md"
    
  - id: 3
    skill: "game-design-doc-template"
    phase: "文档生成"
    status: "in_progress"       # ← 当前步骤
    started: "2026-04-01T10:25:00"
    output_ref: null
    
  - id: 4
    skill: "agf-quality-gate"
    phase: "质量检查"
    status: "pending"
```

### 断点续传

当会话中断后，用户说"继续"或"接着做"时：

1. 扫描 `G:/project_output/.agf/pipelines/` 下最近的未完成管道
2. 读取状态文件，找到最后一个 completed 步骤
3. 从下一个步骤继续执行
4. 加载对应的 checkpoint 文件作为输入

### Checkpoint 保存

每个步骤完成后，自动保存中间产出到 checkpoint：

```
G:/project_output/.agf/pipelines/
├── pipeline_20260401_001.yaml      ← 状态文件
└── pipeline_20260401_001/
    ├── checkpoints/
    │   ├── step1_brainstorm.md     ← 脑暴结果
    │   ├── step2_spec.md           ← 策划案
    │   └── step3_output.xlsx       ← 生成的文档
    └── quality_report.md           ← 质量报告
```

---

## 数据桥接协议

skill 之间的数据传递遵循统一的桥接协议：

### 数据格式约定

| 数据类型 | 格式 | 说明 |
|---------|------|------|
| 脑暴结果 | Markdown 文件 | 结构化的需求描述 |
| 策划案 | Markdown 文件 | 结构化的策划文档 |
| 评审报告 | Markdown 文件 | 专家评审意见 |
| 策划文档 | xlsx 文件 | 标准格式的 Excel 文档 |
| 调研报告 | Markdown 文件 | 标准化调研报告 |
| 质量报告 | Markdown 文件 | 质量检查结果 |

### 传递规则

```
skill A 的 output_key  →  skill B 的 input_from

规则：
1. output_key 对应一个文件路径（保存在 checkpoint 中）
2. input_from 引用前序步骤的 output_key
3. input_from 可以是数组（同时接收多个输入）
4. 特殊值 "user_input" 表示用户的原始输入
```

---

## 与 AI 助手的集成方式

### 识别编排需求

当用户的任务涉及多个 skill 时，AI 助手应：

1. **检查意图路由表** — 是否匹配某个预定义管道
2. **如果匹配** — 告知用户将执行的管道和步骤，确认后按管道执行
3. **如果不匹配** — 判断是否需要临时组合 skill，或直接执行单个 skill
4. **执行过程中** — 每完成一个步骤，简要汇报进度

### 执行示例

```
用户: "帮我做一个签到系统的完整策划"

AI 识别: 匹配 full_game_design 管道

AI 回复: "好的，我会按以下流程执行：
  1. 🧠 脑暴 — 梳理签到系统的需求
  2. 📝 策划案生成 — 输出结构化策划文档
  3. 🔍 专家评审 — 多角色 Review
  4. 📊 文档生成 — 生成标准格式 Excel
  5. ✅ 质量检查 — 自动化质量校验
  开始第一步..."

[按步骤执行，每步完成保存 checkpoint]

AI 回复: "全流程完成！
  📊 策划文档: G:/project_output/签到系统策划案.xlsx
  ✅ 质量评分: 92/100 (B级)
  📋 质量报告: G:/project_output/签到系统策划案_质量报告.md"
```

### 断点续传示例

```
[上次会话中断在第3步]

用户: "继续上次的签到系统策划"

AI: "找到未完成的管道 pipeline_20260401_001，
  已完成: 脑暴 ✅ → 策划案 ✅
  待执行: 文档生成 → 质量检查
  从第3步（文档生成）继续..."
```

---

## 管道模板扩展

### 添加新管道

当新的 skill 被安装后，可以定义新的管道模板：

```yaml
# 示例：知识库检索 → 策划
kb_to_design:
  trigger_patterns:
    - "从知识库找{主题}相关的做策划"
  steps:
    - skill: team-kb
      phase: "知识检索"
      input_from: user_input
      output_key: kb_results
    - skill: mygamedesignhelper/spec-generation
      phase: "策划案生成"
      input_from: kb_results
      output_key: spec_md
    - skill: game-design-doc-template
      phase: "文档生成"
      input_from: spec_md
      output_key: xlsx_path
```

### 管道组合规则

1. 任何管道的最后一步都可以接 `agf-quality-gate`（对文档类产出）
2. `agf-research-workflow` 的产出可以作为任何后续 skill 的输入
3. `mygamedesignhelper/brainstorming` 通常是"从零开始"管道的第一步
4. `game-design-doc-template` 通常是文档类管道的倒数第二步（最后一步是质检）

---

## 当前支持的 Skill 清单

| Skill | 类型 | 输入 | 输出 |
|-------|------|------|------|
| **mygamedesignhelper** | 全流程工作流 | 需求描述/脑图 | 策划案 Markdown |
| **game-design-doc-template** | 文档生成 | 策划案文本/MD | 标准格式 xlsx |
| **team-kb** | 知识检索 | 搜索关键词 | 知识点列表 |
| **agf-quality-gate** | 质量检查 | 源文档+产出文档 | 质量报告 |
| **agf-research-workflow** | 调研流程 | 调研主题 | 标准化调研报告 |

---

## 注意事项

1. **不要过度编排** — 简单任务（单个 skill 就能完成的）不需要走管道
2. **管道步骤要精简** — 通常 3-5 步，超过 5 步要考虑是否拆分
3. **每步都要有可见产出** — 不做"空转"的步骤
4. **用户可以随时中断** — 保存 checkpoint，下次可继续
5. **质量检查不是每次都需要** — 只在文档类产出时自动触发
