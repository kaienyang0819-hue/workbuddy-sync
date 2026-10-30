# WorkBuddy 双周自省 - 执行记录

> 路径说明（第 15 期起）：本文件为任务指令指定的规范路径 `G:\project_output\.workbuddy\memory\automations\workbuddy\memory.md`。
> 第 1~14 期的历史记录仍在旧路径 `G:\project_output\.workbuddy\automations\workbuddy\memory.md`（sync.ps1 不同步该目录）。
> 两处并存属路径漂移遗留问题，建议后续合并（见 2026-10-29 报告发现 7）。

## 2026-10-29 18:00（第15次）

- 状态：✅ 报告生成完成
- 报告路径：`G:\project_output\self-reflect\2026-10-29.md`
- 发现数：**10 条（高优 3、中优 5、低优 2）**；上期执行率 **8%**（1/12，↓ from 20%）
- 关键变化：
  - 🟢 **系统层全面翻正**：10/15~10/29 共 56 次运行，成功 53、失败 2（均在 10/15 上午，`-32603 / Internal error`）→ **成功率 96.4%**（上期失败率 62%）。三条产出线零断档：ai_daily 15 天、km 16 天、trending 18 天。日报推送 10/21 起连续 9 天 `errcode=0`
  - 🔴 **推翻上期处方（本期最重要）**：失败率归零**未做任何 harness 改动** → 上期"根因=平台 524"判断正确，但"加重试 + 落盘自检"开错。真正有效的是用户 10/20 自建 `wecom_bot_push.py` 把"需审批的 A2A"换成"免审批的机器人直连"。**机制修订：换依赖 > 加补偿**
  - 🔴 **诊断字段第二次踩坑**：上期把 5 个已 `deleted_at` 的任务误判为"僵尸 ACTIVE"（`ai`/`ai-2` 6/11、`km-ai-2` 7/1、`automation-2` 8/11、`automation-1784084795294` **10/16**）→ **读表三问**（软删除 / 内层错误 / 状态修饰字段）
  - 🟢 **成本首次可量化**（`session_usage` join `metadata_json.sessionId`；旧 `usage.byCategory` 已失效）：两周 877.7 credits / 507 万 tokens，`f216f548` 独占 **70%**（38.1 credits/次、150k tokens/次）
  - 🟢 **去重库成线性成本项**：`dedup_history.json` 38.9KB / 182 条 / ≈10.9k tokens 每次读入（占单次 7.3%），日均 +600 tokens，**无分片/无归档/无备份**
  - 🟢 **社区源连续 7 天零产出**（约 95 次检索净产出 0 条），却仍占 prompt 47% 的信源预算 → 建议降级为每周 2 次抽样
  - 🟢 **信源可信度教训 5 天 4 次**（壹语前研 / AI OPC 社区 / llmgateway / 虎扑帖）从未沉淀 → 建议插入分级 + "发布日期以厂商官方日志为准"硬规则
  - 🟡 **63 个 skill 全量元数据加载**（≈6.3k tokens/次）、4 个 `skill_2053*` 来源不明目录（第 6 期）、Snyk 36.82% 缺陷率
  - 🟡 **学习闭环事实死亡**：0 active pattern、candidate use_count=0、2 条 episode 停在 9/3、周报 W41~W44 逐字节等长 1038B、剪枝预检误报"状态良好"（实际 2/3 deprecated）
  - 🟡 **自省 prompt 从未更新**（721 字符原文，仍写"只出报告"）→ A1-4/A1-5 死锁：改 prompt 的建议卡在没人改 prompt
  - 🟡 **凭证边界错位**：`wecom_bot_config.json`（bot secret 明文）在 `ai_daily_report/`，sync.ps1 只同步 memory/learning/scripts 故 **secret 未泄露（全库扫描 0 命中）**；但 chatid 已随 memory 进公开 GitHub（1 处，低危）
  - 🔵 **记忆保护**：`archive/` 仍空（168 天）、32 个 daily memory（最早 4/30，182 天）、钉住机制不存在、`tasks/` 空
  - 🟡 **10/23~10/29 无交互式工作日志**（7 天），但同期 `f216f548` 执行记录每日更新 → 记录能力正常，是**写错了地方**；建议 daily memory 只记"人做的决策与产出"
  - 🟢 **行业信号**：10/22 Anthropic 将 Agent Skills 捐给 **AAIF（Linux Foundation）**；10/23 MCP TS SDK 2.4.0 落地 **SEP-2640（Skills over MCP，skills/list + per-file SHA-256）**；渐进披露 ~100 tokens/skill 元数据、body <5k；Cloudflare Code Mode 把 2,594 工具 117 万 tokens 压到约 1,000；Snyk 扫描 3,984 skill，36.82% 有缺陷、13.4% 含 CRITICAL
- 健康度：**7.6/10**（↑ from 7.0）—— 可靠性 9、推送 9；配置时效性 3、学习闭环 2
- 本期用户工作：地铁逃生·专属 AI 队友收益风险分析（10/16，多轮口径纠偏）、日报推送通道方案 C 改造（10/20，逆向长连接协议）、学习闭环自省（10/19 W43、10/26 W44）
- [PENDING_REVIEW] 报告待用户审阅
