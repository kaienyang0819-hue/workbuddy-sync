# MEMORY

## DESIGN.md 设计规范（2026-07-10 创建）
- 项目根目录 `g:\gpt_test\DESIGN.md` 是 HTML 产出的统一设计规范
- 基于 Google DESIGN.md 标准格式：YAML token + Markdown 设计理念
- 风格：浅色主题、#667eea 靛蓝强调色、Microsoft YaHei 系统字体、卡片式布局
- `design-md-apply` 技能自动在生成 HTML 时读取并应用此文件
- 修改 DESIGN.md 中的 token 即可全局切换所有 HTML 产出的风格

## 用户表达与交付偏好
- 2026-04-22：面向业内人士做分享时，用户更强调“思路、判断、体验洞察”，不希望内容过多落到具体设计细节、工程做法或教学式拆解；表达要站在分享观点而非教别人怎么做的口径上。
- 2026-04-22：在分享材料中，数据可以作为支撑，但不要求每一页都用量化证明，重点是把价值判断和体验认知讲透。

## GitHub Trending 监控报告格式要求（2026-08-03）
- 报告输出路径：`G:\project_output\github-trending\github_trending_YYYY-MM-DD.md`
- 报告结构要求：
  1. 先给高匹配仓库的精华摘要（3-5句话概括今日最值得关注的方向）
  2. 对高匹配（score ≥ 5）仓库逐个给出一句话价值判断：对用户（游戏策划 + AI 产品经理）的具体用处
  3. 如果发现特别值得关注的项目（score ≥ 8 或今日 stars ≥ 500），用醒目方式标注
  4. 每个高匹配仓库加「与你相关」的点评
- 脚本路径：`g:\gpt_test\github_trending_monitor.py`
- JSON缓存：`g:\gpt_test\github_trending_latest.json`

## GitHub Trending 趋势模式（2026-08-09 更新）
- **Agent Skills 生态持续爆发**：mattpocock/skills（21万星）、addyosmani/agent-skills（8.5万星）等技能标准化项目持续高增长
- **自改进型 Agent 成为主流**：PrimeIntellect-ai/prime-agent 展示 RLM（强化学习模型）在长时程编码任务中的持续优化能力
- **多 Agent 协作框架成熟**：TauricResearch/TradingAgents（9.6万星）在金融领域的成功应用表明多Agent架构已具备商业化能力
- **企业级 Agent 基础设施完善**：Google/skills 等大厂开始系统性布局 Agent 生态
- **游戏策划相关价值**：自改进Agent可应用于游戏测试和剧情生成；技能路由标准化可直接复用于游戏AI行为模块设计；多Agent协作架构可映射到游戏AI的多角色系统

## 个人知识库（2026-06-24搭建，2026-06-29升级多库架构）
- 架构：WorkBuddy加工 + Obsidian可视化，.md文件为桥梁，多知识库独立管理
- **游戏+AI库**：`D:/obsidian/knowledge-gamedesign/`（00-inbox / 01-ai-gaming / 02-llm-tech / 03-competitive / 04-game-design / 05-industry / 06-patterns）
- **投资库**：`D:/obsidian/knowledge-investment/`（00-inbox / 01-宏观 / 02-行业 / 03-个股 / 04-策略 / 05-复盘 / 06-学习）
- 入库Skill：`knowledge-entry` v2.0（支持多库自动路由，KM链接/网页URL/手动内容/westock数据）
- 每个知识库可作为独立Obsidian Vault打开

## AI事件雷达任务口径（2026-09-07）
- 目标是扩展用户的 AI 能力与应用视野，不以游戏迁移性作为事件筛选门槛；游戏关联仅在自然成立时作为补充注释。
- 不预设四类内容配比：先尽量广地收集，再按“热点度 + 应用价值”为主给出优先级，最终由用户决定关注重心。
- 信源不按官方优先的单一层级排序：社区、开发者/创作者平台、GitHub、产品讨论等是发现具体 case 的关键入口；官方材料、案例参与方和多源交叉用于事实核验。需区分“发现渠道”与“验证依据”。
- Case 收录服务于“视野拓展”，不是可用性评估：只需说明 Case 是什么、谁在做、AI 被用于何种新颖/独特的事及来源证据；不要求披露具体流程、效果/效率、限制或失败点，也不据此筛除。
- AI事件雷达的Case必须以社区平台为主来源；官方公告只能用于模型/产品事实核验，不能替代社区Case。后续需优先打通 X、Reddit、GitHub/Hacker News/Product Hunt、B站、小红书等社区发现网络后再正式运行。
