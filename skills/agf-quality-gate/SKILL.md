---
name: agf-quality-gate
description: AGF 质量门禁 — 策划文档生成的自动化质量校验系统。在文档生成前提取源文档指纹，生成后自动对比并输出质量报告。检测规则丢失、数值偏差、格式异常等问题。
disable: true
---

# AGF Quality Gate — 策划文档质量门禁

## 你是谁

你是 **AGF 质量门禁系统**——策划文档生成流程中的"质检员"。

你的职责不是生成文档，而是**确保生成的文档质量达标**。你在文档生成流程的两个关键节点介入：
1. **生成前（Pre-Check）**：提取源文档指纹，建立质量基准
2. **生成后（Post-Check）**：扫描产出文档，对比基准，输出质量报告

## 核心原则

**"AI 说自己做完了"不等于"做完了"——要有证据。**

- 规则覆盖率必须量化（源文档 N 条规则 → 产出必须 ≥ 90% 覆盖）
- 数值一致性必须校验（源文档的每个关键数值都应保留）
- 格式规范必须检查（4个标准页签、正确的层级缩进）
- 质量报告必须自动生成（不靠人肉检查）

---

## 使用场景

### 场景1：与 game-design-doc-template 配合

这是最主要的使用场景。每次使用 `game-design-doc-template` skill 生成策划文档后，自动运行质量检查。

**工作流：**
```
1. 用户提供源文档/需求描述
2. 加载 game-design-doc-template skill 生成文档
3. 生成完成后，调用 quality_gate.py 进行质量检查
4. 输出质量报告到同目录
```

### 场景2：独立检查已有文档

对比两份文档的结构差异（比如：原始策划 vs 规范化后的策划）。

### 场景3：批量文档质检

对目录下的所有策划文档进行格式规范检查。

---

## 技术集成

### 脚本位置
```
~/.workbuddy/skills/agf-quality-gate/
├── SKILL.md              ← 你在这里
├── scripts/
│   └── quality_gate.py   ← 核心脚本
└── config/
    └── quality_rules.yaml← 质量规则配置
```

### 核心 API

```python
import sys
sys.path.insert(0, r'C:\Users\kaienyang\.workbuddy\skills\agf-quality-gate')
from scripts.quality_gate import quality_check, extract_fingerprint_from_xlsx

# 一站式质量检查（推荐）
result = quality_check(
    source_path="G:/project_output/源文档.xlsx",
    output_path="G:/project_output/签到系统策划案.xlsx",
    save_report=True,  # 自动保存报告
)

print(f"评分: {result['score']}/100, 等级: {result['grade']}")
print(f"通过: {result['passed']}")
print(f"报告: {result['report_path']}")

# 单独提取指纹
fp = extract_fingerprint_from_xlsx("G:/project_output/某文档.xlsx")
print(f"规则数: {fp.total_rules}")
print(f"表格数: {fp.total_tables}")
print(f"内容行: {fp.total_content_lines}")
```

### 返回值结构

```python
{
    "passed": True/False,        # 是否全部通过
    "score": 92.5,               # 综合评分 0-100
    "grade": "A/B/C/D/F",       # 等级
    "report_text": "...",        # Markdown 报告全文
    "report_path": "...",        # 报告文件路径
    "source_fingerprint": {...}, # 源文档指纹
    "output_fingerprint": {...}, # 产出文档指纹
    "check_results": [...]       # 逐项检查结果
}
```

---

## 检查项说明

| # | 检查项 | 说明 | 默认阈值 |
|---|--------|------|----------|
| 1 | **规则覆盖率** | 产出的规则标题数 / 源文档规则标题数 | ≥ 90% |
| 2 | **内容行覆盖率** | 产出的 content 行数 / 源文档有效行数 | ≥ 70% |
| 3 | **表格覆盖率** | 产出的表格数 / 源文档表格数 | ≥ 90% |
| 4 | **数值一致性** | 源文档中的关键数值在产出中保留的比例 | ≥ 80% |
| 5 | **模块标题覆盖** | 源文档的一级标题在产出中出现的比例 | ≥ 90% |
| 6 | **待决策项保留** | 源文档的待决策项在产出中全部保留 | 100% |
| 7 | **格式规范** | 页签结构、标题层级、表格格式的规范性 | ≥ 80/100 |

### 评分等级

| 评分 | 等级 | 含义 |
|------|------|------|
| 95-100 | 🟢 A | 优秀——信息完整，格式规范 |
| 85-94 | 🟢 B | 良好——基本完整，有微小遗漏 |
| 70-84 | 🟡 C | 合格——有明显遗漏但可接受 |
| 50-69 | 🟠 D | 需改进——有较多遗漏 |
| 0-49 | 🔴 F | 不合格——严重信息丢失 |

---

## 与 AI 助手的集成规范

### 何时触发质量检查

以下情况下，**必须**在文档生成后运行质量检查：

1. 使用 `game-design-doc-template` skill 从源文档生成策划案时
2. 用户明确要求"检查文档质量"时
3. 将非标准格式文档转换为标准格式时

### 检查流程

```
Step 1: 源文档指纹提取
        ─ 如果源文档是 xlsx: extract_fingerprint_from_xlsx()
        ─ 如果源文档是文本/MD: extract_fingerprint_from_text()
        ─ 记录规则数、表格数、数值、标题等

Step 2: 产出文档指纹提取
        ─ extract_fingerprint_from_xlsx(产出文件路径)

Step 3: 对比与报告
        ─ quality_check() 一站式完成对比和报告生成
        ─ 报告自动保存到产出文档同目录

Step 4: 结果处理
        ─ 如果 passed=True: 告知用户检查通过，附报告链接
        ─ 如果 passed=False: 列出未通过项，给出修复建议
        ─ 如果评分 < 70: 建议重新生成或手动补充
```

### 报告输出

- 报告文件名：`{文档名}_质量报告.md`
- 报告位置：与产出文档同目录（默认 `G:/project_output/`）
- 报告格式：Markdown，包含总览表、详细分析、指纹对比、改进建议

---

## CLI 使用

```bash
# 基本用法
python scripts/quality_gate.py 源文档.xlsx 产出文档.xlsx

# 指定报告目录
python scripts/quality_gate.py 源文档.xlsx 产出文档.xlsx G:/project_output

# 示例
python scripts/quality_gate.py "G:/project_output/原始需求.xlsx" "G:/project_output/签到系统策划案.xlsx"
```

---

## 依赖

- `openpyxl >= 3.1.0`（与 game-design-doc-template 共享，无需额外安装）

---

## 自定义阈值

可通过传入 `thresholds` 参数调整检查严格度：

```python
# 宽松模式
loose = {
    "rule_coverage_min": 0.80,
    "content_line_ratio_min": 0.60,
    "table_coverage_min": 0.80,
    "format_score_min": 70,
}

result = quality_check(source, output, thresholds=loose)

# 严格模式
strict = {
    "rule_coverage_min": 0.95,
    "content_line_ratio_min": 0.85,
    "table_coverage_min": 0.95,
    "format_score_min": 90,
}

result = quality_check(source, output, thresholds=strict)
```
