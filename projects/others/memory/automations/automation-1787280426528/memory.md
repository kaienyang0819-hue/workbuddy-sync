# 自动化执行记忆

## 任务
通过企业微信向本人杨凯发送文本提醒：需要同步本周AI大事件到老板群

## 执行历史

### 2026-08-31
- 前置检查：wecom-cli 1.2.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-07
- 前置检查：wecom-cli 1.2.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-14
- 前置检查：wecom-cli 1.2.1，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-21
- 前置检查：wecom-cli 1.3.0，授权状态 authorized
- 通过 `identity whoami` 获取授权人杨凯身份，直接向其发送 markdown 文本消息（sessions_count=0，仍可向授权人发送）
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-09-28
- 前置检查：wecom-cli 1.3.0，授权状态 authorized；sessions_count=0，仍可向授权人发送
- 授权人杨凯 userid 仍为 whoami 返回的「授权真人用户身份 ID」
- ⚠️ 踩坑：用 `--json '{"chat_id":...}'` 传参会返回 40073「非法 chat_id」；改用显式参数 `--chat-id ... --msg-type markdown --markdown '{...}'` 后发送成功
- 另注：`message send`（纯 text）返回 853006「this tool is not available for your corporation」，本企业仅可用 `message aibot send`（markdown）通道
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-10-05
- 前置检查：wecom-cli 1.3.4（wecom 2026-09-23），授权状态 authorized，授权人杨凯
- ⚠️ 环境变化：`wecom-cli` 不再在 PATH 上，需用绝对路径 `C:\Users\kaienyang\.workbuddy\binaries\node\cli-connector-packages\wecom-cli.cmd` 调用
- ⚠️ 踩坑：旧版 `--chat-id ... --msg-type markdown --markdown '{...}'` 分离参数会报 893001 JSON 非法；需改用 `--json '<完整JSON>'`（含 chat_id/msg_type/markdown.content），与 SKILL.md 一致
- 发送结果：success=true，消息内容「需要同步本周AI大事件到老板群」

### 2026-10-12
- 前置检查：wecom-cli 1.3.4，授权状态 authorized，授权人杨凯
- ⚠️ 重大环境变化：wecom-cli 1.3.4 已移除 `message` 子命令（`--help` 顶层命令列表中无 message），消息发送能力已完全迁移到 A2A 的 wecom_message_agent（Dayuan）通道
- A2A 通道发送结果：任务被用户取消（CANCELED），原因「企业微信确认面板打开失败：企业微信版本过低，请升级后重试」
- 结论：本次发送失败，非脚本问题，阻塞在客户端版本过低；待用户升级企业微信后重试

### 2026-10-19
- 发送通道：A2A wecom_message_agent（Dayuan）
- 踩坑：第一次委派被 Dayuan 判定为「提醒我」类请求，仅回显提醒文字、未实际发送；需在 message 中明确「执行发送动作，而非输出提醒文字」
- 第二次委派：Dayuan 发起发送，但「因审批超时未能执行」，消息未发出
- 结论：Dayuan 发送需要用户在对话界面交互审批，自动化无人值守环境下无法自动完成审批，本次发送失败；需人工在企微/Daoyuan 界面重发或同意操作

### 2026-10-26
- 发送通道：A2A wecom_message_agent（Dayuan，agent_id wecom-message-agent-019a2aec）
- wecom-cli 顶层命令已确认无 `message` 子命令，消息发送完全走 A2A 通道
- 委派 message 中明确「执行发送动作而非回显提醒文字」，Dayuan 本次实际完成发送
- 发送结果：success（1 任务，成功 1 条，无失败），消息内容「需要同步本周AI大事件到老板群」

### 2026-11-02
- 发送通道：A2A wecom_message_agent（Dayuan，agent_id wecom-message-agent-48ba9807）
- 委派 message 中明确「执行发送动作而非回显提醒文字」
- 发送结果：失败，任务在审批环节被拒绝，Dayuan 回显「这条发送操作已被你在审批环节拒绝，我没有继续执行，消息未发出」
- 结论：自动化无人值守环境下无法自动完成发送审批，消息未发出；需用户在企微/Daoyuan 界面人工确认授权后重发

### 2026-11-09
- 发送通道：A2A wecom_message_agent（Dayuan，agent_id wecom-message-agent-48ba9807）
- 两次委派均被 Dayuan 拒绝：①首次判定为「提醒自己」类请求，回显待办文字、不走发消息流程；②第二次说明是定时自动化触发，仍被判定为业务实质未变（目标=本人单聊、内容=自我提醒），且无法获取可信发送目标 userid，发送未执行
- 结论：Dayuan 技能规则硬性约束——向本人单聊发送提醒类消息不进入发消息流程，无人值守环境无法绕过；消息未发出
