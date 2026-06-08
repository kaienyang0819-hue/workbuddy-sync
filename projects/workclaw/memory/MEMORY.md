# 长期记忆

## 用户画像与沟通偏好

- 用户：杨凯，常用称呼“凯”，腾讯游戏策划，同时承担高校 AI NPC 课程教学工作。
- 必须使用中文，尽量避免英文句子；偏好直接、简洁、先结论后细节。
- 偏好结构化输出：表格优先，其次列表，再次段落。
- 重视深度、逻辑主线、因果链和目标受众视角，不喜欢泛泛而谈。
- 高风险任务先给方案清单确认；低/中风险任务可直接执行并交付结果。
- 修改文案或方案前，先从目标受众视角评估优劣，再执行。
- 幻灯片和汇报材料要求压缩但不改变原意，逻辑要收紧，适合管理层阅读。
- 计算、分析、打分、对比类任务偏好表格或 Excel；可视化偏好 HTML。
- 所有文件产出统一放在 `G:\project_output`。
- 文件版本管理：同一产物迭代时主动删除旧版本，只保留最新版，避免版本混淆。
- 安装新 Skill 前需先评测；评测工具：`G:\project_output\skill-quality-gate\skill_evaluator.py`，B 级及以上可安装。

## 当前长期工作背景

- 游戏工作：负责混元 AI 队友相关项目，重点关注 AI 队友决策能力、角色对齐评测、产品卖点说明及管理层汇报。
- 重点游戏场景：《和平精英》国服绝地指挥模式及 AI 功能，如小马神、AI 军犬；不关注 PUBGM 国际服。
- 当前策划重点：2 真人 + 2 大模型 AI NPC 组队玩法，由“1 真人 + 1 专属 AI”扩展到双人双 AI，希望支持真人指挥自己 AI、指挥队友 AI，并形成四人聊天氛围。
- 教学工作：面向高校学生讲授 AI NPC 课程，作业方向包括产品拆解分析与和平精英 AI NPC 延展设计。
- 当前教学任务：曾处理 8 份学生作业打分，偏好 HTML 汇总。
- 情报工作：持续运营 AI 游戏情报早报自动化，关注 AI 大模型、AI+游戏应用、行业商业动态、论文研究，产出目录 `G:\project_output\ai-game-daily\`。
- 当前早报 prompt：`G:\project_output\情报早报_优化prompt_v2.md`，已加入 AIHOT 19 个增量信源。
- 公众号/小红书内容产品：定位为 AI 领域独立深度分析，核心原则是只追一手源头，重独立观点，不做事件罗列。

## 工作环境与路径

- Windows 桌面版 WorkBuddy，工作区：`G:\workclaw`。
- 用户级 Skills：`C:\Users\kaienyang\.workbuddy\skills\`。
- 项目产出：`G:\project_output`。
- 工作记忆：`G:\workclaw\.workbuddy\memory\`。
- WorkBuddy 配置与身份文件常见位置：`C:\Users\kaienyang\.workbuddy\`。
- 终端偏好：用户本质是 CLI 思维，偏好命令行工作流。

## 核心 Skill 与工具

### game-design-doc-template

- 位置：`C:\Users\kaienyang\.workbuddy\skills\game-design-doc-template`。
- 用途：根据输入动态生成系统策划文档，不是固定模板。
- 关键原则：规范化不等于精简化，源文档每条规则、数值、文案必须保留。
- 文档结构：规则三件套为规则说明、交互图、表格配置；纯逻辑规则可简化。
- Excel 层级：B 列标题，C 列规则标题，D 列标签或待决策项，E 列正文。
- 大文档处理：多页签必须逐页签完整读取，单页签超过 100 行分批读取。
- Gotchas：踩坑要补进 SKILL.md 的 Gotchas 段落。

### mygamedesignhelper

- 位置：`C:\Users\kaienyang\.workbuddy\skills\mygamedesignhelper`。
- 用途：游戏系统策划 AI 工作流，覆盖脑暴、结构化转换、需求澄清、专家评审、定稿和多格式输出。
- 适用场景：策划案、需求文档、脑暴、专家 Review、转 Excel、转 XMind、系统设计、功能设计。
- 与 game-design-doc-template 的区别：前者是完整工作流，后者是文档格式生成工具。

### team-kb

- 位置：`C:\Users\kaienyang\.workbuddy\skills\team-kb`。
- 知识库仓库：`G:\project_output\team-knowledge-base`。
- 用途：作为 mygamedesignhelper 的外部知识检索依赖。

### AGF 行为治理框架

- agf-quality-gate：策划文档质量门禁，检查规则覆盖、内容覆盖、表格覆盖、数值一致性等。
- agf-research-workflow：调研标准化流程，分定义、采集、验证、分析、交付。
- agf-orchestrator：多技能编排引擎，支持预定义管道和状态管理。

## 游戏设计知识库

- 位置：`G:\project_output\game-design-kb\`。
- 目标：系统化学习游戏设计知识，打造 AI 游戏策划专家。
- 知识体系：核心设计理论、系统模块、数值设计、品类专项、商业化、玩家心理、生产管理、策划技术、行业案例、AI+游戏。
- 进度：约 250 张知识卡片，13 项能力达到 Lv.7，覆盖系统、数值、战斗、商业化、关卡、叙事、玩家心理、UX、文档表达、数据分析、项目管理、技术素养、AI+游戏。
- KM 核心资源：腾讯游戏知识库 K 吧。

## IMA 知识库

- 凭证已配置在 `~/.config/ima/client_id` 与 `~/.config/ima/api_key`。
- 常用知识库：个人知识库、测试用、AI资讯追踪库(精华)。
- 注意：`get_knowledge_base` 对部分知识库可能返回无权限，需用 `search_knowledge_base`。
- PowerShell 5.1 处理中文时优先用 `HttpWebRequest` + UTF-8 StreamReader，避免 `Invoke-RestMethod` 乱码。

## 学习闭环系统

- 位置：`G:\workclaw\.workbuddy\learning\` 与 `G:\workclaw\.workbuddy\scripts\`。
- 核心流程：Evaluate → Extract → Route → Persist。
- 关键脚本：`loop_runner.py`、`evaluator.py`、`extractor.py`、`router.py`、`episode_store.py`、`pattern_store.py`、`skill_stats.py`、`skill_evolver.py`、`nudge.py`。
- 自动化：每周一 9:00 自省，包含 pattern 剪枝、episode 归档和周报。
- Windows 注意：运行 Python 脚本时需设置 `PYTHONUTF8=1`，避免 GBK 编码问题。

## 输出与质量标准

- 报告/文档优先 Markdown，需要时再转 PPT、Excel 或 HTML。
- 关键判断应说明依据与置信度，尤其是情报、竞品、趋势、技术选型类任务。
- 对外分享口径要偏观点表达，不要像教程或工程拆解。
- 面向学生出题时目标要清晰，避免模糊地带让学生跑偏。
- 处理外部反馈前先做分析，不直接改。
- 批量上传文件后统一通知处理。

## 维护记录

- 2026-05-09：长期记忆因过长被压缩，已合并重复内容并保留当前仍有用的偏好、项目、路径和核心技能信息。
