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

## 个人知识库（2026-06-24搭建，2026-06-29升级多库架构）
- 架构：WorkBuddy加工 + Obsidian可视化，.md文件为桥梁，多知识库独立管理
- **游戏+AI库**：`D:/obsidian/knowledge-gamedesign/`（00-inbox / 01-ai-gaming / 02-llm-tech / 03-competitive / 04-game-design / 05-industry / 06-patterns）
- **投资库**：`D:/obsidian/knowledge-investment/`（00-inbox / 01-宏观 / 02-行业 / 03-个股 / 04-策略 / 05-复盘 / 06-学习）
- 入库Skill：`knowledge-entry` v2.0（支持多库自动路由，KM链接/网页URL/手动内容/westock数据）
- 每个知识库可作为独立Obsidian Vault打开
