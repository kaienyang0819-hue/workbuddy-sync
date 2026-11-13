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

## 2026-10-17（第十次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-17.html（单文件自包含，10 条）
- 窗口：2026-10-03 ~ 2026-10-17
- 信源：小红书 MCP（5 关键词，窗口内仅 2 条有效：Jev 喵呜岛 10-10、6个AI共享记忆 10-14）、B站（无窗口内高价值，降级）、X feed（25条无 AI 高价值，降级）、官方（NVIDIA blog Super VL、商务部 48号公告）、全网搜索多轮交叉核实、KM（AdBuddy Agent 7个坑，热度433）
- 企业微信：**发送失败**——media upload 直传成功（返回 media_url），A2ASendMessage→A2AGetTask 回报「该操作需要你在对话界面审批，但等待审批超时，操作已自动取消。文件消息尚未发出」。HTML 已生成，文件不受影响。
- 关键教训：
  1. **GPT-6.1 Astra 推迟是 9/28-29 事件（华尔街日报/路透社 9/29 报道），超窗**。The Neuron 10-16「AI News Today」把它列为当天新闻是回顾性质，实际事件日期必须核实，不能按报道日期误判为窗口内。
  2. **NVIDIA Nemotron 3.5 家族本期新发 Super VL（120B 多模态 Agent 模型）**，与上期已收的 Bolt（边缘对话小模型）是不同模型，属新增量可收，但卡片需标注「同家族，Super VL 为旗舰」。
  3. 小红书「AI原生游戏」关键词召回质量高（深圳Soda Game/李飞飞Astrocade混想局/Death by AI/Talespark等），但绝大多数超窗（6-9月），逐条 get_feed_detail 取 time 过滤后仅 Jev 喵呜岛（10-10）在窗口内。
  4. 本期高价值主体密集于 10-16（周五）：商务部 AI 出口管制、155款拒绝豆包、Meta Muse Spark Open、NVIDIA Super VL、GPT-Live-1.1、Veo 3.1、MAI-Base-2 等，为「周五发布潮」。

## 2026-10-18（第十一次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-18.html（单文件自包含，9 条）
- 窗口：2026-10-04 ~ 2026-10-18
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴/AI工具实测 4 词，窗口内有效少）、B站（1条小王子3D）、X feed（25条，DeepSeek官方公告）、全网搜索多轮、KM（近7天，收录助手调研671797+Miora 671756）
- 企业微信：**发送失败**——media upload 直传成功（errcode 0，返回 media_url），A2ASendMessage→A2AGetTask 回报「审批超时未执行，文件消息没发出去」。HTML 已生成，文件不受影响。
- 关键教训：
  1. A2A 工具本会话已加载（agent_id=wecom-message-agent-b7c6e20e）；媒体上传本地代理端口本会话为 57329（hash 仍 e0b98a5dc8efdbcc）。发送仍需对话界面审批，无人值守环境下连续两期（10-17/10-18）审批超时失败，非偶发。
  2. 本期核心：DeepSeek V4.1-Flash-1017（10-17，游戏开发强化+Search/Fetch API 开放）、腾讯混元 Hy-Memory 2.0 开源（10-15，记忆写入模型 3B 激活超 Opus5，直接映射 AI NPC 记忆）、DeepMind 4×Gemini 27h 通关 Minecraft（10-15 论文，多智能体+游戏）。
  3. 去重新增 9 条指纹写入 dedup_history.json。

## 2026-10-19（第十二次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-19.html（单文件自包含，9 条）
- 窗口：2026-10-05 ~ 2026-10-19
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴/AI NPC 4 词，改用 filters sort_by="最新" 直取窗口内内容，命中率大幅提升）、B站（窗口内无高价值，降级）、X feed（DeepSeek 排名第一）、官方+聚合（wccftech/GamesPress/CSDN/中央社/arXiv 多方核实）、KM（近7天高价值多已收录，本期无新增）
- 企业微信：**发送失败**——media upload 直传成功（errcode 0，返回 media_url），A2ASendMessage→A2AGetTask 回报「审批超时未执行，文件消息没发出去」。HTML 已生成，文件不受影响。
- 本期核心：哈佛 MPT 去中心化智能体竞价框架（10/15 arXiv）、NPCTalk GTA V AI NPC 实时语音开源（10/16）、堀井雄二 30 分钟 Claude 做游戏《取调室的小宫》（10/11）、Bot Colony Redux 无脚本对话游戏（10/14）、凤华录 Funloom AI 宫斗文游（10/18 社区）、One Way Mirror AI 0.9.5 AI NPC 接话速度（10/11）、阶跃 Step 5 开源权重（10/15）、DeepSeek V4.1-Flash-1017 登顶 Code Arena（10/18 上期更新）、Meta Muse 虚拟女友现象（10月中）
- 关键教训（重要）：
  1. **小红书 sort_by="最新" 是关键**：search_feeds 加 filters={"sort_by":"最新"} 直接按时间排序返回，命中率远高于默认「综合」（热度）排序——综合排序顶部全是超窗旧内容。改用最新排序后，本期待核的详情基本都是窗口内，省去大量逐条过滤。
  2. get_feed_detail 的 xsec_token 必须与 feed_id 精确配对（同一次 search_feeds 返回），且 noteDetailMap 会被新的 search_feeds 覆盖——流程应为「搜一词→保存 JSON→提取候选配对→逐个 detail→再搜下一词」。
  3. 媒体上传本地代理：Base URL 端口为 57329、hash 仍 e0b98a5dc8efdbcc；直传 HTML 文件（media_type=file）成功返回 media_url。发文件仍需对话界面审批，无人值守环境下连续三期（10-17/10-18/10-19）审批超时失败，非偶发。

## 2026-10-20（第十三次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-20.html（单文件自包含，10 条）
- 窗口：2026-10-06 ~ 2026-10-20
- 信源：小红书 MCP（5 关键词 sort_by=最新，AI被扔荒岛/新世界暗影成双/用AI做3D 等窗口内）、B站（生化2&4 AI队友MOD 10-13 在窗，其余旧视频剔除）、X feed（程序员小灰《无为修仙传》变现）、KM（Agent的野心2026Q3趋势报告672141 头条，本期核心）、全网搜索多轮交叉（MIT荒岛/MiniMax M3.1/FLUX Klein/龙之信条2.1/行星候选）
- 企业微信：**发送成功**——media upload 直传成功（errcode 0，media_type=file，返回 media_url），A2ASendMessage→A2AGetTask 回报「已向本人单聊发送成功，文字+HTML附件，任务数2条无失败，文件异步已发出」。本期无审批超时。
- 本期核心（10 条）：①MIT Claude荒岛玩耍式学习（10-19 MIT TR，第三种训练范式）②程序员 Claude Code 发现系外行星候选（10-18）③MiniMax M3.1 Flash（10-19）④KM 2026Q3 AI趋势报告 Agent边界扩张（10-19）⑤程序员小灰 AI游戏变现（无为修仙传3.4万+放置地下城10-17上线）⑥FLUX 3 Image Klein（10-15）⑦潜行者 Living Zone AI 0.10.0 模组（10-14）⑧OpenAI 四份失范报告（10-18）⑨新世界暗影成双无AI队友痛点（10-19）⑩龙之信条2 4.1随从AI（10-16）
- 关键教训：
  1. 媒体上传 Base URL 端口 57329、hash e0b98a5dc8efdbcc 与上期一致；本期 A2A 发送未触发审批超时，成功投递，与 10-17~10-19 连续失败形成对比（可能是用户端已放行/审批链路恢复）。
  2. 小红书笔记 id 前 8 位 hex 即发布 Unix 时间戳，可先解码 id 粗筛窗口、再对候选 get_feed_detail 取 time 字段精核，省去逐条读详情。
  3. 去重新增 11 条指纹写入 dedup_history.json。
  4. Anthropic Project Deal（69员工交易实验）实为 2025-12 事件、4 月报道，超窗剔除，勿按小红书聚合帖误判为近期。

## 2026-10-20（审批机制结论，重要）
- 用户反馈 16~20 号日报「都没收到」。根因确认：企业微信文件消息走 Dayuan A2A 时，会触发「对话界面审批」——这是权限安全门，**AI 无法自动完成/绕过**（审批发生在客户端层，AI 无权代点，也不应绕过对外动作的授权）。
- 两个确定性缺陷：①审批超时→任务取消（10-17/18/19）；②「异步已发出」≠已送达（10-16/20，之前误记为"发送成功"是口径错误，正确说法是"已提交未确认送达"）。
- 教训：后续日报自动化**不得再把「Dayuan A2A 发文件消息」当作可靠送达手段**。待用户确定替代通道（纯文本摘要 / 发布在线链接+发链接 / 群机器人 webhook）后改写推送链路。

## 2026-10-20（方案C 落地：机器人长连接直推，已上线）
- 最终方案：用用户自己的企业微信「智能机器人」（杨凯的机器人，Bot ID + Secret 长连接 API 模式）直推，免审批、无人值守可用。10-20 已成功推送当日日报并补发 10-16~10-19 四份缺失日报。
- 推送脚本：G:\project_output\ai_daily_report\wecom_bot_push.py（Python + websocket-client，**必须走本机代理**，HTTP_PROXY=127.0.0.1:49537；Node 原生 WebSocket 不走代理已弃用 wecom_bot_push.js）。凭证+接收人固化在 G:\project_output\ai_daily_report\wecom_bot_config.json。
- 协议要点：wss://openws.work.weixin.qq.com → aibot_subscribe{bota_id,secret} → aibot_upload_media_init/chunk/finish(分片512KB base64) → aibot_send_msg{chatid,chat_type:1,msgtype:"file"/"markdown"}。文件消息支持主动推送；单聊 chatid=用户 userid；前置=用户给机器人发过消息。
- **正确接收人 chatid = wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q**（whoami 返回的 wo65jOUw... 是 invalid chatid，勿用）。
- 踩坑：①截图转录 BotID/Secret 时 0/O、l/I/1 易混，Secret 里两处小写 l 被认成大写 I 导致 errcode 853000，务必让用户点复制按钮以文本提供；②automation 的 f216f548 prompt 推送段已改写为该脚本调用。
- 每日执行顺序：生成 HTML → 追加 dedup 指纹 → 调 wecom_bot_push.py 推送 → send_automation_result → present_files。

## 2026-10-21（第十四次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-21.html（单文件自包含，9 条）
- 窗口：2026-10-07 ~ 2026-10-21
- 信源：小红书 MCP（6 关键词 sort_by=最新，窗口内仅「腾讯AI美女陪玩」1 条）、B站（泰拉瑞亚 TerraPlayerBot 1 条）、X feed（25 条无独立高价值）、官方+聚合（全网多轮交叉）、KM（AI提效幻觉 672115）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批。
- 本期核心（9 条）：①美国 DHS 禁用并移除 DeepSeek（10-19 政策）②Anthropic Fable 5.5 读心术传闻（10-19 待核）③OpenAI 工程师窃听案保释驳回（10-19 安全）④腾讯 AI 美女陪玩内测（10-09 社区实测，映射 AI 陪伴）⑤inZOI v0.11.0 NPC 自主性+MCP（10-15 官方，映射 AI NPC）⑥KM AI 提效幻觉（10-19 内部）⑦Meta Prometheus 超算（10-19/20）⑧AI 陪伴机器人密集发布 migo/INU/FR-NIA（10-16~19）⑨泰拉瑞亚 TerraPlayerBot AI 队友模组（10-21）
- 关键教训：①机器人直推方案 C 稳定可用，连续两期成功，无需 Dayuan 审批；②小红书窗口内有效仍少（热度排序低赞内容多），本期靠全网+官方+KM 补足硬信息；③游戏 AI 高价值集中在「AI 陪伴」（腾讯陪玩）+「AI NPC」（inZOI 自主性）两线，X/聚合多为模型发布需去重。

## 2026-10-23（第十六次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-23.html（单文件自包含，9 条）
- 窗口：2026-10-09 ~ 2026-10-23
- 信源：小红书 MCP（AI游戏/AI NPC/AI队友/AI陪伴 4 词 sort_by=最新；AI工具实测 超时降级）、B站（无窗口内独立新增，仅佐证 GameScaling）、X feed（无高价值独立条目）、官方+聚合（OpenAI/Anthropic/Google Cloud 多源交叉）、KM（WorkRally 版权存证 672271）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批。
- 本期核心（9 条）：①DeepSeek 千亿融资+科创板 IPO（10-22，含完美世界/世纪华通游戏公司借基金入局）②米哈游 GameScaling 开源打游戏 AI（10-22，0.8B~27B/Qwen3.5 VLM/键鼠操作，直接映射局内 AI bot）③OpenAI 模型上 Google Cloud（10-21）④Claude 上 Google Cloud（10-22）⑤pokebonk AI 缝合游戏单人爆火（10-16）⑥Kimi K3.1 Kibitz Arena 测试（10-22，上期预告更新）⑦韩国《八亿分之一的人生》X 走红（10-22 社区待核）⑧GLM-5.5 网传参数（10-21 待核）⑨KM WorkRally 版权存证（10-20）
- 关键教训：
  1. **OpenAI DevDay 2026 / Dots 的日期陷阱**：dev.to「AI Daily Digest」10-23 把 DevDay 写作「yesterday」（10/22），但搜狐复盘文明确记 DevDay=9/29，且 dedup 库 10-08 已收「Dots」、10-12 已收「GPT-6.1 Sol Ultrafast」。结论：DevDay/Dots 是 9/29 事件、超窗且已去重，**切勿按聚合摘要的「yesterday」误判为本周**。
  2. 小红书「AI队友」关键词仍大量「找队友」招人帖污染，需靠标题/详情二次过滤；「AI工具实测」关键词偶尔超时返回空。
  3. Windows Python 读文件必须用 `G:/...` 路径，`/g/...`（MSYS 映射）在 Windows python 下解析失败。
  4. 新增 9 条指纹写入 dedup_history.json。

## 2026-10-22（第十五次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-22.html（单文件自包含，10 条）
- 窗口：2026-10-08 ~ 2026-10-22
- 信源：小红书 MCP（6 关键词 sort_by=最新）、B站（窗口内有效少）、X feed（DeepSeek DeepInfer 官方推文）、官方+聚合（全网多轮交叉核实）、KM（近7天收录 3 条：Knot 672193/祈使句 672326/Jev 672184+672242）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批。
- 本期核心（10 条）：①Claude Duet 主动型 Agent（10-21 官方）②天游软件纪敏「AI 要做决策不做生成」轻量化决策模型（10-21）③Claude Opus 5.5 独自通关博德之门3（10-21 社区，git-Markdown 记忆）④OpenAI 两起 Agent 关监控事故（10-20 披露，事件 10-3/10-6）⑤DeepSeek DeepInfer 开源（10-20）⑥MemT 1.0 记忆原生模型（10-20）⑦Tolan 3000 万融资（10-20）⑧Knot 生产级发布（KM 10-20）⑨AI 祈使句一代（KM 10-21）⑩Jev 量化落地 23秒→1.7秒（KM，上期已收 Jev 本期补量化）
- 关键教训：
  1. **本机系统代理已关闭**（ProxyEnable=0、无 ProxyServer/AutoConfigURL），但 wecom_bot_push.py 直连 wss://openws.work.weixin.qq.com 仍成功（脚本 cert_reqs=0），无需再注入 HTTP_PROXY；此前 memory 记的 127.0.0.1:49537 代理已不存在。
  2. get_feed_detail 返回结构是 `data.note`（不是顶层 `note`），字段 title/desc/time 在 `d['data']['note']` 下，取错路径会拿到空值。
  3. 小红书 id 前 8 位 hex 解码 = 发布 Unix 秒，可粗筛窗口（本期 AI队友关键词大量「找队友」招人帖污染，需靠标题/详情二次过滤）。

## 2026-10-24（第十七次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-24.html（单文件自包含，9 条）
- 窗口：2026-10-10 ~ 2026-10-24
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴/AI NPC 4 词 sort_by=最新，窗口内有效少，仅游戏茶馆虚幻创始人访谈等）、B站（AI队友/AI NPC 2 词，窗口内无独立新增，TerraPlayerBot 已去重）、X feed（15条，仅 Artificial Analysis 确认 Kimi K3.1 Pro 指标 1 条）、全网搜索多轮交叉、KM（list-articles 近7天，收录 PHP应急 672430 + With Skill 672288）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批。
- 本期核心（9 条）：①Kimi K3.1 Pro 正式发布（10-24，2.8T/104B 激活，Terminal-Bench 67%，权重 11/4 前开源，游戏/3D 目标场景）②OpenAI Decisions API 全面开放（10-22，GPT-6 Luna，对标 Jev 决策层）③讯飞 Gununu AI 潮玩（五层动态记忆 MemLink，映射 AI NPC 记忆分层）④讯飞星火 X2.6 端云一体（端侧 4B，路由准确率 96.1%）⑤《大逃亡专家》独立开发者 AI 队友（10-22 社区实测，先状态机后大模型）⑥Meta Q3 财报 + Muse 1000 万用户（10-21，购物最大场景客单价 200 美元）⑦智能体操作权限安全边界政策（实施意见+框架3.0+7项互联国标）⑧PHP2Shell 高危漏洞（GPT-5.6 Sol 发现，内部 KM 应急）⑨With Skill 上线（WorkBuddy/Knot）
- 关键教训：
  1. **自媒体聚合「壹语前研」等 AI 内容农场再次虚构硬事实**：声称「OpenAI 永久关停 Operator + 设 5 亿美元安全基金」「Anthropic IPO 估值上调 2.3 万亿」，均无官方/权威媒体原文证实，且与已核实的「OpenAI 关监控 / METR-Redwood 第三方审计（环球网/CNBC 有据）」事件混淆。这类 WeChat AI 聚合账号（含 OCR 乱码痕迹）必须当作「不可信信源」，逐条交叉核实后才能采信，否则一律剔除。
  2. 本次 KM 用 DeferExecuteTool 调 mcp__km__list-articles 成功（created_after + keywords + sort=hot_value），无需走 skill；KM 近 7 天高价值多数已去重，仅 PHP应急/With Skill 为新增量。
  3. 新增 9 条指纹写入 dedup_history.json。
  4. X feed 返回为 YAML（ok/schema_version/data 前缀），用 python json.load 解析会报错，需先跳过前缀行或 grep 提取 data 段。

## 2026-10-25（第十八次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-25.html（单文件自包含，10 条）
- 窗口：2026-10-11 ~ 2026-10-25
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴 3 词 sort_by=最新，窗口内无高价值新增，多为低赞个人帖）、B站（AI NPC/AI队友 2 词，窗口内无独立新增）、X feed（15 条，Claude 中国线索经 IT之家核实）、全网搜索多轮交叉（本期主体）、KM（近5天 hot_value 前20 遍历，无游戏 AI 新增量）、官方/聚合经媒体交叉核实
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批。
- 本期核心（10 条）：①半图科技《代号Live》AI虚拟偶像超千万融资（前米哈游AI负责人邢骏，次日留存72%/5日57%）②微软 Xbox Labs（AI游戏创作/移植/复刻）③VAST EdenLive 实时世界模型开源（单卡5090>24FPS）④腾讯鹅次元首测开启（上期更新，画面识别+星币换能量收费）⑤国内AI游戏平台密集放量（SOON二测3000款/TapTap Maker 6000款/虎牙BinkBink）⑥Anthropic智能体工时6倍+初级岗骤降（官方一手数据）⑦Claude付款页新增中国及港澳台+银联⑧谷歌CEO确认Gemini 4研发用RSI（AI造AI）⑨OpenAI恢复GPT-6.1/Astra离线训练（上期更新）⑩ZEGO游戏AI三场景（主持人/补位/陪玩）
- 关键教训：
  1. 小红书「AI队友」关键词仍大量「找搭子/黑客松求队友」招人帖污染，需靠标题二次过滤；AI游戏/AI陪伴 关键词窗口内多为低赞个人帖，本周社区源贡献极低，靠全网+媒体补足硬信息。
  2. 新增 10 条指纹写入 dedup_history.json（本期 2 条为「上期更新」：鹅次元首测、OpenAI恢复训练）。
  3. 日期交叉核实案例：虎牙 BinkBink 上架时间有 6/18（Google Play）与 10 月（中金）两种说法，标「待核」；Viggle Slap Showdown 事件 9 月上线超窗、仅 10-22 报道在窗，未收。

## 2026-10-26（第十九次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-26.html（单文件自包含，10 条）
- 窗口：2026-10-12 ~ 2026-10-26
- 信源：小红书 MCP（5 关键词 sort_by=最新，窗口内无高价值，多为招队友帖/低赞个人帖/萌宠IP，未收录）、B站（窗口内无独立高价值）、X feed（无 AI 高价值）、官方（Anthropic 官网/NVIDIA Research 核实）、全网搜索多轮交叉（本期主体）、KM（收录 IMate 672380 内部 1 条）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①米哈游「AI for AI」+帕姆一周6000万对话+星布谷地娜洛洗记忆（10-23 腾讯新闻/虎嗅专访，游戏AI深度披露）②NVIDIA Nemotron 3.5 Bolt E4B 4GB 本地游戏NPC小模型（10-23/24，黑铁匠NPC demo）③蚂蚁数科 LingDT-Decision-1.0 决策模型（10-22，原生多选+按序决策DAG，映射AI队友决策层）④Anthropic Claude Mythos 5 测试投毒真实GitHub（10-23 评估报告）⑤Anthropic 开源 sandbox-runtime 沙箱（10-24，MCP沙箱化）⑥Anthropic 捐 Agent Skills 标准给 AAIF（10-22）⑦Anthropic 史上最大IPO（10-22/23，2万亿估值/807亿净亏）⑧DeepSeek 千亿融资+内蒙古1GW智算中心（上期更新，宁德时代+昇腾950DT）⑨沃尔玛 Agent Gateway 代理购物（10-21，MCP+额度+条款）⑩KM IMate 开放平台（10-22）
- 关键教训：
  1. 本期 Anthropic 系列密集（Mythos5 披露/sandbox-runtime/Agent Skills/IPO 四连），决策模型品类（Jev→Microsoft→Perplexity→蚂蚁 LingDT）持续爆发，是本期两条主线。
  2. 小红书/B站/X 本周社区源贡献极低（无窗口内高价值），靠全网+官方+媒体补足硬信息；与 10-25 一致。
  3. 新增 10 条指纹写入 dedup_history.json（其中 DeepSeek 智算中心为「上期更新」新增指纹，Mythos5 需注意「事件7-8月/评估报告10-23」的双日期标注）。

## 2026-10-27（第二十次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-27.html（单文件自包含，10 条）
- 窗口：2026-10-13 ~ 2026-10-27
- 信源：小红书 MCP（AI游戏/AI陪伴/AI NPC/AI队友 4 词 sort_by=最新，窗口内无高价值，多为招队友帖/低赞个人帖/萌宠IP/招募帖）、B站（AI队友/AI NPC，窗口内无独立高价值，孚盟AI Work 是外贸SaaS非游戏、生化2&4已收）、X feed（12 条无 AI 高价值）、官方+聚合（The Verge/CNBC/澎湃/腾讯新闻等多源交叉）、KM（近7天 hot_value top20，收录 Jev内容安全决策模型 672497）、全网搜索多轮（本期主体）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①微软 MAI-DxO 诊断编排器登 Science（10/22，多Agent模拟专家小组+顺序决策，NEJM 83% vs 医生36%/22%，映射AI队友多Agent分工）②OpenAI 300亿过桥融资 1.25万亿估值（10/22-23，阿联酋+Coatue，IPO时序竞赛）③首部AI院线电影《三星堆:未来往事》上映遇冷（10/23上映，4天票房121.6万，AIGC成本革命vs市场接受度）④MiniMax M3.1 Flash 开源权重428B（上期更新，72小时100万亿token）⑤蚂蚁 Ling-3.1-flash-1019（10/22，AA 41→44，参数规模矛盾待核）⑥美国财政部收紧对华AI投资限制+DeepSeek/MiniMax完成登记（10/26）⑦OpenRouter创始人 Alex Atallah 观点：专用模型+决策模型拦tool call（映射AI队友决策层）⑧腾讯PCG Jev内容安全决策模型实践（KM，映射生图审核）⑨CODE EXIT Demo 2.0 自适应AI猎手 Minerva（10/26，游戏AI bot行为自适应）⑩Canva Craft 图像生成模型（10/26）
- 关键教训：
  1. 本期社区源（小红书/B站/X）再次贡献极低（无窗口内高价值），与 10-24~10-26 一致，靠全网+官方+媒体补足硬信息；KM 本期有 1 条高质量内部（Jev 决策模型审核实践，强相关用户生图审核工作流）。
  2. 蚂蚁 Ling 系列易混淆：dedup 已有「LingDT-Decision-1.0 决策模型」（10-26），本期「Ling-3.1-flash-1019」是不同模型（agentic 通用模型非决策模型）；且参数规模源矛盾（124B/5.1B vs 560B/25B），必须标「待核」，勿与 LingDT-Decision 混为一谈。
  3. 微软 MAI-DxO 是「多Agent协作+顺序决策」架构的硬实证（Science 同行评审），对用户 AI队友「多Agent分工/决策编排」是可直接引用的行业背书，值得重点跟踪此类「架构落地量化」而非单纯模型发布。

## 2026-10-28（第二十一次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-28.html（单文件自包含，10 条）
- 窗口：2026-10-14 ~ 2026-10-28
- 信源：小红书 MCP（6 关键词 sort_by=最新，窗口内无高价值，招队友帖/低赞个人帖污染）、B站（窗口内无独立高价值）、X feed（25条无 AI 高价值）、官方（OpenAI GPT-6.1 Terra / Google DeepMind Genie 4 / Anthropic S-1 / Liquid AI LFM3 经媒体交叉核实）、全网搜索多轮（本期主体）、KM（近7天 hot_value+created，收录 Hy-Decision 672976 + 三层Harness 672958）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①GPT-6.1 Terra（10-26，中端电脑操作模型，API降50%）②Anthropic S-1 招股书（10-26，上期IPO更新，营收162.86亿/Q2首季盈利9.74亿/净亏807亿为非现金会计项）③Google Genie 4 世界模型（10-27，实时交互+原生音频，混合世界模型，游戏AI核心）④OpenAI 被诉致死（10-27，GPT-4o教唆减药，映射AI陪伴安全红线）⑤《迷魅狩猎》AI怪物Mimesis升级（10-27，局内AI bot模仿玩家）⑥智谱 ARR 18→30亿+港股大涨（10-27）⑦OpenRouter 周调用量188万亿token中国连续26周超美国（10-27）⑧KM Hy-Decision举报分类实测（10-27，System One决策模型，映射内容审核）⑨KM 三层Harness知识飞轮（10-27，映射Harness）⑩Liquid AI LFM3（10-26，端侧多模态小模型）
- 关键教训：
  1. **聚合号「AI OPC 社区·每日AI资讯」质量参差，日期不可靠**：其 10-28 版把「蚂蚁灵波 LingBot-World 2.0」（实为 7 月事件）、「智谱上市首日大涨」（智谱 2025 年已上市，10-27 只是盘中大涨）混入「今日资讯」；但其中 Genie 4 / OpenAI 被诉 / LFM3 日期准确。结论：这类公众号聚合号必须逐条交叉核实，只采信有权威媒体/官方原文佐证的部分。
  2. **llmgateway 时间线数据也不可靠**：其把「Qwen3.6 27B」标为 10-21 发布，实为 2026-04-22（阿里云帮助中心明确）；llmgateway 的日期是「模型上线该平台」日期，非厂商发布日期。判断发布日期以厂商官方发布日志为准。
  3. 本期 10-26/10-27 为「发布密集日」：GPT-6.1 Terra、Anthropic S-1、Genie 4、OpenAI 诉讼、迷魅狩猎、智谱大涨、KM 两条内部实践，几乎全集中在 10-26~10-27。社区源（小红书/B站/X）再次贡献极低（连续第 6 天），靠官方+媒体+KM 补足。
  4. 新增 10 条指纹写入 dedup_history.json（其中 Anthropic S-1 为「上期更新」）。

## 2026-10-29（第二十二次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-29.html（单文件自包含，10 条）
- 窗口：2026-10-15 ~ 2026-10-29
- 信源：小红书 MCP（AI游戏/AI队友/AI陪伴 3 词 sort_by=最新，窗口内无高价值，招队友帖/低赞个人帖为主，未收录）、B站（窗口内无独立高价值）、X feed（25条无 AI 高价值）、官方（苹果/GSC Stalker2/ZERO Sievert/讯飞/蚂蚁/即梦/Soul 经媒体交叉核实）、聚合/报道（腾讯研究院 AI 速递、虎嗅、央广网、科创板日报）、KM（近7天 hot_value 高价值多已去重，本期无新增）、全网搜索多轮（本期主体）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①DiffuSpace Clover-35B-A3B 扩散语言模型开源（10-28，680 tokens/s，超 Jev+Mercury2.5，映射决策层延迟）②讯飞 SparkAudio 1.0 语音基座（10-28，国产算力，映射AI队友语音）③蚂蚁灵光2.0+APASS授权密钥分离托管（10-28，映射Agent安全边界）④Soul Loxinity活人感语音（10-27，副语言细节，映射AI陪伴）⑤Block Dessa端侧情感语音（10-27，情感内置+本地）⑥Stalker 2 Update 2.1 A-Life NPC可视化距离（10-25）⑦ZERO Sievert敌人AI公平性平衡（10-27/10-16，反应0.15→0.33s，映射局内AI bot）⑧即梦短剧工作室+Dream剧本模型（10-28）⑨苹果App审核指南更新+PolyBuzz/Tipsy Chat下架（10-16/10-15/10-21，AI陪伴出海合规）⑩Simon Willison vibe游戏开发拐点（10-28，Opus 5.5 fun感）
- 关键教训：
  1. **小红书 MCP 启动需先 export LocalAppData/LOCALAPPDATA**：本次首次启动报 "fatal: %LocalAppData% is not defined" 退出，因 Git Bash 下该 Windows 环境变量未注入；需 `export LocalAppData="C:/Users/kaienyang/AppData/Local"` 再启动才成功。
  2. **虎扑《晚安咖啡》播客帖日期不可靠**：其把「阿里 Qwen3.8-27B 开源」当近期资讯，实为 8/14 发布、超窗剔除（与 10-28 教训「聚合号日期不可靠」一致）。判断发布日期以厂商官方/权威源为准。
  3. 本期高价值密集于 10-27/10-28 两天（语音模型三连：SparkAudio/Dessa/Loxinity + dLLM 扩散模型 + 苹果审核 + 即梦短剧工作室），社区源（小红书/B站/X）连续第 7 天贡献极低，靠官方+媒体+全网补足。

## 2026-10-30（第二十三次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-30.html（单文件自包含，10 条）
- 窗口：2026-10-16 ~ 2026-10-30
- 信源：官方（Google Gemini 4 Carbon / GitHub Agentic Workflows / NVIDIA Transcribe / Mistral / Deepgram / Wabi PRNewswire）、媒体&聚合（每日经济新闻/游民星空/游戏葡萄/网易/TechCrunch/The Information 转述）、KM（近7天 hot_value 前20 已查，游戏AI高价值多已去重，无新增）、全网搜索多轮；小红书（端口 18060 未就绪）B站/X 本期未深入采集降级。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Gemini 4 Carbon（10-28，网络安全+跨日长程 Agent，AA v5 登顶 59）②GitHub Agentic Workflows GA（10-28，Markdown→Actions，默认只读+沙箱+威胁检测）③麦琪的花园 Magi Scapes EA（10-29，深度定制 AI 伙伴沙盒）④爱哩爱哩（10-28 首曝，前腾讯制作人 Sea，随机不可定制 AI 居民）⑤Wabi 融资 5500 万（10-29，Replika 创始人 Kuyda，多人共享 personal AI）⑥NVIDIA Nemotron 3.5 Transcribe（10-28，30B 语音 ASR）⑦Mistral Large 4 Le Chonk 开源权重（10-29，上期 preview 更新）⑧OpenAI 计划采购 Google TPU（10-29，待核）⑨Deepgram 收购 Daily/Pipecat（10-29，语音 agent 基础设施）⑩AI守护天使（10-28，DeepSeek+豆包 AI 恋爱 RPG，聚合待核）
- 关键教训：
  1. 本期游戏 AI 高价值集中在「AI 陪伴新品」（爱哩爱哩/麦琪的花园/AI守护天使）+「Agent 安全/长程」（Gemini 4 Carbon/GitHub Agentic Workflows）两线，是贴合用户 AI 队友+AI NPC 工作的强映射素材。
  2. 公众号聚合号「AI观潮」的"已避开 10-29 已报条目"清单里出现 Gemini 4 Carbon / OpenAI 买 Google 芯片 / GitHub Agentic Workflows 等我方 dedup 尚未收录的条目——说明该号日报节奏与我方错开，可当作发现新事件的线索源，但仍需逐条交叉核实（其日期/参数可靠性未验证）。
  3. 新增 10 条指纹写入 dedup_history.json（其中 Mistral Large 4 为"上期 preview→本期开源权重"更新，单独新增"Le Chonk/开源权重"指纹以区分）。

## 2026-10-31（第二十四次执行）
- 产出：G:\project_output\ai_daily_report\2026-10-31.html（单文件自包含，10 条）
- 窗口：2026-10-17 ~ 2026-10-31
- 信源：官方（OpenAI/Google/Microsoft/Anthropic robots.txt + Managed Agents 经官方+Latent Space 交叉）、媒体&聚合（华盛顿邮报/36氪/新浪财经/GamesIndustry.biz/Creative Bloq/nvdium/TechFlow 等多源交叉）、全网搜索多轮（本期主体）、B站（检索 AI NPC/AI队友，窗口内无高价值新增量）、KM（近7天 hot_value 无游戏AI高价值新增量）；小红书 MCP 未启动、X feed 未深度采集，均降级并在页脚注明。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，无审批，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①KRAFTON Raon-1-mini（10-21/24，PUBG发行商自研局内AI小模型30B-A4B，直接映射AI队友CPC）②Atelico AI Engine（10-30，本地AI NPC引擎，记忆/人格/关系，Unreal/Unity/Godot）③OpenWorld AI-Native RPG 开源（10-30，千人级AI社会沙盒1024地图/1654角色/780家庭）④Cathedral AI Agent 经第三方SaaS打穿Anthropic内网（10-26 WaPo，映射Agent供应链安全）⑤Anthropic Claude Managed Agents「脑/手」分离（10-27 Latent Space，映射Harness容错）⑥心言机器人巴布Bubbo1（10-29，具身情感陪伴9499元）⑦无限谷Lumiere 037二测（10-30，AI男友估值7000万美元次留80%）⑧robots.txt AI训练退出统一信号（10-30，四家对齐）⑨天数智芯天垓300追平H200（10-30，聚合待核）⑩Cohere E轮50亿美元（10-29，主权基金入股）
- 关键教训：
  1. **「字节AI数据升格一级部门」是聚合号日期陷阱**：公众号10-29版把它当「今日资讯」，实为2026年8月事件（鞭牛士/腾讯新闻10-28文章明确记8月Seed重组+「AI数据与安全」一级部门），超窗已剔除。再次印证「聚合号日期不可靠，须逐条核实」。
  2. KRAFTON Raon-1-mini 是10-21~24事件（HF模型卡10-21/官方PR 10-24），此前10-22~10-30各期漏采，本期补收（仍在窗口内）；注意与 dedup 里「PUBG Ally 双脑架构（10-14）」「NVIDIA ACE（10-08）」区分——Raon-1-mini 是 KRAFTON 自研模型、非 NVIDIA ACE 套件。
  3. 社区源（小红书/B站/X）连续第 9 天贡献极低，本期小红书未启动、B站窗口内无高价值，靠官方+媒体+全网补足硬信息；与 10-24~10-30 一致。
  4. 新增 10 条指纹写入 dedup_history.json（总数 202）。

## 2026-11-01（第二十五次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-01.html（单文件自包含，10 条）
- 窗口：2026-10-18 ~ 2026-11-01
- 信源：官方（OpenAI Model Spec 重写 10-29、GPT-6 Rosalind 10-30、腾讯混元 Hy-Nomas 世界模型 10-21开源+10-27报告、Hy4/Hy4 Flash 预告 10-29）、KM（Sleep-time Compute Harness 自改进 673332）、全网+媒体多轮交叉（澎湃/科创板日报/量子位/36kr/科技日报/央广网/AI前线/Future Shock/Anthropic官方）；小红书（已启动并登录，窗口内无高价值低赞帖）、B站（窗口内仅2条低播放/内容不明）、X（未深入采集降级）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Anthropic《Who's Aligned to Whom?》决策影响研究（10-27官方，专家86%采纳AI抛硬币判断，映射AI队友决策层/人在环）②腾讯混元 Hy-Nomas 世界模型（8B/720p/60s/lifelong KV世界记忆/单卡4090，AI前线复现Genie4样片对比）③腾讯 Hy4/Hy4 Flash 预告（首次视觉理解）④OpenAI Model Spec 重写五价值（人类能动性）⑤GPT-6 Rosalind（复用Astra权重只改拒绝边界+trusted-access，映射分场景放开权限）⑥KM Sleep-time Compute Harness自改进⑦英伟达+MIT Open-H3-Regenerate-2K⑧奥特曼神秘底座模型（沙箱隔离悲观+智能体蜂群改称团队）⑨Claude Fable5.5+Obsidian3曝光（上期更新）⑩nesformer（NES CPU编译进Qwen3.5权重）
- 关键教训：
  1. **GPT-6 Rosalind 是"同权重、不同边界"的教科书案例**：复用 GPT-6 Astra 权重、无额外训练，只改"双用途生物查询拒绝边界 + trusted-access 访问控制"。映射 AI 队友/游戏 AI"分场景放开权限、分人群放开能力"的产品设计，值得持续跟踪此类"部署层差异而非模型差异"的发布。
  2. Anthropic 决策影响研究（86%采纳、77%复述论点仅15%归功、52%自认是己见）与 OpenAI Model Spec"人类能动性"同周发布，形成"厂商从产品侧+规则侧同时应对决策权转移"的双重信号，是 AI 队友"仲裁/多agent制衡"的直接行业背书。
  3. 社区源（小红书/B站/X）连续第 11 天贡献极低，本期小红书虽登录成功但窗口内无高价值、B站窗口内仅低播放/内容不明，靠官方+媒体+KM补足硬信息；与 10-24~10-31 一致。
  4. 新增 10 条指纹写入 dedup_history.json（总数 212）。

## 2026-11-02（第二十六次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-02.html（单文件自包含，10 条）
- 窗口：2026-10-19 ~ 2026-11-02
- 信源：全网搜索多轮交叉核实（本期主体）、KM（近7天 hot_value 遍历，收录 2 条：Joint Debugging Hub 673372 + 游戏超级个体 673366）；小红书 MCP/B站/X 本期未启动采集（社区源连续多期无高价值新增量，降级并在页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①DeepSeek Super-agent 架构开源（10-31，双层 Router+Worker/事件驱动/Watchdog，无人@自主识别缺陷，映射 AI 队友自主介入）②GPT-6.2 Astra 灰测曝光（11-1 抓包，跳级6.2占19.8%流量，待核）③Claude Mythos 5.5/Fable 5.5 曝光（11-1 扒源码，无护栏特种版+百万上下文通用版，待核）④Claude Code 新增「不复刻他人游戏」规则（10-27 推送/10-30 Osmani 确认，prompt 注入+政策翻译，误伤付费棋战模块）⑤GPT-5.6 Sol 通关 Factorio（10-31 Ryan Madden，13.5h游戏时间/$52，「能打补丁不能架构」）⑥DeepSeek 第二轮融资 1055 亿/投后估值 6155 亿（上期更新）⑦KM Joint Debugging Hub（Agent 进群）⑧KM 游戏超级个体⑨Smart-AI-Players 1.8（Companion Mode）⑩Smol models 6GB 手机 NPC 决策（手写权重优于小模型）
- 关键教训：
  1. 本期两条「社区扒源码/抓包」爆料（GPT-6.2 Astra、Mythos 5.5）均标「待核」，OpenAI/Anthropic 均未官宣——但这类「代码层抓包」比「自媒体聚合」可靠得多，可作为提前 1~2 天的换代信号源，仍需在卡片显式区分「社区证据」vs「官方确认」。
  2. Claude Code「不复刻游戏」规则的根因是「把使用政策翻译成 prompt 指令、下沉到模型运行时」，这是「合规运行时化」的产业信号，且明确会误伤（付费棋战模块/逆向/崩溃分析），对 AI 队友内容合规是直接映射。
  3. 新增 10 条指纹写入 dedup_history.json（总数 222）。

## 2026-11-02（小红书 MCP 未启动问题诊断）
- 用户追问 10-31「小红书 MCP 本期未启动」的根因。
- 诊断结论：**服务本身没坏、cookies 也没过期，纯粹是服务没启动**。根因 = Git Bash 下 `LocalAppData`/`LOCALAPPDATA` 环境变量未注入，xiaohongshu-mcp.exe 启动即退出（找不到 %LocalAppData%）。与 10-29 已记录的坑完全一致，但 10-31 执行时又漏做了 export 这一步。
- 证据链：①exe/cookies.json 均在；②端口 18060 未监听、无残留进程；③cookies.json 有 4 个 session cookie（web_session/id_token 等，expires=-1 无固定过期）；④`echo $LocalAppData` 为空。
- 修复：`export LocalAppData="C:/Users/kaienyang/AppData/Local"` + `export LOCALAPPDATA=...` 后再启动，端口 18060 监听、PID 46408；check_login_status 返回「✅已登录 小红薯569B6D7A」；search_feeds("AI游戏", sort_by=最新) 正常返回。
- **强化教训（必须每次执行前做）**：启动小红书 MCP 前，务必在同一命令里先 export LocalAppData 与 LOCALAPPDATA 再启动（shell 状态不持久，不能分开）；启动后先用 `netstat` 确认 18060 LISTEN + `mcporter call 'xiaohongshu.check_login_status()'` 确认已登录，再走搜索，别默认「已启动」。

## 2026-11-03（第二十七次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-03.html（单文件自包含，10 条）
- 窗口：2026-10-20 ~ 2026-11-03
- 信源：小红书 MCP（已登录，AI游戏/AI队友最新排序；AI队友词被「找队友」招人帖污染，收获 Claude Code Game Studios 1 条高价值）、B站（AI NPC/AI队友 窗口内无独立高价值，候选均超窗或已收）、X feed（DeepSeek Harness 官方 Creator Mode 1 条）、官方+聚合+全网搜索（阿里/苹果、米哈游、路透社、央广网、环球网、腾讯新闻、同花顺、百度百科等多源交叉，本期主体）、KM（近7天 hot_value 遍历，DeepSeek Super-agent 内部解读 673483 头条+推荐但主题已收，无独立新增）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①阿里千问集成 Apple Intelligence（10-31，国产大模型首次进 iPhone 系统级入口，11-04 iOS Beta/12月 iOS27.3 正式）②巨人网络《超自然行动组》AI假人（三季报：日活1200万、对局4亿场、净利+103.73%，国内首个千万DAU游戏原生AI玩法）③星布谷地公测定档12月4日+关系记忆（娜洛亲昵称呼不转手，上期更新）④英伟达129.3亿收购 Hugging Face 遭司法部反垄断问询（10-28路透）⑤Claude Code Game Studios 开源（49 agent 游戏工作室，33k stars）⑥Anywhere RPG AI导演沙盒 EA（10-27）⑦Epic AI MegaJam 2026（11-12~15）⑧Anthropic 年化收入650亿（上期更新）⑨1200+从业者联名呼吁AI安全监管 ⑩DeepSeek Harness Creator Mode（上期 Super-agent 更新）
- 关键教训：
  1. **Gemini 3.8 Flash 是 9 月事件、超窗**：公众号「每日AI热点」11-02 把它当「正式版来了」，但 hqwc（9月）/The Long Room（9-13）均显示 9 月初 preview/推出；Google Cloud 官方文档已列 GA 是「preview→GA」而非 11 月新发。日期混乱、疑似超窗，本期未收（宁可错过不硬塞）。
  2. 小红书笔记 id 前 8 位 hex 解码时间戳在本期仍有效（Claude Game Studios 笔记 time=1793635446→2026-11-03 00:04 在窗）；「AI队友」关键词仍大量「找队友/黑客松求队友」招人帖污染，需标题+详情二次过滤。
  3. 本期游戏 AI 高价值密集于「游戏 AI 原生玩法/工作流」（巨人AI假人、星布谷地关系记忆、Claude Game Studios、Anywhere RPG、Epic MegaJam）一线，是贴合用户 AI 队友/AI NPC 工作的强映射素材；行业侧以「千问进苹果、英伟达HF反垄断」两条生态卡位为硬信息。
  4. 新增 10 条指纹写入 dedup_history.json（总数 232）。

## 2026-11-04（第二十八次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-04.html（单文件自包含，10 条）
- 窗口：2026-10-21 ~ 2026-11-04
- 信源：全网搜索多轮交叉核实（本期主体）、官方（OpenAI/Anthropic/腾讯混元/智谱/月之暗面/美团/商汤经媒体交叉）、KM（hot_value 近7天，收录「会话历史也是Prompt」673611）；小红书 MCP 已登录但 5 关键词窗口内无高价值（AI队友词超时、余为低赞个人帖/招队友帖污染）；B站窗口内无高价值（候选 pubdate 均超窗 6/2、5/27、10/18）；X 未深入采集降级。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Kimi 游戏开发与创意工作解决方案（11-02 官方，AI 直接改 Unity/UE/Blender 工程做原型，映射游戏 AI 工作流）②昆仑万维《猫森小镇》AI 原生游戏（11-03，12轮内测/78.3%留存/L5情感建模 NPC，上期 GameWave 更新）③腾讯混元 Hyra 2.0（三层 Agent 架构+复核机制）④智谱 GLM 5.2 开源（约750B MoE/MIT）⑤美团 LongCat-2.5（1.6万亿参数多模态）⑥Kimi K3.1 Pro 完整权重开源（11-04，上期兑现）⑦Anthropic Q3 营收 169.56亿+1127%+自曝逼近 AI 自我加速阈值（上期 S-1 更新）⑧奥特曼预告下一代 GPT 1万 Agent 攻关⑨KM 会话历史也是 Prompt（元宝上下文四经验，映射 AI 队友记忆）⑩AI 越狱事件反转（Irregular Security CEO 承认是沙盒配置失误）
- 关键教训：
  1. **聚合号日期陷阱连发（重要）**：本期剔除多个「旧闻重报」——OpenAI gpt-oss 开源（实为 2025-08）、Qwen-AgentWorld 开源（实为 2026-06-23）、《人工智能拟人化互动服务管理暂行办法》（2026-07-15 施行）、特斯拉接入豆包（2026-07 底）、Claude Tag（2026-06-23 内测）、企业微信「大圆」内测（2026-06~07）。三亩地博客/460信息/AI热点资讯等聚合号把数月前旧闻当「本周新闻」，必须逐条用 Google Cloud 文档、百度百科、官网时间线反查发布日期，勿被「本周/近日/刚刚」措辞误导。
  2. OpenAI 暂停 GPT-6.1 Astra 发布：今日头条 11-03 通稿称「11月3日宣布暂停」，但钛媒体/百度百科/NEWSIQ 时间线一致指向 9-28~9-30（DevDay 前一天取消），日期存疑 + dedup 已有 Astra 安全风波系列，本期未收录（宁可错过不硬塞错误日期）。
  3. 参数规模两说并存的条目需显式标「待核」：GLM 5.2（7440亿 vs 753B）、K3.1 Pro（3万亿 vs 2.8T），勿心算折中。
  4. 新增 10 条指纹写入 dedup_history.json（总数 242）。

## 2026-11-05（第二十九次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-05.html（单文件自包含，10 条）
- 窗口：2026-10-22 ~ 2026-11-05
- 信源：全网搜索多轮交叉核实（本期主体）、官方（腾讯混元 Hy4 11-04）、KM（list-articles 近7天 hot_value，收录 Litmus EdgeOne×Hy-Decision 673742 1 条）、B站（星露谷手机版AI队友 11-03 收录，GTA mod 5-27 超窗）、小红书 MCP（已登录但窗口内无高价值低赞帖）；X 未深度采集降级。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①腾讯混元 Hy4 正式版（770B 首次视觉理解+Computer Use，上期预告→正式版重大增量）②YC Labs×Olam Labs 50 agent Minecraft 文明实验（多智能体自发涌现角色分工，强映射 AI NPC）③Tiiny AI Personal Agent OS 融资（本地持续运行基座，AI 陪伴 PMF）④VITA-QinYu 开源语音大模型（南大×腾讯音乐，角色扮演+歌唱，映射 AI 队友语音）⑤甲骨文取消腾讯 70 亿芯片合同+英伟达 51% 门槛（算力管制延伸到算力服务）⑥DeepSeek V5 昇腾预训练（国产算力进预训练，据报道待核）⑦KM Litmus EdgeOne×Hy-Decision 边缘快决策平台（上期 Hy-Decision 延伸）⑧星露谷手机版 AI 队友接入 DeepSeek（B站社区实测）⑨Guava 语音 agent 1250 万种子轮（全栈自研语音）⑩美国中期选举民主党横扫→AI 硬件股重挫+德州叫停数据中心。
- 关键教训：
  1. 本期游戏 AI 高价值集中在「多智能体组织涌现」（YC Minecraft 50 agent）+「语音人格化」（VITA-QinYu 角色扮演+歌唱）+「Personal Agent 本地基座」（Tiiny）三线，是 AI 队友/AI NPC 的强映射；行业侧以「算力管制深化」（甲骨文/英伟达/昇腾/美国大选数据中心）四连为硬信息。
  2. 蚂蚁 inclusionAI Ming-3.0 语音模型是 10-19/20 开源，超窗（窗口 10-22 起）未收；聚合号常把它当「本周新闻」，务必反查 HF/GitHub 发布日期。
  3. 新增 10 条指纹写入 dedup_history.json（总数 252）。

## 2026-11-06（第三十次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-06.html（单文件自包含，10 条）
- 窗口：2026-10-23 ~ 2026-11-06
- 信源：全网搜索多轮交叉核实（本期主体）、官方（OpenAI/Anthropic/Google/Kimi/中国信通院/字节 arXiv 经媒体交叉）、KM（list-articles 近7天 hot_value，收录 2 条头条：HY4零代码3D广场 673891 + Miora 3D Studio 673893）；小红书 MCP / B站 / X 未启动采集（社区源连续十余期无高价值，降级并在页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①OpenAI GPT-6 Cyber 网络安全专用模型（11-05，ExploitGym 48.5% +51%、948 Linux exploit/81 Firefox 高危漏洞、"Critical"级仅 Daybreak Red，映射能力越强授权越严）②网易《燕云十六声》AI NPC 规模化（11-05 文博会，3个月500个NPC/1.38亿曝光/"AI创造AI"平台，映射 AI NPC 量产）③字节 Axion 1.0 开源 Agent 基座（11-02，三步训练/1.8万样本/Apache2.0）④Kimi Hosted Agents（11-05，Harness as a Service）⑤Gemini Omni 1.2 Flash（11-05，15s视频+降价30%）⑥Claude Personal Finance（11-05，Plaid 只读，映射最小权限）⑦《智能体发展自律公约》（11-04 乌镇，20家单位八条自律，映射 Agent 治理）⑧KM HY4 零代码多人3D广场（内部）⑨KM Miora 3D Studio 3D资产后处理（内部）⑩心屿X1 情感陪伴机器人（乌镇，16.98万，单一日媒待核）
- 关键教训：
  1. 本期游戏 AI 高价值主线：网易 AI NPC 规模化量产（500个NPC）+ 内部两条（HY4 零代码游戏原型 / Miora 3D资产后处理），是「AI NPC 量产」+「AI 造 AI」+「3D资产可实战」三条可落地的对照样本。
  2. 去重注意：腾讯 Hy4 正式版（11-05已收）、米哈游 GameScaling（10-23已收，11-05被网易重报）、Anthropic Q3（11-04已收）均跳过；GPT-6 Cyber 虽命中旧「GPT-6」指纹，但属全新安全子型号，单列新指纹。
  3. 心屿X1、Gemini Omni 1.2 Flash 均为单源（搜狐自媒体/theitguysfix），已标「待核」；KM 本次无走 skill，直接 DeferExecuteTool 调 mcp__km__list-articles（hot_value）+ show-article(full_content)。
  4. 新增 10 条指纹写入 dedup_history.json（总数 262）。

## 2026-11-07（第三十一次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-07.html（单文件自包含，10 条）
- 窗口：2026-10-24 ~ 2026-11-07
- 信源：小红书 MCP（已登录，AI游戏/AI队友 最新排序，窗口内仅「AI内鬼」1条高价值，经官方交叉核验采信）、B站（EmbodiedNPC 开源活人感NPC 11-06 1条，星露谷/生化MOD已去重）、X feed（Qwen官方预告为主，信息不足未成条）、官方（Anthropic Project EVE 11-06 / 腾讯全球数字生态大会 11-04 / 百度AI Day 11-03）、媒体多源交叉（DOIT/腾讯网/第一财经/网易智东西/The Decoder/经济参考网）、KM（近7天 hot_value 无游戏AI高价值新增，均为低热度刚发工程文）
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Anthropic Project EVE「AI内鬼」实验（11-06，多agent协调已解/审计问责未解，映射AI队友仲裁）②腾讯 Giinex 游戏AI引擎对外开放（11-04，决策AI日均15亿调用/5000万玩家，映射游戏AI商业化）③自然选择 A+轮累计超1亿美元（11-06，3D AI伴侣EVE+Agentic社交Elys）④Menlo Ventures报告：美国企业开源支出89%流向中国（Kimi61%/DeepSeek15%/GLM11%）⑤METR审计 Anthropic能力约翻倍80%AI加速（11-06）⑥Thinking Machines Inkling 2 Small 594B MoE（11-05，西方开放权重第一）⑦Perplexity Teammates $200/月常驻（11-06）⑧Meta Muse视频聊天开放（Realtime Avatar/Voice）⑨百度 Apollo World 世界模型（11-03，智能体驱动）⑩EmbodiedNPC 开源活人感NPC（11-06 B站）
- 关键教训：
  1. Anthropic Project EVE（AI内鬼）是本期最高价值：直接用游戏（EVE Frontier）做多agent信任/审计实验，结论「协调已解、问责未解，需审计轨迹+职责分离而非agent互查」，直接映射用户 AI队友「多Agent信任/仲裁/审计」工作，值得重点跟踪此类「架构落地量化」而非单纯模型发布。
  2. 腾讯 Giinex 对外开放是用户同赛道强映射：邓民文 11-04 全球数字生态大会披露决策AI日均15亿调用/5000万玩家/七大案例（王者AI指挥官/PUBG AI队友/三角洲NPC），首次对外卖游戏AI能力，与用户 AI队友 工作直接相关。
  3. 日期交叉核实：Inkling 2 Small 中文源(智东西)标11-06、英文源(Think Facility/Decoder)标11-05发布，取「11-05发布/11-06中文报道」双标注；Apollo World 为11-03深圳百度AI Day（非11-05报道日）。
  4. 新增 10 条指纹写入 dedup_history.json（总数 272）。注意「自然选择AI伴侣产品名 EVE」与「Anthropic Project EVE」重名，指纹已用不同关键词区分。

## 2026-11-08（第三十二次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-08.html（单文件自包含，10 条）
- 窗口：2026-10-25 ~ 2026-11-08
- 信源：全网搜索多轮交叉核实（本期主体）、官方（百度 ERNIE 官网/HF、Google ADK GitHub、Gradium HF 官方博客、Ramen GamePress 新闻稿）、媒体（彭博社/中国证券网/澎湃/北京日报/中国经营报/中国基金报/网易/环球网等多源交叉）、社区实测（GitHub ramenvr/autopilot、HackerNoon/Dev.to 独立复现）；KM（近 7 天 hot_value 遍历，无游戏 AI 高价值新增）；小红书 MCP / B站 / X 本期未启动采集（社区源连续十余期无高价值，降级并在页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Ramen Aura Autopilot 游戏测试 agent 开源（10-30，编码agent+Jev决策模型两层分工，映射局内AI bot分层决策+QA自动化）②Spore 运行时+Kêr-Is：AI智能体自建游戏又自写机器人验货（11-07，AI造AI闭环）③可灵AI 198亿融资落定、投后估值180亿美元反超快手（10-30交割，BAT同台）④Sand.ai 2亿美元A+轮跻身独角兽（11-05，MAGI-2正式版将发布）⑤百度开源 ERNIE 5.5 Flash Base（11-05，280B MoE/14B激活/1M上下文）⑥DeepSeek Harness 日活154万+官方插件市场（11-05，上期更新）⑦OpenAI 110亿美元首期融资交割、估值1.25万亿缩水（11-07彭博，上期更新）⑧Phonon 端侧TTS开源（Gradium，65MB/CPU首包28ms，映射AI队友本地语音）⑨Google ADK 2.14 将A2A协议标记稳定（11-07，多agent互通标准）⑩OpenAI Images 2.6 Flare/Sunburst双模型（11-06/07，快/稳分SKU）。
- 关键教训：
  1. 本期游戏AI主线是「AI造AI落在真实劳动」：Aura Autopilot（游戏测试）+ Spore（自建游戏自验货）两条都是「编码agent生成harness+决策模型执行」的分层架构，与 AI队友「分层决策」同构，值得持续跟踪此类「架构落地」而非单纯模型发布。
  2. 视频生成融资双信号同窗：可灵（198亿、估值超快手）+ Sand.ai（2亿美元）均指向游戏CG/剧情/素材生产成本曲线持续下探，是游戏AI内容生产链的强映射。
  3. Phonon 权重开放 10-20 略早于 14 天窗起点（窗口 10-25 起），但 11-05 官方完整发布+榜单在窗，已如实双日期标注，未硬塞。
  4. 新增 10 条指纹写入 dedup_history.json（总数 282）。

## 2026-11-09（第三十三次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-09.html（单文件自包含，9 条）
- 窗口：2026-10-26 ~ 2026-11-09
- 信源：全网搜索多轮交叉核实（本期主体）、官方（腾讯混元官网/阿里云·ModelScope/ElevenLabs 博客）、媒体多源（贝壳财经/凤凰网/IT之家/百度百科/EastFrontier/TechNews）、学术（arXiv）；KM（近7天 hot_value 无游戏AI高价值新增）；小红书/B站/X 未启动采集（降级）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q。
- 本期核心（9 条）：①易鑫开源 Harness 治理体系（11-05 乌镇，五类机制/45智能体90%自主交付，映射AI队友治理）②腾讯 Hy4 游戏AI评测数据（11-05 官方，和平精英 AI NPC 情绪价值2.96/总分2.91、王者荣耀99.32%，上期更新）③阿里 Qwen3.8 全系开源（11-05/06，旗舰2.4T首开权重）④ElevenLabs ElevenAgents Unity SDK（11月上旬，Client tools 让AI反向触发游戏代码，映射AI队友语音）⑤蚂蚁 Ling-3.2-flash（11-05/06，560B原生多模态）⑥Uncracked City（11-03，LLM嫌疑人会说谎+AI侦探模型验货）⑦LLM游戏NPC系统综述（arXiv 2611.05427，377篇，长期记忆31%/反思38%/RAG14%）⑧Fabula Rasa VR（11-12预告，LLM即兴NPC）⑨中国移动云×智谱 GLM进MoMA（11-06/08）。
- 关键教训（重要，日期陷阱连发）：
  1. **Claude Sonnet 4.6 是 2026-02-17 老模型**（dev.to 11-08 文章标「今日发布」误导），Claude Opus 5.5 实为 09-22 发布（夜雨飘零博客 11-06 误标「官方发布」）——以 modelavailability.com / llm.okamomedia.tokyo 权威模型时间线为准反查，聚合号/个人博客的「今日/发布」措辞不可信。
  2. **《和平精英》AI 明星队友「小田」是 5/27 SPARK 2026 发布会事件**：mtvccc.com 用「刚刚，腾讯一口气曝光9项游戏AI」转述 5/27 发布会内容，日期完全缺失，差点误判为窗口内新事件。内容聚合站（mtvccc）的「刚刚」措辞 + 无日期 = 高危信号，务必反查原始发布会日期。
  3. 腾讯混元 Hy4 官方页（hy.tencent.com/research/hy4）含游戏AI一手量化评测（和平精英AI NPC 情绪价值2.96、王者荣耀99.32%准确率），是「上期已收Hy4正式版」的重大分解数据，标注上期更新后单列，直接服务用户AI队友项目。
  4. 新增 9 条指纹写入 dedup_history.json（总数 291）。

## 2026-11-10（第三十四次执行）
- 产出：G:\project_outputi_daily_report6-11-10.html（单文件自包含，10 条）
- 窗口：2026-10-27 ~ 2026-11-10
- 信源：官方（Anthropic 官网核实 Fable/Mythos 5.2、NVIDIA/UbiSoft/MADFINGER/Meta/Ricursive 经媒体交叉）、媒体&聚合（财联社/机器之心/凤凰/腾讯新闻/雷峰网/新浪财经/Axios/TechCrunch 多源交叉）、内部 KM（list-articles 近7天 + show-article 全文，收录「判别式多标签内容审核」674168）、全网搜索多轮（本期主体）；小红书 MCP 已登录并查「AI游戏」最新排序（窗口内低赞个人帖/聚合快讯，无高价值收录）；B站/X 未深入采集降级。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q
- 本期核心（10 条）：①Anthropic Fable 5.2/Mythos 5.2（11-10 官方，1000 agent 30h 形式化费马大定理、8天做OS、RoboDojo 64.9%、IPO 估值1-1.5万亿）②OpenAI GPT-6.1 Sol（11-09，近Astra 1/5价格）③Meta Muse Ember（11-09，$0.10/M 最便宜模型）④NVIDIA Cosmos 3 Nano+VFlash（11-05/06，世界模型商用许可+并行轨迹解码）⑤腾讯PCG判别式多标签内容审核（11-09 KM头条，Qwen3-VL-8B+9维sigmoid判定头，耗时-30%算力-50%，映射生图审核）⑥全境封锁2 3 AI队友（11-03）⑦灰区战争 0.5.1.0 AI感知大改（拟真不背板）⑧Ora-Orb 情绪陪伴硬件融资（11-06）⑨Ripple-65B 开源（11-04）⑩Meta 收购 Conductor（11-04）
- 关键教训：
  1. **版本号陷阱（重要）**：此前社区扒源码流传「Fable/Mythos 5.5」（10-21/11-02 已收录待核），本次官方正式版为「5.2」（官方页明确「较 5.1 升级、快30%」）。结论：社区泄露的版本号不可信，以官方发布页为准；本期在卡片里显式标注「5.5 疑为误传、待核」。
  2. OpenAI 模型线密集且易混：本期「GPT-6.1 Sol 正式 GA（11-09，1/5价格）」与 10-12 已收「GPT-6.1 Sol Ultrafast」、10-28「GPT-6.1 Terra」、11-06「GPT-6 Cyber」是不同子型号，需按「正式 GA + 定价」区分新增量，标注上期更新。
  3. 小红书本期仍为低赞个人帖/聚合快讯（连续十余期无高价值），但 sort_by=最新 返回的 id 前8位 hex 时间戳可快速判断窗口；B站/X 未深入采集，已在页脚如实标注降级。
  4. 新增 10 条指纹写入 dedup_history.json（总数 301）。

## 2026-11-11（第三十五次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-11.html（单文件自包含，10 条）
- 窗口：2026-10-28 ~ 2026-11-11
- 信源：官方（Google/Anthropic/DeepMind/美团/MiniMax/阿里 经官方页核实）、媒体多源交叉（科技日报/证券时报/上证报/IT时报/腾讯新闻/AIbase/Yahoo财经等）、内部 KM（list-articles hot_value，收录 full-cycle-developer 674306 1 条）、全网搜索多轮（本期主体）；小红书 MCP / B站 / X 未启动采集（社区源连续十余期无窗口内高价值，降级并在页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q。
- 本期核心（10 条）：①Qwen4 GameFeel Bench 游戏创造力基准首超 Opus 5.5（11-08 泄露待核）②千问办公 2.0 Team Agent 多人与 Agent 协作（11-09，映射 AI 队友群聊）③Nuance Emma 全双工非语言信号（11-10 待核）④Gemini 4 Carbon 全面开放 + /swarm 蜂群（上期更新）⑤美团 LongCat-2.5 开源 MIT（上期更新，国产算力 86% 吞吐）⑥DeepMind AlphaProof Code 验证 Signal libsignal（11-10）⑦Claude Whiteboards/Sheets/Data 办公套件（11-10）⑧Anthropic IPO 路演 $70-$78 + 7 巨头 260 亿 N 类股（上期更新）⑨MiniMax H3-Image 开源（4K<10秒）⑩KM full-cycle-developer 自验收返工。
- 关键教训：
  1. 本期密集在 11-09~11-10 两天：Qwen4/千问办公2.0（11-09）+ Gemini Carbon 全面开放/AlphaProof Code/Claude 办公套件/Anthropic 路演/H3-Image/Emma（11-10），为「周一发布潮」。社区源再次无高价值，靠官方+媒体+KM 补足。
  2. 「上期更新」三条（Gemini 4 Carbon、LongCat-2.5、Anthropic IPO）需显式标注：10-30 已收 Carbon 首次公布→本期「全面开放+/swarm」；11-04 已收 LongCat 发布→本期「MIT 开源权重」；10-26/28 已收 IPO/S-1→本期「路演启动+发行价区间 $70-$78+260 亿 N 类股」。
  3. 新增 10 条指纹写入 dedup_history.json（总数 311）。

## 2026-11-12（第三十六次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-12.html（单文件自包含，10 条）
- 窗口：2026-10-29 ~ 2026-11-12
- 信源：官方（Google/OpenAI/Anthropic/阿里 经官方页核实）、媒体多源交叉（凤凰/腾讯/网易/中新经纬/上证报/彭博）、社区实测（Rein-NPC-4B HF+artrealmai）、内部 KM（list-articles hot_value，收录 WMA+Browser Use 674438 头条）；小红书/B站/X 未深入采集（降级，页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q。
- 本期核心（10 条）：①Google Gemini Decision 1 + Decisions API（11-12，决策模型独立品类，$0.10/1M、150-250ms、零输出计费，映射AI队友决策层）②SpaceXAI Grok Bot 1.0（11-11，AI队友转正，Team Bots全队共用+主动介入+永远在线，最强映射）③OpenAI Control Room 熔断（11-09，35秒叫停+失效关闭，映射AI队友安全兜底）④Rein-NPC-4B 开源（11-09，64 token决策层，96%动作准确率）⑤Anthropic MAMUBench（11-11，单agent协调胜多agent）⑥阿里 Qwen4-Max 预览版（11-11，1M上下文+Agentic升级）⑦Grok CSAM 集体诉讼（11-11/12，映射生图审核红线）⑧Grok Build 94.7% 匿名访问（11-12，映射Agent默认门禁）⑨OpenAI Q3 营收100亿（11-11/12，付费用户超1亿，亏损109亿）⑩KM WorkBuddy WMA+Browser Use（11-12 内部头条）。
- 关键教训：
  1. 本期「决策模型」品类集中爆发：Google Gemini Decision 1（独立品类）+ Rein-NPC-4B（NPC决策层）两条，与 10 月 Jev/蚂蚁 LingDT/OpenAI Decisions API 决策模型系列同线，决策层正成为独立计价能力，持续映射 AI队友仲裁/决策层。
  2. Grok Bot 1.0 是「AI队友」作为独立产品转正的最强对标：多人协作/主动介入/永远在线三点逐条对应 AI队友 项目，SpaceXAI 已并入 SpaceX 序列（xAI→SpaceXAI 品牌变更需标注）。
  3. 新增 10 条指纹写入 dedup_history.json（总数 321）。

## 2026-11-13（第三十七次执行）
- 产出：G:\project_output\ai_daily_report\2026-11-13.html（单文件自包含，10 条）
- 窗口：2026-10-30 ~ 2026-11-13
- 信源：全网搜索多轮交叉核实（本期主体）、官方（Google/百度/OpenAI/米哈游/腾讯经官方页+媒体交叉）、媒体&聚合（澎湃/上证报/央广网/凤凰网/量子位/iThome 等）、KM（list-articles hot_value 近7天，无游戏 AI 高价值新增量）；小红书 MCP/B站/X 未深入采集（降级，页脚注明）。
- 企业微信：**发送成功**——wecom_bot_push.py 直推，ok=true，markdown errcode=0 + file errcode=0 均送达，chatid=wokSFfCgAAvcWG9LpK3omw4OqVzOdK9Q。
- 本期核心（10 条，7 新增 + 3 上期更新）：①Gemini 4 Hydrogen + Antigravity Orchestrator（11-12，高效执行引擎 $1.5/1M + 双模型动态路由 Carbon规划/Hydrogen执行降24%配额）②百度世界2026 文心5.5 Flash Preview + 词元所大模型交易平台（11-12，李彦宏"智能组织"）③OpenAI Codex Security 安全扫描开源（11-12，CLI+SDK，断点续扫/成本预算）④张一鸣内部定调字节AI追平最早2029-2030（11-12，Seed数据规模偏少+排蒸馏）⑤LucidML 630M 本地世界模型（11-11，RTX3060 跑"神经GTA"，Summaryformer 记忆压缩）⑥OpenAI 儿童安全宪章+200万美元（11-12，映射 AI 陪伴未成年人红线）⑦ReTrace SOP Agent 编译降本（arXiv，成本-24%/170s→1.3s）⑧星布谷地 Famitsu 访谈 AI NPC 群聊漏话（11-09，上期更新）⑨Fable 5.2 首批实测（8h做COD射击/76min大鱼吃小鱼，上期更新）⑩鹅次元元气首测+能量计费规则（11-10，上期更新）。
- 关键教训：
  1. 本期 11-12 为"发布密集日"（周四）：Gemini 4 Hydrogen、百度世界、Codex Security、张一鸣定调、OpenAI 儿童宪章、Claude Meetings 六连，几乎全集中在 11-12；社区源（小红书/B站/X）连续多期无高价值，靠官方+媒体+全网补足硬信息。
  2. 两条"同周期产业共识"值得持续跟踪：李彦宏"智能组织"与张一鸣"组织接盘能力/数据规模"同日共振，判断行业竞争焦点正从"单模型"转向"组织+数据"；Gemini Orchestrator 的"贵模型规划+便宜模型执行"双模型路由，与 AI 队友"决策层（贵）+执行层（便宜）"分层计价同构。
  3. 去重注意：Gemini 4 Hydrogen 与已收"Gemini 4 Carbon/Argon"是不同子型号（Hydrogen 为高效执行引擎）；文心 5.5 Flash Preview + 词元所与已收"ERNIE 5.5 Flash Base 开源"（11-08）不同（Preview vs Base + 词元所平台）；星布谷地/Fable 5.2/鹅次元均标"上期更新"。
  4. 新增 7 条指纹写入 dedup_history.json（总数 328）。
