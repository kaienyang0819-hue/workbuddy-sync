# 学习闭环系统 — 实现参考

> 行为原则见 `SOUL.md`，本文档仅存放实现细节。

## 存储布局

```
g:\workclaw\.workbuddy\
├── learning/
│   ├── config.json              # 全局配置（阈值/权重/衰减/晋升规则）
│   ├── semantic-patterns.json   # L3 语义模式库
│   ├── skill-stats.json         # 技能使用统计
│   ├── episodes/YYYY/MM/        # L2 情景记忆
│   ├── feedback/                # 用户反馈记录
│   ├── reports/                 # 自省周报
│   └── README.md                # 本文件
├── scripts/
│   ├── evaluator.py             # 任务评估器
│   ├── extractor.py             # 经验提取器（含 experience_type 推断）
│   ├── router.py                # 分流决策器
│   ├── loop_runner.py           # 闭环主入口（一键串联全链路）
│   ├── episode_store.py         # 情景记忆 CRUD
│   ├── pattern_store.py         # 语义模式库管理（含 candidate→active 晋升）
│   ├── skill_stats.py           # 技能使用统计
│   ├── skill_evolver.py         # 技能进化器（Gotchas 候选化 + 晋升）
│   └── nudge.py                 # 周期自省（剪枝/归档/周报）
```

## 闭环脚本 CLI

### 一键闭环（推荐）

```bash
python g:\workclaw\.workbuddy\scripts\loop_runner.py '{"task_summary":"...", "task_type":"...", "steps":5, ...}'
```

### 单步调用

```bash
# 评估
python evaluator.py '{"task_summary":"...", "task_type":"...", ...}'

# 提取经验
python extractor.py '<evaluation_json>' '<experience_data_json>'

# 分流决策
python router.py '<evaluation_json>' '<experience_json>'

# 模式库操作
python pattern_store.py stats          # 查看统计
python pattern_store.py list           # 列出所有 pattern（含 candidate）
python pattern_store.py search <kw>    # 搜索
python pattern_store.py relevant <desc> # 获取相关 pattern

# 情景记忆
python episode_store.py count          # 总数
python episode_store.py list [limit]   # 列出最近 N 条
python episode_store.py search <kw>    # 搜索

# 技能进化
python skill_evolver.py list                           # 列出已安装 skill
python skill_evolver.py gotcha <name> '["p1","p2"]'    # 追加候选 Gotchas
python skill_evolver.py promote <name> [min_occ]       # 晋升候选到正式

# 自省
python nudge.py                        # 预检模式
python nudge.py --execute              # 执行实际操作
```

## Pattern 生命周期

```
创建 → candidate (置信度 0.5)
  ↓ 命中 ≥ 2次 且 成功率 ≥ 75% 且 置信度 ≥ 0.65
晋升 → active (正常参与任务注入)
  ↓ 持续使用 → 置信度最高到 0.99
  ↓ 长期未用 → 每月衰减 0.02
  ↓ 置信度 < 0.3 且 6个月未用
废弃 → deprecated (不参与检索)
```

## Gotchas 生命周期

```
发现坑点 → gotchas-candidates.jsonl (候选)
  ↓ 同类坑出现 ≥ 2次 或 用户手动确认
晋升 → SKILL.md 正式 Gotchas 表格
```

## 配置参考

所有阈值、权重、衰减率见 `learning/config.json`，关键配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `patterns.candidate_initial_confidence` | 新 pattern 初始置信度 | 0.50 |
| `patterns.promotion.min_hits` | 晋升最少命中次数 | 2 |
| `patterns.promotion.min_success_rate` | 晋升最低成功率 | 0.75 |
| `patterns.promotion.min_confidence` | 晋升最低置信度 | 0.65 |
| `patterns.decay_per_month_unused` | 每月未用衰减 | 0.02 |
| `patterns.deprecation_threshold` | 废弃置信度阈值 | 0.30 |
| `skills.gotchas_candidate_mode` | Gotchas 候选模式开关 | true |
| `skills.gotchas_promotion_min_occurrences` | Gotchas 晋升最少出现次数 | 2 |
| `skills.auto_create_requires_confirmation` | Skill 创建须确认 | true |

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-14 | v1.0 | Phase 0-3 初始实现 |
| 2026-04-14 | v1.1 | 5项改进：Pattern candidate 状态、Gotchas 候选化、experience_type、SOUL.md 瘦身、nudge 增强 |
