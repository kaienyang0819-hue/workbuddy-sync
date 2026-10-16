# AI 情报日报 自动化执行记录

## 2026-10-08（首次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-08.html（单文件自包含，10 条）
- 窗口：2026-09-25 ~ 2026-10-08
- 信源：小红书 MCP（3 关键词，AI NPC/AI队友/AI视频工作流 搜索超时降级）、B站（2 条实测）、X feed（无 AI 高价值）、全网搜索（多轮）、KM（无游戏 AI 高价值）、官方/聚合经媒体交叉核实
- 关键教训：
  1. 小红书 search_feeds 返回热度排序（非时间排序），顶部常为 8 月底旧内容，必须读详情取 `time` 字段（Unix 毫秒）严格过滤 14 天窗口；"腾讯IEG重组AI游戏部"实为 8/24、AI陪伴 Bside 为 9/4，均超窗剔除。
  2. 小红书"AI NPC / AI队友 / AI视频工作流"带空格关键词会 SIGTERM 超时；"AI游戏/AI陪伴/AI工具实测"可正常返回。
  3. B站 pubdate 用 `curl https://api.bilibili.com/x/web-interface/view?bvid=XXX` 取 pubdate 字段判断窗口。
  4. 日期核对用 `date -d @<秒>` 转本地时区，勿心算。

## 2026-10-09（第二次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-09.html（单文件自包含，9 条）
- 窗口：2026-09-25 ~ 2026-10-09
- 信源：小红书 MCP（AI游戏/AI陪伴/AI工具实测/AI队友 4 关键词，均可用）、B站、X feed（search 404 降级 feed）、官方 Release（OpenAI/Google-Unity/Anthropic 三方核实）、全网搜索、KM（收录 3 条）
- 企业微信：成功发送文件消息给杨凯（whoami 取到 chat_id=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q；media upload 成功；send 返回 success:true）
- 关键教训：
  1. wecom media upload 的 file_path 必须用正斜杠绝对路径（G:/...），反斜杠会被 JSON 转义吃掉导致 893001 报错。
  2. 本次重大事件密集：GPT-6+Intelligent UI（10/7）、谷歌 Playground+Unity Spark（10/7）、Claude Haiku 5.5（10/7）三大官方发布同窗，为高价值主体。
  3. 小红书详情 get_feed_detail 单条可能耗时 2-3 分钟超时被后台化，应批量并行 + 用 grep 只取 title/desc/time 字段。
  4. "和平精英 AI 队友批量下架"仅单一社区源（3赞小号），需标「待核」且注明低可信度，不能当事实。

## 2026-10-10（第三次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-10.html（单文件自包含，8 条）
- 窗口：2026-09-26 ~ 2026-10-10
- 信源：小红书 MCP（AI游戏/AI队友/AI工具实测 可用；AI陪伴 超时）、B站、X feed（AI高价值少降级）、官方（OpenAI/Anthropic 核实）、全网搜索、KM（收录 ThinkFlow 等）
- 企业微信：成功发送文件消息给杨凯（media_id 上传成功，send 返回 success:true）
- 关键教训：
  1. 小红书端口检测用 curl 根路径会返 404（MCP 无根路由），应直接用 mcporter check_login_status 判断是否就绪，别被 404 误导重复启动。
  2. config.yaml 字段名是 twitter_auth_token/twitter_ct0（下划线），不是 auth_token/ct0；grep 时要用正确字段名否则 token 为空。
  3. 全网搜索 GPT-5.5 结果严重混淆：混入 4 月旧闻 + 自媒体"GPT-5.5 不存在是误称"；官方事实是 GPT-6+Intelligent UI（10/7）。务必以 openai.com/news 官方页为准，勿采信搜索摘要里的版本号。
  4. Epic Fortnite 42.30 AI NPC 工具的日期，个别媒体误标 10/9，权威技术源一致为 10/1，需交叉核实取多数源。

## 2026-10-12（第五次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-12.html（单文件自包含，10 条）
- 窗口：2026-09-28 ~ 2026-10-12
- 信源：小红书 MCP（AI游戏 关键词超时降级，AI队友/AI陪伴/AI NPC/AI工具实测 4 词可用）、B站、X feed（REA 逆向 Agent 10/11）、官方（OpenAI/Mistral/Google 多方交叉核实）、全网搜索、KM（互选巡检 Agent 工程实践 671631，本期核心）
- 企业微信：成功发送文件消息给杨凯（whoami 取 chat_id=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q；media upload 成功；send success:true）
- 关键教训：
  1. 小红书热度排序仍大量返回超窗旧内容（腾讯IEG 8/25、星布谷地 9/23、Tipsychat 9/22、AI陪伴新规 7/12 等），必须逐条 get_feed_detail 取 time 字段过滤，勿被标题/热度误导。
  2. 本期高价值主体是 OpenAI 安全风波（10/6-10/9 暂停训练+解雇3研究员+722数学手稿+年化营收500亿），属本周最具价值的 Agent 安全边界现实案例，对 AI 队友/沙箱权限设计直接映射。
  3. 去重：Claude Haiku 5.5（10/9已收）、DeepSeek Harness v0.2.1（10/11已收）、Fortnite 42.30 AI NPC（10/10已收）、Meta Muse（10/11已收）均跳过不重复收录。
  4. Tarkov 1.2.0.0 AI bot 大改（10/6）是游戏 AI bot（局内敌人）行为设计的真实迭代样本，贴合用户 AI bot/AI队友 分类，值得持续跟踪这类「非主流但具体」的游戏 AI 事件。

## 2026-10-11（第四次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-11.html（单文件自包含，8 条）
- 窗口：2026-09-27 ~ 2026-10-11
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴/AI NPC/AI工具实测 均可用，偶发超时重试成功）、B站（11家AI做33款游戏18万播放等实测）、X feed（Claude Opus 5.5+Blender+Unity 游戏开发工作流）、官方（Anthropic Haiku 5.5 10/7、DeepSeek Harness v0.2.1 10/3）、全网搜索、KM（Muse 爆火，热度265，本期核心条目）
- 企业微信：成功发送文件消息给杨凯（whoami 取 chat_id=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q；media upload 成功；send 返回 success:true）
- 关键教训：
  1. 小红书 get_feed_detail 报 "Inspected target navigated or closed" 的根因是 xsec_token 与 feed_id 不匹配——必须用同一次 search_feeds 返回的 id+xsecToken 配对，不能跨结果混用。
  2. 时间戳过滤是核心：本期小红书 AI陪伴/AI队友 大量热门帖超窗（鹅家AI陪伴 9/15、Bside 9/4、AI男友 5/18、Tipsychat 9/22、1.1亿人组队 5/25），务必逐条 date -d 转本地时间，勿被热度误导。
  3. KM 内部 "AI 观察：2026年9月AI圈动态" 是虚构未来观察（AI摘要已标注），不作为事实收录，仅 Muse 这类有真实数据+内部分析的才收。
  4. 小红书 xsecToken 是每篇笔记的访问凭证，字段名是 xsecToken（大写T），grep 时注意。

## 2026-10-13（第六次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-13.html（单文件自包含，9 条）
- 窗口：2026-09-29 ~ 2026-10-13
- 信源：小红书 MCP（5 关键词均可用）、B站（七日杀NPC模组 9/26 超窗剔除、伊莫全息AI队友 10/10）、X feed（Anthropic点名偷思维链 10/13 热议但事件9/10超窗）、KM（混元3D Hy3D 3.6 10/12，核心条目）、全网搜索+抓取（字节世界模型、索尼AI专利、REA）
- 企业微信：**发送失败**——media_url 上传成功，但 Dayuan 回「企业微信确认面板打开失败：企业微信版本过低。请升级后重试」，任务被用户 DECLINED/CANCELED。HTML 已生成，文件本身不受影响。
- 关键教训（重要）：
  1. **wecom-cli 已无 `message aibot send` 子命令**（历史记录 10/9~10/12 用的命令已失效）。当前 CLI 只有 auth/calendar/contact/disk/doc/mail/media/meeting/sheet/smartpage/smartsheet/todo/slide。发消息必须走 Dayuan（A2A）。
  2. 发文件消息的正确链路：`wecom-media-upload` 技能的本地代理上传（POST http://127.0.0.1:59414/a2a/upstream/e0b98a5dc8efdbcc/media/upload?media_type=file，multipart 字段名 media）→ 拿 media_url → A2ASendMessage 给 Dayuan（attachments[].url=media_url）。不要用 wecom-cli 的 `media upload`（那个返回 media_id，不是 media_url，无法给 Dayuan 用）。
  3. 授权人 chat_id 已变化：whoami 返回的授权真人用户 ID 现为 `wo65jOUwAA6plSAHz6yv_VnF9wADN1BQ`（历史记录里的 wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q 是旧值）。
  4. 本期高价值主体：字节世界模型首秀（10/11 美好奇妙夜 Tim 演示，张一鸣亲督，游戏是应用场景）、索尼 AI 自适应 NPC 专利（10/1 公开，直接映射用户 AI bot 设计）、混元3D Hy3D 3.6（10/12，游戏资产生产）、REA 逆向一周11.5万星（与黄一孟"AI反编译毁灭独立游戏"形成产业叙事）。

## 2026-10-13（补充：去重机制上线 + 重发成功）
- **去重库**：G:\project_output\ai_daily_report\dedup_history.json（JSON，记录已收录事件的「指纹」正则 + 主题 + 首次收录日期）。
- **去重规则（每次生成日报前必须执行）**：
  1. 先 Read G:\project_output\ai_daily_report\dedup_history.json，加载全部「已收录事件指纹」。
  2. 对每个候选条目的标题/事实，用指纹正则做匹配；命中即视为「已收录过」，**除非有重大新增量，否则剔除**。
  3. 若同一事件有重大新增量（新数据/新结论/新动作），可再次收录，但卡片内必须标注「上期已收录，本期更新」。
  4. 本次日报生成后，把**新收录**事件的指纹追加进 dedup_history.json（含首次收录日期），保持库持续更新。
- **【去重 ≠ 减量】保量规则（重要）**：去重只负责「过滤已收内容」，绝不能因去重导致日报条目骤减。要求：
  1. **去重后仍须保持 8~10 条高质量新增量**为目标；若去重后不足 8 条，说明本期采集广度不够，必须**扩大采集**（多轮换关键词、深挖 B站/X 长尾、补充官方更新与聚合源），而不是拿历史内容凑数。
  2. **采集阶段就要「过量采集」**：每个信源尽量多收候选（小红书 5 关键词都跑 + B站多关键词 + X feed 拉长到 25 条 + KM 多轮 + 全网多轮搜索），先求「候选池大」，再进去重过滤，这样过滤后仍有足量。
  3. **绝不为了保量把已收内容重新塞回去**——宁可当天明确写「今日高价值新增量仅 N 条」，也不重复收录。数量少是采集问题，不是去重问题。
  4. 若某天确实无足够高价值新增量，如实产出较少条目并在页脚说明，不凑数、不重复。
- **10-13 当日教训（已发生的重复，证明去重必要）**：10-13 日报重复收录了 4 条历史已收内容——①索尼AI自适应NPC专利（10-08/10-10 已收）②策划拆米哈游AI NPC（10-11 已收）③AI乙游盘点（10-12 已收）④和平精英AI队友下架（10-09/10-11 已收）。这些指纹已全部写入 dedup_history.json，后续不会再重复。
- **企业微信重发成功**：用户升级企微客户端后，10-13 日报已成功以文件消息发送（第二次 A2ASendMessage 成功）。注意：宿主代理端口会变（本次从 59414→55678），每次发文件前务必重新读 env 的 WECOM_MEDIA_UPLOAD_BASE_URL 和 A2AGetAgentCard 重新发现 Dayuan 的 agent_id（本次从 wecom-message-agent-8a30e5be → wecom-message-agent-a180176f），不要沿用上次的值。

## 2026-10-14（第七次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-14.html（单文件自包含，10 条）
- 窗口：2026-09-30 ~ 2026-10-14
- 信源：小红书 MCP（5 关键词均可用）、X feed（拉长 25 条）、官方+聚合（全网搜索多轮交叉核实）；B站降级（无窗口内高价值，6/2、9/19 超窗）；KM 未采集（连接器 MCP 工具未在本会话加载）
- 企业微信：**发送失败**——wecom-cli 已确认彻底移除 `message` 子命令（`message` 报 unrecognized subcommand；`identity whoami` 仍可用，返回授权人 ID wo65jOUwAA6plSAHz6yv_VnF9wADN1BQ）；发文件必须走 Dayuan A2A，但 A2A 工具（A2AGetAgentCard/A2ASendMessage/A2AGetTask）在当前自动化会话通过 ToolSearch 完全搜不到、未加载。HTML 已生成，文件不受影响。
- 关键教训（重要）：
  1. **A2A 工具在自动化会话可能未加载**：本次多次 ToolSearch（tool_names 精确 + queries 宽泛）均未返回 A2AGetAgentCard/A2ASendMessage，导致 Dayuan 发送通道不可用。后续执行前应先验证 A2A 工具是否可用；若不可用，如实标注发送失败，不伪造。
  2. 小红书 get_feed_detail 字段确认：`title`/`desc`/`time`（`time` 是 Unix 毫秒，`time/1000` 才是秒），用 python datetime.fromtimestamp 转本地时间过滤窗口。
  3. 本期高价值主体：Character.AI 破产+迪士尼2000万竞拍（10/12，头条，AI陪伴头号独角兽）、腾讯元器 11/9 停服（10/8 官方）、Meta Muse Wonder（10/12 前沿模型，上期 Muse 的模型底座重大新增量）、个人智能体赛道两周加速（dots/Cue/蚂蚁灵光/元宝助手/Spell）、Manus 5亿美元融资（10/8）、Claude 动态工作流（10/9）、星布谷地 AI NPC 三层记忆+超智记忆（10/6 上观深度披露）、PUBG Ally 上交大双脑架构（10/14）、DeepSeek 鲸鱼娘+和平精英 1.1亿/1770万数据、月之暗面 500亿估值 IPO。
  4. 去重新增 11 条指纹写入 dedup_history.json，后续不重复收录。

## 2026-10-14（网络恢复后重试确认）
- 状态：HTML 已生成且完整有效，无需重做采集；重试仅针对企业微信推送。
- 复检结论（与首次一致）：① identity whoami 正常返回授权人 ID wo65jOUwAA6plSAHz6yv_VnF9wADN1BQ；② wecom-cli 无 message 子命令，media upload 可用但只返回 media_id、无投递通道；③ wecom-media-upload 技能里 WECOM_MEDIA_UPLOAD_BASE_URL 仍是字面占位符（宿主未注入本地代理地址）；④ A2A 工具（A2AGetAgentCard/A2ASendMessage/A2AGetTask）经 ToolSearch 精确+宽泛多次检索均未返回，本自动化会话未加载。
- 结论：企业微信文件消息推送在本自动化会话无法完成，非偶发。HTML 交付不受影响。后续需在自动化会话中预置 A2A 工具 + 媒体上传代理注入，或改用其他已授权的发送通道。

## 2026-10-15（第八次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-15.html（单文件自包含，5条）
- 窗口：2026-10-02 ~ 2026-10-15
- 信源：小红书（服务启动、登录正常，5关键词搜索；Matrix-Game 4.0社区实测与GitHub交叉核验）、B站（搜索可用，发布时间API 412，未收录）、X feed（读取25条，无合格独立条目）、官方GitHub/Steam、TechCrunch/中国证券网/网易、KM（近7天查询并阅读全文Agent Builder评测指南）。官方模型厂商更新页与AIBARS未全面采集，已在日报注明。
- 企业微信：HTML原文件媒体上传成功；Dayuan回报文件消息已发出（sending_count=1、失败0），异步发送，无法确认最终接收。
- 本期核心：Matrix-Game 4.0开源实时神经渲染游戏；Idle Pixel Maids本地AI聊天；千问Go个人Agent；Hark Pro电脑操作Agent；Agent Builder质量评测。

## 2026-10-16（第九次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-16.html（单文件自包含，9 条）
- 窗口：2026-10-02 ~ 2026-10-16
- 信源：小红书（AI游戏/AI陪伴/AI工具实测 3 词，大量超窗剔除，仅不问凡尘销量1条有效）、B站（窗口内无高价值，均6月/5月超窗）、X feed（25条无AI高价值，降级）、官方（NVIDIA/xAI/可灵博客核实）、全网搜索多轮、KM（近7天，收录"别只会改prompt在工具层解决"）
- 企业微信：文件消息通过 Dayuan A2A 发送成功（media upload 直传成功返回 media_url；A2ASendMessage→A2AGetTask 回报"已向本人单聊发送成功，文件异步发送中"）
- 本期核心：NVIDIA Nemotron 3.5 Bolt（ACE第三代，上古卷轴5）、下一段路途本地AI NPC+Qwen3-4B、不问凡尘销量26万（上期更新）、可灵Kling 4.0、KM Agent工具层、Grok Voice 3.0、Mistlabs Ambi AI-to-AI、物外智趣儿童陪伴硬件、Kimi K3.1预告
- 关键教训：
  1. 媒体上传通道已恢复可用：本会话宿主代理端口为 62607，media upload 直传 URL hash 仍是 e0b98a5dc8efdbcc（与 10/13 一致，端口会变、hash 稳定）；A2A 工具（A2AGetAgentCard/A2ASendMessage/A2AGetTask）本会话已正常加载，Dayuan agent_id=wecom-message-agent-9727b5e9。
  2. 小红书热度排序仍大量返回超窗旧内容（腾讯IEG重组8/24、鹅家AI陪伴9/15、AI陪伴60%次留9/4），逐条 get_feed_detail 取 time 字段过滤，最终仅1条窗口内。
  3. B站搜索关键词结果多为6月/5月旧视频，pubdate 过滤后无窗口内高价值，无需硬凑。
