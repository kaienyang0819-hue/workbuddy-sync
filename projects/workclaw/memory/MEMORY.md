# 长期记忆

## 用户偏好

- 用户要求所有文件产出统一放在 `G:\project_output`
- 用户偏好使用标准化的文档格式和样式规范
- **文件版本管理规范（2026-04-17确立）**：每次迭代生成新版本文件时，必须主动删除之前的旧版本文件（同一产物的 v1.0→v1.1、v2.0→v2.1 等），只保留最新版。避免目录膨胀和版本混淆。

## 项目技能

### game-design-doc-template (系统策划文档标准格式)
- **位置**: `C:\Users\kaienyang\.workbuddy\skills\game-design-doc-template`
- **核心理念**: **通用动态生成** - 根据需求动态构建文档，不是固定模板
- **层级缩进规范（2026-03-27重构）**:
  - B列(2): 标题/单行内容/表格标题
  - C列(3): 规则标题(rule_title)
  - D列(4): 标签(label) / 待决策项(pending_item)
  - E列(5): 正文内容(content)
  - **所有函数已固定列号,调用时不传col参数**
- **样式体系（2026-03-27优化）**:
  - 5级蓝色渐变: 海军蓝→标准蓝→钢蓝→天蓝→浅蓝灰
  - 正文11pt深灰(#333333)，标题16/13/12pt
  - 规则标题有天蓝底色作为视觉锚点
  - 表格数据交替行色(#F2F2F2)
- **关键API**:
  - `add_doc_info(ws, row, label, value)` - 文档信息行
  - `add_version_table(ws, row, versions)` - 版本记录表格
  - `add_people_table(ws, row, people)` - 相关人员表格
  - `add_table(ws, row, title, headers, data)` - 一站式表格创建（支持列宽自适应）
  - `reset_auto_number()` + `add_content(..., auto_number=True)` - 自动递增序号
  - `add_content(..., is_sub=True)` - 子层级缩进内容（"  · "前缀）
- **规则三件套**: 1、规则说明 → 2、交互图 → 3、表格配置（**支持简化**：纯逻辑规则可省略空交互图/表格）
- **泛用性优化（2026-03-27）**:
  - 输出路径可配置化（环境配置区域）
  - 三件套简化规则（纯逻辑规则可省略空占位）
  - 页签1必填/选填指引
  - `add_content(is_sub=True)` 子层级缩进
  - `add_table` 列宽自适应（超过4列自动调整）
  - 规则标题命名规范（≤15字动宾短语）
  - 新增中等复杂度example（签到系统，展示全API综合用法）
- **通用模块菜单（2026-03-27更新）**: SKILL.md中包含21种标准模块（新增：界面入口/角色信息/聊天互动/成长体系/新手引导等），AI根据输入内容按需选用
- **构建决策流程（2026-03-27强化）**: 7步法 - 完整读取→逐页签映射→模块选择→结构判断→逐模块构建→同步页签3/4→完整性自检
- **信息完整性原则（最高优先级）**: 规范化≠精简化，源文档每条规则/数值/文案必须保留，生成后需做信息量对比检查
- **大文档处理**: 源文档多页签时必须逐页签完整读取，单页签>100行分批读取
- **图片提取修复**: xlsx中图片可能在xl/drawings/media/路径（非xl/media/），需多路径尝试
- **工作流**: 接收需求 → 分析内容 → 动态构建模块 → 生成文档
- **输入支持**: 文字描述、图片截图、xmind脑图
- **图片嵌入（2026-03-27新增）**: 
  - `add_image_in_rule()` - 规则内交互图嵌入(E列)
  - `add_image_under_title()` - 标题下方大图嵌入(B列)
  - 三种处理策略: 交互图→嵌入规则位, 数据图→嵌入标题下, 脑图→仅提取内容
- **Gotchas 段落（2026-04-09新增）**: 16条已知陷阱(G1~G16)，分4类：源文档读取/内容生成/API调用/完成度检查
- **SKILL.md 顺序优化（2026-04-09）**: Gotchas 移到最前面（紧跟核心理念后），低频参考（样式/API/内容规范）移到后半段，增加"── 以下为详细参考规范 ──"分隔线
- **⚠️ 拆分阈值**: 当 SKILL.md 超过 **1000行** 时，将 API 函数速查拆分为独立的 `docs/api-reference.md`，主文件保留索引链接

## IMA 知识库

- **凭证已配置**（2026-03-30）：存储在 `~/.config/ima/client_id` 和 `~/.config/ima/api_key`
- **用户知识库列表**（3个）：
  1. **个人知识库** — id: `n9xhZKkp1u4_DEZsdcpoGDflcNALz90Bl6xRKbJXy7g=`
  2. **测试用** — id: `GgBN5Zm3_WFgtSeeJbafJESxiGrRYfiJxFyVnmyJq3U=`
  3. **AI资讯追踪库(精华)** — id: `jW9jprbrK6AAYXI4_Emri0gTRW9US2SlZnnU_RWD6-k=`
- **注意**: `get_knowledge_base` 接口对这些知识库返回"没有权限"，需用 `search_knowledge_base` 获取基本信息
- **PowerShell 5.1 环境**: 必须用 `HttpWebRequest` + UTF-8 StreamReader 正确处理中文，`Invoke-RestMethod` 会乱码

## 公众号/小红书内容产品（2026-04-09启动）

- **定位**: AI领域的独立深度分析产品，面向公众读者（不局限于游戏，AI全领域）
- **信源方案**: `G:\project_output\公众号小红书_信源方案_v1.0.md`
- **核心原则**: 只追一手源头，不引用中文公众号/媒体；独立观点是核心壁垒
- **架构**: 独立定时任务（任务B），与AI大事件（任务A）并行
  - 任务A产出 → 作为任务B的线索入口
  - 任务B信源独立维护，修改不影响任务A
- **信源**: L0原始事实源35个 + L1一手深度报道7个 = 42个
- **内容策略**: 精选1-3个核心选题+深度分析（有主线串联+完整论证链），不是事件罗列
- **写作要求**: 深度 > 数量；读者读完要有"原来如此"的启发；每个观点要有推理链和数据支撑
- **更新频率**: 周更/不定期，AI评估内容质量后决定是否发布
- **发布方式**: 公众号→生成到草稿箱手动发 / 小红书→手动发
- **人设**: 阿雾（战争迷雾意象，亲近/理性/简洁），人设卡片 `G:\project_output\公众号小红书_人设卡片_阿雾.md`
- **任务B prompt草稿**: `G:\project_output\公众号小红书_任务B_prompt草稿.md`
- **阶段**: 信源方案+人设+prompt草稿已完成，下一步确认prompt → 注入自动化 → 试运行

## 工作习惯

- 用户重视文档的规范性和可读性
- 偏好统一的视觉标准和格式规范
- skill支持从xmind脑图提取内容并动态生成策划文档（测试通过：团竞段位追求系统）
- **Gotchas 标准行为（2026-04-09确立）**: 任何 Skill 在实际使用中踩到的坑，都主动整理进对应 SKILL.md 的 `## ⚠️ Gotchas（已知陷阱）` 段落。同一个坑出现过就补进去，新坑追加到表格末尾。这是所有 Skill 的标准维护流程。

### mygamedesignhelper (游戏系统策划 AI 工作流)
- **位置**: `C:\Users\kaienyang\.workbuddy\skills\mygamedesignhelper`
- **安装日期**: 2026-03-30
- **安全审计**: P2（安全），无任何红旗项
- **核心功能**: 覆盖从灵感脑暴到策划案定稿的全流程工作流
- **6个模块**:
  - 00-主编排: 流程路由、状态管理、用户交互入口
  - 01-知识库查找: 依赖外部 `team-kb` skill（需单独安装）
  - 02-XMind处理: XMind ↔ 结构化 Markdown 双向转换（scripts/xmind_toolkit/ + scripts/md2xmind.py）
  - 03-Excel处理: MD → Excel 转换（scripts/md2excel/）
  - 04-脑暴: 结构化需求脑暴（sub-skills/04-brainstorming/）
  - 05-策划案生成: 格式转换→需求澄清→定稿（sub-skills/05-spec-generation/）
  - 06-专家Review: 多角色专家评审（sub-skills/06-expert-review/）
- **主工作流**: 脑暴引导 → 结构化转换 → 需求澄清 → 专家评审 → 定稿 → 多格式输出（MD/XMind/Excel）
- **支持非线性入口**: 只脑暴 / 只澄清 / 只Review / 只转格式
- **触发关键词**: "策划案"、"需求文档"、"脑暴"、"头脑风暴"、"需求澄清"、"专家Review"、"策划案生成"、"转格式"、"转Excel"、"转XMind"、"游戏设计"、"系统设计"、"功能设计"
- **外部依赖**: openpyxl, PyYAML, xmind, xmindparser（Python包）
- **专家角色**: 挑战策（策划设计）、挑战克（客户端技术）、挑战侯（服务器技术）、挑战绘（UI/UX）
- **与 game-design-doc-template 的区别**: 本 skill 是全流程工作流（脑暴→澄清→评审→定稿），game-design-doc-template 是纯文档格式生成工具

### 游戏设计知识库 (game-design-kb)
- **位置**: `G:\project_output\game-design-kb\`
- **创建日期**: 2026-04-01
- **目标**: 系统化学习游戏设计全领域知识，打造AI游戏策划专家
- **知识体系**: 10大模块 — 01核心设计理论/02系统模块/03数值设计/04品类专项/05商业化/06玩家心理/07生产管理/08策划技术/09行业案例/10AI+游戏
- **知识卡片模板**: `_templates/card_template.md`（核心观点/方法论/案例/检查清单/元数据）
- **学习计划**: `LEARNING_PLAN.md` — 5个Sprint，10周覆盖全部模块基础
- **知识索引**: `INDEX.md` — 按标签/评级/时间检索
- **当前进度**: 100张卡片（Phase 1完成79张+Phase 2深化21张）
- **KM接入**: ✅ 已验证（2026-04-01），MCP server `km` → `https://prod.mcp.it.woa.com/paasfront_km-pro_woa_com/mcp`，Bearer Token认证
  - 工具: list-articles / show-article / hot-articles / list-groups / list-knowledges / show-knowledge 等
  - 核心资源: **腾讯游戏知识库** K吧 (#29321)
- **知识来源**: KM(深度接入50+篇) + GDC Vault + 机核GCORES + GameRes + 知乎
- **Phase 1完成**: 79张卡片，11/13能力达标，全部达到Lv.3应用级（2026-04-01）
- **Phase 2完成（2026-04-02）**: 四项核心能力全部达到Lv.7专业级
  - C1系统设计深化: ✅ 完成（20/20张，Lv.7达标）
  - C2数值设计深化: ✅ 完成（20/20张，Lv.7达标）
  - C5战斗设计深化: ✅ 完成（20/20张，Lv.7达标）
  - C13 AI+游戏深化: ✅ 完成（20/20张，Lv.7达标）
- **Phase 3完成（2026-04-03）**: 四项次核心能力达到Lv.7
  - 去重修复: ✅ 删除15个重复文件
  - C3商业化深化: ✅ ~18张 Lv.7（无畏契约/CSGO/帕鲁/暖暖/外观付费/GaaS等）
  - C6关卡设计深化: ✅ ~19张 Lv.7（三角洲GDC/赛博朋克/塞尔达/IPMT/11步法等）
  - C7叙事设计深化: ✅ 19张 Lv.7（艾尔登法环/博德之门3/三位一体/神话学/AI叙事等）
  - C4玩家心理深化: ✅ 19张 Lv.7（心流/注意力/Bartle/FOMO/斯金纳箱/社交心理等）
- **Phase 4完成（2026-04-03）**: 五项支撑能力全部达到Lv.7 → 13×Lv.7全满级
  - C8 UX交互深化: ✅ 21张 Lv.7（HUD/手感/无障碍/动效/音频UX等）
  - C9 文档表达深化: ✅ 20张 Lv.7（系统文档/需求/数值/竞品/提案/评审等）
  - C10 数据分析深化: ✅ 20张 Lv.7（AB测试/漏斗/留存/付费/SQL/可视化等）
  - C11 项目管理深化: ✅ 20张 Lv.7（敏捷/里程碑/排期/复盘/工具链等）
  - C12 技术素养深化: ✅ 20张 Lv.7（帧同步/引擎/渲染/热更/物理/寻路/反作弊/AI等）
- **总卡片数**: ~250张（Phase 1:79 + Phase 2:48 + Phase 3:54 + Phase 4:77 - 去重15 + 补齐）
- **Lv.7能力数**: 13项全满级（C1~C13）
- **KM文章引用**: 120+篇

### team-kb (团队知识库管理)
- **位置**: `C:\Users\kaienyang\.workbuddy\skills\team-kb`
- **安装日期**: 2026-03-30
- **知识库仓库路径**: `G:\project_output\team-knowledge-base`
- **配置文件**: `~/.workbuddy/skills/team-kb/.kb-config.json` → `repo_path` 指向仓库
- **CLI 脚本**: `scripts/kb-search.py`（支持 search / get 命令）
- **5 个默认分类**: 技术架构、业务流程、产品设计、项目管理、通用知识
- **知识库当前状态**: 空（刚初始化，无知识点）
- **与 mygamedesignhelper 的关系**: 作为 01-知识库查找模块的外部依赖，提供只读检索服务

## AGF — Agent Governance Framework（AI 助手行为治理框架）

- **灵感来源**: Everything Claude Code (ECC)，100K+ Stars
- **核心理念**: AI 助手的可靠性不靠模型能力，靠工程化约束
- **安装日期**: 2026-04-01
- **三个组件**:

### agf-quality-gate（策划文档质量门禁）
- **位置**: `~/.workbuddy/skills/agf-quality-gate/`
- **核心脚本**: `scripts/quality_gate.py`
- **功能**: 文档指纹提取 → 对比 → 质量报告自动生成
- **7项检查**: 规则覆盖率/内容行覆盖率/表格覆盖率/数值一致性/模块标题覆盖/待决策项保留/格式规范
- **API**: `quality_check(source_path, output_path)` 一站式调用
- **CLI**: `python quality_gate.py 源文档.xlsx 产出文档.xlsx [报告目录]`
- **配置**: `config/quality_rules.yaml`，支持 default/strict/loose 三档
- **已测试通过**: 完整文档100分A级，故意不完整文档44分F级

### agf-research-workflow（调研标准化工作流）
- **位置**: `~/.workbuddy/skills/agf-research-workflow/`
- **5阶段流程**: 定义(Scope)→采集(Gather)→验证(Verify)→分析(Analyze)→交付(Deliver)
- **三种深度**: quick(3-5源) / standard(5-10源) / deep(10-20源)
- **质量自评**: 5维度100分制
- **标准化报告模板**: 9个章节固定结构

### agf-orchestrator（多技能编排引擎）
- **位置**: `~/.workbuddy/skills/agf-orchestrator/`
- **7个预定义管道**: full_game_design/doc_standardize/research_report/research_to_design/expert_review/brainstorm_only/quality_check_only
- **意图路由**: 关键词匹配+语义推断，自动匹配管道
- **状态管理**: YAML状态文件+checkpoint，支持断点续传
- **数据桥接**: output_key→input_from 统一协议
- **管道存储**: `G:/project_output/.agf/pipelines/`

## 学习闭环系统（2026-04-14 搭建完成）

- **灵感来源**: Hermes Agent (Nous Research, 78K Stars) 的自进化架构
- **核心理念**: 学习闭环是系统底层能力，不是独立 Skill。嵌入 SOUL.md，每次 session 自动生效
- **设计方案**: `G:\project_output\hermes_learning_loop_design.md`
- **路线图**: `G:\project_output\hermes_learning_loop_roadmap.md` (v2.0)
- **实施状态**: Phase 0-3 ✅ 全部完成，Phase 4（向量检索）按需
- **闭环四步**: Evaluate(评估) → Extract(提取) → Route(分流) → Persist(存储)
- **脚本位置**: `g:\workclaw\.workbuddy\scripts\` (9个Python文件)
  - `loop_runner.py` — 闭环主入口（一键串联全链路）
  - `evaluator.py` — 任务评估器（综合得分1-10）
  - `extractor.py` — 经验提取器（结构化JSON）
  - `router.py` — 分流决策器（create_skill/improve_skill/extract_pattern/store_episode）
  - `episode_store.py` — 情景记忆 CRUD
  - `pattern_store.py` — 语义模式库管理
  - `skill_stats.py` — 技能使用统计
  - `skill_evolver.py` — 技能进化器（扫描20个已安装skill）
  - `nudge.py` — 周期自省（剪枝/归档/周报）
- **数据位置**: `g:\workclaw\.workbuddy\learning\`
  - `config.json` — 全局配置（阈值/权重/衰减规则）
  - `semantic-patterns.json` — L3 语义模式库（当前2个active pattern）
  - `skill-stats.json` — 技能使用统计
  - `episodes/` — L2 情景记忆（当前3个episodes）
  - `reports/` — 自省周报
- **分流规则**: score≥7 + steps≥3 + 无复用 → 创建新Skill（需用户确认）；复用skill+有问题 → 改进Gotchas；有通用模式 → 写入patterns；兜底 → 存episode
- **遗忘机制**: 成功+0.05, 失败-0.10, 30天未用-0.02/月, <0.3且6月未用→deprecated
- **自动化**: 每周一 9:00 执行 nudge.py 自省任务
- **Windows注意**: 运行Python脚本需设 `$env:PYTHONUTF8=1` 避免GBK编码问题
